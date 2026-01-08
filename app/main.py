from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="盐湖景观实时监测系统")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0 (Minimal Mode)"}

@app.get("/")
def read_root():
    return {"message": "Salt Lake System is Running!"}

# --- TEMPORARILY DISABLED FOR DEBUGGING ---
# from app.db.session import engine, Base
# from app.db.init_data import init_sample_attractions
# from app.db.models_poi import PointOfInterest
# from app.tasks.scheduler import start_scheduler
# ... (All router imports commented out) ...
# ------------------------------------------
