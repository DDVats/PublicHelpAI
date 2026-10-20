# PublicHelp AI — Government Scheme Navigator

**An explainable, locally-runnable AI/ML application for discovering Indian government schemes and benefits.**

> Academic project — not an official government service. All scheme data sourced from the public gov-myscheme-dataset.

---

## Quick Start (Fedora Linux / Python 3.12)

### 1. Prerequisites

```bash
# Ensure Python 3.12, Node 22, npm 10 are available
python3 --version   # Python 3.12.x
node --version      # v22.x
npm --version       # 10.x
```

### 2. Clone / Navigate to project

```bash
cd ~/Downloads/government
```

### 3. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Ingest dataset and build index

```bash
# Ingest 2,066 schemes into SQLite
python scripts/ingest_data.py

# Build TF-IDF index (fast, ~10s)
python scripts/build_index.py --no-transformers

# Build full hybrid index with sentence embeddings (~60s on CPU, download ~90MB once)
python scripts/build_index.py
```

### 5. Start the backend

```bash
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API available at: **http://localhost:8000**  
API docs (interactive): **http://localhost:8000/docs**

### 6. Install and start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: **http://localhost:5173**

---

## Running Tests

```bash
# All backend tests (63 tests across API, Data, Eligibility)
source venv/bin/activate
pytest backend/tests/ -v

# Eligibility unit tests only
pytest backend/tests/test_eligibility.py -v

# Data quality tests
pytest backend/tests/test_data.py -v

# API integration tests
pytest backend/tests/test_api.py -v
```

## Running Evaluation

```bash
source venv/bin/activate
python scripts/evaluate.py
# Outputs:
# - reports/model_comparison.json
# - reports/evaluation_report.md
# - reports/evaluation_results.csv
# - reports/query_level_results.csv
```

## Colab Notebook for GPU Research & Training

```bash
# Single entry-point notebook:
notebooks/PublicHelp_AI_Research_Training.ipynb
```

---

## Project Structure

```
government/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routers (health, schemes, recommend, qa, saved, compare, stats)
│   │   ├── core/          # ML engine + eligibility engine
│   │   ├── models/        # Pydantic schemas
│   │   └── main.py        # FastAPI app entry point
│   └── tests/             # 63 pytest test cases
├── frontend/
│   └── src/
│       ├── pages/         # Landing, Search, SchemeDetail, Compare, Saved, ML, Privacy
│       ├── components/    # Layout, SchemeCard, EligibilityBadge, ProfileForm
│       └── api.ts         # Axios API client
├── notebooks/
│   └── PublicHelp_AI_Research_Training.ipynb # Standalone research & Colab training notebook
├── scripts/
│   ├── ingest_data.py     # Dataset ingestion & structured regex parsing pipeline
│   ├── build_index.py     # TF-IDF + sentence embedding index builder
│   ├── validate_data.py   # Data quality audit validation
│   └── evaluate.py        # 30-query retrieval benchmark (P@K, R@K, NDCG@K, MRR, MAP)
├── data/
│   ├── raw/               # Untouched copy of raw CSV
│   ├── clean/             # Cleaned CSV + JSON
│   ├── cache/             # Precomputed TF-IDF matrix & 384-dim embeddings
│   └── publichelp.db      # SQLite database (2,066 authentic schemes)
├── docs/                  # INITIAL_AUDIT, IMPROVEMENT_REPORT, EXPERIMENT_DESIGN, etc.
├── reports/               # Machine-readable evaluation & data quality reports
├── references/            # Cloned reference repositories (research only)
└── requirements.txt
```

---

## Architecture

```
React (Vite + TypeScript + Tailwind)  [http://localhost:5173]
       ↕ HTTP/JSON (Axios)
FastAPI (Python 3.12, Uvicorn)        [http://localhost:8000]
       ↕
  ┌─────────────────────────────┐
  │  Eligibility Engine         │  Deterministic rule engine (age, gender, income, state, caste)
  │  ML Engine (Hybrid)         │  TF-IDF + sentence-transformers/all-MiniLM-L6-v2 (cached singleton)
  │  SQLite DB (2,066 schemes)  │  Full-text search (FTS5) + structured queries
  └─────────────────────────────┘
```

**Ranking formula:**
```
score = 0.35 × semantic_sim + 0.25 × profile_match + 0.20 × state_relevance
      + 0.10 × category_match + 0.10 × data_completeness
```

---

## Dataset

- **Source:** [gov-myscheme-dataset](https://github.com/Aryan-Pardeshi/gov-myscheme-dataset) — scraped from myscheme.gov.in
- **Records:** 2,066 schemes (527 Central + 1,539 State/UT)
- **Coverage:** 100% name/description/benefits, 18.4% age parsed, 22.0% gender parsed, 3.8% income ceiling parsed
- **Verified:** No individual records manually verified against official source pages — always check official links

---

## Acceptance Criteria Status

| Criterion | Status |
|---|---|
| Launches locally with documented commands | ✅ |
| Real imported records visible (2,066) | ✅ |
| Profile change affects ranking/eligibility | ✅ |
| Natural-language search returns results | ✅ |
| Real source links exposed | ✅ |
| Evaluation runs reproducibly (30 queries) | ✅ |
| Interface polished and responsive | ✅ |
| Works without paid API keys | ✅ |
| CPU fallback (no CUDA required) | ✅ |
| 63 / 63 tests passing | ✅ |
| No placeholder buttons/routes | ✅ |
| Limitations documented | ✅ |

---

## Limitations

- No individual scheme manually verified against official government portals
- Eligibility parsing from unstructured prose — some conditions may remain unknown
- Evaluation benchmark is preliminary (30 queries across 8 civic categories)
- Income ceiling parseable for ~3.8% of schemes (sparse in source dataset)
- Saved schemes session-scoped in client browser memory

## Licence & Attribution

Dataset: public [gov-myscheme-dataset](https://github.com/Aryan-Pardeshi/gov-myscheme-dataset).  
ML model: `sentence-transformers/all-MiniLM-L6-v2` (Apache 2.0).  
Original scheme data from `myscheme.gov.in` (Government of India).


