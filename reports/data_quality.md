# PublicHelp AI — Data Quality Report

**Generated:** 2026-10-19 17:30
**Source:** myscheme.gov.in (via GitHub dataset Aryan-Pardeshi/gov-myscheme-dataset)

## Record Counts

| Metric | Value |
|--------|-------|
| Total records | 2,066 |
| Duplicates removed | 0 |
| Central Government schemes | 527 |
| State / UT schemes | 1,539 |
| States / UTs represented | 36 |

## Field Completeness

| Field | Present | % |
|-------|---------|---|
| Name | 2066 | 100.0% |
| Description | 2066 | 100.0% |
| Benefits | 2066 | 100.0% |
| Eligibility text | 2065 | 100.0% |
| Eligibility general | 2064 | 99.9% |
| Exclusions / Ineligibility | 401 | 19.4% |
| Documents required | 2062 | 99.8% |
| Application process | 2066 | 100.0% |
| Official link | 2066 | 100.0% |
| MyScheme URL | 2066 | 100.0% |

## Eligibility Field Parsing

| Parsed Field | Count | % | Notes |
|-------------|-------|---|-------|
| Age range | 381 | 18.4% | Min and/or max age extracted from text |
| Gender restriction | 455 | 22.0% | After fix: 367 female, 3 male, 85 all |
| Income ceiling | 79 | 3.8% | After fix: values with Rs/lakh/thousand units |
| Caste/category | 354 | 17.1% | SC, ST, OBC, EWS, or General |

> **Gender parsing fix:** The original implementation matched `\bmen\b` which
> appeared in 'government', 'department', 'management' etc., creating 1,112 false
> male classifications. The fix uses stricter patterns: `\bmale\b`, `\bboys?\b`,
> `\bwidower\b`, `\bfor\s+men\b`, `\bmen\s+who|above|below|aged\b`.
> Post-fix: 3 male-specific, 367 female-specific (verified correct).

## Data Quality Scores

The completeness score now reflects structural richness:

| Score Range | Count | Description |
|------------|-------|-------------|
| 1.0 | 6 | Full text + all eligibility fields parsed |
| 0.8–0.9 | 348 | Text complete + partial eligibility parsing |
| 0.6–0.7 | 1710 | Text complete, minimal eligibility structure |
| 0.5 | 2 | Missing some text fields |

## Known Limitations

1. **Dataset version:** The dataset was retrieved from GitHub; the exact scraping
   date is not included in the CSV. Scheme details may have changed.
2. **Unverified official links:** All 2,066 records have official_link URLs but
   none have been individually verified as currently active and correct.
3. **Income data is sparse (3.8%):** Most schemes do not include parseable income
   thresholds in free-form text. Income-based filtering is unreliable.
4. **Eligibility text is unstructured:** 80.6% of schemes lack exclusion details.
5. **No scheme status/expiry dates:** The dataset does not include whether a
   scheme is currently active or discontinued.

## Licence and Attribution

- Source dataset: [Aryan-Pardeshi/gov-myscheme-dataset](https://github.com/Aryan-Pardeshi/gov-myscheme-dataset)
- Upstream source: myscheme.gov.in (Government of India)
- Dataset licence: Not specified in repository (public domain government data)
- PublicHelp AI is an independent informational tool and NOT an official government service.