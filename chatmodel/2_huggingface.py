import os 
from dotenv import load_dotenv # mandatory step if you are using the model , accesses the .env file

load_dotenv()
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

llm= HuggingFaceEndpoint(
    repo_id= "deepseek-ai/DeepSeek-R1" # repo id --> kis user se liya ?

)

model = ChatHuggingFace(llm=llm)
response= model.invoke(" who are you ?")
print(response.content)