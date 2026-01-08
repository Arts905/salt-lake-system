import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from datetime import datetime

from app.db.session import SessionLocal, engine

# Defensive imports
try:
    from app.db.models_community import CommunityPost
    from app.utils.oss import upload_file_to_oss
except ImportError:
    pass

# Auto-create table moved to main.py startup event

router = APIRouter()

# Schema
class PostResponse(BaseModel):
    id: int
    image_url: str
    caption: str | None
    author_name: str
    likes: int
    created_at: datetime

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Local storage fallback
UPLOAD_DIR = "storage/community"
try:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    # If read-only filesystem (Vercel), we might fail here. 
    # Fallback to /tmp only when actually writing.
    pass

@router.get("/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return db.query(CommunityPost).order_by(desc(CommunityPost.created_at)).all()

@router.post("/posts", response_model=PostResponse)
def create_post(
    caption: str = Form(""),
    author_name: str = Form("Visitor"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_url = None
    
    # Try OSS Upload first
    if os.getenv("ALIYUN_OSS_BUCKET"):
        try:
            image_url = upload_file_to_oss(file.file, file.filename)
        except Exception:
            pass
        
    # Fallback to local storage if OSS fails or not configured
    if not image_url:
        file.file.seek(0) # Reset cursor
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Use /tmp for Vercel if storage not available
        final_dir = UPLOAD_DIR
        try:
            if not os.path.exists(final_dir):
                os.makedirs(final_dir, exist_ok=True)
        except Exception:
            final_dir = "/tmp"
            
        file_path = os.path.join(final_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Note: URL depends on static mount in main.py
        image_url = f"/static/community/{filename}"
    
    new_post = CommunityPost(
        image_url=image_url,
        caption=caption,
        author_name=author_name
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes += 1
    db.commit()
    return {"likes": post.likes}
