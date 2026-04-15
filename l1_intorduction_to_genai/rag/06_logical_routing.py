# =============================================================================
# LOGICAL ROUTING (LLM BASED DECISION MAKING)
# =============================================================================

# 📌 KYA HOTA HAI?
# Logical routing ka matlab hai:
# LLM se decide karwana ki user ka question kis lane me jaayega.

# 👉 Simple language me:
# Question aaya → model ne route choose kiya → sahi function chal gaya

# -----------------------------------------------------------------------------
# 📌 REAL LIFE ANALOGY
# -----------------------------------------------------------------------------

# Customer support ka example:
# - Billing ka question → billing team
# - Technical problem → tech team
# - General doubt → FAQ bot

# 👉 Ye routing hai 🔥

# -----------------------------------------------------------------------------
# 📌 AI SYSTEM ME KAHA USE HOTA HAI?
# -----------------------------------------------------------------------------

# - RAG chahiye ya direct answer
# - Code question hai ya normal theory question
# - Math query hai ya general knowledge
# - Tool call karna hai ya nahi

# -----------------------------------------------------------------------------
# 📌 TYPES OF ROUTES (EXAMPLE)
# -----------------------------------------------------------------------------

# 1. "rag"       → jab bahar ka data chahiye
# 2. "direct"    → seedha simple answer
# 3. "code"      → coding se related query

# -----------------------------------------------------------------------------
# 📌 FLOW
# -----------------------------------------------------------------------------

# User question aata hai
#       ↓
# LLM route decide karta hai
#       ↓
# agar route = "rag" → retrieval run karo
# agar route = "code" → coding handler run karo
# warna → direct answer do

# -----------------------------------------------------------------------------
# 📌 BENEFITS
# -----------------------------------------------------------------------------

# ✅ System efficient hota hai
# ✅ Response fast milta hai
# ✅ Sahi pipeline choose hoti hai
# ✅ Cost bachti hai, har baar RAG nahi chalana padta

# -----------------------------------------------------------------------------
# 📌 INTERVIEW LINE
# -----------------------------------------------------------------------------

# "Logical routing uses an LLM to classify user queries and dynamically select
# the appropriate processing pipeline."

# =============================================================================
# CODE START
# =============================================================================

# ------------------------------
# IMPORTS
# ------------------------------

from dotenv import load_dotenv   # .env file se values load karne ke liye
import json                      # JSON ko parse karne ke liye
from openai import OpenAI        # OpenAI ka client banane ke liye

# ------------------------------
# SETUP
# ------------------------------

load_dotenv()                   # .env se API key uthao
client = OpenAI()               # OpenAI client ready karo

# ------------------------------
# ROUTER PROMPT
# ------------------------------

# Ye prompt model ko batata hai ki kaunsa route choose karna hai
ROUTER_PROMPT = """
Classify the user query into one of these routes:

1. "code"   → programming related
2. "rag"    → needs external knowledge / documents
3. "direct" → simple/general question

Return JSON:
{
  "route": "code" or "rag" or "direct"
}
"""

# ------------------------------
# HANDLER 1: DIRECT ANSWER
# ------------------------------

def handle_direct(query):

    # Simple question ka seedha jawab do
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer simply."},
            {"role": "user", "content": query},
        ],
    )

    return response.choices[0].message.content

# ------------------------------
# HANDLER 2: CODE ANSWER
# ------------------------------

def handle_code(query):

    # Code related answer generate karo
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer with code."},
            {"role": "user", "content": query},
        ],
    )

    return response.choices[0].message.content

# ------------------------------
# HANDLER 3: RAG (SIMULATED)
# ------------------------------

def handle_rag(query):

    # Real app me yaha vector DB / retriever hota
    # Abhi demo ke liye fake context use kar rahe hain

    context = "This is some retrieved knowledge related to the query."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer using context."},
            {
                "role": "user",
                "content": f"""
Context: {context}

Question: {query}
"""
            },
        ],
    )

    return response.choices[0].message.content

# ------------------------------
# ROUTER FUNCTION
# ------------------------------

def route_query(query):

    # Query ko classify karne ke liye model call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    # Model se aaya JSON string parse karo
    data = json.loads(response.choices[0].message.content)

    return data["route"]

# ------------------------------
# MAIN
# ------------------------------

def main():

    # User se question lo
    query = input("Enter your question: ")

    # STEP 1: pehle route decide karo
    route = route_query(query)

    print("\nSelected Route:", route)

    # STEP 2: sahi handler chalao
    if route == "code":
        answer = handle_code(query)

    elif route == "rag":
        answer = handle_rag(query)

    else:
        answer = handle_direct(query)

    # Final answer print karo
    print("\nFinal Answer:")
    print(answer)

# Script direct run ho to main() chalao
if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# FULL FLOW (END OF FILE)
# -----------------------------------------------------------------------------
# 1) User question input hota hai
# 2) route_query() question ko classify karti hai
# 3) LLM decide karta hai: code / rag / direct
# 4) Agar route = code  → handle_code() chalega
# 5) Agar route = rag   → handle_rag() chalega
# 6) Agar route = direct → handle_direct() chalega
# 7) Jo answer aata hai wo screen par print hota hai
#
# Simple flow diagram:
# User Query
#     ↓
# route_query()
#     ↓
# LLM decides route
#     ↓
# ┌───────────────┬───────────────┬───────────────┐
# │     code      │      rag      │    direct     │
# │ handle_code() │ handle_rag()  │ handle_direct()│
# └───────────────┴───────────────┴───────────────┘
#     ↓
#   Final Answer