# 灵犀 Dashboard

OpenClaw 实时监控面板

## 功能特性

- 📋 任务列表展示（定时任务/实时任务）
- 🔍 任务详情弹窗
- 📊 LLM 调用统计
- 🔧 技能列表
- 🤖 大模型配置
- 🔄 任务重试功能

## 技术栈

- **后端:** FastAPI + SQLite
- **前端:** 原生 HTML + JavaScript
- **部署:** systemd 守护 + uvicorn

## 快速开始

### 安装依赖

```bash
pip install fastapi uvicorn python-multipart
```

### 启动服务

```bash
cd /root/.openclaw/skills/lingxi/dashboard
python3 server.py
```

或使用 uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8765
```

### 访问 Dashboard

- **本地:** http://localhost:8765
- **域名:** http://dashboard.ailoveai.love:8765
- **IP:** http://106.52.101.202:8765

Token 在 `/root/.openclaw/workspace/.lingxi/dashboard_token.txt`

## 项目结构

```
dashboard/
├── server.py      # FastAPI 后端
├── database.py    # 数据库操作
├── index.html     # 前端页面
└── README.md      # 本文档
```

## API 文档

| API | 方法 | 功能 |
|-----|------|------|
| /api/health | GET | 健康检查 |
| /api/tasks | GET | 获取任务列表 |
| /api/tasks/{id} | GET | 获取任务详情 |
| /api/stats | GET | 获取统计数据 |
| /api/skills | GET | 获取技能列表 |

## 系统服务

使用 systemd 管理服务:

```bash
# 查看状态
systemctl status lingxi-dashboard

# 重启服务
systemctl restart lingxi-dashboard

# 查看日志
journalctl -u lingxi-dashboard -f
```

## 许可证

MIT License

## 作者

Scarlett <scarlett@ailoveai.love>
