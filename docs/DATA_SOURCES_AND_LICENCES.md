# Data Sources and Licences — PublicHelp AI

## 1. Primary Dataset

**Name**: gov-myscheme-dataset  
**Author**: Aryan Pardeshi  
**URL**: https://github.com/Aryan-Pardeshi/gov-myscheme-dataset  
**Data source**: MyScheme portal (myscheme.gov.in), Government of India  
**Licence**: No explicit licence in repository (README does not specify).  
**Attribution action**: Dataset credited in all documentation and UI footer. Not redistributed; fetched at build time only. Official links retained in records.  
**Records**: 2,066 schemes as of ingestion date  
**Ingestion date**: 2026-10-16  
**Last verified**: Not individually verified against official pages (blocking official portal automation — see below)

## 2. Official Portal Reference

**Name**: MyScheme — National Scheme Discovery Portal  
**URL**: https://www.myscheme.gov.in/  
**Operator**: Ministry of Electronics and Information Technology (MeitY), Government of India  
**Access**: Public; automated scraping not attempted out of respect for ToS and robots.txt  
**Role**: All Official Links in the dataset point to this portal or linked official pages. Used as reference only.

## 3. National Scholarship Portal

**URL**: https://scholarships.gov.in/  
**Role**: Reference for scholarship-related scheme validation  
**Access**: Public; no automated access attempted

## 4. Reference Repositories (Not redistributed)

| Repository | URL | Use |
|---|---|---|
| SchemeConnect-AI | https://github.com/NandiniSrivastava/SchemeConnect-AI | Pattern reference for TF-IDF pipeline |
| YojanaSetu | https://github.com/divisayscode/YojanaSetu-Government-Scheme-Recommendation-System | Pattern reference for semantic retrieval |

## 5. ML Models

| Model | Source | Licence | Use |
|---|---|---|---|
| all-MiniLM-L6-v2 | HuggingFace (sentence-transformers) | Apache 2.0 | Semantic embeddings |
| scikit-learn TF-IDF | scikit-learn | BSD-3-Clause | Keyword baseline |

## 6. Limitations and Disclaimers

- **No individual scheme has been manually verified** against its official page. Scheme information is sourced from the public dataset and may be outdated.
- Official portal rate limits and ToS prevented automated freshness checks.
- Eligibility criteria parsed programmatically from free text — may contain errors.
- PublicHelp AI is an **independent informational tool**, not affiliated with or endorsed by the Government of India.
- All scheme details should be confirmed at the official link before applying.
