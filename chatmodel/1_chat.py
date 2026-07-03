from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model #initialise a standalone chat model 

from langchain_mistralai import ChatMistralAI # importing a model's specific SDK

model = init_chat_model(model="gpt-5.1")
print(model)
response = model.invoke("why do parrots talk ?")

print(response) # most basic usage of the model to get the content . 
# Do not run this, Im not running this i have limited tokens bro .


print(response.content) # to get only the content 

# if you are using an open source like groq, you have to specify that model like :
model = init_chat_model("groq:openai/gpt-oss-120b")
print(model.invoke("why do parrots talk ?")) 

# Parameters =Temperature
# If you want more creativity in the response you have to keep the temperature higher 
# if you want more deterministic response you have to keep the temperature lower 
# Temperature values range from 0 to 1 
# If you want mathematical/Logical reponse , lower the temperature 

model = ChatMistralAI(model="mistral-small-2506",temperature=0,max_tokens=20)
# max_tokens = maximum output tokens u want to generate 

# Now , ChatGPT, Gemini are closed source , meaning , you pay - you use
# HuggingFace is open source , you can use many models for free . People make their LLMs,
# and other users are allowed to improve that model , and HuggingFace provides a platform
# where all these models can be stored at a place 