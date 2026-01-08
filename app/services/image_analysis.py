import numpy as np
from typing import Dict

try:
    import cv2
except ImportError:
    cv2 = None


# 重新定义：分区域分析（湖面+天空），并侧重湖面颜色
# 保持函数名与接口不变，向下兼容（返回中仍包含旧键，但语义改为湖面区域）

def compute_color_features(img_bgr: np.ndarray) -> Dict[str, float]:
    """
    提取色彩特征（分区域）：
    - 湖面区域（底部 65%）：饱和度、红/粉占比、粉色鲜艳度
    - 天空区域（顶部 35%）：蓝色占比、亮度均值、白云占比
    返回的字典将包含：
    - lake_saturation, lake_red_ratio, lake_pink_ratio, lake_pink_vivid_ratio
    - sky_blue_ratio, sky_brightness_mean, sky_whiteness_ratio
    - saturation_mean（与 lake_saturation 一致，用于兼容旧逻辑）
    - red_ratio, pink_ratio（与湖面区域一致，用于兼容旧逻辑）
    """
    if cv2 is None:
        # 如果没有 OpenCV，返回默认全0特征
        return {
            "lake_saturation": 0.0,
            "lake_red_ratio": 0.0,
            "lake_pink_ratio": 0.0,
            "lake_pink_vivid_ratio": 0.0,
            "sky_blue_ratio": 0.0,
            "sky_brightness_mean": 0.0,
            "sky_whiteness_ratio": 0.0,
            "saturation_mean": 0.0,
            "red_ratio": 0.0,
            "pink_ratio": 0.0,
        }

    if img_bgr is None or img_bgr.size == 0:
        return {
            "lake_saturation": 0.0,
            "lake_red_ratio": 0.0,
            "lake_pink_ratio": 0.0,
            "lake_pink_vivid_ratio": 0.0,
            "sky_blue_ratio": 0.0,
            "sky_brightness_mean": 0.0,
            "sky_whiteness_ratio": 0.0,
            "saturation_mean": 0.0,
            "red_ratio": 0.0,
            "pink_ratio": 0.0,
        }

    h, w = img_bgr.shape[:2]
    split_y = int(h * 0.35)  # 顶部天空约 35%，底部湖面约 65%
    sky = img_bgr[:split_y, :]
    lake = img_bgr[split_y:, :]

    # 湖面分析（关注盐藻红/粉）
    lake_hsv = cv2.cvtColor(lake, cv2.COLOR_BGR2HSV)
    lh, ls, lv = cv2.split(lake_hsv)
    lake_sat = float(np.mean(ls)) / 255.0

    # 红色范围（HSV：H 0-10 或 170-180），S/V 适中
    red_mask1 = (lake_hsv[:, :, 0] <= 10) & (lake_hsv[:, :, 1] > 80) & (lake_hsv[:, :, 2] > 50)
    red_mask2 = (lake_hsv[:, :, 0] >= 170) & (lake_hsv[:, :, 1] > 80) & (lake_hsv[:, :, 2] > 50)
    red_mask = red_mask1 | red_mask2

    # 粉色范围（OpenCV H 150-170，S 略低、V 高）
    pink_mask = (lake_hsv[:, :, 0] >= 150) & (lake_hsv[:, :, 0] <= 170) & (lake_hsv[:, :, 1] > 40) & (lake_hsv[:, :, 2] > 120)
    # 粉色鲜艳度（更高的饱和度与亮度）
    pink_vivid_mask = (lake_hsv[:, :, 0] >= 145) & (lake_hsv[:, :, 0] <= 175) & (lake_hsv[:, :, 1] > 100) & (lake_hsv[:, :, 2] > 130)

    lake_total = max(1, lake.shape[0] * lake.shape[1])
    lake_red_ratio = float(np.count_nonzero(red_mask)) / lake_total
    lake_pink_ratio = float(np.count_nonzero(pink_mask)) / lake_total
    lake_pink_vivid_ratio = float(np.count_nonzero(pink_vivid_mask)) / lake_total

    # 天空分析（关注蓝度与云量/亮度）
    sky_hsv = cv2.cvtColor(sky, cv2.COLOR_BGR2HSV)
    sh, ss, sv = cv2.split(sky_hsv)
    sky_brightness = float(np.mean(sv))  # 0-255

    # 蓝色范围（OpenCV H 90-130，S/V 适中）
    blue_mask = (sky_hsv[:, :, 0] >= 90) & (sky_hsv[:, :, 0] <= 130) & (sky_hsv[:, :, 1] > 50) & (sky_hsv[:, :, 2] > 60)

    # 白云（高亮且低饱和度），近似：S < 30 且 V > 180
    white_mask = (sky_hsv[:, :, 1] < 30) & (sky_hsv[:, :, 2] > 180)

    sky_total = max(1, sky.shape[0] * sky.shape[1])
    sky_blue_ratio = float(np.count_nonzero(blue_mask)) / sky_total
    sky_whiteness_ratio = float(np.count_nonzero(white_mask)) / sky_total

    return {
        "lake_saturation": lake_sat,
        "lake_red_ratio": lake_red_ratio,
        "lake_pink_ratio": lake_pink_ratio,
        "lake_pink_vivid_ratio": lake_pink_vivid_ratio,
        "sky_blue_ratio": sky_blue_ratio,
        "sky_brightness_mean": sky_brightness / 255.0,  # 归一化到0-1
        "sky_whiteness_ratio": sky_whiteness_ratio,
        # 兼容旧字段（改为湖面语义）
        "saturation_mean": lake_sat,
        "red_ratio": lake_red_ratio,
        "pink_ratio": lake_pink_ratio,
    }


