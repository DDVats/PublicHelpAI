# PublicHelp AI — Complete Project Explanation & Viva Presentation Guide

---

## Part 1: What is the Project? (The Big Picture)

### 1. Project Title
**PublicHelp AI: A Multi-Channel Hybrid Recommender System with Deterministic Eligibility & Explainability for Citizen Welfare Schemes**

### 2. The Problem Statement
The Government of India and State Governments run over 2,000 welfare schemes covering agriculture, education, pensions, women empowerment, health insurance, and enterprise loans. However, the majority of eligible citizens—especially rural, elderly, and lower-income individuals—fail to benefit due to **severe information asymmetry**:
- **Fragmented Portals**: Schemes are dispersed across hundreds of central and state ministry websites.
- **Complex Eligibility Criteria**: Income ceilings, age brackets, domicile rules, caste categories, and landholding limits are written in convoluted legal phrasing.
- **Keyword Search Failure**: If a farmer searches *"financial help"*, standard lexical search often fails because the scheme is named *"PM Kisan Samman Nidhi"* or *"Pradhan Mantri Fasal Bima"*, which may not contain the exact colloquial query words.

### 3. The Solution: Why a Recommender System (Not Just Search)?
PublicHelp AI transforms this discovery process. Instead of treating welfare discovery as a simple search box:
1. It takes a citizen’s **demographic profile** (age, gender, state, income, caste category, occupation, residence).
2. It uses a **Hybrid Reciprocal Rank Fusion (RRF)** engine combining sparse keyword matching (TF-IDF) with dense semantic understanding (`all-MiniLM-L6-v2` embeddings accelerated on GPU).
3. It filters candidates through a **Deterministic Eligibility Engine** (guaranteeing legal criteria like gender or age boundaries are never violated).
4. It applies **Maximal Marginal Relevance (MMR)** so top recommendations are diverse across health, income, and education rather than 10 repetitive variants from the same department.
5. It groups schemes into **Complementary Welfare Packages** (e.g. Farmer income + insurance + solar subsidy).
6. It provides **Transparent Explainability ("Why Recommended")** so the citizen understands why each scheme matches their profile.

---

## Part 2: How Does It Work? (System Architecture & Pipeline)

```
[ User Profile + Query ]
          │
          ├──► [ 1. Sparse Lexical Channel (TF-IDF N-grams) ] ──┐
          │                                                    ▼
          └──► [ 2. Dense Semantic Channel (all-MiniLM-L6-v2) ] ──► [ 3. Reciprocal Rank Fusion (RRF, k=60) ]
                                                                                │
                                                                                ▼
[ 4. Deterministic Eligibility Engine ] ◄──────────────────────── [ Candidate Pool (Top 2,066) ]
  • Checks: State / Age / Gender / Income / Caste / Land
  • Tri-state: POTENTIALLY_ELIGIBLE, NEEDS_MORE_INFO, NOT_ELIGIBLE
                                                                                │
                                                                                ▼
[ 5. Multi-Objective Scoring & Confidence Multiplier ] ◄────────── [ Eligible Candidates Only ]
  • Demographic utility + State relevance + Category overlap
                                                                                │
                                                                                ▼
[ 6. Vectorized Maximal Marginal Relevance (MMR, λ=0.85) ] ──► Prevents department duplication
                                                                                │
                                                                                ▼
[ 7. Explainability Generator & Feature Presentation ]
  • "Why Recommended" data-backed badges
  • Item-to-Item Content-Based Similar Schemes
  • Curated Complementary Benefit Bundles
```

### Detailed Breakdown of Components

#### 1. Dual-Channel Candidate Retrieval
- **Lexical Channel (TF-IDF)**: Extracts word and character n-grams to catch exact statutory terms, scheme names, and acronyms (e.g., "PMAY", "KCC", "OBC scholarship").
- **Dense Semantic Channel (GPU Sentence Transformers)**: Encodes queries and scheme descriptions into 384-dimensional vector embeddings using `sentence-transformers/all-MiniLM-L6-v2` running on an **NVIDIA GeForce RTX 2050 GPU**. It captures semantic intent (e.g., *"scholarship for poor college girl"* connects to *"Post-Matric Financial Assistance"* even without word overlap).

