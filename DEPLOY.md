# 盐湖导览系统部署与维护手册 (DEPLOY.md)

本文档详细说明了如何将盐湖导览系统部署到生产环境（AWS/阿里云），以及后续的维护流程。

## 1. 系统架构
- **前端**：HTML5/JS (Vue/Vanilla)，嵌入在后端静态服务中。
- **后端**：Python FastAPI，提供 REST API。
- **数据库**：SQLite (默认/开发)，生产环境推荐 PostgreSQL。
- **容器化**：Docker + Docker Compose。

## 2. 部署前准备 (Pre-flight Checklist)
- [ ] 申请云服务器 (ECS/EC2)，建议配置：2核 4G内存及以上。
- [ ] 申请域名并完成备案 (如需要)。
- [ ] 申请 SSL 证书 (Let's Encrypt 或云厂商提供)。
- [ ] 安装 Docker 和 Docker Compose。

## 3. 部署步骤 (Deployment)

### 3.1 获取代码
在服务器上克隆代码库：
```bash
git clone https://github.com/your-repo/salt-lake-system.git
cd salt-lake-system/backend
```

### 3.2 配置环境变量
复制并编辑配置文件：
```bash
cp .env.example .env
vi .env
```
确保修改以下安全项：
- `DATABASE_URL`: 如果使用外部 PostgreSQL，请在此配置。
- `SECRET_KEY`: 用于 Session 加密。
- **OSS 对象存储 (推荐)**: 
  如果使用 Vercel 或希望图片持久化，请添加以下变量：
  ```
  ALIYUN_ACCESS_KEY_ID=your_id
  ALIYUN_ACCESS_KEY_SECRET=your_secret
  ALIYUN_OSS_BUCKET=your_bucket_name
  ALIYUN_OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
  ```

### 3.3 启动服务 (Docker)
使用 Docker Compose 一键启动：
```bash
docker-compose up -d --build
```
查看日志确保启动成功：
```bash
docker-compose logs -f
```

### 3.4 配置 Nginx (反向代理 & SSL)
建议在宿主机安装 Nginx 作为网关：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8085;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 4. 自动化运维 (CI/CD)
本项目已配置 GitHub Actions (`.github/workflows/ci.yml`)。
- **自动测试**：每次 Push 代码到 `main` 分支会自动运行 Pytest。
- **自动构建**：测试通过后会构建 Docker 镜像。
- **自动部署**：(需配置 SSH Key) 可自动 SSH 到服务器拉取最新镜像并重启。

## 5. 维护与监控 (Maintenance)

### 5.1 数据备份
建议设置 Crontab 每天凌晨备份数据库：
```bash
# 每日备份 SQLite 文件 (如果是 PostgreSQL 请用 pg_dump)
0 3 * * * cp /app/data.db /backup/data_$(date +\%F).db
```

### 5.2 日志监控
- 实时日志：`docker logs -f salt_lake_backend`
- 建议接入 ELK 或 CloudWatch 进行日志收集。

### 5.3 安全检查
- 定期运行 `docker scan salt-lake-backend` 检查镜像漏洞。
- 保持服务器系统更新：`apt-get update && apt-get upgrade`。

## 6. 常见问题 (FAQ)
- **Q: 注册失败？**
  - A: 检查数据库 `users` 表是否包含 `preferences` 字段。如无，运行迁移脚本。
- **Q: 502 Bad Gateway?**
  - A: 检查 Docker 容器是否运行 (`docker ps`)，以及 Nginx 配置是否正确指向 8085 端口。
