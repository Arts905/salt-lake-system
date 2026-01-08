import os
import random
import shutil
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.db.models_community import CommunityPost

def init_sample_posts():
    """Initialize sample community posts using existing attraction images"""
    db = SessionLocal()
    try:
        # Ensure community storage dir exists
        community_dir = "storage/community"
        if not os.path.exists(community_dir):
            os.makedirs(community_dir, exist_ok=True)

        # Get list of source images from attractions
        source_dir = "storage/attractions"
        if not os.path.exists(source_dir):
            print("Source directory not found!")
            return
            
        source_files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if not source_files:
            print("No source images found!")
            return

        # Sample data
        authors = ["PhotoMaster", "SaltLakeLover", "HikerJoe", "NatureFan", "TravelBug", "SkyWalker", "LakeSpirit", "ColorHunter", "GeologyGeek", "WeekendVibes"]
        captions = [
            "今天的盐湖颜色太美了！Amazing colors today!",
            "夕阳西下，倒影如画。Sunset reflection.",
            "周末的好去处，空气很清新。Great weekend spot.",
            "被这里的景色治愈了。Healing view.",
            "大自然的鬼斧神工。Nature's masterpiece.",
            "偶遇一只可爱的水鸟。Spotted a cute bird.",
            "强推这个机位，太好拍了！Best photo spot.",
            "千年的盐湖，历史的沉淀。Ancient lake.",
            "带家人一起来打卡。Family trip.",
            "下次还会再来！Will come back again."
        ]

        print("Generating 10 new posts...")
        # Create 10 posts
        for i in range(10):
            # Pick random image
            src_filename = random.choice(source_files)
            src_path = os.path.join(source_dir, src_filename)
            
            # Create a copy in community folder to simulate user upload
            # Use timestamp to ensure unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            dest_filename = f"auto_gen_{timestamp}_{i}_{src_filename}"
            dest_path = os.path.join(community_dir, dest_filename)
            shutil.copy2(src_path, dest_path)
            
            # Construct URL
            image_url = f"/static/community/{dest_filename}"
            
            post = CommunityPost(
                image_url=image_url,
                caption=random.choice(captions),
                author_name=random.choice(authors),
                likes=random.randint(5, 100),
                created_at=datetime.now() - timedelta(hours=random.randint(1, 48))
            )
            db.add(post)
        
        db.commit()
        print("Successfully created 10 sample community posts.")
        
    except Exception as e:
        print(f"Error initializing community data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_posts()
