from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# --- Category ---
class CategoryCreate(BaseModel):
    name: str = Field(max_length=50)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    daily_budget: Optional[Decimal] = Field(default=None, ge=0)


class CategoryOut(BaseModel):
    id: int
    name: str
    daily_budget: Optional[Decimal] = None
    model_config = {"from_attributes": True}


# --- Asset ---
class AssetCreate(BaseModel):
    name: str = Field(max_length=100)
    category_id: int
    purchase_price: Decimal = Field(ge=0)
    purchase_date: date
    purchase_channel: Optional[str] = None
    expected_days: Optional[int] = Field(default=None, gt=0)
    notes: Optional[str] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    purchase_price: Optional[Decimal] = None
    purchase_date: Optional[date] = None
    purchase_channel: Optional[str] = None
    expected_days: Optional[int] = Field(default=None, gt=0)
    notes: Optional[str] = None
    status: Optional[str] = None
    disposed_date: Optional[date] = None
    disposed_reason: Optional[str] = None
    recovery_amount: Optional[Decimal] = Field(default=None, ge=0)
    recovery_date: Optional[date] = None


class AssetOut(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: str = ""
    purchase_price: Decimal
    purchase_date: date
    purchase_channel: Optional[str] = None
    status: str
    disposed_date: Optional[date] = None
    disposed_reason: Optional[str] = None
    recovery_amount: Optional[Decimal] = None
    recovery_date: Optional[date] = None
    expected_days: Optional[int] = None
    notes: Optional[str] = None
    days_used: int = 0
    daily_cost: Decimal = Decimal("0")
    net_cost: Decimal = Decimal("0")
    estimated_daily_cost: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DisposeRequest(BaseModel):
    disposed_date: date
    disposed_reason: str = ""
    recovery_amount: Optional[Decimal] = Field(default=None, ge=0)
    recovery_date: Optional[date] = None


# --- Analytics ---
class TrendPoint(BaseModel):
    date: date
    value: Decimal


class CategoryAssetItem(BaseModel):
    name: str
    daily_cost: Decimal


class CategoryDistribution(BaseModel):
    category_name: str
    total_cost: Decimal
    total_daily_cost: Decimal
    count: int
    avg_daily_cost: Decimal
    assets: list[CategoryAssetItem] = []


class CostSummary(BaseModel):
    total_purchase: Decimal
    total_daily_cost: Decimal
    avg_daily_cost: Decimal
    active_count: int
    disposed_count: int


# --- Clothing ---
class ClothingCreate(BaseModel):
    name: str = Field(max_length=100)
    category: str = Field(max_length=30)
    color: Optional[str] = None
    brand: Optional[str] = None
    purchase_price: Optional[Decimal] = Field(default=None, ge=0)
    purchase_date: Optional[date] = None
    purchase_channel: Optional[str] = None
    season: Optional[str] = None
    notes: Optional[str] = None


class ClothingUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    purchase_price: Optional[Decimal] = Field(default=None, ge=0)
    purchase_date: Optional[date] = None
    purchase_channel: Optional[str] = None
    season: Optional[str] = None
    notes: Optional[str] = None


class ClothingOut(BaseModel):
    id: int
    name: str
    category: str
    color: Optional[str] = None
    brand: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    purchase_date: Optional[date] = None
    purchase_channel: Optional[str] = None
    image_url: Optional[str] = None
    season: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ClothingBatchCreateRequest(BaseModel):
    items: list[ClothingCreate] = Field(min_length=1, max_length=200)


# --- Outfit ---
class OutfitItemIn(BaseModel):
    clothing_id: int
    position_x: int = 0
    position_y: int = 0
    scale: float = 1.0


class OutfitCreate(BaseModel):
    name: str = Field(max_length=100)
    occasion: Optional[str] = None
    season: Optional[str] = None
    rendered_image_url: Optional[str] = None
    notes: Optional[str] = None
    items: list[OutfitItemIn] = []


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    occasion: Optional[str] = None
    season: Optional[str] = None
    rendered_image_url: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[list[OutfitItemIn]] = None


class OutfitItemOut(BaseModel):
    id: int
    clothing_id: int
    position_x: int
    position_y: int
    scale: float
    clothing: ClothingOut
    model_config = {"from_attributes": True}


class OutfitOut(BaseModel):
    id: int
    name: str
    occasion: Optional[str] = None
    season: Optional[str] = None
    rendered_image_url: Optional[str] = None
    notes: Optional[str] = None
    items: list[OutfitItemOut] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class OutfitRenderItemIn(BaseModel):
    name: str = Field(max_length=100)
    category: str = Field(max_length=30)
    image_url: str = Field(min_length=1, max_length=512)


class OutfitRenderRequest(BaseModel):
    items: list[OutfitRenderItemIn] = Field(min_length=1, max_length=8)
    prompt: Optional[str] = Field(default=None, max_length=1000)


class OutfitRenderResponse(BaseModel):
    image_url: str
    model: str
    text: Optional[str] = None
