from sqlalchemy.orm import Session

from backend.app.models import Bookmark, ResumeMatch, User, UserPreference


def get_or_create_user(db: Session, username: str, email: str | None = None) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_bookmark(db: Session, username: str, job_id: int) -> Bookmark:
    user = get_or_create_user(db, username)
    bookmark = Bookmark(user_id=user.id, job_id=job_id)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def list_bookmarks(db: Session, username: str) -> list[Bookmark]:
    user = get_or_create_user(db, username)
    return db.query(Bookmark).filter(Bookmark.user_id == user.id).all()


def save_resume_match(
    db: Session, username: str, resume_name: str, matched_job_id: int | None, match_score: float
) -> ResumeMatch:
    user = get_or_create_user(db, username)
    record = ResumeMatch(
        user_id=user.id,
        resume_name=resume_name,
        matched_job_id=matched_job_id,
        match_score=match_score,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_resume_matches(db: Session, username: str) -> list[ResumeMatch]:
    user = get_or_create_user(db, username)
    return db.query(ResumeMatch).filter(ResumeMatch.user_id == user.id).all()


def save_preferences(
    db: Session,
    username: str,
    target_stream: str | None,
    target_salary: str | None,
    location: str | None,
    email_digest: bool,
) -> UserPreference:
    user = get_or_create_user(db, username)
    pref = db.query(UserPreference).filter(UserPreference.user_id == user.id).first()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
    pref.target_stream = target_stream
    pref.target_salary = target_salary
    pref.location = location
    pref.email_digest = email_digest
    db.commit()
    db.refresh(pref)
    return pref


def get_preferences(db: Session, username: str) -> UserPreference | None:
    user = get_or_create_user(db, username)
    return db.query(UserPreference).filter(UserPreference.user_id == user.id).first()
