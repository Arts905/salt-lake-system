from pydantic import BaseModel, Field
from typing import Optional

class PointRecommendation(BaseModel):
    id: int
    name: str
    accessibility: float
    thematic: float
    colorfulness: float
    popularity: float
    composite_score: float
    category: str
    description: Optional[str] = None
    
    # UI 字段
    ui_title: Optional[str] = None
    ui_subtitle: Optional[str] = None
    ui_category_icon: Optional[str] = None
    ui_is_photo_hotspot: bool = False
    ui_cover_image: Optional[str] = None
    
    # 经纬度
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
