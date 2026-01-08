import time
import os
from datetime import datetime

try:
    import cv2
except ImportError:
    cv2 = None


def capture_rtsp(rtsp_url: str, lake_id: int, interval_seconds: int = 60, output_dir: str = "storage/snapshots"):
    if not cv2:
        print("OpenCV not available. Skipping RTSP capture.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("无法打开RTSP流:", rtsp_url)
        return
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("读取帧失败，重试...")
                time.sleep(2)
                continue
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(output_dir, f"lake{lake_id}_{ts}.jpg")
            cv2.imwrite(path, frame)
            print("已保存截图:", path)
            time.sleep(interval_seconds)
    finally:
        cap.release()


def capture_once(rtsp_url: str, lake_id: int, output_dir: str = "storage/snapshots") -> str | None:
    """抓取单张并返回文件路径，用于定时任务按需截图。"""
    if not cv2:
        print("OpenCV not available. Skipping capture_once.")
        return None
        
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("无法打开RTSP流:", rtsp_url)
        return None
    try:
        ret, frame = cap.read()
        if not ret:
            print("读取帧失败")
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(output_dir, f"lake{lake_id}_{ts}.jpg")
        cv2.imwrite(path, frame)
        print("已保存截图:", path)
        return path
    finally:
        cap.release()