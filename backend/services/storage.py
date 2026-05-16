import os
from supabase import create_client, Client

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


def upload(path: str, data: bytes, content_type: str) -> str:
    """파일을 Supabase Storage에 업로드하고 공개 URL을 반환한다."""
    bucket = os.environ["SUPABASE_BUCKET"]
    client = _get_client()
    client.storage.from_(bucket).upload(
        path=path,
        file=data,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return public_url(path)


def public_url(path: str) -> str:
    bucket = os.environ["SUPABASE_BUCKET"]
    return _get_client().storage.from_(bucket).get_public_url(path)
