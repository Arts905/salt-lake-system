from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Prediction
from app.tasks.scheduler import refresh_predictions

def trigger_refresh():
    # 1. Clear old predictions (optional, but good for clean slate)
    db = SessionLocal()
    try:
        db.query(Prediction).delete()
        db.commit()
        print("Cleared old predictions.")
    except Exception as e:
        print(f"Error clearing predictions: {e}")
    finally:
        db.close()

    # 2. Trigger refresh
    print("Triggering refresh_predictions...")
    refresh_predictions()
    print("Done.")

if __name__ == "__main__":
    trigger_refresh()
