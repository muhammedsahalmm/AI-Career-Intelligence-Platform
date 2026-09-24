import requests
import pandas as pd
import streamlit as st

from modules.logger import logger


# =====================================================
# CONFIGURATION
# =====================================================

API_URL = "http://fastapi:8000/analyze"
FEEDBACK_API_URL = "http://fastapi:8000/generate-feedback"

MAX_RESUME_UPLOADS = 20
MAX_AI_REQUESTS = 5


# =====================================================
# STREAMLIT PAGE
# =====================================================

st.set_page_config(
    page_title="AI Career Intelligence Platform",
    page_icon="📄",
    layout="wide"
)


# =====================================================
# SESSION STATE
# =====================================================

if "results" not in st.session_state:
    st.session_state.results = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "ai_requests_used" not in st.session_state:
    st.session_state.ai_requests_used = 0


# =====================================================
# HEADER
# =====================================================

st.title("AI Career Intelligence Platform")

st.markdown("""
Upload one or more Resume PDFs and paste a Job Description.

The platform performs:

- 🎯 Top-2 Role Prediction
- 📈 Semantic JD Matching
- ✅ Keyword Gap Analysis
- 🤖 AI Recruiter Feedback
""")


# =====================================================
# AI REQUEST STATUS
# =====================================================

ai_requests_remaining = max(
    MAX_AI_REQUESTS - st.session_state.ai_requests_used,
    0
)

st.caption(
    f"🤖 Gemini AI Requests Remaining: "
    f"{ai_requests_remaining}/{MAX_AI_REQUESTS}"
)


# =====================================================
# USER INPUTS
# =====================================================

job_description = st.text_area(
    label="Paste Job Description",
    height=220,
    placeholder="Paste the complete Job Description here..."
)

