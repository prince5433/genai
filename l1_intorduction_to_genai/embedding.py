from dotenv import load_dotenv
from openai import OpenAI

# 1. Environment variables aur OpenAI client initialization
load_dotenv()  
client = OpenAI()  

text="Eifeel Toweris in Paris and is a famous landmark ,it is 324 meters "

# 2. Text to Vector Embedding Conversion (Semantic Meaning Capture)
# text-embedding-3-small model ka use karke text ke semantic meaning (bhaav/arth) ko numbers ki ek list (vector) me convert karte hain.
response=client.embeddings.create(input=text, model="text-embedding-3-small")

# 3. Embedding Vector output print karna (Yeh vector similarity comparisons ke liye use hota hai)
print("Embedding Vector:", response.data[0].embedding)