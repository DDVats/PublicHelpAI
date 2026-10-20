# Data Dictionary — PublicHelp AI

## Source Dataset: gov_myscheme_data.csv

| Column (original) | Internal field | Type | Description | Coverage |
|---|---|---|---|---|
| Scheme Name (BOM-prefixed) | name | str | Full name of scheme | 100% |
| Scheme Slug | slug | str | URL-safe identifier | 100% |
| Level | level | str | `Central Government` or `State / UT Government` | 100% |
| State / UT / Ministry | state_ministry | str | Administering body | 100% |
| Application Mode | application_mode | str | Online / Offline / Both | 100% |
| Tags / Categories | categories | str (pipe-sep) | Comma-separated topic tags | 99.2% |
| Description | description | str | Plain-language scheme description | 100% |
| Eligibility Criteria | eligibility_text | str | Full eligibility text (raw, preserved) | 99.9% |
| Eligibility (General) | eligibility_general | str | Simplified eligibility summary | 99.9% |
| Exclusions / Ineligibility | exclusions_text | str | Who is NOT eligible | 19.4% |
| Benefits | benefits | str | Description of benefit/scheme value | 100% |
| Application Process | application_process | str | Steps to apply | 100% |
| Documents Required | documents_required | str | Required supporting documents | 99.8% |
| Frequently Asked Questions (FAQs) | faqs | str | Common questions and answers | 100% |
| Official Link | official_link | str (URL) | Link to official government page | 100% |
| MyScheme URL | myscheme_url | str (URL) | Link on myscheme.gov.in | 100% |

## Parsed/Derived Fields (added during ingestion)

| Field | Type | Description |
|---|---|---|
| id | int | Auto-increment primary key |
| source_dataset | str | Always `myscheme-v1` for this corpus |
| ingested_at | datetime | UTC timestamp of ingestion |
| verified | bool | False — not individually official-source verified |
| verification_date | date | NULL until manual review |
| data_completeness_score | float | 0–1, structural quality index (40% core text, 20% process/docs, 30% parsed eligibility, 10% exclusions) |
| parsed_min_age | int? | Extracted minimum age (381 schemes have parsed age range) |
| parsed_max_age | int? | Extracted maximum age |
| parsed_gender | str? | `male` (3 schemes), `female` (367 schemes), `all` (85 schemes), or NULL (1,611 schemes) |
| parsed_income_max | int? | Annual income ceiling in INR (79 schemes parsed) |
| parsed_caste_categories | list[str] | SC, ST, OBC, General, EWS (354 schemes parsed) |
| parsed_is_central | bool | 1 if Level = Central Government, 0 otherwise |
| categories_list | list[str] | Parsed JSON array of cleaned category tags |


## Eligibility Assessment States

| State | Code | Meaning |
|---|---|---|
| Potentially eligible | `potentially_eligible` | All checked criteria match profile |
| Possibly eligible — more info needed | `needs_more_info` | Some criteria unparseable or missing |
| Criteria not met | `not_eligible` | At least one criterion definitively fails |
