import io
from PIL import Image
from graph.state import GraphState

MAX_SIZE = (1920, 1920)


def preprocess_node(state: GraphState) -> dict:
    """이미지를 최대 1920x1920으로 리사이즈하고 JPEG로 정규화한다."""
    img = Image.open(io.BytesIO(state["image_bytes"]))

    if img.mode != "RGB":
        img = img.convert("RGB")

    img.thumbnail(MAX_SIZE, Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)

    return {
        "image_bytes": buf.getvalue(),
        "current_step": "이미지 전처리 완료",
    }
