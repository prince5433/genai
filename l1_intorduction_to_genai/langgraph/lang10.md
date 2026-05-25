# LangGraph — Complete Notes (Hinglish)
### Topics: Framework vs Library, LangGraph Architecture, State, Nodes, Edges, Routing, Autonomous Agents

---

## 1. Framework vs Library — Pehle Yeh Samjho

Yeh Image 1 ka core concept hai.

### Library kya hoti hai?
- Ek **tool** hai jo tum use karte ho apni marzi se
- Tum control mein ho — kab call karo, kaise use karo, sab tumhara decision
- Example: `requests`, `pandas`, `numpy`

```
Tum → Library ko call karte ho
(Control tumhare haath mein)
```

### Framework kya hota hai?
- Framework **tumhe call karta hai** — tum uski structure mein kaam karte ho
- Framework ka flow hota hai — tum bas apna code plug in karte ho
- Example: **FastAPI**, Django, LangGraph

```
Framework → Tumhare code ko call karta hai
(Control framework ke haath mein)
```

### FastAPI example:
```python
# FastAPI framework hai
# Tumne sirf route define kiya
# FastAPI khud decide karta hai kab call karna hai

@app.get("/users")      # ← tum sirf yeh likhte ho
def get_users():        # ← FastAPI khud call karta hai
    return users
```

> **Key Baat:** LangGraph ek **Framework** hai — tum nodes aur edges define karte ho, LangGraph khud flow manage karta hai.

---

## 2. LangGraph kya hai? — Simple Explanation

> **LangGraph = AI workflows banane ka framework jahan "graph" structure mein pipeline chalti hai**

- **Nodes** = Code blocks — har node ek kaam karta hai
- **Edges** = Flow define karte hain — node A ke baad kahan jaana hai

```
Sochlo ek assembly line:
Station 1 → Station 2 → Station 3 → END
(Node 1)  → (Node 2)  → (Node 3)  → END
```

### n8n vs LangGraph
> **"n8n is just UI of it"**

- n8n = LangGraph jaisa hi concept, bas **visual drag-drop interface** mein
- LangGraph = Code mein same cheez likhte ho
- Dono mein nodes aur edges hain — fark sirf UI vs Code ka hai

---

## 3. State — LangGraph ka Dil

### State kya hota hai?

> **State = Pipeline ka "memory" — har node is data ko padh sakta hai aur update kar sakta hai**

```python
class State(TypedDict):
    messages: list      # conversation history
    query: str          # current user query
    answer: str         # final answer
    route: str          # kahan jaana hai
```

### State kaise flow hota hai?

```
User Input aaya
    ↓
State bana: { message: "User is saying hey there" }
    ↓
Node 1 state padha → kuch kiya → state update kiya
    ↓
Node 2 updated state padha → kuch kiya → state update kiya
    ↓
END tak pohoncha
```

**Analogy:** Sochlo ek dak (courier) — dak ek jagah se doosri jagah jaata hai, har jagah pe kuch add hota hai (stamp, signature), par dak wahi rehta hai. State bhi aisa hi hai — ek packet jo har node se guzarta hai.

---

## 4. LangGraph ka Poora Flow — Practical Example

Diagram mein ek **Chatbot** example tha:

```
User Message: "Mujhe Python mein sorting algorithm batao"
    ↓
State: { message: "..." }
    ↓
┌─────────────────┐
│  detect_query   │  ← Query ka type identify karo
│  (Node 1)       │     "Yeh coding question hai"
└────────┬────────┘
         ↓
    State update:
    { route: "coding" }
         ↓
┌─────────────────┐
│     route       │  ← Routing node
│  (Node 2)       │     Decide karo kahan jaana hai
└────────┬────────┘
         ↓
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌──────────────┐
│solve_ │  │solve_simple_ │
│coding_│  │question      │
│question│ │(mini model)  │
│(gpt-4.1)│ └──────────────┘
└───────┘
    ↓
  END
```

