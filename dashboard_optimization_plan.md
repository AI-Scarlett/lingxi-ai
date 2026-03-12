# 灵犀 Dashboard 优化方案

**分析日期**: 2026-03-12  
**当前版本**: v3.3.3  
**目标版本**: v4.0

---

## 一、当前问题诊断

### 1.1 架构层面的问题

| 问题 | 严重程度 | 描述 |
|------|----------|------|
| **数据孤岛** | 🔴 高 | `server.py` 只读取 HEARTBEAT.md，而 `database.py` 定义了完整的数据库模型但未被使用 |
| **前后端割裂** | 🔴 高 | 前端展示的数据与后端数据库模型不匹配 |
| **硬编码路径** | 🟡 中 | `/root/.openclaw` 路径硬编码，无法适配不同环境 |
| **无数据持久化** | 🔴 高 | 任务数据只从 HEARTBEAT.md 解析，无法记录历史 |

### 1.2 功能缺失

| 功能 | 当前状态 | 影响 |
|------|----------|------|
| WebSocket 实时推送 | ❌ 缺失 | 页面需要手动刷新才能看到新数据 |
| 数据筛选/搜索 | ❌ 缺失 | 无法按时间、状态、渠道筛选任务 |
| 分页功能 | ❌ 缺失 | 任务多时页面卡顿 |
| 图表可视化 | ❌ 缺失 | 纯数字展示，趋势不明显 |
| 导出功能 | ❌ 缺失 | 无法导出报表 |

### 1.3 性能问题

| 问题 | 描述 |
|------|------|
| 全文件读取 | 每次请求都读取整个 HEARTBEAT.md |
| 无缓存机制 | 相同查询重复计算 |
| 前端渲染阻塞 | 大量 DOM 操作无虚拟列表优化 |

### 1.4 用户体验问题

| 问题 | 描述 |
|------|------|
| 技能列表写死 | 18个技能是前端写死的，非动态获取 |
| 统计数据静态 | 记忆数/调用数显示为 "-" 或固定值 |
| 设置页面无效 | 保存配置按钮无实际功能 |

---

## 二、优化方案

### 2.1 架构重构

```
┌─────────────────────────────────────────────────────────────────┐
│                     优化后的 Dashboard 架构                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    WebSocket     ┌──────────────────────┐   │
│  │   前端 UI    │ ◄──────────────► │   FastAPI 后端       │   │
│  │  (Vue3/React)│                   │   - REST API         │   │
│  └──────────────┘                   │   - WebSocket        │   │
│         │                           │   - 缓存层(Redis)    │   │
│         │ HTTP                      └──────────┬───────────┘   │
│         ▼                                      │               │
│  ┌──────────────┐                              │               │
│  │   Nginx      │    ┌─────────────────────────┘               │
│  │  (静态资源)  │    │                                         │
│  └──────────────┘    ▼                                         │
│                 ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│                 │ SQLite  │    │ 文件    │    │ OpenClaw│     │
│                 │ (主数据)│    │ 监控    │    │ Sessions│     │
│                 └─────────┘    └─────────┘    └─────────┘     │
│                                                      │          │
│                                                 ┌────┴────┐     │
│                                                 │ 数据同步 │     │
│                                                 │ 服务     │     │
│                                                 └─────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 后端优化 (server.py)

#### 2.2.1 统一数据层

```python
# 建议使用 database.py 中定义的完整模型
# 重写 server.py 使用 DashboardDatabase 类

from database import DashboardDatabase, TaskRecord, TaskStatus

