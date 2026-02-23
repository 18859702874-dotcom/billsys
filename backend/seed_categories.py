"""
初始化一级和二级分类。可安全重复运行（按名称查重）。
运行方式: python backend/seed_categories.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import AssetCategory

# 一级分类
L1_CATEGORIES = [
    "家庭", "住房", "餐饮", "恋爱", "购物", "话费", "衣服",
    "娱乐", "交通", "成长", "电子产品", "礼金人情",
]

# 二级分类: {一级名称: [子分类名]}
L2_CATEGORIES = {
    "家庭": ["负债", "母亲保险", "其他购置"],
    "餐饮": ["三餐", "饮用水", "咖啡", "水果", "饮料"],
    "成长": ["Wolai", "脑图", "百度网盘", "其他"],
    "电子产品": ["台式电脑", "笔记本", "平板", "手机", "咖啡机", "显示器", "耳机", "音响", "相机", "键鼠"],
}


def seed():
    db = SessionLocal()
    try:
        created_l1 = 0
        created_l2 = 0

        # 创建一级分类
        l1_map = {}
        for i, name in enumerate(L1_CATEGORIES):
            existing = db.query(AssetCategory).filter(AssetCategory.name == name).first()
            if existing:
                l1_map[name] = existing
            else:
                cat = AssetCategory(name=name, parent_id=None, sort_order=i)
                db.add(cat)
                db.flush()
                l1_map[name] = cat
                created_l1 += 1

        db.commit()

        # 创建二级分类
        for parent_name, children in L2_CATEGORIES.items():
            parent = l1_map.get(parent_name)
            if not parent:
                print(f"[warn] 父分类「{parent_name}」未找到，跳过子分类")
                continue
            for j, child_name in enumerate(children):
                existing = db.query(AssetCategory).filter(AssetCategory.name == child_name).first()
                if existing:
                    # 更新 parent_id（如果之前没有）
                    if existing.parent_id != parent.id:
                        existing.parent_id = parent.id
                        existing.sort_order = j
                else:
                    cat = AssetCategory(name=child_name, parent_id=parent.id, sort_order=j)
                    db.add(cat)
                    created_l2 += 1

        db.commit()
        print(f"[seed] 完成：新建一级分类 {created_l1} 个，新建二级分类 {created_l2} 个")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
