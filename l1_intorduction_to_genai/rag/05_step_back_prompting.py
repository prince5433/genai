# =============================================================================
# STEP-BACK PROMPTING (QUERY DECOMPOSITION - ABSTRACT LEVEL)
# =============================================================================

# 📌 KYA HOTA HAI?
# Step-Back Prompting ek technique hai jisme hum directly user ke specific
# question ka answer nahi dete, balki pehle us question ka ek broader (abstract)
# version banate hain.

# 👉 Matlab:
# Specific Question → Broader Question (Step-back)

# -----------------------------------------------------------------------------
# 📌 KYUN USE KARTE HAIN?
# -----------------------------------------------------------------------------

# Problem:
# - Specific query par search karne se limited information milti hai
# - Context incomplete hota hai
# - Important background missing ho sakta hai

# Solution:
# - Ek broader question generate karo
# - Usse zyada general aur rich context retrieve karo
# - Fir usko original query ke context ke saath combine karo

# -----------------------------------------------------------------------------
# 📌 EXAMPLE (IMPORTANT)
# -----------------------------------------------------------------------------

# Original:
# "How does kubelet restart a failed container?"

# Step-back:
# "How does Kubernetes manage container lifecycle?"

# 👉 Result:
# - Step-back → big picture deta hai
# - Original → exact detail deta hai
# - Dono combine → best answer 🔥

# -----------------------------------------------------------------------------
# 📌 FLOW
# -----------------------------------------------------------------------------

# User Query (Specific)
#         ↓
# Generate Step-back Query (Broader)
#         ↓
# Retrieve Context:
#     - Original Query → Specific Info
#     - Step-back Query → Broader Info
#         ↓
# Merge both contexts
#         ↓
# Final Answer (LLM)

# -----------------------------------------------------------------------------
# 📌 BENEFITS
# -----------------------------------------------------------------------------

# ✅ Better context coverage
# ✅ Missing information reduce hoti hai
# ✅ Answer zyada accurate aur complete hota hai
# ✅ Complex questions me reasoning improve hoti hai

# -----------------------------------------------------------------------------
# 📌 FEW-SHOT PROMPTING (MODEL KO TRAIN KARNE KE LIYE)
# -----------------------------------------------------------------------------

# Example 1:
# Original: What is React useEffect cleanup?
# Step-back: How does React manage component lifecycle?

# Example 2:
# Original: How does Docker restart container?
# Step-back: How does container lifecycle management work?

# Example 3:
# Original: What is Kubernetes HPA?
# Step-back: How does Kubernetes handle scaling?

# -----------------------------------------------------------------------------
# 📌 INTERVIEW LINE (IMPORTANT)
# -----------------------------------------------------------------------------

# "Step-back prompting improves retrieval by generating a broader query
# to capture missing context and combining it with the original query."

# =============================================================================
# CODE START
# =============================================================================


# ------------------------------
# IMPORTS
# ------------------------------

from dotenv import load_dotenv      # .env load karne ke liye
import json                         # JSON parsing ke liye
from openai import OpenAI           # OpenAI client

# ------------------------------
# SETUP
# ------------------------------

load_dotenv()                       # API key load karo
client = OpenAI()                  # client initialize

# ------------------------------
# STEP-BACK PROMPT
# ------------------------------

STEPBACK_PROMPT = """
You are an expert at abstraction.

Convert given question into a broader step-back question.

Return JSON:
{
  "original": "same question",
  "stepback": "broader version"
}

Examples:
Original: What is React useEffect cleanup?
Step-back: How does React manage lifecycle?

Original: How does Docker restart container?
Step-back: How does container lifecycle work?
"""

# ------------------------------
# RETRIEVAL PROMPT
# ------------------------------

RETRIEVAL_PROMPT = """
Give 2 short facts about this query.
"""

# ------------------------------
# FINAL PROMPT
# ------------------------------

FINAL_PROMPT = """
Use both contexts (broader + specific) to answer clearly.
"""

# ------------------------------
# FUNCTION: STEP-BACK GENERATE
# ------------------------------

def generate_stepback(question):

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": STEPBACK_PROMPT},
            {"role": "user", "content": question},
        ],
    )

    # JSON parse
    data = json.loads(response.choices[0].message.content)

    # stepback return
    return data["stepback"]

# ------------------------------
# FUNCTION: RETRIEVE CONTEXT
# ------------------------------

def retrieve(query):

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": RETRIEVAL_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    return response.choices[0].message.content

# ------------------------------
# MAIN
# ------------------------------

def main():

    # user input
    question = input("Enter question: ")

    # STEP 1: step-back generate
    stepback = generate_stepback(question)

    print("\nOriginal:", question)
    print("Step-back:", stepback)

    # STEP 2: dono ke liye context lao
    original_context = retrieve(question)
    stepback_context = retrieve(stepback)

    # print contexts
    print("\nOriginal Context:\n", original_context)
    print("\nStep-back Context:\n", stepback_context)

    # STEP 3: final answer
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": FINAL_PROMPT},
            {
                "role": "user",
                "content": f"""
Question: {question}

Broader Context:
{stepback_context}

Specific Context:
{original_context}
"""
            },
        ],
    )

    print("\nFinal Answer:")
    print(response.choices[0].message.content)


# run
if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# FULL FLOW (END OF FILE)
# -----------------------------------------------------------------------------
# 1) User specific question input karta hai
# 2) generate_stepback() uska broader version banata hai
# 3) retrieve() original question ka context lata hai
# 4) retrieve() step-back question ka broader context lata hai
# 5) Dono contexts combine hote hain
# 6) Final LLM answer banta hai
# 7) Output print hota hai