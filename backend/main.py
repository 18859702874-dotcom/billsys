import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import assets, categories, analytics, clothing, outfits, tryon

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


@app.get("/api/health")
def health():
    return {"status": "ok"}
