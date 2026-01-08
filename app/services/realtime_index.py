import os
from datetime import datetime
import glob
import cv2

from sqlalchemy.orm import Session
from app.schemas.prediction import RealtimeIndex
from app.db.session import SessionLocal
from app.db.crud_realtime import save_realtime_index
from app.capture.capture_rtsp import capture_once
from app.capture.capture_http import http_snapshot_once
from app.services.image_analysis import compute_color_features, score_from_features, build_reason_from_features


def _find_latest_snapshot(lake_id: int, dir_path: str = "storage/snapshots") -> str | None:
    pattern = os.path.join(dir_path, f"lake{lake_id}_*.jpg")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


def compute_and_store_realtime_index(lake_id: int) -> RealtimeIndex:
    """
    RTSP→截图（若可用）→分析HSV与红/粉比例→计算指数→写入DB→返回。
    若无截图可用，则尝试按需抓取；仍失败则回退启发式但也写库。
    """
    lake_name = f"{lake_id}号盐湖"
    captured_at = datetime.now()
    img_path = _find_latest_snapshot(lake_id)

    # 如无图片且配置了抓取地址，尝试按需抓取一张（支持RTSP/HTTP）
    if not img_path:
        stream_env_key = f"RTSP_LAKE_{lake_id}"
        stream_url = os.getenv(stream_env_key)
        if stream_url:
            if stream_url.startswith("http"):
                img_path = http_snapshot_once(stream_url, lake_id)
            else:
                img_path = capture_once(stream_url, lake_id)

    score = 0
    feats = {"saturation_mean": 0.0, "red_ratio": 0.0, "pink_ratio": 0.0}
    reason = ""
    if img_path and os.path.exists(img_path):
        img = cv2.imread(img_path)
        feats = compute_color_features(img)
        img_score = score_from_features(feats)
        reason_img = build_reason_from_features(feats)
        from app.services.weather_client import get_forecast
        from app.services.prediction_model import deep_weather_score, build_weather_reason_and_factors
        forecast = get_forecast(days=1)
        hours = forecast.get("hours", [])
        if hours:
            h1 = hours[max(0, len(hours) - 2)]
            h2 = hours[-1]
            w_score = (deep_weather_score(h1) + deep_weather_score(h2)) / 2
            w_reason, w_factors = build_weather_reason_and_factors(h1, h2)
        else:
            w_score = img_score * 0.0
            w_reason, w_factors = "天气数据缺失，按图像分析为准。", {"weather": {}}
        score = int(round(0.75 * img_score + 0.25 * w_score))
        reason = f"{reason_img} 天气参考：{w_reason.replace('预测：', '')}"
        factors = {"image_analysis": feats}
        factors.update(w_factors)

        # 融合现场传感器数据（如有）
        from app.db.session import SessionLocal as _SessionLocal
        from app.db.crud_sensor import get_latest_sensor_reading
        db_s = _SessionLocal()
        try:
            sensor = get_latest_sensor_reading(db_s, lake_id)
        finally:
            db_s.close()
        if sensor:
            s = {
                "air_temp": sensor.air_temp,
                "humidity": sensor.humidity,
                "wind_speed": sensor.wind_speed,
                "water_temp": sensor.water_temp,
                "salinity": sensor.salinity,
                "dissolved_oxygen": sensor.dissolved_oxygen,
                "tds": sensor.tds,
                "turbidity": sensor.turbidity,
                "captured_at": sensor.captured_at.isoformat(),
            }
            factors["sensor"] = s
            # 适度调整分数（-6~+6），偏好：低湿度、适中风速、温度舒适、盐度较高
            adjust = 0.0
            if sensor.humidity is not None:
                adjust += max(-4.0, min(4.0, (60 - float(sensor.humidity)) * 0.05))
            if sensor.wind_speed is not None:
                adjust += max(-2.0, min(2.0, -abs(float(sensor.wind_speed) - 4.0) * 0.5 + 2.0))
            if sensor.air_temp is not None:
                adjust += max(-2.0, min(2.0, -abs(float(sensor.air_temp) - 28.0) * 0.2 + 2.0))
            if sensor.water_temp is not None:
                adjust += max(-2.0, min(2.0, -abs(float(sensor.water_temp) - 25.0) * 0.2 + 2.0))
            if sensor.salinity is not None:
                adjust += max(0.0, min(2.0, (float(sensor.salinity) - 20.0) * 0.1))
            score = int(max(0, min(100, round(score + adjust))))
            # 补充说明
            parts = []
            if sensor.wind_speed is not None:
                parts.append(f"风速{sensor.wind_speed}m/s")
            if sensor.humidity is not None:
                parts.append(f"湿度{sensor.humidity}%")
            if sensor.water_temp is not None:
                parts.append(f"水温{sensor.water_temp}℃")
            if sensor.salinity is not None:
                parts.append(f"盐度{sensor.salinity}")
            if parts:
                reason = reason + " 现场监测参考：" + "、".join(parts) + "。"
    else:
        # 回退：时段启发式
        hour = captured_at.hour
        score = max(10, min(95, 50 + (16 - abs(14 - hour)) * 3))
        reason = "实时：未获取到图像，按时段启发式估计。"
        factors = {"image_analysis": feats}

    # 写入DB
    db: Session = SessionLocal()
    try:
        rec = save_realtime_index(db, lake_id, lake_name, int(score), img_path, captured_at)
    finally:
        db.close()

    return RealtimeIndex(
        lake_id=lake_id,
        lake_name=lake_name,
        score=int(score),
        captured_at=captured_at.isoformat(),
        image_path=img_path,
        reason=reason,
        factors=factors,
    )