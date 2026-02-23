import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import assets, categories, analytics, clothing, outfits, tryon, media

Base.metadata.create_all(bind=engine)

# Auto-migrate: add new columns to existing tables
try:
    from sqlalchemy import inspect as _inspect, text as _text
    _insp = _inspect(engine)
    _cat_cols = [c["name"] for c in _insp.get_columns("asset_categories")]
    if "daily_budget" not in _cat_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE asset_categories ADD COLUMN daily_budget DECIMAL(10,2) NULL"))
            _conn.commit()

    _outfit_cols = [c["name"] for c in _insp.get_columns("outfits")]
    if "rendered_image_url" not in _outfit_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE outfits ADD COLUMN rendered_image_url VARCHAR(512) NULL"))
            _conn.commit()
except Exception as _e:
    print(f"[migration] warning: {_e}")

app = FastAPI(title="个人资产追踪系统", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(categories.router)
app.include_router(assets.router)
app.include_router(analytics.router)
app.include_router(clothing.router)
app.include_router(outfits.router)
app.include_router(tryon.router)
app.include_router(media.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
