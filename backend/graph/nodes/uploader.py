from pathlib import Path
from graph.state import GraphState
from services import storage


def upload_files_node(state: GraphState) -> dict:
    """생성된 파일을 Supabase Storage에 업로드하고 공개 URL을 반환한다."""
    job_id = state["job_id"]
    updates: dict = {"current_step": "파일 업로드 완료"}

    # 악보 PNG
    png_path = state.get("score_png_path")
    if png_path and Path(png_path).exists():
        data = Path(png_path).read_bytes()
        updates["score_url"] = storage.upload(f"scores/{job_id}.png", data, "image/png")

    # MP3
    audio_path = state.get("audio_path")
    if audio_path and Path(audio_path).exists():
        data = Path(audio_path).read_bytes()
        updates["audio_url"] = storage.upload(f"audio/{job_id}.mp3", data, "audio/mpeg")

    # MusicXML (항상 저장)
    if state.get("final_musicxml"):
        data = state["final_musicxml"].encode("utf-8")
        storage.upload(f"xml/{job_id}.xml", data, "application/vnd.recordare.musicxml+xml")

    _cleanup_temp(job_id)

    return updates


def _cleanup_temp(job_id: str) -> None:
    import shutil, tempfile
    job_dir = Path(tempfile.gettempdir()) / "photo-maestro" / job_id
    shutil.rmtree(job_dir, ignore_errors=True)
