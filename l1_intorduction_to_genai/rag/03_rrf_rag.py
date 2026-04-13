# RRF (Reciprocal Rank Fusion) kya hota hai? (Easy Hinglish):
# Jab multiple retrieval lists aati hain (alag-alag queries se), to har list ka top result zyada important hota hai.
# RRF me hum rank ke basis par score dete hain: score ~ 1 / (k + rank).
# Matlab jo document har list me upar-upar baar baar aata hai, uska total score high ho jata hai.
# Simple words me: RRF alag lists ko fair way me merge karta hai aur common strong results ko top pe laata hai.
# Isse final answer me zyada relevant aur diverse information milti hai.
# ------------------------------
# IMPORTS
# ------------------------------

# .env load karne ke liye
from dotenv import load_dotenv

# JSON handle karne ke liye
import json

# parallel execution ke liye
from concurrent.futures import ThreadPoolExecutor

# OpenAI client
from openai import OpenAI

# ------------------------------
# SETUP
# ------------------------------

# .env load karo
load_dotenv()

# OpenAI client
client = OpenAI()

# ------------------------------
# PROMPTS
# ------------------------------

# Query generate karne ke liye
QUERY_PROMPT = """
Convert question into 3 search queries.

Return JSON:
{
  "queries": ["q1","q2","q3"]
}
"""

# Retrieval ke liye
RETRIEVAL_PROMPT = """
For query, return 3 results.

Return JSON:
{
  "results": [
    {"id": "doc1", "text": "info1"},
    {"id": "doc2", "text": "info2"},
    {"id": "doc3", "text": "info3"}
  ]
}
"""

# Final answer
FINAL_PROMPT = """
Answer using given ranked data.
"""

# ------------------------------
# STEP 1: QUERY GENERATION
# ------------------------------

def generate_queries(question):

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": QUERY_PROMPT},
            {"role": "user", "content": question},
        ],
    )

    # JSON parse
    data = json.loads(response.choices[0].message.content)

    return data["queries"]

# ------------------------------
# STEP 2: RETRIEVE RESULTS
# ------------------------------

def retrieve(query):

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": RETRIEVAL_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    # JSON parse
    return json.loads(response.choices[0].message.content)["results"]

# ------------------------------
# STEP 3: PARALLEL RETRIEVAL
# ------------------------------

def parallel_retrieve(queries):

    results = []

    # parallel execution
    with ThreadPoolExecutor(max_workers=3) as executor:

        futures = [executor.submit(retrieve, q) for q in queries]

        for f in futures:
            results.append(f.result())

    return results  # list of list

# ------------------------------
# STEP 4: RRF ALGORITHM
# ------------------------------

def rrf_fusion(all_results, k=60):

    # final scores store karne ke liye dict
    scores = {}

    # har query ke results loop
    for result_list in all_results:

        # rank start hota hai 1 se
        for rank, item in enumerate(result_list, start=1):

            doc_id = item["id"]

            # RRF formula:
            # score = 1 / (rank + k)
            score = 1 / (rank + k)

            # agar doc already hai to add karo
            if doc_id in scores:
                scores[doc_id] += score
            else:
                scores[doc_id] = score

    # scores ko sort karo (high to low)
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_docs

# ------------------------------
# STEP 5: FINAL ANSWER
# ------------------------------

def final_answer(question, ranked_docs):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": FINAL_PROMPT},
            {
                "role": "user",
                "content": json.dumps({
                    "question": question,
                    "ranked_docs": ranked_docs
                }),
            },
        ],
    )

    return response.choices[0].message.content

# ------------------------------
# MAIN
# ------------------------------

def main():

    # user input
    question = input("Enter question: ")

    # STEP 1: queries
    queries = generate_queries(question)
    print("\nQueries:", queries)

    # STEP 2: parallel retrieval
    all_results = parallel_retrieve(queries)

    print("\nRaw Results:")
    print(json.dumps(all_results, indent=2))

    # STEP 3: RRF fusion
    ranked = rrf_fusion(all_results)

    print("\nRRF Ranked Docs:")
    print(ranked)

    # STEP 4: final answer
    answer = final_answer(question, ranked)

    print("\nFinal Answer:")
    print(answer)

# run
if __name__ == "__main__":
    main()