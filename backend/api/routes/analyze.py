import base64
import json
import os
import uuid
import redis as redis_lib
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from celery_app import celery_app
from models.schemas import AnalyzeJobResponse

router = APIRouter()

_redis: redis_lib.Redis | None = None


def _redis_client() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
    return _redis


@router.post("/", response_model=AnalyzeJobResponse)
async def analyze(
    image: UploadFile = File(...),
    mood_input: str = Form(""),
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    image_bytes = await image.read()
    job_id = str(uuid.uuid4())

    _redis_client().setex(
        f"job:{job_id}",
        3600,
        json.dumps({"status": "queued", "current_step": "대기 중", "progress": 0}, ensure_ascii=False),
    )

    image_b64 = base64.b64encode(image_bytes).decode()
    celery_app.send_task(
        "worker.run_analysis_task",
        args=[job_id, image_b64, mood_input],
        queue="analysis",
    )

    return AnalyzeJobResponse(job_id=job_id, status="queued")
