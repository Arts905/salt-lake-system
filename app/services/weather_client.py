import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("weather")


def _requests_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def get_forecast(days: int = 2):
    """
    返回未来hours级别的天气数据（正式接入和风天气）。
    - 24小时数据使用 /v7/weather/24h
    - 若需要48小时，优先使用24小时并在末尾补充启发式；或如账号支持72h则改为72h并裁剪。
    返回结构：{"source": str, "hours": [{time, temp, humidity, uvIndex, windSpeed, cloud, precip, visibility}]}
    """
    api_key = os.getenv("HEWEATHER_API_KEY")
    # 固定应用默认定位：运城盐湖主景区坐标（经度,纬度），可被 HEWEATHER_LOCATION 覆盖
    location = os.getenv("HEWEATHER_LOCATION", "110.9775,35.0661")
    # 新增：可配置 API 基础域名（开发/商业），以及可选 Referer 与超时
    api_base = os.getenv("HEWEATHER_API_BASE", "https://devapi.qweather.com")
    referer = os.getenv("HEWEATHER_REFERER")
    timeout = int(os.getenv("HEWEATHER_TIMEOUT", "8"))

    hours = []
    if api_key:
        try:
            session = _requests_session()
            url_24h = f"{api_base}/v7/weather/24h?location={location}&key={api_key}"
            headers = {}
            if referer:
                headers["Referer"] = referer
            r = session.get(url_24h, headers=headers, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            for item in data.get("hourly", []):
                hours.append({
                    "time": item["fxTime"],
                    "temp": float(item["temp"]),
                    "humidity": int(item["humidity"]),
                    "uvIndex": int(item.get("uvIndex", 0)),
                    "windSpeed": float(item.get("windSpeed", 0)),
                    "cloud": int(item.get("cloud", 0)),
                    "precip": float(item.get("precip", 0.0)),
                    # 新增：能见度（km），QWeather字段为 vis
                    "visibility": float(item.get("vis", 0.0)),
                })
            logger.info(f"HeWeather获取成功，hour数: {len(hours)}，location={location}, base={api_base}, referer={referer or '-'}")
        except Exception as e:
            logger.exception(f"HeWeather调用失败: {e}")

    # 若需要48小时且不足，补充启发式段
    if days >= 2 and len(hours) < 48:
        now = datetime.fromisoformat(hours[0]["time"]) if hours else datetime.now().replace(minute=0, second=0, microsecond=0)
        needed = 48 - len(hours)
        for i in range(needed):
            t = now + timedelta(hours=len(hours) + i)
            hours.append({
                "time": t.isoformat(),
                "temp": 25 + (i % 6) - 3,
                "humidity": 40 + (i % 20),
                "uvIndex": 6 if 10 <= t.hour <= 16 else 1,
                "windSpeed": 3 + (i % 4),
                "cloud": 20 if 12 <= t.hour <= 16 else 50,
                "precip": 0.0,
                "visibility": 10.0,
            })

    if hours:
        return {"source": "HeWeather" if api_key else "dummy", "hours": hours}

    # 回退：生成24小时启发式数据
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    hours = []
    for i in range(24):
        t = now + timedelta(hours=i)
        hours.append({
            "time": t.isoformat(),
            "temp": 25 + (i % 6) - 3,
            "humidity": 40 + (i % 20),
            "uvIndex": 6 if 10 <= t.hour <= 16 else 1,
            "windSpeed": 3 + (i % 4),
            "cloud": 20 if 12 <= t.hour <= 16 else 50,
            "precip": 0.0,
            "visibility": 10.0,
        })
    logger.warning("使用启发式天气数据回退")
    return {"source": "dummy", "hours": hours}