from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    patterns: dict
    music_params: dict
    score: dict
