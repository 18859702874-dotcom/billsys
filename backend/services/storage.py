import mimetypes
import os
import uuid
from typing import Optional
from urllib.parse import quote, unquote, urlparse

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import dotenv_values
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
MEDIA_PREFIX = "/api/media/"


def _env() -> dict:
    cfg = dotenv_values(ENV_PATH)
    return {
        "account_id": (cfg.get("CF_ACCOUNT_ID") or "").strip(),
        "bucket": (cfg.get("R2_BUCKET") or "").strip(),
        "access_key_id": (cfg.get("R2_ACCESS_KEY_ID") or "").strip(),
        "secret_access_key": (cfg.get("R2_SECRET_ACCESS_KEY") or "").strip(),
        "public_base_url": (cfg.get("R2_PUBLIC_BASE_URL") or "").strip().rstrip("/"),
    }


def is_r2_enabled() -> bool:
    cfg = _env()
    return bool(cfg["account_id"] and cfg["bucket"] and cfg["access_key_id"] and cfg["secret_access_key"])


def _client():
    cfg = _env()
    if not is_r2_enabled():
        raise HTTPException(500, "R2 未配置完整，请检查 backend/.env")

    endpoint = f"https://{cfg['account_id']}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=cfg["access_key_id"],
        aws_secret_access_key=cfg["secret_access_key"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def _safe_ext(filename: Optional[str], content_type: Optional[str]) -> str:
    ext = os.path.splitext(filename or "")[1].lower().strip()
    if ext:
        return ext
    guessed = mimetypes.guess_extension(content_type or "") or ""
    if guessed:
        return guessed
    return ".bin"


def _build_key(folder: str, filename: str, content_type: Optional[str]) -> str:
    ext = _safe_ext(filename, content_type)
    clean_folder = folder.strip("/").replace("\\", "/")
    return f"{clean_folder}/{uuid.uuid4().hex}{ext}"


def _put_local(folder: str, filename: str, data: bytes) -> str:
    ext = _safe_ext(filename, None)
    clean_folder = folder.strip("/")
    os.makedirs(os.path.join(UPLOADS_DIR, clean_folder), exist_ok=True)
    local_name = f"{uuid.uuid4().hex}{ext}"
    local_path = os.path.join(UPLOADS_DIR, clean_folder, local_name)
    with open(local_path, "wb") as f:
        f.write(data)
    return f"/uploads/{clean_folder}/{local_name}"


def upload_bytes(folder: str, filename: str, data: bytes, content_type: Optional[str] = None) -> str:
    if not data:
        raise HTTPException(400, "上传文件为空")

    if not is_r2_enabled():
        return _put_local(folder, filename, data)

    cfg = _env()
    object_key = _build_key(folder, filename, content_type)
    try:
        _client().put_object(
            Bucket=cfg["bucket"],
            Key=object_key,
            Body=data,
            ContentType=content_type or "application/octet-stream",
        )
    except ClientError as exc:
        raise HTTPException(502, f"上传 R2 失败: {exc.response.get('Error', {}).get('Message', 'unknown')}") from exc

    # Prefer public base url if configured, otherwise use backend proxy path.
    if cfg["public_base_url"]:
        return f"{cfg['public_base_url']}/{object_key}"
    return f"{MEDIA_PREFIX}{quote(object_key, safe='/')}"


def get_object_stream(object_key: str):
    cfg = _env()
    try:
        return _client().get_object(Bucket=cfg["bucket"], Key=object_key)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"NoSuchKey", "404"}:
            raise HTTPException(404, "图片不存在") from exc
        raise HTTPException(502, "读取 R2 图片失败") from exc


def _extract_key_from_url(image_url: str) -> Optional[str]:
    if not image_url:
        return None

    if image_url.startswith(MEDIA_PREFIX):
        return unquote(image_url[len(MEDIA_PREFIX):])

    cfg = _env()
    public = cfg["public_base_url"]
    if public and image_url.startswith(public + "/"):
        return image_url[len(public) + 1:]

    parsed = urlparse(image_url)
    if parsed.scheme and parsed.netloc and ".r2.dev" in parsed.netloc:
        return parsed.path.lstrip("/")
    return None


def delete_by_url(image_url: Optional[str]) -> None:
    if not image_url:
        return

    # Local file cleanup (legacy path and R2-disabled mode).
    if image_url.startswith("/uploads/"):
        local_path = os.path.join(BASE_DIR, image_url.lstrip("/"))
        if os.path.exists(local_path):
            os.remove(local_path)
        return

    key = _extract_key_from_url(image_url)
    if not key:
        return
    if not is_r2_enabled():
        return

    cfg = _env()
    try:
        _client().delete_object(Bucket=cfg["bucket"], Key=key)
    except ClientError:
        # Best-effort cleanup, do not block user flow.
        return
