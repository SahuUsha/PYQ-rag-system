import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def expand_query(query: str):
    """
    Strong semantic query expansion:
    - fixes spelling
    - adds synonyms
    - adds concept terms
    - generates variations
    """

    try:
        prompt = f"""
You are an expert academic search assistant.

User Query:
"{query}"

Your job is to deeply expand this query for semantic search.

🔹 Tasks:

1. Correct spelling mistakes (if any)
2. Keep original meaning STRICTLY (no topic drift)
3. Generate:
   - synonyms (different wording)
   - concept terms (related academic terms)
   - alternate terminology used in exams
4. Include BOTH:
   - short phrases
   - full exam-style questions
5. Include hidden/related concepts students may use

🔹 Example:
"cyclomatic complexity"
→ "McCabe complexity", "control flow graph complexity", "basis path testing"

---

🔹 Return JSON ONLY:

{{
  "corrected_query": "...",

  "enhanced_query": "...",

  "keywords": [
    "...", "...", "..."
  ],

  "concepts": [
    "...", "...", "..."
  ],

  "variations": [
    "...",
    "...",
    "..."
  ]
}}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # slightly higher for diversity
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        # 🔥 Merge EVERYTHING into search queries
        all_queries = list(set(
            [query] +
            [data.get("corrected_query", "")] +
            [data.get("enhanced_query", "")] +
            data.get("keywords", []) +
            data.get("concepts", []) +
            data.get("variations", [])
        ))

        # remove empty strings
        all_queries = [q.strip() for q in all_queries if q.strip()]

        return {
            "main_query": data.get("corrected_query", query),
            "all_queries": all_queries
        }

    except Exception as e:
        print(f"Expansion failed: {e}")
        return {
            "main_query": query,
            "all_queries": [query]
        }