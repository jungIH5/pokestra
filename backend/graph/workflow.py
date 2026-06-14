from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes.preprocessor import preprocess_node
from graph.nodes.classifier import classify_node
from graph.nodes.structural_extractor import structural_extract_node
from graph.nodes.mood_parser import mood_parse_node
from graph.nodes.mapper import map_params_node
from graph.nodes.score_gen import generate_score_node
from graph.nodes.omr import omr_node
from graph.nodes.score_render import render_score_node
from graph.nodes.audio_gen import generate_audio_node
from graph.nodes.uploader import upload_files_node


def _route_by_image_type(state: GraphState) -> str:
    return state.get("image_type", "general")


def build_graph() -> StateGraph:
    g = StateGraph(GraphState)

    g.add_node("preprocess", preprocess_node)
    g.add_node("classify", classify_node)
    g.add_node("structural_extract", structural_extract_node)
    g.add_node("mood_parse", mood_parse_node)
    g.add_node("map_params", map_params_node)
    g.add_node("generate_score", generate_score_node)
    g.add_node("omr", omr_node)
    g.add_node("render_score", render_score_node)
    g.add_node("generate_audio", generate_audio_node)
    g.add_node("upload_files", upload_files_node)

    g.set_entry_point("preprocess")
    g.add_edge("preprocess", "classify")

    g.add_conditional_edges(
        "classify",
        _route_by_image_type,
        {
            "general": "structural_extract",
            "sheet_music": "omr",
        },
    )

    # 일반 사진 경로
    g.add_edge("structural_extract", "mood_parse")
    g.add_edge("mood_parse", "map_params")
    g.add_edge("map_params", "generate_score")
    g.add_edge("generate_score", "render_score")

    # 악보 사진 경로
    g.add_edge("omr", "render_score")

    # 합류
    g.add_edge("render_score", "generate_audio")
    g.add_edge("generate_audio", "upload_files")
    g.add_edge("upload_files", END)

    return g


graph = build_graph().compile()
