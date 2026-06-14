import logging
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import analyze, jobs
from services.database import init_db

logger = logging.getLogger(__name__)

app = FastAPI(title="photo-maestro API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

media_root = Path(os.getenv("MEDIA_ROOT", "/app/media"))
media_root.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_root)), name="media")

app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])


@app.on_event("startup")
async def startup():
    try:
        init_db()
    except Exception as e:
        logger.warning("DB 초기화 실패 (계속 실행): %s", e)


@app.get("/health")
async def health():
    import redis as redis_lib
    result: dict = {"status": "ok", "redis": "unknown", "mysql": "unknown"}

    try:
        r = redis_lib.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), socket_connect_timeout=2)
        r.ping()
        result["redis"] = "ok"
    except Exception:
        result["redis"] = "unavailable"
        result["status"] = "degraded"

    try:
        from services.database import _get_engine
        from sqlalchemy import text
        engine = _get_engine()
        if engine is None:
            result["mysql"] = "not_configured"
        else:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result["mysql"] = "ok"
    except Exception:
        result["mysql"] = "unavailable"
        result["status"] = "degraded"

    return result
