import tempfile
from pathlib import Path
from music21 import stream, note, tempo, dynamics
from graph.state import GraphState

SCALE_NOTES = {
    "C major": ["C", "D", "E", "F", "G", "A", "B"],
    "G major": ["G", "A", "B", "C", "D", "E", "F#"],
    "D major": ["D", "E", "F#", "G", "A", "B", "C#"],
    "F major": ["F", "G", "A", "Bb", "C", "D", "E"],
    "A minor": ["A", "B", "C", "D", "E", "F", "G"],
    "E minor": ["E", "F#", "G", "A", "B", "C", "D"],
    "D minor": ["D", "E", "F", "G", "A", "Bb", "C"],
    "B minor": ["B", "C#", "D", "E", "F#", "G", "A"],
}

# edge density 임계값 → quarter length 매핑 (낮을수록 긴 음)
_DENSITY_TO_DUR = [(0.10, 2.0), (0.20, 1.0), (0.35, 0.5)]


def generate_score_node(state: GraphState) -> dict:
    """structural_data와 music_params를 조합해 구조 기반 악보를 생성한다."""
    params = state["music_params"]
    structural = state["structural_data"]
    job_id = state["job_id"]

    notes_pool = SCALE_NOTES.get(params["scale"], SCALE_NOTES["C major"])
    pitch_contour = structural["pitch_contour"]
    edge_density = structural["edge_density"]
    brightness = structural["brightness_profile"]
    n_slices = structural["n_slices"]

    s = stream.Score()
    part = stream.Part()
    part.append(tempo.MetronomeMark(number=params["tempo"]))
    part.append(dynamics.Dynamic(params["base_dynamic"]))

    for i in range(n_slices):
        dur = _density_to_duration(edge_density[i])

        if edge_density[i] < 0.02:
            part.append(note.Rest(quarterLength=dur))
            continue

        # pitch_contour 0~1 → 음계 인덱스
        idx = min(int(pitch_contour[i] * len(notes_pool)), len(notes_pool) - 1)
        pitch_name = notes_pool[idx]

        octave = 5
        if pitch_contour[i] > 0.75:
            octave = 6
        elif pitch_contour[i] < 0.25:
            octave = 4

        n = note.Note(f"{pitch_name}{octave}", quarterLength=dur)
        n.volume.velocity = int(brightness[i] * 80 + 40)  # 40~120
        part.append(n)

    s.append(part)

    job_dir = _job_dir(job_id)
    xml_path = job_dir / "score.xml"
    midi_path = job_dir / "score.mid"

    s.write("musicxml", fp=str(xml_path))
    s.write("midi", fp=str(midi_path))

    return {
        "final_musicxml": xml_path.read_text(encoding="utf-8"),
        "midi_path": str(midi_path),
        "current_step": "악보 생성 완료",
    }


def _density_to_duration(density: float) -> float:
    for threshold, dur in _DENSITY_TO_DUR:
        if density < threshold:
            return dur
    return 0.25  # 16분음표


def _job_dir(job_id: str) -> Path:
    job_dir = Path(tempfile.gettempdir()) / "photo-maestro" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
