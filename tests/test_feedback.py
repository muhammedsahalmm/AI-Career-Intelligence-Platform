"""
Tests for POST /generate-feedback.

Gemini is mocked — no real API calls are made.
Covers spec §20, §24, §37.
"""

import pytest

from modules.rate_limiter import (
    gemini_rate_limiter,
    MAX_REQUESTS,
)


# ============================================================
# Helpers
# ============================================================

def valid_feedback_payload():

    return {
        "file_name": "resume.pdf",
        "top_role": "INFORMATION-TECHNOLOGY",
        "top_confidence": "85.5",
        "second_role": "ENGINEERING",
        "second_confidence": "10.2",
        "jd_match_score": "72.0",
        "matched_keywords": "python, docker",
        "missing_keywords": "kubernetes",
    }


# ============================================================
# Fixture: Mock Gemini
# ============================================================

@pytest.fixture
def mock_gemini(monkeypatch):
    """
    Replace generate_recruiter_feedback with a fake.

    No real Gemini call is made.
    """

    def fake_feedback(**kwargs):

        return "MOCKED RECRUITER FEEDBACK"

    monkeypatch.setattr(
        "api.main.generate_recruiter_feedback",
        fake_feedback
    )


# ============================================================
# Missing Required Fields
# ============================================================

def test_missing_required_field_returns_422(client):

    response = client.post(
        "/generate-feedback",
        data={"file_name": "resume.pdf"}
    )

    assert response.status_code == 422


# ============================================================
# Rate Limit Exceeded
# ============================================================

def test_rate_limit_exceeded_returns_flag(client):

    # Exhaust the limiter
    for _ in range(MAX_REQUESTS):

        gemini_rate_limiter.allow_request()

    response = client.post(
        "/generate-feedback",
        data=valid_feedback_payload()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["rate_limit_exceeded"] is True
    assert data["requests_remaining"] == 0


# ============================================================
# Successful Generation (Gemini Mocked)
# ============================================================

def test_successful_feedback_returns_text(
    client,
    mock_gemini
):

    response = client.post(
        "/generate-feedback",
        data=valid_feedback_payload()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ai_feedback"] == (
        "MOCKED RECRUITER FEEDBACK"
    )

    assert data["rate_limit_exceeded"] is False

    assert data["file_name"] == "resume.pdf"


# ============================================================
# Counter Decrement
# ============================================================

def test_remaining_requests_decrements(
    client,
    mock_gemini
):

    response = client.post(
        "/generate-feedback",
        data=valid_feedback_payload()
    )

    data = response.json()

    # First call: 5 - 1 = 4 remaining
    assert data["requests_remaining"] == 4