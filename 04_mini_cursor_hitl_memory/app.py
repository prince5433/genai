import json  # JSON parse/write ke liye
import os  # Env vars aur OS config ke liye
import re  # Regex matching ke liye
import subprocess  # Shell commands chalane ke liye
import warnings  # Warnings filter/ignore ke liye
from pathlib import Path  # Path handling ke liye
from typing import Annotated, Any, Literal, TypedDict  # Typing helpers

# External libraries:
# - dotenv: .env file se OPENAI_API_KEY / model load karne ke liye.
# - langchain_core messages: LangGraph state me chat history ko typed messages ke form me rakhte hain.
# - ChatOpenAI: actual OpenAI chat model wrapper.
# - MemorySaver: LangGraph ka in-process checkpointer.
# - StateGraph: LangGraph workflow banane ka main builder.
# - add_messages: reducer jo old messages + new messages ko append karta hai.
from dotenv import load_dotenv  # .env load helper
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage  # Message types
from langchain_openai import ChatOpenAI  # OpenAI chat wrapper
from langgraph.checkpoint.memory import MemorySaver  # In-process checkpointer
from langgraph.graph import END, START, StateGraph  # Graph builder + terminals
from langgraph.graph.message import add_messages  # Messages reducer

# Mem0 telemetry ko band rakha hai, warna extra network/telemetry calls ho sakti hain.
# HF symlink warning Windows par common hai; functionality break nahi hoti, bas warning noisy hoti hai.
os.environ.setdefault("MEM0_TELEMETRY", "False")  # Mem0 telemetry off
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")  # HF symlink warning off
warnings.filterwarnings("ignore", message="Payload indexes have no effect in the local Qdrant.*")  # Noisy warning ignore

# Mem0 optional rakha hai. Agar package/import fail ho jaye, app phir bhi LangGraph
# checkpoint + local JSON knowledge graph ke saath chal sakta hai.
try:
    from mem0 import Memory  # Optional Mem0 import
except ImportError:
    Memory = None  # Mem0 missing ho to None


# Project path setup:
# PROJECT_ROOT hamesha isi new project folder ko point karega.
# Isse tools ko bahar ke folders me file write/read karne se roka ja sakta hai.
PROJECT_ROOT = Path(__file__).parent.resolve()  # Project root
ROOT_ENV = PROJECT_ROOT.parent / ".env"  # Parent .env
PROJECT_ENV = PROJECT_ROOT / ".env"  # Project .env

# Pehle GENAI\.env load hota hai, phir project-specific .env override kar sakta hai.
# Matlab common key root me rakh sakte ho, ya is project ka model/key alag rakh sakte ho.
load_dotenv(ROOT_ENV)  # Root env load
load_dotenv(PROJECT_ENV, override=True)  # Project env override

# Runtime data files:
# - langgraph_state.json: restart ke baad chat messages wapas load karne ke liye.
# - knowledge_graph.json: entities/relations ka simple local graph.
# - mem0_history.db / qdrant: Mem0 persistent memory ke files.
DATA_DIR = PROJECT_ROOT / "data"  # Data folder
SNAPSHOT_FILE = DATA_DIR / "langgraph_state.json"  # Chat snapshot
KG_FILE = DATA_DIR / "knowledge_graph.json"  # Knowledge graph file
MEM0_HISTORY_DB = DATA_DIR / "mem0_history.db"  # Mem0 history DB
MEM0_QDRANT_PATH = DATA_DIR / "qdrant"  # Qdrant path

# THREAD_ID LangGraph checkpoint aur Mem0 memory ko ek stable conversation id deta hai.
# MODEL .env se aa sakta hai; default gpt-4o-mini rakha hai because broadly available hai.
THREAD_ID = "mini-cursor-hitl-memory"  # Stable thread id
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Model name


