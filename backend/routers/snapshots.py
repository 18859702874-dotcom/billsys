from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import AssetValueSnapshot, Asset
from schemas import SnapshotCreate, SnapshotOut

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


@router.post("", response_model=SnapshotOut)
def create_snapshot(data: SnapshotCreate, db: Session = Depends(get_db)):
    asset = db.query(Asset).get(data.asset_id)
    if not asset:
        raise HTTPException(404, "资产不存在")
    # 同一天同一资产只保留一条手动快照
    existing = db.query(AssetValueSnapshot).filter(
        AssetValueSnapshot.asset_id == data.asset_id,
        AssetValueSnapshot.date == data.date,
        AssetValueSnapshot.source == "manual"
    ).first()
    if existing:
        existing.value = data.value
        db.commit()
        db.refresh(existing)
        return existing
    snap = AssetValueSnapshot(
        asset_id=data.asset_id,
        date=data.date,
        value=data.value,
        source="manual"
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


@router.get("/{asset_id}", response_model=List[SnapshotOut])
def list_snapshots(asset_id: int, db: Session = Depends(get_db)):
    return db.query(AssetValueSnapshot).filter(
        AssetValueSnapshot.asset_id == asset_id
    ).order_by(AssetValueSnapshot.date.desc()).all()
