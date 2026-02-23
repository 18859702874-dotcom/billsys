from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services.storage import get_object_stream, is_r2_enabled

router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/{object_key:path}")
def get_media(object_key: str):
    if not is_r2_enabled():
        raise HTTPException(404, "R2 未启用，媒体代理不可用")

    obj = get_object_stream(object_key)
    body = obj["Body"]
    content_type = obj.get("ContentType") or "application/octet-stream"

    return StreamingResponse(
        body.iter_chunks(),
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
