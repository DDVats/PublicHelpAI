"""
ML Engine — Hybrid Reciprocal Rank Fusion (RRF), Dense Embedding & Profile-Based Recommender.
Features:
- Deterministic constraint satisfaction (Eligibility)
- Lexical retrieval (TF-IDF) + Dense retrieval (sentence-transformers/all-MiniLM-L6-v2)
- Reciprocal Rank Fusion (RRF) candidate merging (k=60)
- Multi-objective personalized ranking with documented configuration
- Maximal Marginal Relevance (MMR) candidate diversity re-ranking
- Content-based item-to-item nearest-neighbor recommendations
- Complementary benefit bundles (e.g. Farmer Package, Girl Student Pathway, Senior Net)
- Grounded extractive question answering
"""

from __future__ import annotations
import json
import logging
import os
import pickle
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any

import re
import math
import numpy as np
from scipy.sparse import load_npz
import torch

from .eligibility import assess_eligibility, EligibilityStatus

log = logging.getLogger(__name__)

DB_PATH = Path("data/publichelp.db")
CACHE_DIR = Path("data/cache")


@dataclass
class RankingConfig:
    """Documented configuration weights for the Recommender Pipeline."""
    # When query is provided: 35% search intent + 65% personalized profile composite
    w_query: float = 0.35
    w_profile_composite: float = 0.65

    # Sub-weights for profile composite (sum to 1.0)
    w_profile_fit: float = 0.40      # Demographic criteria (age, gender, income, caste)
    w_state_relevance: float = 0.30  # State domicile / Central authority
    w_category_overlap: float = 0.15 # User goals vs scheme categories
    w_data_evidence: float = 0.15    # Completeness of criteria & required documentation

    # Reciprocal Rank Fusion constant (Cormack et al. 2009)
    rrf_k: int = 60

    # Diversity re-ranking (Maximal Marginal Relevance)
    enable_diversity_mmr: bool = True
    mmr_lambda: float = 0.85

    # Cross-encoder re-ranking (optional, evaluated option)
    enable_cross_encoder: bool = False
    cross_encoder_top_n: int = 20


