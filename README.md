# 运城盐湖智能检查与推送系统（后端）

本项目是“盐湖出片预测与推送”的后端服务与AI分析骨架，支持：
- 数据采集：天气预报、监控截图（RTSP）、历史数据整理
- AI分析：实时色彩指数、24–48小时出片预测（可插拔模型）
- API服务：为微信小程序提供预测查询与订阅
- 定时任务：自动刷新预测并（后续）触发订阅推送

## 技术栈
- 后端：Python 3.10+，FastAPI
- 任务调度：APScheduler
- 数据库：默认SQLite（开发），生产建议PostgreSQL + Redis
- 计算机视觉：OpenCV（实时色彩分析）、NumPy
- 部署：Docker + Nginx（建议），云服务器推荐腾讯云

## 目录结构
```
backend/
  app/
    api/
      routes/
        predictions.py       # 预测与实时指数API
        subscriptions.py     # 订阅API（占位）
    capture/
      capture_rtsp.py        # RTSP定时截图（占位）
    db/
      session.py             # SQLAlchemy会话与Base
      models.py              # 基础表模型（占位）
    schemas/
      prediction.py          # Pydantic模式
      subscription.py        # Pydantic模式
    services/
      weather_client.py      # 天气API客户端（HeWeather占位）
      prediction_model.py    # 预测模型（规则占位，可替换为XGBoost/LSTM）
      realtime_index.py      # 实时色彩指数（占位：时段启发式）
    tasks/
      scheduler.py           # APScheduler定时任务
    main.py                  # FastAPI入口
  requirements.txt
  .env.example
  Dockerfile
  docker-compose.yml
```

## 环境变量（.env）
复制`.env.example`为`.env`并按需填写：
- `DATABASE_URL`：数据库连接（开发缺省为SQLite）
- `HEWEATHER_API_KEY`：和风天气API密钥（可选）
- `HEWEATHER_LOCATION`：和风天气location标识（如地理编码或城市ID）
- `RTSP_LAKE_1`、`RTSP_LAKE_2`：各湖区RTSP地址（可选）

## 启动（开发）
1) 安装依赖：
```
pip install -r requirements.txt
```
2) 运行后端：
```
uvicorn app.main:app --reload
```
访问API文档：`http://127.0.0.1:8000/docs`

## API概要
- `GET /api/prediction/today`
  - 返回今日各盐湖的“出片指数”和“最佳时间段”（当前为启发式规则）
- `GET /api/prediction/realtime/{lake_id}`
  - 返回指定湖区的实时指数（当前为启发式规则）
- `POST /api/subscribe`
  - 订阅推送（当前为内存占位，后续接入DB与微信订阅消息）

## 数据流（目标）
- 监控摄像头 → 视频流服务器 → 定时截图 → AI实时分析 → 实时出片指数 → DB
- 定时任务 → 天气API → AI预测模型 → 未来出片指数预测 → DB
- 小程序 → 请求后端API → 获取预测/实时数据 → 展示
- 后端定时任务 → 检查高出片指数时段 → 触发小程序订阅消息推送

## 模型策略（占位说明）
- 实时色彩分析：
  - 识别水体/盐田/藻类区域，计算饱和度、红/粉色占比，输出`0–100`指数。
  - 当前以时间段启发式返回占位结果，后续替换为OpenCV+CNN（ResNet/EfficientNet）。
- 出片率预测：
  - 输入未来24/48小时天气特征（温度、湿度、风速、云量、UV、降水）。
  - 输出各时间点的预测指数与最佳拍摄时间段。
  - 当前以规则占位，后续替换为XGBoost/LightGBM/LSTM并接入训练数据。

## 部署建议
- 使用Docker容器化后端，前置Nginx反向代理。
- 数据库选PostgreSQL，缓存用Redis；使用APScheduler或云原生定时器触发任务。
- 腾讯云CVM部署并与微信生态集成，后续接入微信订阅消息推送。

## 后续迭代
- 接入和风天气/中国气象局API的正式密钥与城市编码。
- RTSP截图入库，并基于OpenCV进行色彩特征提取与CNN训练。
- 完成DB表设计与消息推送服务，联动微信小程序订阅消息。
- 引入训练管线与评估（准确率与用户满意度>85%为目标）。
