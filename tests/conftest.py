"""
Shared pytest fixtures for the AI Career Intelligence Platform.

Provides:
- TestClient for FastAPI endpoints
- Automatic rate limiter reset between tests
"""

import pytest

from fastapi.testclient import TestClient

from api.main import app

from modules.rate_limiter import gemini_rate_limiter


@pytest.fixture
def client():
    """
    FastAPI TestClient.

    Runs requests against the app in-process.
    No server, no Docker needed.
    """

    with TestClient(app) as test_client:

        yield test_client


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Reset the global Gemini rate limiter before every test.

    Prevents rate-limit state from leaking across tests.
    """

    gemini_rate_limiter.request_times.clear()

    yield

    gemini_rate_limiter.request_times.clear()