# Administrative vernacular & Hinglish synonyms
ADMIN_SYNONYMS = {
    "kisan": "farmer agriculture farming crops",
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

CURATED_BUNDLES_DATA = [
    {
        "bundle_id": "farmer_welfare",
        "title": "Kisan Samriddhi & Protection Package",
        "description": "Comprehensive agricultural safety net combining direct cash assistance, institutional credit, and solar/farm asset subsidies.",
        "target_persona": "Farmers, cultivators, and agricultural workers",
        "icon": "Tractor",
        "schemes": [
            {
                "id": 1421,
                "benefit_role": "Direct Income Support",
                "rationale": "Provides ₹6,000 annual direct cash transfer in 3 installments directly credited to bank account.",
            },
            {
                "id": 919,
                "benefit_role": "Institutional Credit",
                "rationale": "Concessional crop credit up to ₹3 Lakhs at subsidized 4% interest rate with prompt repayment.",
            },
            {
                "id": 1422,
                "benefit_role": "Energy & Solar Irrigation",
                "rationale": "Capital subsidy for standalone solar agriculture pumps to eliminate diesel irrigation costs.",
            },
            {
                "id": 57,
                "benefit_role": "Farm Infrastructure",
                "rationale": "Subsidized debt financing for post-harvest management infrastructure and community farming assets.",
            },
        ],
    },
    {
        "bundle_id": "women_girl_empowerment",
        "title": "Girl Child & Women Empowerment Pathway",
        "description": "Integrated social security, higher education scholarship, and long-term asset building for girls and women.",
        "target_persona": "Female students, daughters, and women seeking higher education",
        "icon": "GraduationCap",
        "schemes": [
            {
                "id": 1870,
                "benefit_role": "Long-term Asset Building",
                "rationale": "Government-backed savings scheme for girl child with sovereign guarantee, high interest, and full tax exemption.",
            },
            {
                "id": 1512,
                "benefit_role": "Technical Higher Education",
                "rationale": "₹50,000 annual scholarship for girls entering AICTE-approved technical degree programs.",
            },
            {
                "id": 1181,
                "benefit_role": "Merit Scholarship",
                "rationale": "Scholarship awarded to single girl children who cleared CBSE Class X exam with distinction.",
            },
            {
                "id": 1403,
                "benefit_role": "Postgraduate Education",
                "rationale": "Direct fellowship supporting single girl children pursuing higher education at university level.",
            },
        ],
    },
    {
        "bundle_id": "senior_citizen_security",
        "title": "Senior Citizen Social Security & Welfare Net",
        "description": "Welfare net designed for elderly citizens combining guaranteed pension and essential medical safety nets.",
        "target_persona": "Citizens aged 60 and above, pensioners, and senior citizens",
        "icon": "HeartHandshake",
        "schemes": [
            {
                "id": 109,
                "benefit_role": "Guaranteed Monthly Pension",
                "rationale": "Government guaranteed monthly pension scheme ensuring regular income security in old age.",
            },
            {
                "id": 38,
                "benefit_role": "Medical & Critical Illness Grant",
                "rationale": "Financial assistance for medical treatment of serious diseases for eligible non-pensioners/widows.",
            },
            {
                "id": 1420,
                "benefit_role": "Food Security & Ration",
                "rationale": "Free monthly foodgrain allotment ensuring nutritional security under the National Food Security safety net.",
            },
        ],
    },
    {
        "bundle_id": "student_youth_pathway",
        "title": "Youth Higher Education & Skill Development",
        "description": "Coordinated civic pathway assisting students through secondary schooling, college graduation, and technical skilling.",
        "target_persona": "Undergraduate youth, college students, and young job-seekers",
        "icon": "BookOpen",
        "schemes": [
            {
                "id": 56,
                "benefit_role": "Higher Education Support",
                "rationale": "AICTE technical scholarship supporting higher education tuition and living allowance.",
            },
            {
                "id": 1419,
                "benefit_role": "Skill Development & Placement",
                "rationale": "Free vocational skill training, certification, and stipend support for youth employment.",
            },
            {
                "id": 178,
                "benefit_role": "Residential & Hostel Support",
                "rationale": "Hostel facility and educational infrastructure support for undergraduate college students.",
            },
        ],
    },
]

DEMO_PERSONAS = [
    {
        "persona_id": "maya_student",
        "name": "Maya Sharma",
        "tagline": "19yo SC Female Student · Uttar Pradesh",
        "avatar": "👩‍🎓",
        "description": "Undergraduate engineering student from an SC background in UP seeking higher education scholarships and digital study support.",
        "profile": {
            "state": "Uttar Pradesh",
            "age": 19,
            "gender": "female",
            "caste_category": "SC",
            "annual_income": 150000,
            "education": "College / University",
            "occupation": "Student",
            "is_rural": False,
            "goals": ["Education", "Scholarships", "Skill Development"],
        },
    },
    {
        "persona_id": "ramesh_farmer",
        "name": "Ramesh Patel",
        "tagline": "44yo Marginal Farmer · Madhya Pradesh",
        "avatar": "👨‍🌾",
        "description": "Smallholder cultivator in rural MP seeking direct income support, subsidized crop credit, and solar irrigation subsidies.",
        "profile": {
            "state": "Madhya Pradesh",
            "age": 44,
            "gender": "male",
            "caste_category": "OBC",
            "annual_income": 95000,
            "occupation": "Farmer",
            "is_rural": True,
            "goals": ["Agriculture", "Credit", "Insurance"],
        },
    },
    {
        "persona_id": "lakshmi_senior",
        "name": "Lakshmi Ammal",
        "tagline": "65yo Widow Pensioner · Tamil Nadu",
        "avatar": "👵",
        "description": "Elderly widow living in Tamil Nadu with low household income seeking old-age social security pension, medical assistance, and food rations.",
        "profile": {
            "state": "Tamil Nadu",
            "age": 65,
            "gender": "female",
            "caste_category": "General",
            "annual_income": 40000,
            "occupation": "Retired",
            "is_rural": False,
            "goals": ["Social Security", "Healthcare", "Pension"],
        },
    },
    {
        "persona_id": "anita_artisan",
        "name": "Anita Devi",
        "tagline": "32yo Rural Artisan · Bihar",
        "avatar": "🧵",
        "description": "Self-employed rural handicraft artisan in Bihar seeking housing support, rural enterprise loans, and women welfare benefits.",
        "profile": {
            "state": "Bihar",
            "age": 32,
            "gender": "female",
            "caste_category": "EWS",
            "annual_income": 110000,
            "occupation": "Artisan / Self-employed",
            "is_rural": True,
            "goals": ["Housing", "Livelihood", "Women Welfare"],
        },
    },
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
        self.gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU Mode"
        self._st_model = None
        self._cross_encoder = None
        self.config = RankingConfig()
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
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
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

    def _rerank_with_cross_encoder(self, query: str, candidates: list[dict], top_rerank: int = 20) -> list[dict]:
        """
        Optional Stage 2 Neural Cross-Attention Reranking via Transformer Cross-Encoder.
        Computes token-to-token cross-attention between query and scheme text.
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
            for r, s in zip(to_rerank, raw_scores):
                ce_norm = 1.0 / (1.0 + math.exp(-float(s)))
                r["cross_encoder_score"] = round(ce_norm, 4)
                # Calibrated blend: 30% neural cross-attention + 70% Stage-1 multi-objective score
                r["ranking_score"] = round(0.30 * ce_norm + 0.70 * r["ranking_score"], 4)

            to_rerank.sort(key=lambda x: x["ranking_score"], reverse=True)
            return to_rerank + remaining
        except Exception as e:
            log.warning(f"Cross-encoder reranking failed: {e}")
            return candidates

    def _reciprocal_rank_fusion(
        self,
        dense_scores: Optional[np.ndarray],
        tfidf_scores: np.ndarray,
        k: int = 60,
    ) -> tuple[np.ndarray, dict[int, int], dict[int, int]]:
        """
        Reciprocal Rank Fusion (RRF) - combines ordinal ranks of dense and lexical retrieval.
        RRF(d) = sum(1 / (k + rank_m(d)))
        Eliminates incompatible score scale assumptions between sparse TF-IDF and dense embeddings.
        Returns: (normalized_rrf_scores, dense_rank_map, tfidf_rank_map)
        """
        n = len(self.scheme_ids)
        rrf = np.zeros(n, dtype=np.float32)

        # Lexical ranks
        tfidf_order = np.argsort(tfidf_scores)[::-1]
        tfidf_rank_map = {idx: rank + 1 for rank, idx in enumerate(tfidf_order)}

        # Dense ranks
        dense_rank_map = {}
        if dense_scores is not None and len(dense_scores) == n:
            dense_order = np.argsort(dense_scores)[::-1]
            dense_rank_map = {idx: rank + 1 for rank, idx in enumerate(dense_order)}
            max_rrf = (1.0 / (k + 1)) + (1.0 / (k + 1))
            for i in range(n):
                rrf[i] = (1.0 / (k + dense_rank_map[i])) + (1.0 / (k + tfidf_rank_map[i]))
        else:
            max_rrf = 1.0 / (k + 1)
            for i in range(n):
                rrf[i] = 1.0 / (k + tfidf_rank_map[i])

        # Normalize to [0, 1] range
        normalized_rrf = rrf / max_rrf
        return normalized_rrf, dense_rank_map, tfidf_rank_map

    def _apply_mmr(
        self,
        candidates: list[dict],
        top_k: int,
        lambda_param: float = 0.85,
    ) -> list[dict]:
        """
        Maximal Marginal Relevance (MMR) (Carbonell & Goldstein 1998).
        Vectorized greedy selection balancing relevance with embedding diversity.
        Prevents redundant schemes from the same department from dominating results.
        """
        if len(candidates) <= 1 or self.embeddings is None:
            return candidates

        max_select = min(top_k, 50)
        pool_size = min(len(candidates), max(max_select * 2, 40))
        pool = candidates[:pool_size]
        tail = candidates[pool_size:]

        scheme_to_idx = {sid: i for i, sid in enumerate(self.scheme_ids)}
        indices_in_emb = []
        valid_pool = []
        for c in pool:
            idx = scheme_to_idx.get(c["id"])
            if idx is not None and idx < len(self.embeddings):
                indices_in_emb.append(idx)
                valid_pool.append(c)

        if not valid_pool:
            return candidates

        vectors = self.embeddings[indices_in_emb]  # shape: (P, 384)
        relevance_scores = np.array([c["ranking_score"] for c in valid_pool], dtype=np.float32)

        max_rel = float(np.max(relevance_scores))
        min_rel = float(np.min(relevance_scores))
        if max_rel > min_rel:
            norm_rel = (relevance_scores - min_rel) / (max_rel - min_rel)
        else:
            norm_rel = relevance_scores

        selected = [0]
        unselected = set(range(1, len(valid_pool)))
        sim_matrix = np.dot(vectors, vectors.T)

        while len(selected) < min(max_select, len(valid_pool)) and unselected:
            unselected_list = list(unselected)
            sub_sims = sim_matrix[unselected_list][:, selected]
            max_sims = np.max(sub_sims, axis=1)

            mmr_scores = lambda_param * norm_rel[unselected_list] - (1.0 - lambda_param) * max_sims
            best_idx = int(np.argmax(mmr_scores))
            best_cand = unselected_list[best_idx]

            selected.append(best_cand)
            unselected.remove(best_cand)

        reordered = [valid_pool[i] for i in selected] + [valid_pool[i] for i in unselected]
        return reordered + tail

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

    def _generate_why_recommended(
        self,
        scheme: dict,
        profile: dict,
        query: str,
        sem_score: float,
        prof_score: float,
        state_rel: float,
        cat_match: float,
    ) -> list[str]:
        """Generate explainable, data-backed rationale bullets for why scheme was recommended."""
        reasons = []
        user_state = profile.get("state")
        user_goals = profile.get("goals", [])

        if cat_match >= 0.5 and user_goals:
            reasons.append(f"Category aligns with your interests: {', '.join(user_goals[:2])}")
        if state_rel == 1.0 and user_state:
            reasons.append(f"Specifically enacted for residents of {user_state}")
        elif scheme.get("parsed_is_central"):
            reasons.append("Central Government scheme available across all States/UTs")
        if prof_score >= 0.7:
            reasons.append("High demographic compatibility (age, gender, income criteria met)")
        if query and sem_score >= 0.35:
            reasons.append("High semantic relevance to your stated requirement")

        if not reasons:
            reasons.append("National public benefit matching your baseline eligibility criteria")

        return reasons

    def search(
        self,
        query: str,
        profile: Optional[dict] = None,
        filters: Optional[dict] = None,
        top_k: int = 20,
    ) -> list[dict]:
        """
        Hybrid Reciprocal Rank Fusion (RRF) search and personalization.
        Combines lexical + dense retrieval, deterministic eligibility filtering,
        and multi-objective profile scoring.
        """
        if not self._loaded:
            self.load()

        profile = profile or {}
        filters = filters or {}
        user_goals = profile.get("goals", [])
        user_state = profile.get("state", "")

        has_query = bool(query and query.strip())
        dense_rank_map = {}
        tfidf_rank_map = {}

        if has_query:
            expanded_query = expand_query(query.strip())
            emb_scores = self._embedding_scores(expanded_query)
            tfidf_scores = self._tfidf_scores(expanded_query)
            # Reciprocal Rank Fusion
            query_scores, dense_rank_map, tfidf_rank_map = self._reciprocal_rank_fusion(
                emb_scores, tfidf_scores, k=self.config.rrf_k
            )
        else:
            query_scores = np.full(len(self.scheme_ids), 0.5)

        w_q = self.config.w_query if has_query else 0.0
        w_p = self.config.w_profile_composite if has_query else 1.0

        results = []
        for i, scheme_id in enumerate(self.scheme_ids):
            scheme = self.scheme_index.get(scheme_id)
            if scheme is None:
                continue

            # Apply structured search filters
            if filters.get("state") and not bool(scheme.get("parsed_is_central")):
                if filters["state"].lower() not in scheme.get("state_ministry", "").lower():
                    continue
            if filters.get("level"):
                if filters["level"].lower() not in scheme.get("level", "").lower():
                    continue
            if filters.get("category"):
                if filters["category"].lower() not in (scheme.get("categories_raw", "") or "").lower():
                    continue

            # Deterministic eligibility evaluation
            elig = assess_eligibility(scheme, profile)
            if elig.status == EligibilityStatus.NOT_ELIGIBLE:
                continue  # Hard safety prune

            # Feature components
            q_score = float(query_scores[i]) if i < len(query_scores) else 0.0
            prof = self._profile_match(scheme, profile)
            state_rel = self._state_relevance(scheme, user_state)
            cat_match = self._category_match(scheme, user_goals)
            completeness = float(scheme.get("data_completeness_score", 0.5))

            # Composite profile score
            profile_composite = (
                self.config.w_profile_fit * prof
                + self.config.w_state_relevance * state_rel
                + self.config.w_category_overlap * cat_match
                + self.config.w_data_evidence * completeness
            )

            # Unified multi-objective score
            final_score = (w_q * q_score) + (w_p * profile_composite)

            # Confidence multiplier
            if elig.status == EligibilityStatus.POTENTIALLY_ELIGIBLE:
                final_score *= 1.10
            else:
                final_score *= 0.90

            why_bullets = self._generate_why_recommended(
                scheme, profile, query if has_query else "", q_score, prof, state_rel, cat_match
            )

            results.append({
                **scheme,
                "eligibility": elig.to_dict(),
                "ranking_score": round(final_score, 4),
                "semantic_score": round(q_score, 4),
                "profile_match_score": round(prof, 4),
                "state_relevance_score": round(state_rel, 4),
                "why_recommended": why_bullets,
                "rrf_score": round(q_score, 5) if has_query else None,
                "dense_rank": dense_rank_map.get(i),
                "tfidf_rank": tfidf_rank_map.get(i),
            })

        # Rank descending
        results.sort(key=lambda x: x["ranking_score"], reverse=True)

        # Maximal Marginal Relevance (MMR) for candidate diversity
        if self.config.enable_diversity_mmr and len(results) > 1:
            results = self._apply_mmr(results, top_k=top_k, lambda_param=self.config.mmr_lambda)

        # Optional Stage 2 Neural Cross-Attention Reranking
        if has_query and self.config.enable_cross_encoder:
            results = self._rerank_with_cross_encoder(query.strip(), results, top_rerank=self.config.cross_encoder_top_n)

        return results

    def get_similar_schemes(self, scheme_id: int, top_k: int = 4) -> list[dict]:
        """
        Content-Based Filtering (Item-to-Item Similarity).
        Uses 384-dimensional dense semantic embeddings to discover complementary
        and similar alternative schemes.
        """
        if not self._loaded:
            self.load()
        if scheme_id not in self.scheme_index or self.embeddings is None:
            return []

        try:
            target_idx = self.scheme_ids.index(scheme_id)
        except ValueError:
            return []

        target_scheme = self.scheme_index[scheme_id]
        target_vec = self.embeddings[target_idx]

        # Compute cosine similarity
        sims = (self.embeddings @ target_vec).flatten()
        ranked_indices = np.argsort(sims)[::-1]

        target_cats = set(re.split(r"[|,;]", target_scheme.get("categories_raw", "") or ""))
        target_cats = {c.strip().lower() for c in target_cats if c.strip()}

        similar = []
        for idx in ranked_indices:
            cand_id = self.scheme_ids[idx]
            if cand_id == scheme_id:
                continue

            cand = self.scheme_index.get(cand_id)
            if not cand:
                continue

            cand_cats = set(re.split(r"[|,;]", cand.get("categories_raw", "") or ""))
            cand_cats = {c.strip().lower() for c in cand_cats if c.strip()}
            shared = list(target_cats & cand_cats)

            sim_val = float(sims[idx])
            match_pct = round(max(0.0, min(1.0, sim_val)) * 100, 1)

            similar.append({
                "id": cand["id"],
                "name": cand["name"],
                "slug": cand.get("slug", ""),
                "level": cand.get("level", ""),
                "state_ministry": cand.get("state_ministry", ""),
                "categories_raw": cand.get("categories_raw", ""),
                "description": (cand.get("description", "") or "")[:200] + "...",
                "benefits": (cand.get("benefits", "") or "")[:180] + "...",
                "similarity_score": round(sim_val, 4),
                "match_pct": match_pct,
                "shared_categories": [c.title() for c in shared[:3]],
                "official_link": cand.get("official_link", ""),
                "myscheme_url": cand.get("myscheme_url", ""),
                "required_documents": cand.get("required_documents", []),
            })

            if len(similar) >= top_k:
                break

        return similar

    def get_complementary_bundles(self, profile: Optional[dict] = None) -> list[dict]:
        """
        Propose complementary welfare packages (e.g. Farmer Package, Girl Student Pathway).
        Evaluates independent eligibility for each constituent scheme without assuming
        cross-scheme eligibility transfer.
        """
        if not self._loaded:
            self.load()
        profile = profile or {}

        bundles = []
        for b in CURATED_BUNDLES_DATA:
            bundle_schemes = []
            for item in b["schemes"]:
                sid = item["id"]
                scheme = self.scheme_index.get(sid)
                if not scheme:
                    continue

                elig = assess_eligibility(scheme, profile)
                bundle_schemes.append({
                    "id": scheme["id"],
                    "name": scheme["name"],
                    "slug": scheme.get("slug", ""),
                    "level": scheme.get("level", ""),
                    "state_ministry": scheme.get("state_ministry", ""),
                    "benefit_role": item["benefit_role"],
                    "rationale": item["rationale"],
                    "eligibility": elig.to_dict(),
                    "official_link": scheme.get("official_link", ""),
                    "myscheme_url": scheme.get("myscheme_url", ""),
                    "required_documents": scheme.get("required_documents", []),
                })

            bundles.append({
                "bundle_id": b["bundle_id"],
                "title": b["title"],
                "description": b["description"],
                "target_persona": b["target_persona"],
                "icon": b["icon"],
                "schemes": bundle_schemes,
            })

        return bundles

    def get_recommended_feed(
        self,
        profile: Optional[dict] = None,
        saved_ids: Optional[list[int]] = None,
        top_k: int = 8,
    ) -> dict:
        """
        Dedicated Personalized Recommendation Feed.
        Aggregates:
        1. Top personalized scheme recommendations for the profile
        2. Complementary welfare benefit bundles
        3. Item-to-item recommendations based on saved items
        4. State-specific spotlight
        """
        if not self._loaded:
            self.load()
        profile = profile or {}
        saved_ids = saved_ids or []

        # 1. Top profile recommendations
        top_matches = self.search(query="", profile=profile, top_k=top_k)

        # 2. Complementary bundles
        bundles = self.get_complementary_bundles(profile=profile)

        # 3. Item-to-Item recommendations based on saved items
        similar_to_saved = []
        if saved_ids:
            latest_id = saved_ids[-1]
            if latest_id in self.scheme_index:
                raw_sims = self.get_similar_schemes(latest_id, top_k=4)
                for s in raw_sims:
                    full_scheme = self.scheme_index.get(s["id"])
                    if full_scheme:
                        elig = assess_eligibility(full_scheme, profile)
                        if elig.status != EligibilityStatus.NOT_ELIGIBLE:
                            similar_to_saved.append({
                                **full_scheme,
                                "eligibility": elig.to_dict(),
                                "ranking_score": round(s["similarity_score"], 4),
                                "semantic_score": round(s["similarity_score"], 4),
                                "profile_match_score": 0.8,
                                "state_relevance_score": 0.8,
                                "why_recommended": [f"High content similarity ({s['match_pct']}%) to saved scheme #{latest_id}"],
                            })

        # 4. State spotlight
        user_state = profile.get("state", "")
        state_spotlight = []
        if user_state:
            state_schemes = [
                s for s in self.schemes
                if user_state.lower() in (s.get("state_ministry", "") or "").lower()
            ]
            state_schemes.sort(key=lambda x: x.get("data_completeness_score", 0), reverse=True)
            for s in state_schemes[:4]:
                elig = assess_eligibility(s, profile)
                if elig.status != EligibilityStatus.NOT_ELIGIBLE:
                    state_spotlight.append({
                        **s,
                        "eligibility": elig.to_dict(),
                        "ranking_score": 0.85,
                        "semantic_score": 0.5,
                        "profile_match_score": 0.75,
                        "state_relevance_score": 1.0,
                        "why_recommended": [f"Official initiative of Government of {user_state}"],
                    })

        # Summary text
        summary_parts = []
        if profile.get("age"): summary_parts.append(f"Age {profile['age']}")
        if profile.get("gender"): summary_parts.append(profile["gender"].title())
        if profile.get("state"): summary_parts.append(profile["state"])
        if profile.get("caste_category"): summary_parts.append(profile["caste_category"])
        summary_str = " · ".join(summary_parts) if summary_parts else "Default Citizen Profile"

        return {
            "top_matches": top_matches[:top_k],
            "bundles": bundles,
            "similar_to_saved": similar_to_saved[:4],
            "state_spotlight": state_spotlight[:4],
            "algorithm_info": {
                "architecture": "Hybrid Reciprocal Rank Fusion (RRF) + Demographic Utility + MMR Diversity",
                "lexical_model": "TF-IDF (30,000 n-grams)",
                "dense_model": "all-MiniLM-L6-v2 (384 dimensions)",
                "diversity_algorithm": "Maximal Marginal Relevance (lambda=0.85)",
                "device": self.device,
                "hardware": self.gpu_name,
            },
            "active_profile_summary": summary_str,
        }

    def get_personas(self) -> list[dict]:
        """Returns preset citizen personas for live demo and evaluation."""
        return DEMO_PERSONAS

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
            "architecture": "Hybrid Reciprocal Rank Fusion (RRF) + MMR Diversity",
            "bi_encoder_model": "all-MiniLM-L6-v2",
            "cross_encoder_model": "cross-encoder/ms-marco-MiniLM-L-6-v2 (optional)",
            "schemes_with_structured_docs": sum(1 for s in self.schemes if s.get("required_documents")),
        }

    def extractive_qa(self, query: str, top_k: int = 3) -> list[dict]:
        """Simple extractive QA: find most relevant scheme snippets."""
        results = self.search(query, top_k=top_k)[:top_k]
        answers = []
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
