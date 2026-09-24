"""
Tests for root and health endpoints.

Confirms the API is alive and responding correctly.
"""


def test_root_returns_message(client):

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data

    assert (
        "AI Career Intelligence Platform"
        in data["message"]
    )


def test_health_returns_healthy(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data == {"status": "healthy"}
    