#### 2. Reciprocal Rank Fusion (RRF)
Instead of adding raw cosine similarity to arbitrary TF-IDF scores (which distorts rankings because their score scales and distributions differ), RRF combines their **ordinal ranks**:
$$\text{RRF Score}(d) = \frac{1}{k + r_{\text{dense}}(d)} + \frac{1}{k + r_{\text{tfidf}}(d)}$$
Where $k = 60$ is the standard smoothing constant. This ensures both channels contribute fairly and robustly.

#### 3. Deterministic Eligibility Engine
**CRITICAL EXAMINER DEFENSE POINT**:
*Why not use an LLM or neural network for eligibility?*
> **Answer**: Deep learning and LLMs are probabilistic and prone to hallucination. Eligibility for government welfare is legal and deterministic. If a citizen exceeds the income cap or is male applying for a female-only scheme, the system must produce a guaranteed hard rejection (`NOT_ELIGIBLE`).
- The engine uses a strict **tri-state status**:
  - `POTENTIALLY_ELIGIBLE`: All specified criteria match.
  - `NEEDS_MORE_INFO`: Information is missing from the scheme text or user profile; citizen is alerted rather than falsely confirmed.
  - `NOT_ELIGIBLE`: Explicit contradiction found (e.g., wrong state, over age limit). Automatically pruned from recommendations.

#### 4. Maximal Marginal Relevance (MMR)
- **Problem**: Without MMR, if a user searches *"farming assistance"*, the top 10 results might all be different sub-sections of the Agriculture Department's crop seed subsidy.
- **Solution**: MMR iteratively picks the next candidate that maximizes relevance while minimizing cosine similarity to already chosen results ($\lambda = 0.85$). We vectorized this with matrix multiplication (`np.dot`) so it completes in under 1 millisecond.

#### 5. Item-to-Item Content-Based Filtering ("Similar Schemes")
- On every scheme detail page, the system calculates pairwise cosine similarity across all 2,066 scheme embeddings to suggest related alternatives and displays the match percentage and shared categories.

#### 6. Complementary Welfare Packages (Bundles)
- Citizens rarely need just one scheme. For example, a farmer needs working capital (`PM-Kisan`), risk protection (`Fasal Bima`), and power infrastructure (`PM-KUSUM`).
- The engine groups complementary schemes and independently evaluates eligibility for every single item in the package.

#### 7. Transparent Explainability ("Why Recommended")
- Every recommendation card displays truthful, data-backed bullet points explaining why it was recommended based on state match, category alignment, income ceiling compliance, or central coverage.

---

## Part 2: Real Evaluation Metrics (What to Show)

We evaluated the system using a reproducible benchmark of 20 realistic citizen queries and personas (`reports/model_comparison.json`):

| Evaluation Metric | Baseline (Hybrid Sum) | Upgraded (RRF + MMR) | Improvement / Meaning |
| :--- | :--- | :--- | :--- |
| **Precision@5** | 0.0815 | **0.0963** | **+18.2%** higher relevance in top 5 items |
| **NDCG@5** | 0.1071 | **0.1220** | **+13.9%** higher ranking quality |
| **MRR (Mean Reciprocal Rank)** | 0.1629 | **0.2000** | **+22.8%** faster discovery of relevant scheme |
| **Average Query Latency** | 548.5 ms | **388.9 ms** | **29.1% faster** response time |
| **Catalog Coverage** | 100.0% | **100.0%** | All 2,066 schemes in database are indexable & discoverable |
| **Intra-List Diversity (ILD)** | 0.6840 | **0.7102** | High variety across ministries in recommendation list |
| **Personalization Dissimilarity**| 24.10% | **31.63%** | Substantially distinct recommendations tailored to different citizen personas |

---

## Part 3: Step-by-Step Presentation & Demo Script (2 to 3 Minutes)

When presenting to your professors, follow this structured demo:

### Step 1: The Pitch (30 seconds)
> *"Good morning, Sir/Ma'am. Our project is **PublicHelp AI**. India has over 2,000 welfare schemes, but citizens struggle to find and understand what they qualify for. Most existing portals are simple search bars that fail when a user doesn't know the exact scheme title.
> 
> We engineered a **Hybrid Recommender System** combining **Reciprocal Rank Fusion (RRF)**, **GPU-accelerated Sentence Transformers**, **Maximal Marginal Relevance (MMR)** for diversity, and a **Deterministic Rule Engine** for zero-hallucination eligibility checking."*

