# Demo Script — PublicHelp AI
## 3–5 Minute Live Presentation

---

## Setup checklist (before demo)

```bash
# Terminal 1 — Backend
cd ~/Downloads/government
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd ~/Downloads/government/frontend
npm run dev

# Browser: open http://localhost:5173
```

---

## Minute 1 — Introduction (talk track)

> "PublicHelp AI is an explainable government scheme navigator.
> It uses a hybrid AI system — keyword TF-IDF plus sentence-transformer embeddings
> plus structured eligibility rules — to match user profiles to relevant schemes
> from a corpus of 2,066 real records from myscheme.gov.in.
> Every result shows an explicit eligibility explanation, not just a score."

**Show:** Landing page hero, live stats bar (2,066 schemes, central vs state breakdown).

---

## Minute 2 — Demo profile + search

**Action:** Click "Find Schemes" → Profile form appears

**Load demo profile:** Click **"Priya — Student (SC, Rajasthan)"**

*This sets: state=Rajasthan, age=20, gender=female, caste=SC, income=₹1,50,000, rural=true*

**Search query:** `scholarship for girls education`

**Point out on results:**
- Green "Potentially Eligible" badges on schemes that match all parsed criteria
- Amber "More Info Needed" on schemes with unparseable rules
- Click the eligibility badge → expands to show: matched rules, unknown rules
- Ranking score visible (35% semantic + 25% profile + 20% state…)

---

## Minute 3 — Scheme detail

**Action:** Click any scheme → Detail page

**Point out:**
- Full eligibility criteria (raw text preserved)
- Exclusions section (if present)
- Benefits / Documents Required / Application Process
- Official link → myscheme.gov.in (real government page)
- Data freshness: "Ingested 2026-10-16 — not individually verified"
- Disclaimer at bottom

---

## Minute 4 — QA mode + Compare

**QA mode:**
- Switch to "Ask a Question"
- Type: `What documents are needed for Pradhan Mantri Awas Yojana?`
- Show: extractive snippet quoted from scheme record + official link
- Show disclaimer note: "Always verify with official source"

**Compare:**
- Go back to search results
- Click GitCompare icon on 2–3 schemes
- Click "Compare" bar → side-by-side table with eligibility badges

---

## Minute 5 — ML evaluation & scientific defense

**ML & Data page (/ml):**
- Show live dataset volume (2,066 total schemes, 527 central, 1,539 state).
- Show both engines loaded in memory: "all-MiniLM-L6-v2: Active" and "TF-IDF: Active".
- Show the 5-component ranking weights formula.
- **Evaluation Table (Live, dynamic from reports/model_comparison.json):**
  - Point to the 30-query benchmark across 8 civic domains.
  - Explain why TF-IDF has higher keyword overlap P@5 while Embeddings and Hybrid handle paraphrases and personalized profile utility.
- Bar chart: top 10 states by scheme count (Puducherry, Gujarat, Goa, Rajasthan).
- Data quality table: 100% name/description/benefits coverage, 18.4% age parsed, 22.0% gender parsed, 3.8% income parsed.

**Professor Defense Talk Track:**
> "Rather than using an opaque black-box LLM, we architected a transparent 3-layer system:
> 1. Hard deterministic eligibility filtering (excluding disqualified applicants before ranking).
> 2. Dense semantic embeddings (`all-MiniLM-L6-v2`) combined with sparse TF-IDF.
> 3. Profile-aware demographic and geographic re-ranking.
> All metrics on the ML page are computed dynamically from `reports/model_comparison.json` over 30 verified test queries. The application runs entirely on our Fedora laptop CPU without external API dependencies."


---

## Example search queries to use live

| Query | Demo profile |
|---|---|
| `scholarship for SC ST students` | Priya (SC, Rajasthan, student) |
| `old age pension senior citizen` | Suresh (68, ST, Kerala) |
| `farmer crop insurance` | Ramesh (OBC, Gujarat, farmer) |
| `women entrepreneurship loan` | Meena (General, Delhi, self-employed) |
| `housing scheme for poor` | Any rural profile |
| `free medical treatment BPL` | Low income profile |
| `maternity benefit scheme` | Female profile |
| `disability pension handicapped` | No specific profile |

---

## Closing statement

> "PublicHelp AI demonstrates a working end-to-end AI/ML pipeline:
> real data ingestion, structured eligibility rules, hybrid semantic retrieval,
> explainable ranking, and a professional UI — all running locally, no paid APIs.
> The system is clearly labelled as an independent informational tool,
> with all limitations documented."
