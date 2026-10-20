#!/usr/bin/env python3
"""
Data ingestion pipeline for PublicHelp AI.
Downloads/copies the raw dataset, cleans, deduplicates, parses eligibility fields,
and exports to SQLite + clean CSV/JSON.

Usage:
    python scripts/ingest_data.py [--raw-csv PATH]
"""

import argparse
import csv
import json
import logging
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/ingest.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("ingest")

RAW_CSV = Path("references/dataset-myscheme/gov_myscheme_data.csv")
RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
DB_PATH = Path("data/publichelp.db")

CASTE_KEYWORDS = {
    "sc": ["scheduled caste", "sc/st", "dalit"],
    "st": ["scheduled tribe", "sc/st", "tribal"],
    "obc": ["other backward", "obc"],
    "ews": ["economically weaker", "ews"],
    "general": ["general category", "unreserved"],
}

# GENDER_MAP: Use strict patterns that won't match compound words.
# Critical: \bmen\b matches "men" in "government", "department", "management"
# Solution: use negative lookbehind for common compound-word prefixes.
# We only mark a scheme as male-specific when the text explicitly targets men/boys.
# "woman/women" is reliable; "man/men" requires stricter context.
GENDER_MAP = {
    "female": [
        r"\bwom[ae]n\b",
        r"\bgirls?\b",
        r"\bfemale\b",
        r"\bmahila\b",
        r"\bwidow\b",
        r"\bbride\b",
    ],
    "male": [
        r"\bmale\b",                          # "male applicant"
        r"\bboys?\b",                          # "boy", "boys"  
        r"\bwidower\b",                        # "widower"
        r"\bfor\s+men\b",                      # "for men"
        r"\bmen\s+(?:who|above|below|aged|belonging)\b",  # "men who/above/below/aged"
    ],
}


def strip_bom(s: str) -> str:
    return s.lstrip("\ufeff").strip()


def parse_age(text: str) -> tuple[int | None, int | None]:
    """Extract min/max age from eligibility text.
    
    Returns (min_age, max_age). Both can be None if not found or unreliable.
    Ages outside 0-100 are discarded as parsing artifacts.
    """
    if not text:
        return None, None
    text = text.lower()
    patterns = [
        r"between\s+(\d+)\s+(?:to|and|-)\s+(\d+)\s+years",
        r"(\d+)\s*(?:to|-)\s*(\d+)\s+years",
        r"age\s*(?:of|:)?\s*(\d+)\s*(?:to|-)\s*(\d+)",
        r"minimum\s+age\s*(?:of|:)?\s*(\d+)",
        r"at\s+least\s+(\d+)\s+years",
        r"above\s+(\d+)\s+years",
        r"below\s+(\d+)\s+years",
        r"aged?\s+(\d+)\s+(?:to|-)\s+(\d+)",
    ]
    mn, mx = None, None
    for p in patterns:
        m = re.search(p, text)
        if m:
            groups = [int(g) for g in m.groups() if g is not None]
            if len(groups) == 2:
                a, b = min(groups), max(groups)
                if 0 < a < b <= 100:  # sanity check
                    mn, mx = a, b
            elif len(groups) == 1:
                val = groups[0]
                if 0 < val <= 100:
                    if "above" in p or "minimum" in p or "least" in p:
                        mn = val
                    elif "below" in p:
                        mx = val
            if mn is not None or mx is not None:
                break
    return mn, mx


def parse_gender(text: str) -> str | None:
    """Parse gender restriction from eligibility text.
    
    Conservative: only marks male when text explicitly targets men/boys,
    not when "men" appears in words like "government" or "management".
    Returns: "female", "male", "all", or None (unknown).
    """
    if not text:
        return None
    t = text.lower()
    found = set()
    for g, patterns in GENDER_MAP.items():
        if any(re.search(p, t) for p in patterns):
            found.add(g)
    if len(found) == 1:
        return found.pop()
    if len(found) == 0:
        return None  # unknown → needs_more_info in eligibility engine
    return "all"


def parse_income(text: str) -> int | None:
    """Extract maximum annual income ceiling in INR.
    
    Only extracts when a clear currency amount with context is present.
    Returns None when uncertain rather than a wrong number.
    """
    if not text:
        return None
    text_lower = text.lower().replace(",", "")
    # Pattern requires explicit Rs/INR/₹ OR "income" context + numeric + unit
    patterns = [
        # "annual income not exceeding Rs 2 lakh" / "income up to Rs. 2,50,000"
        r"income\s+(?:of|below|less\s+than|not\s+exceeding|up\s+to|upto|within)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|thousand|k|crore)?",
        r"(?:rs\.?|inr|₹)\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|thousand|k|crore)?\s*(?:per\s+annum|annual|yearly|p\.?a\.?)",
        r"family\s+income\s+(?:below|up\s+to|upto|not\s+exceeding)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|thousand|k)?",
    ]
    for pattern in patterns:
        m = re.search(pattern, text_lower)
        if m:
            val = float(m.group(1))
            unit = (m.group(2) or "").strip().lower()
            if unit in ("lakh", "lakhs"):
                val *= 100_000
            elif unit in ("thousand", "k"):
                val *= 1_000
            elif unit == "crore":
                val *= 10_000_000
            # Sanity check: income ceiling should be between ₹1,000 and ₹50 lakh
            if 1_000 <= val <= 50_00_000:
                return int(val)
    return None



