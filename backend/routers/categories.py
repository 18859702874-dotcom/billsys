from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AssetCategory, Asset, Transaction
from schemas import CategoryCreate, CategoryUpdate, CategoryOut, CategoryTreeNode

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(AssetCategory).order_by(AssetCategory.sort_order.asc(), AssetCategory.id.asc()).all()


@router.get("/tree", response_model=List[CategoryTreeNode])
def get_categories_tree(db: Session = Depends(get_db)):
    all_cats = db.query(AssetCategory).order_by(AssetCategory.sort_order.asc(), AssetCategory.id.asc()).all()
    # Build tree in Python to avoid lazy-loading issues
    cat_map = {c.id: {"id": c.id, "name": c.name, "daily_budget": c.daily_budget,
                       "parent_id": c.parent_id, "sort_order": c.sort_order, "is_asset_related": c.is_asset_related, "children": []}
               for c in all_cats}
    roots = []
    for c in all_cats:
        node = cat_map[c.id]
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


@router.post("", response_model=CategoryOut)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "分类名称不能为空")

    exists = db.query(AssetCategory).filter(AssetCategory.name == name).first()
    if exists:
        raise HTTPException(400, "分类已存在")

    if data.parent_id:
        parent = db.query(AssetCategory).get(data.parent_id)
        if not parent:
            raise HTTPException(400, "父分类不存在")

    cat = AssetCategory(
        name=name,
        parent_id=data.parent_id,
        sort_order=data.sort_order,
        is_asset_related=data.is_asset_related,
    )
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

    if "parent_id" in data.model_fields_set:
        if data.parent_id == cat_id:
            raise HTTPException(400, "不能将分类设为自身的父分类")
        cat.parent_id = data.parent_id

    if data.sort_order is not None:
        cat.sort_order = data.sort_order

    if "is_asset_related" in data.model_fields_set:
        cat.is_asset_related = bool(data.is_asset_related)

    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(AssetCategory).get(cat_id)
    if not cat:
        raise HTTPException(404, "分类不存在")

    # 检查子分类
    children_count = db.query(AssetCategory).filter(AssetCategory.parent_id == cat_id).count()
    if children_count > 0:
        raise HTTPException(400, f"该分类下还有 {children_count} 个子分类，请先删除子分类")

    # 检查关联资产
    asset_count = db.query(Asset).filter(Asset.category_id == cat_id).count()
    if asset_count > 0:
        raise HTTPException(400, f"该分类下还有 {asset_count} 条资产，无法删除")

    # 检查关联交易
    tx_count = db.query(Transaction).filter(Transaction.category_id == cat_id).count()
    if tx_count > 0:
        raise HTTPException(400, f"该分类下还有 {tx_count} 条交易记录，无法删除")

    db.delete(cat)
    db.commit()
    return {"ok": True}
