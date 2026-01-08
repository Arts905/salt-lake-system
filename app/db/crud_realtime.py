from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import RealtimeIndexRecord


def save_realtime_index(db: Session, lake_id: int, lake_name: str, score: int, image_path: str | None, captured_at: datetime) -> RealtimeIndexRecord:
    rec = RealtimeIndexRecord(
        lake_id=lake_id,
        lake_name=lake_name,
        score=score,
        image_path=image_path,
        captured_at=captured_at,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_latest_realtime_index_record(db: Session, lake_id: int) -> RealtimeIndexRecord | None:
    return (
        db.query(RealtimeIndexRecord)
        .filter(RealtimeIndexRecord.lake_id == lake_id)
        .order_by(RealtimeIndexRecord.captured_at.desc())
        .first()
    )