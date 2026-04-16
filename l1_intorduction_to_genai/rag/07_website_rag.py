# Yeh script website-based RAG banata hai using OpenAI + Qdrant.

# OS level env variables read/set karne ke liye.
import os
# Python version check ke liye.
import sys
# .env file se environment variables load karne ke liye.
from dotenv import load_dotenv

# URL ko parse karke validate karne ke liye.
from urllib.parse import urlparse

# Env vars start me load karo taaki baaki modules ko values mil jaye.
load_dotenv()
# USER_AGENT default set karo taaki WebBaseLoader warning na de.
os.environ.setdefault("USER_AGENT", "rag-qdrant-prod/1.0")

# Website content fetch/load karne ke liye loader.
from langchain_community.document_loaders import WebBaseLoader
# Documents ko chunks me todne ke liye text splitter.
from langchain_text_splitters import RecursiveCharacterTextSplitter

# OpenAI embedding model wrapper.
from langchain_openai import OpenAIEmbeddings
# OpenAI chat model wrapper.
from langchain_openai import ChatOpenAI

# Qdrant vector store integration (new package path).
from langchain_qdrant import QdrantVectorStore


# Embedding model initialize karo (text -> vector).
embeddings = OpenAIEmbeddings(
    # Chhota, fast aur cost-effective embedding model.
    model="text-embedding-3-small"
)

# LLM initialize karo jo final answer banayega.
llm = ChatOpenAI(
    # Chat completion ke liye selected model.
    model="gpt-4o-mini",
    # Deterministic output ke liye temperature 0.
    temperature=0
)


def is_valid_url(url):
    # URL ko parse karo (scheme, netloc, path etc.).
    parsed = urlparse(url)
    # Valid tab hi manenge jab scheme http/https ho aur domain present ho.
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def load_website(url):
    # Loader object banao with URL and custom User-Agent.
    loader = WebBaseLoader(
        # Jo website scrape karni hai.
        web_path=url,
        # Request header me User-Agent bhejo.
        header_template={"User-Agent": os.environ["USER_AGENT"]}
    )
    # Website se docs load karo.
    docs = loader.load()
    # Loaded docs list return karo.
    return docs


def split_docs(docs):

    # Splitter config set karo.
    splitter = RecursiveCharacterTextSplitter(
        # Ek chunk me approx 500 chars.
        chunk_size=500,
        # Context continuity ke liye 100 chars overlap.
        chunk_overlap=100
    )

    # Input docs ko chunks me convert karo.
    chunks = splitter.split_documents(docs)

    # Chunk list return karo.
    return chunks


def create_qdrant_store(chunks):
    # Qdrant URL env se lo, warna localhost default use karo.
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    # Collection ka naam env se lo, warna rag_collection use karo.
    collection_name = os.getenv("QDRANT_COLLECTION", "rag_collection")
    # Connection fail ho to memory fallback allowed hai ya nahi.
    fallback_to_memory = os.getenv("QDRANT_FALLBACK_TO_MEMORY", "true").lower() == "true"

    try:
        # Pehle external Qdrant (Docker/server) par documents index karo.
        vector_store = QdrantVectorStore.from_documents(
            # Chunked documents to be embedded and stored.
            documents=chunks,
            # Embedding function/model.
            embedding=embeddings,
            # Qdrant server URL.
            url=qdrant_url,
            # Target collection name.
            collection_name=collection_name,
            # Version check warning avoid karne ke liye.
            check_compatibility=False
        )
        # Success ho gaya to vector store return karo.
        return vector_store
    except Exception as exc:
        # Agar fallback disabled hai to explicit runtime error throw karo.
        if not fallback_to_memory:
            raise RuntimeError(
                "Qdrant connection failed. Start Qdrant on localhost:6333 "
                "(or set QDRANT_URL) and retry. "
                f"Original error: {exc}"
            ) from exc

        # User ko warning do ki external Qdrant connect nahi hua.
        print(
            "Warning: Could not connect to external Qdrant at "
            f"{qdrant_url}. Falling back to in-memory vector store."
        )
        # Original exception details bhi print karo for debugging.
        print(f"Details: {exc}")

        # Fallback: in-memory vector store banao (temporary, RAM-only).
        return QdrantVectorStore.from_documents(
            # Same docs memory store me daalo.
            documents=chunks,
            # Same embeddings use karo.
            embedding=embeddings,
            # :memory: matlab persistent DB nahi, sirf RAM.
            location=":memory:",
            # Same collection name use karo.
            collection_name=collection_name
        )