def score_from_features(feats: Dict[str, float]) -> int:
    """根据特征计算0-100出片指数：湖面为主（85%），天空为辅（15%）。"""
    # 湖面
    sat_lake = float(feats.get("lake_saturation", feats.get("saturation_mean", 0.0)))
    red_lake = float(feats.get("lake_red_ratio", feats.get("red_ratio", 0.0)))
    pink_lake = float(feats.get("lake_pink_ratio", feats.get("pink_ratio", 0.0)))
    pink_vivid = float(feats.get("lake_pink_vivid_ratio", pink_lake))

    # 天空
    blue = float(feats.get("sky_blue_ratio", 0.0))
    sky_brightness = float(feats.get("sky_brightness_mean", 0.0))  # 0-1
    white = float(feats.get("sky_whiteness_ratio", 0.0))

    # 强化“显粉”贡献：鲜艳度与覆盖度综合
    lake_color_power = (0.7 * min(0.85, pink_vivid) + 0.3 * min(0.85, (red_lake + pink_lake)))
    # 饱和度作为次要加分，避免粉色画面被平均饱和度拉低
    lake_score = 100 * (0.7 * lake_color_power + 0.3 * min(1.0, sat_lake))

    # 天空蓝度与亮度加分，白云适度扣分（影响较小）
    sky_score = 100 * (0.6 * min(0.7, blue) + 0.4 * sky_brightness - 0.2 * min(0.7, white))
    score = 0.85 * lake_score + 0.15 * sky_score
    return int(max(0, min(100, round(score))))


def build_reason_from_features(feats: Dict[str, float]) -> str:
    sat_lake = float(feats.get("lake_saturation", feats.get("saturation_mean", 0.0)))
    red_lake = float(feats.get("lake_red_ratio", feats.get("red_ratio", 0.0)))
    pink_lake = float(feats.get("lake_pink_ratio", feats.get("pink_ratio", 0.0)))
    pink_vivid = float(feats.get("lake_pink_vivid_ratio", pink_lake))
    blue = float(feats.get("sky_blue_ratio", 0.0))
    white = float(feats.get("sky_whiteness_ratio", 0.0))
    bright = float(feats.get("sky_brightness_mean", 0.0))

    parts = []
    # 湖面表达
    if sat_lake >= 0.6:
        parts.append("湖面饱和度高")
    elif sat_lake >= 0.4:
        parts.append("湖面饱和度适中")
    else:
        parts.append("湖面饱和度偏低")

    # 显粉强度（鲜艳度为主，覆盖度为辅）
    if pink_vivid >= 0.20 or (red_lake + pink_lake) >= 0.35:
        parts.append("粉色表现极为鲜明")
    elif pink_vivid >= 0.12 or (red_lake + pink_lake) >= 0.20:
        parts.append("红/粉色盐藻表现明显")
    elif (red_lake + pink_lake) >= 0.10:
        parts.append("红/粉色盐藻略有表现")
    else:
        parts.append("红/粉色盐藻较弱")

    # 天空表达
    if blue >= 0.25:
        parts.append("天空蓝度较高")
    elif blue >= 0.12:
        parts.append("天空蓝度一般")
    else:
        parts.append("天空蓝度较低")

    if white >= 0.35:
        parts.append("云量较多")
    elif white >= 0.18:
        parts.append("云量适中")
    else:
        parts.append("云量较少")

    if bright >= 0.6:
        parts.append("光照充足")
    elif bright >= 0.4:
        parts.append("光照一般")
    else:
        parts.append("光照较弱")

    # 结论短语依据综合得分
    final_score = score_from_features(feats)
    if final_score >= 80:
        concl = "综合表现很优"
    elif final_score >= 60:
        concl = "综合表现较优"
    elif final_score >= 40:
        concl = "综合表现一般"
    else:
        concl = "综合表现较弱"

    return "实时：" + "，".join(parts) + "，" + concl + "。"