#!/usr/bin/env python3
"""
Validate dataset quality and report issues.
Usage: python scripts/validate_data.py
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/publichelp.db")


def main():
    if not DB_PATH.exists():
        print("ERROR: Database not found. Run ingest_data.py first.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    schemes = [dict(r) for r in conn.execute("SELECT * FROM schemes")]
    conn.close()

    total = len(schemes)
    issues = []
    url_pattern = re.compile(r"^https?://")

    stats = {
        "total": total,
        "missing_name": 0,
        "missing_description": 0,
        "missing_eligibility": 0,
        "missing_benefits": 0,
        "missing_official_link": 0,
        "invalid_official_link": 0,
        "missing_documents": 0,
        "age_parsed": 0,
        "gender_parsed": 0,
        "income_parsed": 0,
        "caste_parsed": 0,
        "exclusions_present": 0,
        "empty_categories": 0,
        "low_completeness": 0,
    }

    for s in schemes:
        if not s["name"]:
            stats["missing_name"] += 1
            issues.append({"id": s["id"], "issue": "missing_name"})
        if not s["description"]:
            stats["missing_description"] += 1
        if not s["eligibility_text"]:
            stats["missing_eligibility"] += 1
        if not s["benefits"]:
            stats["missing_benefits"] += 1
        link = s.get("official_link", "")
        if not link:
            stats["missing_official_link"] += 1
        elif not url_pattern.match(link):
            stats["invalid_official_link"] += 1
            issues.append({"id": s["id"], "issue": "invalid_url", "url": link})
        if not s["documents_required"]:
            stats["missing_documents"] += 1
        if s["parsed_min_age"] or s["parsed_max_age"]:
            stats["age_parsed"] += 1
        if s["parsed_gender"]:
            stats["gender_parsed"] += 1
        if s["parsed_income_max"]:
            stats["income_parsed"] += 1
        if s["parsed_caste_categories"] and s["parsed_caste_categories"] != "[]":
            stats["caste_parsed"] += 1
        if s["exclusions_text"]:
            stats["exclusions_present"] += 1
        if not s["categories_raw"]:
            stats["empty_categories"] += 1
        if s["data_completeness_score"] < 0.7:
            stats["low_completeness"] += 1

    pct = lambda n: f"{n} ({100*n/total:.1f}%)"
    report = {
        "total_records": total,
        "missing_name": pct(stats["missing_name"]),
        "missing_description": pct(stats["missing_description"]),
        "missing_eligibility_text": pct(stats["missing_eligibility"]),
        "missing_benefits": pct(stats["missing_benefits"]),
        "missing_official_link": pct(stats["missing_official_link"]),
        "invalid_official_link_format": pct(stats["invalid_official_link"]),
        "missing_documents_required": pct(stats["missing_documents"]),
        "age_range_parsed": pct(stats["age_parsed"]),
        "gender_parsed": pct(stats["gender_parsed"]),
        "income_ceiling_parsed": pct(stats["income_parsed"]),
        "caste_category_parsed": pct(stats["caste_parsed"]),
        "has_exclusions": pct(stats["exclusions_present"]),
        "empty_categories": pct(stats["empty_categories"]),
        "low_completeness_under_70pct": pct(stats["low_completeness"]),
        "sample_issues": issues[:20],
    }

    Path("reports").mkdir(exist_ok=True)
    out_path = Path("reports/validation_report.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nValidation report saved to {out_path}")

    # Exit with error if critical issues
    if stats["missing_name"] > 0:
        print("CRITICAL: schemes with missing names found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
