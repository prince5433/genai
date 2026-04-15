# =============================================================================
# WEBSITE RAG USING WEBBASELOADER (LANGCHAIN)
# =============================================================================

# 📌 KYA BAN RAHA HAI?
# Yeh ek simple RAG (Retrieval Augmented Generation) system hai jo:
# 1. Website se data scrape karega (WebBaseLoader se)
# 2. Us data ko chunks me todhega
# 3. Embeddings banayega (OpenAI se)
# 4. Store karega (in-memory list, simple version)
# 5. Query aane par relevant chunks retrieve karega
# 6. LLM se final answer generate karega

# -----------------------------------------------------------------------------
# 📌 RAG KYA HOTA HAI?
# -----------------------------------------------------------------------------

# RAG = Retrieval + Generation

# Step:
# User question → relevant docs retrieve → LLM answer banata hai

# -----------------------------------------------------------------------------
# 📌 WEBBASELOADER KYA KARTA HAI?
# -----------------------------------------------------------------------------

# LangChain ka WebBaseLoader:
# 👉 kisi bhi website ka content scrape karta hai
# 👉 clean text format me deta hai

# -----------------------------------------------------------------------------
# 📌 FLOW
# -----------------------------------------------------------------------------

# URL → scrape → chunk → embed → store
# User Query → embed → similarity search → context
# Context + Query → LLM → Final Answer

# -----------------------------------------------------------------------------
# 📌 INTERVIEW LINE
# -----------------------------------------------------------------------------

# "Built a website-based RAG system using LangChain WebBaseLoader to scrape,
# embed, and retrieve web content for answering queries."

# =============================================================================
# CODE START
# =============================================================================


# ------------------------------
# IMPORTS
# ------------------------------

# OS module: environment variables set/read karne ke liye
import os

# USER_AGENT set kar dete hain taaki web loading warning na aaye
os.environ.setdefault("USER_AGENT", "website-rag/1.0")

# .env file (OPENAI_API_KEY etc.) load karne ke liye
from dotenv import load_dotenv

# Website ka content text me laane ke liye loader
from langchain_community.document_loaders import WebBaseLoader

# Bada text chote chunks me todne ke liye splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# OpenAI API client
from openai import OpenAI

# Numerical operations (cosine similarity) ke liye
import numpy as np

# Regex se tokenization/cleanup ke liye
import re

# URL valid hai ya nahi check karne ke liye
from urllib.parse import urlparse

# ------------------------------
# SETUP
# ------------------------------

# .env file se env vars load karo (OPENAI_API_KEY)
load_dotenv()

# OpenAI client object banao
client = OpenAI()

# ------------------------------
# STEP 1: LOAD WEBSITE
# ------------------------------

def load_website(url):

    # URL ko WebBaseLoader me do
    loader = WebBaseLoader(url)

    # Website ka cleaned content documents ke form me laao
    docs = loader.load()

    # Loaded documents return karo
    return docs

def is_valid_url(url):
    # URL ko parse karke scheme/netloc check karte hain
    parsed = urlparse(url)

    # Sirf http/https and proper domain accepted
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

# ------------------------------
# STEP 2: SPLIT INTO CHUNKS
# ------------------------------

def split_docs(docs):

    # Splitter config:
    # chunk_size = ek chunk me max chars
    # chunk_overlap = adjacent chunks me shared chars
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,         # ek chunk ka size
        chunk_overlap=100       # overlap taaki context na tute
    )

    # Documents ko chote manageable chunks me convert karo
    chunks = splitter.split_documents(docs)

    # Chunk list return karo
    return chunks

# ------------------------------
# STEP 3: CREATE EMBEDDINGS
# ------------------------------

def get_embeddings(texts):

    # OpenAI embedding model se vector create karo
    # input me text list jaata hai
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    # Response object se vectors निकाल kar list return karo
    return [item.embedding for item in response.data]

# ------------------------------
# STEP 4: STORE (IN-MEMORY)
# ------------------------------

# Simple in-memory DB (demo purpose)
# Har item: {"text": chunk_text, "vector": embedding}
VECTOR_DB = []

def store_embeddings(chunks):

    # Har chunk ka original text nikalo
    texts = [c.page_content for c in chunks]

    # In texts ki embeddings banao
    vectors = get_embeddings(texts)

    # Text + vector pair ko VECTOR_DB me store karo
    for i in range(len(chunks)):
        VECTOR_DB.append({
            "text": texts[i],
            "vector": vectors[i]
        })

# ------------------------------
# STEP 5: SIMILARITY SEARCH
# ------------------------------

def cosine_similarity(a, b):
    # Cosine similarity formula ka denominator
    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    # Safety: denominator zero hua to divide-by-zero avoid karo
    if denominator == 0:
        return 0.0

    # Final cosine score return
    return np.dot(a, b) / denominator

def normalize_query(text):
    # Query normalize karte hain taaki matching improve ho
    # Example: c++ ko words me convert kiya gaya
    normalized = text.lower().replace("c++", "c plus plus c")

    # Extra spaces hatao
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Clean query return
    return normalized

