# ------------------------------


# Query Decomposition (easy Hinglish):
# Iska matlab hai step-by-step pipeline.
# Har next step, previous step ke output par depend karta hai.
# Example flow: question samjho -> query banao -> retrieve karo -> final answer synthesize karo.
# Is approach me hum zyada control rakhte hain har step par.
# Har step ke liye alag prompt design kar sakte hain.
# IMPORTS
# ------------------------------

# .env load karne ke liye
from dotenv import load_dotenv

# JSON handle karne ke liye
import json

# OpenAI client
from openai import OpenAI

# ------------------------------
# SETUP
# ------------------------------

# .env load karo
load_dotenv()

# OpenAI client init
client = OpenAI()

# ------------------------------
# PROMPTS
# ------------------------------

# STEP 1: question ko todna
DECOMPOSE_PROMPT = """
Break the question into 3 simple sub-questions.

Return JSON:
{
  "steps": ["step1", "step2", "step3"]
}
"""

# STEP 2: har step solve karna
SOLVE_PROMPT = """
Answer this step clearly in 1-2 lines.
"""

# STEP 3: final combine
FINAL_PROMPT = """
Combine all answers into one final answer.
"""

# ------------------------------
# STEP 1: DECOMPOSE
# ------------------------------

def decompose(question):

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": DECOMPOSE_PROMPT},
            {"role": "user", "content": question},
        ],
    )

    # JSON parse
    data = json.loads(response.choices[0].message.content)

    return data["steps"]

# ------------------------------
# STEP 2: SEQUENTIAL SOLVING
# ------------------------------

def solve_steps(steps):

    answers = []

    # har step ek ke baad ek solve hoga
    for i, step in enumerate(steps):

        # previous answers ko context me bhej rahe hain
        context = "\n".join(answers)

        # OpenAI call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SOLVE_PROMPT},
                
                # IMPORTANT: previous output use ho raha hai
                {
                    "role": "user",
                    "content": f"""
Step: {step}

Previous Answers:
{context}
"""
                },
            ],
        )

        # current step ka answer
        ans = response.choices[0].message.content

        # list me add karo (next step use karega)
        answers.append(ans)

    return answers

# ------------------------------
# STEP 3: FINAL COMBINE
# ------------------------------

def final_answer(question, answers):

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": FINAL_PROMPT},
            {
                "role": "user",
                "content": f"""
Question: {question}

Step Answers:
{answers}
"""
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

    # STEP 1: break question
    steps = decompose(question)

    print("\nSteps:")
    print(steps)

    # STEP 2: solve step-by-step (dependency chain)
    answers = solve_steps(steps)

    print("\nStep Answers:")
    for a in answers:
        print("-", a)

    # STEP 3: final answer
    final = final_answer(question, answers)

    print("\nFinal Answer:")
    print(final)

# run
if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# FULL FLOW (END OF FILE)
# -----------------------------------------------------------------------------
# 1) User question input hota hai
# 2) decompose() question ko 3 simple steps me todta hai
# 3) solve_steps() har step ko previous answers ke saath solve karta hai
# 4) Answers list me save hote hain
# 5) final_answer() sab answers ko combine karta hai
# 6) Final response print hota hai