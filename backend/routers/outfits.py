import asyncio
import base64
import mimetypes
import os
from typing import Any, List, Optional
from urllib.parse import unquote

import httpx
from dotenv import dotenv_values
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Outfit, OutfitItem, ClothingItem
from schemas import (
    OutfitCreate,
    OutfitOut,
    OutfitRenderRequest,
    OutfitRenderResponse,
    OutfitUpdate,
)
from services.storage import BASE_DIR, MEDIA_PREFIX, get_object_stream, upload_bytes

router = APIRouter(prefix="/api/outfits", tags=["outfits"])

ENV_PATH = os.path.join(BASE_DIR, ".env")
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _load_outfit(db: Session, outfit_id: int) -> Outfit:
    outfit = (
        db.query(Outfit)
        .options(joinedload(Outfit.items).joinedload(OutfitItem.clothing))
        .filter(Outfit.id == outfit_id)
        .first()
    )
    if not outfit:
        raise HTTPException(404, "搭配不存在")
    return outfit


@router.get("", response_model=List[OutfitOut])
def list_outfits(
    occasion: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Outfit).options(joinedload(Outfit.items).joinedload(OutfitItem.clothing))
    if occasion:
        q = q.filter(Outfit.occasion == occasion)
    if season:
        q = q.filter(Outfit.season == season)
    return q.order_by(Outfit.created_at.desc()).all()


def _build_image_model_candidates(env: dict) -> list[str]:
    # Keep legacy aliases compatible with newer model IDs.
    alias = {
        "gemini-3.0-generate-001": "gemini-3-pro-image-preview",
        "gemini-2.5-flash-image-preview": "gemini-2.5-flash-image",
        "gemini-2.0-flash-preview-image-generation": "gemini-2.0-flash-exp-image-generation",
    }

    def normalize(name: str) -> str:
        cleaned = (name or "").strip()
        return alias.get(cleaned, cleaned)

    primary = normalize(env.get("GEMINI_IMAGE_MODEL") or env.get("GEMINI_MODEL") or "gemini-3-pro-image-preview")
    fallback_raw = env.get("GEMINI_IMAGE_FALLBACK_MODELS") or (
        "gemini-2.5-flash-image,gemini-2.0-flash-exp-image-generation"
    )
    fallback = [normalize(m) for m in fallback_raw.split(",") if m.strip()]
    merged: list[str] = []
    for model in [primary, *fallback]:
        if model and model not in merged:
            merged.append(model)
    if not merged:
        merged.append("gemini-3-pro-image-preview")
    return merged


async def _call_gemini_image_with_retry(payload: dict, api_key: str, models: list[str]) -> tuple[dict, str]:
    max_attempts = 3
    backoff_seconds = [0.6, 1.4, 2.8]
    errors: list[str] = []

    async with httpx.AsyncClient(timeout=75) as client:
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            for attempt in range(1, max_attempts + 1):
                try:
                    resp = await client.post(url, json=payload)
                except httpx.RequestError as exc:
                    if attempt < max_attempts:
                        await asyncio.sleep(backoff_seconds[attempt - 1])
                        continue
                    errors.append(f"{model} network_error: {exc}")
                    break

                if resp.status_code == 200:
                    return resp.json(), model

                body_preview = resp.text[:180].replace("\n", " ")
                if resp.status_code in RETRYABLE_STATUS:
                    if attempt < max_attempts:
                        await asyncio.sleep(backoff_seconds[attempt - 1])
                        continue
                    errors.append(f"{model} {resp.status_code}: {body_preview}")
                    break

                errors.append(f"{model} {resp.status_code}: {body_preview}")
                break

    raise HTTPException(
        502,
        "Gemini 图像生成失败，已自动重试并切换模型仍未成功。"
        f" 尝试模型: {', '.join(models)}。最近错误: {errors[-1] if errors else 'unknown'}",
    )


def _guess_mime_from_url(image_url: str) -> str:
    ext = os.path.splitext(image_url.split("?")[0])[1].lower()
    mime = mimetypes.types_map.get(ext)
    return mime or "image/jpeg"


async def _load_source_image(image_url: str) -> tuple[bytes, str]:
    if image_url.startswith("/uploads/"):
        local_path = os.path.join(BASE_DIR, image_url.lstrip("/"))
        if not os.path.exists(local_path):
            raise HTTPException(400, f"图片不存在: {image_url}")
        with open(local_path, "rb") as f:
            data = f.read()
        if not data:
            raise HTTPException(400, f"图片为空: {image_url}")
        return data, _guess_mime_from_url(image_url)

    if image_url.startswith(MEDIA_PREFIX):
        object_key = unquote(image_url[len(MEDIA_PREFIX):])
        obj = get_object_stream(object_key)
        body = obj["Body"].read()
        if not body:
            raise HTTPException(400, f"图片为空: {image_url}")
        content_type = obj.get("ContentType") or _guess_mime_from_url(image_url)
        return body, content_type

    if image_url.startswith("http://") or image_url.startswith("https://"):
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(image_url)
        if resp.status_code != 200:
            raise HTTPException(400, f"拉取图片失败: {image_url}")
        body = resp.content
        if not body:
            raise HTTPException(400, f"图片为空: {image_url}")
        header_ct = (resp.headers.get("content-type") or "").split(";")[0].strip()
        return body, header_ct or _guess_mime_from_url(image_url)

    raise HTTPException(400, f"不支持的图片地址: {image_url}")


