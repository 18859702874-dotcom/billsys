from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class AssetCategory(Base):
    __tablename__ = "asset_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    daily_budget = Column(Numeric(10, 2), nullable=True)

    assets = relationship("Asset", back_populates="category")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)
    purchase_price = Column(Numeric(12, 2), nullable=False)
    purchase_date = Column(Date, nullable=False)
    purchase_channel = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="active")  # active / disposed
    disposed_date = Column(Date, nullable=True)
    disposed_reason = Column(String(100), nullable=True)
    recovery_amount = Column(Numeric(12, 2), nullable=True)
    recovery_date = Column(Date, nullable=True)
    expected_days = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("AssetCategory", back_populates="assets")


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(30), nullable=False)  # 上衣/下装/外套/鞋子/配饰
    color = Column(String(30), nullable=True)
    brand = Column(String(50), nullable=True)
    purchase_price = Column(Numeric(12, 2), nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_channel = Column(String(50), nullable=True)
    image_url = Column(String(255), nullable=True)
    season = Column(String(20), nullable=True)  # 春/夏/秋/冬/四季
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    outfit_items = relationship("OutfitItem", back_populates="clothing", cascade="all, delete-orphan")


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    occasion = Column(String(50), nullable=True)  # 日常/通勤/运动/约会/正式
    season = Column(String(20), nullable=True)
    rendered_image_url = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    clothing_id = Column(Integer, ForeignKey("clothing_items.id"), nullable=False)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    scale = Column(Numeric(3, 2), default=1.0)

    outfit = relationship("Outfit", back_populates="items")
    clothing = relationship("ClothingItem", back_populates="outfit_items")
