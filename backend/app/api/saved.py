"""Saved schemes — session-based, in-memory (no PII stored)."""
from fastapi import APIRouter, HTTPException
from backend.app.core.ml_engine import MLEngine

router = APIRouter()

# In-memory store keyed by session_id. Not persisted on restart by design.
_saved: dict[str, set[int]] = {}


@router.post("/saved/{session_id}/{scheme_id}")
async def save_scheme(session_id: str, scheme_id: int):
    engine = MLEngine.get()
    engine.load()
    if engine.get_scheme(scheme_id) is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    _saved.setdefault(session_id, set()).add(scheme_id)
    return {"saved": True, "scheme_id": scheme_id}


@router.delete("/saved/{session_id}/{scheme_id}")
async def remove_scheme(session_id: str, scheme_id: int):
    _saved.get(session_id, set()).discard(scheme_id)
    return {"removed": True, "scheme_id": scheme_id}


@router.get("/saved/{session_id}")
async def get_saved(session_id: str):
    engine = MLEngine.get()
    engine.load()
    ids = _saved.get(session_id, set())
    schemes = [engine.get_scheme(i) for i in ids if engine.get_scheme(i)]
    return {"count": len(schemes), "schemes": schemes}
