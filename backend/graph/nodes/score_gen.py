import random
import tempfile
from pathlib import Path
from music21 import stream, note, tempo, dynamics, key
from graph.state import GraphState

SCALE_NOTES = {
    "C major": ["C", "D", "E", "F", "G", "A", "B"],
    "G major": ["G", "A", "B", "C", "D", "E", "F#"],
    "D major": ["D", "E", "F#", "G", "A", "B", "C#"],
    "F major": ["F", "G", "A", "Bb", "C", "D", "E"],
    "A minor": ["A", "B", "C", "D", "E", "F", "G"],
    "E minor": ["E", "F#", "G", "A", "B", "C", "D"],
}


def generate_score_node(state: GraphState) -> dict:
    """music_params로 music21 악보를 생성하고 MusicXML과 MIDI를 저장한다."""
    params = state["music_params"]
    job_id = state["job_id"]

    notes_pool = SCALE_NOTES.get(params["scale"], SCALE_NOTES["C major"])
    octave = params["octave"]
    note_count = params["note_count"]
    bpm = params["tempo"]

    s = stream.Score()
    part = stream.Part()
    part.append(tempo.MetronomeMark(number=bpm))
    part.append(dynamics.Dynamic(params["dynamic"]))

    durations = [0.5, 1.0, 1.5, 2.0]
    for _ in range(note_count):
        pitch = random.choice(notes_pool)
        dur = random.choice(durations)
        part.append(note.Note(f"{pitch}{octave}", quarterLength=dur))

    s.append(part)

    job_dir = _job_dir(job_id)
    xml_path = job_dir / "score.xml"
    midi_path = job_dir / "score.mid"

    s.write("musicxml", fp=str(xml_path))
    s.write("midi", fp=str(midi_path))

    final_musicxml = xml_path.read_text(encoding="utf-8")

    return {
        "final_musicxml": final_musicxml,
        "midi_path": str(midi_path),
        "current_step": "악보 생성 완료",
    }


def _job_dir(job_id: str) -> Path:
    job_dir = Path(tempfile.gettempdir()) / "photo-maestro" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
