from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobPosting(BaseModel):
    id: Optional[int] = None
    title: str
    company: str
    location: str
    description: Optional[str] = None
    skills: Optional[str] = None
    salary: Optional[str] = None
    date_posted: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    stream: Optional[str] = None
    scraped_at: Optional[datetime] = None