import base64
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

ANALYSIS_PROMPT = """
이 이미지를 음악적 관점에서 분석해줘.
다음 항목을 JSON으로 반환해줘 (다른 텍스트 없이 JSON만):

{
  "dominant_colors": ["색상 이름들"],
  "brightness": 0.0~1.0,
  "contrast": "low|medium|high",
  "pattern_complexity": "simple|moderate|complex",
  "rhythm_hint": "이미지 반복 구조 설명",
  "mood": "밝음|어두움|활기참|차분함|긴장됨|평화로움",
  "tempo_hint": "slow|medium|fast",
  "note_density": 0.0~1.0
}
"""


async def analyze_image(image_bytes: bytes) -> dict:
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": ANALYSIS_PROMPT},
                ],
            }
        ],
    )
    import json
    return json.loads(message.content[0].text)