### Model Routing bhi LangGraph mein:
- **Coding question** → `gpt-4.1` (powerful model)
- **Simple question** → `mini model` (cheap, fast)

---

## 5. Nodes — Code Blocks

Har node ek **Python function** hota hai jo:
1. State ko input mein leta hai
2. Kuch processing karta hai
3. Updated state return karta hai

```python
def detect_query(state: State) -> State:
    # State se message nikalo
    message = state["messages"][-1]

    # LLM se identify karo
    if "code" in message or "program" in message:
        state["route"] = "coding"
    else:
        state["route"] = "simple"

    return state  # updated state return karo
```

---

## 6. Edges — Flow Define Karte Hain

### Simple Edge (hamesha ek hi jagah jaata hai):
```
Node A → Node B   (always)
```

### Conditional Edge (condition pe depend karta hai):
```
route_node → solve_coding_question   (agar route == "coding")
           → solve_simple_question   (agar route == "simple")
```

### YML style flow (diagram mein tha):
```yaml
# Graph ka flow define karna
call_a -> b -> c    # A ke baad B, B ke baad C
b -> a -> c         # B ke baad A bhi ho sakta hai (loop!)
a -> d -> b -> c    # Install d dependency ke saath alternate path
```

---

## 7. Autonomous Agent — LangGraph ka Advanced Use

### Autonomous kya hota hai?

> **AI agent khud decide karta hai — kaunsa tool use karna hai, kab use karna hai, kab rukna hai**

```
User: "Research karo AI trends ke baare mein aur ek report banao"
    ↓
Autonomous Agent:
  Step 1: Web search karo (khud decide kiya)
  Step 2: Results analyze karo (khud decide kiya)
  Step 3: Draft likho (khud decide kiya)
  Step 4: Review karo (khud decide kiya)
  Step 5: Final report do
```

### Autonomous Agent ka LangGraph Flow:

```
Input
  ↓
[Agent Node] ← yeh node khud decide karta hai next step
  ↓       ↑
[Tool 1]  │  (result wapas agent ke paas jaata hai)
[Tool 2]  │
[Tool 3] ─┘
  ↓
END (jab agent satisfied ho)
```

**"While True" loop** — Diagram mein yeh likha tha:
```python
# Autonomous agent ka internal loop
while True:
    action = agent.decide_next_action(state)
    if action == "END":
        break
    state = execute_action(action, state)
```

---

## 8. Blocking Request — Human in the Loop

### Blocking Request kya hai?

> **Pipeline rok do — pehle human se approval lo, tab aage badho**

```
Agent: "Main ₹50,000 ka transaction karne wala hoon"
    ↓
[BLOCKING REQUEST] ← Pipeline ruk jaati hai
    ↓
Human ko notification: "Approve karo?"
    ↓
Human: "Haan, approve"
    ↓
Pipeline resume hoti hai → Transaction complete
```

### Kab use karo?

| Situation | Blocking chahiye? |
|---|---|
| Email draft karna | ❌ Nahi |
| Summary banana | ❌ Nahi |
| Payment process karna | ✅ Haan |
| AWS mein resources delete karna | ✅ Haan |
| Production pe deploy karna | ✅ Haan |

---

## 9. State Management — YML aur Dependencies

Diagram mein yeh flow tha:
```
call_a -> b -> c
b -> a -> c
pip install d
a -> d -> b -> c
```

### Kya matlab hai?

- Graph ke nodes ka **execution order** define hota hai
- Agar ek node doosre pe depend karta hai → dependency install karo (`pip install d`)
- Graph **non-linear** bhi ho sakta hai — loops possible hain

---

## 10. AI — 98% 

Diagram mein **"AI - 98%"** likha tha — yeh likely ek retrieval ya accuracy metric tha:

- RAG pipeline mein AI ka accuracy score
- 98% relevant results retrieve ho rahe hain
- Ya phir: 98% tasks AI khud handle kar sakta hai, 2% mein human help chahiye

