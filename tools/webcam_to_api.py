#!/usr/bin/env python3
"""
Capture one frame from local webcam and upload to backend /api/prediction/upload_snapshot.
Works on Windows with default webcam (index 0).
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import requests


def capture_frame(camera_index: int, width=None, height=None):
    # Use DirectShow backend for Windows to avoid delays
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    if width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError("Failed to read frame from camera")
    return frame


def encode_jpeg(frame, quality=90):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    ok, buf = cv2.imencode(".jpg", frame, encode_param)
    if not ok:
        raise RuntimeError("Failed to encode JPEG")
    return buf.tobytes()


def upload_snapshot(server: str, lake_id: int, jpeg_bytes: bytes, filename: str = "webcam.jpg", timeout=15):
    url = server.rstrip("/") + "/api/prediction/upload_snapshot"
    files = {"file": (filename, jpeg_bytes, "image/jpeg")}
    data = {"lake_id": str(lake_id)}
    resp = requests.post(url, data=data, files=files, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Capture from local webcam and upload to backend /upload_snapshot.")
    parser.add_argument("--lake-id", type=int, default=1, help="Lake ID to tag the snapshot")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (0 for default)")
    parser.add_argument("--server", type=str, default="http://127.0.0.1:8000", help="Backend server base URL")
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality (1-100)")
    parser.add_argument("--save-local", action="store_true", help="Also save a local copy for preview")
    parser.add_argument("--preview", action="store_true", help="Show the captured frame in a window")
    parser.add_argument("--width", type=int, help="Capture width")
    parser.add_argument("--height", type=int, help="Capture height")
    args = parser.parse_args()

    try:
        frame = capture_frame(args.camera, args.width, args.height)
        if args.preview:
            cv2.imshow("Captured", frame)
            cv2.waitKey(500)
            cv2.destroyAllWindows()
        jpeg_bytes = encode_jpeg(frame, quality=args.quality)
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"webcam_{ts}.jpg"
        result = upload_snapshot(args.server, args.lake_id, jpeg_bytes, filename=filename)
        print("Uploaded successfully. Backend response:")
        print(result)

        if args.save_local:
            out_dir = Path(__file__).resolve().parents[1] / "storage" / "snapshots"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"local_{filename}"
            with open(out_path, "wb") as f:
                f.write(jpeg_bytes)
            print(f"Saved local copy: {out_path}")
            print(f"Access via: {args.server.rstrip('/')}/snapshots/{out_path.name}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()