from app.db.session import SessionLocal
from app.db.models_poi import PointOfInterest

def check_db():
    db = SessionLocal()
    try:
        pois = db.query(PointOfInterest).all()
        print(f"Total POIs: {len(pois)}")
        print(f"{'ID':<5} {'Name':<20} {'Category':<10}")
        print("-" * 40)
        for p in pois:
            print(f"{p.id:<5} {p.name:<20} {p.category:<10}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
