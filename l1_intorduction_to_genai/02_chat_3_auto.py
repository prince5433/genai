import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

system_prompt = """
You are an AI assistant who is expert in breaking down complex problems and then resolve the user query.

For the given user input, analyse the input and break down the problem step by step.
Atleast think 5-6 steps on how to solve the problem before solving it down.

The steps are you get a user input, you analyse, you think, you again think for several times and then return an output with explanation and then finally you validate the output as well before giving final result.

Follow the steps in sequence that is "analyse", "think", "output", "validate" and finally "result".

Rules:
1. Follow the strict JSON output as per Output schema.
2. Always perform one step at a time and wait for next input
3. Carefully analyse the user query

Output Format:
{{ step: "string", content: "string" }}

Example:
Input: What is 2 + 2.
Output: {{ step: "analyse", content: "Alright! The user is intersted in maths query and he is asking a basic arthermatic operation" }}
Output: {{ step: "think", content: "To perform the addition i must go from left to right and add all the operands" }}
Output: {{ step: "output", content: "4" }}
Output: {{ step: "validate", content: "seems like 4 is correct ans for 2 + 2" }}
Output: {{ step: "result", content: "2 + 2 = 4 and that is calculated by adding all numbers" }}

"""

messages = [
    { "role": "system", "content": system_prompt },
]


query = input("> ") # user se input lena
messages.append({ "role": "user", "content": query })# user ke input ko messages me add karna taki model uske basis pe response de sake


while True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=messages
    )

    parsed_response = json.loads(response.choices[0].message.content)# model ke response ko json me parse karna taki uske step aur content ko alag se access kar sake
    messages.append({ "role": "assistant", "content": json.dumps(parsed_response) })# model ke response ko messages me add karna taki model apne pichle response ko dekh ke agla response de sake

    if parsed_response.get("step") != "output":# agar step output nahi hai to iska matlab hai ki model abhi tak problem ko solve karne ke process me hai aur hame uska content dikhana chahiye taki hame pata chale ki model problem ko kaise solve kar raha hai
        print(f"🧠: {parsed_response.get("content")}")
        continue
    
    print(f"🤖: {parsed_response.get("content")}")# output dikha do yaha pe
    break



