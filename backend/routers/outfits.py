from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Outfit, OutfitItem, ClothingItem
from schemas import OutfitCreate, OutfitUpdate, OutfitOut

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


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


@router.post("", response_model=OutfitOut)
def create_outfit(data: OutfitCreate, db: Session = Depends(get_db)):
    outfit = Outfit(
        name=data.name,
        occasion=data.occasion,
        season=data.season,
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