# System prompt model ko strict JSON protocol sikhata hai.
# App model se normal prose nahi chahta; app ko decision chahiye:
# - plan: sirf short thinking/status
# - action: tool call
# - output: final answer
SYSTEM_PROMPT = """
You are a LangGraph mini Cursor-style coding assistant.

You can inspect files, write files, run commands, ask a human for help, and use
long-term memories. You must protect the user's files.

Rules:
- Always read a file before editing it.
- Keep edits minimal.
- Use ask_human when you need missing information or a decision.
- Use write_file only with the complete intended file content.
- Use run_command only when it helps solve the task.
- Never access paths outside this project folder.
- Approval is handled by the app. Do not ask for approval in a plan message.
- If you need to write a file or run a command, return an action immediately.
- Use ask_human only for missing information, not for yes/no approval.
- Do not repeat plan messages. After one plan, choose an action or output.

Return only JSON:
{
  "step": "plan | action | output",
  "content": "short message",
  "function": "read_file | write_file | run_command | ask_human",
  "input": "tool input"
}

Tool input formats:
- read_file: "README.md"
- run_command: "dir"
- ask_human: "What file name should I use?"
- write_file: {"path": "hello.txt", "content": "hello from langgraph"}
"""

# Ye separate prompt conversation se durable facts nikalne ke liye hai.
# Example:
# user says "project uses LangGraph and Mem0"
# knowledge graph me entity/relation save ho sakti hai.
KG_PROMPT = """
Extract useful knowledge graph facts from this conversation turn.

Return only JSON:
{
  "entities": [{"name": "string", "type": "string", "summary": "string"}],
  "relations": [{"source": "string", "relation": "string", "target": "string"}]
}

Keep only durable facts useful for future coding help. If nothing useful exists,
return empty lists.
"""


# LangGraph state schema:
# Har node isi dictionary ko read/update karta hai.
# messages: chat history, add_messages reducer ke saath append hoti rahegi.
# memories: Mem0 se retrieved relevant memories.
# knowledge_graph: local JSON graph ka current data.
# pending_action: model ne tool call maanga, to yahan hold hota hai.
# approved: human approval ka yes/no result.
# done: final output aa gaya to True.
class AgentState(TypedDict):  # Graph state ka schema
    messages: Annotated[list[BaseMessage], add_messages]  # Chat history + reducer
    memories: list[str]  # Mem0 se aayi strings
    knowledge_graph: dict[str, Any]  # Local KG snapshot
    pending_action: dict[str, Any] | None  # Pending tool action
    tool_output: Any  # Last tool output
    approved: bool | None  # Human approval flag
    done: bool  # Final output flag


def ensure_data_dir():  # Data folder ensure helper
    # data folder runtime par create hota hai. Isme memory/snapshot/KG files rakhe jate hain.
    DATA_DIR.mkdir(exist_ok=True)  # Create if missing


def project_path(path: str) -> Path:  # Safe path resolver
    # Tool ko diya gaya path project root ke andar resolve karo.
    # Security guard: model/user galti se "../" dekar project ke bahar access na kar sake.
    resolved = (PROJECT_ROOT / path).resolve()  # Absolute resolve
    if resolved != PROJECT_ROOT and PROJECT_ROOT not in resolved.parents:  # Outside check
        raise ValueError("Access denied: path is outside this project")  # Block
    return resolved  # Safe path


def load_knowledge_graph() -> dict[str, Any]:  # KG load helper
    # Local JSON knowledge graph load karo. First run par empty graph return hota hai.
    ensure_data_dir()  # Data dir ready
    if not KG_FILE.exists():  # First run
        return {"entities": {}, "relations": []}  # Empty KG
    with KG_FILE.open("r", encoding="utf-8") as file:  # Open KG file
        return json.load(file)  # JSON parse


def save_knowledge_graph(kg: dict[str, Any]):  # KG save helper
    # Updated knowledge graph ko disk par save karo so restart ke baad bhi facts available rahen.
    ensure_data_dir()  # Data dir ensure
    with KG_FILE.open("w", encoding="utf-8") as file:  # Open for write
        json.dump(kg, file, indent=2)  # Pretty JSON write


