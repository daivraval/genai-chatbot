from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings= OpenAIEmbeddings(
    model= 'text-embedding-3-large',
    dimensions=64
)

vector = embeddings.embed_query("python is a programming language") 
# query = ask only one thing
# embed_document= ask many things/lines
    
print(vector)

