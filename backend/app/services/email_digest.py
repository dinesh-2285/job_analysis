import os
import smtplib
import ssl
from email.message import EmailMessage

from loguru import logger

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

    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    context = ssl.create_default_context()
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        logger.error(f"SMTP authentication failed: {exc}")
    except smtplib.SMTPConnectError as exc:
        logger.error(f"SMTP connection failed: {exc}")
    except smtplib.SMTPException as exc:
        logger.error(f"SMTP error sending digest: {exc}")
