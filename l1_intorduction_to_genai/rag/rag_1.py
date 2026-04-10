import os
from pathlib import Path
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.exceptions import ResponseHandlingException

# Yaha .env file se secret keys load hoti hain.
load_dotenv()

# Yaha nayi PDF ka path set hai.
pdf_path = Path(__file__).parent / "1620.pdf"

# Ye question model se puchna hai.
query = "Summarize the chapter 'The Last Lesson' from Class 12 English in 5 key points."

# Qdrant me ye collection name use hoga.
collection_name = "genai_rag_last_lesson"

# Qdrant ka URL (default local machine).
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")

# OpenAI key read karo.
openai_api_key = os.getenv("OPENAI_API_KEY")

# Key missing ho to script yahin band kar do.
if not openai_api_key:
    print("Error: OPENAI_API_KEY missing hai. .env me set karo phir run karo.")
    sys.exit(1)

# PDF file na mile to script yahin band kar do.
if not pdf_path.exists():
    print(f"Error: PDF file nahi mili: {pdf_path}")
    sys.exit(1)

# Pehli baar data dalna ho tab True karo, warna False rakho.
INGEST_DATA = False

# PDF load karne ka object banao.
loader = PyPDFLoader(file_path=pdf_path)

# PDF ke pages ko docs me lo.
docs = loader.load()

# Badi text ko chhote chunks me todne ke liye splitter banao.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Docs ko chunks me split karo.
split_docs = text_splitter.split_documents(documents=docs)

# Embedding model banao.
embedder = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=openai_api_key
)

# Agar INGEST_DATA True hai to chunks ko Qdrant me save karo.
if INGEST_DATA:
    QdrantVectorStore.from_documents(
        documents=split_docs,
        url=qdrant_url,
        collection_name=collection_name,
        embedding=embedder
    )
    print("Ingestion Done")

# Existing collection se connect karke similar chunks nikaalo.
try:
    vector_store = QdrantVectorStore.from_existing_collection(
        url=qdrant_url,
        collection_name=collection_name,
        embedding=embedder
    )
    relevant_chunks = vector_store.similarity_search(query=query, k=3)
except ResponseHandlingException:
    print(
        "Error: Qdrant se connect nahi ho pa raha. "
        "Docker Qdrant start karo: docker compose -f docker-compose.db.yml up -d"
    )
    sys.exit(1)

# Chunks ka text jodkar model ko context do.
context_text = "\n\n".join(chunk.page_content for chunk in relevant_chunks)

# Model ko instruction do ki context ke base par answer de.
system_prompt = f"""
You are a helpful assistant for answering questions based on the provided context. Use the following context to answer the question. If you don't know the answer, say you don't know.

context: {context_text}
"""

# OpenAI client banao.
client = OpenAI(timeout=60.0)

# Final answer generate karo.
chat_result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
)

# Answer print karo.
print("Answer:", chat_result.choices[0].message.content)
