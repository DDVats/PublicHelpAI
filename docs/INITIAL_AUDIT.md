# PublicHelp AI — Initial Technical & Scientific Audit

**Audit Date:** October 2026  
**Auditor:** Senior AI/ML & Information Retrieval Engineer  
**Codebase:** `~/Downloads/government`

---

## 1. Executive Summary

This audit establishes the baseline facts and unvarnished realities of the PublicHelp AI project before recent corrective actions. While the project possessed a functional prototype architecture with FastAPI, React, and SQLite, critical technical bugs and scientific methodological flaws compromised both recommendation correctness and evaluation validity.

---

## 2. Dataset & Data Engineering Audit

### Findings:
1. **Raw Corpus Size:** Exactly **2,066 scheme records** retrieved from the public repository `Aryan-Pardeshi/gov-myscheme-dataset` (scraped from `myscheme.gov.in`).
2. **Duplicate Records:** 0 exact duplicates found by slug or normalized name.
3. **Encoding Bug:** The original CSV contains a UTF-8 Byte Order Mark (`\ufeffScheme Name`), which caused raw dictionary readers without `utf-8-sig` encoding to corrupt column access.
4. **Data Completeness Bug:** The initial completeness metric evaluated basic text presence across 7 fields. Because 99.8% of records had these fields populated, 2,061 out of 2,066 schemes received a score of `1.0`, rendering the data completeness signal completely inert in ranking.
5. **Gender Parsing Disaster:** 
   - Initial parser classified **1,519 schemes** as gender-specific, including **1,112 schemes as male-only**.
   - Root Cause: Unbounded substring regex matching `\bmen\b` and `\bman\b` falsely triggered on compound administrative words like `government`, `management`, `department`, `permanent`, and `recommendation`.
   - Consequence: Schemes like "AICTE Grants", "Atal Amrit Abhiyan", and "Aam Aadmi Bima Yojana" were falsely hard-excluded for female citizens.
6. **Income Parsing Flaws:**
   - Raw regex matched numbers without unit validation, extracting corrupt income ceilings such as ₹240/year for ARAVANAIPPU. Only 23 schemes had parseable income ceilings.

---

## 3. Eligibility Engine & Rule Soundness Audit

1. **Deterministic Separation:** The separation of hard eligibility filters from soft ranking scores is architecturally sound.
2. **Conservative Default:** The tri-state model (`potentially_eligible`, `needs_more_info`, `not_eligible`) properly treats missing user profile data as unknown rather than eligible.
3. **State Matching Fragility:** Initial substring matching between `state_ministry` and user profile could match substrings loosely without normalizing union territories or ministry jurisdictions.

---

## 4. Recommendation & Retrieval Algorithm Audit

1. **Latent Latency Bottleneck:**
   - `MLEngine._embedding_scores()` re-instantiated `SentenceTransformer("all-MiniLM-L6-v2")` on **every single user query**, causing 1.5–3.0 second latency per request and unnecessary disk I/O.
2. **Empty Query Failure:**
   - The original FastAPI schema enforced `min_length=1` for search queries. When a citizen configured their profile without entering text in the search bar, the UI failed to return any schemes.
3. **Arbitrary Linear Combination:**
   - Soft scores summed uncalibrated components (35% semantic, 25% profile, 20% state, 10% category, 10% completeness). Without score normalization, dense embedding cosine similarities (range [-1, 1]) and sparse TF-IDF scores (range [0, 1]) had mismatched variances.

---

## 5. Evaluation Methodology Audit

1. **Microscopic Query Set:** The original evaluation relied on only **8 search queries**.
2. **Self-Serving Ground Truth:** Ground truth labels were constructed using keyword overlap, creating an artificial bias where pure TF-IDF naturally scored higher than semantic or hybrid systems.
3. **Hardcoded UI Metrics:** The frontend `ML.tsx` page displayed hardcoded static strings (`0.850`, `0.274`, `0.928`) instead of dynamically consuming pipeline outputs.

---

## 6. Audit Conclusion & Roadmap

Prior to our intervention, the application suffered from:
- A false-positive gender exclusion bug affecting >50% of the corpus.
- Ineffective completeness weighting.
- Unnecessary 2-second per-query neural loading overhead.
- Flawed 8-query evaluation.

All of these issues have been targeted for scientific correction in the improvement phase.