def merge_knowledge_graph(existing: dict[str, Any], extracted: dict[str, Any]) -> dict[str, Any]:  # KG merge
    # LLM se nikle naye entities/relations ko existing graph me merge karta hai.
    # Duplicate relations avoid karne ke liye "seen" set use hota hai.
    entities = existing.setdefault("entities", {})  # Entities ensure
    for entity in extracted.get("entities", []):  # New entities loop
        name = entity.get("name")  # Entity name
        if not name:  # Empty name skip
            continue
        entities[name] = {  # Insert/update entity
            "type": entity.get("type", entities.get(name, {}).get("type", "unknown")),  # Type merge
            "summary": entity.get("summary", entities.get(name, {}).get("summary", "")),  # Summary merge
        }

    relations = existing.setdefault("relations", [])  # Relations list ensure
    seen = {(r.get("source"), r.get("relation"), r.get("target")) for r in relations}  # Duplicate guard
    for relation in extracted.get("relations", []):  # New relations loop
        item = (  # Relation tuple
            relation.get("source"),  # Source
            relation.get("relation"),  # Relation
            relation.get("target"),  # Target
        )
        if all(item) and item not in seen:  # Valid + not seen
            relations.append(  # Append relation
                {
                    "source": item[0],  # Source
                    "relation": item[1],  # Relation
                    "target": item[2],  # Target
                }
            )
            seen.add(item)  # Track seen

    return existing  # Merged graph


def create_mem0():  # Mem0 init helper
    # Mem0 long-term semantic memory provide karta hai.
    # Persistent config pehle try hota hai. Agar Windows/OneDrive/Qdrant SQLite issue aaye,
    # fallback in-memory Mem0 use hota hai, taaki app crash na ho.
    if Memory is None:  # Mem0 missing
        return None  # Disable Mem0

    ensure_data_dir()  # Data dir ensure
    MEM0_QDRANT_PATH.mkdir(exist_ok=True)  # Qdrant folder ensure
    persistent_config = {  # Persistent config
        "vector_store": {  # Vector DB settings
            "provider": "qdrant",  # Qdrant backend
            "config": {  # Qdrant config
                "path": str(MEM0_QDRANT_PATH),  # Local path
                "collection_name": "mini_cursor_memory",  # Collection name
            },
        },
        "llm": {  # LLM config for Mem0
            "provider": "openai",  # OpenAI provider
            "config": {  # Provider config
                "model": MODEL,  # Model name
            },
        },
        "embedder": {  # Embedding model config
            "provider": "openai",  # OpenAI embedder
            "config": {  # Embedder config
                "model": "text-embedding-3-small",  # Embedding model
            },
        },
        "history_db_path": str(MEM0_HISTORY_DB),  # History DB file
    }

    try:
        return Memory.from_config(persistent_config)  # Persistent init
    except Exception as exc:
        print(f"Persistent Mem0 unavailable, using in-memory Mem0: {exc}")  # Fallback log

    in_memory_config = {  # In-memory fallback config
        "vector_store": {  # Vector DB settings
            "provider": "qdrant",  # Qdrant backend
            "config": {  # Qdrant config
                "path": ":memory:",  # In-memory path
                "collection_name": "mini_cursor_memory",  # Collection name
            },
        },
        "llm": {  # LLM config for Mem0
            "provider": "openai",  # OpenAI provider
            "config": {  # Provider config
                "model": MODEL,  # Model name
            },
        },
        "embedder": {  # Embedding model config
            "provider": "openai",  # OpenAI embedder
            "config": {  # Embedder config
                "model": "text-embedding-3-small",  # Embedding model
            },
        },
        "history_db_path": ":memory:",  # In-memory history DB
    }
    try:
        return Memory.from_config(in_memory_config)  # In-memory init
    except Exception as exc:
        print(f"Mem0 disabled: {exc}")  # Fully disable log
        return None  # Mem0 off


