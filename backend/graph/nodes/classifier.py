import base64
import json
import os
from anthropic import Anthropic
from graph.state import GraphState

_client: Anthropic | None = None

PROMPT = """이 이미지가 악보(sheet music)인지 일반 사진인지 판별해줘.
악보 기준: 오선지·음표·쉼표·박자표·조표 등 음악 기호가 명확히 보이면 sheet_music.
JSON만 반환해줘: {"type": "sheet_music"} 또는 {"type": "general"}"""


def _client_instance() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def classify_node(state: GraphState) -> dict:
    """Claude Vision으로 악보 사진 여부를 판별한다."""
    b64 = base64.standard_b64encode(state["image_bytes"]).decode()
    msg = _client_instance().messages.create(
        model="claude-opus-4-7",
        max_tokens=32,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    result = json.loads(msg.content[0].text)
    image_type = result.get("type", "general")
    return {
        "image_type": image_type,
        "current_step": f"이미지 분류 완료: {image_type}",
    }
