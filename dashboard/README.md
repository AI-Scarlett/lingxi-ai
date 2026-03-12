# 灵犀 Dashboard v3.3.4

🚀 **现代化 AI 助手数据看板**

---

## ✨ 新特性 (v3.3.4)

### 后端优化
- ✅ **统一数据层** - 使用 SQLite 数据库，完整持久化
- ✅ **WebSocket 实时推送** - 数据变更即时同步到前端
- ✅ **自动同步** - 启动时自动从 OpenClaw 同步历史数据
- ✅ **内存缓存** - 统计数据缓存，减少数据库查询
- ✅ **完整 REST API** - 支持 CRUD 操作
- ✅ **数据导出** - 支持 JSON 格式导出

### 前端重构
- ✅ **Vue 3 + Tailwind CSS** - 现代化技术栈
- ✅ **响应式设计** - 完美适配桌面/平板/手机
- ✅ **暗黑模式** - 支持浅色/深色主题切换
- ✅ **ECharts 图表** - 任务趋势、渠道分布可视化
- ✅ **实时状态指示** - WebSocket 连接状态显示
- ✅ **全局搜索** - 快速查找任务

### 功能增强
- ✅ **任务筛选** - 按状态/渠道/类型筛选
- ✅ **分页加载** - 大量任务不卡顿
- ✅ **任务详情弹窗** - 查看完整信息
- ✅ **手动同步** - 一键同步 OpenClaw 数据
- ✅ **技能动态加载** - 从文件系统扫描技能

---

## 📁 文件结构

```
dashboard/
├── backend/
│   └── main.py          # FastAPI 后端服务
├── frontend/
│   └── index.html       # Vue3 前端页面
├── v3/                  # 旧版本备份
│   ├── server.py
│   ├── index.html
│   ├── database.py
│   └── pages/
├── start.py             # 启动脚本
└── README.md            # 说明文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn aiosqlite
```

### 2. 启动服务

```bash
python start.py
```

或者使用 uvicorn 直接启动：

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8765 --reload
```

### 3. 访问 Dashboard

打开浏览器访问：
```
http://localhost:8765?token=YOUR_TOKEN
```

Token 从 `~/.openclaw/workspace/.lingxi/dashboard_token.txt` 读取。

---

## 🔌 API 接口

### 统计数据
```
GET /api/stats?hours=24
GET /api/stats/trends?days=7
```

### 任务管理
```
GET    /api/tasks?limit=50&offset=0&status=&channel=
POST   /api/tasks
GET    /api/tasks/{task_id}
PUT    /api/tasks/{task_id}
```

### 技能列表
```
GET /api/skills
```

### 数据同步
```
POST /api/sync
```

### WebSocket
```
WS /ws
```

---

## 🎨 界面预览

### 概览页
- 实时统计卡片（今日任务/成功率/Token消耗/成本）
- 任务趋势图表（7天/14天/30天）
- 渠道分布饼图
- 最近任务列表

### 任务管理页
- 完整的任务表格
- 状态/渠道/类型筛选
- 分页加载
- 任务详情弹窗

### 技能中心页
- 动态加载技能列表
- 技能使用统计
- 技能状态显示

### 数据分析页
- Token 消耗分析
- 成本统计
- 性能指标
- 模型使用分布

### 系统设置页
- 主题切换
- 手动数据同步
- 数据导出
- 系统信息

---

## ⚙️ 配置

### 数据路径
默认使用以下路径：
- 数据库: `~/.openclaw/workspace/.lingxi/dashboard_v3.db`
- Token: `~/.openclaw/workspace/.lingxi/dashboard_token.txt`
- Sessions: `~/.openclaw/agents/main/sessions/`
- Skills: `~/.openclaw/workspace/skills/`

### 环境变量
```bash
# 自定义数据目录
export LINGXI_DATA_DIR=/path/to/data

# 自定义 OpenClaw 路径
export OPENCLAW_DIR=/path/to/.openclaw
```

---

## 🔄 从旧版本迁移

### 数据迁移
```bash
# 启动 v3.3.4 时会自动从 OpenClaw sessions 同步数据
python start.py

# 或手动触发同步
curl -X POST "http://localhost:8765/api/sync?token=YOUR_TOKEN"
```

### 配置迁移
- Token 文件位置不变
- 旧版数据库保留在 `v3/` 目录

---

## 🛠️ 开发

### 开发模式启动
```bash
python start.py --dev
```

### 前端开发
前端使用纯 HTML + Vue 3，无需构建步骤。直接编辑 `frontend/index.html` 即可。

---

## 📊 性能优化

- **数据库索引** - 自动创建常用查询索引
- **内存缓存** - 统计数据 30 秒缓存
- **趋势数据** - 5 分钟缓存
- **分页加载** - 避免大数据量查询

---

## 📝 更新日志

### v3.3.4 (2026-03-12)
- 🎉 全面重构，全新架构
- ✨ 新增 WebSocket 实时推送
- ✨ 新增数据可视化图表
- ✨ 新增暗黑模式
- ✨ 新增任务筛选和分页
- ✨ 新增技能动态加载
- 🔧 优化数据库性能
- 🔧 优化前端响应速度

### v3.3.3 (2026-03-11)
- 基础版本

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

**Made with ❤️ by 斯嘉丽 Scarlett**
