"""一次性迁移脚本：为 assets 表添加 expected_days 列"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE assets ADD COLUMN expected_days INT NULL"))
    conn.commit()
    print("OK: expected_days 列已添加")
