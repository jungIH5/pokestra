import json
import os
import redis as redis_lib
from fastapi import APIRouter, HTTPException
from models.schemas import JobStatusResponse

router = APIRouter()

_redis: redis_lib.Redis | None = None


def _redis_client() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(os.environ["REDIS_URL"])
    return _redis


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    raw = _redis_client().get(f"job:{job_id}")
    if raw is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 job_id입니다.")

    data = json.loads(raw)
    return JobStatusResponse(
        job_id=job_id,
        status=data.get("status", "queued"),
        current_step=data.get("current_step", ""),
        progress=data.get("progress", 0),
        result=data.get("result"),
        error=data.get("error"),
    )
