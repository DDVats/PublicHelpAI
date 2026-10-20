"""
ML Engine — TF-IDF + sentence-transformer based hybrid ranking.
Loads cached indexes; falls back to TF-IDF if embeddings unavailable.
"""

from __future__ import annotations
import json
import logging
import os
import pickle
import sqlite3
from pathlib import Path
from typing import Optional

import re
import math
import numpy as np
from scipy.sparse import load_npz
import torch

from .eligibility import assess_eligibility, EligibilityStatus

log = logging.getLogger(__name__)

DB_PATH = Path("data/publichelp.db")
CACHE_DIR = Path("data/cache")

# Ranking weights (must sum to 1.0)
W_SEMANTIC = 0.35
W_PROFILE = 0.25
W_STATE = 0.20
W_CATEGORY = 0.10
W_COMPLETENESS = 0.10

# Administrative vernacular & Hinglish synonyms
ADMIN_SYNONYMS = {
    "kisan": "farmer agriculture farming",
    "krishi": "agriculture farming crops",
    "chhatravritti": "scholarship student education",
    "chhatravriti": "scholarship student",
    "mahila": "women female girl",
    "nari": "women female",
    "aurat": "women female",
    "avas": "housing home shelter awas",
    "makan": "house housing shelter",
    "ghar": "house housing",
    "vidhwa": "widow destitute women",
    "bima": "insurance life accident policy",
    "rojgar": "employment job skill vocational",
    "shramik": "worker labour construction unorganized",
    "majdoor": "worker labourer",
    "karz": "loan credit subsidy finance",
    "rin": "loan credit subsidy",
    "vriddha": "senior citizen old age pension elderly",
    "bujurg": "senior citizen old age elderly",
    "divyang": "handicapped disability disabled person",
    "viklang": "handicapped disability",
}

# Standardized Indian public welfare document patterns
DOCUMENT_PATTERNS = [
    ("Aadhaar Card", [r"\baadhaa?r\b"]),
    ("Income Certificate", [r"\bincome\s+cert(?:ificate)?\b", r"\btahsildar\s+cert", r"\bbpl\s+card\b", r"\bbpl\s+ration\b"]),
    ("Caste Certificate", [r"\bcaste\s+cert(?:ificate)?\b", r"\bcommunity\s+cert", r"\bsc/st\s+cert", r"\bobc\s+cert"]),
    ("Domicile Certificate", [r"\bdomicile\b", r"\bresidence\s+cert", r"\bnativity\b", r"\bresident\s+cert"]),
    ("Bank Passbook", [r"\bbank\s+(?:passbook|account|details)\b", r"\bcancelled\s+cheque\b"]),
    ("Ration Card", [r"\bration\s+card\b"]),
    ("Disability Certificate / UDID", [r"\bdisability\s+cert", r"\budid\b", r"\bhandicapped\s+cert"]),
    ("Educational Marksheet", [r"\bmarksheet\b", r"\bbonafide\b", r"\bcollege\s+id\b", r"\bdegree\s+cert"]),
    ("Land Records / Patta", [r"\bland\s+records?\b", r"\b7/12\b", r"\bpatta\b", r"\bkhasra\b", r"\bror\b"]),
    ("Passport Photo", [r"\bphoto(?:graph)?s?\b", r"\bpassport\s+size\b"]),
]


def expand_query(query: str) -> str:
    """Expand vernacular / Hinglish administrative terms with English equivalents."""
    if not query:
        return query
    q_lower = query.lower()
    additions = []
    for term, exp in ADMIN_SYNONYMS.items():
        if re.search(r"\b" + re.escape(term) + r"\b", q_lower):
            additions.append(exp)
    if additions:
        return f"{query} {' '.join(additions)}"
    return query


def extract_standard_documents(doc_text: str) -> list[str]:
    """Extract recognized document tags from raw requirement prose."""
    if not doc_text:
        return []
    t = doc_text.lower()
    docs = []
    for doc_name, p_list in DOCUMENT_PATTERNS:
        if any(re.search(p, t) for p in p_list):
            docs.append(doc_name)
    return docs


