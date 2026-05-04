import time

import schedule
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.services.ingestion import ingest_all_sources


def _run_ingestion_job(session_factory) -> None:
    db: Session = session_factory()
    try:
        ingest_all_sources(db)
    finally:
        db.close()


def schedule_daily_ingestion(session_factory, hour: int = 2) -> None:
    schedule.every().day.at(f"{hour:02d}:00").do(_run_ingestion_job, session_factory=session_factory)


def run_scheduler(session_factory, stop_event=None, max_cycles: int | None = None) -> None:
    logger.info("Starting ingestion scheduler...")
    cycles = 0
    while True:
        schedule.run_pending()
        time.sleep(60)
        cycles += 1
        if max_cycles and cycles >= max_cycles:
            break
        if stop_event is not None and stop_event.is_set():
            break