memory = create_mem0()  # Mem0 instance (ya None)

# Main LLM agent decisions ke liye.
llm = ChatOpenAI(model=MODEL)  # Main LLM

# Knowledge graph extraction deterministic-ish rakhne ke liye temperature 0.
kg_llm = ChatOpenAI(model=MODEL, temperature=0)  # KG extractor LLM


def search_memories(query: str) -> list[str]:
    # User ke latest query ke basis par Mem0 se relevant old memories retrieve karo.
    # Agar Mem0 unavailable hai, empty list return karte hain.
    if memory is None:  # Mem0 disabled
        return []  # Empty memories
    try:
        results = memory.search(query=query, user_id=THREAD_ID, top_k=5)  # Search call
    except Exception as exc:
        return [f"Mem0 search unavailable: {exc}"]  # Error fallback

    memories = []  # Output list
    if isinstance(results, dict):  # Dict response case
        results = results.get("results", [])  # Normalize
    for item in results or []:  # Iterate results
        if isinstance(item, dict):  # Dict result
            memories.append(item.get("memory") or item.get("text") or json.dumps(item))  # Best field
        else:
            memories.append(str(item))  # Stringify
    return memories  # Final list


def add_memory(text: str):
    # Latest conversation/tool observations ko Mem0 me add karta hai.
    # Exceptions silently ignore ki hain because memory failure se core assistant crash nahi hona chahiye.
    if memory is None or not text.strip():  # No memory or empty text
        return  # Skip add
    try:
        memory.add(text, user_id=THREAD_ID)  # Add memory
    except Exception:
        pass  # Ignore failure


def read_file(path: str) -> str:
    # Cursor-like read tool. File content read karne se pehle path guard lagta hai.
    target = project_path(path)  # Safe path resolve
    if not target.exists():  # Missing file
        return f"File not found: {path}"  # Error text
    return target.read_text(encoding="utf-8")  # File content


def write_file(path: str, content: str) -> str:
    # Cursor-like write tool. Approval node isse pehle yes/no le chuka hota hai.
    # Parent folders auto-create hote hain, e.g. notes/test.txt.
    target = project_path(path)  # Safe path resolve
    target.parent.mkdir(parents=True, exist_ok=True)  # Ensure dirs
    target.write_text(content, encoding="utf-8")  # Write file
    return f"File written: {target.relative_to(PROJECT_ROOT)}"  # Success msg


def run_command(command: str) -> dict[str, Any]:
    # Shell command project folder ke andar run hota hai.
    # stdout/stderr ko last 4000 chars tak trim kiya hai so model context huge na ho.
    completed = subprocess.run(  # Run command
        command,  # Command string
        cwd=PROJECT_ROOT,  # Project cwd
        shell=True,  # Shell enabled
        text=True,  # Text mode
        capture_output=True,  # Capture stdout/stderr
        timeout=60,  # Timeout seconds
    )
    return {  # Trimmed output
        "returncode": completed.returncode,  # Exit code
        "stdout": completed.stdout[-4000:],  # Stdout tail
        "stderr": completed.stderr[-4000:],  # Stderr tail
    }


def ask_human(query: str) -> str:
    # Jab model ko missing info chahiye, ye tool terminal me human se answer leta hai.
    # Approval ke liye ye tool use nahi hota; approval_node separately yes/no leta hai.
    return input(f"\nHuman input needed:\n{query}\nAnswer > ")  # Prompt human


# Tool registry: model JSON me function name deta hai, app yahan se Python function nikalta hai.
TOOLS = {  # Tool registry
    "read_file": read_file,  # Read tool
    "write_file": write_file,  # Write tool
    "run_command": run_command,  # Command tool
    "ask_human": ask_human,  # Human tool
}

# Ye tools risky/complex maan kar human yes/no approval demand karte hain.
COMPLEX_TOOLS = {"write_file", "run_command"}  # Approval-required tools


