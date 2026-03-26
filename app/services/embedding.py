import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"


def clean_text(text):
    return text.lower().strip().replace("\n", " ")


def generate_embedding(text: str):

    if not text or not text.strip():
        return None   # 🔥 FIXED

    try:
        text = clean_text(text)
        text = text[:1000]   # 🔥 LIMIT LENGTH

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text
        )

        if hasattr(result, "embeddings") and len(result.embeddings) > 0:
            return result.embeddings[0].values

    except Exception as e:
        print("Embedding error:", e)

    return None