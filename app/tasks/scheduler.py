from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
from sqlalchemy import func

# Lazy imports moved inside functions to prevent import loops or side effects
# from app.services.weather_client import get_forecast
# ...

scheduler = BackgroundScheduler()
logger = logging.getLogger("scheduler")

LAKES = [] # Deprecated, use DB

def _parse_iso(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return datetime.now()


def _check_and_trigger_push(db, preds):
    """检查订阅阈值并打印模拟推送日志。"""
    from app.db.crud_subscriptions import get_all_subscriptions
    
    subs = get_all_subscriptions(db)
    now = datetime.now()
    within_2h = now + timedelta(hours=2)
    for sub in subs:
        try:
            lake_ids = [int(x) for x in (sub.lake_ids or '').split(',') if x]
        except ValueError:
            lake_ids = []
        for p in preds:
            if p.lake_id in lake_ids and p.score >= (sub.threshold or 90):
                start_dt = _parse_iso(p.best_time.start)
                if now <= start_dt <= within_2h:
                    # 模拟推送触发日志
                    logger.info(
                        f"[PUSH TRIGGER] 用户[{sub.openid}]订阅的{p.lake_name}将在{start_dt.strftime('%H:%M')}达到{p.score}分，准备推送！"
                    )

def refresh_predictions():
    from app.db.session import SessionLocal
    from app.db.models_poi import PointOfInterest
    from app.services.weather_client import get_forecast
    from app.services.prediction_model import predict_for_lakes
    from app.db.crud import save_predictions
    
    db = SessionLocal()
    try:
        # 从数据库动态加载所有点位
        pois = db.query(PointOfInterest).all()
        lakes = [{"id": p.id, "name": p.name} for p in pois]
        
        if not lakes:
            logger.warning("No POIs found in DB, skipping prediction refresh.")
            return

        forecast = get_forecast(days=2)
        preds = predict_for_lakes(lakes, forecast)
        save_predictions(db, preds)
        logger.info(f"刷新预测成功，写入{len(preds)}条。")
        _check_and_trigger_push(db, preds)
    except Exception as e:
        logger.exception(f"刷新预测失败: {e}")
    finally:
        db.close()

from app.utils.ui_templates import UI_TEMPLATES

def check_daily_recommendations():
    """每日推荐检查任务 (8:00, 16:00)"""
    from app.db.session import SessionLocal
    from app.db.models_poi import PointOfInterest
    from app.services.realtime_index import compute_and_store_realtime_index
    from app.db.models import RealtimeIndexRecord
    
    logger.info("开始每日推荐检查...")
    db = SessionLocal()
    try:
        # 1. 查询符合条件的点位：category == '摄影型' 且 composite_score >= 0.70
        candidates = db.query(PointOfInterest).filter(
            PointOfInterest.category == '摄影型',
            PointOfInterest.composite_score >= 0.70
        ).all()
        
        if not candidates:
            logger.info("未找到符合条件的推荐点位")
            return

        for poi in candidates:
            try:
                # 2. 获取当前实时指数
                # 注意：poi.id 需要对应 lake_id。假设数据中的ID与实时监测的Lake ID一致
                current_idx = compute_and_store_realtime_index(poi.id)
                current_score = float(current_idx.score)
                
                # 3. 获取昨日平均指数
                yesterday_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
                yesterday_end = yesterday_start + timedelta(days=1)
                
                avg_score = db.query(func.avg(RealtimeIndexRecord.score)).filter(
                    RealtimeIndexRecord.lake_id == poi.id,
                    RealtimeIndexRecord.captured_at >= yesterday_start,
                    RealtimeIndexRecord.captured_at < yesterday_end
                ).scalar()
                
                if avg_score is None:
                    logger.info(f"点位[{poi.name}]昨日无数据，跳过对比")
                    continue
                    
                avg_score = float(avg_score)
                if avg_score == 0:
                    continue # 避免除以零
                    
                # 4. 计算提升率
                lift = (current_score - avg_score) / avg_score
                
                if lift > 0.15:
                    # 使用 UI 模板生成推送内容
                    title = UI_TEMPLATES["photo_alert_title"].format(name=poi.name)
                    body = UI_TEMPLATES["photo_alert_body"].format(
                        score=current_score,
                        description=poi.description
                    )
                    
                    logger.info(f"[WECHAT PUSH] {title} | {body}")
                    # 在此处添加实际的微信推送逻辑
                    
            except Exception as e:
                logger.error(f"处理点位[{poi.name}]推荐检查时出错: {e}")
                
    except Exception as e:
        logger.exception(f"每日推荐检查失败: {e}")
    finally:
        db.close()


def start_scheduler():
    try:
        scheduler.add_job(
            refresh_predictions,
            "interval",
            hours=1,
            id="refresh_predictions",
            next_run_time=datetime.now(),
        )
        
        # 添加每日推荐检查任务
        scheduler.add_job(
            check_daily_recommendations,
            "cron",
            hour="8,16",
            minute=0,
            id="daily_recommend_check"
        )
        
        scheduler.start()
        logger.info("定时任务已启动")
    except Exception as e:
        logger.exception("Scheduler start error: %s", e)


def shutdown_scheduler():
    try:
        scheduler.shutdown()
        logger.info("定时任务已关闭")
    except Exception:
        pass
