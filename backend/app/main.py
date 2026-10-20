"""
FastAPI application entry point for PublicHelp AI backend.
"""
from __future__ import annotations
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.api import schemes, recommend, qa, stats, saved, compare, health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("publichelp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML engine on startup
    from backend.app.core.ml_engine import MLEngine
    log.info("Starting PublicHelp AI backend...")
    start = time.time()
    engine = MLEngine.get()
    try:
        engine.load()
        log.info(f"ML Engine loaded in {time.time()-start:.2f}s")
    except Exception as e:
        log.error(f"ML Engine load failed: {e}. Some endpoints will be unavailable.")
    yield
    log.info("PublicHelp AI backend shutting down.")


app = FastAPI(
    title="PublicHelp AI — Government Scheme Navigator API",
    description=(
        "Explainable, hybrid recommendation API for Indian government schemes. "
        "This is an independent informational tool, NOT an official government service."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(schemes.router, prefix="/api", tags=["schemes"])
app.include_router(recommend.router, prefix="/api", tags=["recommend"])
app.include_router(qa.router, prefix="/api", tags=["qa"])
app.include_router(saved.router, prefix="/api", tags=["saved"])
app.include_router(compare.router, prefix="/api", tags=["compare"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
