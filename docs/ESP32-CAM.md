# ESP32-CAM 沙盒测试环境搭建指南

本指南帮助你把 ESP32-CAM 作为可控的摄像头源，接入当前后端，完成从图像采集 → OpenCV分析 → 数据入库 → 小程序展示的闭环联调。

## 硬件准备
- ESP32-CAM 模块（建议 1–3 块）
- Micro USB 转 UART 下载器（如 FT232/CP2102）与杜邦线
- 5V/2A 电源
- 若使用 AI-Thinker 版本：IO0 与 GND 短接进入下载模式

## 固件选择
两种模式均可：
1) RTSP 视频流：兼容后端的 `capture_rtsp.py`，便于持续抓拍。
2) HTTP 快照服务：设备提供 `GET /capture` 返回 JPEG，后端从该地址拉取单帧分析（推荐简单稳定）。

下面给出 HTTP 快照固件示例（Arduino IDE），烧录后设备在本地网络提供 `http://<设备IP>/capture`：

```cpp
#include <WiFi.h>
#include "esp_camera.h"

// 替换为你的WiFi信息
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASS";

// AI Thinker PIN定义
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

WiFiServer server(80);

void startCamera()
{
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA; // 800x600，可根据需要调整
  config.jpeg_quality = 12;  // 10-30质量，数值越小质量越高
  config.fb_count = 1;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    while(true) delay(1000);
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  startCamera();
  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (!client) return;
  // 简易HTTP解析
  String req = client.readStringUntil('\r');
  client.readStringUntil('\n');
  if (req.indexOf("GET /capture") >= 0) {
    // 拍照并返回JPEG
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) { client.stop(); return; }
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: image/jpeg");
    client.println("Connection: close");
    client.println();
    client.write(fb->buf, fb->len);
    esp_camera_fb_return(fb);
  } else {
    client.println("HTTP/1.1 404 Not Found\r\n\r\n");
  }
  client.stop();
}
```

> 若需要RTSP固件，可参考开源 `esp32cam-rtsp` 项目或ESP32-IDF相关示例。

## 后端配置
- 在 `backend/.env` 设置（任选其一）：
  - `RTSP_LAKE_1=http://<设备IP>/capture`
  - 或 `RTSP_LAKE_1=rtsp://...`
- 重启后端：`uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

## 联调与验证
1. 文档页测试：打开 `http://127.0.0.1:8000/docs`，调用 `GET /api/prediction/realtime/1`。
   - 若没有现成图片，后端会从 `RTSP_LAKE_1`（HTTP或RTSP）抓拍一张保存到 `storage/snapshots` 并分析。
2. 主动上传测试：
   - `curl -F "lake_id=1" -F "file=@test.jpg" http://127.0.0.1:8000/api/prediction/upload_snapshot`
3. 查看图片：将返回的 `image_path` 文件名拼接到 `http://127.0.0.1:8000/snapshots/<文件名>`。
4. 小程序实时页面：编译并打开 `pages/realtime`，应显示最新抓拍图与指数、因子。

## 成功标准
- 能稳定获取ESP32-CAM图片并在后端分析出指数；
- 数据入库并可在API返回 `score`、`reason`、`factors`；
- 小程序实时页面展示设备拍摄的画面与悬浮卡片指标。

## 故障排查
- 抓拍失败：检查设备IP、WiFi、HTTP路径（`/capture`）、防火墙。
- 图片无法访问：确认已写入 `backend/storage/snapshots`，通过 `/snapshots/<文件名>` 访问。
- OpenCV解码失败：降低JPEG质量、调整分辨率（如 `FRAMESIZE_VGA`）。