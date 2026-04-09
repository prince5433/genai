import json
import requests
from dotenv import load_dotenv
from langfuse import observe
from langfuse.openai import openai
import os

load_dotenv()

client = openai.Client()


# -------------------- TOOLS --------------------

# Every tool below is wrapped so the agent can call it as a function.
# The @observe decorator helps track tool usage in Langfuse.
#observe decorator ka use karke hum ye dekh sakte hai ki kaunse tools kitni baar call ho rahe hai, unka input kya hai, output kya hai, aur unka execution time kya hai. Ye information Langfuse dashboard pe jaake dekh sakte hai jisse hume apne tools ke usage aur performance ka insight milta hai.
@observe()
#run command function ka kam hai ki system commands ko execute karna, jaise ki 'ls' (Linux/Mac) ya 'dir' (Windows). Ye function os.system() ka use karta hai jo command ko execute karta hai aur uska exit status return karta hai (0 matlab success). Agent is tool ka use karke apne environment ke baare me information le sakta hai ya files ko manipulate kar sakta hai.
def run_command(command):
    print("🔨 Tool Called: run_command", command)
    return os.system(command)


#read_file function ka kam hai ki given file path se file content ko read karna. Ye function try-except block me wrapped hai taaki agar file nahi milti ya koi error aata hai to usko handle kiya ja sake. Agent is tool ka use karke kisi bhi file ka content padh sakta hai, jo ki file manipulation ke liye zaruri hota hai.
@observe()
def read_file(path):
    print("🔨 Tool Called: read_file", path)
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return "File not found"

#write_file function ka kam hai ki given file path par specified content ko write karna. Ye function bhi try-except block me wrapped hai taaki agar file write karne me koi error aata hai to usko handle kiya ja sake. Agent is tool ka use karke kisi bhi file ko modify kar sakta hai, jo ki coding assistant ke liye ek important feature hai.
@observe()
def write_file(path, content):
    print("🔨 Tool Called: write_file", path)
    try:
        with open(path, "w") as f:
            f.write(content)
        return "File updated successfully"
    except:
        return "Error writing file"



# -------------------- TOOLS MAP --------------------

# This dictionary is the bridge between the model's tool name and the Python function.
#available_tools dictionary me humne apne tools ko map kiya hai jisse model jab tool call kare to wo easily us function ko identify kar sake. Har tool ke liye ek entry hai jisme "fn" key ke under uska corresponding Python function diya gaya hai. Is structure se model ko pata chal jata hai ki jab wo kisi tool ka naam use kare to uske peeche kaunse function ko execute karna hai.
available_tools = {
    "run_command": {"fn": run_command},
    "read_file": {"fn": read_file},
    "write_file": {"fn": write_file},
}


# -------------------- SYSTEM PROMPT --------------------

# The system prompt teaches the model how to behave like a coding assistant.
# It must decide step-by-step: plan, call a tool, observe the result, then answer.
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
action: read_file → "test.py"

observe: <file content>

plan: fix bug

action: write_file → {
  "path": "test.py",
  "content": "fixed code"
}

output: Bug fixed successfully
"""

# The message history that will be sent to the model, starting with the system prompt.
messages = [
    {"role": "system", "content": system_prompt}
]


# -------------------- MAIN LOOP --------------------

# Outer loop keeps the program alive for multiple user requests.
while True:
    # Take user input and add to message history
    user_query = input("\n> ")
    messages.append({"role": "user", "content": user_query})

    # Inner loop keeps asking the model for the next step until a final answer is produced.
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=messages
        )

        # Parse model response and add to history
        parsed_output = json.loads(response.choices[0].message.content)

        # We store the model's structured JSON response as text in the message history so the next model call can see the full conversation and all prior steps.
        messages.append({
            "role": "assistant",
            "content": json.dumps(parsed_output)
        })
        # The model is expected to follow the step-by-step process outlined in the system prompt. We check which step it is on and act accordingly.
        step = parsed_output.get("step")

        # -------- PLAN --------
        if step == "plan":
            # Planning step is only for reasoning; no tool is called yet.
            print(f"🧠 {parsed_output.get('content')}")
            continue

        # -------- ACTION --------
        if step == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            # Look up the requested tool and execute it if it exists.
            if tool_name in available_tools:
                fn = available_tools[tool_name]["fn"]

                # If the model sends JSON as text, convert it to a Python object first.
                if isinstance(tool_input, str):
                    try:
                        tool_input = json.loads(tool_input)
                    except:
                        pass

                # Support both single-argument tools and tools that expect keyword arguments.
                try:
                    if isinstance(tool_input, dict):
                        output = fn(**tool_input)
                    else:
                        output = fn(tool_input)
                except Exception as e:
                    # If the tool fails, return the error back into the conversation.
                    output = str(e)

                # Send the tool result back as an observe step so the model can continue.
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "step": "observe",
                        "output": output
                    })
                })
                continue

        # -------- OUTPUT --------
        if step == "output":
            # Final response is printed to the user and the inner loop ends.
            print(f"🤖 {parsed_output.get('content')}")
            break


# -------------------- FULL FLOW SUMMARY --------------------
# 1. User `>` prompt me kuch likhta hai.
# 2. User input `messages` list me add hota hai.
# 3. Model `plan` step deta hai to sirf soch ko print kiya jata hai.
# 4. Model `action` step deta hai to requested tool dhoondh kar run kiya jata hai.
# 5. Tool ka result `observe` step ke roop me wapas model ko bheja jata hai.
# 6. Model result dekh kar next step decide karta hai, jab tak final answer ready na ho.
# 7. `output` step aate hi final answer print hota hai aur inner loop khatam ho jata hai.
# 8. Outer loop phir se next user query ke liye ready rehta hai.
# 9. `read_file` aur `write_file` file operations handle karte hain.
# 10. `run_command` system commands chalata hai.
# 11. `get_weather` external API se weather laata hai.
# 12. `@observe` tool calls ko Langfuse me track karta hai.