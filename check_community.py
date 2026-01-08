from app.db.session import SessionLocal
from app.db.models_community import CommunityPost

db = SessionLocal()
count = db.query(CommunityPost).count()
print(f"Count: {count}")
if count > 0:
    posts = db.query(CommunityPost).all()
    for p in posts:
        print(f"{p.id}: {p.author_name} - {p.caption}")
db.close()
