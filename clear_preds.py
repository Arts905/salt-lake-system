from app.db.session import SessionLocal
from app.db.models import Prediction
from sqlalchemy import text

def clear_predictions():
    db = SessionLocal()
    try:
        # 使用 SQLAlchemy 的 delete 方法
        num = db.query(Prediction).delete()
        db.commit()
        print(f"Deleted {num} old prediction records.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_predictions()
