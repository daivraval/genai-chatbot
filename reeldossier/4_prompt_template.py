# ReelDossier wants to build an Al-powered tool that:
# 1. Takes a raw paragraph about a movie
# 2. Extracts important structured information
# 3. Generates a clean summary
# 4. Returns it in JSON format
# 5. Stores it in their database

# Todays task :- 3 movies

# Paragraph:
# Interstellar is a visually stunning science fiction epic directed by Christopher Nolan.
# Released in 2014, the film stars Matthew McConaughey, Anne Hathaway, Jessica Chastain,
# and Michael Caine. The story revolves around a group of astronauts who travel through a
# wormhole near Saturn in search of a new home for humanity as Earth faces environmental
# collapse. The movie was widely appreciated for its emotional depth, scientific accuracy, and
# Hans Zimmer's powerful soundtrack. It holds a rating of 8.6 on IMDb and is often considered
# one of the greatest sci-fi films of the 21st century.


# but for a company , if given 100 movies per day , we cant prompt every time for the new movie
# so we use prompt templates . It is a fixed template for specific task to be prompted
# but it contains a {} that can fit different things( in this case, movies) 

from dotenv import load_dotenv 
load_dotenv()
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

model=ChatMistralAI(model="mistral-small-2506")

prompt = ChatPromptTemplate.from_messages([
    ("system",
"""You are an expert data extraction assistant. Analyze the provided paragraph and extract key information into the exact format shown below. 

Do not include any conversational filler, intro, or outro text. Extract only what is present in the text. If an element is missing, write "Not mentioned".

### Expected Output Format ###
Movie Name: [Name]
Release Year: [Year]
Director: [Director]
Cast: [Comma-separated list of actors]
Genre: [Genre]
Key Themes: [Core themes or plot points, e.g., space travel, survival]
IMDb Rating: [Rating/10 or Not mentioned]
Quick Summary: [A concise 1-2 sentence summary of the plot and reception]

### Example ###
Paragraph: "The Matrix is a 1999 science fiction action film written and directed by the Wachowskis. It stars Keanu Reeves, Laurence Fishburne, and Carrie-Anne Moss. It depicts a dystopian future in which humanity is unknowingly trapped inside a simulated reality."
Output:
Movie Name: The Matrix
Release Year: 1999
Director: The Wachowskis
Cast: Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss
Genre: Science Fiction, Action
Key Themes: Dystopian future, simulated reality, AI control
IMDb Rating: Not mentioned
Quick Summary: A 1999 sci-fi action film directed by the Wachowskis starring Keanu Reeves, where humanity is trapped in a simulated reality.
"""),
("Human",
"""
### Task ###
Paragraph: {paragraph}
Output:""")
])
para = input("Give you paragraph : ")
final_prompt=prompt.invoke(
    {"paragraph":para})

response=model.invoke(final_prompt)
print (response.content)

