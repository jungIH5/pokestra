from graph.state import GraphState

COLOR_TO_SCALE = {
    "빨강": "C major", "파랑": "A minor", "노랑": "G major",
    "초록": "D major", "보라": "E minor", "주황": "F major",
    "흰색": "C major", "검정": "A minor",
}
TEMPO_MAP = {"slow": 60, "medium": 90, "fast": 130}
COMPLEXITY_TO_OCTAVE = {"simple": 4, "moderate": 5, "complex": 6}


def map_params_node(state: GraphState) -> dict:
    """시각 패턴 분석 결과를 음악 파라미터로 변환한다."""
    analysis = state.get("raw_analysis") or {}

    dominant = (analysis.get("dominant_colors") or ["흰색"])[0]
    scale = COLOR_TO_SCALE.get(dominant, "C major")
    tempo = TEMPO_MAP.get(analysis.get("tempo_hint", "medium"), 90)
    octave = COMPLEXITY_TO_OCTAVE.get(analysis.get("pattern_complexity", "moderate"), 5)
    brightness = analysis.get("brightness", 0.5)
    note_density = analysis.get("note_density", 0.5)

    music_params = {
        "scale": scale,
        "tempo": tempo,
        "octave": octave,
        "dynamic": _brightness_to_dynamic(brightness),
        "note_count": max(4, int(note_density * 16)),
        "mood": analysis.get("mood", "평화로움"),
    }

    return {
        "music_params": music_params,
        "error": None,
        "current_step": "음악 파라미터 매핑 완료",
    }


def _brightness_to_dynamic(brightness: float) -> str:
    thresholds = [(0.2, "pp"), (0.4, "p"), (0.6, "mp"), (0.8, "mf"), (0.9, "f")]
    for threshold, dynamic in thresholds:
        if brightness < threshold:
            return dynamic
    return "ff"
