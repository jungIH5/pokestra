import base64
import json
import os
import redis as redis_lib
from celery_app import celery_app
from graph.workflow import graph
from graph.state import GraphState

_redis: redis_lib.Redis | None = None

# 노드 이름 → 진행률 매핑
PROGRESS_MAP = {
    "preprocess": 5,
    "classify": 15,
    "analyze": 35,
    "validate": 45,
    "map_params": 55,
    "omr": 50,
    "generate_score": 65,
    "render_score": 75,
    "generate_audio": 88,
    "upload_files": 97,
}


def _redis_client() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(os.environ["REDIS_URL"])
    return _redis


def _set_status(job_id: str, payload: dict, ttl: int = 3600) -> None:
    _redis_client().setex(f"job:{job_id}", ttl, json.dumps(payload, ensure_ascii=False))


@celery_app.task(bind=True, name="worker.run_analysis_task")
def run_analysis_task(self, job_id: str, image_b64: str) -> None:
    """LangGraph 파이프라인을 실행하고 각 노드 완료 시 Redis에 상태를 업데이트한다."""
    _set_status(job_id, {"status": "running", "current_step": "시작", "progress": 0})

    try:
        image_bytes = base64.b64decode(image_b64)
        initial_state: GraphState = {
            "job_id": job_id,
            "image_bytes": image_bytes,
            "image_type": None,
            "raw_analysis": None,
            "analysis_attempts": 0,
            "music_params": None,
            "omr_musicxml": None,
            "final_musicxml": None,
            "midi_path": None,
            "score_png_path": None,
            "audio_path": None,
            "score_url": None,
            "audio_url": None,
            "current_step": "시작",
            "error": None,
        }

        # initial_state를 기반으로 누적하여 전체 최종 상태를 유지한다.
        # graph.stream() 기본 모드("updates")는 노드별 partial delta만 반환하므로
        # 단순히 final_state = node_output으로 덮어쓰면 이전 노드의 값이 사라진다.
        final_state: dict = dict(initial_state)
        graph_ran = False
        for event in graph.stream(initial_state):
            for node_name, node_output in event.items():
                final_state.update(node_output)
                progress = PROGRESS_MAP.get(node_name, 50)
                step = node_output.get("current_step", node_name)
                _set_status(job_id, {
                    "status": "running",
                    "current_step": step,
                    "progress": progress,
                })
                graph_ran = True

        if not graph_ran:
            raise RuntimeError("그래프가 결과를 반환하지 않았습니다.")

        result = {
            "score_url": final_state.get("score_url"),
            "audio_url": final_state.get("audio_url"),
            "image_type": final_state.get("image_type", "general"),
            "music_params": final_state.get("music_params"),
        }

        _set_status(job_id, {
            "status": "done",
            "current_step": "완료",
            "progress": 100,
            "result": result,
            "error": None,
        }, ttl=86400)  # 완료된 잡은 24시간 보관

    except Exception as exc:
        _set_status(job_id, {
            "status": "failed",
            "current_step": "오류 발생",
            "progress": 0,
            "error": str(exc),
        })
        raise
