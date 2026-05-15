"""패턴 분석 결과를 음악 파라미터로 변환."""

COLOR_TO_SCALE = {
    "빨강": "C major",
    "파랑": "A minor",
    "노랑": "G major",
    "초록": "D major",
    "보라": "E minor",
    "주황": "F major",
    "흰색": "C major",
    "검정": "A minor",
}

TEMPO_MAP = {"slow": 60, "medium": 90, "fast": 130}

COMPLEXITY_TO_OCTAVE = {"simple": 4, "moderate": 5, "complex": 6}


def map_to_music_params(patterns: dict) -> dict:
    dominant = patterns.get("dominant_colors", ["흰색"])[0]
    scale = COLOR_TO_SCALE.get(dominant, "C major")

    tempo = TEMPO_MAP.get(patterns.get("tempo_hint", "medium"), 90)
    brightness = patterns.get("brightness", 0.5)
    octave = COMPLEXITY_TO_OCTAVE.get(patterns.get("pattern_complexity", "moderate"), 5)
    note_density = patterns.get("note_density", 0.5)

    # 밝기 → 음량 (pp~ff)
    dynamic = _brightness_to_dynamic(brightness)

    return {
        "scale": scale,
        "tempo": tempo,
        "octave": octave,
        "dynamic": dynamic,
        "note_count": max(4, int(note_density * 16)),
        "mood": patterns.get("mood", "평화로움"),
    }


def _brightness_to_dynamic(brightness: float) -> str:
    if brightness < 0.2:
        return "pp"
    elif brightness < 0.4:
        return "p"
    elif brightness < 0.6:
        return "mp"
    elif brightness < 0.8:
        return "mf"
    elif brightness < 0.9:
        return "f"
    return "ff"