def normalize_tool_input(tool_name: str, tool_input: Any, action: dict[str, Any]) -> Any:
    # LLM kabhi-kabhi strict JSON input nahi deta.
    # Example expected:
    #   {"path": "hello.txt", "content": "hello"}
    # But model de sakta hai:
    #   "hello.txt\nhello"
    #   "hello"
    # Ye helper messy input ko write_file ke required format me convert karne ki koshish karta hai.
    if isinstance(tool_input, str):  # String input case
        try:
            tool_input = json.loads(tool_input)  # JSON parse try
        except json.JSONDecodeError:
            pass  # Raw string hi rakho

    if tool_name != "write_file" or isinstance(tool_input, dict):  # Non-write or already dict
        return tool_input  # As-is return

    text = str(tool_input)  # Raw text
    filename_match = re.search(r"[\w.-]+\.txt|[\w./\\-]+\.py|[\w./\\-]+\.md", str(action))  # Filename guess
    path = filename_match.group(0) if filename_match else "hello.txt"  # Default path

    if "\n" in text:  # Multiline input
        first_line, rest = text.split("\n", 1)  # Split filename/content
        if re.search(r"\.[A-Za-z0-9]+$", first_line.strip()):  # Filename like?
            return {"path": first_line.strip(), "content": rest}  # Dict format

    return {"path": path, "content": text}  # Fallback dict


def parse_json_message(message: AIMessage) -> dict[str, Any]:  # JSON parse helper
    # Agent se JSON expected hai. Agar kabhi invalid JSON/prose aa jaye,
    # usko output maan kar app ko crash hone se bachate hain.
    try:
        return json.loads(str(message.content))  # JSON parse
    except json.JSONDecodeError:
        return {  # Fallback to output
            "step": "output",  # Treat as final
            "content": str(message.content),  # Raw text
        }


def load_context_node(state: AgentState) -> dict[str, Any]:
    # LangGraph node 1:
    # Latest human message nikalta hai, phir:
    # - Mem0 se similar memories search karta hai.
    # - local knowledge graph load karta hai.
    # Dono context agent_node ko diye jate hain.
    last_user = next(  # Latest HumanMessage content
        (message.content for message in reversed(state["messages"]) if isinstance(message, HumanMessage)),
        "",
    )
    return {  # Context payload
        "memories": search_memories(str(last_user)),  # Mem0 search
        "knowledge_graph": load_knowledge_graph(),  # KG load
    }


def agent_node(state: AgentState) -> dict[str, Any]:
    # LangGraph node 2:
    # Ye actual LLM decision node hai.
    # It receives:
    # - system prompt
    # - relevant saved memory
    # - knowledge graph
    # - current chat messages
    #
    # Model JSON me decide karta hai:
    # - action: tool run karna hai
    # - output: final answer dena hai
    # - plan: small plan/status
    context = {  # Context bundle
        "memories": state.get("memories", []),  # Mem0 memories
        "knowledge_graph": state.get("knowledge_graph", {}),  # KG snapshot
    }
    messages = [  # Prompt + history
        SystemMessage(content=SYSTEM_PROMPT),  # Protocol rules
        SystemMessage(content=f"Relevant saved context:\n{json.dumps(context, indent=2)}"),  # Context
        *state["messages"],  # Conversation
    ]
    response = llm.bind(response_format={"type": "json_object"}).invoke(messages)  # LLM call
    parsed = parse_json_message(response)  # JSON parse

    if parsed.get("step") == "action":  # Tool action path
        # Action ko direct execute nahi karte. Pehle pending_action me store hota hai,
        # phir approval_node decide karta hai ki human approval chahiye ya nahi.
        return {  # Pending action set
            "messages": [response],  # Save response
            "pending_action": parsed,  # Hold action
            "approved": None,  # Approval pending
            "tool_output": None,  # No output yet
        }

    if parsed.get("step") == "output":  # Final output path
        # Final answer mil gaya, graph ko done mark kar do.
        return {  # Done state
            "messages": [response],  # Save response
            "done": True,  # Mark done
            "pending_action": None,  # Clear action
        }

    plan_content = parsed.get("content")  # Plan content
    if isinstance(plan_content, str) and plan_content.strip().endswith("?"):  # Question in plan
        # Safety fix:
        # Agar model question ko plan me repeat karne lage, usko ask_human tool me convert kar dete hain.
        # Isse ek hi baar terminal me human se answer pucha jata hai.
        return {  # Convert to ask_human
            "messages": [response],  # Save response
            "pending_action": {
                "step": "action",  # Action step
                "content": "Ask the human for missing information.",  # Reason
                "function": "ask_human",  # Tool
                "input": plan_content.strip(),  # Question
            },
            "approved": True,  # Auto-approve ask_human
            "tool_output": None,  # No output yet
        }

    if plan_content:  # Plan log
        print(f"plan: {plan_content}")  # Terminal log
    return {  # Default plan path
        "messages": [response],  # Save response
        "pending_action": None,  # No action
        "approved": None,  # No approval
    }