def parse_castes(text: str) -> list[str]:
    if not text:
        return []
    t = text.lower()
    found = []
    for cat, kws in CASTE_KEYWORDS.items():
        if any(kw in t for kw in kws):
            found.append(cat.upper())
    return found


def parse_categories(text: str) -> list[str]:
    if not text:
        return []
    # handles pipe, comma, semicolon separated
    parts = re.split(r"[|,;]", text)
    return [p.strip() for p in parts if p.strip()]


def data_completeness(row: dict) -> float:
    """
    Compute a data quality / completeness score for a scheme record.
    
    Weights a mix of presence (basic fields) and structure quality (parsed fields).
    This score is designed to have discriminating power — not to give 1.0 to
    every record merely because text fields are non-empty.
    
    Components:
      - Core text fields present (name, description, benefits, eligibility): 40%
      - Application info present (process, documents): 20%  
      - Structured eligibility fields parsed (age, gender, caste, income): 30%
      - Exclusions text present: 10%
    """
    score = 0.0

    # Core text fields (10% each, max 40%)
    core_fields = ["description", "benefits", "eligibility_text", "official_link"]
    for f in core_fields:
        if str(row.get(f, "")).strip():
            score += 0.10

    # Application info (10% each, max 20%)
    for f in ["application_process", "documents_required"]:
        if str(row.get(f, "")).strip():
            score += 0.10

    # Structured eligibility parsed (max 30%)
    if row.get("parsed_min_age") or row.get("parsed_max_age"):
        score += 0.10
    if row.get("parsed_gender"):
        score += 0.10
    if row.get("parsed_caste_categories") and row["parsed_caste_categories"] not in ("[]", "", None):
        score += 0.10

    # Exclusions present (10%)
    if str(row.get("exclusions_text", "")).strip():
        score += 0.10

    return round(score, 3)



def clean_row(raw: dict, idx: int) -> dict:
    name = strip_bom(raw.get("\ufeffScheme Name", "") or raw.get("Scheme Name", ""))
    eligibility_text = raw.get("Eligibility Criteria", "")
    eligibility_general = raw.get("Eligibility (General)", "")
    combined_elig = f"{eligibility_text} {eligibility_general}"

    row = {
        "id": idx,
        "name": name,
        "slug": raw.get("Scheme Slug", "").strip(),
        "level": raw.get("Level", "").strip(),
        "state_ministry": raw.get("State / UT / Ministry", "").strip(),
        "application_mode": raw.get("Application Mode", "").strip(),
        "categories_raw": raw.get("Tags / Categories", "").strip(),
        "description": raw.get("Description", "").strip(),
        "eligibility_text": eligibility_text.strip(),
        "eligibility_general": eligibility_general.strip(),
        "exclusions_text": raw.get("Exclusions / Ineligibility", "").strip(),
        "benefits": raw.get("Benefits", "").strip(),
        "application_process": raw.get("Application Process", "").strip(),
        "documents_required": raw.get("Documents Required", "").strip(),
        "faqs": raw.get("Frequently Asked Questions (FAQs)", "").strip(),
        "official_link": raw.get("Official Link", "").strip(),
        "myscheme_url": raw.get("MyScheme URL", "").strip(),
        "source_dataset": "myscheme-v1",
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "verified": 0,
        "verification_date": None,
    }

    # Parsed fields
    mn_age, mx_age = parse_age(combined_elig)
    row["parsed_min_age"] = mn_age
    row["parsed_max_age"] = mx_age
    row["parsed_gender"] = parse_gender(combined_elig)
    row["parsed_income_max"] = parse_income(combined_elig)
    row["parsed_caste_categories"] = json.dumps(parse_castes(combined_elig))
    row["parsed_is_central"] = 1 if row["level"] == "Central Government" else 0
    row["categories_list"] = json.dumps(parse_categories(row["categories_raw"]))
    row["data_completeness_score"] = data_completeness(row)
    return row


def deduplicate(rows: list[dict]) -> tuple[list[dict], int]:
    seen_slugs = set()
    seen_names = set()
    clean = []
    dupes = 0
    for r in rows:
        slug = r["slug"].lower()
        name_norm = re.sub(r"\s+", " ", r["name"].lower().strip())
        if slug in seen_slugs or name_norm in seen_names:
            dupes += 1
            continue
        seen_slugs.add(slug)
        seen_names.add(name_norm)
        clean.append(r)
    return clean, dupes


