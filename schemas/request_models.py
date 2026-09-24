from pydantic import BaseModel, Field


class ResumeRequest(BaseModel):
    """
    Request model for resume analysis.
    """

    job_description: str = Field(
        ...,
        min_length=20,
        description="Job Description"
    )