def warn_on_python_version():
    # Python version 3.14 ya above ho to warning show karo.
    if sys.version_info >= (3, 14):
        # Friendly display ke liye short version string banao.
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        # Compatibility guidance print karo.
        print(
            "Warning: Python "
            f"{version} may be incompatible with LangChain components using Pydantic v1. "
            "Use Python 3.11 to 3.13 for best compatibility."
        )


def retrieve(query, vector_store):

    # User query ke against similarity search chalao.
    docs = vector_store.similarity_search(
        # Search query text.
        query,
        # Top 5 relevant chunks return karo.
        k=5
    )

    # Documents se sirf page_content निकाल ke list return karo.
    return [doc.page_content for doc in docs]


def generate_answer(query, context_chunks):

    # Agar retrieval se context empty aaya to direct message return karo.
    if not context_chunks:
        return "No relevant context found."

    # Multiple chunks ko ek context string me join karo.
    context = "\n\n".join(context_chunks)

    # LLM prompt tayyar karo jisme context + question ho.
    prompt = f"""
    You are a helpful assistant.

    Context:
    {context}

    Question:
    {query}

    Answer in bullet points.
    """

    # Chat model invoke karke response lo.
    response = llm.invoke(prompt)

    # Final generated text return karo.
    return response.content


def main():

    # Start me Python compatibility warning check.
    warn_on_python_version()

    # User se target website URL input lo.
    url = input("Enter website URL: ")

    # Invalid URL ho to turant stop kar do.
    if not is_valid_url(url):
        # Invalid URL message print karo.
        print("Invalid URL")
        # Function end.
        return

    try:
        # Website data load karo.
        docs = load_website(url)

        # Loaded docs ko chunks me split karo.
        chunks = split_docs(docs)

        # Agar chunks nahi bane to process stop.
        if not chunks:
            # No content message print karo.
            print("No content found")
            # Function end.
            return

        # Qdrant vector store create/connect/index karo.
        vector_store = create_qdrant_store(chunks)

    except Exception as e:
        # Runtime error ko readable way me print karo.
        print(f"Error: {e}")
        # Error case me function end.
        return

    # User ko successful chunk count show karo.
    print(f"Loaded {len(chunks)} chunks")

    # Interactive Q&A loop start.
    while True:
        # Har iteration me query input lo.
        query = input("\nAsk question (type 'exit'): ")

        # exit type karte hi loop break.
        if query == "exit":
            break

        # Query ke liye relevant context chunks lao.
        context = retrieve(query, vector_store)

        # Retrieved context se final answer generate karo.
        answer = generate_answer(query, context)

        # Answer heading print karo.
        print("\nAnswer:")
        # Actual generated answer print karo.
        print(answer)


if __name__ == "__main__":
    # Script direct chal rahi hai to main function run karo.
    main()


# FLOW DIAGRAM (HIGH-LEVEL)
# [Start]
#    |
#    v
# [Load .env + set USER_AGENT]
#    |
#    v
# [Input URL] --> [Validate URL]
#                    | valid? no --> [Print Invalid URL + Exit]
#                    v yes
#               [Load Website Docs]
#                    |
#                    v
#               [Split into Chunks]
#                    | empty? yes --> [Print No content + Exit]
#                    v no
#               [Create Qdrant Store]
#                    | fail + fallback false --> [Raise Error + Exit]
#                    | fail + fallback true  --> [Use In-Memory Store]
#                    v
#               [Ask Query Loop]
#                    |
#                    v
#               [Retrieve Top-k Chunks]
#                    |
#                    v
#               [Generate Answer via LLM]
#                    |
#                    v
#               [Print Answer]
#                    |
#                    v
#               [exit? yes -> End | no -> Ask next query]