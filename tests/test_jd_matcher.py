"""
Tests for modules/jd_matcher.py.

The SentenceTransformer model is mocked with a
deterministic fake encoder.

No real model is loaded — tests run in milliseconds.
Covers spec §15, §37.
"""

import numpy as np
import pytest

import modules.jd_matcher as jd_matcher


# ============================================================
# Fake Embedding Model
# ============================================================

class FakeEmbeddingModel:
    """
    Deterministic encoder.

    Maps each text to a small vector derived from
    its character codes. Same text -> same vector.
    Different text -> different vector.
    """

    def encode(self, texts, convert_to_numpy=True):

        vectors = []

        for text in texts:

            seed = sum(ord(c) for c in text) % 1000

            vec = np.array(
                [
                    float(seed % 10),
                    float((seed // 10) % 10),
                    float((seed // 100) % 10),
                    1.0,
                ],
                dtype=float,
            )

            vectors.append(vec)

        return np.array(vectors)


# ============================================================
# Fixture: Patch load_embedding_model
# ============================================================

@pytest.fixture
def fake_model(monkeypatch):

    fake = FakeEmbeddingModel()

    monkeypatch.setattr(
        jd_matcher,
        "load_embedding_model",
        lambda: fake,
    )

    return fake


# ============================================================
# Empty / Whitespace Input
# ============================================================

def test_empty_text_returns_none():

    assert jd_matcher.get_text_embedding("") is None


def test_whitespace_text_returns_none():

    assert (
        jd_matcher.get_text_embedding("   \n\t  ")
        is None
    )


# ============================================================
# Score Bounds
# ============================================================

def test_identical_texts_score_near_100(fake_model):

    text = (
        "Python developer with machine learning "
        "and FastAPI experience."
    )

    score = jd_matcher.calculate_semantic_jd_match_score(
        text,
        text,
    )

    # Identical text -> identical embeddings
    # -> cosine similarity 1.0 -> 100%
    assert score == pytest.approx(100.0, abs=0.01)


def test_different_texts_in_range(fake_model):

    resume = (
        "Java backend developer with 5 years "
        "of enterprise experience."
    )

    jd = (
        "Python ML engineer with deep learning "
        "and NLP experience."
    )

    score = jd_matcher.calculate_semantic_jd_match_score(
        resume,
        jd,
    )

    assert 0.0 <= score <= 100.0


def test_empty_resume_returns_zero(fake_model):

    score = jd_matcher.calculate_semantic_jd_match_score(
        "",
        "Some job description text.",
    )

    assert score == 0.0


def test_empty_jd_returns_zero(fake_model):

    score = jd_matcher.calculate_semantic_jd_match_score(
        "Some resume text.",
        "",
    )

    assert score == 0.0


# ============================================================
# Embedding Shape
# ============================================================

def test_embedding_shape(fake_model):

    embedding = jd_matcher.get_text_embedding(
        "Short resume text."
    )

    assert embedding is not None

    # Must be 2D row vector (1, N)
    assert embedding.shape[0] == 1

    assert embedding.shape[1] > 0