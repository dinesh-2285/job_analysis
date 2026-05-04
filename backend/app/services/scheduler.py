import time

import schedule
from loguru import logger
from sqlalchemy.orm import Session

from backend.app.services.ingestion import ingest_all_sources


def schedule_daily_ingestion(db: Session, hour: int = 2) -> None:
    schedule.every().day.at(f"{hour:02d}:00").do(ingest_all_sources, db=db)


def run_scheduler(db: Session) -> None:
    logger.info("Starting ingestion scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)
