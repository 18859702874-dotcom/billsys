from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from sqlalchemy.orm import Session, joinedload

from models import Asset
from schemas import TrendPoint, CategoryDistribution, CategoryAssetItem, CostSummary
from services.depreciation import calc_daily_cost, calc_days_used, calc_estimated_daily_cost


def _month_end(year: int, month: int) -> date:
    """返回指定年月的最后一天"""
    if month == 12:
        return date(year + 1, 1, 1) - timedelta(days=1)
    return date(year, month + 1, 1) - timedelta(days=1)


def get_total_daily_cost_trend(db: Session, start_date: date, end_date: date) -> List[TrendPoint]:
    """按月统计所有在用资产的日均总费用趋势，取每月末快照"""
    assets = db.query(Asset).options(joinedload(Asset.category)).all()

    points = []
    year, month = start_date.year, start_date.month
    while True:
        snap = _month_end(year, month)
        if snap > end_date:
            snap = end_date
        if snap < start_date:
            break
        total = Decimal("0")
        for asset in assets:
            if asset.purchase_date > snap:
                continue
            if asset.status == "disposed" and asset.disposed_date and snap > asset.disposed_date:
                continue
            total += _comprehensive_daily_cost(asset, snap)
        points.append(TrendPoint(date=date(year, month, 1), value=total))
        if year == end_date.year and month == end_date.month:
            break
        month += 1
        if month > 12:
            month = 1
            year += 1
    return points


def _comprehensive_daily_cost(asset: Asset, target_date: date = None) -> Decimal:
    """综合每日成本：
    1) 在用资产若实际使用天数超过预计使用天数，则为 0
    2) 否则取 daily_cost 和 estimated_daily_cost 中较小值
    """
    if asset.status != "disposed" and asset.expected_days:
        days_used = calc_days_used(asset, target_date)
        if days_used > asset.expected_days:
            return Decimal("0")

    actual = calc_daily_cost(asset, target_date)
    estimated = calc_estimated_daily_cost(asset)
    if estimated is not None and actual > estimated:
        return estimated
    return actual


def get_category_distribution(db: Session) -> List[CategoryDistribution]:
    """各分类资产的费用分布"""
    assets = db.query(Asset).options(joinedload(Asset.category)).filter(
        Asset.status == "active"
    ).all()

    cat_map: dict[str, dict] = {}
    for asset in assets:
        cat_name = asset.category.name if asset.category else "未分类"
        if cat_name not in cat_map:
            cat_map[cat_name] = {"total_cost": Decimal("0"), "count": 0, "total_daily": Decimal("0"), "assets": []}
        daily = _comprehensive_daily_cost(asset)
        cat_map[cat_name]["total_cost"] += Decimal(str(asset.purchase_price))
        cat_map[cat_name]["count"] += 1
        cat_map[cat_name]["total_daily"] += daily
        cat_map[cat_name]["assets"].append(CategoryAssetItem(name=asset.name, daily_cost=daily))

    return [
        CategoryDistribution(
            category_name=name,
            total_cost=data["total_cost"],
            total_daily_cost=data["total_daily"].quantize(Decimal("0.01"), ROUND_HALF_UP),
            count=data["count"],
            avg_daily_cost=(data["total_daily"] / data["count"]).quantize(Decimal("0.01"), ROUND_HALF_UP) if data["count"] else Decimal("0"),
            assets=sorted(data["assets"], key=lambda x: x.daily_cost, reverse=True),
        )
        for name, data in cat_map.items()
    ]


def get_cost_summary(db: Session) -> CostSummary:
    """费用汇总"""
    assets = db.query(Asset).options(joinedload(Asset.category)).all()

    active = [a for a in assets if a.status == "active"]
    disposed = [a for a in assets if a.status == "disposed"]

    total_purchase = sum(Decimal(str(a.purchase_price)) for a in active) if active else Decimal("0")
    total_daily = sum(_comprehensive_daily_cost(a) for a in active) if active else Decimal("0")
    avg_daily = (total_daily / len(active)).quantize(Decimal("0.01"), ROUND_HALF_UP) if active else Decimal("0")

    return CostSummary(
        total_purchase=total_purchase,
        total_daily_cost=total_daily,
        avg_daily_cost=avg_daily,
        active_count=len(active),
        disposed_count=len(disposed),
    )
