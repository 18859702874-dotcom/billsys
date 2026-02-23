from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Asset
from schemas import AssetCreate, AssetUpdate, AssetOut, DisposeRequest
from services.depreciation import calc_days_used, calc_daily_cost, calc_net_cost, calc_estimated_daily_cost

router = APIRouter(prefix="/api/assets", tags=["assets"])


def _enrich(asset: Asset) -> AssetOut:
    days = calc_days_used(asset)
    daily = calc_daily_cost(asset)
    net = calc_net_cost(asset)
    estimated = calc_estimated_daily_cost(asset)
    return AssetOut(
        **{c.name: getattr(asset, c.name) for c in asset.__table__.columns},
        category_name=asset.category.name if asset.category else "",
        days_used=days,
        daily_cost=daily,
        net_cost=net,
        estimated_daily_cost=estimated,
    )


@router.get("", response_model=List[AssetOut])
def list_assets(
    category_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Asset).options(joinedload(Asset.category))
    if category_id:
        q = q.filter(Asset.category_id == category_id)
    if status:
        q = q.filter(Asset.status == status)
    if search:
        q = q.filter(Asset.name.contains(search))
    assets = q.order_by(Asset.created_at.desc()).all()
    return [_enrich(a) for a in assets]


@router.post("", response_model=AssetOut)
def create_asset(data: AssetCreate, db: Session = Depends(get_db)):
    asset = Asset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    asset = db.query(Asset).options(joinedload(Asset.category)).get(asset.id)
    return _enrich(asset)


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).options(joinedload(Asset.category)).get(asset_id)
    if not asset:
        raise HTTPException(404, "资产不存在")
    return _enrich(asset)


@router.put("/{asset_id}", response_model=AssetOut)
def update_asset(asset_id: int, data: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).options(joinedload(Asset.category)).get(asset_id)
    if not asset:
        raise HTTPException(404, "资产不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    db.commit()
    db.refresh(asset)
    return _enrich(asset)


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).get(asset_id)
    if not asset:
        raise HTTPException(404, "资产不存在")
    db.delete(asset)
    db.commit()
    return {"ok": True}


@router.post("/{asset_id}/dispose", response_model=AssetOut)
def dispose_asset(asset_id: int, data: DisposeRequest, db: Session = Depends(get_db)):
    asset = db.query(Asset).options(joinedload(Asset.category)).get(asset_id)
    if not asset:
        raise HTTPException(404, "资产不存在")
    asset.status = "disposed"
    asset.disposed_date = data.disposed_date
    asset.disposed_reason = data.disposed_reason
    asset.recovery_amount = data.recovery_amount
    asset.recovery_date = data.recovery_date
    db.commit()
    db.refresh(asset)
    return _enrich(asset)


@router.post("/{asset_id}/restore", response_model=AssetOut)
def restore_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).options(joinedload(Asset.category)).get(asset_id)
    if not asset:
        raise HTTPException(404, "资产不存在")
    asset.status = "active"
    asset.disposed_date = None
    asset.disposed_reason = None
    asset.recovery_amount = None
    asset.recovery_date = None
    db.commit()
    db.refresh(asset)
    return _enrich(asset)
