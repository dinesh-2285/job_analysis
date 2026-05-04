from fastapi import FastAPI

from backend.app.api.routes import router
from backend.app.core.logging import configure_logging
from backend.app.db.init_db import init_db


def create_app() -> FastAPI:
    configure_logging()
    init_db()
    app = FastAPI(title="Job Analytics API")
    app.include_router(router)
    return app


app = create_app()