def needs_approval(action: dict[str, Any]) -> bool:
    # Approval policy:
    # - write_file/run_command always approval maangte hain.
    # - content me risky words aaye, to bhi approval maangte hain.
    tool_name = action.get("function")  # Tool name
    content = f"{action.get('content', '')} {action.get('input', '')}".lower()  # Combined text
    complex_words = {"complex", "delete", "remove", "overwrite", "install", "migrate", "refactor"}  # Risky words
    return tool_name in COMPLEX_TOOLS or any(word in content for word in complex_words)  # Approval decision


def approval_node(state: AgentState) -> dict[str, Any]:
    # LangGraph node 3:
    # Pending action ko inspect karta hai.
    # Agar risky/complex hai, terminal me yes/no puchta hai.
    # Agar simple read_file/ask_human hai, auto-approved.
    action = state["pending_action"] or {}  # Pending action
    if not needs_approval(action):  # Simple action
        return {"approved": True}  # Auto-approve

    print("\nHuman approval required")  # Prompt header
    print(f"Reason: {action.get('content')}")  # Reason
    print(f"Tool: {action.get('function')}")  # Tool name
    print(f"Input: {action.get('input')}")  # Tool input
    answer = input("Approve? (yes/no) > ").strip().lower()  # Human answer
    approved = answer in {"y", "yes"}  # Yes/no to bool
    return {"approved": approved}  # Approval result


def tool_node(state: AgentState) -> dict[str, Any]:
    # LangGraph node 4:
    # Approved action ko actual Python tool se execute karta hai.
    # Tool result ko AIMessage observe format me messages me append karta hai,
    # taaki agent next loop me result dekh kar continue kar sake.
    action = state["pending_action"] or {}  # Pending action
    tool_name = action.get("function")  # Tool name
    tool_input = action.get("input")  # Tool input

    if state.get("approved") is False:  # Rejected by human
        output = "Human rejected this action. Choose a safer path or ask_human for clarification."  # Reject msg
    elif tool_name not in TOOLS:  # Unknown tool
        output = f"Unknown tool: {tool_name}"  # Error msg
    else:
        tool_input = normalize_tool_input(tool_name, tool_input, action)  # Normalize input
        try:
            if isinstance(tool_input, dict):  # Dict args
                output = TOOLS[tool_name](**tool_input)  # **kwargs
            else:
                output = TOOLS[tool_name](tool_input)  # Single arg
        except Exception as exc:
            output = f"Tool error: {exc}"  # Tool error

    observation = AIMessage(content=json.dumps({"step": "observe", "output": output}, default=str))  # Observe msg
    return {  # Tool result state
        "messages": [observation],  # Add observation
        "tool_output": output,  # Save output
        "pending_action": None,  # Clear action
        "approved": None,  # Reset approval
    }


