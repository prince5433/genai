# Parallel Query Fan-out Retrieval (Easy Hinglish):
# User ka 1 sawaal lete hain, usko multiple chhoti search queries me todte hain,
# fir sab queries ko ek saath (parallel) chalate hain taaki jaldi aur better info mile,
# aur end me sab results jod ke final answer dete hain.
#

# ------------------------------
# STEP 0: IMPORTS
# ------------------------------

# .env file load karne ke liye
from dotenv import load_dotenv

# JSON data handle karne ke liye
import json

# parallel execution ke liye
from concurrent.futures import ThreadPoolExecutor

# OpenAI client import
from openai import OpenAI

# ------------------------------
# STEP 1: SETUP
# ------------------------------

# .env file load karo (isme API key hai)
load_dotenv()

# OpenAI client bana rahe hain
client = OpenAI()

# ------------------------------
# STEP 2: SYSTEM PROMPTS
# ------------------------------

# Ye prompt model ko bolta hai:
# ek question ko 3 chhoti queries me tod
QUERY_PROMPT = """
Convert user question into exactly 3 short search queries.

Return JSON:
{
  "queries": ["q1", "q2", "q3"]
}
"""

# Ye prompt har query ke liye data generate karega
RETRIEVAL_PROMPT = """
For given query, give 2 short facts.

Return JSON:
{
  "query": "string",
  "facts": ["fact1", "fact2"]
}
"""

# Final answer banane ka prompt
FINAL_PROMPT = """
Use given data and answer clearly.
"""

# ------------------------------
# STEP 3: QUERY GENERATION
# ------------------------------

def generate_queries(question):
    
    # OpenAI ko call kar rahe hain
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        
        # JSON output force kar rahe hain
        response_format={"type": "json_object"},
        
        # messages bhej rahe hain
        messages=[
            {"role": "system", "content": QUERY_PROMPT},
            {"role": "user", "content": question},
        ],
    )

    # model ka output JSON string hota hai → parse karo
    data = json.loads(response.choices[0].message.content)

    # queries list return karo
    return data["queries"]

# ------------------------------
# STEP 4: SINGLE QUERY RETRIEVAL
# ------------------------------

def retrieve(query):
    
    # ek query ke liye OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": RETRIEVAL_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    # JSON parse karke return
    return json.loads(response.choices[0].message.content)

# ------------------------------
# STEP 5: PARALLEL EXECUTION
# ------------------------------

def parallel_retrieval(queries):
    
    # results store karne ke liye list
    results = []

    # ThreadPoolExecutor → parallel execution
    with ThreadPoolExecutor(max_workers=3) as executor:

        # har query ko ek thread me run kar rahe hain
        futures = [executor.submit(retrieve, q) for q in queries]

        # sabke results collect karo
        for future in futures:
            results.append(future.result())

    # final results return
    return results

# ------------------------------
# STEP 6: FINAL ANSWER
# ------------------------------

def generate_final_answer(question, data):
    
    # OpenAI call final answer ke liye
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": FINAL_PROMPT},
            
            # question + data dono bhej rahe hain
            {
                "role": "user",
                "content": json.dumps({
                    "question": question,
                    "data": data
                }),
            },
        ],
    )

    # final answer return
    return response.choices[0].message.content

# ------------------------------
# STEP 7: MAIN PROGRAM
# ------------------------------

def main():
    
    # user se input lo
    question = input("Enter your question: ")

    # STEP 1: queries generate
    queries = generate_queries(question)

    # queries print karo
    print("\nGenerated Queries:")
    print(queries)

    # STEP 2: parallel retrieval
    results = parallel_retrieval(queries)

    # results print karo
    print("\nRetrieved Data:")
    print(json.dumps(results, indent=2))

    # STEP 3: final answer generate
    answer = generate_final_answer(question, results)

    # final answer print karo
    print("\nFinal Answer:")
    print(answer)

# program start yaha se hota hai
if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# FULL FLOW (END OF FILE)
# -----------------------------------------------------------------------------
# 1) User question input hota hai
# 2) generate_queries() question ko 3 short queries me todta hai
# 3) parallel_retrieval() tino queries ko ek saath run karta hai
# 4) Har query se short facts milte hain
# 5) Sab results collect hote hain
# 6) generate_final_answer() un results se final response banata hai
# 7) Final answer print hota hai
