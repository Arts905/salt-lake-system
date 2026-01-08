from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import SensorReading


def save_sensor_reading(
    db: Session,
    lake_id: int,
    captured_at: Optional[datetime],
    air_temp: Optional[float],
    humidity: Optional[float],
    wind_speed: Optional[float],
    water_temp: Optional[float],
    salinity: Optional[float],
    dissolved_oxygen: Optional[float],
    tds: Optional[float],
    turbidity: Optional[float],
) -> SensorReading:
    rec = SensorReading(
        lake_id=lake_id,
        captured_at=captured_at or datetime.utcnow(),
        air_temp=int(air_temp) if air_temp is not None else None,
        humidity=int(humidity) if humidity is not None else None,
        wind_speed=int(wind_speed) if wind_speed is not None else None,
        water_temp=int(water_temp) if water_temp is not None else None,
        salinity=int(salinity) if salinity is not None else None,
        dissolved_oxygen=int(dissolved_oxygen) if dissolved_oxygen is not None else None,
        tds=int(tds) if tds is not None else None,
        turbidity=int(turbidity) if turbidity is not None else None,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_latest_sensor_reading(db: Session, lake_id: int) -> Optional[SensorReading]:
    return (
        db.query(SensorReading)
        .filter(SensorReading.lake_id == lake_id)
        .order_by(SensorReading.captured_at.desc())
        .first()
    )