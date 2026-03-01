import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_references(context, query):
    prompt = f"""
    Based on these previous years' questions :
    {context}
    
    Generate at least 5 questions:
    1. Similar reference questions
    2. Predicted 10 mark question
    3. Topic summary
    
    Query: {query}
    """
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role":"user",
                "content": prompt
            }
        ]
    )
    
    return response.choices[0].message.content
    