# 🧠 Complete AI / LLM Notes — Hinglish
> Diagram se banaye gaye complete detailed notes  
> **Topics:** Fine Tuning • RAG • Agents • LangChain • LangGraph • MCP • Agentic AI

---

## 📌 Table of Contents
1. [Fine Tuning — Broad Use Cases](#1-fine-tuning--broad-use-cases)
2. [Pre-trained Models](#2-pre-trained-models)
3. [Few-Shot Learning](#3-few-shot-learning)
4. [RAG — Retrieval Augmented Generation](#4-rag--retrieval-augmented-generation)
5. [Embeddings & Vector DB](#5-embeddings--vector-db)
6. [Agents](#6-agents)
7. [LangChain](#7-langchain)
8. [LangGraph](#8-langgraph)
9. [MCP — Model Context Protocol](#9-mcp--model-context-protocol)
10. [Agentic AI / Multi-Agent System](#10-agentic-ai--multi-agent-system)
11. [Code Execution Agent](#11-code-execution-agent)
12. [Tool Use / Function Calling](#12-tool-use--function-calling)
13. [Memory in Agents](#13-memory-in-agents)
14. [Full Architecture Summary](#14-full-architecture-summary)

---

## 1. Fine Tuning — Broad Use Cases

### Fine Tuning Kya Hai?
- **Pre-trained model** ko apne specific data pe aur zyada train karna
- Jaise ek general doctor ko specialist banana (cardiologist)
- Base model pehle se bahut kuch jaanta hai — hum sirf **domain-specific knowledge** add karte hain

### Broad Use Cases:
| Use Case | Example |
|----------|---------|
| Customer Support | Company-specific Q&A bot |
| Medical | Disease diagnosis assistant |
| Legal | Contract review AI |
| Code | Company codebase pe trained copilot |
| Finance | Earnings report analyzer |

### Fine Tuning ke Types:

**1. Full Fine Tuning**
- Poore model ke weights update hote hain
- Bahut expensive — GPU + time lagta hai
- Best results milte hain

**2. PEFT (Parameter Efficient Fine Tuning)**
- Sirf kuch layers train karte hain
- Kam resources chahiye
- Popular method: **LoRA (Low-Rank Adaptation)**

**3. LoRA — Low Rank Adaptation**
```
Original Weights (freeze)
        +
Small Adapter Matrices (train karo)
        =
Fine-tuned Behavior
```
- Sirf adapter train hota hai → 90% less compute
- Most popular fine tuning method aajkal

**4. RLHF — Reinforcement Learning from Human Feedback**
- Human raters model ke outputs ko rate karte hain
- Model seekhta hai ki kya "good" response hai
- OpenAI ne ChatGPT banane mein ye use kiya

### Fine Tuning vs Prompting:
```
Prompting → Instructions dete ho (no training)
Fine Tuning → Model ko actually sikhate ho
```
- Pehle always prompting try karo
- Agar prompting se kaam na chale → tab fine tuning

---

## 2. Pre-trained Models

### Kya Hota Hai?
- Internet ka data use karke already trained model
- Billions of parameters
- Hum inhe **directly use** kar sakte hain ya **fine-tune** kar sakte hain

### Popular Pre-trained Models:
```
OpenAI:      GPT-4, GPT-4o, GPT-3.5
Google:      Gemini Pro, Gemini Flash
Meta:        LLaMA 3, LLaMA 3.1
Mistral:     Mistral 7B, Mixtral
DeepSeek:    DeepSeek-R1, DeepSeek-V3
Anthropic:   Claude 3.5, Claude Opus
Microsoft:   Phi-3, Phi-4
```

### Model Size Matters:
| Size | Parameters | Best For |
|------|-----------|---------|
| Small | 1B-7B | Edge devices, fast inference |
| Medium | 13B-30B | Balance of speed & quality |
| Large | 70B+ | Best quality, needs big GPU |

### Hugging Face — Model Hub:
- Sabse bada **open source model repository**
- Hazaron pre-trained models free mein available
- `transformers` library se directly use karo

```python
from transformers import pipeline

# Ek line mein model load karo
classifier = pipeline("sentiment-analysis")
result = classifier("Main bahut khush hoon!")
print(result)  # [{'label': 'POSITIVE', 'score': 0.99}]
```

---

## 3. Few-Shot Learning

### Kya Hota Hai?
- LLM ko **examples dekar** task sikhana — bina training ke
- Prompt ke andar hi examples dete hain

### Types:
**Zero-Shot:** Koi example nahi
```
Prompt: "Is sentence ka sentiment kya hai: 'Mujhe pizza pasand hai'"
```

**One-Shot:** Ek example
```
Prompt: 
Example: "Mujhe cricket pasand hai" → Positive
Ab batao: "Aaj bahut bura din tha" → ?
```

**Few-Shot:** Multiple examples
```
Prompt:
"Mujhe cricket pasand hai" → Positive
"Aaj bahut bura din tha" → Negative  
"Movie average thi" → Neutral
Ab batao: "Khana sach mein zabardast tha" → ?
```

### Chain-of-Thought (CoT) Prompting:
- Model ko step-by-step sochne dena
- Complex problems ke liye better results

```
Prompt: "Ek dukan mein 5 apples hain. 3 bik gaye. Phir 4 aur aaye. 
Kitne hain? Step by step socho."

Response:
Step 1: Start = 5 apples
Step 2: 3 bik gaye → 5-3 = 2
Step 3: 4 aur aaye → 2+4 = 6
Answer: 6 apples
```

---

## 4. RAG — Retrieval Augmented Generation

### RAG Kya Hai?
> **RAG = LLM + Apna Knowledge Base**

- LLM ki training cutoff hoti hai (purana data)
- RAG se hum **fresh/private data** LLM ko dete hain
- Without RAG: LLM sirf training data se answer deta hai
- With RAG: LLM **pehle search karta hai**, phir answer deta hai

### RAG kab use karein?
- Company ke internal documents pe Q&A
- Latest news ya current events
- Private/confidential data jo training mein nahi tha
- Long documents (books, PDFs, research papers)

### RAG Architecture:

```
                    ┌─────────────────────┐
User Question ───→  │   Query Processing  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Vector Database   │  ← (documents stored as embeddings)
                    │  Similarity Search  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Relevant Chunks    │  ← Top-K results retrieve hote hain
                    │  (Context)          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   LLM              │  ← Question + Context dono jaate hain
                    │   (Generate)        │
                    └──────────┬──────────┘
                               │
                    Final Answer ◄────────┘
```

### RAG Pipeline Steps:

**Step 1 — Ingestion (Data Load karo)**
```python
# Documents load karo
from langchain.document_loaders import PyPDFLoader
loader = PyPDFLoader("company_docs.pdf")
documents = loader.load()
```

**Step 2 — Chunking (Documents toro)**
```python
# Bade documents ko chunks mein toro
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Har chunk 500 characters
    chunk_overlap=50     # Overlap for context continuity
)
chunks = splitter.split_documents(documents)
```

**Step 3 — Embedding (Numbers mein convert karo)**
```python
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()
# Har chunk ko vector (numbers) mein convert karo
```

**Step 4 — Vector Store (Save karo)**
```python
from langchain.vectorstores import FAISS, Chroma, Pinecone

# FAISS — local, free
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("my_index")
```

**Step 5 — Retrieval + Generation**
```python
# Query aai → similar chunks dhundo → LLM ko do
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
answer = chain.run("Company ki refund policy kya hai?")
```

### Popular Vector Databases:
| DB | Type | Best For |
|----|------|---------|
| FAISS | Local | Prototype, small data |
| Chroma | Local/Server | Development |
| Pinecone | Cloud | Production |
| Weaviate | Cloud/Self-hosted | Enterprise |
| Qdrant | Cloud/Local | Performance |

---

## 5. Embeddings & Vector DB

### Embedding Kya Hai?
- Text ko **numbers ki list (vector)** mein convert karna
- Similar meanings → Similar vectors
- LLM "meaning" ko numbers mein encode karta hai

```
"cat"  → [0.2, 0.8, 0.1, 0.9, ...]  (1536 numbers)
"dog"  → [0.2, 0.7, 0.2, 0.8, ...]  (similar!)
"car"  → [0.9, 0.1, 0.7, 0.2, ...]  (different)
```

### Cosine Similarity:
- Do vectors kitne "paas" hain → similarity
- 1.0 = identical, 0.0 = completely different

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

v1 = model.encode("cat")
v2 = model.encode("dog")
v3 = model.encode("car")

print(cosine_similarity([v1], [v2]))  # 0.89 (similar!)
print(cosine_similarity([v1], [v3]))  # 0.21 (different)
```

### Popular Embedding Models:
```
OpenAI:     text-embedding-3-small, text-embedding-ada-002
Google:     text-embedding-004
HuggingFace: sentence-transformers/all-MiniLM-L6-v2 (FREE)
Cohere:     embed-english-v3.0
```

---

## 6. Agents

### Agent Kya Hai?
> **Agent = LLM + Tools + Memory + Planning**

- Sirf answer nahi deta — **actions leta hai**
- Goals ke basis pe khud decide karta hai kya karna hai
- Loop mein kaam karta hai jab tak goal complete na ho

### Agent Loop (ReAct Pattern):
```
┌─────────────────────────────────────────┐
│              AGENT LOOP                 │
│                                         │
│  1. Thought → "Mujhe weather check     │
│                karna chahiye"           │
│  2. Action  → weather_tool("Delhi")    │
│  3. Observation → "28°C, Sunny"        │
│  4. Thought → "Ab answer de sakta hoon"│
│  5. Final Answer → User ko bata do     │
└─────────────────────────────────────────┘
```

### Agent ke Components:
```
┌──────────────────────────────────┐
│           AGENT                  │
│                                  │
│  ┌─────────┐  ┌───────────────┐ │
│  │   LLM   │  │    Tools      │ │
│  │ (Brain) │  │ - Web Search  │ │
│  └────┬────┘  │ - Calculator  │ │
│       │       │ - Code Runner │ │
│  ┌────▼────┐  │ - DB Query    │ │
│  │ Memory  │  │ - Email Send  │ │
│  │ (Past)  │  └───────────────┘ │
│  └─────────┘                    │
└──────────────────────────────────┘
```

### Types of Agents:

**1. ReAct Agent (Reason + Act)**
- Sochta hai → Action karta hai → Observe karta hai
- Most common type

**2. Plan-and-Execute Agent**
- Pehle poora plan banata hai
- Phir step by step execute karta hai
- Complex tasks ke liye

**3. Self-Reflective Agent**
- Apne outputs ko evaluate karta hai
- Galti ho to khud correct karta hai

---

## 7. LangChain

### LangChain Kya Hai?
- LLM applications banane ka **popular framework**
- Chains, Agents, RAG — sab ek jagah
- Python aur JavaScript dono mein available

### Install:
```bash
pip install langchain langchain-openai langchain-community
```

### Core Concepts:

**1. LLM / ChatModel**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)
response = llm.invoke("Python kya hai?")
print(response.content)
```

**2. Prompt Templates**
```python
from langchain.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "Tum ek helpful {language} teacher ho"),
    ("human", "{topic} samjhao")
])

chain = template | llm
result = chain.invoke({"language": "Python", "topic": "loops"})
```

**3. Chains (LCEL — LangChain Expression Language)**
```python
# Pipe operator se chain banao
chain = prompt | llm | output_parser

# Invoke karo
result = chain.invoke({"input": "Hello"})
```

**4. Memory**
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
# Previous conversation yaad rakhta hai
```

**5. Tools & Agents**
```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"{city} mein 28°C aur sunny hai"

agent = create_react_agent(llm, tools=[get_weather], prompt=prompt)
executor = AgentExecutor(agent=agent, tools=[get_weather])
result = executor.invoke({"input": "Delhi ka weather kya hai?"})
```

### LangChain Architecture:
```
Input
  ↓
Prompt Template
  ↓
LLM (OpenAI / Ollama / etc.)
  ↓
Output Parser
  ↓
Final Output
```

---

## 8. LangGraph

### LangGraph Kya Hai?
- LangChain ka extension
- **Graph-based** agent workflows
- Complex, multi-step, **stateful** applications ke liye
- Nodes aur Edges se workflow define karo

### LangChain vs LangGraph:
| | LangChain | LangGraph |
|--|-----------|-----------|
| Structure | Linear chains | Graph (nodes + edges) |
| State | Limited | Full state management |
| Loops | Difficult | Easy |
| Complexity | Medium | High (but powerful) |
| Use case | Simple pipelines | Complex agents |

### LangGraph Concepts:

**State** — Shared data jo nodes ke beech pass hoti hai
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list
    next_action: str
    result: str
```

**Nodes** — Functions jo kaam karte hain
```python
def research_node(state: AgentState) -> AgentState:
    # Web search karo
    query = state["messages"][-1]
    results = web_search(query)
    return {"result": results}

def answer_node(state: AgentState) -> AgentState:
    # Answer generate karo
    answer = llm.invoke(state["messages"])
    return {"messages": [answer]}
```

**Graph** — Nodes ko connect karo
```python
graph = StateGraph(AgentState)

# Nodes add karo
graph.add_node("research", research_node)
graph.add_node("answer", answer_node)

# Edges add karo (flow define karo)
graph.set_entry_point("research")
graph.add_edge("research", "answer")
graph.add_edge("answer", END)

# Compile karo
app = graph.compile()
result = app.invoke({"messages": ["AI kya hai?"]})
```

### Conditional Edges (Decision Making):
```python
def should_continue(state):
    if state["result"] == "needs_more_research":
        return "research"  # Loop back
    else:
        return "answer"   # Aage badho

graph.add_conditional_edges(
    "research",
    should_continue,
    {"research": "research", "answer": "answer"}
)
```

### LangGraph Use Cases:
- **Customer support bot** — Multiple departments route karo
- **Research agent** — Search → Analyze → Summarize loop
- **Code review agent** — Write → Test → Fix loop
- **Multi-agent systems** — Alag-alag agents coordinate karein

---

## 9. MCP — Model Context Protocol

### MCP Kya Hai?
> **MCP = Standard way to connect LLMs to external tools/data**

- Anthropic ne banaya (Claude ke creators)
- LLM aur tools ke beech **universal protocol**
- USB-C jaiso sochho — ek standard connector sab ke liye

### MCP Architecture:
```
┌─────────────────┐     MCP Protocol     ┌──────────────────┐
│   MCP Client    │ ◄──────────────────► │   MCP Server     │
│  (AI App/LLM)  │                       │  (Tool Provider) │
└─────────────────┘                       └──────────────────┘
                                                   │
                                        ┌──────────▼──────────┐
                                        │ - File System       │
                                        │ - Database          │
                                        │ - Web APIs          │
                                        │ - Custom Tools      │
                                        └─────────────────────┘
```

### MCP ke Components:

**1. Resources** — Data jo LLM read kar sake
```
Files, databases, API responses
```

**2. Tools** — Functions jo LLM call kar sake
```
search(), create_file(), send_email()
```

**3. Prompts** — Reusable prompt templates
```
Pre-defined workflows
```

### MCP vs Direct API:
```
Without MCP:
LLM → Custom code → Tool A
LLM → Custom code → Tool B
LLM → Custom code → Tool C
(Har tool ke liye alag code)

With MCP:
LLM → MCP Protocol → Tool A
                   → Tool B  
                   → Tool C
(Ek standard, sab tools)
```

### Popular MCP Servers:
- `filesystem` — Local files access
- `github` — GitHub repos manage karo
- `postgres` — Database queries
- `brave-search` — Web search
- `slack` — Slack messages
- `google-drive` — Google Drive files

### MCP Setup (Claude Desktop):
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "your_token"}
    }
  }
}
```

---

## 10. Agentic AI / Multi-Agent System

### Agentic AI Kya Hai?
- **Multiple AI agents** milke ek bade goal pe kaam karte hain
- Har agent ka ek specific role hota hai
- Agents ek dusre se communicate karte hain

### Multi-Agent Architecture:
```
         ┌─────────────────────┐
         │   Orchestrator      │  ← Boss agent — tasks distribute karta hai
         │   (Manager Agent)   │
         └──────────┬──────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼───┐ ┌─────▼─────┐ ┌──▼────────┐
│ Research  │ │  Writer   │ │  Critic   │
│  Agent    │ │  Agent    │ │  Agent    │
└───────────┘ └───────────┘ └───────────┘
  Web Search   Content Gen   Review & Fix
```

### Real World Example — Blog Writing System:
```
User: "Python tutorial likhna hai"
         ↓
Orchestrator Agent
         ↓
    ┌────┴────┐
    │         │
Research    Outline
  Agent      Agent
(facts dhundo) (structure banao)
    │         │
    └────┬────┘
         ↓
    Writer Agent
    (Content likho)
         ↓
    Editor Agent
    (Proofread karo)
         ↓
   Final Blog Post ✅
```

### Agent Communication Patterns:

**1. Sequential (Line mein)**
```
Agent A → Agent B → Agent C → Result
```

**2. Parallel (Saath mein)**
```
Agent A ─┐
Agent B ─┼─→ Aggregator → Result
Agent C ─┘
```

**3. Hierarchical (Manager-Worker)**
```
Manager
├── Worker 1
├── Worker 2
└── Worker 3
```

### AutoGen — Microsoft ka Multi-Agent Framework:
```python
import autogen

# Agents define karo
assistant = autogen.AssistantAgent("assistant", llm_config=llm_config)
user_proxy = autogen.UserProxyAgent("user_proxy", code_execution_config={"work_dir": "."})

# Conversation start karo
user_proxy.initiate_chat(
    assistant,
    message="Python mein bubble sort likhna aur test karo"
)
```

---

## 11. Code Execution Agent

### Kya Karta Hai?
- Code **khud likhta hai**
- Code **khud run karta hai**
- Output dekh ke **khud fix karta hai**

### Flow:
```
Problem Statement
       ↓
LLM → Code Generate karo
       ↓
Code Execute karo (sandbox mein)
       ↓
Error aaya? → Fix karo → Re-run karo
       ↓
Success → Result do
```

### Code Execution Setup:
```python
from langchain.agents import create_python_agent
from langchain.tools import PythonREPLTool

# Python REPL tool — code run kar sakta hai
python_tool = PythonREPLTool()

agent = create_python_agent(
    llm=llm,
    tool=python_tool,
    verbose=True
)

result = agent.run("""
1 se 100 tak ke prime numbers nikalo 
aur unka sum batao
""")
```

### Sandbox Safety:
- Code execution **isolated environment** mein hona chahiye
- Docker containers use karo production mein
- Never directly system pe run karo untrusted code

---

## 12. Tool Use / Function Calling

### Kya Hai?
- LLM directly external functions call kar sakta hai
- OpenAI, Anthropic — sab support karte hain
- JSON format mein tool define karo

### OpenAI Function Calling:
```python
import openai
import json

# Tools define karo
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Kisi bhi city ka weather batao",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# LLM call karo tools ke saath
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Delhi ka weather kya hai?"}],
    tools=tools,
    tool_choice="auto"  # LLM decide kare kab tool use karna hai
)

# LLM ne tool call kiya?
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    city = json.loads(tool_call.function.arguments)["city"]
    
    # Actual function call karo
    weather = get_weather(city)  # "28°C, Sunny"
    
    # Result wapas LLM ko do
    final_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Delhi ka weather kya hai?"},
            response.choices[0].message,
            {"role": "tool", "content": weather, "tool_call_id": tool_call.id}
        ]
    )
    print(final_response.choices[0].message.content)
```

### Common Tools:
```python
tools = [
    web_search_tool,      # Internet search
    calculator_tool,      # Math calculations
    file_read_tool,       # Files padhna
    database_tool,        # DB queries
    email_tool,           # Email bhejna
    calendar_tool,        # Calendar manage
    code_execution_tool,  # Code run karna
]
```

---

## 13. Memory in Agents

### Types of Memory:

**1. Short-term Memory (Conversation Buffer)**
- Current conversation yaad rakhta hai
- Context window ki limit hai
```python
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()
```

**2. Long-term Memory (Vector Store)**
- Past conversations save hoti hain
- Similarity search se relevant memories retrieve hoti hain
```python
from langchain.memory import VectorStoreRetrieverMemory
memory = VectorStoreRetrieverMemory(retriever=vectorstore.as_retriever())
```

**3. Episodic Memory**
- Specific events/episodes yaad rakhna
- "Last time user ne pizza order kiya tha"

**4. Semantic Memory**
- Facts aur knowledge store karna
- User preferences, important information

### Memory Architecture:
```
New Message
     ↓
┌────┴────────────────────────┐
│   Working Memory            │  ← Current conversation
│   (Context Window)          │
└────┬────────────────────────┘
     │
     ↓ (important info save)
┌────┴────────────────────────┐
│   Long-term Memory          │  ← Vector DB
│   (Past experiences)        │
└─────────────────────────────┘
     ↑
     │ (relevant memories retrieve)
     └── Next conversation mein use
```

---

## 14. Full Architecture Summary

### Complete AI Application Stack:
```
┌─────────────────────────────────────────────────┐
│                  USER INTERFACE                  │
│         (Web App / API / Chat Interface)         │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              ORCHESTRATION LAYER                 │
│         LangChain / LangGraph / AutoGen          │
└──────────────────────┬──────────────────────────┘
                       │
         ┌─────────────┼──────────────┐
         │             │              │
┌────────▼───┐  ┌──────▼──────┐ ┌───▼──────────┐
│    LLM     │  │   Memory    │ │    Tools     │
│ GPT-4 /    │  │ Short-term  │ │ Web Search   │
│ Claude /   │  │ Long-term   │ │ Calculator   │
│ LLaMA      │  │ Vector DB   │ │ Code Runner  │
└────────────┘  └─────────────┘ └──────────────┘
         │
┌────────▼───────────────────────────────────────┐
│                DATA LAYER                       │
│  RAG Pipeline → Vector DB → Embeddings         │
│  Documents / PDFs / Databases / APIs            │
└─────────────────────────────────────────────────┘
```

### Technology Stack Choices:
| Layer | Options |
|-------|---------|
| LLM | OpenAI GPT-4 / Claude / Gemini / LLaMA (Ollama) |
| Framework | LangChain / LlamaIndex / Haystack |
| Orchestration | LangGraph / AutoGen / CrewAI |
| Vector DB | FAISS / Chroma / Pinecone / Weaviate |
| Embedding | OpenAI / HuggingFace / Cohere |
| Tools/MCP | Custom Tools / MCP Servers |
| Memory | ConversationBuffer / Redis / Vector Store |
| Deployment | FastAPI / Docker / Cloud (AWS/GCP/Azure) |

---

## 🚀 Quick Revision — Sab Ek Jagah

| Concept | Ek Line Mein |
|---------|-------------|
| Fine Tuning | Pre-trained model ko apne data pe aur train karna |
| LoRA | Sirf small adapters train karo — efficient fine tuning |
| RLHF | Human feedback se model ko improve karo |
| RAG | External knowledge + LLM = Accurate answers |
| Embeddings | Text → Numbers (meaning encode karo) |
| Vector DB | Embeddings store karo aur fast search karo |
| Agent | LLM jo khud actions le sakta hai |
| ReAct | Think → Act → Observe → Repeat |
| LangChain | LLM apps banane ka framework |
| LangGraph | Graph-based complex agent workflows |
| MCP | Standard protocol LLM aur tools ko connect karne ka |
| Multi-Agent | Multiple AI agents milke kaam karte hain |
| Function Calling | LLM external functions call kar sakta hai |
| Memory | Agent past conversations yaad rakhta hai |

---

## 📚 Resources for Further Learning

```
LangChain Docs:     https://docs.langchain.com
LangGraph:          https://langchain-ai.github.io/langgraph
MCP Docs:           https://modelcontextprotocol.io
OpenAI Docs:        https://platform.openai.com/docs
HuggingFace:        https://huggingface.co/docs
Ollama:             https://ollama.ai

YouTube Channels:
- Andrej Karpathy (Deep LLM understanding)
- AI Jason (LangChain tutorials)
- Matt Williams (Ollama)
```

---

> 📝 **Notes created from:** Excalidraw diagram + Image diagram  
> **Topics covered:** Fine Tuning → RAG → Embeddings → Agents → LangChain → LangGraph → MCP → Multi-Agent → Memory → Full Stack Architecture

## extra notes by me
llm as a judge: LLM ko ek judge ki tarah use karna, jahan wo alag-alag tools ke outputs ko evaluate karta hai aur decide karta hai ki kaunsa output best hai. Ye approach multi-agent systems mein bahut useful hota hai, jahan multiple agents alag-alag tasks perform karte hain aur LLM unke results ko judge karta hai.

sdk: Software Development Kit, ek set of tools aur libraries jo developers ko specific platform ya framework ke liye applications banane mein madad karta hai. LLMs ke context mein, SDKs developers ko LLM APIs ke saath easily integrate karne ka tarika provide karte hain, jisse wo apne applications mein LLM capabilities add kar sakte hain bina low-level API calls ke.