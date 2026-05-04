from loguru import logger

from backend.app.db.init_db import init_db
from backend.app.services.ingestion import ingest_all_sources


def run_pipeline(db) -> dict:
    init_db()
    result = ingest_all_sources(db)
    logger.info(f"Pipeline completed: {result}")
    return result
