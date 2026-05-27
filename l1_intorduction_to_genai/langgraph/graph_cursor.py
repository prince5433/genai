import json
import os
from typing import Any, Dict, List, Literal

from dotenv import load_dotenv
from langfuse import observe
from langfuse.openai import openai
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


# .env file se OPENAI_API_KEY, Langfuse keys etc. load ho jayengi.
load_dotenv()

# Ye OpenAI client Langfuse wrapper se aa raha hai.
# Iska benefit: model calls aur tool traces Langfuse dashboard me track ho sakte hain.
client = openai.Client()


# -------------------- TOOLS --------------------
# Ye wahi tools hain jo mini cursor agent use kar sakta hai.
# Model directly file system access nahi karta. Model sirf JSON me bolta hai:
# "function": "read_file", "input": "test.py"
# Fir hum Python side par us tool ko execute karte hain.


@observe()
def run_command(command):
    # System command run karta hai, jaise: dir, ls, python file.py
    # os.system command ka exit code return karta hai.
    print("Tool Called: run_command", command)
    return os.system(command)


@observe()
def read_file(path):
    # Given file path ka content read karta hai.
    # Agar file nahi mili ya error aaya to readable message return karega.
    print("Tool Called: read_file", path)
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        return "File not found"


@observe()
def write_file(path, content):
    # Given file path par content overwrite karta hai.
    # Coding assistant ke edit operation ke liye ye main tool hai.
    print("Tool Called: write_file", path)
    try:
        with open(path, "w") as f:
            f.write(content)
        return "File updated successfully"
    except Exception:
        return "Error writing file"


# -------------------- TOOLS MAP --------------------
# Model JSON me tool ka naam bhejta hai.
# Ye dictionary us naam ko actual Python function se connect karti hai.
# Example: "read_file" -> read_file function


available_tools = {
    "run_command": {"fn": run_command},
    "read_file": {"fn": read_file},
    "write_file": {"fn": write_file},
}


# -------------------- SYSTEM PROMPT --------------------
# Ye prompt model ko mini cursor ki rules batata hai.
# Important idea:
# - Model ko hamesha JSON return karna hai.
# - Model step-by-step chalega: plan -> action -> observe -> output
# - File edit se pehle file read karni zaroori hai.


system_prompt = """
You are an AI coding assistant (like Cursor).

You can:
- read files
- modify files
- run commands

You MUST follow steps:
1. plan
2. action
3. observe
4. output

Rules:
- Always use tools for file operations
- NEVER guess file content
- Always read file before editing
- Make minimal changes

Output JSON format:
{
    "step": "plan | action | observe | output",
    "content": "string",
    "function": "tool name (if action)",
    "input": "input to tool"
}

Example:
User: fix bug in test.py

plan: I should read file
action: read_file -> "test.py"

observe: <file content>

plan: fix bug

action: write_file -> {
  "path": "test.py",
  "content": "fixed code"
}

output: Bug fixed successfully
"""


# -------------------- STATE --------------------
# LangGraph me har node ko ek shared state milti hai.
# Node state ko read/update karke next node ko pass karta hai.
#
# messages:
#   Full conversation history. Isme system prompt, user input,
#   assistant ke plan/action/output aur tool observe results store hote hain.
#
# parsed_output:
#   Model ka latest JSON response Python dictionary ke form me.
#   Example: {"step": "action", "function": "read_file", "input": "test.py"}
#
# final_answer:
#   Jab model "output" step deta hai, uska content yahan save hota hai.


class State(TypedDict):
    messages: List[Dict[str, Any]]
    parsed_output: Dict[str, Any]
    final_answer: str


# -------------------- GRAPH NODES --------------------
# Node 1: call_model
# Node 2: run_tool
#
# Mini cursor ke original code me inner while loop tha.
# LangGraph version me wahi loop graph edges se ban raha hai.


def call_model(state: State):
    # Current conversation history model ko bhejte hain.
    # Model next step decide karega: plan, action, ya output.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=state["messages"],
    )

    # Model response JSON string hota hai.
    raw_content = response.choices[0].message.content

    # JSON string ko Python dict me convert karte hain.
    # Agar invalid JSON aa jaye to graceful output set kar dete hain.
    try:
        parsed_output = json.loads(raw_content)
    except Exception:
        parsed_output = {
            "step": "output",
            "content": "Model ne valid JSON response nahi diya.",
        }

    # Model ka response bhi message history me save karna zaroori hai.
    # Next model call ko pata rahega ki pehle kya plan/action hua tha.
    state["messages"].append(
        {
            "role": "assistant",
            "content": json.dumps(parsed_output),
        }
    )

    # Latest parsed response state me save ho gaya.
    # Routing function isi parsed_output ko read karke next node decide karega.
    state["parsed_output"] = parsed_output
    return state