---

## 11. Advanced RAG mein LangGraph ka Role

Diagram mein **rag_graph** aur **rag_graph.invoke()** tha:

```python
# RAG pipeline ko LangGraph se banao
from langgraph.graph import StateGraph

rag_graph = StateGraph(State)

# Nodes add karo
rag_graph.add_node("query_translation", translate_query)
rag_graph.add_node("routing", route_query)
rag_graph.add_node("retrieval", retrieve_docs)
rag_graph.add_node("generation", generate_answer)

# Edges define karo
rag_graph.add_edge("query_translation", "routing")
rag_graph.add_conditional_edges("routing", route_decision)
rag_graph.add_edge("retrieval", "generation")

# Graph compile karo
graph = rag_graph.compile()

# Invoke karo
result = graph.invoke({"messages": ["User ka question"]})
# ↑ yahi rag_graph.invoke() hai diagram mein
```

### Saari RAG techniques LangGraph nodes ban jaati hain:

```
ranking → query_translation → fan_out → logical_routing
                                            ↓
                                    PDF → Chunks → Retrieval
```

---

## 12. Cursor — AI Coding Tool

Diagram mein **Cursor** ka reference tha:

- **Cursor** = AI-powered code editor (VS Code jaisa)
- Tumhara code context samajhta hai
- LangGraph code likhne mein Cursor se help le sakte ho
- GenAI engineer ke liye ek important productivity tool

---

## 13. LangGraph vs LangChain — Fark Kya Hai?

| Feature | LangChain | LangGraph |
|---|---|---|
| Structure | Linear chains | Graph (nodes + edges) |
| Loops | Nahi | ✅ Haan |
| State management | Limited | ✅ Built-in TypedDict State |
| Complex workflows | Mushkil | ✅ Easy |
| Human-in-loop | Manual | ✅ Built-in support |
| Autonomous agents | Possible but complex | ✅ First class support |
| Checkpointing | Nahi | ✅ Haan |

> **Simple rule:** Simple pipeline → LangChain. Complex workflow with loops/routing/human-approval → LangGraph.

---

## 14. Complete LangGraph Mental Model

```
┌─────────────────────────────────────────────────┐
│                  LangGraph                       │
│                                                 │
│   START                                         │
│     ↓                                           │
│   [Node 1: Query Translation]                   │
│     ↓                                           │
│   [Node 2: Routing]                             │
│     ↓           ↓                               │
│   [Node 3A]   [Node 3B]   ← Conditional edges  │
│   (Complex)   (Simple)                          │
│     ↓           ↓                               │
│   [Node 4: Retrieval]                           │
│     ↓                                           │
│   [Node 5: Generation]                          │
│     ↓                                           │
│   END                                           │
│                                                 │
│  State har node se guzarta hai ──────────────►  │
│  { query, route, docs, answer }                 │
└─────────────────────────────────────────────────┘
```

---

## 15. Key Takeaways — Yaad Rakhne Wali Baatein

| Baat | Explanation |
|---|---|
| **Framework = tum plug in, woh control kare** | LangGraph framework hai — apna code nodes mein daalo |
| **State = sab nodes ka shared memory** | TypedDict use karo, har node state update karta hai |
| **Nodes = functions** | Python functions jo state lete hain aur return karte hain |
| **Edges = flow** | Simple edges hamesha ek jagah, conditional edges routing karte hain |
| **n8n = LangGraph ka UI version** | Concept same hai, bas code ki jagah drag-drop |
| **Autonomous = AI decides** | Agent khud tools choose karta hai while loop mein |
| **Blocking = human approval** | Critical steps pe pipeline rok ke human se puchho |
| **rag_graph.invoke()** | Poori RAG pipeline ek line mein chala do |

---

*Notes based on 6 images — LangGraph Framework, State Management, Nodes & Edges, Routing, Autonomous Agents, Human-in-Loop, Blocking Requests, aur Advanced RAG integration (Hinglish).*