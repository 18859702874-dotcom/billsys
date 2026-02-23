from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from models import Asset


def calc_days_used(asset: Asset, target_date: date = None) -> int:
    """计算资产已使用天数"""
    if target_date is None:
        target_date = date.today()
    if asset.status == "disposed" and asset.disposed_date:
        end = asset.disposed_date
    else:
        end = target_date
    days = (end - asset.purchase_date).days
    return max(days, 1)


def calc_net_cost(asset: Asset) -> Decimal:
    """净成本 = 购买价格 - 回收金额（最低为 0）"""
    purchase = Decimal(str(asset.purchase_price))
    recovery = Decimal(str(asset.recovery_amount or 0))
    net = purchase - recovery
    if net < 0:
        net = Decimal("0")
    return net.quantize(Decimal("0.01"), ROUND_HALF_UP)


def calc_daily_cost(asset: Asset, target_date: date = None) -> Decimal:
    """日均费用 = 净成本 / 使用天数"""
    days = calc_days_used(asset, target_date)
    net = calc_net_cost(asset)
    return (net / days).quantize(Decimal("0.01"), ROUND_HALF_UP)


def calc_estimated_daily_cost(asset: Asset) -> Decimal | None:
    """预估日费用 = 净成本 / 预计使用天数"""
    if not asset.expected_days:
        return None
    net = calc_net_cost(asset)
    return (net / asset.expected_days).quantize(Decimal("0.01"), ROUND_HALF_UP)