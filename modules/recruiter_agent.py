import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from modules.logger import logger


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


# ============================================================
# Load Prompt Template
# ============================================================

def load_prompt():

    prompt_path = Path(
        "prompts/recruiter_prompt.txt"
    )

    with open(
        prompt_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# AI Recruiter Agent
# ============================================================

def generate_recruiter_feedback(
    file_name,
    top_role,
    top_confidence,
    second_role,
    second_confidence,
    jd_match_score,
    matched_keywords,
    missing_keywords
):
    """
    Generate AI Recruiter feedback using Google Gemini.

    Gemini is called ONLY when the user explicitly
    requests AI recruiter feedback.
    """

    # --------------------------------------------------------
    # Load Prompt
    # --------------------------------------------------------

    prompt_template = load_prompt()

    # --------------------------------------------------------
    # Build Prompt
    # --------------------------------------------------------

    prompt = prompt_template.format(

        file_name=file_name,

        top_role=top_role,
        top_confidence=top_confidence,

        second_role=second_role,
        second_confidence=second_confidence,

        jd_match_score=jd_match_score,

        matched_keywords=(
            ", ".join(matched_keywords)
            if matched_keywords
            else "None"
        ),

        missing_keywords=(
            ", ".join(missing_keywords)
            if missing_keywords
            else "None"
        )

    )

    # ========================================================
    # Performance Timer
    # ========================================================

    start_time = time.perf_counter()

    # ========================================================
    # Gemini API Request
    # ========================================================

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )

        # ----------------------------------------------------
        # Calculate Gemini Response Time
        # ----------------------------------------------------

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        # ----------------------------------------------------
        # Success Logging
        # ----------------------------------------------------

        logger.info(
            f"AI feedback generated successfully "
            f"for {file_name} | "
            f"Gemini response time: "
            f"{elapsed_time:.2f}s"
        )

        return response.text

    # ========================================================
    # Gemini Error Handling
    # ========================================================

    except Exception as e:

        # ----------------------------------------------------
        # Calculate Failed Request Time
        # ----------------------------------------------------

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        # ----------------------------------------------------
        # Error Logging
        # ----------------------------------------------------

        logger.error(
            f"Gemini Error for {file_name} | "
            f"Response time: "
            f"{elapsed_time:.2f}s | "
            f"Error: {str(e)}"
        )

        error = str(e).lower()

        # ----------------------------------------------------
        # Quota Error
        # ----------------------------------------------------

        if "quota" in error:

            return (
                "❌ Gemini API quota exceeded.\n\n"
                "Please try again later."
            )

        # ----------------------------------------------------
        # Permission / Authentication Error
        # ----------------------------------------------------

        elif "permission" in error:

            return (
                "❌ Invalid Gemini API Key."
            )

        # ----------------------------------------------------
        # Missing API Key
        # ----------------------------------------------------

        elif "api key" in error:

            return (
                "❌ Gemini API Key is missing."
            )

        # ----------------------------------------------------
        # Timeout Error
        # ----------------------------------------------------

        elif "timeout" in error:

            return (
                "❌ Request timed out.\n"
                "Please try again."
            )

        # ----------------------------------------------------
        # Network Error
        # ----------------------------------------------------

        elif "network" in error:

            return (
                "❌ Network connection error."
            )

        # ----------------------------------------------------
        # Unknown Error
        # ----------------------------------------------------

        else:

            return (
                "❌ Unable to generate AI recruiter "
                "feedback.\n"
                "Please try again later."
            )