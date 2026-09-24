import re
import fitz


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from a PDF uploaded through either
    Streamlit or FastAPI.
    """

    try:

        # FastAPI UploadFile
        if hasattr(uploaded_file, "file"):

            uploaded_file.file.seek(0)

            pdf_document = fitz.open(
                stream=uploaded_file.file.read(),
                filetype="pdf"
            )

        # Streamlit UploadedFile
        else:

            uploaded_file.seek(0)

            pdf_document = fitz.open(
                stream=uploaded_file.read(),
                filetype="pdf"
            )

        text = ""

        for page in pdf_document:
            text += page.get_text()

        pdf_document.close()

        return text

    except Exception:

        return ""


def clean_resume(text):
    """
    Clean resume text for TF-IDF role prediction.
    """

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"www\S+", " ", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\d{10,}", " ", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_text_for_embedding(text):
    """
    Clean text before generating sentence embeddings.
    """

    text = str(text)

    # Remove URLs
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"www\S+", " ", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\d{10,}", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_text_into_chunks(text, chunk_size=250):
    """
    Split long documents into smaller chunks
    before generating embeddings.
    """

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(words[i:i + chunk_size])

        chunks.append(chunk)

    return chunks