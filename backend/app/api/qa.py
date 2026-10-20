"""Grounded extractive QA endpoint."""
from fastapi import APIRouter
from backend.app.core.ml_engine import MLEngine
from backend.app.models.schemas import QARequest

router = APIRouter()


@router.post("/qa")
async def question_answer(req: QARequest):
    engine = MLEngine.get()
    engine.load()
    answers = engine.extractive_qa(req.query, top_k=3)
    return {
        "query": req.query,
        "answers": answers,
        "note": (
            "Answers are extracted from the scheme dataset. "
            "Always verify with the official source link before taking action. "
            "PublicHelp AI is not an official government service."
        ),
    }