def _build_render_prompt(items: list[dict[str, Any]], custom_prompt: Optional[str]) -> str:
    item_lines = "\n".join([f"- {idx + 1}. {row['category']}：{row['name']}" for idx, row in enumerate(items)])
    user_prompt = custom_prompt.strip() if custom_prompt else ""

    base_prompt = f"""
你是专业时尚视觉设计师。请使用这些单品图片生成 1 张完整“整身穿搭图”。

必须满足：
1) 保留每件单品的核心特征（颜色、版型、材质纹理、图案）。
2) 生成真实自然的人体上身效果，完整展示头到脚的穿搭比例。
3) 人像姿态自然，背景简洁干净，适合商品展示。
4) 只输出一张图片，不要拼贴，不要多张图。
5) 避免改变单品颜色，避免过度艺术化。

单品清单：
{item_lines}
""".strip()

    if not user_prompt:
        return base_prompt

    return f"{base_prompt}\n\n补充要求：\n{user_prompt}"


def _extract_generated_image(data: dict) -> tuple[bytes, str, Optional[str]]:
    candidates = data.get("candidates") or []
    text_parts: list[str] = []

    for cand in candidates:
        content = cand.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            text = (part.get("text") or "").strip()
            if text:
                text_parts.append(text)

            inline = part.get("inlineData") or part.get("inline_data") or {}
            image_b64 = inline.get("data")
            if not image_b64:
                continue

            mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            try:
                image_bytes = base64.b64decode(image_b64)
            except Exception:
                continue
            if image_bytes:
                merged_text = "\n".join(text_parts).strip() or None
                return image_bytes, mime_type, merged_text

    text_preview = " ".join(text_parts).strip()
    if text_preview:
        text_preview = text_preview[:120]
    raise HTTPException(502, f"Gemini 未返回图片数据。{f'返回文本: {text_preview}' if text_preview else ''}")


@router.post("/render-image", response_model=OutfitRenderResponse)
async def render_outfit_image(data: OutfitRenderRequest):
    env = dotenv_values(ENV_PATH)
    api_key = (env.get("GEMINI_IMAGE_API_KEY") or env.get("GEMINI_API_KEY") or "").strip()
    models = _build_image_model_candidates(env)

    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(400, "请先在 backend/.env 中配置 GEMINI_IMAGE_API_KEY 或 GEMINI_API_KEY")

    source_items: list[dict[str, Any]] = []
    for row in data.items:
        image_bytes, mime_type = await _load_source_image(row.image_url)
        source_items.append(
            {
                "name": row.name,
                "category": row.category,
                "image_url": row.image_url,
                "image_bytes": image_bytes,
                "mime_type": mime_type,
            }
        )

    prompt = _build_render_prompt(source_items, data.prompt)

    parts: list[dict[str, Any]] = [{"text": prompt}]
    for idx, row in enumerate(source_items):
        parts.append({"text": f"单品 {idx + 1}: {row['category']} / {row['name']}"})
        parts.append(
            {
                "inlineData": {
                    "mimeType": row["mime_type"],
                    "data": base64.b64encode(row["image_bytes"]).decode("utf-8"),
                }
            }
        )

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.9,
        },
    }

    response_data, used_model = await _call_gemini_image_with_retry(payload, api_key, models)
    image_bytes, image_mime, text = _extract_generated_image(response_data)
    ext = mimetypes.guess_extension(image_mime) or ".png"
    image_url = upload_bytes(
        folder="outfits/ai",
        filename=f"rendered_outfit{ext}",
        data=image_bytes,
        content_type=image_mime,
    )

    return OutfitRenderResponse(
        image_url=image_url,
        model=used_model,
        text=text,
    )


@router.post("", response_model=OutfitOut)
def create_outfit(data: OutfitCreate, db: Session = Depends(get_db)):
    outfit = Outfit(
        name=data.name,
        occasion=data.occasion,
        season=data.season,
        rendered_image_url=data.rendered_image_url,
        notes=data.notes,
    )
    db.add(outfit)
    db.flush()

    for item_data in data.items:
        clothing = db.query(ClothingItem).get(item_data.clothing_id)
        if not clothing:
            raise HTTPException(400, f"服装 {item_data.clothing_id} 不存在")
        oi = OutfitItem(
            outfit_id=outfit.id,
            clothing_id=item_data.clothing_id,
            position_x=item_data.position_x,
            position_y=item_data.position_y,
            scale=item_data.scale,
        )
        db.add(oi)

    db.commit()
    return _load_outfit(db, outfit.id)


@router.get("/{outfit_id}", response_model=OutfitOut)
def get_outfit(outfit_id: int, db: Session = Depends(get_db)):
    return _load_outfit(db, outfit_id)


@router.put("/{outfit_id}", response_model=OutfitOut)
def update_outfit(outfit_id: int, data: OutfitUpdate, db: Session = Depends(get_db)):
    outfit = _load_outfit(db, outfit_id)

    for k, v in data.model_dump(exclude_unset=True, exclude={"items"}).items():
        setattr(outfit, k, v)

    if data.items is not None:
        # Replace all items
        for old_item in outfit.items:
            db.delete(old_item)
        db.flush()

        for item_data in data.items:
            clothing = db.query(ClothingItem).get(item_data.clothing_id)
            if not clothing:
                raise HTTPException(400, f"服装 {item_data.clothing_id} 不存在")
            oi = OutfitItem(
                outfit_id=outfit.id,
                clothing_id=item_data.clothing_id,
                position_x=item_data.position_x,
                position_y=item_data.position_y,
                scale=item_data.scale,
            )
            db.add(oi)

    db.commit()
    return _load_outfit(db, outfit.id)


@router.delete("/{outfit_id}")
def delete_outfit(outfit_id: int, db: Session = Depends(get_db)):
    outfit = db.query(Outfit).get(outfit_id)
    if not outfit:
        raise HTTPException(404, "搭配不存在")
    db.delete(outfit)
    db.commit()
    return {"ok": True}
