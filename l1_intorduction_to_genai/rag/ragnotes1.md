# 📌 RAG vs Fine-Tuning vs Simple Chat App - Notes

---

## 🔹 1. Simple Chat Application

* Uses only **Pre-trained Data**
* No external or custom data
* Example: Basic GPT usage

### ❌ Limitations:

* Cannot access latest data
* No knowledge of your private/custom data
* May hallucinate

---

## 🔹 2. Fine-Tuning

* Model ko **custom data pe train** karte hain
* "Our Data" → model me permanently embed ho jata hai

### ✅ Use Case:

* Specific domain knowledge (medical, legal, etc.)

### ❌ Limitations:

* Expensive
* Retraining required for updates
* Static knowledge (real-time update nahi)

---

## 🔹 3. RAG (Retrieval-Augmented Generation)

👉 Best of both worlds (LLM + External Data)

### 🔄 Flow:

1. **User Query**
2. `get_data_from_db()`
3. Relevant data fetch karo
4. Prompt me daal do:

   ```
   "Bhai jo relevant data hai, usko prompt me daal do"
   ```
5. LLM generate karta hai answer

---

## 🔹 Core Idea

👉 **"Retrieve relevant data → add to prompt → generate answer"**

---

## 🔹 Data Handling

* DB me data stored hota hai
* Functions:

  * `get_data_from_db()`
  * `write_to_db()`

---

## 🔹 Context Injection

LLM ko diya jata hai:

```id="ctx01"
Resolve the user query based on following data:
```

* Example:

  * 20 rows relevant data
  * Context ke andar pass hota hai

---

## 🔹 Context Window

* LLM ek limit tak hi data process kar sakta hai
* context window basically ek limit hai ki kitna data ek baar me process kar sakta hai

### 📊 Examples:

* GPT-3 → small context
* GPT-4 → larger
* GPT-4.1 → up to ~1M tokens

👉 Isliye:

* Sirf **relevant data** hi bhejna chahiye

---

## 🔹 Why RAG?

### ✅ Advantages:

* Real-time data access
* No retraining needed
* Cost effective
* Dynamic updates possible

### ❌ Compared to Fine-Tuning:

| Feature        | Fine-Tuning | RAG  |
| -------------- | ----------- | ---- |
| Update Data    | Hard        | Easy |
| Cost           | High        | Low  |
| Flexibility    | Low         | High |
| Real-time Data | No          | Yes  |

---

## 🔹 Example Flow

User: "Explain invoices"

System:

1. DB se invoices related data fetch
2. Top 20 rows select
3. Prompt me add
4. LLM → answer generate

---

## 🔹 Key Insight

👉 LLM sab kuch yaad nahi rakhta
👉 RAG me hum usko **relevant info provide karte hain**

---

## 🔹 Interview Ready Answer

**"RAG is a technique where instead of retraining the model, we retrieve relevant data from external sources and inject it into the prompt to generate more accurate and up-to-date responses."**

---

## 🔹 One-Line Difference

* Simple Chat → Only pretrained knowledge
* Fine-Tuning → Train model on custom data
* RAG → Fetch data dynamically + use LLM

---


# 📌 RAG Diagram Notes (Focused)

---

## 🔹 1. Data Handling

* Large dataset present:

  * Example: **10,000 rows**

### ✂️ Chunking

* Data ko small parts me todte hain

  * Example: **40 rows per chunk**

👉 Purpose:

* Efficient processing
* Better retrieval

---

## 🔹 2. Query Flow

* User question input deta hai:

  ```
  Question
  ```

* System relevant chunks select karta hai

---

## 🔹 3. Database Search (Traditional)

* Query pattern based search:

  * `%honda%`
  * `%piyush%`
  * `%car%`

👉 Problem:

* Keyword/regex based
* Semantic meaning miss hota hai ❌

---

## 🔹 4. Vector Embeddings

* Text → Vector form

### 📌 Concept:

* "Semantic meaning dena 3D space me"

👉 Similar words → close vectors
👉 Different meaning → far vectors

---

## 🔹 5. Example Use Case

* Input:

  ```
  How to write into a file?
  ```

* PDF (Node.js) se data liya jata hai

---

## 🔹 6. PDF Processing

1. PDF → Text conversion
2. Text → System me use hota hai

---

## 🔹 7. System Prompt

* Format:

  ```
  SYSTEM_PROMPT {Text}
  ```

