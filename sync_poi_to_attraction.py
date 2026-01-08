from app.db.session import SessionLocal
from app.db.models_poi import PointOfInterest
from app.db.models_attractions import Attraction

def sync_data():
    db = SessionLocal()
    try:
        # 1. Clear Attractions
        db.query(Attraction).delete()
        db.commit()
        print("Cleared Attractions table.")
        
        # 2. Get POIs
        pois = db.query(PointOfInterest).all()
        print(f"Found {len(pois)} POIs.")
        
        # 3. Copy to Attractions
        for p in pois:
            att = Attraction(
                id=p.id,
                name=p.name,
                description=p.description,
                category=p.category,
                # Map scores
                accessibility_score=p.accessibility,
                thematic_score=p.thematic,
                colorfulness_score=p.colorfulness,
                rating=round(p.composite_score * 5, 1), # Map 0-1 to 0-5
                # Defaults
                is_recommended=True,
                sort_order=0,
                latitude=0.0, # POI doesn't have lat/lon, use defaults
                longitude=0.0,
                distance="未知距离"
            )
            db.add(att)
        
        db.commit()
        print("Synced POIs to Attractions.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_data()
