import json
import re

from neo4j import GraphDatabase

openai_client = None
neo4j_driver = None
graph_user_id = "user_1"


def setup_graph(client, neo4j_url, neo4j_username, neo4j_password, user_id="user_1"):
    global openai_client, neo4j_driver, graph_user_id
    openai_client = client
    neo4j_driver = GraphDatabase.driver(
        neo4j_url,
        auth=(neo4j_username, neo4j_password),
    )
    graph_user_id = user_id


def relation_name(text):
    relation = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().upper())
    return relation or "RELATED_TO"


def extract_graph_facts(message):
    result = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """
Extract graph facts from the user message.
Return ONLY valid JSON:
{"facts":[{"source":"User","relation":"LIKES","target":"Python"}]}

Rules:
- Use "User" for I, me, my.
- Split comma/and lists into separate facts.
- Keep relation short and factual.
- If no fact exists, return {"facts":[]}.
""",
            },
            {"role": "user", "content": message},
        ],
    )

    raw = result.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    return json.loads(raw).get("facts", [])


def save_graph_facts(message):
    if openai_client is None or neo4j_driver is None:
        print("neo4j_graph_skipped graph setup missing")
        return

    try:
        facts = extract_graph_facts(message)

        with neo4j_driver.session() as session:
            for fact in facts:
                source = str(fact.get("source", "")).strip()
                relation = relation_name(str(fact.get("relation", "")))
                target = str(fact.get("target", "")).strip()

                if not source or not target:
                    continue

                query = f"""
                MERGE (s:Entity {{name: $source, user_id: $user_id}})
                MERGE (t:Entity {{name: $target, user_id: $user_id}})
                MERGE (s)-[r:{relation}]->(t)
                SET r.updated_at = datetime()
                """
                session.run(query, source=source, target=target, user_id=graph_user_id)

        print("neo4j_graph_facts", facts)
    except Exception as exc:
        print("neo4j_graph_skipped", exc)
