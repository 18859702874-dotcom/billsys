import asyncio
import base64
import json
import os
from datetime import date as date_type
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional

import httpx
from dotenv import dotenv_values
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models import ClothingItem
from schemas import ClothingBatchCreateRequest, ClothingOut
from services.storage import delete_by_url, upload_bytes

router = APIRouter(prefix="/api/clothing", tags=["clothing"])

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

VALID_CATEGORIES = ["上衣", "下装", "外套", "鞋子", "配饰"]
VALID_SEASONS = ["春", "夏", "秋", "冬", "四季"]
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _as_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _safe_decimal(value: Any) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _safe_int(value: Any, default: int = 1) -> int:
    try:
        n = int(value)
        return n if n > 0 else default
    except (TypeError, ValueError):
        return default


def _normalize_category(value: Any) -> str:
    text = _as_str(value)
    if text in VALID_CATEGORIES:
        return text
    return "上衣"


def _normalize_season(value: Any) -> Optional[str]:
    text = _as_str(value)
    if text in VALID_SEASONS:
        return text
    return None


def _parse_date(value: Optional[str]) -> Optional[date_type]:
    if not value:
        return None
    try:
        return date_type.fromisoformat(value)
    except ValueError:
        raise HTTPException(400, "购买日期格式应为 YYYY-MM-DD")


def _normalize_order(data: Any) -> dict:
    if not isinstance(data, dict):
        return {}

    order = {
        "order_no": _as_str(data.get("order_no")),
        "purchase_date": _as_str(data.get("purchase_date")),
        "purchase_channel": _as_str(data.get("purchase_channel")),
        "total_amount": _safe_decimal(data.get("total_amount")),
    }
    return {k: v for k, v in order.items() if v is not None}


def _normalize_items(parsed: Any, order: dict) -> list[dict]:
    raw_items: list[dict] = []

    if isinstance(parsed, dict):
        if isinstance(parsed.get("items"), list):
            raw_items = [x for x in parsed["items"] if isinstance(x, dict)]
        elif any(k in parsed for k in ("name", "category", "purchase_price", "purchase_date")):
            raw_items = [parsed]

    items: list[dict] = []
    for raw in raw_items:
        name = _as_str(raw.get("name"))
        if not name:
            continue

        qty = _safe_int(raw.get("qty"), 1)
        amount = _safe_decimal(raw.get("amount"))
        unit_price = _safe_decimal(raw.get("purchase_price") or raw.get("unit_price"))

        if unit_price is None and amount is not None and qty > 0:
            try:
                unit_price = (amount / Decimal(qty)).quantize(Decimal("0.01"))
            except (InvalidOperation, ZeroDivisionError):
                unit_price = None

        item = {
            "name": name,
            "category": _normalize_category(raw.get("category")),
            "color": _as_str(raw.get("color")),
            "brand": _as_str(raw.get("brand")),
            "purchase_price": unit_price,
            "purchase_date": _as_str(raw.get("purchase_date")) or order.get("purchase_date"),
            "purchase_channel": _as_str(raw.get("purchase_channel")) or order.get("purchase_channel"),
            "season": _normalize_season(raw.get("season")),
            "qty": qty,
            "amount": amount,
            "notes": _as_str(raw.get("notes")),
        }

        items.append(item)

    return items

def _build_model_candidates(env: dict) -> list[str]:
    primary = (env.get("GEMINI_TEXT_MODEL") or env.get("GEMINI_MODEL") or "gemini-2.5-flash-lite").strip()
    fallback_raw = env.get("GEMINI_TEXT_FALLBACK_MODELS") or env.get("GEMINI_FALLBACK_MODELS") or "gemini-2.5-flash,gemini-2.0-flash-lite"
    fallback = [m.strip() for m in fallback_raw.split(",") if m.strip()]
    merged: list[str] = []
    for model in [primary, *fallback]:
        if model not in merged:
            merged.append(model)
    if not merged:
        merged.append("gemini-2.5-flash-lite")
    return merged


async def _call_gemini_with_retry(payload: dict, api_key: str, models: list[str]) -> dict:
    max_attempts = 3
    backoff_seconds = [0.6, 1.4, 2.8]
    errors: list[str] = []

    async with httpx.AsyncClient(timeout=45) as client:
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
                    return resp.json()

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
        "Gemini 服务繁忙，已自动重试并切换模型仍失败。"
        f" 尝试模型: {', '.join(models)}。最近错误: {errors[-1] if errors else 'unknown'}",
    )