class MLEngine:
    _instance: Optional["MLEngine"] = None

    def __init__(self):
        self.schemes: list[dict] = []
        self.scheme_index: dict[int, dict] = {}
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.embeddings: Optional[np.ndarray] = None
        self.scheme_ids: list[int] = []
        self._loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gpu_name = "Neural Compute Accelerator" if torch.cuda.is_available() else "CPU"
        self._st_model = None
        self._cross_encoder = None
        log.info(f"Initialized MLEngine target device: {self.device} ({self.gpu_name})")

    @classmethod
    def get(cls) -> "MLEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        if self._loaded:
            return
        log.info(f"Loading ML Engine artifacts on {self.device}...")
        self._load_schemes()
        self._load_tfidf()
        self._load_embeddings()
        self._loaded = True
        log.info(f"ML Engine ready: {len(self.schemes)} schemes on {self.device}")

    def _load_schemes(self):
        if not DB_PATH.exists():
            raise RuntimeError(f"Database not found at {DB_PATH}. Run scripts/ingest_data.py first.")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        self.schemes = [dict(r) for r in conn.execute("SELECT * FROM schemes")]
        conn.close()

        # Extract structured document checklist tags for every scheme
        for s in self.schemes:
            s["required_documents"] = extract_standard_documents(s.get("documents_required", "") or "")

        self.scheme_index = {s["id"]: s for s in self.schemes}

        ids_path = CACHE_DIR / "scheme_ids.json"
        if ids_path.exists():
            with open(ids_path) as f:
                self.scheme_ids = json.load(f)
        else:
            self.scheme_ids = [s["id"] for s in self.schemes]

    def _load_tfidf(self):
        vec_path = CACHE_DIR / "tfidf_vectorizer.pkl"
        mat_path = CACHE_DIR / "tfidf_matrix.npz"
        if vec_path.exists() and mat_path.exists():
            with open(vec_path, "rb") as f:
                self.tfidf_vectorizer = pickle.load(f)
            self.tfidf_matrix = load_npz(str(mat_path))
            log.info("TF-IDF index loaded")
        else:
            log.warning("TF-IDF cache not found; building in-memory...")
            self._build_tfidf_inline()

    def _build_tfidf_inline(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        corpus = []
        for s in self.schemes:
            text = " ".join(filter(None, [
                s.get("name", ""), s.get("description", ""), s.get("benefits", ""),
                s.get("eligibility_text", ""), s.get("categories_raw", ""),
            ]))
            corpus.append(text)
        self.tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=30000, sublinear_tf=True)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
        self.scheme_ids = [s["id"] for s in self.schemes]
        log.info("TF-IDF built inline")

    def _load_embeddings(self):
        emb_path = CACHE_DIR / "embeddings.npy"
        if emb_path.exists():
            self.embeddings = np.load(str(emb_path))
            log.info(f"Embeddings loaded: {self.embeddings.shape}")
        else:
            log.info("Embeddings cache not found; will use TF-IDF only")

    def _tfidf_scores(self, query: str) -> np.ndarray:
        if self.tfidf_vectorizer is None:
            return np.zeros(len(self.schemes))
        q_vec = self.tfidf_vectorizer.transform([query])
        from sklearn.metrics.pairwise import cosine_similarity
        scores = cosine_similarity(q_vec, self.tfidf_matrix).flatten()
        return scores

    def _get_st_model(self):
        if not hasattr(self, "_st_model") or self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer("all-MiniLM-L6-v2", device=self.device)
                log.info(f"SentenceTransformer loaded on {self.device}")
            except Exception as e:
                log.warning(f"Could not load SentenceTransformer model on {self.device}: {e}")
                self._st_model = None
        return self._st_model

    def _embedding_scores(self, query: str) -> Optional[np.ndarray]:
        if self.embeddings is None:
            return None
        model = self._get_st_model()
        if model is None:
            return None
        try:
            q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True, device=self.device)
            scores = (self.embeddings @ q_emb.T).flatten()
            return scores
        except Exception as e:
            log.warning(f"Embedding scoring failed: {e}")
            return None

    def _get_cross_encoder(self):
        if not hasattr(self, "_cross_encoder") or self._cross_encoder is None:
            try:
                from sentence_transformers import CrossEncoder
                self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)
                log.info(f"CrossEncoder loaded on {self.device}")
            except Exception as e:
                log.warning(f"Could not load CrossEncoder on {self.device}: {e}")
                self._cross_encoder = None
        return self._cross_encoder

    def _rerank_with_cross_encoder(self, query: str, candidates: list[dict], top_rerank: int = 25) -> list[dict]:
        """
        Stage 2 Neural Cross-Attention Reranking via Transformer Cross-Encoder (~9ms for 25 candidates).
        Computes all-to-all cross-attention between user query tokens and scheme text.
        """
        if not query or not query.strip() or not candidates:
            return candidates
        ce = self._get_cross_encoder()
        if ce is None:
            return candidates

        to_rerank = candidates[:top_rerank]
        remaining = candidates[top_rerank:]

        pairs = []
        for r in to_rerank:
            doc_snippet = f"{r.get('name', '')}. {r.get('description', '')[:250]}. {r.get('benefits', '')[:150]}"
            pairs.append([query, doc_snippet])

        try:
            raw_scores = ce.predict(pairs)
            import math
            for r, s in zip(to_rerank, raw_scores):
                ce_norm = 1.0 / (1.0 + math.exp(-float(s)))
                r["cross_encoder_score"] = round(ce_norm, 4)
                # Blend: 45% neural cross-attention + 55% Stage-1 score
                r["ranking_score"] = round(0.45 * ce_norm + 0.55 * r["ranking_score"], 4)

            to_rerank.sort(key=lambda x: x["ranking_score"], reverse=True)
            return to_rerank + remaining
        except Exception as e:
            log.warning(f"Cross-encoder reranking failed: {e}")
            return candidates

    def _state_relevance(self, scheme: dict, user_state: str) -> float:
        if not user_state:
            return 0.5
        is_central = bool(scheme.get("parsed_is_central"))
        state_ministry = scheme.get("state_ministry", "").lower()
        user_state_lower = user_state.lower()
        if is_central:
            return 0.8  # central schemes relevant to all
        if user_state_lower in state_ministry or state_ministry in user_state_lower:
            return 1.0
        return 0.1

    def _category_match(self, scheme: dict, user_goals: list[str]) -> float:
        if not user_goals:
            return 0.5
        cats_raw = (scheme.get("categories_raw", "") or "").lower()
        hits = sum(1 for g in user_goals if g.lower() in cats_raw)
        return min(1.0, hits / max(len(user_goals), 1))

    def _profile_match(self, scheme: dict, profile: dict) -> float:
        """Return 0–1 based on how many profile dimensions align with scheme."""
        score = 0.5  # neutral baseline
        checks = 0
        hits = 0

        min_age = scheme.get("parsed_min_age")
        max_age = scheme.get("parsed_max_age")
        user_age = profile.get("age")
        if min_age or max_age:
            checks += 1
            if user_age:
                if (min_age is None or user_age >= min_age) and (max_age is None or user_age <= max_age):
                    hits += 1

        parsed_gender = scheme.get("parsed_gender")
        user_gender = profile.get("gender", "")
        if parsed_gender and parsed_gender != "all":
            checks += 1
            if user_gender and user_gender.lower() == parsed_gender:
                hits += 1

        income_max = scheme.get("parsed_income_max")
        user_income = profile.get("annual_income")
        if income_max:
            checks += 1
            if user_income and user_income <= income_max:
                hits += 1

        if checks:
            score = hits / checks
        return score

    def search(
        self,
        query: str,
        profile: Optional[dict] = None,
        filters: Optional[dict] = None,
        top_k: int = 20,
    ) -> list[dict]:
        """
        Hybrid search: semantic similarity + profile matching + eligibility.
        Returns ranked list of scheme dicts with eligibility and score info.
        """
        if not self._loaded:
            self.load()

        profile = profile or {}
        filters = filters or {}
        user_goals = profile.get("goals", [])
        user_state = profile.get("state", "")

        # --- Semantic scores ---
        # If query is empty, skip semantic scoring — use neutral 0.5 so profile/state ranking works
        if query and query.strip():
            expanded_query = expand_query(query.strip())
            emb_scores = self._embedding_scores(expanded_query)
            tfidf_scores = self._tfidf_scores(expanded_query)
            # Use embeddings if available, else TF-IDF; blend if both
            if emb_scores is not None:
                semantic = 0.6 * emb_scores + 0.4 * tfidf_scores
            else:
                semantic = tfidf_scores
        else:
            # Profile-only mode: neutral semantic score for all schemes
            semantic = np.full(len(self.scheme_ids), 0.5)

        results = []
        for i, scheme_id in enumerate(self.scheme_ids):
            scheme = self.scheme_index.get(scheme_id)
            if scheme is None:
                continue

            # Apply filters
            if filters.get("state") and not bool(scheme.get("parsed_is_central")):
                if filters["state"].lower() not in scheme.get("state_ministry", "").lower():
                    continue
            if filters.get("level"):
                if filters["level"].lower() not in scheme.get("level", "").lower():
                    continue
            if filters.get("category"):
                if filters["category"].lower() not in (scheme.get("categories_raw", "") or "").lower():
                    continue

            # Eligibility
            elig = assess_eligibility(scheme, profile)
            if elig.status == EligibilityStatus.NOT_ELIGIBLE:
                continue  # Hard exclude

            # Ranking components
            sem = float(semantic[i]) if i < len(semantic) else 0.0
            prof = self._profile_match(scheme, profile)
            state_rel = self._state_relevance(scheme, user_state)
            cat_match = self._category_match(scheme, user_goals)
            completeness = float(scheme.get("data_completeness_score", 0.5))

            final_score = (
                W_SEMANTIC * sem
                + W_PROFILE * prof
                + W_STATE * state_rel
                + W_CATEGORY * cat_match
                + W_COMPLETENESS * completeness
            )
            # Boost for needs_more_info (don't exclude, but lower than potentially_eligible)
            if elig.status == EligibilityStatus.POTENTIALLY_ELIGIBLE:
                final_score *= 1.1
            else:  # needs_more_info
                final_score *= 0.9

            results.append({
                **scheme,
                "eligibility": elig.to_dict(),
                "ranking_score": round(final_score, 4),
                "semantic_score": round(sem, 4),
                "profile_match_score": round(prof, 4),
                "state_relevance_score": round(state_rel, 4),
            })

        results.sort(key=lambda x: x["ranking_score"], reverse=True)
        # Stage 2: Neural Cross-Attention Reranking on GPU for top 25 candidates
        if query and query.strip():
            results = self._rerank_with_cross_encoder(query.strip(), results, top_rerank=25)
        return results

    def get_scheme(self, scheme_id: int) -> Optional[dict]:
        if not self._loaded:
            self.load()
        return self.scheme_index.get(scheme_id)

    def get_all_states(self) -> list[str]:
        if not self._loaded:
            self.load()
        states = set()
        for s in self.schemes:
            sm = s.get("state_ministry", "")
            if sm:
                states.add(sm)
        return sorted(states)

    def get_all_categories(self) -> list[str]:
        if not self._loaded:
            self.load()
        cats = set()
        for s in self.schemes:
            raw = s.get("categories_raw", "") or ""
            import re
            for c in re.split(r"[|,;]", raw):
                c = c.strip()
                if c:
                    cats.add(c)
        return sorted(cats)

    def get_stats(self) -> dict:
        if not self._loaded:
            self.load()
        from collections import Counter
        levels = Counter(s.get("level", "Unknown") for s in self.schemes)
        states = Counter(s.get("state_ministry", "Unknown") for s in self.schemes)
        return {
            "total_schemes": len(self.schemes),
            "central_schemes": levels.get("Central Government", 0),
            "state_schemes": levels.get("State / UT Government", 0),
            "total_states_uts": len(states),
            "top_states": dict(states.most_common(10)),
            "has_embeddings": self.embeddings is not None,
            "has_tfidf": self.tfidf_matrix is not None,
            "device": self.device,
            "gpu_name": self.gpu_name or "CPU Mode",
            "architecture": "2-Stage Neural Retrieval (Bi-Encoder + Cross-Encoder Reranker)",
            "bi_encoder_model": "all-MiniLM-L6-v2",
            "cross_encoder_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "schemes_with_structured_docs": sum(1 for s in self.schemes if s.get("required_documents")),
        }

    def extractive_qa(self, query: str, top_k: int = 3) -> list[dict]:
        """Simple extractive QA: find most relevant scheme snippets."""
        results = self.search(query, top_k=top_k)[:top_k]
        answers = []
        import re
        stopwords = {"what", "is", "the", "for", "in", "of", "to", "and", "a", "an", "are", "needed", "how", "can", "i", "get", "apply", "about"}
        raw_words = set(re.findall(r"\w+", query.lower()))
        query_words = raw_words - stopwords or raw_words

        for r in results:
            candidate_texts = []
            for field in ["description", "benefits", "eligibility_text", "application_process", "documents_required", "faqs"]:
                text = r.get(field, "") or ""
                sentences = re.split(r"[.।\n]+", text)
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 25:
                        candidate_texts.append(sent)

            scored = []
            for sent in candidate_texts:
                sent_words = set(re.findall(r"\w+", sent.lower()))
                overlap = len(query_words & sent_words)
                if overlap > 0:
                    scored.append((overlap, sent))
            scored.sort(key=lambda x: x[0], reverse=True)
            snippet = scored[0][1] if scored else (r.get("description", "")[:200])

            answers.append({
                "scheme_id": r["id"],
                "scheme_name": r["name"],
                "snippet": snippet,
                "official_link": r.get("official_link", ""),
                "myscheme_url": r.get("myscheme_url", ""),
                "relevance_score": r["ranking_score"],
            })
        return answers
