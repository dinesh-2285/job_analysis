import os
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from backend.app.models import JobPosting


def send_weekly_digest(db: Session, recipient: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_host or not smtp_user or not smtp_password:
        return

    jobs = db.query(JobPosting).order_by(JobPosting.posted_at.desc()).limit(10).all()
    body = "\n".join([f"{job.title} at {job.company}" for job in jobs])

    msg = EmailMessage()
    msg["Subject"] = "Weekly Job Digest"
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.set_content(body or "No new jobs yet.")

    with smtplib.SMTP(smtp_host) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
