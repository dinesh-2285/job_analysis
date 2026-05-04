from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.models import JobPosting


def skill_trends(db: Session) -> dict:
    buckets: dict[str, Counter] = defaultdict(Counter)
    jobs = db.query(JobPosting).filter(JobPosting.skills.is_not(None)).all()
    for job in jobs:
        if not job.posted_at:
            continue
        month = job.posted_at.strftime("%Y-%m")
        skills = [s.strip().lower() for s in (job.skills or "").split(",") if s.strip()]
        buckets[month].update(skills)

    return {month: counts.most_common(10) for month, counts in buckets.items()}


def job_counts_by_month(db: Session) -> dict:
    counts: dict[str, int] = defaultdict(int)
    jobs = db.query(JobPosting).filter(JobPosting.posted_at.is_not(None)).all()
    for job in jobs:
        month = job.posted_at.strftime("%Y-%m")
        counts[month] += 1
    return dict(sorted(counts.items()))
