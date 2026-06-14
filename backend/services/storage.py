import os
from pathlib import Path

MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", "/app/media"))


def upload(path: str, data: bytes, _content_type: str = "") -> str:
    dest = MEDIA_ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    return f"{base_url}/media/{path}"


def public_url(path: str) -> str:
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    return f"{base_url}/media/{path}"
