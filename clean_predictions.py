from app.db.session import SessionLocal
from app.db.models import Prediction

def clean_predictions():
    db = SessionLocal()
    try:
        num = db.query(Prediction).delete()
        db.commit()
        print(f"Deleted {num} predictions.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_predictions()
