# Project Template

基于当前仓库技术栈抽出的前后端一体化模板。

包含内容：

- `frontend/`：Vite + React + TypeScript + Tailwind CSS v4 的空白前端
- `backend/`：FastAPI 最小后端，保留 Nacos 配置读取/监听、配置查看与更新、心跳接口、Loguru 日志模块
- `docker-compose.yml`：沿用当前项目的 MySQL + Nacos + MinIO + 后端 + 前端启动结构
- `nacos/`：初始化配置模板与导入脚本

## 本地开发

1. 复制 `.env.example` 为 `.env`
2. 前端启动：`cd frontend && pnpm install && pnpm dev`
3. 后端启动：`cd backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

## Docker 启动

1. 在 `template/` 目录执行 `docker compose up -d`
2. 前端访问 `http://localhost:12345`
3. 后端健康检查 `http://localhost:8000/health`
