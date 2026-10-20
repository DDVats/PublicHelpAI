"""Comparison endpoint — side-by-side scheme comparison with optional eligibility."""
import json
from fastapi import APIRouter, HTTPException
from backend.app.core.ml_engine import MLEngine
from backend.app.core.eligibility import assess_eligibility
from backend.app.models.schemas import CompareRequest

router = APIRouter()


@router.post("/compare")
async def compare_schemes(req: CompareRequest):
    engine = MLEngine.get()
    engine.load()

    profile = req.profile.model_dump(exclude_none=True) if req.profile else {}
    schemes = []
    for sid in req.scheme_ids:
        s = engine.get_scheme(sid)
        if s is None:
            raise HTTPException(status_code=404, detail=f"Scheme {sid} not found")
        try:
            s["categories_list"] = json.loads(s.get("categories_list", "[]"))
        except Exception:
            s["categories_list"] = []
        s["eligibility"] = assess_eligibility(s, profile).to_dict()
        schemes.append(s)

    return {"schemes": schemes, "profile_used": bool(profile)}
