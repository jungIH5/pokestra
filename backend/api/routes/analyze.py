from fastapi import APIRouter, UploadFile, File, HTTPException
from services.image_analyzer import analyze_image
from services.pattern_mapper import map_to_music_params
from services.music_generator import generate_score
from models.schemas import AnalyzeResponse

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
async def analyze(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    image_bytes = await image.read()
    patterns = await analyze_image(image_bytes)
    music_params = map_to_music_params(patterns)
    score = generate_score(music_params)

    return AnalyzeResponse(patterns=patterns, music_params=music_params, score=score)
