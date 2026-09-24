"""
Tests for modules/rate_limiter.py.

Covers spec §20:
- 5 requests per minute enforcement
- remaining_requests counting
- window expiration
- instance isolation
"""

import time

from modules.rate_limiter import (
    GeminiRateLimiter,
    MAX_REQUESTS,
    TIME_WINDOW,
)


# ============================================================
# Basic Allow / Block
# ============================================================

def test_first_five_requests_allowed():

    limiter = GeminiRateLimiter()

    for index in range(MAX_REQUESTS):

        allowed, remaining = limiter.allow_request()

        assert allowed is True

        # 5th call: 5 - 5 = 0
        expected_remaining = (
            MAX_REQUESTS - (index + 1)
        )

        assert remaining == expected_remaining


def test_sixth_request_blocked():

    limiter = GeminiRateLimiter()

    for _ in range(MAX_REQUESTS):
        limiter.allow_request()

    allowed, remaining = limiter.allow_request()

    assert allowed is False
    assert remaining == 0


# ============================================================
# Remaining Counter
# ============================================================

def test_remaining_counter_decreases():

    limiter = GeminiRateLimiter()

    expected_sequence = [4, 3, 2, 1, 0]

    actual_sequence = []

    for _ in range(MAX_REQUESTS):

        _, remaining = limiter.allow_request()

        actual_sequence.append(remaining)

    assert actual_sequence == expected_sequence


# ============================================================
# Window Expiration
# ============================================================

def test_window_expires_and_allows_again():

    # Short window for fast test
    limiter = GeminiRateLimiter(
        max_requests=2,
        time_window=0.1
    )

    # Use up the limit
    assert limiter.allow_request()[0] is True
    assert limiter.allow_request()[0] is True
    assert limiter.allow_request()[0] is False

    # Wait for window to expire
    time.sleep(0.15)

    # Should be allowed again
    allowed, remaining = limiter.allow_request()

    assert allowed is True
    assert remaining == 1


# ============================================================
# Instance Isolation
# ============================================================

def test_instances_do_not_share_state():

    limiter_a = GeminiRateLimiter()
    limiter_b = GeminiRateLimiter()

    # Exhaust limiter_a
    for _ in range(MAX_REQUESTS):
        limiter_a.allow_request()

    # limiter_b should be unaffected
    allowed, remaining = limiter_b.allow_request()

    assert allowed is True
    assert remaining == MAX_REQUESTS - 1


# ============================================================
# Default Configuration
# ============================================================

def test_default_configuration():

    limiter = GeminiRateLimiter()

    assert limiter.max_requests == 5
    assert limiter.time_window == 60