def save_memory_node(state: AgentState) -> dict[str, Any]:
    # LangGraph node 5:
    # Har tool/output ke baad memory save ka step.
    # - last kuch messages Mem0 me add hote hain.
    # - same text se knowledge graph facts extract hote hain.
    # - full chat snapshot JSON file me save hota hai.
    last_messages = state["messages"][-4:]  # Last few msgs
    memory_text = "\n".join(f"{message.type}: {message.content}" for message in last_messages)  # Combined text
    add_memory(memory_text)  # Mem0 add

    try:
        response = kg_llm.bind(response_format={"type": "json_object"}).invoke(  # KG extraction
            [
                SystemMessage(content=KG_PROMPT),  # KG prompt
                HumanMessage(content=memory_text),  # Text for extraction
            ]
        )
        extracted = json.loads(str(response.content))  # Parsed KG output
        kg = merge_knowledge_graph(load_knowledge_graph(), extracted)  # Merge KG
        save_knowledge_graph(kg)  # Save KG
    except Exception:
        pass  # KG errors ignore

    save_snapshot(state)  # Snapshot save
    return {}  # No update


def route_after_agent(state: AgentState) -> Literal["approve", "save_memory", "agent"]:
    # Conditional edge after agent:
    # - final output hai -> memory save
    # - tool action hai -> approval
    # - sirf plan hai -> agent ko dobara call
    if state.get("done"):  # Final output
        return "save_memory"  # Save then end
    if state.get("pending_action"):  # Tool action pending
        return "approve"  # Approval path
    return "agent"  # Loop back


def route_after_save(state: AgentState) -> Literal["agent", "__end__"]:
    # Conditional edge after save_memory:
    # - done hai -> graph end
    # - tool observation save hua hai -> agent ko result dikhao, next decision lo
    if state.get("done"):  # Done state
        return END  # Graph end
    return "agent"  # Continue loop


def build_graph():
    # Pure LangGraph workflow yahan define hota hai.
    #
    # Flow:
    # START
    #   -> load_context
    #   -> agent
    #   -> approve (if action)
    #   -> tool
    #   -> save_memory
    #   -> agent again OR END
    #
    # checkpointer=MemorySaver() graph ke internal thread state ko checkpoint karta hai.
    # Disk restart ke liye hum separately save_snapshot/load_snapshot use kar rahe hain.
    builder = StateGraph(AgentState)  # Graph builder init
    builder.add_node("load_context", load_context_node)  # Node: load context
    builder.add_node("agent", agent_node)  # Node: LLM agent
    builder.add_node("approve", approval_node)  # Node: approval
    builder.add_node("tool", tool_node)  # Node: tool run
    builder.add_node("save_memory", save_memory_node)  # Node: memory save

    builder.add_edge(START, "load_context")  # Start -> load_context
    builder.add_edge("load_context", "agent")  # Context -> agent
    builder.add_conditional_edges("agent", route_after_agent)  # Agent routing
    builder.add_edge("approve", "tool")  # Approval -> tool
    builder.add_edge("tool", "save_memory")  # Tool -> save_memory
    builder.add_conditional_edges("save_memory", route_after_save)  # Save routing

    return builder.compile(checkpointer=MemorySaver())  # Graph compile


def message_to_dict(message: BaseMessage) -> dict[str, str]:
    # LangChain message object ko JSON-serializable dict me convert karta hai.
    return {"type": message.type, "content": str(message.content)}  # JSON-safe dict


def dict_to_message(item: dict[str, str]) -> BaseMessage:
    # Snapshot JSON se message object wapas banata hai.
    message_type = item.get("type")  # Type string
    content = item.get("content", "")  # Content string
    if message_type == "human":  # Human case
        return HumanMessage(content=content)
    if message_type == "ai":  # AI case
        return AIMessage(content=content)
    return SystemMessage(content=content)  # Default system


