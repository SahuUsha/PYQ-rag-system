import json
import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_references(context, query):
    """
    Generates academic reference questions when no results are found in the database.
    """
    prompt = f"""
    Objective: You are an expert university professor. Generate a set of high-quality exam questions related to the user's query.
    
    Context: {context if context else "No additional context provided."}
    User Query: {query}
    
    Requirements:
    1. Generate at least 5 SIMILAR SHORT QUESTIONS (2-3 marks each).
    2. Generate 1 PREDICTED LONG QUESTION (5-10 marks).
    3. Provide a brief TOPIC SUMMARY (2-3 sentences).
    
    Return ONLY a single valid JSON object with the following structure:
    {{
        "similar_questions": [
            {{ "question": "Short Question 1", "marks": 2, "type": "short" }},
            {{ "question": "Short Question 2", "marks": 3, "type": "short" }},
            {{ "question": "Short Question 3", "marks": 2, "type": "short" }},
            {{ "question": "Short Question 4", "marks": 2, "type": "short" }},
            {{ "question": "Short Question 5", "marks": 3, "type": "short" }}
        ],
        "predicted_long_question": {{
            "question": "A comprehensive long question here.",
            "marks": 10,
            "type": "long"
        }},
        "topic_summary": "A brief explanation of why these topics are important."
    }}
    
    Constraints:
    - ONLY return JSON.
    - No markdown, no explanations, no prefixing.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Reference generation failed: {e}")
        return {
            "similar_questions": [],
            "predicted_long_question": None,
            "topic_summary": "Could not generate references at this time."
        }