@router.post("/recognize")
async def recognize_clothing(image: UploadFile = File(...)):
    """通过订单截图 AI 识别服装信息，支持多商品明细。"""
    env = dotenv_values(ENV_PATH)
    api_key = (env.get("GEMINI_TEXT_API_KEY") or env.get("GEMINI_API_KEY") or "").strip()
    models = _build_model_candidates(env)

    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(400, "请先在 backend/.env 中配置 GEMINI_TEXT_API_KEY 或 GEMINI_API_KEY")

    image_bytes = await image.read()
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    content_type = image.content_type or "image/jpeg"

    prompt = """
你是服装订单识别助手。请分析这张订单截图或服装图片，识别订单信息与商品明细。

请严格返回 JSON（不要 markdown 代码块），格式如下：
{
  "order": {
    "order_no": "订单号，没有则 null",
    "purchase_date": "购买日期，YYYY-MM-DD，没有则 null",
    "purchase_channel": "购买渠道，如淘宝/京东，没有则 null",
    "total_amount": 订单总金额数字，没有则 null
  },
  "items": [
    {
      "name": "商品名",
      "category": "上衣/下装/外套/鞋子/配饰 之一，无法判断可给最接近",
      "color": "颜色，没有则 null",
      "brand": "品牌，没有则 null",
      "purchase_price": 单件价格数字，没有则 null,
      "qty": 数量整数，没有则 1,
      "amount": 小计金额数字，没有则 null,
      "purchase_date": "购买日期，YYYY-MM-DD，没有则 null",
      "purchase_channel": "购买渠道，没有则 null",
      "season": "春/夏/秋/冬/四季 之一，没有则 null",
      "notes": "补充信息，没有则 null"
    }
  ]
}

要求：
1) items 必须是数组，即使只有 1 个商品。
2) 不要返回数组外的解释文本。
""".strip()

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": content_type,
                        "data": b64_image,
                    }
                },
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048,
        },
    }


    try:
        data = await _call_gemini_with_retry(payload, api_key, models)
        parts = data["candidates"][0]["content"]["parts"]
        text = ""
        for part in parts:
            if isinstance(part, dict) and part.get("text"):
                text = part["text"]
                break

        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        parsed = json.loads(text)
    except HTTPException:
        raise
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(502, f"AI 返回结果解析失败: {exc}")

    order = _normalize_order(parsed.get("order") if isinstance(parsed, dict) else {})
    items = _normalize_items(parsed, order)
    if not items:
        raise HTTPException(422, "未识别到可导入的商品明细")

    return {"order": order, "items": items}


@router.get("", response_model=List[ClothingOut])
def list_clothing(
    category: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(ClothingItem)
    if category:
        q = q.filter(ClothingItem.category == category)
    if season:
        q = q.filter(ClothingItem.season == season)
    if search:
        q = q.filter(ClothingItem.name.contains(search))
    return q.order_by(ClothingItem.created_at.desc()).all()


@router.post("", response_model=ClothingOut)
def create_clothing(
    name: str = Form(...),
    category: str = Form(...),
    color: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    purchase_price: Optional[float] = Form(None),
    purchase_date: Optional[str] = Form(None),
    purchase_channel: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    image_url = None
    if image and image.filename:
        image_bytes = image.file.read()
        image_url = upload_bytes(
            folder="clothing",
            filename=image.filename,
            data=image_bytes,
            content_type=image.content_type,
        )

    item = ClothingItem(
        name=name,
        category=category,
        color=color,
        brand=brand,
        purchase_price=purchase_price,
        purchase_date=_parse_date(purchase_date),
        purchase_channel=purchase_channel,
        image_url=image_url,
        season=season,
        notes=notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/batch", response_model=List[ClothingOut])
def create_clothing_batch(payload: ClothingBatchCreateRequest, db: Session = Depends(get_db)):
    created: list[ClothingItem] = []

    for row in payload.items:
        item = ClothingItem(
            name=row.name,
            category=row.category,
            color=row.color,
            brand=row.brand,
            purchase_price=row.purchase_price,
            purchase_date=row.purchase_date,
            purchase_channel=row.purchase_channel,
            season=row.season,
            notes=row.notes,
        )
        db.add(item)
        created.append(item)

    db.commit()
    for item in created:
        db.refresh(item)
    return created


@router.get("/{item_id:int}", response_model=ClothingOut)
def get_clothing(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ClothingItem).get(item_id)
    if not item:
        raise HTTPException(404, "服装不存在")
    return item


@router.put("/{item_id:int}", response_model=ClothingOut)
def update_clothing(
    item_id: int,
    name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    purchase_price: Optional[float] = Form(None),
    purchase_date: Optional[str] = Form(None),
    purchase_channel: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    item = db.query(ClothingItem).get(item_id)
    if not item:
        raise HTTPException(404, "服装不存在")

    old_image_url = item.image_url
    if image and image.filename:
        image_bytes = image.file.read()
        item.image_url = upload_bytes(
            folder="clothing",
            filename=image.filename,
            data=image_bytes,
            content_type=image.content_type,
        )

    fields = {
        "name": name,
        "category": category,
        "color": color,
        "brand": brand,
        "purchase_price": purchase_price,
        "purchase_channel": purchase_channel,
        "season": season,
        "notes": notes,
    }
    for key, value in fields.items():
        if value is not None:
            setattr(item, key, value)

    if purchase_date is not None:
        item.purchase_date = _parse_date(purchase_date)

    db.commit()
    db.refresh(item)
    if image and image.filename and old_image_url and old_image_url != item.image_url:
        delete_by_url(old_image_url)
    return item


@router.delete("/{item_id:int}")
def delete_clothing(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ClothingItem).get(item_id)
    if not item:
        raise HTTPException(404, "服装不存在")

    delete_by_url(item.image_url)

    db.delete(item)
    db.commit()
    return {"ok": True}
