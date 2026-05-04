from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models import JobPosting


def fetch_remotive_jobs() -> list[dict]:
    settings = get_settings()
    try:
        response = requests.get(settings.remotive_base_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("jobs", [])
    except Exception as exc:
        logger.error(f"Remotive fetch failed: {exc}")
        return []


def fetch_adzuna_jobs() -> list[dict]:
    settings = get_settings()
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        return []

    url = f"{settings.adzuna_base_url}/us/search/1"
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": 50,
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as exc:
        logger.error(f"Adzuna fetch failed: {exc}")
        return []


def fetch_linkedin_jobs(keyword: str = "data", location: str = "United States") -> list[dict]:
    jobs: list[dict] = []
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    for start in range(0, 50, 25):
        params = {"keywords": keyword, "location": location, "start": start}
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.select("li"):
                title = card.select_one("h3")
                company = card.select_one("h4")
                location_tag = card.select_one(".job-search-card__location")
                job_link = card.select_one("a")
                job_id = card.get("data-entity-urn", "").split(":")[-1]
                if not job_id:
                    job_id = job_link.get("href") if job_link else ""
                if not job_id:
                    continue
                jobs.append(
                    {
                        "id": job_id or job_link.get("href", ""),
                        "title": title.get_text(strip=True) if title else "Unknown Role",
                        "company": company.get_text(strip=True) if company else "Unknown Company",
                        "location": location_tag.get_text(strip=True) if location_tag else None,
                        "description": "",
                        "url": job_link.get("href") if job_link else "",
                    }
                )
        except Exception as exc:
            logger.error(f"LinkedIn scraping failed: {exc}")
            break
    return jobs


def normalize_remotive(job: dict, version_tag: str) -> dict:
    return {
        "source": "remotive",
        "external_id": str(job.get("id")),
        "title": job.get("title") or "Unknown Role",
        "company": job.get("company_name") or "Unknown Company",
        "location": job.get("candidate_required_location"),
        "description": job.get("description"),
        "skills": ", ".join(job.get("tags", [])),
        "stream": job.get("category"),
        "posted_at": parse_datetime(job.get("publication_date")),
        "salary_min": None,
        "salary_max": None,
        "data_version": version_tag,
    }


def normalize_adzuna(job: dict, version_tag: str) -> dict:
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    category = job.get("category")
    category_label = category.get("label") if isinstance(category, dict) else None
    return {
        "source": "adzuna",
        "external_id": str(job.get("id")),
        "title": job.get("title") or "Unknown Role",
        "company": (job.get("company") or {}).get("display_name", "Unknown Company"),
        "location": (job.get("location") or {}).get("display_name"),
        "description": job.get("description"),
        "skills": category_label or "",
        "stream": category_label,
        "posted_at": parse_datetime(job.get("created")),
        "salary_min": float(salary_min) if salary_min else None,
        "salary_max": float(salary_max) if salary_max else None,
        "data_version": version_tag,
    }


def normalize_linkedin(job: dict, version_tag: str) -> dict:
    return {
        "source": "linkedin",
        "external_id": str(job.get("id") or job.get("url") or job.get("title")),
        "title": job.get("title") or "Unknown Role",
        "company": job.get("company") or "Unknown Company",
        "location": job.get("location"),
        "description": job.get("description"),
        "skills": job.get("skills"),
        "stream": job.get("stream"),
        "posted_at": parse_datetime(job.get("date_posted")),
        "salary_min": None,
        "salary_max": None,
        "data_version": version_tag,
    }


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def upsert_jobs(db: Session, jobs: Iterable[dict]) -> int:
    inserted = 0
    for job in jobs:
        existing = (
            db.query(JobPosting)
            .filter(JobPosting.source == job["source"], JobPosting.external_id == job["external_id"])
            .first()
        )
        if existing:
            continue
        db.add(JobPosting(**job))
        inserted += 1
    db.commit()
    return inserted


def ingest_all_sources(db: Session) -> dict:
    version_tag = f"v{datetime.now(timezone.utc):%Y%m%d}"
    remotive_jobs = [normalize_remotive(job, version_tag) for job in fetch_remotive_jobs()]
    adzuna_jobs = [normalize_adzuna(job, version_tag) for job in fetch_adzuna_jobs()]
    linkedin_jobs = [normalize_linkedin(job, version_tag) for job in fetch_linkedin_jobs()]

    total_inserted = 0
    total_inserted += upsert_jobs(db, remotive_jobs)
    total_inserted += upsert_jobs(db, adzuna_jobs)
    total_inserted += upsert_jobs(db, linkedin_jobs)

    return {
        "inserted": total_inserted,
        "remotive": len(remotive_jobs),
        "adzuna": len(adzuna_jobs),
        "linkedin": len(linkedin_jobs),
    }