# 初始化数据库
db = DashboardDatabase()

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.close()
```

#### 2.2.2 新增 API 端点

| 端点 | 功能 | 优先级 |
|------|------|--------|
| `GET /api/tasks` | 使用数据库查询，支持筛选 | P0 |
| `POST /api/tasks` | 创建任务记录 | P0 |
| `PUT /api/tasks/{id}` | 更新任务状态 | P0 |
| `GET /api/tasks/{id}` | 获取任务详情 | P0 |
| `DELETE /api/tasks/{id}` | 删除任务 | P1 |
| `GET /api/stats` | 统计数据（带缓存） | P0 |
| `GET /api/stats/trends` | 趋势数据（7天/30天） | P1 |
| `GET /api/skills` | 动态扫描技能目录 | P1 |
| `GET /api/channels` | 渠道统计 | P1 |
| `GET /api/export` | 导出数据（CSV/JSON） | P2 |
| `WS /ws` | WebSocket 实时推送 | P1 |

#### 2.2.3 数据同步服务

```python
# 新增文件监控，自动同步 OpenClaw 数据到 Dashboard DB

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SessionFileHandler(FileSystemEventHandler):
    """监控 OpenClaw session 文件变化"""
    
    def on_modified(self, event):
        if event.src_path.endswith('.jsonl'):
            # 解析新消息，同步到数据库
            sync_session_to_db(event.src_path)

# 启动监控
observer = Observer()
observer.schedule(SessionFileHandler(), 
                  path="/root/.openclaw/agents/main/sessions")
observer.start()
```

### 2.3 前端优化 (index.html)

#### 2.3.1 技术栈升级建议

**方案 A: 轻量级改进 (保持单文件)**
- 使用 Alpine.js 替代原生 JS
- 引入 Chart.js 做数据可视化
- 使用 Tailwind CSS 优化样式

**方案 B: 现代化重构 (推荐)**
- Vue 3 + TypeScript
- Element Plus / Ant Design Vue
- ECharts 图表库
- Vite 构建工具

#### 2.3.2 页面结构优化

```
Dashboard/
├── 📊 概览页 (Overview)
│   ├── 实时数据卡片
│   ├── 趋势图表 (24h/7d/30d)
│   └── 渠道分布饼图
│
├── ✅ 任务管理 (Tasks)
│   ├── 任务列表 (支持筛选/排序/分页)
│   ├── 任务详情抽屉
│   └── 批量操作
│
├── 🧠 记忆管理 (Memories)
│   ├── 记忆列表
│   ├── 搜索功能
│   └── 记忆统计
│
├── 🎯 技能中心 (Skills)
│   ├── 技能列表 (动态加载)
│   ├── 技能使用统计
│   └── 技能配置
│
├── 📈 数据分析 (Analytics)
│   ├── LLM 调用分析
│   ├── Token 消耗趋势
│   ├── 成本统计
│   └── 性能指标
│
├── 📝 日志中心 (Logs)
│   ├── 调用日志
│   ├── 错误日志
│   └── 系统日志
│
└── ⚙️ 系统设置 (Settings)
    ├── 通用配置
    ├── 通知设置
    └── 数据管理
```

### 2.4 数据库优化

#### 2.4.1 表结构完善

```sql
-- 新增索引
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_status_created ON tasks(status, created_at);
CREATE INDEX idx_tasks_channel_created ON tasks(channel, created_at);
CREATE INDEX idx_tasks_schedule_name ON tasks(schedule_name);

-- 新增表：操作日志
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    operation TEXT,
    details TEXT,
    created_at REAL NOT NULL
);

-- 新增表：系统配置
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at REAL
);
```

#### 2.4.2 数据归档策略

```python
# 自动归档旧数据
async def archive_old_data():
    """归档 30 天前的数据"""
    cutoff = time.time() - 30 * 24 * 3600
    
    # 移动到归档表
    await db.execute('''
        INSERT INTO tasks_archive 
        SELECT * FROM tasks WHERE created_at < ?
    ''', (cutoff,))
    
    # 删除原表数据
    await db.execute('DELETE FROM tasks WHERE created_at < ?', (cutoff,))
```

### 2.5 缓存策略

```python
# 使用内存缓存 + Redis
from functools import lru_cache
import aioredis

redis = aioredis.from_url("redis://localhost")

async def get_cached_stats(hours: int = 24):
    cache_key = f"stats:{hours}"
    
    # 先查 Redis
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 查数据库
    stats = await db.get_stats(hours)
    
    # 写入缓存（5分钟过期）
    await redis.setex(cache_key, 300, json.dumps(stats))
    
    return stats
