import json
import os
import redis as redis_lib
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter()

_redis: redis_lib.Redis | None = None


def _redis_client() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(os.environ["REDIS_URL"])
    return _redis


def _get_result(job_id: str) -> dict:
    raw = _redis_client().get(f"job:{job_id}")
    if raw is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 job_id입니다.")
    data = json.loads(raw)
    if data.get("status") != "done" or not data.get("result"):
        raise HTTPException(status_code=409, detail="아직 완료되지 않은 작업입니다.")
    return data["result"]


@router.get("/{job_id}/score")
async def get_score(job_id: str):
    """악보 PNG의 Supabase URL로 리다이렉트한다."""
    result = _get_result(job_id)
    url = result.get("score_url")
    if not url:
        raise HTTPException(status_code=404, detail="악보 이미지가 없습니다.")
    return RedirectResponse(url=url)


@router.get("/{job_id}/audio")
async def get_audio(job_id: str):
    """MP3의 Supabase URL로 리다이렉트한다."""
    result = _get_result(job_id)
    url = result.get("audio_url")
    if not url:
        raise HTTPException(status_code=404, detail="오디오 파일이 없습니다.")
    return RedirectResponse(url=url)
