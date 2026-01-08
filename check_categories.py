from app.db.session import SessionLocal
from app.db.models_poi import PointOfInterest

def check_categories():
    db = SessionLocal()
    try:
        categories = db.query(PointOfInterest.category).distinct().all()
        print("Existing categories in DB (repr):")
        for cat in categories:
            print(f"- {repr(cat[0])}")
            
        # Also print a few full records to be sure
        print("\nSample records (repr):")
        points = db.query(PointOfInterest).limit(5).all()
        for p in points:
            print(f"ID: {p.id}, Category: {repr(p.category)}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_categories()
