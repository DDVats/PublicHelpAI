# PublicHelp AI — Research, References & Comparative Analysis

## 1. External Repositories & Datasets Inspected

### 1. Dataset: `Aryan-Pardeshi/gov-myscheme-dataset`
- **URL:** https://github.com/Aryan-Pardeshi/gov-myscheme-dataset
- **Source Material:** Scraped from official `myscheme.gov.in` public pages.
- **Records:** 2,066 scheme entries in CSV and JSON formats.
- **Licence:** Public domain government informational data.
- **Audit Findings:** No exact duplicates. Required BOM stripping (`\ufeff`). Rich in unstructured text (descriptions, benefits, procedures) but sparse in structured attributes (age, income, category limits).
- **Project Role:** Primary source corpus for ingestion, SQLite indexing, and evaluation.

### 2. Implementation Reference: `NandiniSrivastava/SchemeConnect-AI`
- **URL:** https://github.com/NandiniSrivastava/SchemeConnect-AI
- **Licence:** MIT
- **Inspected Components:** Demographic profile matching and rule categorization.
- **Key Takeaways & Pitfalls Avoided:** 
  - SchemeConnect used hardcoded demographic thresholds that frequently produced false positives when data was missing.
  - PublicHelp AI adopted a conservative tri-state model (`potentially_eligible`, `needs_more_info`, `not_eligible`) where missing criteria are classified as unknown, never as eligible.

### 3. Semantic Search Reference: `divisayscode/YojanaSetu-Government-Scheme-Recommendation-System`
- **URL:** https://github.com/divisayscode/YojanaSetu-Government-Scheme-Recommendation-System
- **Licence:** MIT
- **Inspected Components:** Sentence-transformers vector search and Streamlit UI.
- **Key Takeaways & Pitfalls Avoided:**
  - YojanaSetu relied exclusively on dense vector search without deterministic eligibility filtering. This led to serious errors, such as recommending women-only scholarships to male applicants if the query text matched.
  - PublicHelp AI decoupled deterministic eligibility exclusion from soft semantic ranking to prevent disqualifying rule violations.

### 4. Official Platforms
- **MyScheme Portal:** https://www.myscheme.gov.in/ — Used to verify schema fields, metadata naming, and application modes.
- **National Scholarship Portal (NSP):** https://scholarships.gov.in/ — Used to benchmark central scholarship criteria (Pre-Matric, Post-Matric, Top Class).

---

## 2. Model Architecture & Literature

### Sentence Transformers (`all-MiniLM-L6-v2`)
- **Reference:** Reimers & Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (EMNLP 2019).
- **Model Card:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **Parameters:** 22.7M parameters; 384-dimensional dense vectors.
- **Suitability:** Extreme efficiency on standard laptop CPUs (inference < 20ms per query), low memory footprint (< 120MB in RAM), and robust general semantic similarity.

### TF-IDF & Sublinear Term Frequency
- **Reference:** Robertson et al., BM25 and Okapi TF-IDF adaptations.
- **Implementation:** `scikit-learn` `TfidfVectorizer(ngram_range=(1,2), max_features=30000, sublinear_tf=True)`.
- **Role:** High-precision exact keyword matching for specific scheme titles, ministry abbreviations, and legal terminology.

### Contrastive Ranking Loss (`MultipleNegativesRankingLoss`)
- **Reference:** Henderson et al., "Efficient Natural Language Response Suggestion for Smart Reply" (2017).
- **Mechanism:** Given batch $(q_i, p_i)$, treats all other documents $p_j (j \neq i)$ in the mini-batch as negative samples.
- **Included in:** `notebooks/PublicHelp_AI_Research_Training.ipynb` for optional GPU fine-tuning.
