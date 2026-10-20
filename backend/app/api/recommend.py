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
        "Hybrid Reciprocal Rank Fusion (RRF: all-MiniLM-L6-v2 + TF-IDF) + MMR Diversity"
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


@router.post("/recommend/feed")
async def recommend_feed(req: dict = None):
    engine = MLEngine.get()
    engine.load()
    req = req or {}
    raw_profile = req.get("profile") or {}
    saved_ids = req.get("saved_ids") or []
    top_k = req.get("top_k", 8)

    feed = engine.get_recommended_feed(profile=raw_profile, saved_ids=saved_ids, top_k=top_k)
    return feed


@router.get("/recommend/bundles")
async def get_bundles(state: str = None, gender: str = None, age: int = None):
    engine = MLEngine.get()
    engine.load()
    profile = {}
    if state: profile["state"] = state
    if gender: profile["gender"] = gender
    if age: profile["age"] = age

    bundles = engine.get_complementary_bundles(profile=profile)
    return {"bundles": bundles}


@router.get("/recommend/personas")
async def get_personas():
    engine = MLEngine.get()
    engine.load()
    return {"personas": engine.get_personas()}

