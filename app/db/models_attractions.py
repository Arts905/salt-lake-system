from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from datetime import datetime
from app.db.session import Base


class Attraction(Base):
    """景点管理模型"""
    __tablename__ = "attractions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="景点名称")
    description = Column(Text, nullable=True, comment="景点简介")
    cover_image = Column(String(255), nullable=True, comment="封面图片路径")
    latitude = Column(Float, nullable=True, comment="纬度")
    longitude = Column(Float, nullable=True, comment="经度")
    rating = Column(Float, default=4.5, comment="评分")
    distance = Column(String(20), nullable=True, comment="距离描述，如'2.5 km'")
    category = Column(String(50), default="景点", comment="分类：景点/博物馆/观景台等")
    is_recommended = Column(Boolean, default=True, comment="是否推荐显示")
    sort_order = Column(Integer, default=0, comment="排序权重，数字越大越靠前")

    # AHP 评价指标
    accessibility_score = Column(Float, default=0.5, comment="可达性得分 (0-1)")
    thematic_score = Column(Float, default=0.5, comment="主题性得分 (0-1)")
    colorfulness_score = Column(Float, default=0.5, comment="色彩性得分 (0-1)")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def __repr__(self):
        return f"<Attraction(id={self.id}, name='{self.name}')>"