uploaded_files = st.file_uploader(
    label="Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)


# =====================================================
# ANALYZE RESUMES
# =====================================================

if st.button("Analyze Resumes"):

    logger.info("Resume analysis started.")

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    if job_description.strip() == "":
        st.warning("Please paste a Job Description.")
        st.stop()

    if not uploaded_files:
        st.warning("Please upload at least one Resume PDF.")
        st.stop()

    if len(uploaded_files) > MAX_RESUME_UPLOADS:

        st.error(
            f"You can upload a maximum of "
            f"{MAX_RESUME_UPLOADS} resumes."
        )

        st.stop()

    # -------------------------------------------------
    # Prepare Files for FastAPI
    # -------------------------------------------------

    files = []

    for uploaded_file in uploaded_files:

        uploaded_file.seek(0)

        files.append(
            (
                "resumes",
                (
                    uploaded_file.name,
                    uploaded_file.read(),
                    "application/pdf"
                )
            )
        )

    data = {
        "job_description": job_description
    }

    # -------------------------------------------------
    # Call FastAPI
    # -------------------------------------------------

    with st.spinner("Analyzing resumes..."):

        try:

            response = requests.post(
                API_URL,
                data=data,
                files=files,
                timeout=300
            )

            if response.status_code != 200:

                st.error(
                    f"API Error ({response.status_code})"
                )

                try:
                    st.json(response.json())
                except Exception:
                    st.error(response.text)

                st.stop()

            response_json = response.json()

            st.session_state.results = (
                response_json["results"]
            )

            st.session_state.analysis_done = True

            st.success(
                "Resume analysis completed successfully."
            )

            logger.info(
                "Resume analysis completed successfully."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to FastAPI.\n\n"
                "Make sure FastAPI is running."
            )

        except requests.exceptions.Timeout:

            st.error(
                "Resume analysis request timed out."
            )

        except Exception as e:

            logger.error(
                f"Streamlit analysis error: {str(e)}"
            )

            st.error(str(e))


# =====================================================
# DISPLAY RESULTS
# =====================================================

if st.session_state.analysis_done:

    results = st.session_state.results

    st.divider()

    st.header("Resume Analysis Results")

    for index, resume in enumerate(results):

        with st.container(border=True):

            st.subheader(
                f"📄 {resume['file_name']}"
            )

            # =================================================
            # ERROR RESULT
            # =================================================

            if resume.get("primary_role") == "ERROR":

                st.error(
                    resume.get(
                        "ai_feedback",
                        "Resume analysis failed."
                    )
                )

                continue

            # =================================================
            # ROLE PREDICTION
            # =================================================

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "### 🎯 Role Prediction"
                )

                st.write(
                    f"**Primary Role:** "
                    f"{resume['primary_role']}"
                )

                st.progress(
                    min(
                        resume["primary_confidence"] / 100,
                        1.0
                    )
                )

                st.write(
                    f"{resume['primary_confidence']:.2f}%"
                )

                st.write("")

                st.write(
                    f"**Secondary Role:** "
                    f"{resume['secondary_role']}"
                )

                st.progress(
                    min(
                        resume["secondary_confidence"] / 100,
                        1.0
                    )
                )

                st.write(
                    f"{resume['secondary_confidence']:.2f}%"
                )

            # =================================================
            # JD MATCH
            # =================================================

            with col2:

                st.markdown(
                    "### 📈 JD Match"
                )

                st.metric(
                    label="Semantic Match",
                    value=(
                        f"{resume['semantic_jd_match_score']:.2f}%"
                    )
                )

            # =================================================
            # KEYWORD ANALYSIS
            # =================================================

            st.markdown(
                "### ✅ Keyword Analysis"
            )

            matched = (
                ", ".join(
                    resume["matched_keywords"]
                )
                if resume["matched_keywords"]
                else "None"
            )

            missing = (
                ", ".join(
                    resume["missing_keywords"]
                )
                if resume["missing_keywords"]
                else "None"
            )

            st.success(
                f"Matched Keywords:\n\n{matched}"
            )

            st.warning(
                f"Missing Keywords:\n\n{missing}"
            )

            # =================================================
            # AI RECRUITER AGENT
            # =================================================

            st.markdown(
                "### 🤖 AI Recruiter Agent"
            )

            feedback_key = (
                f"feedback_{resume['file_name']}_{index}"
            )

            # -------------------------------------------------
            # Generate AI Feedback Button
            # -------------------------------------------------

            if feedback_key not in st.session_state:

                if st.button(
                    "🤖 Generate AI Feedback",
                    key=f"generate_feedback_{index}"
                ):

                    # -----------------------------------------
                    # Check frontend session counter
                    # -----------------------------------------

                    if (
                        st.session_state.ai_requests_used
                        >= MAX_AI_REQUESTS
                    ):

                        st.error(
                            "Gemini AI request limit reached. "
                            "Please wait before generating "
                            "more feedback."
                        )

                    else:

                        with st.spinner(
                            "AI Recruiter Agent is analyzing..."
                        ):

                            try:

                                feedback_response = (
                                    requests.post(

                                        FEEDBACK_API_URL,

                                        data={

                                            "file_name":
                                                resume["file_name"],

                                            "top_role":
                                                resume["primary_role"],

                                            "top_confidence":
                                                resume[
                                                    "primary_confidence"
                                                ],

                                            "second_role":
                                                resume[
                                                    "secondary_role"
                                                ],

                                            "second_confidence":
                                                resume[
                                                    "secondary_confidence"
                                                ],

                                            "jd_match_score":
                                                resume[
                                                    "semantic_jd_match_score"
                                                ],

                                            "matched_keywords":
                                                matched,

                                            "missing_keywords":
                                                missing

                                        },

                                        timeout=180
                                    )
                                )

                                # ---------------------------------
                                # API Response Handling
                                # ---------------------------------

                                if (
                                    feedback_response.status_code
                                    != 200
                                ):

                                    st.error(
                                        f"AI Feedback API Error "
                                        f"({feedback_response.status_code})"
                                    )

                                else:

                                    feedback_data = (
                                        feedback_response.json()
                                    )

                                    # ---------------------------------
                                    # Rate Limit Reached
                                    # ---------------------------------

                                    if feedback_data.get(
                                        "rate_limit_exceeded",
                                        False
                                    ):

                                        st.error(
                                            feedback_data.get(
                                                "ai_feedback",
                                                "Gemini rate limit reached."
                                            )
                                        )

                                    else:

                                        # ---------------------------------
                                        # Count successful Gemini request
                                        # ---------------------------------

                                        st.session_state.ai_requests_used += 1

                                        # ---------------------------------
                                        # Save feedback
                                        # ---------------------------------

                                        st.session_state[
                                            feedback_key
                                        ] = feedback_data[
                                            "ai_feedback"
                                        ]

                                        st.success(
                                            "AI recruiter feedback generated successfully."
                                        )

                                        logger.info(
                                            f"AI feedback generated for "
                                            f"{resume['file_name']}"
                                        )

                                        st.rerun()

                            except (
                                requests.exceptions.ConnectionError
                            ):

                                st.error(
                                    "Cannot connect to FastAPI.\n\n"
                                    "Make sure the backend is running."
                                )

                            except (
                                requests.exceptions.Timeout
                            ):

                                st.error(
                                    "AI feedback request timed out."
                                )

                            except Exception as e:

                                logger.error(
                                    f"AI feedback error: {str(e)}"
                                )

                                st.error(
                                    f"Unable to generate AI feedback: {e}"
                                )

            # -------------------------------------------------
            # Display Generated Feedback
            # -------------------------------------------------

            if feedback_key in st.session_state:

                st.info(
                    st.session_state[feedback_key]
                )

            st.divider()


# =====================================================
# DOWNLOAD REPORT
# =====================================================

if st.session_state.analysis_done:

    st.divider()

    csv_df = pd.DataFrame(
        st.session_state.results
    )

    csv_df.rename(
        columns={

            "file_name": "File Name",

            "primary_role": "Primary Role",
            "primary_confidence": "Primary Confidence",

            "secondary_role": "Secondary Role",
            "secondary_confidence": "Secondary Confidence",

            "semantic_jd_match_score": "Semantic JD Match",

            "matched_keywords": "Matched Keywords",

            "missing_keywords": "Missing Keywords",

            "ai_feedback": "AI Recruiter Feedback"

        },
        inplace=True
    )

    csv_df["Matched Keywords"] = (
        csv_df["Matched Keywords"].apply(
            lambda x:
                ", ".join(x)
                if isinstance(x, list)
                else x
        )
    )

    csv_df["Missing Keywords"] = (
        csv_df["Missing Keywords"].apply(
            lambda x:
                ", ".join(x)
                if isinstance(x, list)
                else x
        )
    )

    csv_data = (
        csv_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="📥 Download Analysis Report",
        data=csv_data,
        file_name="resume_analysis_report.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()


# =====================================================
# FOOTER
# =====================================================

st.caption(
    "AI Career Intelligence Platform • Version 1.0"
)