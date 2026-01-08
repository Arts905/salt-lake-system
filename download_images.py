import os
import requests
import hashlib

# 必须与 ui_templates.py 中的定义一致
cover_images = {
    "盐湖湿地公园": "https://images.unsplash.com/photo-1596323102374-e85d95d85202?q=80&w=600&auto=format&fit=crop", # 湿地风景
    "22号堤埝": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?q=80&w=600&auto=format&fit=crop", # 森林堤坝
    "落日红堤": "https://images.unsplash.com/photo-1472120435266-53107fd0c44a?q=80&w=600&auto=format&fit=crop", # 夕阳
    "鸟类观测点1": "https://images.unsplash.com/photo-1552728089-57bdde30ebd1?q=80&w=600&auto=format&fit=crop", # 鸟类
    "野生大豆观测点": "https://images.unsplash.com/photo-1530634963246-86d701a221f4?q=80&w=600&auto=format&fit=crop", # 植物
    "色彩之境": "https://images.unsplash.com/photo-1508197149814-0cc02a8b7f82?q=80&w=600&auto=format&fit=crop", # 多彩
    "天空之境": "https://images.unsplash.com/photo-1494548162494-384bba4ab999?q=80&w=600&auto=format&fit=crop", # 镜面
    "项链池": "https://images.unsplash.com/photo-1518098268026-4e1c91a28a67?q=80&w=600&auto=format&fit=crop", # 池子
    "湿地芦苇荡": "https://images.unsplash.com/photo-1476900966873-12c44288a7c1?q=80&w=600&auto=format&fit=crop", # 芦苇
    "天鹅湖": "https://images.unsplash.com/photo-1548504769-900b70ed122e?q=80&w=600&auto=format&fit=crop", # 天鹅
    "硝花池": "https://images.unsplash.com/photo-1623945206065-274a62c4e234?q=80&w=600&auto=format&fit=crop", # 盐花
    "鸟类观测点2": "https://images.unsplash.com/photo-1452570053594-1b985d6ea890?q=80&w=600&auto=format&fit=crop", # 另一种鸟
    "盐湖博物馆": "https://images.unsplash.com/photo-1565060169194-1188383a8b66?q=80&w=600&auto=format&fit=crop" # 博物馆建筑
}

SAVE_DIR = "storage/attractions"
os.makedirs(SAVE_DIR, exist_ok=True)

new_mapping = {}

def download_images():
    print(f"Start downloading {len(cover_images)} images to {SAVE_DIR}...")
    
    for name, url in cover_images.items():
        try:
            print(f"Downloading {name}...")
            # Generate filename from hash of URL or name to be consistent
            ext = ".jpg"
            safe_name = hashlib.md5(name.encode('utf-8')).hexdigest()
            filename = f"{safe_name}{ext}"
            file_path = os.path.join(SAVE_DIR, filename)
            
            # Check if exists
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"  - Exists: {filename}")
            else:
                # Try original URL
                print(f"  - Requesting: {url}")
                resp = requests.get(url, timeout=30)
                
                if resp.status_code != 200:
                    print(f"  - Failed {resp.status_code}, trying fallback random image...")
                    # Fallback to a reliable random image source
                    resp = requests.get(f"https://picsum.photos/seed/{safe_name}/600/400", timeout=30)
                
                if resp.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(resp.content)
                    print(f"  - Saved: {filename}")
                else:
                    print(f"  - Failed completely: {resp.status_code}")
                    continue
            
            # Update mapping
            new_mapping[name] = f"/static/attractions/{filename}"
            
        except Exception as e:
            print(f"  - Error: {e}")

    print("\nComplete! Here is the new mapping dict for ui_templates.py:")
    print("="*50)
    for k, v in new_mapping.items():
        print(f'        "{k}": "{v}",')
    print("="*50)

if __name__ == "__main__":
    download_images()
