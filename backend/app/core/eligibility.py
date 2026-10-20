"""
Eligibility Engine — rule-based eligibility assessment.
Conservative: missing data → needs_more_info, never potentially_eligible.
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EligibilityStatus(str, Enum):
    POTENTIALLY_ELIGIBLE = "potentially_eligible"
    NEEDS_MORE_INFO = "needs_more_info"
    NOT_ELIGIBLE = "not_eligible"


@dataclass
class EligibilityResult:
    status: EligibilityStatus
    score: float  # 0-1 where 1 = all rules matched
    matched_rules: list[str] = field(default_factory=list)
    failed_rules: list[str] = field(default_factory=list)
    unknown_rules: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "score": self.score,
            "matched_rules": self.matched_rules,
            "failed_rules": self.failed_rules,
            "unknown_rules": self.unknown_rules,
            "explanation": self.explanation,
        }


def _parse_caste_list(raw: str) -> list[str]:
    try:
        lst = json.loads(raw)
        return [c.upper() for c in lst]
    except Exception:
        return []


CASTE_NORM = {
    "sc": "SC", "scheduled caste": "SC", "dalit": "SC",
    "st": "ST", "scheduled tribe": "ST", "tribal": "ST",
    "obc": "OBC", "other backward class": "OBC", "other backward": "OBC",
    "ews": "EWS", "economically weaker": "EWS",
    "general": "General", "unreserved": "General",
    "all": "all",
}

STATE_NORM = {s.lower(): s for s in [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli",
    "Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep",
    "Puducherry",
]}


def normalize_caste(raw: str) -> str | None:
    if not raw:
        return None
    return CASTE_NORM.get(raw.lower().strip())


def normalize_state(raw: str) -> str | None:
    if not raw:
        return None
    return STATE_NORM.get(raw.lower().strip(), raw.strip())


def assess_eligibility(scheme: dict, profile: dict) -> EligibilityResult:
    """
    Assess eligibility of a user profile against a scheme.

    profile keys (all optional):
        age: int
        gender: str  (male|female|other)
        state: str
        caste_category: str  (SC|ST|OBC|EWS|General)
        annual_income: int  (INR)
        is_rural: bool
        education: str
        occupation: str
    """
    matched = []
    failed = []
    unknown = []

    # --- Age check ---
    min_age = scheme.get("parsed_min_age")
    max_age = scheme.get("parsed_max_age")
    user_age = profile.get("age")

    if min_age is not None or max_age is not None:
        if user_age is None:
            unknown.append(f"Age requirement ({min_age}–{max_age}) — age not provided")
        else:
            if min_age is not None and user_age < min_age:
                failed.append(f"Age {user_age} below minimum {min_age}")
            elif max_age is not None and user_age > max_age:
                failed.append(f"Age {user_age} above maximum {max_age}")
            else:
                lbl = []
                if min_age: lbl.append(f"≥{min_age}")
                if max_age: lbl.append(f"≤{max_age}")
                matched.append(f"Age {user_age} meets requirement ({', '.join(lbl)})")

    # --- Gender check ---
    scheme_gender = scheme.get("parsed_gender")
    user_gender = profile.get("gender", "").lower()
    if scheme_gender and scheme_gender != "all":
        if not user_gender:
            unknown.append(f"Gender requirement ({scheme_gender}) — gender not provided")
        elif user_gender != scheme_gender and user_gender != "other":
            failed.append(f"Gender mismatch: scheme requires {scheme_gender}, profile is {user_gender}")
        else:
            matched.append(f"Gender '{user_gender}' matches scheme requirement '{scheme_gender}'")

    # --- Income check ---
    income_max = scheme.get("parsed_income_max")
    user_income = profile.get("annual_income")
    if income_max is not None:
        if user_income is None:
            unknown.append(f"Income ceiling ≤₹{income_max:,} — income not provided")
        elif user_income > income_max:
            failed.append(f"Income ₹{user_income:,} exceeds ceiling ₹{income_max:,}")
        else:
            matched.append(f"Income ₹{user_income:,} within ceiling ₹{income_max:,}")

    # --- State/UT check ---
    scheme_is_central = bool(scheme.get("parsed_is_central"))
    scheme_state = scheme.get("state_ministry", "")
    user_state = profile.get("state", "")
    if not scheme_is_central and scheme_state:
        if not user_state:
            unknown.append(f"State-specific scheme ({scheme_state}) — user state not provided")
        else:
            user_state_norm = normalize_state(user_state) or user_state
            if user_state_norm.lower() not in scheme_state.lower() and scheme_state.lower() not in user_state_norm.lower():
                failed.append(f"State mismatch: scheme is for {scheme_state}, user is in {user_state_norm}")
            else:
                matched.append(f"State match: {user_state_norm} / {scheme_state}")

    # --- Caste/category check ---
    caste_list = _parse_caste_list(scheme.get("parsed_caste_categories", "[]"))
    user_caste = normalize_caste(profile.get("caste_category", ""))
    if caste_list:
        if not user_caste:
            unknown.append(f"Caste/category requirement ({', '.join(caste_list)}) — not provided")
        elif user_caste not in caste_list and "all" not in [c.lower() for c in caste_list]:
            failed.append(f"Category '{user_caste}' not in eligible list {caste_list}")
        else:
            matched.append(f"Category '{user_caste}' is eligible")

    # --- Exclusions text check (keyword) ---
    exclusions = scheme.get("exclusions_text", "")
    if exclusions and user_gender:
        # Basic exclusion: if scheme excludes user's gender by name
        if user_gender == "male" and re.search(r"\bmale\b.*\bexclud", exclusions, re.I):
            failed.append("Exclusion: males explicitly excluded")
        if user_gender == "female" and re.search(r"\bfemale\b.*\bexclud", exclusions, re.I):
            failed.append("Exclusion: females explicitly excluded")

    # --- Compute result ---
    if failed:
        status = EligibilityStatus.NOT_ELIGIBLE
        score = 0.0
    elif unknown:
        status = EligibilityStatus.NEEDS_MORE_INFO
        total_checks = len(matched) + len(unknown)
        score = len(matched) / total_checks if total_checks else 0.5
    elif matched:
        status = EligibilityStatus.POTENTIALLY_ELIGIBLE
        score = 1.0
    else:
        # No structured rules available — conservative
        status = EligibilityStatus.NEEDS_MORE_INFO
        score = 0.5
        unknown.append("No structured eligibility rules could be extracted — check official source")

    # Human-readable explanation
    parts = []
    if matched:
        parts.append("✓ Matched: " + "; ".join(matched))
    if failed:
        parts.append("✗ Not met: " + "; ".join(failed))
    if unknown:
        parts.append("? Unknown: " + "; ".join(unknown))
    explanation = " | ".join(parts) or "No structured eligibility data available."

    return EligibilityResult(
        status=status,
        score=round(score, 3),
        matched_rules=matched,
        failed_rules=failed,
        unknown_rules=unknown,
        explanation=explanation,
    )
