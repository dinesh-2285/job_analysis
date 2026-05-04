from pydantic import BaseModel


class ResumeMatchRequest(BaseModel):
    resume_text: str
    top_k: int = 5


class ResumeMatchResult(BaseModel):
    job_id: int
    score: float
    title: str
    company: str
    location: str | None


class ResumeMatchResponse(BaseModel):
    matches: list[ResumeMatchResult]


class ResumeHistoryRequest(BaseModel):
    username: str
    resume_name: str
    matched_job_id: int | None
    match_score: float
