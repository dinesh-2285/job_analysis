from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.models import JobPosting
from backend.app.services.ingestion import upsert_jobs


def test_upsert_jobs_inserts():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    jobs = [
        {
            "source": "remotive",
            "external_id": "1",
            "title": "Data Analyst",
            "company": "Example",
            "location": "Remote",
            "description": "Analyze data",
            "skills": "python, sql",
            "stream": "Data",
            "posted_at": None,
            "salary_min": None,
            "salary_max": None,
            "data_version": "v1",
        }
    ]

    inserted = upsert_jobs(session, jobs)
    assert inserted == 1
    assert session.query(JobPosting).count() == 1
