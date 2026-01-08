import os
import requests
from datetime import datetime


def http_snapshot_once(url: str, lake_id: int, output_dir: str = "storage/snapshots") -> str | None:
    """
    从HTTP快照地址抓取一张图片并保存到本地，返回文件路径。
    适配ESP32-CAM等设备的 /capture 或 /jpg 路径。
    """
    os.makedirs(output_dir, exist_ok=True)
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        content = resp.content
        if not content:
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(output_dir, f"lake{lake_id}_{ts}.jpg")
        with open(path, "wb") as f:
            f.write(content)
        return path
    except Exception:
        return None