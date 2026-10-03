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
# Retry Configuration
# ============================================================

MAX_RETRY_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 2


# ============================================================
# Transient Error Detection
# ============================================================

def is_transient_error(error_message):
    """
    Decide whether a Gemini error is worth retrying.

    Transient (retry):
        - 503 UNAVAILABLE
        - high demand
        - timeout
        - network

    Permanent (do not retry):
        - quota exceeded
        - permission
        - api key
    """

    error = error_message.lower()

    transient_keywords = [
        "503",
        "unavailable",
        "high demand",
        "timeout",
        "network",
    ]

    return any(
        keyword in error
        for keyword in transient_keywords
    )


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
# Friendly Error Message Builder
# ============================================================

def build_error_message(error_message):
    """
    Convert a Gemini error into a user-friendly message.
    """

    error = error_message.lower()

    # --------------------------------------------------------
    # Quota Error
    # --------------------------------------------------------

    if "quota" in error:

        return (
            "❌ Gemini API quota exceeded.\n\n"
            "Please try again later."
        )

    # --------------------------------------------------------
    # Permission / Authentication Error
    # --------------------------------------------------------

    elif "permission" in error:

        return (
            "❌ Invalid Gemini API Key."
        )

    # --------------------------------------------------------
    # Missing API Key
    # --------------------------------------------------------

    elif "api key" in error:

        return (
            "❌ Gemini API Key is missing."
        )

    # --------------------------------------------------------
    # Timeout Error
    # --------------------------------------------------------

    elif "timeout" in error:

        return (
            "❌ Request timed out.\n"
            "Please try again."
        )

    # --------------------------------------------------------
    # Network Error
    # --------------------------------------------------------

    elif "network" in error:

        return (
            "❌ Network connection error."
        )

    # --------------------------------------------------------
    # Unknown Error
    # --------------------------------------------------------

    else:

        return (
            "❌ Unable to generate AI recruiter "
            "feedback.\n"
            "Please try again later."
        )


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

    Transient Gemini errors (503, high demand, timeout,
    network) are retried automatically up to
    MAX_RETRY_ATTEMPTS times with exponential backoff.

    Permanent errors (quota, permission, api key) fail
    immediately without retry.
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
    # Retry Loop
    # ========================================================

    last_error = None

    for attempt in range(
        1,
        MAX_RETRY_ATTEMPTS + 1
    ):

        try:

            response = client.models.generate_content(

                model="gemini-2.5-flash",

                contents=prompt

            )

            # ------------------------------------------------
            # Calculate Gemini Response Time
            # ------------------------------------------------

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            # ------------------------------------------------
            # Success Logging
            # ------------------------------------------------

            logger.info(
                f"AI feedback generated successfully "
                f"for {file_name} | "
                f"attempt={attempt}/{MAX_RETRY_ATTEMPTS} | "
                f"Gemini response time: "
                f"{elapsed_time:.2f}s"
            )

            return response.text

        except Exception as e:

            last_error = str(e)

            # ------------------------------------------------
            # Decide Whether To Retry
            # ------------------------------------------------

            can_retry = (
                is_transient_error(last_error)
                and attempt < MAX_RETRY_ATTEMPTS
            )

            if can_retry:

                backoff = (
                    INITIAL_BACKOFF_SECONDS
                    * attempt
                )

                logger.warning(
                    f"Gemini transient error for "
                    f"{file_name} | "
                    f"attempt={attempt}/{MAX_RETRY_ATTEMPTS} | "
                    f"retrying in {backoff}s | "
                    f"Error: {last_error}"
                )

                time.sleep(backoff)

                continue

            # ------------------------------------------------
            # No Retry — Log Final Failure
            # ------------------------------------------------

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            logger.error(
                f"Gemini Error for {file_name} | "
                f"attempt={attempt}/{MAX_RETRY_ATTEMPTS} | "
                f"Response time: "
                f"{elapsed_time:.2f}s | "
                f"Error: {last_error}"
            )

            break

    # ========================================================
    # All Attempts Exhausted
    # ========================================================

    return build_error_message(last_error)