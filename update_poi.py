from app.db.session import SessionLocal
from app.db.models_poi import PointOfInterest

def update_poi():
    db = SessionLocal()
    try:
        poi = db.query(PointOfInterest).filter(PointOfInterest.id == 4).first()
        if poi:
            poi.name = "盐湖博物馆"
            poi.accessibility = 0.95
            poi.popularity = 0.85
            poi.composite_score = 0.88
            poi.description = "深入了解盐湖历史、地质成因与生态价值的最佳场所。"
            db.commit()
            print("Successfully updated POI 4 to '盐湖博物馆'")
        else:
            print("POI 4 not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_poi()