👉 Role:

* LLM ko guide karta hai
* Context ke basis pe answer dene ke liye

---

## 🔹 8. Context Building

* Retrieved chunks → combine hote hain

👉 Multiple blocks (context pieces) banaye jaate hain

---

## 🔹 9. Key Insight

* Raw DB search se better hai:
  👉 **Embeddings + context-based approach**

* Focus:

  * Relevant data
  * Context-driven answer

---

## 🔹 10. Mini Flow (From Image)

1. Large data (10k rows)
2. Chunking (40 rows)
3. Query input
4. DB / embedding-based search
5. Relevant data select
6. System prompt + context
7. Final processing

---

## 🔹 11. Important Takeaways

* Chunking improves efficiency
* Regex search limited hota hai
* Embeddings semantic understanding dete hain
* Context banana important hai

---

## vector embeddings basically ek technique hai jisme hum text ko numerical form me convert karte hain, jisse machine easily samajh sake. RAG me vector embeddings ka use hota hai taaki hum apne data ke semantic meaning ko capture kar sakein aur uske basis pe relevant information retrieve kar sakein jab user query aati hai.

## Indexing basically ek trick hai jisse hum apne data ko organize karte hain taaki hum usme se relevant information easily retrieve kar sakein. RAG me indexing ka use hota hai taaki hum apne data ko aise structure me organize kar sakein jisse hum usme se relevant chunks ko efficiently retrieve kar sakein jab user query aati hai.

# RAG System — Complete Notes
> **RAG = Retrieval-Augmented Generation**

---

## RAG kya hai?

RAG ek technique hai jisme LLM ko seedha jawab nahi dene dete.  
Pehle **relevant data dhundha jaata hai**, phir usse milake jawab banaya jaata hai.

**Faayda:** LLM apni imagination se nahi, **real data se** jawab deta hai — isliye hallucination kam hoti hai.

---

## Phase 1: Indexing *(ek baar hota hai)*

```
Data Source → Chunking → Embeddings → Vector Store
```

| Step | Kya hota hai | Detail |
|------|-------------|--------|
| **Data Source** | Apna data lo | PDFs, Word docs, websites, databases |
| **Chunking** | Bade documents ko chote tukdon mein todo | LLM ka context window limited hota hai |
| **Embeddings** | Har chunk ko numerical vector mein convert karo | Semantic meaning capture hoti hai |
| **Vector Store** | Vectors ko database mein save karo | Size ~1.5–2 GB hoti hai |

### 🔑 Key Concepts

- **Chunking kyun?**  
  LLM ek saath poora document nahi padh sakta. Chunking se sirf relevant hissa milta hai.

- **Embeddings kya hain?**  
  Text ko numbers ki list mein convert karna. Similar text ke vectors bhi similar hote hain.

- **Vector Store examples:**  
  Pinecone, ChromaDB, FAISS, Weaviate

---

## Phase 2: Query Time *(har sawaal pe hota hai)*

```
User Question → Embeddings → Vector Search → Relevant Chunks
```

| Step | Kya hota hai | Detail |
|------|-------------|--------|
| **User Question** | User kuch poochta hai | Natural language mein |
| **Embeddings** | Sawaal ko bhi vector mein convert karo | Same embedding model use karo |
| **Vector Search** | Vector store mein match dhundo | Cosine similarity se closest chunks milte hain |
| **Relevant Chunks** | Sirf relevant tukde nikalo | Top-K chunks select hote hain |

### 🔑 Key Concepts

- **Vector Search** exact match nahi, **similarity-based** hota hai
- Sawaal aur chunks — dono ko **same embedding model** se convert karna zaroori hai
- **Top-K** = kitne chunks LLM ko dene hain (usually 3–5)

---

## Phase 3: Generation

```
User Question + Relevant Chunks → LLM → Output
```

- LLM ko **do cheezein** milti hain:
  1. User ka original sawaal
  2. Retrieved relevant chunks (context)

- LLM in dono ko milaakar **grounded, accurate jawab** deta hai

### LLM examples:
GPT-4, Claude, Gemini, LLaMA — koi bhi kaam karta hai

---

## Full Flow (Summary)

