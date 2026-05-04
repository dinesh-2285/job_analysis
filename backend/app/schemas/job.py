from datetime import datetime
from pydantic import BaseModel


class JobBase(BaseModel):
    id: int
    source: str
    external_id: str
    title: str
    company: str
    location: str | None
    description: str | None
    skills: str | None
    stream: str | None
    salary_min: float | None
    salary_max: float | None
    posted_at: datetime | None

    class Config:
        from_attributes = True


class JobList(BaseModel):
    jobs: list[JobBase]
    total: int
