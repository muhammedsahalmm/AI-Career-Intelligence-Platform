import fitz


# ============================================================
# Validation Configuration
# ============================================================

ALLOWED_EXTENSIONS = ["pdf"]

MAX_FILE_SIZE_MB = 5


# ============================================================
# Resume Upload Validation
# ============================================================

def validate_uploaded_file(uploaded_file):
    """
    Validate a resume PDF uploaded through either:

    - Streamlit UploadedFile
    - FastAPI UploadFile

    Returns:
        (True, "Valid")
        (False, "Reason")
    """

    if uploaded_file is None:
        return False, "No file uploaded."

    # --------------------------------------------------------
    # Get filename
    # --------------------------------------------------------

    filename = getattr(
        uploaded_file,
        "filename",
        None
    )

    if filename is None:

        filename = getattr(
            uploaded_file,
            "name",
            ""
        )

    filename = filename.lower()

    # --------------------------------------------------------
    # File Extension Validation
    # --------------------------------------------------------

    if not filename.endswith(".pdf"):

        return (
            False,
            "Only PDF files are allowed."
        )

    # --------------------------------------------------------
    # Read File Content
    # --------------------------------------------------------

    try:

        # FastAPI UploadFile
        if hasattr(uploaded_file, "file"):

            uploaded_file.file.seek(0)

            file_bytes = uploaded_file.file.read()

        # Streamlit UploadedFile
        else:

            uploaded_file.seek(0)

            file_bytes = uploaded_file.read()

    except Exception:

        return (
            False,
            "Unable to read uploaded file."
        )

    # --------------------------------------------------------
    # File Size Validation
    # --------------------------------------------------------

    file_size_mb = (
        len(file_bytes)
        / (1024 * 1024)
    )

    if file_size_mb > MAX_FILE_SIZE_MB:

        return (
            False,
            f"File size exceeds "
            f"{MAX_FILE_SIZE_MB} MB."
        )

    # --------------------------------------------------------
    # PDF Validation
    # --------------------------------------------------------

    try:

        pdf = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

    except Exception:

        return (
            False,
            "Invalid or corrupted PDF."
        )

    # --------------------------------------------------------
    # Password Protected PDF
    # --------------------------------------------------------

    if pdf.needs_pass:

        pdf.close()

        return (
            False,
            "Password-protected PDFs are not supported."
        )

    # --------------------------------------------------------
    # Empty PDF
    # --------------------------------------------------------

    if len(pdf) == 0:

        pdf.close()

        return (
            False,
            "PDF contains no pages."
        )

    # --------------------------------------------------------
    # Close PDF
    # --------------------------------------------------------

    pdf.close()

    # --------------------------------------------------------
    # Reset File Pointer
    # --------------------------------------------------------

    try:

        if hasattr(uploaded_file, "file"):

            uploaded_file.file.seek(0)

        else:

            uploaded_file.seek(0)

    except Exception:

        pass

    return True, "Valid"