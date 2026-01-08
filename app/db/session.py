import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 加载环境变量，支持本地 .env 与生产环境变量
load_dotenv()

# Vercel / Serverless Environment Check
is_vercel = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")

if is_vercel:
    # In Vercel, use in-memory SQLite for maximum safety during startup
    # Or /tmp/data.db if persistence within same lambda instance is desired
    # But often /tmp is cleaner.
    DEFAULT_SQLITE_PATH = "/tmp/data.db"
    
    # Ensure /tmp exists (it should)
    if not os.path.exists("/tmp"):
        try:
            os.makedirs("/tmp")
        except:
            pass
            
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "data.db").replace("\\", "/")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

try:
    engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
    # Test connection immediately to fail fast or fallback
    with engine.connect() as conn:
        pass
except Exception as e:
    print(f"Database connection failed: {e}. Falling back to in-memory SQLite.")
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()