def create_db(rows: list[dict], db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE schemes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT UNIQUE,
        level TEXT,
        state_ministry TEXT,
        application_mode TEXT,
        categories_raw TEXT,
        categories_list TEXT,
        description TEXT,
        eligibility_text TEXT,
        eligibility_general TEXT,
        exclusions_text TEXT,
        benefits TEXT,
        application_process TEXT,
        documents_required TEXT,
        faqs TEXT,
        official_link TEXT,
        myscheme_url TEXT,
        source_dataset TEXT,
        ingested_at TEXT,
        verified INTEGER DEFAULT 0,
        verification_date TEXT,
        parsed_min_age INTEGER,
        parsed_max_age INTEGER,
        parsed_gender TEXT,
        parsed_income_max INTEGER,
        parsed_caste_categories TEXT,
        parsed_is_central INTEGER DEFAULT 0,
        data_completeness_score REAL
    )
    """)
    cur.executemany(
        """INSERT INTO schemes VALUES (
            :id,:name,:slug,:level,:state_ministry,:application_mode,
            :categories_raw,:categories_list,:description,:eligibility_text,
            :eligibility_general,:exclusions_text,:benefits,:application_process,
            :documents_required,:faqs,:official_link,:myscheme_url,
            :source_dataset,:ingested_at,:verified,:verification_date,
            :parsed_min_age,:parsed_max_age,:parsed_gender,:parsed_income_max,
            :parsed_caste_categories,:parsed_is_central,:data_completeness_score
        )""",
        rows,
    )
    # Full-text search virtual table
    cur.execute("""
    CREATE VIRTUAL TABLE schemes_fts USING fts5(
        name, description, benefits, eligibility_text, categories_raw,
        state_ministry, content=schemes, content_rowid=id
    )
    """)
    cur.execute("""
    INSERT INTO schemes_fts(rowid, name, description, benefits, eligibility_text, categories_raw, state_ministry)
    SELECT id, name, description, benefits, eligibility_text, categories_raw, state_ministry FROM schemes
    """)
    conn.commit()
    conn.close()
    log.info(f"Database created at {db_path} with {len(rows)} records")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-csv", default=str(RAW_CSV))
    args = parser.parse_args()

    Path("logs").mkdir(exist_ok=True)
    raw_csv = Path(args.raw_csv)

    if not raw_csv.exists():
        log.error(f"Raw CSV not found at {raw_csv}. Clone the dataset first.")
        sys.exit(1)

    # Copy raw
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest_raw = RAW_DIR / "gov_myscheme_data.csv"
    shutil.copy(raw_csv, dest_raw)
    log.info(f"Raw data copied to {dest_raw}")

    # Read
    with open(raw_csv, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)
    log.info(f"Loaded {len(raw_rows)} raw records")

    # Clean
    cleaned = [clean_row(r, i + 1) for i, r in enumerate(raw_rows)]
    log.info(f"Cleaned {len(cleaned)} records")

    # Deduplicate
    deduped, dupes = deduplicate(cleaned)
    log.info(f"Deduplicated: {len(deduped)} unique ({dupes} duplicates removed)")

    # Export clean CSV
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    clean_csv = CLEAN_DIR / "schemes_clean.csv"
    if deduped:
        with open(clean_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(deduped[0].keys()))
            writer.writeheader()
            writer.writerows(deduped)
    log.info(f"Clean CSV exported to {clean_csv}")

    # Export JSON
    clean_json = CLEAN_DIR / "schemes_clean.json"
    with open(clean_json, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)
    log.info(f"Clean JSON exported to {clean_json}")

    # SQLite
    create_db(deduped, DB_PATH)

    # Quality report
    total = len(deduped)
    missing_elig = sum(1 for r in deduped if not r["eligibility_text"])
    missing_excl = sum(1 for r in deduped if not r["exclusions_text"])
    age_parsed = sum(1 for r in deduped if r["parsed_min_age"] or r["parsed_max_age"])
    gender_parsed = sum(1 for r in deduped if r["parsed_gender"])
    income_parsed = sum(1 for r in deduped if r["parsed_income_max"])

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": total,
        "duplicates_removed": dupes,
        "missing_eligibility_text": missing_elig,
        "missing_exclusions": missing_excl,
        "age_parsed_count": age_parsed,
        "gender_parsed_count": gender_parsed,
        "income_parsed_count": income_parsed,
        "avg_completeness": round(sum(r["data_completeness_score"] for r in deduped) / total, 3),
    }
    Path("reports").mkdir(exist_ok=True)
    with open("reports/data_quality.json", "w") as f:
        json.dump(report, f, indent=2)
    log.info(f"Data quality report: {report}")
    log.info("Ingestion complete.")


if __name__ == "__main__":
    main()