def run_tool(state: State):
    # Ye node tab chalega jab model ne "step": "action" return kiya ho.
    # Iska kaam hai requested tool ko Python side par execute karna.
    parsed_output = state["parsed_output"]
    tool_name = parsed_output.get("function")
    tool_input = parsed_output.get("input")

    # Agar model ne galat tool name bheja to error ko observe bana kar bhej denge.
    if tool_name not in available_tools:
        output = f"Tool not found: {tool_name}"
    else:
        # Tool name se actual function nikalo.
        fn = available_tools[tool_name]["fn"]

        # Kabhi-kabhi model input ko stringified JSON me bhej sakta hai.
        # Example: "{\"path\": \"test.py\", \"content\": \"...\"}"
        # Isliye pehle JSON parse try karte hain.
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except Exception:
                pass

        # Agar input dict hai to keyword arguments ke form me pass hoga.
        # Example: write_file(path="test.py", content="...")
        #
        # Agar input normal string hai to single argument ke form me pass hoga.
        # Example: read_file("test.py")
        try:
            if isinstance(tool_input, dict):
                output = fn(**tool_input)
            else:
                output = fn(tool_input)
        except Exception as e:
            output = str(e)

    # Tool output ko conversation me "observe" step ke form me add karte hain.
    # Model next call me ye observe dekhega aur decide karega:
    # - next plan banana hai
    # - aur tool call karna hai
    # - ya final output dena hai
    state["messages"].append(
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "step": "observe",
                    "output": output,
                }
            ),
        }
    )

    return state


# -------------------- ROUTING --------------------
# LangGraph me conditional edge ek function se decide hota hai.
# Ye function model ke latest "step" ko dekhta hai aur next node batata hai.


def route_after_model(state: State) -> Literal["call_model", "run_tool", "end"]:
    parsed_output = state["parsed_output"]
    step = parsed_output.get("step")

    # Agar model plan deta hai, tool nahi chalana.
    # Bas plan print karo aur model ko next step ke liye dobara call karo.
    if step == "plan":
        print(f"PLAN: {parsed_output.get('content')}")
        return "call_model"

    # Agar model action deta hai, run_tool node par jao.
    if step == "action":
        return "run_tool"

    # Agar model output deta hai, graph finish ho jayega.
    if step == "output":
        state["final_answer"] = parsed_output.get("content", "")
        return "end"

    # Agar model ne unknown step diya to graph ko safely end kar do.
    state["final_answer"] = "Unknown step received from model."
    return "end"


# -------------------- GRAPH BUILD --------------------
# Yahan actual LangGraph ban raha hai.
#
# Flow:
# START -> call_model
#
# call_model ke baad:
#   plan   -> call_model
#   action -> run_tool
#   output -> END
#
# run_tool ke baad:
#   run_tool -> call_model
#
# Isse original mini cursor ka inner while loop graph cycle me convert ho gaya.


graph_builder = StateGraph(State)

# Graph me nodes register karo.
graph_builder.add_node("call_model", call_model)
graph_builder.add_node("run_tool", run_tool)

# Graph start hote hi sabse pehle model call hoga.
graph_builder.add_edge(START, "call_model")

# call_model ke baad route_after_model decide karega next node.
graph_builder.add_conditional_edges(
    "call_model",
    route_after_model,
    {
        "call_model": "call_model",
        "run_tool": "run_tool",
        "end": END,
    },
)

# Tool execute hone ke baad observe result ke saath model ko phir call karna hai.
graph_builder.add_edge("run_tool", "call_model")

# Compile karne ke baad graph runnable ban jata hai.
graph = graph_builder.compile()


# -------------------- MAIN LOOP --------------------
# Ye outer loop original mini cursor jaise multiple user queries handle karta hai.
# Har user query ke liye graph invoke hota hai.


def call_graph():
    # Conversation history yahan preserve hoti rahegi.
    # System prompt sirf ek baar add hota hai.
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_query = input("\n> ")

        # Simple exit commands.
        if user_query.lower() in ["exit", "quit", "q"]:
            print("Bye")
            break

        # User query conversation history me add karo.
        messages.append({"role": "user", "content": user_query})

        # Initial state banao jo graph me pass hoga.
        state = {
            "messages": messages,
            "parsed_output": {},
            "final_answer": "",
        }

        # Graph run karo.
        # recursion_limit isliye diya hai taaki infinite loop me graph forever na chale.
        result = graph.invoke(state, config={"recursion_limit": 50})

        # Updated messages ko preserve karo.
        # Isse next user query ko previous context milta rahega.
        messages = result["messages"]

        # Final answer print karo.
        print(f"AI: {result.get('final_answer')}")


# Jab file directly run hogi tab chatbot start hoga.
# Agar kisi aur file me import karoge to auto-run nahi hoga.
if __name__ == "__main__":
    call_graph()
