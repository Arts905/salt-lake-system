
UI_TEMPLATES = {
    "photo_alert_title": "【出片预警】{name} 色彩指数飙升！",
    "photo_alert_body": "当前指数 {score:.0f}%，{description}，建议立即前往拍摄。",
    "home_card_title": "📸 {name}",
    "home_card_subtitle": "{description}",
    "map_label": "{name} • {category}",
    "category_icon": {
        "摄影型": "📸",
        "科普型": "🧪",
        "休闲型": "🚶‍♂️"
    },
    # 封面图映射（使用本地下载的图片，确保稳定性）
    "cover_images": {
        "盐湖湿地公园": "/static/attractions/f8533591cb2059ef1ca4cb47b12cec1c.jpg",
        "22号堤埝": "/static/attractions/811f35279813bf1aaafc8ca769265a8f.jpg",
        "落日红堤": "/static/attractions/3ad8043bd2901e1fb45382e242f5342a.jpg",
        "鸟类观测点1": "/static/attractions/91b42e63d9d45a4d151265180242f6bb.jpg",
        "野生大豆观测点": "/static/attractions/728d0861a485483185a688e893e92f49.jpg",
        "色彩之境": "/static/attractions/d86c7e86c449707168e5e17270f08a54.jpg",
        "天空之境": "/static/attractions/619dadda4779a367fbc28f5e5be258e5.jpg",
        "项链池": "/static/attractions/22766396f89788b8d225c5afa56ae56a.jpg",
        "湿地芦苇荡": "/static/attractions/618d67c0efe84e994a70255ec30ce7bd.jpg",
        "天鹅湖": "/static/attractions/475fded6bfad021d1f255c60227ff26b.jpg",
        "硝花池": "/static/attractions/5968448f75f0aee34e5bafd351b0db74.jpg",
        "鸟类观测点2": "/static/attractions/9f6a1b992e8c542c14f92d96f911d8aa.jpg",
        "盐湖博物馆": "/static/attractions/e987d30acd6043c194698bb89ea2c054.jpg"
    }
}

def format_for_ui(point):
    icon = UI_TEMPLATES["category_icon"].get(point.category, "📍")
    
    # 优先使用数据库中的图片
    if hasattr(point, "cover_image") and point.cover_image:
        image = point.cover_image
    else:
        # 获取对应图片，如果没有则使用默认图
        image = UI_TEMPLATES["cover_images"].get(point.name, "/static/attractions/default.jpg")
    
    return {
        "ui_title": f"📸 {point.name}" if point.category == "摄影型" else f"{icon} {point.name}",
        "ui_subtitle": point.description,
        "ui_category_icon": icon,
        "ui_is_photo_hotspot": point.category == "摄影型",
        "ui_cover_image": image
    }
