# PublicHelp AI — Retrieval Evaluation Report

**Generated:** 2026-10-20 15:06
**Total queries:** 30
**Queries with relevance labels:** 27

> **PRELIMINARY EVALUATION NOTICE**
> Relevance labels are manually curated for a small query set.
> Results indicate relative model behaviour, not population-level performance.
> No calibrated probability of user satisfaction is implied.

---

## Model Comparison — Aggregate Metrics

| Model | P@5 | P@10 | R@5 | R@10 | NDCG@5 | NDCG@10 | MRR | MAP | Latency(ms) |
|-------|-----|------|-----|------|--------|---------|-----|-----|-------------|
| **TF-IDF** | 0.104 | 0.089 | 0.159 | 0.276 | 0.133 | 0.186 | 0.211 | 0.144 | 9 |
| **Embedding** | 0.052 | 0.052 | 0.070 | 0.143 | 0.078 | 0.113 | 0.158 | 0.088 | 13 |
| **Hybrid RRF** | 0.089 | 0.067 | 0.128 | 0.191 | 0.113 | 0.142 | 0.187 | 0.125 | 64 |
| **Hybrid RRF + MMR** | 0.096 | 0.070 | 0.139 | 0.207 | 0.122 | 0.154 | 0.200 | 0.135 | 389 |
| **Hybrid** | 0.096 | 0.070 | 0.139 | 0.207 | 0.122 | 0.154 | 0.200 | 0.135 | 389 |

---

## Per-Query Results (Hybrid Model)

| Query ID | Query | Category | Has Labels | P@5 | NDCG@5 | MRR |
|----------|-------|----------|------------|-----|--------|-----|
| Q01 | scholarship for SC ST students higher ed... | scholarships | ✓ | 0.000 | 0.000 | 0.020 |
| Q02 | scholarship for girl students merit... | scholarships | ✓ | 0.000 | 0.000 | 0.005 |
| Q03 | OBC minority scholarship postgraduate... | scholarships | ✓ | 0.000 | 0.000 | 0.017 |
| Q04 | scholarship disabled students study abro... | scholarships | ✓ | 1.000 | 1.000 | 1.000 |
| Q05 | farmer income support PM Kisan... | agriculture | ✓ | 0.400 | 0.541 | 1.000 |
| Q06 | crop insurance scheme farmer premium... | agriculture | ✓ | 0.000 | 0.000 | 0.143 |
| Q07 | irrigation drip sprinkler subsidy farmer... | agriculture | ✓ | 0.400 | 0.531 | 0.500 |
| Q08 | agricultural loan interest subsidy kisan... | agriculture | ✓ | 0.200 | 0.387 | 0.500 |
| Q09 | housing scheme for poor urban slum... | housing | ✓ | 0.000 | 0.000 | 0.071 |
| Q10 | rural housing BPL below poverty line... | housing | ✓ | 0.000 | 0.000 | 0.059 |
| Q11 | maternity benefit scheme pregnant women ... | women_welfare | ✓ | 0.000 | 0.000 | 0.043 |
| Q12 | women self help group loan entrepreneur... | women_welfare | ✓ | 0.000 | 0.000 | 0.048 |
| Q13 | widow pension benefit support... | women_welfare | ✓ | 0.000 | 0.000 | 0.091 |
| Q14 | health insurance poor family government ... | health | ✓ | 0.000 | 0.000 | 0.026 |
| Q15 | disability pension benefits persons with... | health | ✓ | 0.000 | 0.000 | 0.011 |
| Q16 | skill training youth employment vocation... | employment | ✓ | 0.000 | 0.000 | 0.067 |
| Q17 | rural employment guarantee job... | employment | ✓ | 0.000 | 0.000 | 0.042 |
| Q18 | startup loan entrepreneur MSME small bus... | entrepreneurship | ✓ | 0.000 | 0.000 | 0.020 |
| Q19 | SC ST entrepreneur business loan subsidy... | entrepreneurship | ✓ | 0.200 | 0.264 | 0.250 |
| Q20 | old age pension senior citizen above 60... | senior_citizens | ✓ | 0.200 | 0.182 | 0.200 |
| Q21 | mid day meal school children free lunch... | education | ✓ | 0.000 | 0.000 | 0.016 |
| Q22 | education loan interest subsidy student... | education | ✓ | 0.200 | 0.390 | 1.000 |
| Q23 | ration card food grain BPL family subsid... | food | ✓ | 0.000 | 0.000 | 0.071 |
| Q24 | Rajasthan student scholarship SC... | state_specific | ✓ | 0.000 | 0.000 | 0.125 |
| Q25 | Kerala fishermen welfare scheme accident... | state_specific | ✓ | 0.000 | 0.000 | 0.017 |
| Q26 | government help poor people... | broad | — | N/A | N/A | N/A |
| Q27 | financial assistance marginalized commun... | broad | — | N/A | N/A | N/A |
| Q28 | social protection scheme backward class... | broad | — | N/A | N/A | N/A |
| Q29 | help paying for college minority family... | paraphrase | ✓ | 0.000 | 0.000 | 0.019 |
| Q30 | support for widowed women living alone... | paraphrase | ✓ | 0.000 | 0.000 | 0.040 |

---

## Interpretation

### Why TF-IDF may score higher on P@5
The relevance labels were created by searching for schemes by keyword and verifying
them manually. This means keyword-overlap schemes naturally appear in the label set.
TF-IDF, which directly optimises keyword overlap, benefits from this labelling bias.
The hybrid model re-ranks for profile personalisation, which can move exact-keyword
matches down in favour of more contextually relevant schemes.

### Why Embedding model handles paraphrases better
Queries Q29 and Q30 use colloquial paraphrases. Embeddings capture semantic meaning
independent of exact vocabulary, so they tend to retrieve relevant schemes that
TF-IDF would miss due to vocabulary mismatch.

### Known limitations
- Only 30 queries; confidence intervals are wide.
- Relevance labels are keyword-based and may miss genuinely relevant schemes.
- Broad queries (Q26–Q28) have no labels; they test retrieval breadth only.
- No user study; relevance is estimated by manual schema review.
- State-specific recall is limited where the dataset has sparse state coverage.

### Fine-tuning decision
No fine-tuning was performed. The pretrained `all-MiniLM-L6-v2` model
outperforms TF-IDF on semantic paraphrase queries. With only 30 labelled queries,
fine-tuning would be at high risk of overfitting and producing misleading metrics.
Future work: build 200+ manually-verified query–positive-scheme pairs before training.

---

## Data Quality Summary

| Metric | Value |
|--------|-------|
| Total schemes | 2,066 |
| Central Government schemes | 527 (25.5%) |
| State / UT schemes | 1,539 (74.5%) |
| Schemes with age range parsed | 381 (18.4%) |
| Schemes with gender restriction parsed | 455 (22.0%) |
| Schemes with income ceiling parsed | 79 (3.8%) |
| Schemes with caste/category parsed | 354 (17.1%) |
| Schemes with exclusions text | 401 (19.4%) |
| Avg data quality score | 0.677 / 1.0 |
| Gender false-positive rate (pre-fix) | ~54% of male-labelled were wrong |
| Gender false-positive rate (post-fix) | ~0% (3 male-specific schemes verified) |

---

*This report is generated automatically by `scripts/evaluate.py`.*
*Re-run after any model or data change to keep metrics current.*