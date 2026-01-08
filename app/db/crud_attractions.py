from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.db.models_attractions import Attraction
from app.schemas.attraction import AttractionCreate, AttractionUpdate


def create_attraction(db: Session, attraction: AttractionCreate) -> Attraction:
    """创建景点"""
    db_attraction = Attraction(**attraction.dict())
    db.add(db_attraction)
    db.commit()
    db.refresh(db_attraction)
    return db_attraction


def get_attraction(db: Session, attraction_id: int) -> Optional[Attraction]:
    """根据ID获取景点"""
    return db.query(Attraction).filter(Attraction.id == attraction_id).first()


def get_attractions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_recommended: Optional[bool] = None,
    category: Optional[str] = None
) -> List[Attraction]:
    """获取景点列表"""
    query = db.query(Attraction)
    
    if is_recommended is not None:
        query = query.filter(Attraction.is_recommended == is_recommended)
    
    if category:
        query = query.filter(Attraction.category == category)
    
    return (
        query.order_by(desc(Attraction.sort_order), desc(Attraction.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_attractions_count(
    db: Session,
    is_recommended: Optional[bool] = None,
    category: Optional[str] = None
) -> int:
    """获取景点总数"""
    query = db.query(Attraction)
    
    if is_recommended is not None:
        query = query.filter(Attraction.is_recommended == is_recommended)
    
    if category:
        query = query.filter(Attraction.category == category)
    
    return query.count()


def get_recommended_attractions(db: Session, limit: int = 10) -> List[Attraction]:
    """获取推荐景点列表"""
    return (
        db.query(Attraction)
        .filter(Attraction.is_recommended == True)
        .order_by(desc(Attraction.sort_order), desc(Attraction.rating))
        .limit(limit)
        .all()
    )


def update_attraction(db: Session, attraction_id: int, attraction_update: AttractionUpdate) -> Optional[Attraction]:
    """更新景点"""
    db_attraction = db.query(Attraction).filter(Attraction.id == attraction_id).first()
    if not db_attraction:
        return None
    
    update_data = attraction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_attraction, field, value)
    
    db.commit()
    db.refresh(db_attraction)
    return db_attraction


def delete_attraction(db: Session, attraction_id: int) -> bool:
    """删除景点"""
    db_attraction = db.query(Attraction).filter(Attraction.id == attraction_id).first()
    if not db_attraction:
        return False
    
    db.delete(db_attraction)
    db.commit()
    return True


def search_attractions(db: Session, keyword: str, limit: int = 20) -> List[Attraction]:
    """搜索景点"""
    return (
        db.query(Attraction)
        .filter(
            (Attraction.name.contains(keyword)) |
            (Attraction.description.contains(keyword)) |
            (Attraction.category.contains(keyword))
        )
        .order_by(desc(Attraction.sort_order), desc(Attraction.rating))
        .limit(limit)
        .all()
    )