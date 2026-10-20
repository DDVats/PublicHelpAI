# PublicHelp AI — Experiment Design & Scientific Methodology

## 1. Research Question & Hypothesis

### Primary Research Question:
> *Does a hybrid retrieval architecture combining lexical matching (TF-IDF), dense semantic embeddings (`all-MiniLM-L6-v2`), and deterministic eligibility filtering outperform pure keyword search for Indian government scheme discovery?*

### Formal Hypotheses:
- **$H_{0}$ (Null Hypothesis):** Combining semantic embeddings and demographic re-ranking does not improve user-centric discovery over standard lexical keyword matching.
- **$H_{1}$ (Alternative Hypothesis):** Dense embeddings handle vocabulary mismatch (paraphrases, colloquial descriptions), while deterministic eligibility rules prevent disqualifying recommendations, yielding higher contextual utility despite lower keyword overlap.

---

## 2. Experimental Setup

### Corpus:
- **Collection:** 2,066 Indian central and state/UT schemes from `data/publichelp.db`.
- **Indexed Fields:** Name, description, benefits, eligibility criteria, categories, state/ministry.

### Models Evaluated:
1. **Model A — TF-IDF Baseline:**
   - Preprocessing: Word + bigram n-grams (`ngram_range=(1,2)`), sublinear term frequency scaling.
   - Similarity: Cosine distance against sparse 30,000-dimensional matrix.
2. **Model B — Dense Semantic Baseline:**
   - Pretrained `sentence-transformers/all-MiniLM-L6-v2`.
   - Embeddings: L2-normalized 384-dimensional dense vectors; cosine dot product.
3. **Model C — Hybrid Fused Ranking:**
   - $S_{\text{semantic}} = 0.6 \cdot S_{\text{emb}} + 0.4 \cdot S_{\text{tfidf}}$
   - $S_{\text{hybrid}} = 0.35 \cdot S_{\text{semantic}} + 0.25 \cdot S_{\text{profile}} + 0.20 \cdot S_{\text{state}} + 0.10 \cdot S_{\text{cat}} + 0.10 \cdot S_{\text{comp}}$
   - Gating: Hard exclusion of `not_eligible` candidates prior to sorting.

---

## 3. Evaluation Metrics

For each query $q$ with relevant ground-truth set $R_q$ and ranked list $\hat{R}_q$:

1. **Precision@K:**
   $$\text{P@K} = \frac{|\hat{R}_q[:K] \cap R_q|}{K}$$
2. **Recall@K:**
   $$\text{R@K} = \frac{|\hat{R}_q[:K] \cap R_q|}{|R_q|}$$
3. **Discounted Cumulative Gain (DCG@K) & NDCG@K:**
   $$\text{DCG@K} = \sum_{i=1}^K \frac{\mathbb{I}(\hat{r}_i \in R_q)}{\log_2(i + 1)}$$
   $$\text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$
4. **Mean Reciprocal Rank (MRR):**
   $$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$
5. **Mean Average Precision (MAP):**
   $$\text{MAP} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \text{AP}(q)$$

---

## 4. Benchmark Query Suite

The evaluation suite comprises **30 diverse information needs**:
- 4 Scholarship queries (SC/ST, Merit Girls, OBC, Disability Abroad)
- 4 Agriculture queries (Income support, Crop insurance, Irrigation, Credit card)
- 2 Housing queries (Urban slum, Rural poverty)
- 3 Women & Child Welfare queries (Maternity, Self-help groups, Widow pensions)
- 2 Health & Disability queries (Ayushman hospital assurance, Assistive equipment)
- 2 Employment & Skill queries (Youth vocational, MGNREGA)
- 2 Enterprise queries (Mudra MSME, Affirmative entrepreneurship)
- 1 Senior Citizen query (Old age pension)
- 2 Education loan & Nutrition queries (Midday meals, Student loan interest)
- 1 Food security query (Garib Kalyan Anna Yojana)
- 2 State-specific queries (Rajasthan SC, Kerala marine fisheries)
- 3 Broad exploratory queries (General welfare help)
- 2 Colloquial paraphrase queries (Non-technical vocabulary)

---

## 5. Fine-Tuning Decision Rationale

### Scientific Gate:
Fine-tuning a neural retrieval model requires substantial pairs of $(q, d^+)$ where $d^+$ is genuinely relevant and not merely a lexical neighbor. Training on small (<100) unverified synthetic pairs creates high risks of:
1. **Catastrophic Forgetting:** Degrading the model's general linguistic representations.
2. **Evaluation Leakage:** Overfitting to the test query vocabulary.

### Conclusion:
In this phase, **pre-trained `all-MiniLM-L6-v2` is maintained for production**, while the full fine-tuning architecture is packaged inside `notebooks/PublicHelp_AI_Research_Training.ipynb` with GPU support for further exploration when larger annotated datasets become available.
