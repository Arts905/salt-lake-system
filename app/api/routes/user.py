from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.session import SessionLocal, engine

# Defensive imports
try:
    from app.db.models_user import User, UserFavorite
    from app.db.models_attractions import Attraction
    from app.utils.ui_templates import format_for_ui
    from app.schemas.poi import PointRecommendation
except ImportError:
    pass

# Auto-create tables moved to main.py startup event
# User.metadata.create_all(bind=engine)
# UserFavorite.metadata.create_all(bind=engine)

router = APIRouter()

# Schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    preferences: str | None = None

class FavoriteRequest(BaseModel):
    user_id: int
    attraction_id: int

class PreferenceRequest(BaseModel):
    user_id: int
    preferences: List[str]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth Routes ---

@router.post("/register", response_model=UserResponse)
def register(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    try:
        new_user = User(username=user.username, password=user.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return db_user

@router.post("/preferences")
def save_preferences(pref: PreferenceRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == pref.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Store as comma-separated string
    user.preferences = ",".join(pref.preferences)
    db.commit()
    return {"status": "updated", "preferences": user.preferences}

# --- Favorites Routes ---

@router.get("/{user_id}/favorites", response_model=List[PointRecommendation])
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
    
    results = []
    for fav in favorites:
        a = db.query(Attraction).filter(Attraction.id == fav.attraction_id).first()
        if not a:
            continue
            
        # Re-use logic from recommend.py (Should ideally be refactored to shared service)
        comp_score = (a.accessibility_score + a.thematic_score + a.colorfulness_score) / 3.0
        if comp_score == 0: comp_score = 0.8
            
        p_dict = {
            "id": a.id,
            "name": a.name,
            "accessibility": a.accessibility_score,
            "thematic": a.thematic_score,
            "colorfulness": a.colorfulness_score,
            "popularity": (a.rating / 5.0) if a.rating else 0.8,
            "composite_score": comp_score,
            "category": a.category,
            "description": a.description or "暂无描述",
            "latitude": a.latitude,
            "longitude": a.longitude
        }
        p_dict.update(format_for_ui(a))
        results.append(PointRecommendation(**p_dict))
        
    return results

@router.post("/favorites")
def add_favorite(fav: FavoriteRequest, db: Session = Depends(get_db)):
    # Check if already exists
    exists = db.query(UserFavorite).filter(
        UserFavorite.user_id == fav.user_id,
        UserFavorite.attraction_id == fav.attraction_id
    ).first()
    
    if exists:
        return {"status": "already_added"}
    
    new_fav = UserFavorite(user_id=fav.user_id, attraction_id=fav.attraction_id)
    db.add(new_fav)
    db.commit()
    return {"status": "added"}

@router.delete("/{user_id}/favorites/{attraction_id}")
def remove_favorite(user_id: int, attraction_id: int, db: Session = Depends(get_db)):
    db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.attraction_id == attraction_id
    ).delete()
    db.commit()
    return {"status": "removed"}
