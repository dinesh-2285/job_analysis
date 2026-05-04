from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str
    email: str | None = None


class BookmarkRequest(BaseModel):
    username: str
    job_id: int


class PreferenceRequest(BaseModel):
    username: str
    target_stream: str | None = None
    target_salary: str | None = None
    location: str | None = None
    email_digest: bool = False
