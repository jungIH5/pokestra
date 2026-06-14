from graph.state import GraphState


def map_params_node(state: GraphState) -> dict:
    """structural_data의 슬라이스 수를 music_params에 반영한다."""
    structural = state.get("structural_data") or {}
    params = dict(state.get("music_params") or {})
    params["note_count"] = structural.get("n_slices", 16)

    return {
        "music_params": params,
        "error": None,
        "current_step": "음악 파라미터 매핑 완료",
    }
