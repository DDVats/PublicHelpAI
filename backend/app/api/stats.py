import json
from pathlib import Path
from fastapi import APIRouter
from backend.app.core.ml_engine import MLEngine

router = APIRouter()


@router.get("/stats")
async def get_stats():
    engine = MLEngine.get()
    engine.load()
    return engine.get_stats()


@router.get("/filters")
async def get_filters():
    """Return available filter options from actual dataset."""
    engine = MLEngine.get()
    engine.load()
    return {
        "states": engine.get_all_states(),
        "categories": engine.get_all_categories(),
        "levels": ["Central Government", "State / UT Government"],
    }


@router.get("/evaluation")
async def get_evaluation():
    """Return latest measured model evaluation metrics from disk."""
    eval_file = Path("reports/model_comparison.json")
    if eval_file.exists():
        with open(eval_file) as f:
            return json.load(f)
    return {
        "error": "Evaluation report not found. Run scripts/evaluate.py first.",
        "models": {}
    }


@router.get("/data-quality")
async def get_data_quality():
    """Return latest data quality report from disk."""
    dq_file = Path("reports/data_quality.json")
    if dq_file.exists():
        with open(dq_file) as f:
            return json.load(f)
    return {
        "error": "Data quality report not found. Run scripts/ingest_data.py first."
    }

