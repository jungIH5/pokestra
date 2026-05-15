from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/download/{score_id}")
async def download_score(score_id: str):
    # TODO: score_id로 저장된 파일 반환
    return {"score_id": score_id, "status": "not_implemented"}
