from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from app.services.weather_client import get_forecast

router = APIRouter()

@router.get("/now2h")
def get_now_and_next2h() -> Dict[str, Any]:
    """返回当前小时和未来两个小时的天气要素。
    依赖服务器端和风天气配置，避免在小程序暴露密钥。
    返回示例：
    {
      "source": "HeWeather",
      "now": { ... },
      "next2h": [{ ... }, { ... }]
    }
    """
    fc = get_forecast(days=1)
    hours = fc.get("hours", [])
    result: Dict[str, Any] = {
        "source": fc.get("source", "HeWeather"),
        "now": None,
        "next2h": []
    }
    if hours:
        # 取列表前3个作为当前与后续两小时（若不足自动裁剪）
        result["now"] = hours[0]
        result["next2h"] = hours[1:3]
    return result