from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.db.session import SessionLocal

# Defensive imports
try:
    from app.db.models_attractions import Attraction
    from app.schemas.poi import PointRecommendation
    from app.utils.ui_templates import format_for_ui
except ImportError:
    pass

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recommend", response_model=List[PointRecommendation])
def get_recommendations(db: Session = Depends(get_db)):
    """
    获取推荐点位列表，现在直接从 Attraction 表（后台管理表）读取数据
    """
    # 获取推荐的景点，按排序权重降序
    attractions = db.query(Attraction).filter(Attraction.is_recommended == True).order_by(desc(Attraction.sort_order)).all()
    
    return format_results(attractions)

@router.get("/recommend/personalized", response_model=List[PointRecommendation])
def get_personalized_recommendations(user_id: int, db: Session = Depends(get_db)):
    try:
        from app.db.models_user import User
    except ImportError:
        # If user model fails to import, just return standard recommendations
        return get_recommendations(db)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.preferences:
        # Fallback to standard recommendations
        return get_recommendations(db)
        
    preferences = user.preferences.split(",")
    all_attractions = db.query(Attraction).all()
    
    # Calculate score based on preferences
    scored_attractions = []
    
    for a in all_attractions:
        score = 0
        
        # Base Score
        if a.is_recommended:
            score += 1
            
        # Preference Matching
        # "拍照打卡" -> "摄影型" or colorfulness > 0.8
        if "拍照打卡" in preferences:
            if a.category == "摄影型": score += 5
            if a.colorfulness_score and a.colorfulness_score > 0.8: score += 2
            
        # "体验盐湖景观" -> "景点", "观景台"
        if "体验盐湖景观" in preferences:
            if a.category in ["景点", "观景台"]: score += 5
            if a.category == "湿地": score += 2
            
        # "了解历史文化" -> "博物馆", "科普型"
        if "了解历史文化" in preferences:
            if a.category in ["博物馆", "科普型"]: score += 5
            if a.thematic_score and a.thematic_score > 0.8: score += 2
            
        # "放松身心" -> "休闲型", "湿地"
        if "放松身心" in preferences:
            if a.category in ["休闲型", "湿地"]: score += 5
            
        # "观鸟活动" -> "湿地"
        if "观鸟活动" in preferences:
            if a.category == "湿地": score += 5
            if "鸟" in (a.description or "") or "Bird" in (a.description or ""): score += 3
            
        if score > 0:
            scored_attractions.append((score, a))
            
    # Sort by score desc
    scored_attractions.sort(key=lambda x: x[0], reverse=True)
    
    # Take top 5
    top_attractions = [x[1] for x in scored_attractions[:5]]
    
    return format_results(top_attractions)

def format_results(attractions):
    results = []
    for a in attractions:
        # 计算综合得分 (0-1)
        comp_score = (a.accessibility_score + a.thematic_score + a.colorfulness_score) / 3.0
        if comp_score == 0: # 避免除以0或默认值为0的情况
            comp_score = 0.8 # 默认给个高分
            
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
        
        # UI 增强
        # format_for_ui 已经被修改为优先使用对象的 cover_image 属性
        p_dict.update(format_for_ui(a))
        
        results.append(PointRecommendation(**p_dict))
        
    return results
