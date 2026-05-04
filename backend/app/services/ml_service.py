import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.models import JobPosting
from ml.pipeline import (
    build_skill_graph,
    estimate_salary,
    predict_stream,
    train_demand_forecaster,
    train_salary_estimator,
    train_stream_classifier,
)


def load_training_dataframe(db: Session) -> pd.DataFrame:
    jobs = db.query(JobPosting).all()
    return pd.DataFrame(
        [
            {
                "description": job.description,
                "stream": job.stream,
                "posted_at": job.posted_at,
                "skills": job.skills,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "location": job.location,
            }
            for job in jobs
        ]
    )


def train_models(db: Session) -> dict:
    df = load_training_dataframe(db)
    results = {
        "stream_classifier": train_stream_classifier(df),
        "demand_forecaster": train_demand_forecaster(df),
        "salary_estimator": train_salary_estimator(df),
        "skill_graph": build_skill_graph(df),
    }
    logger.info(f"Training results: {results}")
    return results


def predict_stream_from_description(description: str) -> tuple[str | None, float]:
    return predict_stream(description)


def estimate_salary_range(stream: str, location: str | None) -> tuple[float | None, float | None]:
    return estimate_salary(stream, location)