```
┌─────────────────────────────────────────┐
│           INDEXING PHASE                │
│                                         │
│  Data Source → Chunking → Embeddings   │
│                               ↓         │
│                         Vector Store   │
└─────────────────────────────────────────┘
                    ↓ (retrieval time)
┌─────────────────────────────────────────┐
│           QUERY PHASE                   │
│                                         │
│  User Question → Embeddings            │
│                      ↓                  │
│               Vector Search            │
│                      ↓                  │
│            Relevant Chunks             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         GENERATION PHASE                │
│                                         │
│  Question + Chunks → LLM → Output      │
└─────────────────────────────────────────┘
```

---

## 💡 Important Points (Exam ke liye)

| Point | Detail |
|-------|--------|
| RAG ka full form | Retrieval-Augmented Generation |
| Vector Store ka size | ~1.5–2 GB |
| Indexing kitni baar | Sirf ek baar (ya data change hone pe) |
| Query time kitni baar | Har sawaal pe |
| Hallucination kyun kam hoti hai | LLM real data se jawab deta hai |
| Chunking kyun zaroori | Context window limited hoti hai LLM ki |
| Embedding kya hai | Text → Numerical vector conversion |

---

## 🆚 RAG vs Normal LLM

| Feature | Normal LLM | RAG |
|---------|-----------|-----|
| Data source | Training data (purana) | Real-time / custom data |
| Hallucination | Zyada | Kam |
| Custom knowledge | Nahi | Haan |
| Cost | Kam | Thoda zyada |
| Accuracy | Generic | Domain-specific |

---

*Notes by Claude — RAG System Architecture*

## ya to sare functions jo hai use ek ek krke banao ya to langchain use kro jisme sare functions already defined hote hai. RAG me hum apne data ko aise structure me organize karte hain jisse hum usme se relevant chunks ko efficiently retrieve kar sakein jab user query aati hai.

## langchain basically ek framework hai jo RAG applications banane me madad karta hai. Isme pre-built components hote hain jaise ki document loaders, vector stores, retrievers, aur LLM wrappers, jisse developers ko apne RAG system ko jaldi aur efficiently build karne me madad milti hai. Langchain ke through hum apne data ko easily manage kar sakte hain aur LLM ke saath seamlessly integrate kar sakte hain.

# LangChain — RAG Chain Theory Notes

---

## RAG Chain kya hai?

LangChain mein alag-alag components ko **pipe operator `|`** se jodke ek chain banate hain.  
Har component apna output agले component ko deta hai — bilkul assembly line ki tarah.

```
loader | splitter | embedding | vector_store
```

`chain.invoke(pdf_path)` se poori pipeline ek saath execute hoti hai.

---

## 4 Main Components

### 1. Loader
- Document/file ko padhta hai aur raw text nikalta hai
- Alag-alag sources ke liye alag loader hota hai — PDF, website, CSV, Word doc
- Output: Document objects ki list

### 2. Text Splitter
- Bade documents ko chote **chunks** mein todta hai
- **chunk_size** — ek chunk kitna bada ho
- **chunk_overlap** — do chunks ke beech thoda shared text — taaki boundary pe context na tute
- Output: Chunks ki list

### 3. Embedding Model
- Har chunk ko **numerical vector** mein convert karta hai
- Similar meaning wale text ke vectors bhi similar hote hain
- OpenAI (paid) ya HuggingFace (free) use kar sakte hain
- Output: Dense float vectors

### 4. Vector Store
- Vectors ko **store** karta hai aur query time pe **similarity search** karta hai
- Exact match nahi, **semantic similarity** se dhundta hai

| Vector Store | Type |
|---|---|
| Qdrant | Self-hosted / Cloud |
| Chroma | Local / Development |
| Pinecone | Managed Cloud |
| FAISS | In-memory, fast |
| pgvector | PostgreSQL extension |

---

## Chain ka Flow

```
PDF Path
  ↓ Loader      → Raw text
  ↓ Splitter    → Chunks
  ↓ Embedding   → Vectors
  ↓ Vector Store → Stored & ready to search
```

---

## LangChain mein kya-kya chahiye?

| Component | Kaam |
|---|---|
| Document Loader | Source se text lana |
| Text Splitter | Chunks banana |
| Embedding Model | Text → Vector |
| Vector Store | Store + Search |
| Retriever | Query pe top-K chunks nikalna |
| LLM | Final answer generate karna |

---

## Key Points

- Pipe `|` se components connect hote hain — order matter karta hai
- Indexing **ek baar** hoti hai, retrieval **har query pe**
- Embedding model indexing aur query — **dono jagah same** hona chahiye
- chunk_overlap isliye hota hai kyunki context boundary pe cut na ho
- Vector store sirf numbers store karta hai, text bhi saath mein save hota hai mapping ke liye

