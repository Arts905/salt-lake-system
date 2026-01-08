from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from sqlalchemy.orm import Session

from app.schemas.prediction import LakePrediction, RealtimeIndex, BestRealtimeResponse, BestTodayResponse
from app.services.weather_client import get_forecast
from app.services.prediction_model import predict_for_lakes
from app.services.realtime_index import compute_and_store_realtime_index
from app.db.session import SessionLocal
from app.db.crud import get_latest_predictions
from app.db.crud_realtime import save_realtime_index
import os
from datetime import datetime
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

router = APIRouter()

LAKES = [
    {"id": 1, "name": "1号盐湖"},
    {"id": 2, "name": "2号盐湖"},
    {"id": 3, "name": "3号盐湖"},
]


@router.get("/today", response_model=List[LakePrediction])
def get_today_prediction():
    db: Session = SessionLocal()
    try:
        preds = get_latest_predictions(db)
        forecast = get_forecast(days=2)
        if preds:
            # 数据库存在：补充reason与factors
            from app.services.prediction_model import attach_explanations
            return attach_explanations(preds, forecast)
        # Fallback: 若DB为空，实时计算一批（含reason/factors）
        preds = predict_for_lakes(LAKES, forecast, hours=24)
        return preds
    finally:
        db.close()


@router.get("/realtime/{lake_id}", response_model=RealtimeIndex)
def get_realtime(lake_id: int):
    idx = compute_and_store_realtime_index(lake_id)
    return idx


@router.get("/realtime/best", response_model=BestRealtimeResponse)
def get_best_realtime():
    """计算并返回当前3个湖区的实时指数及最佳项"""
    indexes = [compute_and_store_realtime_index(l["id"]) for l in LAKES]
    best = max(indexes, key=lambda x: x.score)
    return BestRealtimeResponse(best=best, all=indexes)


@router.post("/upload_snapshot", response_model=RealtimeIndex)
async def upload_snapshot(lake_id: int = Form(...), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="空文件")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_path = "storage/snapshots"
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception:
            # Vercel read-only fallback
            dir_path = "/tmp"
            
        filename = f"lake{lake_id}_{ts}.jpg"
        file_path = os.path.join(dir_path, filename)
        with open(file_path, "wb") as f:
            f.write(contents)
            
        # Check OpenCV availability
        if cv2 is None:
             # Serverless fallback: Return a mock success response
            return RealtimeIndex(
                lake_id=lake_id,
                lake_name=f"{lake_id}号盐湖",
                score=80,
                captured_at=datetime.now().isoformat(),
                image_path=file_path,
                reason="Serverless模式：图片已接收，但OpenCV未安装，跳过分析。",
                factors={"image_analysis": {"mock": True}},
            )
            
        # 直接在内存中解码并分析
        arr = np.frombuffer(contents, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="无法解码图片")
        from app.services.image_analysis import (
            compute_color_features,
            score_from_features,
            build_reason_from_features,
        )
        feats = compute_color_features(img)
        img_score = score_from_features(feats)
        reason_img = build_reason_from_features(feats)

        # 天气评分融合（取上传时刻附近两小时窗口）
        from app.services.weather_client import get_forecast
        from app.services.prediction_model import deep_weather_score, build_weather_reason_and_factors
        forecast = get_forecast(days=1)
        hours = forecast.get("hours", [])
        if hours:
            # 简单取最后两个小时作为近似窗口
            h1 = hours[max(0, len(hours) - 2)]
            h2 = hours[-1]
            w_score = (deep_weather_score(h1) + deep_weather_score(h2)) / 2
            w_reason, w_factors = build_weather_reason_and_factors(h1, h2)
        else:
            w_score = img_score * 0.0  # 无天气时不影响
            w_reason, w_factors = "天气数据缺失，按图像分析为准。", {"weather": {}}

        final_score = int(round(0.75 * img_score + 0.25 * w_score))
        final_reason = f"{reason_img} 天气参考：{w_reason.replace('预测：', '')}"
        final_factors = {"image_analysis": feats}
        final_factors.update(w_factors)

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
            final_factors["sensor"] = s
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
            final_score = int(max(0, min(100, round(final_score + adjust))))
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
                final_reason = final_reason + " 现场监测参考：" + "、".join(parts) + "。"
        # 写库
        db: Session = SessionLocal()
        captured_at = datetime.now()
        try:
            save_realtime_index(db, lake_id, f"{lake_id}号盐湖", final_score, file_path, captured_at)
        finally:
            db.close()
        return RealtimeIndex(
            lake_id=lake_id,
            lake_name=f"{lake_id}号盐湖",
            score=int(final_score),
            captured_at=captured_at.isoformat(),
            image_path=file_path,
            reason=final_reason,
            factors=final_factors,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传处理失败: {e}")


@router.get("/today/best", response_model=BestTodayResponse)
def get_today_best():
    """返回当天预测的最佳湖区及完整列表（含原因/因素）"""
    db: Session = SessionLocal()
    try:
        preds = get_latest_predictions(db)
        forecast = get_forecast(days=2)
        lakes = get_all_lakes_dict(db)
        
        if preds and len(preds) >= len(lakes):
            from app.services.prediction_model import attach_explanations
            preds = attach_explanations(preds, forecast)
        else:
            preds = predict_for_lakes(lakes, forecast, hours=24)
            
        best = max(preds, key=lambda x: x.score)
        return BestTodayResponse(best=best, all=preds)
    finally:
        db.close()