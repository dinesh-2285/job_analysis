from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobPosting(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: str
    description: str
    skills_required: List[str]
    posted_date: Optional[datetime] = None
    source: Optional[str] = None