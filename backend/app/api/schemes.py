"""Scheme browse/detail endpoints."""
import json
from fastapi import APIRouter, HTTPException, Query
from backend.app.core.ml_engine import MLEngine

router = APIRouter()


@router.get("/schemes")
async def list_schemes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str = Query(None),
    level: str = Query(None),
    category: str = Query(None),
):
    engine = MLEngine.get()
    engine.load()
    schemes = engine.schemes

    if state:
        schemes = [s for s in schemes if state.lower() in s.get("state_ministry", "").lower()
                   or bool(s.get("parsed_is_central"))]
    if level:
        schemes = [s for s in schemes if level.lower() in s.get("level", "").lower()]
    if category:
        schemes = [s for s in schemes if category.lower() in (s.get("categories_raw", "") or "").lower()]

    total = len(schemes)
    start = (page - 1) * page_size
    end = start + page_size
    page_schemes = schemes[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": page_schemes,
    }


@router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: int):
    engine = MLEngine.get()
    engine.load()
    scheme = engine.get_scheme(scheme_id)
    if scheme is None:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_id} not found")
    # Parse categories_list from JSON string
    try:
        scheme["categories_list"] = json.loads(scheme.get("categories_list", "[]"))
    except Exception:
        scheme["categories_list"] = []
    return scheme


@router.get("/schemes/slug/{slug}")
async def get_scheme_by_slug(slug: str):
    engine = MLEngine.get()
    engine.load()
    for s in engine.schemes:
        if s.get("slug", "") == slug:
            try:
                s["categories_list"] = json.loads(s.get("categories_list", "[]"))
            except Exception:
                s["categories_list"] = []
            return s
    raise HTTPException(status_code=404, detail=f"Scheme with slug '{slug}' not found")
