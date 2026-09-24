import time

from modules.logger import logger

from modules.resume_parser import (
    extract_text_from_pdf,
    clean_resume
)

from modules.predictor import (
    predict_roles
)

from modules.jd_matcher import (
    calculate_semantic_jd_match_score
)

from modules.keyword_gap import (
    extract_jd_keywords
)


def analyze_resume(
    uploaded_file,
    job_description
):
    """
    Complete resume analysis pipeline.

    Gemini AI Recruiter feedback is NOT generated here.

    AI feedback is generated separately when the user
    explicitly requests it.

    Performance metrics are logged for the complete
    resume analysis pipeline.
    """

    # ========================================================
    # Performance Timer
    # ========================================================

    start_time = time.perf_counter()

    file_name = (
        uploaded_file.filename
        if hasattr(uploaded_file, "filename")
        else "Unknown File"
    )

    # ========================================================
    # Extract Resume Text
    # ========================================================

    resume_text = extract_text_from_pdf(
        uploaded_file
    )

    if resume_text.strip() == "":

        elapsed_time = (
            time.perf_counter() - start_time
        )

        logger.warning(
            f"Resume analysis failed | "
            f"file={file_name} | "
            f"reason=Text extraction failed | "
            f"duration={elapsed_time:.2f}s"
        )

        # Return a full ResumeResult shape so that
        # api/main.py's response_model=ResumeResponse
        # validation does not fail with HTTP 500.
        return {

            "file_name": file_name,

            "primary_role": "ERROR",
            "primary_confidence": 0.0,

            "secondary_role": "ERROR",
            "secondary_confidence": 0.0,

            "semantic_jd_match_score": 0.0,

            "matched_keywords": [],

            "missing_keywords": [],

            "ai_feedback": (
                "Could not extract text from the PDF. "
                "It may be a scanned image or empty "
                "document."
            )
        }

    # ========================================================
    # Clean Resume
    # ========================================================

    cleaned_resume = clean_resume(
        resume_text
    )

    # ========================================================
    # Role Prediction
    # ========================================================

    (
        resume_vector,
        top_roles,
        top_confidences
    ) = predict_roles(
        cleaned_resume
    )

    # ========================================================
    # Semantic JD Matching
    # ========================================================

    semantic_score = (
        calculate_semantic_jd_match_score(
            resume_text,
            job_description
        )
    )

    # ========================================================
    # Keyword Gap Analysis
    # ========================================================

    (
        matched_keywords,
        missing_keywords
    ) = extract_jd_keywords(
        job_description,
        resume_text
    )

    # ========================================================
    # Performance Metric
    # ========================================================

    elapsed_time = (
        time.perf_counter() - start_time
    )

    logger.info(
        f"Resume analysis completed | "
        f"file={file_name} | "
        f"duration={elapsed_time:.2f}s"
    )

    # ========================================================
    # Return Analysis Result
    # ========================================================

    return {

        "file_name": uploaded_file.filename,

        "primary_role": top_roles[0],
        "primary_confidence": float(
            top_confidences[0]
        ),

        "secondary_role": top_roles[1],
        "secondary_confidence": float(
            top_confidences[1]
        ),

        "semantic_jd_match_score": float(
            semantic_score
        ),

        "matched_keywords": matched_keywords,

        "missing_keywords": missing_keywords,

        # Gemini feedback will be generated later
        # when the user clicks the button.
        "ai_feedback": None
    }