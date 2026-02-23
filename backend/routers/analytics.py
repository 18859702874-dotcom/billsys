from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Asset
from schemas import TrendPoint, CategoryDistribution, CostSummary
from services.analytics import (
    get_total_daily_cost_trend, get_category_distribution, get_cost_summary,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/daily-cost-trend", response_model=List[TrendPoint])
def daily_cost_trend(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    if not end:
        end = date.today()
    if not start:
        earliest = db.query(func.min(Asset.purchase_date)).scalar()
        start = date(earliest.year, earliest.month, 1) if earliest else date(end.year - 1, end.month, 1)
    return get_total_daily_cost_trend(db, start, end)


@router.get("/category-distribution", response_model=List[CategoryDistribution])
def category_distribution(db: Session = Depends(get_db)):
    return get_category_distribution(db)


@router.get("/cost-summary", response_model=CostSummary)
def cost_summary(db: Session = Depends(get_db)):
    return get_cost_summary(db)
