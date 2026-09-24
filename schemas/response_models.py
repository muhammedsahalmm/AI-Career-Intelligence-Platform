from typing import List, Optional

from pydantic import BaseModel


class ResumeResult(BaseModel):
    """
    Analysis result for one resume.
    """

    file_name: str

    primary_role: str
    primary_confidence: float

    secondary_role: str
    secondary_confidence: float

    semantic_jd_match_score: float

    matched_keywords: List[str]
    missing_keywords: List[str]

    # AI feedback is generated separately
    # when the user clicks "Generate AI Feedback".
    ai_feedback: Optional[str] = None


class ResumeResponse(BaseModel):
    """
    API response.
    """

    results: List[ResumeResult]