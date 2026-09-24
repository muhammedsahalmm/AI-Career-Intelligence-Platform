from typing import List, Annotated

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form
)

from services.resume_service import analyze_resume

from modules.recruiter_agent import (
    generate_recruiter_feedback
)

from modules.validator import (
    validate_uploaded_file
)

from modules.rate_limiter import (
    gemini_rate_limiter
)

from schemas.response_models import (
    ResumeResponse
)


# ============================================================
# Configuration
# ============================================================

MAX_RESUME_UPLOADS = 20


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="AI Career Intelligence Platform API",
    description="Resume Screening API powered by ML + LLM",
    version="1.0.0"
)

# ============================================================
# Home Endpoint
# ============================================================

@app.get("/")
def home():

    return {
        "message": (
            "AI Career Intelligence Platform API is running."
        )
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# Resume Analysis Endpoint
# ============================================================

@app.post(
    "/analyze",
    response_model=ResumeResponse,
    summary="Analyze one or more resumes"
)
async def analyze_resumes(

    job_description: Annotated[
        str,
        Form(
            ...,
            description="Paste the Job Description"
        )
    ],

    resumes: Annotated[
        List[UploadFile],
        File(
            ...,
            description="Upload one or more Resume PDFs"
        )
    ]

):

    # --------------------------------------------------------
    # Job Description Validation
    # --------------------------------------------------------

    if not job_description.strip():

        return {
            "results": []
        }

    # --------------------------------------------------------
    # Resume Upload Limit
    # --------------------------------------------------------

    if len(resumes) > MAX_RESUME_UPLOADS:

        return {
            "results": [
                {
                    "file_name": "UPLOAD_LIMIT_EXCEEDED",

                    "primary_role": "ERROR",
                    "primary_confidence": 0.0,

                    "secondary_role": "ERROR",
                    "secondary_confidence": 0.0,

                    "semantic_jd_match_score": 0.0,

                    "matched_keywords": [],

                    "missing_keywords": [],

                    "ai_feedback": (
                        f"You can upload a maximum of "
                        f"{MAX_RESUME_UPLOADS} resumes "
                        f"at a time."
                    )
                }
            ]
        }

    # --------------------------------------------------------
    # Analysis Results
    # --------------------------------------------------------

    results = []

    # --------------------------------------------------------
    # Process Each Resume
    # --------------------------------------------------------

    for uploaded_file in resumes:

        try:

            # ------------------------------------------------
            # Upload / PDF Validation
            # ------------------------------------------------

            is_valid, message = (
                validate_uploaded_file(
                    uploaded_file
                )
            )

            if not is_valid:

                results.append({

                    "file_name": (
                        uploaded_file.filename
                        or "Unknown File"
                    ),

                    "primary_role": "ERROR",
                    "primary_confidence": 0.0,

                    "secondary_role": "ERROR",
                    "secondary_confidence": 0.0,

                    "semantic_jd_match_score": 0.0,

                    "matched_keywords": [],

                    "missing_keywords": [],

                    "ai_feedback": message

                })

                continue

            # ------------------------------------------------
            # Resume Analysis
            # ------------------------------------------------

            result = analyze_resume(

                uploaded_file,

                job_description

            )

            results.append(result)

        except Exception as e:

            results.append({

                "file_name": (
                    uploaded_file.filename
                    or "Unknown File"
                ),

                "primary_role": "ERROR",
                "primary_confidence": 0.0,

                "secondary_role": "ERROR",
                "secondary_confidence": 0.0,

                "semantic_jd_match_score": 0.0,

                "matched_keywords": [],

                "missing_keywords": [],

                "ai_feedback": str(e)

            })

    # --------------------------------------------------------
    # Return Analysis
    # --------------------------------------------------------

    return {
        "results": results
    }
    
    # ============================================================
# Generate AI Recruiter Feedback
# ============================================================

@app.post(
    "/generate-feedback",
    summary="Generate AI recruiter feedback"
)
async def generate_feedback(

    file_name: Annotated[
        str,
        Form(...)
    ],

    top_role: Annotated[
        str,
        Form(...)
    ],

    top_confidence: Annotated[
        float,
        Form(...)
    ],

    second_role: Annotated[
        str,
        Form(...)
    ],

    second_confidence: Annotated[
        float,
        Form(...)
    ],

    jd_match_score: Annotated[
        float,
        Form(...)
    ],

    matched_keywords: Annotated[
        str,
        Form(...)
    ],

    missing_keywords: Annotated[
        str,
        Form(...)
    ]

):

    # --------------------------------------------------------
    # Gemini Rate Limiting
    # --------------------------------------------------------

    allowed, remaining_requests = (
        gemini_rate_limiter.allow_request()
    )

    if not allowed:

        return {
            "file_name": file_name,

            "ai_feedback": (
                "❌ Gemini rate limit reached.\n\n"
                "Maximum 5 AI feedback requests are "
                "allowed per minute.\n\n"
                "Please wait and try again."
            ),

            "rate_limit_exceeded": True,

            "requests_remaining": 0
        }

    # --------------------------------------------------------
    # Convert Keyword Strings Back To Lists
    # --------------------------------------------------------

    matched_keyword_list = [

        keyword.strip()

        for keyword in matched_keywords.split(",")

        if keyword.strip()

    ]

    missing_keyword_list = [

        keyword.strip()

        for keyword in missing_keywords.split(",")

        if keyword.strip()

    ]

    # --------------------------------------------------------
    # Generate Gemini Feedback
    # --------------------------------------------------------

    feedback = generate_recruiter_feedback(

        file_name=file_name,

        top_role=top_role,
        top_confidence=top_confidence,

        second_role=second_role,
        second_confidence=second_confidence,

        jd_match_score=jd_match_score,

        matched_keywords=matched_keyword_list,

        missing_keywords=missing_keyword_list

    )

    # --------------------------------------------------------
    # Return Feedback
    # --------------------------------------------------------

    return {

        "file_name": file_name,

        "ai_feedback": feedback,

        "rate_limit_exceeded": False,

        "requests_remaining": remaining_requests

    }
    
    