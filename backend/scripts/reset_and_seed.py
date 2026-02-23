from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

from database import Base, SessionLocal, engine  # noqa: E402
from models import Asset, AssetCategory  # noqa: E402


def reset_schema() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_data() -> None:
    categories = [
        '台式电脑',
        '笔记本',
        '显示器',
        '便携显示器',
    ]

    assets = [
        {
            'name': '组装电脑',
            'category': '台式电脑',
            'purchase_channel': '淘宝',
            'purchase_date': date(2018, 3, 3),
            'purchase_price': 5500.00,
            'status': 'disposed',
            'disposed_date': date(2025, 1, 10),
            'disposed_reason': '坏了',
            'recovery_amount': 1500.00,
            'recovery_date': date(2025, 1, 10),
            'notes': '示例数据：已弃用资产',
        },
        {
            'name': 'Mac mini M1',
            'category': '台式电脑',
            'purchase_channel': '拼多多百亿补贴',
            'purchase_date': date(2023, 5, 11),
            'purchase_price': 2792.00,
            'status': 'active',
            'disposed_date': None,
            'disposed_reason': None,
            'recovery_amount': None,
            'recovery_date': None,
            'notes': '示例数据：在用资产',
        },
        {
            'name': 'Redmi book pro 15 电脑',
            'category': '笔记本',
            'purchase_channel': '苏宁',
            'purchase_date': date(2021, 6, 1),
            'purchase_price': 3499.00,
            'status': 'disposed',
            'disposed_date': date(2024, 10, 28),
            'disposed_reason': '以旧换新',
            'recovery_amount': 600.00,
            'recovery_date': date(2024, 10, 28),
            'notes': '示例数据：已弃用资产',
        },
        {
            'name': '机械革命无界15x',
            'category': '笔记本',
            'purchase_channel': '京东',
            'purchase_date': date(2024, 11, 5),
            'purchase_price': 3620.00,
            'status': 'active',
            'disposed_date': None,
            'disposed_reason': None,
            'recovery_amount': None,
            'recovery_date': None,
            'notes': '示例数据：在用资产',
        },
        {
            'name': '显示器',
            'category': '显示器',
            'purchase_channel': '京东',
            'purchase_date': date(2021, 6, 8),
            'purchase_price': 1747.00,
            'status': 'active',
            'disposed_date': None,
            'disposed_reason': None,
            'recovery_amount': None,
            'recovery_date': None,
            'notes': '示例数据：在用资产',
        },
        {
            'name': '16英寸便携显示器',
            'category': '便携显示器',
            'purchase_channel': '淘宝',
            'purchase_date': date(2024, 1, 23),
            'purchase_price': 641.00,
            'status': 'active',
            'disposed_date': None,
            'disposed_reason': None,
            'recovery_amount': None,
            'recovery_date': None,
            'notes': '示例数据：在用资产',
        },
    ]

    with SessionLocal() as db:
        for name in categories:
            db.add(AssetCategory(name=name))
        db.commit()

        category_id = {row.name: row.id for row in db.query(AssetCategory).all()}

        for row in assets:
            db.add(
                Asset(
                    name=row['name'],
                    category_id=category_id[row['category']],
                    purchase_price=row['purchase_price'],
                    purchase_date=row['purchase_date'],
                    purchase_channel=row['purchase_channel'],
                    status=row['status'],
                    disposed_date=row['disposed_date'],
                    disposed_reason=row['disposed_reason'],
                    recovery_amount=row['recovery_amount'],
                    recovery_date=row['recovery_date'],
                    notes=row['notes'],
                )
            )
        db.commit()

        total = db.query(Asset).count()
        active = db.query(Asset).filter(Asset.status == 'active').count()
        disposed = db.query(Asset).filter(Asset.status == 'disposed').count()
        cats = db.query(AssetCategory).count()

    print(f'Seed complete: categories={cats}, assets={total}, active={active}, disposed={disposed}')


def main() -> None:
    reset_schema()
    seed_data()


if __name__ == '__main__':
    main()