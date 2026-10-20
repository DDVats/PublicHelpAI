"""
Tests for data ingestion pipeline and schema.
"""
import csv
import json
import sys
import sqlite3
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.ingest_data import (
    clean_row, deduplicate, data_completeness, parse_age, parse_income,
    parse_castes, parse_categories
)


SAMPLE_RAW = {
    "\ufeffScheme Name": "Test Scheme",
    "Scheme Slug": "test-scheme",
    "Level": "Central Government",
    "State / UT / Ministry": "Ministry of Education",
    "Application Mode": "Online",
    "Tags / Categories": "Education|Scholarship",
    "Description": "A test scheme for students.",
    "Eligibility Criteria": "Age between 18 to 25 years. Annual income below 2 lakh.",
    "Eligibility (General)": "Female students from SC/ST category.",
    "Exclusions / Ineligibility": "",
    "Benefits": "Rs 10000 per year",
    "Application Process": "Apply online at official portal.",
    "Documents Required": "Aadhaar, Marksheet",
    "Frequently Asked Questions (FAQs)": "Q: Who can apply? A: Students.",
    "Official Link": "https://scholarships.gov.in/",
    "MyScheme URL": "https://www.myscheme.gov.in/schemes/test-scheme",
}


def test_clean_row_basic():
    row = clean_row(SAMPLE_RAW, 1)
    assert row["name"] == "Test Scheme"
    assert row["slug"] == "test-scheme"
    assert row["level"] == "Central Government"
    assert row["id"] == 1
    assert row["source_dataset"] == "myscheme-v1"


def test_clean_row_parsed_age():
    row = clean_row(SAMPLE_RAW, 1)
    assert row["parsed_min_age"] == 18
    assert row["parsed_max_age"] == 25


def test_clean_row_parsed_income():
    row = clean_row(SAMPLE_RAW, 1)
    assert row["parsed_income_max"] == 200000


def test_clean_row_parsed_gender():
    row = clean_row(SAMPLE_RAW, 1)
    assert row["parsed_gender"] == "female"


def test_clean_row_parsed_caste():
    row = clean_row(SAMPLE_RAW, 1)
    cats = json.loads(row["parsed_caste_categories"])
    assert "SC" in cats
    assert "ST" in cats


def test_clean_row_is_central():
    row = clean_row(SAMPLE_RAW, 1)
    assert row["parsed_is_central"] == 1


def test_clean_row_completeness():
    row = clean_row(SAMPLE_RAW, 1)
    assert 0.0 <= row["data_completeness_score"] <= 1.0
    assert row["data_completeness_score"] > 0.8  # all key fields present


def test_clean_row_categories():
    row = clean_row(SAMPLE_RAW, 1)
    cats = json.loads(row["categories_list"])
    assert "Education" in cats
    assert "Scholarship" in cats


def test_deduplication_removes_dupes():
    row1 = clean_row(SAMPLE_RAW, 1)
    row2 = clean_row(SAMPLE_RAW, 2)  # same slug/name
    deduped, n_dupes = deduplicate([row1, row2])
    assert len(deduped) == 1
    assert n_dupes == 1


def test_deduplication_keeps_unique():
    row1 = clean_row(SAMPLE_RAW, 1)
    raw2 = {**SAMPLE_RAW, "\ufeffScheme Name": "Different Scheme", "Scheme Slug": "different-scheme"}
    row2 = clean_row(raw2, 2)
    deduped, n_dupes = deduplicate([row1, row2])
    assert len(deduped) == 2
    assert n_dupes == 0


def test_completeness_missing_fields():
    raw_missing = {**SAMPLE_RAW, "Benefits": "", "Description": ""}
    row = {"name": "T", "description": "", "benefits": "",
           "eligibility_text": "x", "official_link": "http://x.com",
           "application_process": "x", "documents_required": "x"}
    score = data_completeness(row)
    assert score < 1.0


def test_parse_categories_pipe_separated():
    cats = parse_categories("Health|Agriculture|Women")
    assert "Health" in cats
    assert "Agriculture" in cats
    assert "Women" in cats


def test_parse_categories_empty():
    cats = parse_categories("")
    assert cats == []


def test_real_dataset_loads():
    """Smoke test: real CSV must be present and readable."""
    csv_path = Path("references/dataset-myscheme/gov_myscheme_data.csv")
    if not csv_path.exists():
        pytest.skip("Real dataset not available")
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) > 2000, f"Expected >2000 records, got {len(rows)}"


def test_real_dataset_no_missing_names():
    csv_path = Path("references/dataset-myscheme/gov_myscheme_data.csv")
    if not csv_path.exists():
        pytest.skip("Real dataset not available")
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    name_field = "Scheme Name"  # utf-8-sig strips BOM from first field
    missing = [r for r in rows if not r.get(name_field, "").strip()]
    assert len(missing) == 0, f"{len(missing)} rows have missing scheme names"
