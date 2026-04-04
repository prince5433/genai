from dotenv import load_dotenv
from openai import OpenAI

#few shot prompting me model ko kuch examples ke through samjha rahe hai ki hame kis tarah ka output chahiye. isme ham model ko ek system prompt denge jisme ham usko instructions denge ki wo kis tarah se behave kare, uska tone kaisa ho, aur ham usko kuch examples bhi denge jisse usko ye samajh me aa jaye ki ham kis tarah ka output expect kar rahe hai. isse model ko apne response ko generate karne me madad milegi aur hame better output milega.

load_dotenv()
client = OpenAI()

system_prompt="""
You are an AI assistant who is specialized in maths.
You should not answer any query that is not related to maths.

For a given quer help user to solve that along with explanation.

Example:
Input: What is 2+2?
Output: 2+2 is 4 which is calculated by adding 2 and 2 together.

Input:3*10
Output: 3*10 is 30 which is calculated by multiplying 3 and 10 together.Funfact: you can even multply 10*3 and you will get the same answer because of the commutative property of multiplication.

Input: Why is sky blue?
Output: I am sorry but I cannot answer that question as it is not related to maths.
"""
result=client.chat.completions.create(
    # Use a model your project is allowed to access
    model="gpt-4o-mini",
    # temperature=0.7,
    # max_tokens=100,
    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":"what is dog?"}
    ] #zero short prompting
)
print(result.choices[0].message.content)