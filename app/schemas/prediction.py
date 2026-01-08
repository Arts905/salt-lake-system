from typing import Optional, Dict, Any
from pydantic import BaseModel


class TimeWindow(BaseModel):
    start: str
    end: str


class LakePrediction(BaseModel):
    lake_id: int
    lake_name: str
    score: int
    best_time: TimeWindow
    updated_at: str
    reason: Optional[str] = None
    factors: Optional[Dict[str, Any]] = None


class RealtimeIndex(BaseModel):
    lake_id: int
    lake_name: str
    score: int
    captured_at: str
    image_path: Optional[str] = None
    reason: Optional[str] = None
    factors: Optional[Dict[str, Any]] = None


class BestRealtimeResponse(BaseModel):
    best: RealtimeIndex
    all: list[RealtimeIndex]


class BestTodayResponse(BaseModel):
    best: LakePrediction
    all: list[LakePrediction]