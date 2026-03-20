import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def expand_query(query: str):
    """
    Enhances the user query into a 2-3 line description and generates 3 semantic variations.
    """
    try:
        prompt = f"""
        Objective: Rephrase and expand the user's search query to find related academic/exam questions.
        
        User Query: "{query}"
        
        Tasks:
        1. Enhance the query: Rewrite the query into 2-3 detailed lines that capture the core academic intent, subject matter, and technical keywords. Focus on what an examiner would ask.
        2. Variations: Provide 3 semantic variations that specifically look like university exam questions related to the topic.
        
        Return JSON output with EXACTLY these keys:
        {{
            "enhanced_query": "The 2-3 line expanded version here.",
            "variations": ["variation 1", "variation 2", "variation 3"]
        }}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Slightly higher temperature for better variety
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        return {
            "enhanced_query": data.get("enhanced_query", query),
            "variations": data.get("variations", [query])
        }

    except Exception as e:
        print(f"Expansion failed: {e}")
        return {
            "enhanced_query": query,
            "variations": [query]
        }