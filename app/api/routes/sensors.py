from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import SessionLocal

# Defensive imports
try:
    from app.schemas.sensor import SensorReadingCreate, SensorReadingResponse
    from app.db.crud_sensor import save_sensor_reading, get_latest_sensor_reading
except ImportError:
    pass

router = APIRouter()

@router.post("/sensors/ingest", response_model=SensorReadingResponse)
def ingest_sensor(payload: SensorReadingCreate):
    db: Session = SessionLocal()
    try:
        captured_at = None
        if payload.captured_at:
            try:
                captured_at = datetime.fromisoformat(payload.captured_at)
            except Exception:
                captured_at = None
        rec = save_sensor_reading(
            db,
            lake_id=payload.lake_id,
            captured_at=captured_at,
            air_temp=payload.air_temp,
            humidity=payload.humidity,
            wind_speed=payload.wind_speed,
            water_temp=payload.water_temp,
            salinity=payload.salinity,
            dissolved_oxygen=payload.dissolved_oxygen,
            tds=payload.tds,
            turbidity=payload.turbidity,
        )
        return SensorReadingResponse(
            id=rec.id,
            lake_id=rec.lake_id,
            captured_at=rec.captured_at.isoformat(),
            air_temp=rec.air_temp,
            humidity=rec.humidity,
            wind_speed=rec.wind_speed,
            water_temp=rec.water_temp,
            salinity=rec.salinity,
            dissolved_oxygen=rec.dissolved_oxygen,
            tds=rec.tds,
            turbidity=rec.turbidity,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"传感器数据写入失败: {e}")
    finally:
        db.close()

@router.get("/sensors/latest/{lake_id}", response_model=SensorReadingResponse)
def latest_sensor(lake_id: int):
    db: Session = SessionLocal()
    try:
        rec = get_latest_sensor_reading(db, lake_id)
        if not rec:
            raise HTTPException(status_code=404, detail="暂无传感器数据")
        return SensorReadingResponse(
            id=rec.id,
            lake_id=rec.lake_id,
            captured_at=rec.captured_at.isoformat(),
            air_temp=rec.air_temp,
            humidity=rec.humidity,
            wind_speed=rec.wind_speed,
            water_temp=rec.water_temp,
            salinity=rec.salinity,
            dissolved_oxygen=rec.dissolved_oxygen,
            tds=rec.tds,
            turbidity=rec.turbidity,
        )
    finally:
        db.close()