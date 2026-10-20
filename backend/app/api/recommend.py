"""Recommendation endpoint — hybrid ranking with eligibility."""
from fastapi import APIRouter
from backend.app.core.ml_engine import MLEngine
from backend.app.models.schemas import RecommendRequest

router = APIRouter()
PAGE_SIZE = 10


@router.post("/recommend")
async def recommend(req: RecommendRequest):
    engine = MLEngine.get()
    engine.load()

    profile = req.profile.model_dump(exclude_none=True) if req.profile else {}
    filters = req.filters.model_dump(exclude_none=True) if req.filters else {}

    # Use empty string for profile-only mode
    query = req.query.strip() if req.query else ""

    # Get ALL matching results (engine handles eligibility filtering & ranking)
    all_results = engine.search(
        query=query,
        profile=profile,
        filters=filters,
        top_k=9999,  # no limit — paginate on our side
    )

    total = len(all_results)
    start = (req.page - 1) * req.top_k
    end = start + req.top_k
    page_results = all_results[start:end]

    stats = engine.get_stats()
    mode = "Profile-based ranking" if not query else (
        "2-Stage Neural Retrieval: all-MiniLM-L6-v2 + Cross-Encoder Reranker"
        if stats["has_embeddings"] else "TF-IDF"
    )
    return {
        "total": total,
        "page": req.page,
        "page_size": req.top_k,
        "query": query,
        "results": page_results,
        "has_embeddings": stats["has_embeddings"],
        "model_used": mode,
    }
