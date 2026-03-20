from fastapi import APIRouter
from app.services.embedding import generate_embedding
from app.services.qdrant_service import search_vector
from app.services.db_service import get_questions_by_ids
from app.services.groq_service import generate_references
from app.services.query_expansion_service import expand_query

router = APIRouter()

@router.get("/search")
def search(query: str, page: int = 1, limit: int = 5):
    # 1️⃣ Expand Query (Enhanced + Variations)
    expansion_data = expand_query(query)
    enhanced_query = expansion_data.get("enhanced_query", query)
    variations = expansion_data.get("variations", [])
    
    # Combine all queries to embed
    all_queries = [enhanced_query] + variations
    
    # 2️⃣ Multi-Embedding Retrieval
    all_question_ids = []
    
    # Increase per-query limit to get more results for aggregation
    search_depth = 10 # Search for more results per variation
    
    for q in all_queries:
        emb = generate_embedding(q)
        ids = search_vector(emb, limit=search_depth)
        all_question_ids.extend(ids)
    
    # Deduplicate while preserving order of first appearance
    seen = set()
    unique_question_ids = []
    for qid in all_question_ids:
        if qid not in seen:
            unique_question_ids.append(qid)
            seen.add(qid)
    
    # User requested to remove limitation: Return all unique results found
    final_ids = unique_question_ids

    # 3️⃣ Retrieve from SQL DB
    retrieved_questions = get_questions_by_ids(final_ids)

    # 4️⃣ Generate References (Always, using retrieved questions as context if found)
    context = ""
    if retrieved_questions:
        # Extract question texts for context
        texts = []
        for q in retrieved_questions:
            q_data = q.get("question", {})
            if isinstance(q_data, dict):
                texts.append(q_data.get("question_text", ""))
            else:
                texts.append(str(q_data))
        context = "\n---\n".join(texts)

    generated_content = generate_references(context, enhanced_query)

    return {
        "source": "database" if retrieved_questions else "generated",
        "page": page,
        "query_info": {
            "original": query,
            "enhanced": enhanced_query,
            "variations": variations
        },
        "retrieved_questions": retrieved_questions,
        "generated_content": generated_content
    }
