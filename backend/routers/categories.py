from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AssetCategory
from schemas import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(AssetCategory).order_by(AssetCategory.id.asc()).all()


@router.post("", response_model=CategoryOut)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "分类名称不能为空")

    exists = db.query(AssetCategory).filter(AssetCategory.name == name).first()
    if exists:
        raise HTTPException(400, "分类已存在")

    cat = AssetCategory(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(AssetCategory).get(cat_id)
    if not cat:
        raise HTTPException(404, "分类不存在")

    if data.name is not None:
        name = data.name.strip()
        if not name:
            raise HTTPException(400, "分类名称不能为空")
        exists = db.query(AssetCategory).filter(AssetCategory.name == name, AssetCategory.id != cat_id).first()
        if exists:
            raise HTTPException(400, "分类已存在")
        cat.name = name

    if "daily_budget" in data.model_fields_set:
        cat.daily_budget = data.daily_budget

    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(AssetCategory).get(cat_id)
    if not cat:
        raise HTTPException(404, "分类不存在")
    db.delete(cat)
    db.commit()
    return {"ok": True}
