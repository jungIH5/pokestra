import subprocess
import tempfile
from pathlib import Path
from graph.state import GraphState

SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


def generate_audio_node(state: GraphState) -> dict:
    """FluidSynth로 MIDI를 WAV로 변환하고 ffmpeg으로 MP3로 인코딩한다."""
    midi_path = state.get("midi_path")
    if not midi_path:
        return {"audio_path": None, "current_step": "오디오 생성 건너뜀 (MIDI 없음)"}

    job_dir = _job_dir(state["job_id"])
    wav_path = job_dir / "score.wav"
    mp3_path = job_dir / "score.mp3"

    # MIDI → WAV
    subprocess.run(
        [
            "fluidsynth", "-ni", "-g", "1.0",
            "-F", str(wav_path),
            SOUNDFONT, midi_path,
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )

    # WAV → MP3
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-qscale:a", "4", str(mp3_path)],
        check=True,
        capture_output=True,
        timeout=30,
    )

    wav_path.unlink(missing_ok=True)

    return {
        "audio_path": str(mp3_path),
        "current_step": "오디오 생성 완료",
    }


def _job_dir(job_id: str) -> Path:
    return Path(tempfile.gettempdir()) / "photo-maestro" / job_id
