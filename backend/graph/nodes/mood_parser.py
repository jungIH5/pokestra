import json
import os
from anthropic import Anthropic
from graph.state import GraphState

_client: Anthropic | None = None

_SYSTEM = "You are a music parameter extractor. Return only valid JSON, no explanation."

_PROMPT = """사용자가 원하는 음악 분위기를 음악 파라미터로 변환해줘.
사용자 입력: "{mood_input}"

다음 JSON만 반환해줘:
{{
  "scale": "C major|G major|D major|F major|A minor|E minor|D minor|B minor 중 하나",
  "tempo": 40~180 사이 정수,
  "base_dynamic": "pp|p|mp|mf|f|ff 중 하나"
}}

입력이 비어있거나 모호하면 기본값 C major, 90, mp를 사용해줘."""

_DEFAULTS = {"scale": "C major", "tempo": 90, "base_dynamic": "mp"}


def _client_instance() -> Anthropic:
    global _client
    if _client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise EnvironmentError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        _client = Anthropic(api_key=key)
    return _client


def mood_parse_node(state: GraphState) -> dict:
    """사용자 자연어 분위기 입력을 음악 파라미터로 변환한다."""
    mood_input = (state.get("mood_input") or "").strip() or "기본"

    msg = _client_instance().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        system=_SYSTEM,
        messages=[{"role": "user", "content": _PROMPT.format(mood_input=mood_input)}],
    )

    try:
        parsed = json.loads(msg.content[0].text)
    except (json.JSONDecodeError, IndexError):
        parsed = {}

    return {
        "music_params": {
            "scale": parsed.get("scale", _DEFAULTS["scale"]),
            "tempo": int(parsed.get("tempo", _DEFAULTS["tempo"])),
            "base_dynamic": parsed.get("base_dynamic", _DEFAULTS["base_dynamic"]),
        },
        "current_step": "분위기 파싱 완료",
    }
