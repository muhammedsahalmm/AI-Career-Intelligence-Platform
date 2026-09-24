"""
Tests for POST /analyze.

Fast-only tests:
- No ML models loaded
- No Gemini calls

Slow end-to-end test is intentionally skipped
because the real pipeline was verified manually.
"""


# ============================================================
# Helpers
# ============================================================

def make_fake_pdf(name="resume.pdf"):

    return (
        "resumes",
        (
            name,
            b"%PDF-1.4 fake-content",
            "application/pdf"
        )
    )


# ============================================================
# Missing Required Fields (FastAPI 422)
# ============================================================

def test_missing_job_description_returns_422(client):

    files = [make_fake_pdf()]

    response = client.post(
        "/analyze",
        files=files
    )

    assert response.status_code == 422


def test_missing_resumes_returns_422(client):

    response = client.post(
        "/analyze",
        data={
            "job_description": (
                "We are looking for a Python developer."
            )
        }
    )

    assert response.status_code == 422


# ============================================================
# Empty Job Description — Early Return
# ============================================================

def test_empty_job_description_returns_empty_results(client):

    files = [make_fake_pdf()]

    response = client.post(
        "/analyze",
        data={"job_description": "   "},
        files=files
    )

    assert response.status_code == 200

    assert response.json() == {"results": []}


# ============================================================
# Upload Limit Exceeded
# ============================================================

def test_upload_limit_exceeded(client):

    # MAX_RESUME_UPLOADS = 20; send 21
    files = [
        make_fake_pdf(f"resume_{i}.pdf")
        for i in range(21)
    ]

    response = client.post(
        "/analyze",
        data={
            "job_description": (
                "We are looking for a Python developer "
                "with ML experience."
            )
        },
        files=files
    )

    assert response.status_code == 200

    data = response.json()

    assert "results" in data
    assert len(data["results"]) == 1

    error_result = data["results"][0]

    assert error_result["file_name"] == (
        "UPLOAD_LIMIT_EXCEEDED"
    )

    assert error_result["primary_role"] == "ERROR"