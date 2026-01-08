from app.db.session import SessionLocal
from app.db.crud_attractions import get_attractions_count, create_attraction
from app.schemas.attraction import AttractionCreate
from app.db.models_poi import PointOfInterest

def init_sample_attractions():
    """初始化示例景点数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if get_attractions_count(db) > 0:
            return
        
        # 创建示例景点数据
        sample_attractions = [
            AttractionCreate(
                name="运城盐湖·主景区",
                description="运城盐湖是世界三大硫酸钠型内陆湖泊之一，湖水中含有大量的硫酸钠、氯化钠等盐类，形成了独特的盐湖景观。主景区是观赏盐湖全貌的最佳位置。",
                latitude=35.0661,
                longitude=110.9775,
                rating=4.6,
                distance="市区内",
                category="景点",
                is_recommended=True,
                sort_order=100,
                accessibility_score=0.9,
                thematic_score=0.8,
                colorfulness_score=0.6
            ),
            AttractionCreate(
                name="运城盐湖·五彩盐湖",
                description="在特定的光照和气候条件下，盐湖会呈现出粉红、橙红、金黄等多种颜色，形成绚丽的五彩盐湖奇观，是摄影爱好者的天堂。",
                latitude=35.0645,
                longitude=110.9820,
                rating=4.8,
                distance="2.5 km",
                category="景点",
                is_recommended=True,
                sort_order=90,
                accessibility_score=0.6,
                thematic_score=0.9,
                colorfulness_score=1.0
            ),
            AttractionCreate(
                name="盐湖博物馆",
                description="展示运城盐湖的历史文化、地质成因、生态环境等内容，通过丰富的展品和多媒体展示，让游客深入了解盐湖的科学价值和文化内涵。",
                latitude=35.0680,
                longitude=110.9750,
                rating=4.4,
                distance="1.8 km",
                category="博物馆",
                is_recommended=True,
                sort_order=80,
                accessibility_score=0.95,
                thematic_score=0.9,
                colorfulness_score=0.3
            )
        ]
        
        for attraction_data in sample_attractions:
            create_attraction(db, attraction_data)
            
    finally:
        db.close()


def init_points_of_interest():
    """初始化点位数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(PointOfInterest).count() > 0:
            return
        
        poi_data = [
           { 
             "id": 1, 
             "name": "盐湖湿地公园", 
             "accessibility": 0.95, 
             "thematic": 0.90, 
             "colorfulness": 0.60, 
             "popularity": 0.90, 
             "composite_score": 0.82, 
             "category": "科普型", 
             "description": "核心入口区，生态展示与游客服务中心所在地，适合家庭研学。" 
           }, 
           { 
             "id": 2, 
             "name": "22号堤埝", 
             "accessibility": 0.85, 
             "thematic": 0.70, 
             "colorfulness": 0.65, 
             "popularity": 0.70, 
             "composite_score": 0.75, 
             "category": "休闲型", 
             "description": "平坦堤道，适合散步观景，视野开阔但色彩较平。" 
           }, 
           { 
             "id": 3, 
             "name": "落日红堤", 
             "accessibility": 0.75, 
             "thematic": 0.70, 
             "colorfulness": 0.80, 
             "popularity": 0.80, 
             "composite_score": 0.77, 
             "category": "摄影型", 
             "description": "傍晚时分盐池泛红，是拍摄落日倒影的热门机位。" 
           }, 
           { 
             "id": 4, 
             "name": "鸟类观测点1", 
             "accessibility": 0.65, 
             "thematic": 1.00, 
             "colorfulness": 0.45, 
             "popularity": 0.75, 
             "composite_score": 0.72, 
             "category": "科普型", 
             "description": "配备望远镜与解说牌，可观测迁徙水鸟，教育性强。" 
           }, 
           { 
             "id": 5, 
             "name": "野生大豆观测点", 
             "accessibility": 0.55, 
             "thematic": 0.90, 
             "colorfulness": 0.35, 
             "popularity": 0.60, 
             "composite_score": 0.62, 
             "category": "科普型", 
             "description": "展示盐碱地特有植物，适合自然教育课程。" 
           }, 
           { 
             "id": 6, 
             "name": "色彩之境", 
             "accessibility": 0.45, 
             "thematic": 0.40, 
             "colorfulness": 0.90, 
             "popularity": 0.95, 
             "composite_score": 0.71, 
             "category": "摄影型", 
             "description": "多色盐池交界处，色彩饱和度高，小红书爆款打卡点。" 
           }, 
           { 
             "id": 7, 
             "name": "天空之境", 
             "accessibility": 0.35, 
             "thematic": 0.30, 
             "colorfulness": 0.95, 
             "popularity": 0.98, 
             "composite_score": 0.73, 
             "category": "摄影型", 
             "description": "水面如镜，可拍出‘天地一线’效果，需晴天前往。" 
           }, 
           { 
             "id": 8, 
             "name": "项链池", 
             "accessibility": 0.25, 
             "thematic": 0.50, 
             "colorfulness": 0.75, 
             "popularity": 0.78, 
             "composite_score": 0.59, 
             "category": "休闲型", 
             "description": "形似项链的盐池群，适合慢游，但步行距离较远。" 
           }, 
           { 
             "id": 9, 
             "name": "湿地芦苇荡", 
             "accessibility": 0.15, 
             "thematic": 0.70, 
             "colorfulness": 0.65, 
             "popularity": 0.82, 
             "composite_score": 0.55, 
             "category": "休闲型", 
             "description": "秋季芦苇金黄，氛围感强，但入口较偏。" 
           }, 
           { 
             "id": 10, 
             "name": "天鹅湖", 
             "accessibility": 0.10, 
             "thematic": 0.80, 
             "colorfulness": 0.50, 
             "popularity": 0.88, 
             "composite_score": 0.53, 
             "category": "科普型", 
             "description": "冬季可观赏越冬天鹅，生态价值高，但交通不便。" 
           }, 
           { 
             "id": 11, 
             "name": "硝花池", 
             "accessibility": 0.05, 
             "thematic": 0.40, 
             "colorfulness": 0.40, 
             "popularity": 0.65, 
             "composite_score": 0.39, 
             "category": "休闲型", 
             "description": "结晶硝花景观独特，但位置偏远，适合深度探索者。" 
           }, 
           { 
             "id": 12, 
             "name": "鸟类观测点2", 
             "accessibility": 0.00, 
             "thematic": 1.00, 
             "colorfulness": 0.60, 
             "popularity": 0.72, 
             "composite_score": 0.47, 
             "category": "科普型", 
             "description": "专业观鸟点，需预约进入，科研导向强。" 
           }, 
           { 
             "id": 13, 
             "name": "盐湖博物馆", 
             "accessibility": 0.95, 
             "thematic": 0.95, 
             "colorfulness": 0.30, 
             "popularity": 0.85, 
             "composite_score": 0.85, 
             "category": "科普型", 
             "description": "展示运城盐湖的历史文化、地质成因、生态环境等内容，通过丰富的展品和多媒体展示，让游客深入了解盐湖的科学价值和文化内涵。" 
           }
        ]
        
        for data in poi_data:
            # Check if id exists
            existing = db.query(PointOfInterest).filter(PointOfInterest.id == data["id"]).first()
            if not existing:
                poi = PointOfInterest(**data)
                db.add(poi)
        
        db.commit()
    except Exception as e:
        print(f"Error initializing POI data: {e}")
    finally:
        db.close()
