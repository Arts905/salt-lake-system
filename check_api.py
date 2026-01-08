import requests
import json

try:
    response = requests.get("http://127.0.0.1:8000/api/recommend")
    response.raise_for_status()
    data = response.json()
    if data:
        print("First item sample:")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
        
        has_cover = all("ui_cover_image" in item for item in data)
        print(f"\nAll items have ui_cover_image: {has_cover}")
    else:
        print("No data returned")
except Exception as e:
    print(f"Error: {e}")
