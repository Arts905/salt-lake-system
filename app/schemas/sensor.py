from typing import Optional
from pydantic import BaseModel

class SensorReadingCreate(BaseModel):
    lake_id: int
    captured_at: Optional[str] = None  # ISO string, optional; server defaults to now
    air_temp: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    water_temp: Optional[float] = None
    salinity: Optional[float] = None
    dissolved_oxygen: Optional[float] = None
    tds: Optional[float] = None
    turbidity: Optional[float] = None

class SensorReadingResponse(BaseModel):
    id: int
    lake_id: int
    captured_at: str
    air_temp: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    water_temp: Optional[float] = None
    salinity: Optional[float] = None
    dissolved_oxygen: Optional[float] = None
    tds: Optional[float] = None
    turbidity: Optional[float] = None