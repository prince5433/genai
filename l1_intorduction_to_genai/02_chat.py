from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

result=client.chat.completions.create(
    # Use a model your project is allowed to access
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"Hey there!"}] #zero short prompting
)
print(result.choices[0].message.content)

