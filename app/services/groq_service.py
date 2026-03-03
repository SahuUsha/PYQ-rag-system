import json
import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_references(context, query):

    prompt = f"""
    you are an expert professeor of college and yu have good teaching experience. You have access to previous year question papers and you are trying to help students by generating new questions based on the previous year questions.
    
    {context}

    Generate new questions related to: {query}

    Return ONLY valid JSON in this format:

    {{
        "similar_questions": [
            {{
                "question": "...",
                "marks": 2,
                "type": "short"
            }}
        ],
        "predicted_long_question": {{
            "question": "...",
            "marks": 5-6,
            "type": "long"
        }},
        "topic_summary": "brief summary"
    }}

    Do NOT use markdown.
    Do NOT add explanations.
    Only return JSON.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content

    return json.loads(content)