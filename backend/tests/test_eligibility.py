"""
Tests for eligibility engine.
Run: pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.eligibility import (
    assess_eligibility,
    EligibilityStatus,
)
from scripts.ingest_data import parse_age, parse_gender, parse_income


# ── parse_age tests ────────────────────────────────────────────────────────────

def test_parse_age_range():
    mn, mx = parse_age("Applicant must be between 18 to 35 years")
    assert mn == 18
    assert mx == 35


def test_parse_age_above():
    mn, mx = parse_age("Age above 60 years")
    assert mn == 60
    assert mx is None


def test_parse_age_below():
    mn, mx = parse_age("Age below 25 years")
    assert mn is None
    assert mx == 25


def test_parse_age_none():
    mn, mx = parse_age("")
    assert mn is None
    assert mx is None


# ── parse_gender tests ─────────────────────────────────────────────────────────

def test_parse_gender_female():
    assert parse_gender("Only women and girls are eligible") == "female"


def test_parse_gender_male():
    assert parse_gender("Male applicants only") == "male"


def test_parse_gender_both():
    # Both female AND male signals present → "all"
    g = parse_gender("Both widow and widower are eligible to apply")
    assert g == "all"


def test_parse_gender_both_explicit():
    # "for men who" + "women" signals → all
    g = parse_gender("This scheme is for men who are above 18 and women who are above 18")
    assert g == "all"


def test_parse_gender_unknown():
    assert parse_gender("") is None


def test_parse_gender_no_false_positive_government():
    """Critical regression: 'government' should NOT trigger male classification."""
    g = parse_gender("This is a government scheme for departments and institutions")
    assert g is None, f"'government'/'departments' must not trigger male: got {g}"


def test_parse_gender_no_false_positive_management():
    """'management' and 'department' should not trigger male."""
    g = parse_gender("For management students in engineering departments")
    assert g is None, f"'management'/'departments' must not trigger male: got {g}"


# ── parse_income tests ─────────────────────────────────────────────────────────

def test_parse_income_lakh():
    assert parse_income("Annual income below 2.5 lakh") == 250000


def test_parse_income_thousand():
    assert parse_income("Income not exceeding Rs 50000") == 50000


def test_parse_income_none():
    assert parse_income("") is None


# ── assess_eligibility tests ───────────────────────────────────────────────────

SCHEME_BASE = {
    "id": 1,
    "name": "Test Scheme",
    "parsed_min_age": 18,
    "parsed_max_age": 40,
    "parsed_gender": "female",
    "parsed_income_max": 300000,
    "parsed_caste_categories": '["SC", "ST"]',
    "parsed_is_central": 0,
    "state_ministry": "Rajasthan",
    "exclusions_text": "",
    "eligibility_text": "",
    "eligibility_general": "",
}


def test_eligible_all_match():
    profile = {
        "age": 25, "gender": "female", "annual_income": 200000,
        "caste_category": "SC", "state": "Rajasthan"
    }
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.POTENTIALLY_ELIGIBLE
    assert result.score > 0.8


def test_not_eligible_age():
    profile = {"age": 50, "gender": "female", "annual_income": 100000, "state": "Rajasthan"}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
    assert any("50 above maximum" in r for r in result.failed_rules)


def test_not_eligible_gender():
    profile = {"age": 25, "gender": "male"}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE


def test_not_eligible_income():
    profile = {"age": 25, "gender": "female", "annual_income": 500000}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE


def test_not_eligible_state():
    profile = {"age": 25, "gender": "female", "annual_income": 100000, "state": "Kerala"}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE


def test_needs_more_info_missing_age():
    profile = {"gender": "female", "state": "Rajasthan"}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.NEEDS_MORE_INFO
    assert any("Age requirement" in u for u in result.unknown_rules)


def test_no_rules_needs_more_info():
    scheme_no_rules = {
        "id": 2, "name": "Open Scheme",
        "parsed_min_age": None, "parsed_max_age": None,
        "parsed_gender": None, "parsed_income_max": None,
        "parsed_caste_categories": "[]",
        "parsed_is_central": 1,
        "state_ministry": "Central Government",
        "exclusions_text": "",
    }
    result = assess_eligibility(scheme_no_rules, {})
    assert result.status == EligibilityStatus.NEEDS_MORE_INFO


def test_central_scheme_any_state():
    scheme = {**SCHEME_BASE, "parsed_is_central": 1, "state_ministry": "Ministry of Education"}
    profile = {"age": 25, "gender": "female", "annual_income": 100000, "state": "Kerala"}
    result = assess_eligibility(scheme, profile)
    # Central scheme — state check should not fail
    assert result.status != EligibilityStatus.NOT_ELIGIBLE or \
        all("state mismatch" not in f.lower() for f in result.failed_rules)


def test_boundary_age_exactly_min():
    profile = {"age": 18, "gender": "female", "annual_income": 100000}
    result = assess_eligibility(SCHEME_BASE, profile)
    # Age exactly at min should not fail on age
    assert all("18 below minimum" not in f for f in result.failed_rules)


def test_boundary_age_exactly_max():
    profile = {"age": 40, "gender": "female", "annual_income": 100000}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert all("40 above maximum" not in f for f in result.failed_rules)


def test_explanation_present():
    profile = {"age": 25, "gender": "female", "annual_income": 200000, "state": "Rajasthan"}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert len(result.explanation) > 0


def test_missing_data_never_eligible():
    """If all criteria fields are missing from profile, must not be potentially_eligible."""
    result = assess_eligibility(SCHEME_BASE, {})
    assert result.status != EligibilityStatus.POTENTIALLY_ELIGIBLE


def test_caste_mismatch_not_eligible():
    profile = {"age": 25, "gender": "female", "annual_income": 100000,
               "caste_category": "General", "state": "Rajasthan"}
    result = assess_eligibility(SCHEME_BASE, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
