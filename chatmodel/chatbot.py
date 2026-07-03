from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage

model= ChatMistralAI(model="mistral-small-2506", temperature=0.9)
messages=[
    SystemMessage(content="you are a funny ai agent "), # set the tone of the bot before starting a convo
]
# print("--------------Type 'quit' to exit--------------")
# while True:
#     prompt = input("You:")
#     if prompt == "quit":
#         break
#     response = model.invoke(prompt)
#     print("AI:",response.content)

# till now , it works fine , but this bot will not have memory ,
# so in next prompt , it will be clueless
# so you could have kept list or dictionary as memory , but over time
# when the chat gets long , the bot gets confused 
# even in dictionary , storage becomes the issue 
# this is called short term memory 

# so we use langchain_core.messages. It has 3 parts :
# SystemMessage: tells the model how to talk , like a teacher, sadly , etc (Set the tone of bot)
# HumanMessage: the message given in the form of input by the user, and is stored in json object as content
# AIMessage: the message given by the AI , and is stored in json object as content. 
# This helps maintain context in future interactions 

# so now the code is modified : 

print("--------------Type 'quit' to exit--------------")
while True:
    prompt = input("You :")
    if prompt == "quit":
        break
    
    messages. append (HumanMessage(content=prompt))
    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))
    print("Bot :", response.content)

print (messages)