# Advanced RAG — Query Translation & Enrichment Notes

---

## Yeh kya hai?

Yeh **Advanced RAG** ka ek upgraded version hai jisme user ka sawaal seedha vector store mein nahi jaata.  
Pehle query ko **enrich aur translate** kiya jaata hai — taaki better results milein.

---

## Problem with Basic RAG

Basic RAG mein user jo likhta hai, wahi directly search hota hai.  
Agar user ne **galat words** use kiye ya query **ambiguous** hai — toh relevant chunks nahi milte.

**Solution → Query Translation (Enrichment Node)**

---

## Flow Overview

```
User Query
    ↓
Enrichment Node (Query Translation)
    ↓
Multi Query Generate (via Gemini/LLM)
    ↓
Reciprocal Rank Fusion (res_rank_fusion)
    ↓
Arbitrary Documents (Retrieved + Ranked)
    ↓
LLM → Final Answer
```

---

## Components Detail

### 1. User Query
- User ka original sawaal
- Akela kaafi nahi hota — isliye enrichment hoti hai

---

### 2. Enrichment Node
- Poora query improvement ka kaam yahan hota hai
- Do techniques use hoti hain andar:
  - **Multi Query**
  - **Breakdown**

---

### 3. Query Translation — 2 Techniques

#### A) Multi Query
- Ek hi sawaal se **multiple similar queries** banata hai LLM
- Har query thodi alag perspective se likhi hoti hai
- Faayda: Agar ek query se relevant chunk na mile, doosri se mil jaaye

**Example:**
```
Original: "RAG kya hai?"

Generated queries:
→ "Retrieval Augmented Generation explain karo"
→ "RAG aur normal LLM mein kya fark hai?"
→ "RAG ka use case kya hai?"
```

#### B) Breakdown
- Complex sawaal ko **sub-questions** mein toda jaata hai
- Har sub-question alag se search hota hai
- Faayda: Multi-part questions better handle hote hain

**Example:**
```
Original: "LangChain mein RAG kaise kaam karta hai aur kaunsa vector store best hai?"

Breakdown:
→ "LangChain mein RAG kaise kaam karta hai?"
→ "Best vector store kaunsa hai RAG ke liye?"
```

---

### 4. LLM (Gemini)
- Multi Query aur Breakdown generate karne ke liye **Gemini** (ya koi bhi LLM) use hota hai
- User query input hoti hai → LLM multiple queries banata hai

---

### 5. Reciprocal Rank Fusion (RRF) — `res_rank_fusion`

- Sabhi generated queries se alag-alag results aate hain
- RRF in sabhi results ko **ek ranked list** mein merge karta hai
- Jo document zyada queries mein aaya — uska rank zyada hoga
- **Duplication remove** hoti hai, best chunks upar aate hain

**Simple samajhne ke liye:**
> 3 queries se 3 alag result lists aayi → RRF teeno ko milaakar ek final ranked list banata hai

---

### 6. Arbitrary Documents
- RRF ke baad jo top-ranked documents/chunks hain woh yahan aate hain
- "Arbitrary" matlab — kisi bhi source se ho sakte hain
- Yeh final context ban jaata hai jo LLM ko diya jaata hai

---

### 7. Final Answer (LLM)
- User ka **original query** + **ranked relevant documents** → LLM ko diya jaata hai
- LLM in sab se milaakar accurate answer generate karta hai

---

## Basic RAG vs Advanced RAG

| Feature | Basic RAG | Advanced RAG |
|---|---|---|
| Query | Seedha search | Pehle translate/expand |
| Queries count | 1 | Multiple (3–5) |
| Result merging | Nahi | RRF se ranked |
| Accuracy | Moderate | High |
| Complex questions | Struggle karta hai | Breakdown se handle |

---

## Key Points (Yaad rakho)

- **Enrichment Node** = Query improve karne ki jagah
- **Multi Query** = Ek se zyada similar queries banana
- **Breakdown** = Complex query ko sub-questions mein todna
- **RRF** = Multiple result lists ko ek smart ranked list mein merge karna
- Gemini/LLM ka kaam sirf query banane mein bhi hota hai — sirf answer mein nahi
- Yeh approach **hallucination aur miss rate** dono kam karta hai



