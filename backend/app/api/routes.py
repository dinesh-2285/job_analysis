from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models import JobPosting
from backend.app.schemas.job import JobBase, JobList
from backend.app.schemas.ml import SalaryEstimateRequest, SalaryEstimateResponse, StreamPredictionRequest, StreamPredictionResponse
from backend.app.schemas.resume import (
    ResumeHistoryRequest,
    ResumeMatchRequest,
    ResumeMatchResponse,
    ResumeMatchResult,
)
from backend.app.schemas.user import BookmarkRequest, PreferenceRequest, UserRequest
from backend.app.services.analytics import job_counts_by_month, skill_trends
from backend.app.services.data_pipeline import run_pipeline
from backend.app.services.ml_service import estimate_salary_range, predict_stream_from_description, train_models
from backend.app.services.resume_matcher import SemanticResumeMatcher
from backend.app.services.users import (
    add_bookmark,
    get_or_create_user,
    get_preferences,
    list_bookmarks,
    list_resume_matches,
    save_preferences,
    save_resume_match,
)

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.get("/jobs", response_model=JobList)
def list_jobs(
    stream: str | None = None,
    location: str | None = None,
    search: str | None = None,
    limit: int = Query(50, le=200, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> JobList:
    query = db.query(JobPosting)
    if stream:
        query = query.filter(JobPosting.stream == stream)
    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    if search:
        query = query.filter(JobPosting.title.ilike(f"%{search}%"))
    total = query.count()
    jobs = query.offset(offset).limit(limit).all()
    return JobList(jobs=[JobBase.model_validate(job) for job in jobs], total=total)


@router.get("/jobs/{job_id}", response_model=JobBase)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobBase:
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobBase.model_validate(job)


@router.post("/resume/match", response_model=ResumeMatchResponse)
def resume_match(payload: ResumeMatchRequest, db: Session = Depends(get_db)) -> ResumeMatchResponse:
    matcher = SemanticResumeMatcher()
    matches = matcher.match(db, payload.resume_text, payload.top_k)
    return ResumeMatchResponse(
        matches=[
            ResumeMatchResult(
                job_id=match.job_id,
                score=match.score,
                title=match.title,
                company=match.company,
                location=match.location,
            )
            for match in matches
        ]
    )


@router.post("/users")
def create_user(payload: UserRequest, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_user(db, payload.username, payload.email)
    return {"id": user.id, "username": user.username}


@router.post("/bookmarks")
def create_bookmark(payload: BookmarkRequest, db: Session = Depends(get_db)) -> dict:
    bookmark = add_bookmark(db, payload.username, payload.job_id)
    return {"id": bookmark.id, "job_id": bookmark.job_id}


@router.get("/bookmarks")
def get_bookmarks(username: str, db: Session = Depends(get_db)) -> dict:
    bookmarks = list_bookmarks(db, username)
    return {"bookmarks": [{"id": bm.id, "job_id": bm.job_id} for bm in bookmarks]}


@router.post("/resume/history")
def save_match_history(payload: ResumeHistoryRequest, db: Session = Depends(get_db)) -> dict:
    record = save_resume_match(
        db,
        payload.username,
        payload.resume_name,
        payload.matched_job_id,
        payload.match_score,
    )
    return {"id": record.id}


@router.get("/resume/history")
def get_match_history(username: str, db: Session = Depends(get_db)) -> dict:
    records = list_resume_matches(db, username)
    return {
        "history": [
            {
                "id": record.id,
                "resume_name": record.resume_name,
                "matched_job_id": record.matched_job_id,
                "match_score": record.match_score,
            }
            for record in records
        ]
    }


@router.post("/preferences")
def save_user_preferences(payload: PreferenceRequest, db: Session = Depends(get_db)) -> dict:
    pref = save_preferences(
        db,
        payload.username,
        payload.target_stream,
        payload.target_salary,
        payload.location,
        payload.email_digest,
    )
    return {"id": pref.id}


@router.get("/preferences")
def get_user_preferences(username: str, db: Session = Depends(get_db)) -> dict:
    pref = get_preferences(db, username)
    if not pref:
        return {}
    return {
        "target_stream": pref.target_stream,
        "target_salary": pref.target_salary,
        "location": pref.location,
        "email_digest": pref.email_digest,
    }


@router.get("/skills/trends")
def skills_trends(db: Session = Depends(get_db)) -> dict:
    return {"trends": skill_trends(db), "job_counts": job_counts_by_month(db)}


@router.post("/ml/predict-stream", response_model=StreamPredictionResponse)
def predict_stream(payload: StreamPredictionRequest) -> StreamPredictionResponse:
    stream, confidence = predict_stream_from_description(payload.description)
    return StreamPredictionResponse(stream=stream, confidence=confidence)


@router.post("/ml/salary-estimate", response_model=SalaryEstimateResponse)
def salary_estimate(payload: SalaryEstimateRequest) -> SalaryEstimateResponse:
    salary_min, salary_max = estimate_salary_range(payload.stream, payload.location)
    return SalaryEstimateResponse(salary_min=salary_min, salary_max=salary_max)


@router.post("/ml/train")
def train_all_models(db: Session = Depends(get_db)) -> dict:
    return train_models(db)


@router.post("/pipeline/run")
def run_data_pipeline(db: Session = Depends(get_db)) -> dict:
    return run_pipeline(db)
