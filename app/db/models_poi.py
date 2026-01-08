from sqlalchemy import Column, Integer, String, Float, Text
from app.db.session import Base

class PointOfInterest(Base):
    __tablename__ = "points_of_interest"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    accessibility = Column(Float, nullable=False)
    thematic = Column(Float, nullable=False)
    colorfulness = Column(Float, nullable=False)
    popularity = Column(Float, nullable=False)
    composite_score = Column(Float, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<PointOfInterest(name='{self.name}', score={self.composite_score})>"
