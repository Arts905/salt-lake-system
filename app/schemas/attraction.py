from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AttractionBase(BaseModel):
    """景点基础模型"""
    name: str = Field(..., description="景点名称", max_length=100)
    description: Optional[str] = Field(None, description="景点简介")
    cover_image: Optional[str] = Field(None, description="封面图片路径")
    latitude: Optional[float] = Field(None, description="纬度", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="经度", ge=-180, le=180)
    rating: float = Field(4.5, description="评分", ge=0, le=5)
    distance: Optional[str] = Field(None, description="距离描述", max_length=20)
    category: str = Field("景点", description="分类", max_length=50)
    is_recommended: bool = Field(True, description="是否推荐显示")
    sort_order: int = Field(0, description="排序权重，数字越大越靠前")


class AttractionCreate(AttractionBase):
    """创建景点请求模型"""
    pass


class AttractionUpdate(BaseModel):
    """更新景点请求模型"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    cover_image: Optional[str] = Field(None)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    rating: Optional[float] = Field(None, ge=0, le=5)
    distance: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=50)
    is_recommended: Optional[bool] = Field(None)
    sort_order: Optional[int] = Field(None)
    accessibility_score: Optional[float] = Field(None, ge=0, le=1)
    thematic_score: Optional[float] = Field(None, ge=0, le=1)
    colorfulness_score: Optional[float] = Field(None, ge=0, le=1)


class AttractionResponse(AttractionBase):
    """景点响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AttractionListResponse(BaseModel):
    """景点列表响应模型"""
    total: int
    items: list[AttractionResponse]
    page: int
    page_size: int