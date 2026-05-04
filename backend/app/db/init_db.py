from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.models import job, user


def init_db() -> None:
    _ = job, user
    Base.metadata.create_all(bind=engine)
