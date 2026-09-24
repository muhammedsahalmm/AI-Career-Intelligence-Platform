"""
Tests for modules/validator.py.

Covers spec §13:
- None input
- Wrong extension
- Oversized file
- Corrupted PDF content
- Empty file
- Valid PDF
"""

import io
from pathlib import Path

import pytest

from modules.validator import validate_uploaded_file


# ============================================================
# Test Double
# ============================================================

class FakeUpload:
    """
    Mimics a Streamlit UploadedFile enough for validation.

    Provides:
    - .name attribute
    - .seek() / .read() methods
    """

    def __init__(self, name, content_bytes):

        self.name = name

        self._buffer = io.BytesIO(
            content_bytes
        )

    def seek(self, position):
        self._buffer.seek(position)

    def read(self, size=-1):
        return self._buffer.read(size)


# ============================================================
# Sample Valid PDF
# ============================================================

VALID_PDF_PATH = Path(
    "sample_resume/sahalairesume.pdf"
)


# ============================================================
# Tests
# ============================================================

def test_none_upload_fails():

    is_valid, message = validate_uploaded_file(None)

    assert is_valid is False
    assert "no file" in message.lower()


def test_non_pdf_extension_fails():

    fake = FakeUpload(
        "resume.txt",
        b"hello world"
    )

    is_valid, message = validate_uploaded_file(fake)

    assert is_valid is False
    assert "pdf" in message.lower()


def test_oversized_file_fails():

    # 6 MB of zero bytes — exceeds 5 MB limit
    oversized = b"\x00" * (6 * 1024 * 1024)

    fake = FakeUpload("big.pdf", oversized)

    is_valid, message = validate_uploaded_file(fake)

    assert is_valid is False
    assert "size" in message.lower()


def test_corrupted_pdf_fails():

    # .pdf extension but garbage content
    fake = FakeUpload(
        "fake.pdf",
        b"this is definitely not a pdf"
    )

    is_valid, message = validate_uploaded_file(fake)

    assert is_valid is False
    assert (
        "invalid" in message.lower()
        or "corrupted" in message.lower()
    )


def test_empty_bytes_fails():

    fake = FakeUpload("empty.pdf", b"")

    is_valid, message = validate_uploaded_file(fake)

    assert is_valid is False


def test_valid_pdf_passes():

    if not VALID_PDF_PATH.exists():

        pytest.skip(
            f"Sample PDF not found: {VALID_PDF_PATH}"
        )

    content = VALID_PDF_PATH.read_bytes()

    fake = FakeUpload(
        VALID_PDF_PATH.name,
        content
    )

    is_valid, message = validate_uploaded_file(fake)

    assert is_valid is True
    assert message == "Valid"