def load_snapshot_messages() -> list[BaseMessage]:
    # App restart hone par purani conversation disk se load hoti hai.
    if not SNAPSHOT_FILE.exists():  # No snapshot
        return []  # Empty list
    with SNAPSHOT_FILE.open("r", encoding="utf-8") as file:  # File open
        data = json.load(file)  # JSON load
    return [dict_to_message(item) for item in data.get("messages", [])]  # Convert list


def save_snapshot(state: AgentState):
    # Current messages ko disk par save karta hai.
    # Ye LangGraph MemorySaver se alag hai: MemorySaver process ke andar checkpoint karta hai,
    # ye JSON snapshot restart ke baad bhi messages recover karne ke liye hai.
    ensure_data_dir()  # Data dir ensure
    with SNAPSHOT_FILE.open("w", encoding="utf-8") as file:  # File open
        json.dump(  # JSON save
            {"messages": [message_to_dict(message) for message in state.get("messages", [])]},  # Messages list
            file,  # File handle
            indent=2,  # Pretty indent
        )


def main():
    # CLI entry point:
    # - graph build karo
    # - previous snapshot load karo
    # - REPL loop chalao
    # - har user query ko graph.invoke me bhejo
    graph = build_graph()  # Graph build
    config = {"configurable": {"thread_id": THREAD_ID}}  # Thread config
    messages = load_snapshot_messages()  # Snapshot load

    print("LangGraph Mini Cursor with HITL, checkpointing, Mem0, and knowledge graph")  # Header
    print("Type 'exit' to quit, 'clear memory' to reset local saved state.\n")  # Help

    while True:  # REPL loop
        user_query = input("> ").strip()  # User input
        if user_query.lower() in {"exit", "quit"}:  # Exit command
            break  # Loop end

        if user_query.lower() == "clear memory":  # Reset command
            # Reset command:
            # local snapshot + knowledge graph delete karta hai,
            # aur Mem0 memory clear karne ki try karta hai.
            messages = []  # Clear in-memory messages
            ensure_data_dir()  # Data dir ensure
            for path in (SNAPSHOT_FILE, KG_FILE):  # Files to delete
                if path.exists():  # File exists?
                    path.unlink()  # Delete file
            if memory is not None:  # Mem0 present
                try:
                    memory.delete_all(user_id=THREAD_ID)  # Clear Mem0
                except Exception:
                    pass  # Ignore errors
            print("Local snapshot, knowledge graph, and Mem0 memories cleared.")  # Confirmation
            continue  # Next loop

        state: AgentState = {  # Initial state
            # New graph run ka initial state.
            # Previous messages + current HumanMessage pass karte hain,
            # baaki fields graph nodes fill karenge.
            "messages": [*messages, HumanMessage(content=user_query)],  # History + new input
            "memories": [],  # Filled by load_context
            "knowledge_graph": {},  # Filled by load_context
            "pending_action": None,  # No action yet
            "tool_output": None,  # No tool output yet
            "approved": None,  # No approval yet
            "done": False,  # Not done
        }

        final_state = graph.invoke(state, config=config)  # Graph run
        messages = final_state["messages"]  # Updated messages

        last_ai = next(  # Last AI message find
            (message for message in reversed(messages) if isinstance(message, AIMessage)),
            None,
        )
        if last_ai:  # If AI msg exists
            parsed = parse_json_message(last_ai)  # Parse JSON
            if parsed.get("step") == "output":  # Final output
                print(parsed.get("content"))  # Print answer


if __name__ == "__main__":  # Script entry guard
    main()  # Run main

# Workflow (ASCII diagram)
#
#   [START]
#      |
#      v
#   load_snapshot_messages
#      |
#      v
#   build_graph
#      |
#      v
#   while True (REPL)
#      |
#      v
#   Human input
#      |
#      v
#   graph.invoke
#      |
#      v
#   load_context -> agent
#      |
#      +--> action? -> approve -> tool -> save_memory -> agent
#      |
#      +--> output -> save_memory -> [END]
