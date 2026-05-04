from pydantic import BaseModel


class StreamPredictionRequest(BaseModel):
    description: str


class StreamPredictionResponse(BaseModel):
    stream: str | None
    confidence: float


class SalaryEstimateRequest(BaseModel):
    stream: str
    location: str | None = None
    experience_level: str | None = None
    skills: list[str] | None = None


class SalaryEstimateResponse(BaseModel):
    salary_min: float | None
    salary_max: float | None
