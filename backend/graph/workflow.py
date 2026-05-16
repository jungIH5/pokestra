from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes.preprocessor import preprocess_node
from graph.nodes.classifier import classify_node
from graph.nodes.analyzer import analyze_node
from graph.nodes.validator import validate_node, should_retry
from graph.nodes.mapper import map_params_node
from graph.nodes.score_gen import generate_score_node
from graph.nodes.omr import omr_node
from graph.nodes.score_render import render_score_node
from graph.nodes.audio_gen import generate_audio_node
from graph.nodes.uploader import upload_files_node


def _route_by_image_type(state: GraphState) -> str:
    return state.get("image_type", "general")


def _route_after_validate(state: GraphState) -> str:
    return should_retry(state)


def build_graph() -> StateGraph:
    g = StateGraph(GraphState)

    # 노드 등록
    g.add_node("preprocess", preprocess_node)
    g.add_node("classify", classify_node)
    g.add_node("analyze", analyze_node)
    g.add_node("validate", validate_node)
    g.add_node("map_params", map_params_node)
    g.add_node("generate_score", generate_score_node)
    g.add_node("omr", omr_node)
    g.add_node("render_score", render_score_node)
    g.add_node("generate_audio", generate_audio_node)
    g.add_node("upload_files", upload_files_node)

    # 진입점
    g.set_entry_point("preprocess")

    # 공통 앞 단계
    g.add_edge("preprocess", "classify")

    # 분류 결과에 따라 분기
    g.add_conditional_edges(
        "classify",
        _route_by_image_type,
        {
            "general": "analyze",
            "sheet_music": "omr",
        },
    )

    # 일반 사진 경로: analyze → validate → (재시도 or 계속)
    g.add_edge("analyze", "validate")
    g.add_conditional_edges(
        "validate",
        _route_after_validate,
        {
            "retry": "analyze",
            "continue": "map_params",
        },
    )
    g.add_edge("map_params", "generate_score")
    g.add_edge("generate_score", "render_score")

    # 악보 사진 경로: omr → render_score (generate_score 건너뜀)
    g.add_edge("omr", "render_score")

    # 두 경로 합류
    g.add_edge("render_score", "generate_audio")
    g.add_edge("generate_audio", "upload_files")
    g.add_edge("upload_files", END)

    return g


# 컴파일된 그래프 (worker.py에서 임포트)
graph = build_graph().compile()