```

---

## 三、实施计划

### 阶段一：基础修复 (1-2天)

- [ ] 修复 `server.py` 使用 `database.py` 模型
- [ ] 实现 `POST /api/tasks` 数据写入
- [ ] 修复前端技能列表动态加载
- [ ] 修复统计数据实时显示

### 阶段二：功能完善 (3-5天)

- [ ] 实现 WebSocket 实时推送
- [ ] 添加任务筛选/搜索功能
- [ ] 实现分页功能
- [ ] 添加数据导出功能

### 阶段三：体验优化 (2-3天)

- [ ] 添加图表可视化 (ECharts)
- [ ] 优化移动端适配
- [ ] 添加暗黑模式
- [ ] 实现数据自动刷新

### 阶段四：性能优化 (2-3天)

- [ ] 实现 Redis 缓存
- [ ] 添加数据归档机制
- [ ] 优化大数据量查询
- [ ] 添加性能监控

---

## 四、代码示例

### 4.1 优化后的 server.py 核心代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 服务器 - v4.0 (优化版)
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import Optional, List
import json
import asyncio

from database import DashboardDatabase, TaskRecord, TaskStatus

app = FastAPI(title="灵犀 Dashboard v4.0")
db = DashboardDatabase()

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for conn in self.active_connections:
            await conn.send_json(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.get("/api/tasks")
async def get_tasks(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    date_range: Optional[str] = None,
    search: Optional[str] = None
):
    """获取任务列表 - 使用数据库查询"""
    tasks = await db.get_tasks_v2(
        limit=limit,
        offset=offset,
        status=status,
        channel=channel,
        time_filter=date_range
    )
    
    # 搜索过滤
    if search:
        tasks = [t for t in tasks if search.lower() in t.user_input.lower()]
    
    return {
        "tasks": [t.to_dict() for t in tasks],
        "total": await db.count_tasks(status=status, channel=channel),
        "limit": limit,
        "offset": offset
    }

@app.post("/api/tasks")
async def create_task(task: TaskRecord):
    """创建任务记录"""
    await db.insert_task(task)
    
    # WebSocket 广播
    await manager.broadcast({
        "type": "task_created",
        "data": task.to_dict()
    })
    
    return {"success": True, "id": task.id}

@app.get("/api/stats")
async def get_stats(hours: int = 24):
    """获取统计数据 - 带缓存"""
    stats = await get_cached_stats(hours)
    return stats

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 实时连接"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息
    except:
        manager.disconnect(websocket)
```

### 4.2 优化后的前端核心代码

```javascript
// 使用 Vue 3 + Composition API
const { createApp, ref, onMounted, onUnmounted } = Vue;

const app = createApp({
    setup() {
        const tasks = ref([]);
        const stats = ref({});
        const ws = ref(null);
        
        // WebSocket 连接
        const connectWebSocket = () => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws.value = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.value.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'task_created') {
                    tasks.value.unshift(data.data);
                }
            };
        };
        
        // 加载任务列表
        const loadTasks = async (params = {}) => {
            const query = new URLSearchParams(params);
            const res = await fetch(`/api/tasks?${query}`);
            const data = await res.json();
            tasks.value = data.tasks;
        };
        
        onMounted(() => {
            loadTasks();
            connectWebSocket();
        });
        
        onUnmounted(() => {
            ws.value?.close();
        });
        
        return { tasks, stats, loadTasks };
    }
});

app.mount('#app');
```

---

## 五、预期效果

| 指标 | 当前 | 优化后 |
|------|------|--------|
| 数据实时性 | 手动刷新 | WebSocket 实时推送 |
| 页面加载时间 | 2-3s | <1s (带缓存) |
| 任务查询速度 | 全文件扫描 | 数据库索引查询 (<100ms) |
| 数据保留 | 无持久化 | 完整历史记录 |
| 用户体验 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

**需要我立即开始实施优化吗？** 我可以：
1. 直接重写优化版的 `server.py`
2. 创建新的 Vue3 前端项目
3. 先做一个最小可用版本（修复当前最严重的问题）

请告诉我您的偏好！