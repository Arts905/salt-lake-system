from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import Subscription


def upsert_subscription(db: Session, openid: str, lake_ids: List[int], threshold: int = 90) -> Subscription:
    """根据 openid 更新或创建订阅。lake_ids 存 CSV。"""
    csv = ",".join(str(x) for x in lake_ids)
    sub = db.query(Subscription).filter(Subscription.openid == openid).first()
    if sub:
        sub.lake_ids = csv
        sub.threshold = threshold
    else:
        sub = Subscription(openid=openid, lake_ids=csv, threshold=threshold, created_at=datetime.utcnow())
        db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def get_all_subscriptions(db: Session) -> List[Subscription]:
    return db.query(Subscription).all()


def get_subscriptions_for_lake(db: Session, lake_id: int) -> List[Subscription]:
    subs = db.query(Subscription).all()
    result: List[Subscription] = []
    for s in subs:
        try:
            ids = [int(x) for x in (s.lake_ids or '').split(',') if x]
        except ValueError:
            ids = []
        if lake_id in ids:
            result.append(s)
    return result