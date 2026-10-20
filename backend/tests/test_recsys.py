"""
Tests for upgraded Recommender System functionality:
- Content-Based Item Similarity (/schemes/{id}/similar)
- Reciprocal Rank Fusion & MMR diversity
- Curated Complementary Benefit Bundles
- Citizen Persona Profiles
- Personalized Feed (/recommend/feed)
- Enhanced Eligibility Boundary & Edge Cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from backend.app.core.ml_engine import MLEngine, RankingConfig
from backend.app.core.eligibility import assess_eligibility, EligibilityStatus


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


def test_similar_schemes_endpoint(client):
    # 1421 = Pradhan Mantri Kisan Samman Nidhi
    response = client.get("/api/schemes/1421/similar?top_k=4")
    assert response.status_code == 200
    data = response.json()
    assert data["scheme_id"] == 1421
    assert data["count"] == 4
    assert len(data["results"]) == 4
    # Ensure target scheme is not in its own similar list
    assert all(r["id"] != 1421 for r in data["results"])
    # Ensure results have similarity score and match percentage
    assert all("similarity_score" in r and "match_pct" in r for r in data["results"])


def test_similar_schemes_not_found(client):
    response = client.get("/api/schemes/999999/similar")
    assert response.status_code == 404


def test_personas_endpoint(client):
    response = client.get("/api/recommend/personas")
    assert response.status_code == 200
    personas = response.json().get("personas", [])
    assert len(personas) >= 4
    # Verify persona structure
    first = personas[0]
    assert "persona_id" in first
    assert "name" in first
    assert "profile" in first
    assert "goals" in first["profile"]


def test_bundles_endpoint(client):
    response = client.get("/api/recommend/bundles?state=Uttar%20Pradesh&gender=female&age=19")
    assert response.status_code == 200
    bundles = response.json().get("bundles", [])
    assert len(bundles) >= 4
    for b in bundles:
        assert "bundle_id" in b
        assert "title" in b
        assert "schemes" in b
        assert len(b["schemes"]) > 0
        for s in b["schemes"]:
            assert "benefit_role" in s
            assert "eligibility" in s
            assert s["eligibility"]["status"] in ["potentially_eligible", "needs_more_info", "not_eligible"]


def test_recommend_feed_endpoint(client):
    payload = {
        "profile": {
            "state": "Maharashtra",
            "age": 20,
            "gender": "female",
            "caste_category": "OBC",
            "goals": ["Education", "Scholarships"],
        },
        "top_k": 6,
    }
    response = client.post("/api/recommend/feed", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "top_matches" in data
    assert len(data["top_matches"]) <= 6
    assert "bundles" in data
    assert "algorithm_info" in data
    assert "active_profile_summary" in data


def test_rrf_scoring_in_recommend(client):
    response = client.post("/api/recommend", json={"query": "kisan credit loan for agriculture", "top_k": 5, "page": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    first = data["results"][0]
    assert "why_recommended" in first
    assert len(first["why_recommended"]) > 0
    assert first["rrf_score"] is not None


def test_eligibility_boundary_cases():
    scheme = {
        "id": 999,
        "name": "Strict Boundary Scheme",
        "parsed_min_age": 21,
        "parsed_max_age": 30,
        "parsed_gender": "female",
        "parsed_income_max": 250000,
        "parsed_caste_categories": '["SC", "ST"]',
        "parsed_is_central": 0,
        "state_ministry": "Maharashtra",
        "exclusions_text": "Excludes males and corporate employees",
    }
    # Exactly at min age (21) should be eligible
    p_min = {"age": 21, "gender": "female", "annual_income": 200000, "caste_category": "SC", "state": "Maharashtra"}
    res_min = assess_eligibility(scheme, p_min)
    assert res_min.status == EligibilityStatus.POTENTIALLY_ELIGIBLE

    # Exactly at max age (30) should be eligible
    p_max = {"age": 30, "gender": "female", "annual_income": 200000, "caste_category": "SC", "state": "Maharashtra"}
    res_max = assess_eligibility(scheme, p_max)
    assert res_max.status == EligibilityStatus.POTENTIALLY_ELIGIBLE

    # 1 year below min age (20) should be NOT_ELIGIBLE
    p_below = {"age": 20, "gender": "female", "annual_income": 200000, "caste_category": "SC", "state": "Maharashtra"}
    assert assess_eligibility(scheme, p_below).status == EligibilityStatus.NOT_ELIGIBLE

    # 1 year above max age (31) should be NOT_ELIGIBLE
    p_above = {"age": 31, "gender": "female", "annual_income": 200000, "caste_category": "SC", "state": "Maharashtra"}
    assert assess_eligibility(scheme, p_above).status == EligibilityStatus.NOT_ELIGIBLE

    # Exactly at income ceiling (250000) should be eligible
    p_inc_exact = {"age": 25, "gender": "female", "annual_income": 250000, "caste_category": "SC", "state": "Maharashtra"}
    assert assess_eligibility(scheme, p_inc_exact).status == EligibilityStatus.POTENTIALLY_ELIGIBLE

    # 1 rupee above ceiling (250001) should be NOT_ELIGIBLE
    p_inc_over = {"age": 25, "gender": "female", "annual_income": 250001, "caste_category": "SC", "state": "Maharashtra"}
    assert assess_eligibility(scheme, p_inc_over).status == EligibilityStatus.NOT_ELIGIBLE
