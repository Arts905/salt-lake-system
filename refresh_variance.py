from app.db.session import SessionLocal
from app.db.models import Prediction
from app.tasks.scheduler import refresh_predictions
import logging

# 配置日志以便查看输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def trigger_refresh_with_variance():
    # 1. Clear old predictions to force new logic to apply
    db = SessionLocal()
    try:
        deleted = db.query(Prediction).delete()
        db.commit()
        print(f"Cleared {deleted} old predictions.")
    except Exception as e:
        print(f"Error clearing predictions: {e}")
        db.rollback()
    finally:
        db.close()

    # 2. Trigger refresh (which now uses the updated predict_for_lakes)
    print("Triggering refresh_predictions with variance logic...")
    refresh_predictions()
    print("Refresh done. Please check the API output.")

if __name__ == "__main__":
    trigger_refresh_with_variance()
