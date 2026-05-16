import base64
import json
import os
from anthropic import Anthropic
from graph.state import GraphState

_client: Anthropic | None = None

PROMPT = """이 이미지를 음악적 관점에서 분석해줘.
다른 텍스트 없이 JSON만 반환해줘:

{
  "dominant_colors": ["색상 이름들"],
  "brightness": 0.0~1.0,
  "contrast": "low|medium|high",
  "pattern_complexity": "simple|moderate|complex",
  "rhythm_hint": "이미지 반복 구조 설명",
  "mood": "밝음|어두움|활기참|차분함|긴장됨|평화로움",
  "tempo_hint": "slow|medium|fast",
  "note_density": 0.0~1.0
}"""


def _client_instance() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def analyze_node(state: GraphState) -> dict:
    """Claude Vision으로 이미지의 시각 패턴을 분석한다."""
    b64 = base64.standard_b64encode(state["image_bytes"]).decode()
    attempts = state.get("analysis_attempts", 0) + 1

    msg = _client_instance().messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )

    try:
        analysis = json.loads(msg.content[0].text)
    except json.JSONDecodeError:
        analysis = {}

    return {
        "raw_analysis": analysis,
        "analysis_attempts": attempts,
        "current_step": f"패턴 분석 완료 (시도 {attempts}회)",
    }
