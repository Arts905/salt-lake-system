from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import Prediction
from app.schemas.prediction import LakePrediction, TimeWindow


def save_predictions(db: Session, preds: List[LakePrediction]):
    for p in preds:
        rec = Prediction(
            lake_id=p.lake_id,
            lake_name=p.lake_name,
            score=p.score,
            best_start=p.best_time.start,
            best_end=p.best_time.end,
            updated_at=datetime.fromisoformat(p.updated_at.replace("Z", "+00:00")) if "T" in p.updated_at else datetime.utcnow(),
        )
        db.add(rec)
    db.commit()


def get_latest_predictions(db: Session) -> List[LakePrediction]:
    # 修改逻辑：获取每个 lake_id 的最新一条预测，而不是全局最新的 3 条
    from sqlalchemy import func
    
    # 子查询：找到每个 lake_id 最新的 updated_at
    subquery = (
        db.query(
            Prediction.lake_id,
            func.max(Prediction.updated_at).label("max_updated_at")
        )
        .group_by(Prediction.lake_id)
        .subquery()
    )
    
    # 主查询：连接子查询，获取完整记录
    rows = (
        db.query(Prediction)
        .join(subquery, (Prediction.lake_id == subquery.c.lake_id) & (Prediction.updated_at == subquery.c.max_updated_at))
        .all()
    )
    
    return [
        LakePrediction(
            lake_id=r.lake_id,
            lake_name=r.lake_name,
            score=r.score,
            best_time=TimeWindow(start=r.best_start, end=r.best_end),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]