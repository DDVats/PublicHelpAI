"""
API endpoint integration tests.
"""
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_stats(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_schemes" in data
    assert data["total_schemes"] > 0


def test_filters(client):
    r = client.get("/api/filters")
    assert r.status_code == 200
    data = r.json()
    assert "states" in data
    assert "categories" in data
    assert len(data["states"]) > 0


def test_list_schemes_pagination(client):
    r = client.get("/api/schemes?page=1&page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) <= 10
    assert data["total"] > 0


def test_list_schemes_filter_state(client):
    r = client.get("/api/schemes?state=Rajasthan")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0


def test_get_scheme_by_id(client):
    r = client.get("/api/schemes/1")
    assert r.status_code == 200
    data = r.json()
    assert "name" in data
    assert "official_link" in data


def test_get_scheme_not_found(client):
    r = client.get("/api/schemes/999999")
    assert r.status_code == 404


def test_recommend_basic(client):
    payload = {"query": "scholarship for students", "top_k": 5}
    r = client.post("/api/recommend", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) > 0
    assert data["results"][0]["ranking_score"] >= 0


def test_recommend_empty_query_profile_only_mode(client):
    """Empty query with profile should return profile-ranked results (not a validation error)."""
    payload = {
        "query": "",
        "profile": {"state": "Gujarat", "gender": "female", "age": 25},
        "top_k": 10,
    }
    r = client.post("/api/recommend", json=payload)
    assert r.status_code == 200
    data = r.json()
    # Should return results even without a query
    assert data["total"] > 0
    assert len(data["results"]) > 0
    assert data["model_used"] == "Profile-based ranking"


def test_recommend_empty_query_no_profile(client):
    """Empty query with no profile should still return results (all schemes ranked by completeness)."""
    r = client.post("/api/recommend", json={"query": "", "top_k": 10})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0


def test_recommend_with_profile(client):
    payload = {
        "query": "scholarship for women",
        "profile": {"gender": "female", "age": 22, "state": "Rajasthan"},
        "top_k": 10,
    }
    r = client.post("/api/recommend", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) > 0
    # Check eligibility info present
    first = data["results"][0]
    assert "eligibility" in first
    assert first["eligibility"]["status"] in [
        "potentially_eligible", "needs_more_info", "not_eligible"
    ]


def test_recommend_profile_changes_ranking(client):
    """Changing profile (state) should affect ranking."""
    query = "agriculture support scheme"
    r1 = client.post("/api/recommend", json={"query": query, "profile": {"state": "Rajasthan"}, "top_k": 20})
    r2 = client.post("/api/recommend", json={"query": query, "profile": {"state": "Kerala"}, "top_k": 20})
    assert r1.status_code == 200
    assert r2.status_code == 200
    ids1 = [x["id"] for x in r1.json()["results"]]
    ids2 = [x["id"] for x in r2.json()["results"]]
    # The ranking should differ when state differs
    assert ids1 != ids2, "State change should affect ranking"


def test_recommend_gender_exclusion_works(client):
    """Female-only schemes should be excluded for male users."""
    # Get all results for female user
    rf = client.post("/api/recommend", json={
        "query": "women welfare scheme",
        "profile": {"gender": "female"},
        "top_k": 50
    })
    # Get all results for male user
    rm = client.post("/api/recommend", json={
        "query": "women welfare scheme",
        "profile": {"gender": "male"},
        "top_k": 50
    })
    assert rf.status_code == 200
    assert rm.status_code == 200
    # Male results should not include schemes explicitly for female only
    male_results = rm.json()["results"]
    for scheme in male_results:
        assert scheme["eligibility"]["status"] != "not_eligible", \
            f"NOT_ELIGIBLE schemes should be filtered out, got: {scheme['name']}"


def test_recommend_explanation_present(client):
    payload = {
        "query": "women entrepreneurship loan",
        "profile": {"gender": "female", "age": 30},
        "top_k": 5,
    }
    r = client.post("/api/recommend", json=payload)
    assert r.status_code == 200
    for scheme in r.json()["results"]:
        assert "eligibility" in scheme
        assert "explanation" in scheme["eligibility"]
        assert len(scheme["eligibility"]["explanation"]) > 0


def test_recommend_ranking_stability(client):
    """Same query twice should produce identical results (deterministic)."""
    payload = {"query": "farmer subsidy", "top_k": 10}
    r1 = client.post("/api/recommend", json=payload)
    r2 = client.post("/api/recommend", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    ids1 = [x["id"] for x in r1.json()["results"]]
    ids2 = [x["id"] for x in r2.json()["results"]]
    assert ids1 == ids2, "Ranking should be deterministic"


def test_recommend_no_not_eligible_in_results(client):
    """Results should never include NOT_ELIGIBLE schemes."""
    payload = {
        "query": "scholarship",
        "profile": {"gender": "male", "age": 25, "caste_category": "General"},
        "top_k": 50,
    }
    r = client.post("/api/recommend", json=payload)
    assert r.status_code == 200
    for s in r.json()["results"]:
        assert s["eligibility"]["status"] != "not_eligible", \
            f"NOT_ELIGIBLE scheme in results: {s['name']}"


def test_qa_endpoint(client):
    payload = {"query": "What documents are needed for PM Awas Yojana?"}
    r = client.post("/api/qa", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "answers" in data
    assert "note" in data
    assert len(data["answers"]) > 0


def test_qa_grounded_returns_links(client):
    payload = {"query": "scholarship for SC ST students"}
    r = client.post("/api/qa", json=payload)
    assert r.status_code == 200
    for ans in r.json()["answers"]:
        assert "official_link" in ans
        assert "scheme_name" in ans


def test_compare_endpoint(client):
    payload = {"scheme_ids": [1, 2]}
    r = client.post("/api/compare", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["schemes"]) == 2


def test_compare_with_profile(client):
    payload = {
        "scheme_ids": [1, 2, 3],
        "profile": {"age": 25, "gender": "female", "state": "Rajasthan"}
    }
    r = client.post("/api/compare", json=payload)
    assert r.status_code == 200
    for s in r.json()["schemes"]:
        assert "eligibility" in s


def test_saved_schemes_lifecycle(client):
    session = "test-session-abc"
    # Save a scheme
    r = client.post(f"/api/saved/{session}/1")
    assert r.status_code == 200
    # Get saved
    r = client.get(f"/api/saved/{session}")
    assert r.status_code == 200
    assert r.json()["count"] == 1
    # Remove
    r = client.delete(f"/api/saved/{session}/1")
    assert r.status_code == 200
    r = client.get(f"/api/saved/{session}")
    assert r.json()["count"] == 0

