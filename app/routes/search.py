from fastapi import APIRouter
from app.services.embedding import generate_embedding
from app.services.qdrant_service import search_vector
from app.services.db_service import get_questions_by_ids
from app.services.groq_service import generate_reference

router = APIRouter()

@router.get("/search")
def search(query: str, page: int = 1, limit: int = 5):

    offset = (page - 1) * limit

    # 🔹 Convert query to embedding
    query_vector = generate_embedding(query)

    # 🔹 Search from Qdrant
    results = search_vector(
        query_vector=query_vector,
        limit=limit,
        offset=offset
    )

    # 🔹 If DB has results
    if results:
        ids = [r.id for r in results]
        questions = get_questions_by_ids(ids)

        return {
            "source": "database",
            "page": page,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "marks": q.marks,
                    "year": q.year,
                    "exam_type": q.exam_type
                }
                for q in questions
            ]
        }

    # 🔥 If DB exhausted → Generate new questions
    generated_output = generate_reference("", query)

    return {
        "source": "generated",
        "page": page,
        "generated_questions": generated_output
    }
    