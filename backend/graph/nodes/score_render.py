import subprocess
import tempfile
from pathlib import Path
from music21 import converter
from graph.state import GraphState


def render_score_node(state: GraphState) -> dict:
    """
    MusicXML을 PNG로 렌더링하고, OMR 경로에서 MIDI가 없으면 함께 생성한다.
    MuseScore3를 xvfb-run으로 헤드리스 실행한다.
    """
    job_id = state["job_id"]
    job_dir = _job_dir(job_id)

    xml_path = job_dir / "score.xml"
    xml_path.write_text(state["final_musicxml"], encoding="utf-8")

    png_path = job_dir / "score.png"
    midi_path = job_dir / "score.mid"

    # MuseScore3 PNG 렌더링 (헤드리스)
    try:
        subprocess.run(
            ["xvfb-run", "-a", "musescore3", "--no-gui", "-o", str(png_path), str(xml_path)],
            check=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # MuseScore3가 없거나 실패하면 빈 PNG 대신 xml만 남긴다
        # uploader 노드에서 score_png_path가 없으면 xml URL만 반환
        return {
            "score_png_path": None,
            "midi_path": state.get("midi_path") or _generate_midi(state["final_musicxml"], midi_path),
            "current_step": f"악보 렌더링 실패 (PNG 생략): {e}",
        }

    # OMR 경로: MIDI가 아직 없으면 music21로 생성
    midi_result = state.get("midi_path") or _generate_midi(state["final_musicxml"], midi_path)

    return {
        "score_png_path": str(png_path),
        "midi_path": midi_result,
        "current_step": "악보 이미지 렌더링 완료",
    }


def _generate_midi(musicxml: str, midi_path: Path) -> str:
    score = converter.parse(musicxml)
    score.write("midi", fp=str(midi_path))
    return str(midi_path)


def _job_dir(job_id: str) -> Path:
    job_dir = Path(tempfile.gettempdir()) / "photo-maestro" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
