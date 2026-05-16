from graph.state import GraphState

REQUIRED_KEYS = {"dominant_colors", "brightness", "mood", "tempo_hint", "note_density"}
MAX_ATTEMPTS = 3


def validate_node(state: GraphState) -> dict:
    """분석 결과의 필수 필드 존재 여부를 검사한다."""
    analysis = state.get("raw_analysis") or {}
    missing = REQUIRED_KEYS - analysis.keys()

    if missing:
        return {
            "error": f"분석 누락 필드: {missing}",
            "current_step": "분석 검증 실패",
        }

    return {
        "error": None,
        "current_step": "분석 검증 통과",
    }


def should_retry(state: GraphState) -> str:
    """재시도 여부를 결정하는 조건부 엣지 함수."""
    if state.get("error") and state.get("analysis_attempts", 0) < MAX_ATTEMPTS:
        return "retry"
    return "continue"
