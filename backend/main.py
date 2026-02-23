import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import assets, categories, analytics, clothing, outfits, tryon, media, transactions

# Auto-migrate: convert MyISAM tables to InnoDB and add missing columns
try:
    from sqlalchemy import inspect as _inspect, text as _text
    _insp = _inspect(engine)

    # Convert all existing tables from MyISAM to InnoDB (required for FK support)
    _existing_tables = _insp.get_table_names()
    with engine.connect() as _conn:
        for _tbl in _existing_tables:
            _row = _conn.execute(_text(f"SHOW TABLE STATUS LIKE '{_tbl}'")).fetchone()
            if _row and _row[1] != "InnoDB":
                print(f"[migration] converting {_tbl} to InnoDB")
                _conn.execute(_text(f"ALTER TABLE `{_tbl}` ENGINE=InnoDB"))
        _conn.commit()

    _cat_cols = [c["name"] for c in _insp.get_columns("asset_categories")]
    if "daily_budget" not in _cat_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE asset_categories ADD COLUMN daily_budget DECIMAL(10,2) NULL"))
            _conn.commit()
    if "parent_id" not in _cat_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE asset_categories ADD COLUMN parent_id INTEGER NULL"))
            _conn.commit()
    if "sort_order" not in _cat_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE asset_categories ADD COLUMN sort_order INTEGER DEFAULT 0"))
            _conn.commit()
    if "is_asset_related" not in _cat_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE asset_categories ADD COLUMN is_asset_related BOOLEAN DEFAULT 0"))
            _conn.commit()

    _outfit_cols = [c["name"] for c in _insp.get_columns("outfits")]
    if "rendered_image_url" not in _outfit_cols:
        with engine.connect() as _conn:
            _conn.execute(_text("ALTER TABLE outfits ADD COLUMN rendered_image_url VARCHAR(512) NULL"))
            _conn.commit()
except Exception as _e:
    print(f"[migration] warning: {_e}")

# Create tables after migration (so FK references work with InnoDB)
Base.metadata.create_all(bind=engine)

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
app.include_router(transactions.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
