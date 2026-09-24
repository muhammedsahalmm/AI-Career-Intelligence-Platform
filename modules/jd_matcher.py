import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from modules.resume_parser import (
    clean_text_for_embedding,
    split_text_into_chunks
)


# ============================================================
# Embedding Model
# ============================================================

_embedding_model = None


def load_embedding_model():
    """
    Load the Sentence Transformer embedding model once.

    The model is loaded lazily:
    - It is NOT loaded when this module is imported.
    - It is loaded only when semantic matching is actually required.
    - Once loaded, the same model instance is reused.

    This keeps the module framework-independent and allows it
    to work with FastAPI, Streamlit, Docker, or other clients.
    """

    global _embedding_model

    if _embedding_model is None:

        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _embedding_model


# ============================================================
# Generate Text Embedding
# ============================================================

def get_text_embedding(text):
    """
    Generate a document-level embedding.

    Process:

    1. Clean the text.
    2. Split the text into chunks.
    3. Generate an embedding for each chunk.
    4. Average all chunk embeddings.
    5. Return the final document embedding.
    """

    cleaned_text = clean_text_for_embedding(text)

    if not cleaned_text.strip():
        return None

    chunks = split_text_into_chunks(
        cleaned_text
    )

    if not chunks:
        return None

    model = load_embedding_model()

    chunk_embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    document_embedding = np.mean(
        chunk_embeddings,
        axis=0
    )

    return document_embedding.reshape(
        1,
        -1
    )


# ============================================================
# Semantic JD Matching
# ============================================================

def calculate_semantic_jd_match_score(
    resume_text,
    jd_text
):
    """
    Calculate semantic similarity between a resume
    and a job description.

    Returns:
        float:
            Semantic match score between 0 and 100.
    """

    resume_embedding = get_text_embedding(
        resume_text
    )

    jd_embedding = get_text_embedding(
        jd_text
    )

    if (
        resume_embedding is None
        or jd_embedding is None
    ):
        return 0.0

    similarity_score = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    return float(
        similarity_score * 100
    )