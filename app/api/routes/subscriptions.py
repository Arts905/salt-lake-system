from fastapi import APIRouter
from app.db.session import SessionLocal

# Defensive imports
try:
    from app.schemas.subscription import SubscriptionCreate
    from app.db.crud_subscriptions import upsert_subscription
except ImportError:
    pass

router = APIRouter()


@router.post("/subscribe")
def subscribe(payload: SubscriptionCreate):
    db = SessionLocal()
    try:
        sub = upsert_subscription(db, payload.openid, payload.lake_ids, payload.threshold)
        return {
            "success": True,
            "message": "订阅成功",
            "data": {
                "openid": sub.openid,
                "lake_ids": sub.lake_ids,
                "threshold": sub.threshold,
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
            },
        }
    finally:
        db.close()