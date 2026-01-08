from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    lake_id = Column(Integer, index=True)
    lake_name = Column(String, index=True)
    score = Column(Integer)
    best_start = Column(String)
    best_end = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)


class RealtimeIndexRecord(Base):
    __tablename__ = "realtime_indices"
    id = Column(Integer, primary_key=True, index=True)
    lake_id = Column(Integer, index=True)
    lake_name = Column(String)
    score = Column(Integer)
    captured_at = Column(DateTime, default=datetime.utcnow)
    image_path = Column(String, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String, unique=True, index=True)
    lake_ids = Column(String)  # 简化：CSV形式
    threshold = Column(Integer, default=90)
    created_at = Column(DateTime, default=datetime.utcnow)


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    lake_id = Column(Integer, index=True)
    captured_at = Column(DateTime, default=datetime.utcnow, index=True)
    air_temp = Column(Integer, nullable=True)
    humidity = Column(Integer, nullable=True)
    wind_speed = Column(Integer, nullable=True)
    water_temp = Column(Integer, nullable=True)
    salinity = Column(Integer, nullable=True)
    dissolved_oxygen = Column(Integer, nullable=True)
    tds = Column(Integer, nullable=True)
    turbidity = Column(Integer, nullable=True)