def tokenize_for_overlap(text):
    # Regex se text ko tokens me todte hain
    tokens = re.findall(r"[a-zA-Z0-9_\+#]+", text.lower())

    # Very short tokens (1 char) drop kar dete hain
    return set(token for token in tokens if len(token) > 1)

def keyword_overlap_score(query, text):
    # Query tokens
    q_tokens = tokenize_for_overlap(query)

    # Agar query tokens hi nahi bache to score 0
    if not q_tokens:
        return 0.0

    # Document tokens
    d_tokens = tokenize_for_overlap(text)

    # Common tokens nikaalo
    overlap = q_tokens.intersection(d_tokens)

    # Query coverage score:
    # Query ke kitne tokens document me mil gaye
    return len(overlap) / len(q_tokens)

def retrieve(query, top_k=5):

    # Agar DB empty hai to context nahi milega
    if not VECTOR_DB:
        return []

    # Query normalize karo
    normalized_query = normalize_query(query)

    # Query ka embedding banao
    query_vec = get_embeddings([normalized_query])[0]

    # Har chunk ka final score yahan collect hoga
    scores = []

    # Hybrid retrieval:
    # 1) Semantic similarity (vector)
    # 2) Keyword overlap (exact-ish match)
    for item in VECTOR_DB:
        # Semantic score
        semantic_score = float(cosine_similarity(query_vec, item["vector"]))

        # Keyword overlap score
        overlap_score = keyword_overlap_score(normalized_query, item["text"])

        # Weighted final score
        score = (0.75 * semantic_score) + (0.25 * overlap_score)

        # Score + text pair store
        scores.append((score, item["text"]))

    # High score pehle lane ke liye descending sort
    scores.sort(reverse=True)

    # Top-k best chunks return karo
    return [text for _, text in scores[:top_k]]

# ------------------------------
# STEP 6: FINAL ANSWER
# ------------------------------

def generate_answer(query, context_chunks):

    # Agar context nahi mila to user ko actionable message do
    if not context_chunks:
        return (
            "Mujhe relevant context nahi mila. Try karo:\n"
            "1) query ko specific banao\n"
            "2) same website ka exact topic URL do\n"
            "3) ya top_k badhao"
        )

    # Retrieved chunks ko ek single context string me join karo
    context = "\n\n".join(context_chunks)

    # LLM ko context + user query bhejkar answer generate karo
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    # System instruction: concise and context-grounded answer
                    "You are a helpful tutor. Use the provided context first and give a direct answer. "
                    "If the user asks a close variant (for example C++ vs C), answer from available context "
                    "and clearly mention the scope in one short line. Keep the answer concise with bullet points."
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{query}
"""
            }
        ]
    )

    # Model ka final text answer return
    return response.choices[0].message.content

# ------------------------------
# MAIN (CLI VERSION)
# ------------------------------

def main():

    # User se website URL input lo
    url = input("Enter website URL: ")

    # URL invalid hua to yahin stop
    if not is_valid_url(url):
        print("Invalid URL. Please enter a valid http/https URL.")
        return

    # Pipeline setup block (load -> split -> store)
    try:
        # STEP 1: load website
        docs = load_website(url)

        # STEP 2: split
        chunks = split_docs(docs)

        # Safety: no chunks means no content
        if not chunks:
            print("No content found from this URL.")
            return

        # STEP 3: store embeddings
        store_embeddings(chunks)

    # Agar setup me koi error aaye to handle karo
    except Exception as exc:
        print(f"Failed to prepare RAG pipeline: {exc}")
        return

    # User ko batado kitne chunks load hue
    print(f"\nLoaded {len(chunks)} chunks")

    # Q&A loop: user multiple questions pooch sakta hai
    while True:
        query = input("\nAsk question (type 'exit'): ")

        # Exit command
        if query == "exit":
            break

        # retrieve relevant chunks
        context = retrieve(query)

        # final answer
        try:
            answer = generate_answer(query, context)

        # Answer generation fail hua to graceful message
        except Exception as exc:
            answer = f"Answer generation failed: {exc}"

        # Final answer print
        print("\nAnswer:")
        print(answer)

# Script direct run hone par main() execute karo
if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# FULL FLOW (END OF PAGE)
# -----------------------------------------------------------------------------
# 1) User URL input
# 2) URL validation (http/https)
# 3) Web page load via WebBaseLoader
# 4) Text chunking (RecursiveCharacterTextSplitter)
# 5) Embeddings create (text-embedding-3-small)
# 6) In-memory vector store build (text + vector)
# 7) User query normalize
# 8) Hybrid retrieval:
#    - Semantic similarity (cosine)
#    - Keyword overlap score
#    - Weighted rank (0.75 semantic + 0.25 keyword)
# 9) Top-k context chunks pick
# 10) LLM answer generation (gpt-4o-mini)
# 11) Final answer print