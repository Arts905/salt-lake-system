from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.routes.predictions import router as predictions_router
from app.api.routes.subscriptions import router as subscriptions_router
from app.api.routes.attractions import router as attractions_router
from app.api.routes.sensors import router as sensors_router
from app.api.routes.recommend import router as recommend_router
from app.api.routes.community import router as community_router
from app.api.routes.user import router as user_router
from app.tasks.scheduler import start_scheduler, shutdown_scheduler
from app.db.session import Base, engine
from app.db.init_data import init_sample_attractions, init_points_of_interest

enable_docs = os.getenv("ENABLE_DOCS", "true").lower() == "true"
app = FastAPI(title="盐湖出片预测API", version="0.1.0", docs_url="/docs" if enable_docs else None, redoc_url=None, openapi_url="/openapi.json" if enable_docs else None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to safe mount
def safe_mount(path: str, dir_path: str, name: str):
    if os.path.exists(dir_path):
        app.mount(path, StaticFiles(directory=dir_path), name=name)
    else:
        print(f"Warning: Directory {dir_path} not found. Skipping mount for {path}")

safe_mount("/static/attractions", "storage/attractions", "attractions")

# Community Images
try:
    if not os.path.exists("storage/community"):
        os.makedirs("storage/community", exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create storage/community: {e}")

safe_mount("/static/community", "storage/community", "community")
safe_mount("/static", "app/static", "static")
safe_mount("/snapshots", "storage/snapshots", "snapshots")
# 新增：提供更简单的 /attractions 路径，避免与 /static 嵌套挂载冲突
safe_mount("/attractions", "storage/attractions", "attractions2")

app.include_router(predictions_router, prefix="/api/prediction", tags=["prediction"])
from app.api.routes.weather import router as weather_router
app.include_router(weather_router, prefix="/api/weather", tags=["weather"])

app.include_router(subscriptions_router, prefix="/api", tags=["subscribe"])
app.include_router(attractions_router, prefix="/api", tags=["attractions"])
app.include_router(sensors_router, prefix="/api", tags=["sensors"])
app.include_router(recommend_router, prefix="/api", tags=["recommend"])
app.include_router(community_router, prefix="/api/community", tags=["community"])
app.include_router(user_router, prefix="/api/user", tags=["user"])

# 根路径跳转：开发到 /docs，生产到静态首页
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs" if enable_docs else "/static/index.html")


@app.on_event("startup")
def on_startup():
    try:
        # Check if we are in Vercel/Serverless
        is_vercel = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        
        # In Vercel, we might skip heavy initialization or only do essential DB checks
        # But since we use /tmp/data.db, it's empty every time, so we MUST init data.
        # We just need to be fast.
        
        # 初始化数据库
        Base.metadata.create_all(bind=engine)
        
        # 导入更多模型
        from app.db.models_attractions import Attraction
        from app.db.models_poi import PointOfInterest
        Base.metadata.create_all(bind=engine)
        
        # Only start scheduler if NOT in serverless (Serverless functions freeze, so scheduler is useless/harmful)
        if not is_vercel:
            start_scheduler()
            
        # 初始化示例数据 (Consider making this lighter or async if possible, but for now just keep it)
        init_sample_attractions()
        init_points_of_interest()
        
    except Exception as e:
        print(f"Startup Error (Non-critical for Vercel demo): {e}")


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}
