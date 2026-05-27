# LangGraph: Nodes, Edges & Checkpointing — Complete Notes 🧠

> **Chai piyo aur padho** ☕ | LangGraph ka full breakdown — nodes se lekar checkpointing tak, streaming, human-in-the-loop, aur `.invoke()` sab kuch cover hai.

---

## 📌 Table of Contents

1. [LangGraph Kya Hai?](#1-langgraph-kya-hai)
2. [StateGraph & State](#2-stategraph--state)
3. [Nodes — The Building Blocks](#3-nodes--the-building-blocks)
4. [Edges — Flow Control](#4-edges--flow-control)
5. [`.invoke()` vs `.stream()`](#5-invoke-vs-stream)
6. [Checkpointing — State Ka Backup System](#6-checkpointing--state-ka-backup-system)
7. [Human-in-the-Loop (HITL)](#7-human-in-the-loop-hitl)
8. [Multi-Agent & Subgraphs](#8-multi-agent--subgraphs)
9. [Practical Code Examples](#9-practical-code-examples)
10. [Yaad Rakhne Wali Baatein](#10-yaad-rakhne-wali-baatein)

---

## 1. LangGraph Kya Hai?

LangGraph ek **graph-based framework** hai jo LangChain ke upar bana hai. Ye complex, multi-step, **stateful AI workflows** banane ke liye use hota hai.

```
Normal LangChain:   Chain A → Chain B → Chain C    (linear, no memory between steps)
LangGraph:          Node A ⇄ Node B ⇄ Node C       (graph, shared state, loops allowed)
```

### Kyun Use Karein?

| Feature | LangChain (LCEL) | LangGraph |
|---|---|---|
| State management | ❌ Manual | ✅ Built-in |
| Loops / Cycles | ❌ Nahi | ✅ Haan |
| Human-in-the-loop | ❌ Difficult | ✅ Native |
| Checkpointing | ❌ Nahi | ✅ Thread-based |
| Multi-agent | ❌ Complex | ✅ First-class |

> **Analogy:** LangChain ek recipe hai. LangGraph ek **kitchen workflow** hai jahan multiple chefs (agents) ek saath kaam karte hain, aur agar koi chef galti kare toh wapas pichle step pe ja sakte ho.

---

## 2. StateGraph & State

LangGraph ka core concept hai **shared state** — ek dictionary jo har node ke beech share hoti hai.

### State Define Karna

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

# State schema — yahi graph ki "memory" hai
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # messages append hote hain (reducer)
    user_query: str
    context: str
    final_answer: str
```

### `Annotated` + Reducer Kya Hota Hai?

```
Default behavior:  Node ka return value → state ko OVERWRITE kar deta hai
With Annotated:    operator.add use karo → list mein APPEND hoga, overwrite nahi
```

```python
# Bina reducer ke — overwrite
class State(TypedDict):
    messages: list       # Node 2 ka output, Node 1 ka output overwrite kar dega!

# Reducer ke saath — accumulate
class State(TypedDict):
    messages: Annotated[list, operator.add]  # Dono nodes ke outputs merge honge ✅
```

---

## 3. Nodes — The Building Blocks

**Node = ek Python function** jo current state leta hai aur updated state return karta hai.

### Node ka Basic Structure

```python
def my_node(state: AgentState) -> dict:
    """
    Input:  State dictionary
    Output: Dictionary with ONLY the keys you want to update
    """
    query = state["user_query"]
    
    # Kuch karo — LLM call, tool call, DB query, etc.
    result = llm.invoke(query)
    
    # Sirf updated keys return karo
    return {"final_answer": result.content}
```

### Node Types (Whiteboard se)

```
┌─────────────────────────────────────────────────────────┐
│                    NODE TYPES                           │
├─────────────────┬───────────────────────────────────────┤
│ Regular Node    │ Simple Python function                │
│                 │ def process(state) → dict             │
├─────────────────┼───────────────────────────────────────┤
│ LLM Node        │ LLM call karta hai                    │
│                 │ messages state update karta hai       │
├─────────────────┼───────────────────────────────────────┤
│ Tool Node       │ Tools execute karta hai               │
│                 │ ToolExecutor ya custom                │
├─────────────────┼───────────────────────────────────────┤
│ Conditional     │ Routing logic (edge ke saath use)     │
│ Node            │ Decide karta hai aage kahan jaana     │
└─────────────────┴───────────────────────────────────────┘
```

### Nodes Graph Mein Add Karna

```python
# Graph create karo
graph = StateGraph(AgentState)

# Nodes add karo
graph.add_node("retriever", retriever_node)      # RAG retrieval
graph.add_node("llm_call", llm_node)             # LLM response
graph.add_node("tool_executor", tool_node)       # Tool execution
graph.add_node("human_check", human_node)        # Human review

# Entry point set karo
graph.set_entry_point("retriever")
```

---

## 4. Edges — Flow Control

Edges define karte hain ki ek node ke baad kaunsa node chalega.

### Edge Types

```python
# 1. Simple/Direct Edge — hamesha A ke baad B chalega
graph.add_edge("retriever", "llm_call")

# 2. END Edge — graph khatam karo
graph.add_edge("llm_call", END)

# 3. Conditional Edge — state dekh ke decide karo
graph.add_conditional_edges(
    "llm_call",           # Source node
    routing_function,     # Function jo decide karta hai
    {
        "use_tool": "tool_executor",   # Agar "use_tool" return hua
        "done": END,                   # Agar "done" return hua
        "needs_human": "human_check"   # Agar "needs_human" return hua
    }
)

# Routing function kuch aisa hoga:
def routing_function(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "use_tool"
    elif state.get("needs_review"):
        return "needs_human"
    return "done"
```

### ASCII Flow Diagram (Whiteboard wala)

```
                    START
                      │
                      ▼
              ┌───────────────┐
              │   retriever   │  ← RAG: relevant docs fetch karo
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   llm_call    │  ← LLM se answer generate karo
              └───────┬───────┘
                      │
             routing_function()
            /         │         \
           ▼          ▼          ▼
    "use_tool"     "done"    "needs_human"
        │             │            │
        ▼             ▼            ▼
  tool_executor      END      human_check
        │                          │
        └──────────────────────────┘
              (back to llm_call)
```

---

## 5. `.invoke()` vs `.stream()`

### Graph Compile aur Run Karna

```python
# Graph compile karo (checkpointer ke saath ya bina)
app = graph.compile()

# Ya checkpointer ke saath:
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

### `.invoke(data)` — Whiteboard mein dikh raha tha

```python
# Synchronous — poora graph run karo, final state return karo
config = {"configurable": {"thread_id": "user_123"}}

result = app.invoke(
    {"user_query": "Mujhe IPC 302 ke baare mein batao"},
    config=config
)
print(result["final_answer"])
```

```
invoke(data) kya karta hai:
Input State → Node A → Node B → Node C → Final State return
                                          (ek hi baar, blocking)
```

### `.stream()` — Whiteboard mein `Stream()` likha tha

```python
# Async — har node ke baad intermediate output milta hai
for chunk in app.stream(
    {"user_query": "Bail application kaise file karein?"},
    config=config
):
    # chunk = {node_name: node_output}
    node_name = list(chunk.keys())[0]
    print(f"Node '{node_name}' complete: {chunk[node_name]}")
```

```
stream() ka flow:
Input → Node A runs → yields {A: output} → Node B runs → yields {B: output} → ...
                ↑                                   ↑
          Yahan milta hai                    Yahan milta hai (real-time)
```

## invoke basically poora graph run karta hai aur final state return karta hai. stream() har node ke baad intermediate output deta hai, jisse real-time updates milte hain.

### Comparison Table

| Feature | `.invoke()` | `.stream()` |
|---|---|---|
| Return type | Final state dict | Generator (yields per node) |
| Blocking | Yes | No (streaming) |
| Use case | Simple queries | Real-time UI updates |
| Token streaming | ❌ | ✅ (with `stream_mode="messages"`) |
| LegalSaathi use | Backend APIs | Frontend chat streaming |

### Token-Level Streaming

```python
# Sirf LLM tokens stream karo (words as they generate)
for chunk in app.stream(
    input_data,
    config=config,
    stream_mode="messages"  # "values", "updates", "messages"
):
    if chunk[1]["langgraph_node"] == "llm_call":
        print(chunk[0].content, end="", flush=True)
```

---

## 6. Checkpointing — State Ka Backup System

> **Analogy:** Checkpointing = Video game ka **save point** system. Har level ke baad game save hoti hai. Agar character mar jaye, wapas save point se start hota hai.

Whiteboard mein clearly `Checkpointing` ka diagram tha jisme multiple nodes ke saath DB connections the.

### Checkpointing Kya Karta Hai?

```
BINA Checkpointing:
Run 1: State A → B → C → D (graph khatam, state gone ❌)
Run 2: State A → B → C → D (fresh start, no memory ❌)

CHECKPOINTING KE SAATH:
Run 1: State A → [SAVE to DB] → B → [SAVE] → C → [SAVE] → D
Run 2: Thread ID dene par wahi state wapas load! ✅
```

### Available Checkpointers

```python
# 1. In-Memory (Development only)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# 2. SQLite (Local/Development)
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# 3. PostgreSQL (Production — LegalSaathi ke liye!)
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host:5432/legalsaathi_db"
)

# 4. MongoDB (Agar pehle se MongoDB hai)
from langgraph.checkpoint.mongodb import MongoDBSaver
checkpointer = MongoDBSaver.from_conn_string("mongodb://...")
```

### Thread ID — Har User Ki Apni State

```python
# Thread ID = ek unique conversation/session identifier
# LegalSaathi mein: thread_id = user_id + case_id

config = {
    "configurable": {
        "thread_id": "user_42_case_ipc302"  # Unique per conversation
    }
}

# First message
result1 = app.invoke({"messages": [HumanMessage("IPC 302 kya hai?")]}, config)

# Second message — SAME thread_id, toh pehla context yaad hai!
result2 = app.invoke({"messages": [HumanMessage("Isme bail milti hai?")]}, config)
# LLM ko pata hai ki user IPC 302 ke baare mein baat kar raha tha ✅
```

### Checkpointing Internals — Whiteboard ka DB Diagram

```
Thread: "user_42_case_ipc302"

Checkpoint 1 (Node: retriever)          Checkpoint 2 (Node: llm_call)
┌─────────────────────────┐             ┌─────────────────────────┐
│ thread_id: user_42_...  │             │ thread_id: user_42_...  │
│ checkpoint_id: abc123   │             │ checkpoint_id: def456   │
│ node: retriever         │             │ node: llm_call          │
│ state: {                │             │ state: {                │
│   messages: [...],      │ ──saved──▶  │   messages: [...],      │
│   context: "IPC docs"   │             │   context: "IPC docs",  │
│ }                       │             │   llm_response: "..."   │
│ next: ["llm_call"]      │             │ }                       │
└─────────────────────────┘             │ next: [END]             │
                                        └─────────────────────────┘
                                                     │
                                              DB mein save!
                                              (PostgreSQL/MongoDB)
```

### State Wapas Load Karna

```python
# Current state dekho
current_state = app.get_state(config)
print(current_state.values)        # State dictionary
print(current_state.next)          # Agle nodes kaun se hain
print(current_state.metadata)      # Checkpoint info

# State history dekho (time travel!)
for state in app.get_state_history(config):
    print(f"Step: {state.metadata['step']}")
    print(f"State: {state.values}")

# Purani state se resume karo
old_config = {
    "configurable": {
        "thread_id": "user_42_case_ipc302",
        "checkpoint_id": "abc123"  # specific checkpoint
    }
}
result = app.invoke(None, old_config)  # Wahan se shuru jahan chhoda tha
```

### State Update Karna (Time Travel + Correction)

```python
# Kisi bhi point pe state manually update karo
app.update_state(
    config,
    {"user_query": "Updated query"},  # Updated values
    as_node="retriever"               # Kaunse node ki taraf se update aaya
)

# Fir graph resume karo
app.invoke(None, config)
```

---

## 7. Human-in-the-Loop (HITL)

## human in the loop ka basicalay matlab hai ki AI workflow ke beech mein human intervention allow karna — jaise legal advice generate karne ke baad human lawyer se review karwana.
## in simple words we can say that human in the loop is a design pattern where humans are involved in the AI decision-making process, especially for critical or high-stakes tasks.

Whiteboard mein `human_assistance_tool` aur `abc123 response` dikh raha tha. Ye HITL pattern hai.

> **Analogy:** AI ek junior lawyer hai. Important decisions mein woh senior lawyer (human) ko pause karke poochta hai — approve karo toh aage badho, reject karo toh dobara karo.

### interrupt_before — Node Se Pehle Roko

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_check"]  # Is node se PEHLE ruko
)

# Graph chalao — human_check node pe automatically ruk jayega
result = app.invoke({"messages": [HumanMessage("Yeh case file karein?")]}, config)

# Dekho graph kahan ruka
state = app.get_state(config)
print(state.next)  # Output: ('human_check',)  ← Yahan ruka hai

# Ab human review karta hai...
# Human approve karta hai — resume!
app.invoke(None, config)
```

### interrupt_after — Node Ke Baad Roko

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_after=["llm_call"]  # LLM response ke BAAD ruko (review ke liye)
)
```

### Human Assistance Tool Pattern (Whiteboard wala)

```python
# Whiteboard mein: AI → human_assistance_tool → query() → abc123 response
from langchain_core.tools import tool

@tool
def human_assistance_tool(query: str) -> str:
    """Human se input maango jab AI confident na ho."""
    # Yahan real app mein: WebSocket/API se human ko notify karo
    # Aur unka response wait karo
    human_response = input(f"\n[HUMAN REQUIRED]\nQuery: {query}\nYour response: ")
    return human_response

# State mein store karo
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    abc123: str        # Whiteboard mein "abc123" dikha tha — thread/case ID
    pending_human: bool
```

### Complete HITL Flow

```
User sends query
      │
      ▼
  llm_call node
      │
  "needs_review" condition
      │
      ▼
  [INTERRUPT] ← Graph yahan ruk jata hai
      │
  State DB mein save
      │
  Human ko notify (email/webhook/UI)
      │
  Human reviews & approves/modifies
      │
  app.invoke(None, config)  ← Resume
      │
      ▼
  Continue from where stopped
```

---

## 8. Multi-Agent & Subgraphs

Whiteboard mein multiple agents (User A, User B type) aur unke beech routing dikh raha tha.

### Subgraph Pattern

```python
# Child graph — specialized task ke liye
rag_graph = StateGraph(RAGState)
rag_graph.add_node("retrieve", retrieve_node)
rag_graph.add_node("rerank", rerank_node)
rag_subgraph = rag_graph.compile()

# Parent graph mein child graph ko node ki tarah use karo
main_graph = StateGraph(MainState)
main_graph.add_node("rag_pipeline", rag_subgraph)  # Subgraph = node!
main_graph.add_node("llm_response", llm_node)
```

### LegalSaathi Multi-Agent Architecture

```
User Query
    │
    ▼
Router Agent ──────────────────────────────┐
    │                                      │
    ├── "legal_query"                      ├── "general_query"
    │         │                            │         │
    ▼         ▼                            │         ▼
RAG Agent   Draft Agent              General LLM
(Qdrant)    (Document gen)                │
    │              │                      │
    └──────────────┴──────────────────────┘
                   │
              Final Response
                   │
              Human Review (HITL)
                   │
              User ✅
```

---

## 9. Practical Code Examples

### Complete LegalSaathi-Style Graph

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage, AIMessage
import operator

# ─── STATE ───────────────────────────────────────────────
class LegalState(TypedDict):
    messages: Annotated[list, operator.add]
    query: str
    retrieved_docs: list
    legal_context: str
    draft_response: str
    needs_review: bool
    case_id: str

# ─── NODES ───────────────────────────────────────────────
def retriever_node(state: LegalState) -> dict:
    """Qdrant se relevant legal docs fetch karo"""
    from qdrant_client import QdrantClient
    # ... retrieval logic
    docs = ["IPC Section 302 text...", "Bail provisions..."]
    return {"retrieved_docs": docs, "legal_context": "\n".join(docs)}

def llm_node(state: LegalState) -> dict:
    """LLM se legal advice generate karo"""
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4")
    
    prompt = f"""
    You are LegalSaathi, an AI legal assistant for India.
    Context: {state['legal_context']}
    Query: {state['query']}
    
    Provide clear legal guidance in simple Hindi/English.
    """
    response = llm.invoke([HumanMessage(prompt)])
    
    # High-stakes queries ke liye human review flag karo
    needs_review = any(word in state['query'].lower() 
                      for word in ['murder', 'rape', 'death', 'arrest'])
    
    return {
        "messages": [AIMessage(response.content)],
        "draft_response": response.content,
        "needs_review": needs_review
    }

def human_review_node(state: LegalState) -> dict:
    """Human lawyer review karta hai"""
    # Real app mein: lawyer ko notification, UI pe dikhaao
    print(f"\n⚠️ LEGAL REVIEW REQUIRED\n{state['draft_response']}")
    return {"needs_review": False}

# ─── ROUTING ─────────────────────────────────────────────
def route_after_llm(state: LegalState) -> str:
    if state.get("needs_review"):
        return "needs_human"
    return "done"

# ─── GRAPH BUILD ─────────────────────────────────────────
graph = StateGraph(LegalState)

graph.add_node("retriever", retriever_node)
graph.add_node("llm_call", llm_node)
graph.add_node("human_review", human_review_node)

graph.set_entry_point("retriever")
graph.add_edge("retriever", "llm_call")
graph.add_conditional_edges(
    "llm_call",
    route_after_llm,
    {"needs_human": "human_review", "done": END}
)
graph.add_edge("human_review", END)

# ─── COMPILE WITH CHECKPOINTING ──────────────────────────
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/legalsaathi"
)
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]  # HITL
)

# ─── RUN ─────────────────────────────────────────────────
config = {"configurable": {"thread_id": "user_42_session_1"}}

# Invoke
result = app.invoke(
    {"query": "IPC 302 mein bail kaise milti hai?", "case_id": "CASE_001"},
    config=config
)
```

---

## 10. Yaad Rakhne Wali Baatein

```
╔══════════════════════════════════════════════════════════════╗
║              LANGGRAPH GOLDEN RULES 🏆                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. NODE = function(state) → dict                            ║
║     Sirf changed keys return karo, pura state nahi           ║
║                                                              ║
║  2. STATE = shared memory between ALL nodes                  ║
║     TypedDict use karo, Annotated for reducers               ║
║                                                              ║
║  3. CHECKPOINTING = thread_id ke basis pe save/resume        ║
║     Har conversation ka alag thread_id hona chahiye          ║
║                                                              ║
║  4. .invoke() = blocking, full run, final state              ║
║     .stream() = non-blocking, per-node updates               ║
║                                                              ║
║  5. HITL = interrupt_before/after + app.invoke(None, config) ║
║     None pass karo resume ke liye (naya input nahi)          ║
║                                                              ║
║  6. CONDITIONAL EDGES = routing function returns string      ║
║     String ko edges dict ke key se match karo                ║
║                                                              ║
║  7. END import karo: from langgraph.graph import END         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Quick Reference — Common Patterns

```python
# Pattern 1: Basic invoke
result = app.invoke({"query": "..."}, config)

# Pattern 2: Streaming
for chunk in app.stream(input, config):
    print(chunk)

# Pattern 3: Check where graph stopped (HITL)
state = app.get_state(config)
print(state.next)   # Pending nodes

# Pattern 4: Resume after human approval
app.invoke(None, config)  # None = resume, don't restart

# Pattern 5: State update (correction)
app.update_state(config, {"key": "new_value"}, as_node="node_name")

# Pattern 6: History/Time travel
for checkpoint in app.get_state_history(config):
    print(checkpoint.metadata['step'], checkpoint.values)
```

### Interview Mein Pooche Jane Wale Questions

**Q: LangGraph aur LangChain mein kya farak hai?**
> LangChain LCEL linear chains banata hai. LangGraph **cyclic graphs** banata hai jahan nodes loops kar sakti hain, state share kiya jata hai, aur human-in-the-loop natively supported hai.

**Q: Checkpointing aur Memory mein farak?**
> Memory = LLM ko context dena (conversation history).
> Checkpointing = **graph execution state** save karna — kon sa node chala, state kya thi, resume kahan se karna hai.

**Q: thread_id kab naya banana chahiye?**
> Har nayi independent conversation/session ke liye naya `thread_id`. Same user ke different cases = different thread IDs.

**Q: interrupt_before vs interrupt_after?**
> `interrupt_before=["node"]` → node chalane se **pehle** ruko (human ko decide karne do ki chalana hai ya nahi).
> `interrupt_after=["node"]` → node chalane ke **baad** ruko (output review karo, modify kar sako toh karo).

---

*Notes by Prince Seth | LegalSaathi AI Project | LangGraph v0.2+*
*Reference: LangChain Docs + Chai aur Code learnings*

---

## 11. Audio-to-Audio Pipeline (Whiteboard Diagram)

> **Ye wala part:** Real-time voice AI assistant banane ka architecture — jaise ek AI interviewer ya legal helpline jo bolke sawal karo aur bolke jawab de.

### System Overview

```
                    ┌─────────────────────────────────────┐
                    │         AUDIO-TO-AUDIO LOOP         │
                    │                                     │
  User bolta hai    │  ┌─────┐   ┌────────────┐   ┌─────┐│
  ────────────────▶ │  │ STT │──▶│ Text 2 Text│──▶│ TTS ││──▶ User sunta hai
                    │  └─────┘   └────────────┘   └─────┘│
                    │     ▲                               │
                    │     │  5 second = 1 photo (video)   │
                    └─────────────────────────────────────┘
```

**Iska matlab:** Microphone se audio aaya → text bana → LLM ne process kiya → wapas audio bana → speaker pe gaya. Yeh loop continuously chalta rehta hai.

---

### Component 1: STT — Speech to Text

**Kya karta hai:** User ki awaaz ko text mein convert karta hai taaki LLM samajh sake.

**Kaise kaam karta hai:**

```
Raw Audio (WAV/MP3) ──▶ STT Model ──▶ "IPC 302 kya hota hai?"
     (bytes)          (Whisper etc.)        (text string)
```

**Popular STT Options:**

| Tool | Type | Speed | Cost | Best For |
|---|---|---|---|---|
| OpenAI Whisper | Open source | Medium | Free (self-host) | Offline/Privacy |
| Whisper API | Cloud | Fast | $0.006/min | Simple integration |
| Deepgram | Cloud | Fastest | Pay-per-use | Real-time streaming |
| AssemblyAI | Cloud | Fast | Pay-per-use | Async processing |
| Google Speech API | Cloud | Fast | Pay-per-use | Google ecosystem |

**Key Concepts:**
- **Chunking:** Audio ko chote pieces mein tod ke process karo (latency kam hoti hai)
- **VAD (Voice Activity Detection):** Detect karo ki user bol raha hai ya nahi — silence ko skip karo
- **Language:** Hindi/Hinglish ke liye Whisper sab se achha hai

---

### Component 2: Text 2 Text — LLM Processing

**Whiteboard mein yeh middle node tha** — yahan LLM actual "thinking" karta hai.

```
"IPC 302 kya hota hai?"
          │
          ▼
  ┌───────────────────┐
  │   system prompt   │  ← Personality define karo ("Tu LegalSaathi hai...")
  │   + voice config  │  ← Tone, language, response length set karo
  │   + user query    │
  └────────┬──────────┘
           │
           ▼
        ChatGPT / Claude
           │
           ▼
  "IPC 302 murder ka section hai..."
```

**Voice ke liye special considerations:**
- **Response length:** Text ke liye 500 words theek hai, voice ke liye 2-3 sentences. LLM ko bolo "respond in 2-3 sentences only, conversational tone"
- **No markdown:** Voice mein `**bold**` ya `- bullets` nahi bolte. System prompt mein explicitly likhna hoga "no markdown, no lists"
- **Natural language:** "First... Second... Third..." instead of bullets

---

### Component 3: TTS — Text to Speech

**Kya karta hai:** LLM ka text output wapas human-like awaaz mein convert karta hai.

```
"IPC 302 murder ka section hai..."
          │
          ▼
     TTS Engine
          │
          ▼
  Audio bytes (MP3/WAV) ──▶ Speaker/Browser
```

**Popular TTS Options:**

| Tool | Voice Quality | Latency | Cost | Special |
|---|---|---|---|---|
| OpenAI TTS | Excellent | Medium | $15/1M chars | 6 voices |
| ElevenLabs | Best | Medium | Pay-per-use | Voice cloning |
| Google TTS | Good | Fast | Pay-per-use | 200+ languages |
| pyttsx3 | Basic | Instant | Free | Offline only |
| Coqui TTS | Good | Slow | Free | Open source |

**Natural sounding ke liye:** ElevenLabs sabse natural hai, OpenAI TTS sabse easy integrate karna hai.

---

### Full Pipeline Flow (Whiteboard ka poora diagram)

```
┌──────────────────────────────────────────────────────────────┐
│                    FASTAPI SERVER (Python 🐍)                │
│                                                              │
│  User (mic)                                                  │
│     │                                                        │
│     ▼                                                        │
│  [STT Node]  ←── 5 sec audio chunks (video = photos playing)│
│     │                                                        │
│     ▼ text                                                   │
│  [Text2Text] ←── system_prompt + voice config ←── ChatGPT   │
│     │         (OpenAI KEY injected here)        ($40/M tokens)│
│     ▼ text                                                   │
│  [TTS Node]                                                  │
│     │                                                        │
│     ▼ audio                                                  │
│  User (speaker)         Natural voice output                 │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  User (browser/app)                                          │
│     │                                                        │
│     │  "signup/login request"                                │
│     ▼                                                        │
│  FastAPI ──▶ ChatGPT ──▶ token generate ──▶ User ko do      │
│                                                              │
│  Signed URL (S3) ──▶ User ko direct audio file access        │
│                       (server pe load nahi, S3 pe stored)    │
└──────────────────────────────────────────────────────────────┘
```

---

### Signed URL (S3) — Kya Hai Aur Kyun?

**Problem:** TTS se generated audio file server pe store hogi. Isko user ko kaise dena?

**Wrong approach:** Seedha file serve karo apne server se → server pe load, bandwidth waste

**Right approach: Signed URL**

```
1. TTS audio generate hua
2. File S3 bucket mein upload karo (private bucket)
3. S3 se ek "Signed URL" maango — temporary, expiring URL
   e.g., https://s3.amazonaws.com/bucket/audio.mp3?Expires=1234&Signature=xyz
4. Yeh URL user ko do
5. User seedha S3 se file download karta hai (server bypass)
6. URL 5-15 minutes mein expire ho jaata hai (security ✅)
```

**Fayde:**
- Server pe zero bandwidth load
- File secure hai (koi bhi URL guess nahi kar sakta)
- Scalable — lakhon users bhi handle ho sakte hain

---

### Video = Photos Playing (Whiteboard ka note)

**Yeh concept:** Agar tum ek video AI assistant bana rahe ho jo **video feed bhi samjhe**, toh:

```
Video stream
    │
    ▼
Har 5 seconds mein ek frame capture karo (1 photo)
    │
    ▼
Is photo ko Vision LLM ko bhejo (GPT-4V / Claude)
    │
    ▼
LLM visual context samjhta hai + audio transcription
    │
    ▼
Combined response generate karo
```

**Kyun 5 seconds?** Real-time video har second process karna bahut expensive hai ($). 5 second ka interval achha balance hai — context bhi milta hai, cost bhi kam.

---

### Architecture Summary — Theory Points

```
┌─────────────────────────────────────────────────────────┐
│              KEY ARCHITECTURAL DECISIONS                 │
├──────────────────────────┬──────────────────────────────┤
│ FastAPI server kyun?     │ Python ecosystem — same       │
│                          │ language as AI/ML libs       │
├──────────────────────────┼──────────────────────────────┤
│ OpenAI Key kahan rakhna? │ Server-side ONLY. Never      │
│                          │ frontend mein expose karo     │
├──────────────────────────┼──────────────────────────────┤
│ $40/M tokens kyun?       │ GPT-4 ka pricing — voice     │
│                          │ apps expensive hote hain      │
├──────────────────────────┼──────────────────────────────┤
│ system prompt + voice    │ LLM ko batao ki woh voice    │
│                          │ assistant hai, short reply do │
├──────────────────────────┼──────────────────────────────┤
│ Token (auth)?            │ JWT token — user identity    │
│                          │ verify karta hai              │
├──────────────────────────┼──────────────────────────────┤
│ S3 Signed URL kyun?      │ Server bypass, secure,       │
│                          │ auto-expiring access          │
└──────────────────────────┴──────────────────────────────┘
```

---

*Section added from whiteboard: Audio-to-Audio Pipeline (STT → Text2Text → TTS)*