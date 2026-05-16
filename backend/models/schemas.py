from typing import Optional, Literal
from pydantic import BaseModel


class AnalyzeJobResponse(BaseModel):
    job_id: str
    status: Literal["queued"]


class JobResult(BaseModel):
    score_url: str
    audio_url: str
    image_type: Literal["sheet_music", "general"]
    music_params: Optional[dict] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "failed"]
    current_step: str
    progress: int
    result: Optional[JobResult] = None
    error: Optional[str] = None
