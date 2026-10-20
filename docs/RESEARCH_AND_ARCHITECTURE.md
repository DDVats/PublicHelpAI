# Research and Architecture — PublicHelp AI

## 1. Dataset Research

### Source: gov-myscheme-dataset (Aryan Pardeshi)
- **URL**: https://github.com/Aryan-Pardeshi/gov-myscheme-dataset
- **Records**: 2,066
- **Columns**: 16 (see DATA_DICTIONARY.md)
- **Coverage**: Central Government (527) + State/UT Governments (1,539)
- **Top states**: Puducherry (186), Gujarat (118), Goa (116), Tamil Nadu (108), Rajasthan (83)
- **Missing data**: Exclusions/Ineligibility 80.6% missing — handled conservatively

### Quality Assessment
| Field | Coverage |
|---|---|
| Scheme Name | 100% |
| Description | 100% |
| Benefits | 100% |
| Eligibility Criteria | 99.9% |
| Official Link | 100% |
| Exclusions/Ineligibility | 19.4% |

## 2. Reference Repository Assessment

### SchemeConnect-AI (NandiniSrivastava)
- TF-IDF + cosine similarity baseline pattern — reusable
- GPT dependency for summaries — **not reused** (paid API)
- Flask frontend — replaced with React/FastAPI

### YojanaSetu (divisayscode)
- Semantic search concept, scraping-based pipeline
- Notebooks only, not production-ready
- Concept borrowed: retrieval-then-answer pattern

## 3. Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React + TypeScript UI              │
│  Landing | Profile | Search | Results | Detail | QA │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/JSON
┌──────────────────▼──────────────────────────────────┐
│              FastAPI Backend (Python 3.12)           │
│  /api/schemes  /api/recommend  /api/search  /api/qa  │
└──────┬───────────────┬───────────────┬──────────────┘
       │               │               │
  ┌────▼────┐   ┌──────▼──────┐  ┌───▼────────┐
  │ SQLite  │   │ Eligibility │  │ ML Engine  │
  │ (2066   │   │   Engine    │  │ TF-IDF +   │
  │ schemes)│   │  (rules)    │  │ SentTrans  │
  └─────────┘   └─────────────┘  └────────────┘
```

## 4. ML Pipeline

**Layer A — Eligibility Engine**
- Rule-based: age, state, income band, gender, caste/category, occupation
- Three states: `potentially_eligible`, `needs_more_info`, `not_eligible`
- Human-readable explanation per rule

**Layer B — Semantic Retrieval**
- Baseline: scikit-learn TF-IDF + cosine similarity
- Enhanced: sentence-transformers/all-MiniLM-L6-v2 (22.7M params, ~90MB)
- Embeddings cached in `data/cache/embeddings.npy`
- CPU fallback enforced via `CUDA_VISIBLE_DEVICES=-1` when unavailable

**Layer C — Grounded QA**
- Extractive: retrieve top-3 matching scheme chunks, return relevant text
- No external LLM — fully local, fully offline

**Ranking Function**
```
score = 0.35 * semantic_sim
      + 0.25 * profile_match
      + 0.20 * state_relevance
      + 0.10 * category_match
      + 0.10 * data_completeness
      - 999  * if eligibility == not_eligible
```
