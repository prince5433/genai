import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from neo4j import GraphDatabase
from openai import OpenAI


# Hybrid RAG:
# PDF -> chunks -> Qdrant semantic search + Neo4j knowledge graph -> chat answers.

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "pdf_knowledge_graph")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedder = OpenAIEmbeddings(model="text-embedding-3-small")
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URL", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USERNAME", "neo4j"),
        os.getenv("NEO4J_PASSWORD", "reform-william-center-vibrate-press-5829"),
    ),
)


def clean_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"entities": [], "relationships": []}


def safe_type(text: str, default: str = "RELATED_TO") -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", str(text).upper()).strip("_")
    if text and text[0].isdigit():
        text = f"REL_{text}"
    return text or default


def load_pdf(pdf_path: str):
    pages = PyPDFLoader(str(pdf_path)).load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(pages)


def store_to_qdrant(docs: list) -> None:
    QdrantVectorStore.from_documents(
        documents=docs,
        embedding=embedder,
        url=QDRANT_URL,
        collection_name=COLLECTION,
    )
    print(f"[ok] {len(docs)} chunks stored in Qdrant")


def search_qdrant(query: str, k: int = 4) -> str:
    store = QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        collection_name=COLLECTION,
        embedding=embedder,
    )
    docs = store.similarity_search(query, k=k)
    return "\n\n".join(
        f"Source: {doc.metadata.get('source')} | Page: {doc.metadata.get('page')}\n"
        f"{doc.page_content}"
        for doc in docs
    )


def extract_graph(chunk: str) -> dict:
    prompt = f"""
Extract a knowledge graph from the text.
Return ONLY valid JSON:
{{
  "entities": [{{"name": "entity name", "type": "Person/Organization/Concept/Place/Technology/Other"}}],
  "relationships": [{{"source": "entity name", "target": "entity name", "type": "RELATION_TYPE"}}]
}}

Rules:
- Use only facts present in the text.
- Keep names short and consistent.
- Relationship type must be uppercase snake case.

Text:
{chunk}
"""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return clean_json(response.choices[0].message.content or "{}")


def store_to_neo4j(graph: dict) -> None:
    with driver.session() as session:
        for entity in graph.get("entities", []):
            name = str(entity.get("name", "")).strip()
            entity_type = str(entity.get("type", "Other")).strip() or "Other"
            if name:
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type = coalesce(e.type, $type)
                    """,
                    name=name,
                    type=entity_type,
                )

        for rel in graph.get("relationships", []):
            source = str(rel.get("source", "")).strip()
            target = str(rel.get("target", "")).strip()
            rel_type = safe_type(rel.get("type", "RELATED_TO"))

            if not source or not target or source == target:
                continue

            session.run(
                f"""
                MERGE (a:Entity {{name: $source}})
                MERGE (b:Entity {{name: $target}})
                MERGE (a)-[:{rel_type}]->(b)
                """,
                source=source,
                target=target,
            )


def search_neo4j(query: str) -> str:
    keywords = [word.lower() for word in query.split() if len(word) > 2]

    with driver.session() as session:
        rows = session.run(
            """
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE any(k IN $keywords
                WHERE toLower(a.name) CONTAINS k
                   OR toLower(b.name) CONTAINS k
                   OR toLower(type(r)) CONTAINS k)
            RETURN a.name AS source, type(r) AS rel, b.name AS target
            LIMIT 25
            """,
            keywords=keywords,
        ).data()

    if not rows:
        return "No related graph data found."

    return "\n".join(f"{r['source']} -[{r['rel']}]-> {r['target']}" for r in rows)


def pdf_to_knowledge_graph(pdf_path: str) -> None:
    docs = load_pdf(pdf_path)
    print(f"[ok] {len(docs)} chunks created")

    store_to_qdrant(docs)

    for index, doc in enumerate(docs, start=1):
        graph = extract_graph(doc.page_content)
        store_to_neo4j(graph)
        print(
            f"[ok] chunk {index}/{len(docs)}: "
            f"{len(graph.get('entities', []))} entities, "
            f"{len(graph.get('relationships', []))} relationships"
        )

    print("[done] PDF stored in Qdrant + Neo4j")


def chat(query: str, history: list) -> str:
    qdrant_context = search_qdrant(query)
    graph_context = search_neo4j(query)

    system_prompt = f"""
You answer questions using the provided PDF context and knowledge graph.
If the answer is not present in context, say you do not know.

PDF context:
{qdrant_context}

Knowledge graph context:
{graph_context}
"""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": query}],
    )
    return response.choices[0].message.content


def chat_loop() -> None:
    print("\nHybrid RAG Chat: Qdrant + Neo4j")
    print("Type exit to quit.\n")

    history = []
    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        answer = chat(query, history)
        print(f"\nAssistant: {answer}\n")

        history.extend(
            [
                {"role": "user", "content": query},
                {"role": "assistant", "content": answer},
            ]
        )


if __name__ == "__main__":
    import sys

    try:
        if len(sys.argv) > 1:
            pdf_to_knowledge_graph(sys.argv[1])
        chat_loop()
    finally:
        driver.close()