### Step 2: Live Persona Demonstration (1 minute)
1. Open the **Recommendations Hub** at [http://localhost:5173/recommendations](http://localhost:5173/recommendations).
2. Click on **Ramesh Patel (44yo Marginal Farmer, Madhya Pradesh)**:
   - *"Notice how clicking this persona updates the recommendation engine in real time. The top matches immediately prioritize MP farmer income support, PM-Kisan, and Kisan Credit Card."*
   - Point to the **"Why Recommended"** box on the first card:
     - *"Notice the transparent explainability badges: 'Specifically enacted for residents of Madhya Pradesh', 'Category aligns with your interests: Agriculture, Credit', and 'Central Government scheme'."*
3. Now click on **Maya Sharma (19yo SC Female Student, UP)**:
   - *"The recommendation feed instantly shifts from agriculture to higher education scholarships, girl-child coaching assistance, and SC pre-matric/post-matric grants."*
   - Show the **Personalization Dissimilarity**: the recommendations are completely tailored to Maya's profile.

### Step 3: Complementary Benefit Bundles (30 seconds)
1. In the Recommendations Hub, click the **"Welfare Packages"** tab.
2. Show the **Kisan Samriddhi & Protection Package** and the **Girl Child & Women Empowerment Bundle**.
3. Explain:
   - *"In public policy, citizens require complementary solutions—for example, tuition fee reimbursement combined with a digital device grant. Our engine bundles these together while independently checking eligibility for each component."*

### Step 4: Content-Based Item Similarity (30 seconds)
1. Click into any scheme card to open its detail page (e.g., [http://localhost:5173/schemes/1](http://localhost:5173/schemes/1)).
2. Scroll to the bottom to the **"Similar & Alternative Schemes"** shelf.
3. Explain:
   - *"This uses item-to-item content-based filtering. We compute cosine similarities between the 384-dimensional dense embeddings of the current scheme and all other 2,066 schemes to recommend alternatives with a match percentage."*

### Step 5: Academic Evaluation Page (30 seconds)
1. Click on **ML Insights** in the top navigation bar ([http://localhost:5173/ml](http://localhost:5173/ml)).
2. Show the **RecSys Domain Metrics card**:
   - Point to **Catalog Coverage (100%)**, **Intra-List Diversity (0.7102)**, and **Personalization (31.63%)**.
   - Show the benchmark comparison table proving that **Hybrid RRF + MMR** outperforms pure TF-IDF and pure Dense retrieval across Precision@5, NDCG@5, and MRR.

---

## Part 4: Top 10 Viva Questions & Winning Answers

### Q1: Why did you build a recommender system instead of using an LLM or standard search?
> **Answer**: Standard search depends on exact keyword matching, failing when citizens use colloquial terms. LLMs, on the other hand, are probabilistic and prone to hallucination—inventing schemes or misstating eligibility limits, which is dangerous in governance. Our system combines dense sentence embeddings for semantic retrieval with a strict deterministic rule engine for guaranteed factual eligibility.

### Q2: What is Reciprocal Rank Fusion (RRF) and why is it better than a weighted sum?
> **Answer**: Weighted sum adds raw scores: $\alpha \cdot \text{Score}_{\text{dense}} + (1-\alpha) \cdot \text{Score}_{\text{tfidf}}$. However, cosine similarity scores and TF-IDF scores have completely different statistical distributions and ranges. RRF operates purely on ordinal ranks ($1 / (k + \text{rank})$), eliminating score distribution mismatch and providing more consistent, robust rankings.

### Q3: Why is Maximal Marginal Relevance (MMR) necessary here?
> **Answer**: In government catalogs, one ministry might publish 15 variations of the same loan or scholarship scheme. Without MMR, the top 10 results would be monopolized by near-duplicate schemes. MMR balances relevance against cosine similarity to already chosen results, ensuring citizens discover diverse benefits across health, education, and livelihood.

### Q4: How does your system determine eligibility?
> **Answer**: Eligibility is computed deterministically using parsed scheme criteria (state domicile, age limits, gender restrictions, caste reservations, and income ceilings). It outputs explicit tri-state classifications: `POTENTIALLY_ELIGIBLE`, `NEEDS_MORE_INFO`, and `NOT_ELIGIBLE`. Ineligible schemes are filtered out of recommendations.

### Q5: How do you measure Intra-List Diversity (ILD)?
> **Answer**: ILD is defined as the average pairwise cosine distance between all recommended items in the top-$K$ list:
> $$\text{ILD}(R) = \frac{2}{K(K-1)} \sum_{i=1}^{K} \sum_{j=i+1}^{K} (1 - \cos(\mathbf{e}_i, \mathbf{e}_j))$$
> Our system achieves an ILD of 0.7102, proving high intra-list variety.

### Q6: How do you measure Personalization?
> **Answer**: We compute the Personalization Dissimilarity across contrasting citizen profiles using Jaccard distance on top recommendations:
> $$\text{Personalization} = 1 - \text{JaccardSimilarity}(R_{u_1}, R_{u_2})$$
> Our system achieves 31.63% dissimilarity between distinct citizen segments.

### Q7: What embedding model do you use and where does it run?
> **Answer**: We use `sentence-transformers/all-MiniLM-L6-v2`, a 384-dimensional bi-encoder model. It is loaded locally and runs accelerated on our NVIDIA GeForce RTX 2050 GPU using PyTorch and CUDA, delivering sub-400ms inference with zero reliance on paid cloud APIs.

### Q8: What happens if a user leaves their income or category blank?
> **Answer**: The system does not punish the user or make assumptions. It assigns the scheme a `NEEDS_MORE_INFO` status, displays a warning pill, and highlights which documents (e.g. Income Certificate, Caste Certificate) will be required.

### Q9: What are Complementary Bundles?
> **Answer**: Complementary bundles are curated policy pathways that group related government interventions (e.g., student scholarship + hostel subsidy + free skill coaching). Unlike item similarity (which finds alternatives), bundles find synergistic combinations of different benefit types.

### Q10: What are future improvements for this project?
> **Answer**:
> 1. Multi-lingual voice search in regional Indian languages (Hindi, Tamil, Marathi, Bengali) using Whisper or Bhashini.
> 2. Digilocker / Aadhaar API integration for automated profile extraction and document pre-verification.
> 3. Collaborative filtering based on anonymized application outcomes from similar citizen demographics.

---

## Part 5: Suggested 8-Slide Presentation Deck Outline

| Slide # | Slide Title | Key Content & Bullet Points |
| :---: | :--- | :--- |
| **1** | **Title Slide** | PublicHelp AI: Hybrid Recommender System for Indian Government Schemes. Name, Roll Number, Branch, Supervisor. |
| **2** | **Motivation & Problem Statement** | 2,000+ fragmented welfare schemes; complex eligibility criteria; keyword search fails due to vocabulary mismatch. |
| **3** | **Proposed System Architecture** | Dual-channel retrieval (TF-IDF + all-MiniLM-L6-v2 GPU embeddings); RRF fusion; Deterministic eligibility engine; Vectorized MMR reranker. |
| **4** | **Deterministic Eligibility vs. ML Recommender** | Separation of hard legal rules from probabilistic relevance. Tri-state status (`POTENTIALLY_ELIGIBLE`, `NEEDS_MORE_INFO`, `NOT_ELIGIBLE`). |
| **5** | **Novel RecSys Features** | 1-Click Persona Simulator; Complementary Benefit Bundles; Content-Based Item Similarity; Transparent "Why Recommended" explainability. |
| **6** | **Experimental Evaluation & Results** | Table comparing TF-IDF, Embeddings, Hybrid RRF, and RRF + MMR. Precision@5 (+18.2%), NDCG@5 (+13.9%), MRR (+22.8%), Latency 388ms. |
| **7** | **RecSys Domain Metrics** | 100% Catalog Coverage; 0.7102 Intra-List Diversity (ILD); 31.63% Personalization Dissimilarity. |
| **8** | **Conclusion & Future Scope** | Open-source, runs 100% locally on consumer hardware (RTX 2050), ready for Bhashini multilingual voice integration and DigiLocker. |
