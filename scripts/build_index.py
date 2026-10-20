#!/usr/bin/env python3
"""
Build search index for PublicHelp AI.
Generates TF-IDF and sentence-transformer embeddings, caches them to disk.

Usage:
    python scripts/build_index.py [--no-transformers]
"""

import argparse
import json
import logging
import pickle
import sqlite3
import sys
from pathlib import Path

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("logs/build_index.log"), logging.StreamHandler()],
)
log = logging.getLogger("build_index")

DB_PATH = Path("data/publichelp.db")
CACHE_DIR = Path("data/cache")


def load_schemes(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM schemes").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def build_tfidf_index(schemes: list[dict]):
    from sklearn.feature_extraction.text import TfidfVectorizer

    corpus = []
    for s in schemes:
        text = " ".join(filter(None, [
            s.get("name", ""),
            s.get("description", ""),
            s.get("benefits", ""),
            s.get("eligibility_text", ""),
            s.get("categories_raw", ""),
            s.get("state_ministry", ""),
        ]))
        corpus.append(text)

    log.info(f"Building TF-IDF index over {len(corpus)} documents...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=50000,
        sublinear_tf=True,
        strip_accents="unicode",
    )
    matrix = vectorizer.fit_transform(corpus)
    log.info(f"TF-IDF matrix shape: {matrix.shape}")
    return vectorizer, matrix


def build_embedding_index(schemes: list[dict], batch_size: int = 64):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        log.warning("sentence-transformers not installed; skipping embedding index")
        return None

    log.info("Loading all-MiniLM-L6-v2 (downloads ~90MB on first run)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    corpus = []
    for s in schemes:
        text = f"{s.get('name','')}. {s.get('description','')} {s.get('benefits','')}"
        corpus.append(text[:512])  # token budget

    log.info(f"Encoding {len(corpus)} schemes with sentence-transformers...")
    embeddings = model.encode(
        corpus,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        device="cpu",  # always CPU to avoid VRAM issues
        normalize_embeddings=True,
    )
    log.info(f"Embeddings shape: {embeddings.shape}")
    return embeddings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-transformers", action="store_true",
                        help="Skip sentence-transformer embedding (faster, TF-IDF only)")
    args = parser.parse_args()

    Path("logs").mkdir(exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists():
        log.error(f"Database not found at {DB_PATH}. Run scripts/ingest_data.py first.")
        sys.exit(1)

    schemes = load_schemes(DB_PATH)
    log.info(f"Loaded {len(schemes)} schemes from DB")

    # TF-IDF
    vectorizer, tfidf_matrix = build_tfidf_index(schemes)
    with open(CACHE_DIR / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    # save as dense numpy for compatibility; for large sets keep sparse
    from scipy.sparse import save_npz
    save_npz(str(CACHE_DIR / "tfidf_matrix.npz"), tfidf_matrix)
    log.info("TF-IDF index saved")

    # Save scheme IDs order (must match matrix rows)
    scheme_ids = [s["id"] for s in schemes]
    with open(CACHE_DIR / "scheme_ids.json", "w") as f:
        json.dump(scheme_ids, f)

    # Embeddings
    if not args.no_transformers:
        embeddings = build_embedding_index(schemes)
        if embeddings is not None:
            np.save(str(CACHE_DIR / "embeddings.npy"), embeddings)
            log.info("Sentence-transformer embeddings saved")
    else:
        log.info("Skipping sentence-transformer embeddings (--no-transformers)")

    log.info("Index build complete.")


if __name__ == "__main__":
    main()
