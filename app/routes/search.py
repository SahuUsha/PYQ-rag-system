from fastapi import APIRouter
from app.services.embedding import generate_embedding
from app.services.qdrant_service import search_vector
from app.services.db_service import get_questions_by_ids
from app.services.groq_service import generate_references
from app.services.query_expansion_service import expand_query

router = APIRouter()


# ✅ CENTRAL TEXT EXTRACTION
def extract_text(q):
    data = q.get("question", {})
    main = data.get("question_text", "")
    if main:
        return main
    return " ".join([sq.get("text", "") for sq in data.get("subquestions", [])])


# ✅ IMPROVED KEYWORD SCORE
def keyword_score(q_text, query):
    q_text = q_text.lower()
    words = query.lower().split()
    score = 0
    for w in words:
        if w in q_text:
            score += 1
        elif any(w in t or t in w for t in q_text.split()):
            score += 0.7
    return score


# ✅ DIRECT MATCH BOOST
def direct_keyword_boost(q_text, query):
    if query.lower() in q_text.lower():
        return 2.0
    return 0


# ✅ SEMANTIC BOOST
def semantic_boost(q_text, query):
    q_text = q_text.lower()
    query_words = query.lower().split()
    match_count = sum(1 for w in query_words if w in q_text)
    return match_count * 0.2


@router.get("/search")
def search(query: str, page: int = 1, limit: int = 25):

    print("Original Query:", query)

    # 🔥 Normalize
    query = query.replace(",", " ").strip()

    # 1️⃣ Query Expansion
    try:
        expanded = expand_query(query)
        all_queries = expanded.get("all_queries", [query])
        query = expanded.get("main_query", query)
        all_queries = list(dict.fromkeys([q.lower().strip() for q in all_queries]))[:6]
        print("Expanded Queries:", all_queries)
    except Exception as e:
        print("Expansion failed:", e)
        all_queries = [query]

    # 2️⃣ VECTOR SEARCH
    score_map = {}
    search_depth = 200
    for i, q in enumerate(all_queries):
        weight = 1.0 if i == 0 else 0.85 if i == 1 else 0.7
        try:
            emb = generate_embedding(q)
            results = search_vector(emb, limit=search_depth)
        except Exception as e:
            print("Vector search failed:", e)
            continue

        for qid, score in results:
            weighted_score = score * weight
            score_map[qid] = score_map.get(qid, 0) + weighted_score

    print("Total candidates from vector:", len(score_map))
    if not score_map:
        return {"source": "none", "retrieved_questions": [], "generated_content": "No relevant questions found"}

    # 3️⃣ SORT IDS
    ranked_ids = sorted(score_map, key=score_map.get, reverse=True)

    # 4️⃣ FETCH FROM DB
    retrieved_questions = get_questions_by_ids(ranked_ids)
    print("Total DB fetched:", len(retrieved_questions))

    # 5️⃣ HYBRID RANKING
    reranked = []
    for q in retrieved_questions:
        q_text = extract_text(q)
        if not q_text:
            continue
        vector_score = score_map.get(q["id"], 0)
        kw_score = keyword_score(q_text, query)
        semantic = semantic_boost(q_text, query)
        boost = direct_keyword_boost(q_text, query)
        final_score = 0.7 * vector_score + 0.2 * kw_score + 0.05 * semantic + 0.5 * boost
        reranked.append({
            "question": q,
            "final_score": final_score,
            "vector_score": vector_score,
            "keyword_score": kw_score,
            "semantic_score": semantic,
            "boost": boost
            })

    reranked.sort(key=lambda x: x["final_score"], reverse=True)

    # 6️⃣ SEPARATE HIGHLY RELATED QUESTIONS
    related = []
    others = []
    seen_ids = set()
    for item in reranked:
        q = item["question"]
        score = item["final_score"]
        q_text = extract_text(q)
        if query.lower() in q_text.lower():
            related.append(q)
        else:
            others.append(q)
        seen_ids.add(q["id"])


    print("Other questions:", len(others))

    # 7️⃣ COMBINE SEQUENTIALLY (related first)
    combined = related + others

    # 8️⃣ APPLY LIMIT
    final_questions = combined[:limit]

    print("Final results:", len(final_questions))

    # 9️⃣ CONTEXT BUILD
    context = "\n---\n".join([extract_text(q) for q in final_questions])

    # 🔟 GENERATE ANSWER
    generated_content = generate_references(context, query)

    print("\nTop Results with Scores:")
    for item in reranked[:10]:
        print({
            "id": item["question"]["id"],
            "final": item["final_score"],
            "vector": item["vector_score"],
            "keyword": item["keyword_score"],
            "semantic": item["semantic_score"],
            "boost": item["boost"]
        })

    return {
        "source": "database",
        "query": query,
        "retrieved_questions": final_questions,
        "generated_content": generated_content
    }