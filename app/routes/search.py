from fastapi import APIRouter
from app.services.embedding import generate_embedding
from app.services.qdrant_service import search_vector
from app.services.db_service import get_questions_by_ids
from app.services.groq_service import generate_references

router = APIRouter()

@router.get("/search")
def search(query: str, page: int = 1, limit: int = 5):

    # 1️⃣ Generate embedding
    embedding = generate_embedding(query)

    # 2️⃣ Search in vector DB
    question_ids = search_vector(embedding, limit=limit)

    # 3️⃣ Retrieve from SQL DB
    retrieved_questions = get_questions_by_ids(question_ids)

    # 4️⃣ If found → Return DB data
    if retrieved_questions:
        return {
            "source": "database",
            "page": page,
            "retrieved_questions": retrieved_questions,
            "generated_content": None
        }

    # 5️⃣ If not found → Generate
    generated_content = generate_references("", query)

    return {
        "source": "generated",
        "page": page,
        "retrieved_questions": [],
        "generated_content": generated_content
    }