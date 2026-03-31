from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Load environment variables from .env file
client = OpenAI()  # Initialize the OpenAI client

text="Eifeel Toweris in Paris and is a famous landmark ,it is 324 meters "

response=client.embeddings.create(input=text, model="text-embedding-3-small")

#text-embedding-3-small is a model that generates vector embeddings for text. It is designed to capture the semantic meaning of the input text and represent it as a high-dimensional vector. This allows us to compare the similarity between different pieces of text based on their embeddings.

print("Embedding Vector:", response.data[0].embedding) #Embedding Vector: [0.001, 0.002, 0.003, ...] (example output)