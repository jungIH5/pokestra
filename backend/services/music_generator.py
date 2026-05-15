"""music21로 악보(MusicXML) 및 MIDI 생성."""
import random
from music21 import stream, note, tempo, dynamics, key

SCALE_NOTES = {
    "C major": ["C", "D", "E", "F", "G", "A", "B"],
    "G major": ["G", "A", "B", "C", "D", "E", "F#"],
    "D major": ["D", "E", "F#", "G", "A", "B", "C#"],
    "F major": ["F", "G", "A", "Bb", "C", "D", "E"],
    "A minor": ["A", "B", "C", "D", "E", "F", "G"],
    "E minor": ["E", "F#", "G", "A", "B", "C", "D"],
}


def generate_score(music_params: dict) -> dict:
    scale_name = music_params["scale"]
    notes_pool = SCALE_NOTES.get(scale_name, SCALE_NOTES["C major"])
    octave = music_params["octave"]
    note_count = music_params["note_count"]
    bpm = music_params["tempo"]

    s = stream.Score()
    part = stream.Part()

    mm = tempo.MetronomeMark(number=bpm)
    part.append(mm)

    dyn = dynamics.Dynamic(music_params["dynamic"])
    part.append(dyn)

    durations = [0.5, 1.0, 1.5, 2.0]
    for _ in range(note_count):
        pitch_name = random.choice(notes_pool)
        dur = random.choice(durations)
        n = note.Note(f"{pitch_name}{octave}", quarterLength=dur)
        part.append(n)

    s.append(part)

    xml_str = s.write("musicxml")
    with open(xml_str, "r", encoding="utf-8") as f:
        xml_content = f.read()

    return {
        "scale": scale_name,
        "tempo": bpm,
        "note_count": note_count,
        "musicxml": xml_content,
    }
