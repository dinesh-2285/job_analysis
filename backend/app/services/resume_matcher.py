from __future__ import annotations

from dataclasses import dataclass
import os

from loguru import logger
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from backend.app.models import JobPosting


@dataclass
class ResumeMatch:
    job_id: int
    score: float
    title: str
    company: str
    location: str | None


class SemanticResumeMatcher:
    _cached_job_ids: list[int] | None = None
    _cached_embeddings = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)

    def match(self, db: Session, resume_text: str, top_k: int = 5) -> list[ResumeMatch]:
        max_jobs = int(os.getenv("RESUME_MATCH_LIMIT", "500"))
        jobs = db.query(JobPosting).filter(JobPosting.description.is_not(None)).limit(max_jobs).all()
        if not jobs:
            return []

        descriptions = [job.description or "" for job in jobs]
        try:
            resume_embedding = self.model.encode([resume_text])
            job_ids = [job.id for job in jobs]
            if job_ids == self._cached_job_ids and self._cached_embeddings is not None:
                job_embeddings = self._cached_embeddings
            else:
                job_embeddings = self.model.encode(descriptions)
                self._cached_job_ids = job_ids
                self._cached_embeddings = job_embeddings
            scores = cosine_similarity(resume_embedding, job_embeddings)[0]
        except Exception as exc:
            logger.error(f"Resume matching failed: {exc}")
            return []

        ranked = sorted(zip(jobs, scores), key=lambda item: item[1], reverse=True)[:top_k]
        return [
            ResumeMatch(
                job_id=job.id,
                score=float(score),
                title=job.title,
                company=job.company,
                location=job.location,
            )
            for job, score in ranked
        ]
