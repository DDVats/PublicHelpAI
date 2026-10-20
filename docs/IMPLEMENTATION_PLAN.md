# Implementation Plan — PublicHelp AI

## Completed phases

### Phase 1 — Research ✅
- Cloned and inspected gov-myscheme-dataset (2,066 records, 16 columns)
- Assessed SchemeConnect-AI (TF-IDF pattern useful, GPT dependency rejected)
- Assessed YojanaSetu (semantic retrieval concept, notebooks not production-ready)
- Documented architecture, data dictionary, licences

### Phase 2 — Product Definition ✅
All 12 product features implemented:
1. Landing page with live stats, how-it-works, limitations ✅
2. Profile form: state, age, gender, category, income, rural/urban, occupation, education ✅
3. Natural-language search with semantic + TF-IDF ✅
4. Personalised ranked results ✅
5. Eligibility with 3 states + human-readable explanation ✅
6. Individual scheme detail pages ✅
7. Benefits, eligibility, exclusions, docs, application process, source links, data freshness ✅
8. Saved schemes + comparison view ✅
9. Demo profiles (Priya, Ramesh, Meena, Suresh — all clearly labelled fictional) ✅
10. ML evaluation and data-quality page ✅
11. Privacy page ✅
12. Responsive layout ✅

### Phase 3 — Recommendation Architecture ✅
- **Layer A (Eligibility)**: Rule-based, conservative, 5 fields (age, gender, income, state, caste)
- **Layer B (Semantic)**: TF-IDF baseline + sentence-transformers/all-MiniLM-L6-v2 (2066×384)
- **Layer C (QA)**: Extractive, grounded in scheme records, cites source
- Ranking: 5-component configurable formula with documented weights

### Phase 4 — Dataset Engineering ✅
- `scripts/ingest_data.py` — full pipeline, 2,066 records, 0 duplicates
- `scripts/build_index.py` — TF-IDF (50k features) + embeddings (384d)
- `scripts/validate_data.py` — quality report, 0 critical issues
- SQLite DB with FTS5 virtual table

### Phase 5 — Evaluation ✅
- `scripts/evaluate.py` — P@5, R@5, NDCG@5 on 8 curated queries
- Two systems compared: TF-IDF baseline vs hybrid profile-aware
- Results in `reports/evaluation_report.md` + `reports/evaluation_results.json`

### Phase 6 — UI ✅
- React 19 + TypeScript + Tailwind CSS 3 + Vite 6
- 7 pages: Landing, Search, SchemeDetail, Compare, Saved, ML, Privacy
- Production build successful (761KB JS, 33KB CSS)

### Phase 7 — Engineering ✅
- FastAPI with typed Pydantic schemas, input validation, pagination
- CORS configured for localhost dev
- No PII collected; session-only data
- Requirements pinned in requirements.txt

### Phase 8 — Testing ✅
- 39 unit/data tests: all PASSED
- 17 API integration tests: all PASSED
- Frontend production build: PASSED

### Phase 9 — Deliverables ✅
- README.md with exact setup commands
- docs/DEMO_SCRIPT.md
- docs/PROJECT_REPORT.md
- reports/evaluation_report.md
- Complete source code

## Known limitations
- Income ceiling parseable for only 1.1% of schemes (sparse field in source data)
- 80.6% of schemes lack exclusions text
- Eligibility parsing is regex-based from free text — not 100% accurate
- Evaluation on 8 manual queries — preliminary, not population-level
- No individual scheme verified against its live official page
