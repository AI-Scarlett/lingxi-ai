# 灵犀 AI 助手 - 技术架构文档

> 详细技术说明、架构设计、API 文档和部署指南

## 📋 目录

1. [系统架构](#系统架构)
2. [核心模块](#核心模块)
3. [API 参考](#api 参考)
4. [数据库设计](#数据库设计)
5. [部署指南](#部署指南)
6. [故障排查](#故障排查)

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────┐
│              用户层 (User Layer)                 │
│  飞书 │ 钉钉 │ QQ │ 企业微信 │ WebChat │ Dashboard│
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           OpenClaw Gateway (网关层)              │
│  消息路由 │ 会话管理 │ 技能调度 │ 认证授权       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            灵犀核心层 (Lingxi Core)              │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ MindCore │  TaskMgr │  Skills  │ Layer0-3 │ │
│  │ 记忆管理 │  任务调度 │  技能中心│ 响应规则 │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │  Agent   │ EvoMind  │ Security │ Device   │ │
│  │  积分    │  自改进  │  巡察    │  认证    │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            数据持久层 (Data Layer)               │
│  SQLite │ JSON Files │ Session Files │ Logs    │
└─────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + TailwindCSS | Dashboard 可视化 |
| **后端** | FastAPI (Python) | RESTful API |
| **网关** | OpenClaw | 消息路由和会话管理 |
| **数据库** | SQLite + JSON | 轻量级数据存储 |
| **定时任务** | Cron + Python | 周期性任务调度 |
| **认证** | Token + 设备指纹 | 双重认证机制 |

---

## 核心模块

### 1. MindCore 记忆管理

**文件**: `dashboard/v3/server.py`

**功能**:
- 从 `memory/*.md` 读取每日记忆
- 从 `sessions/*.jsonl` 提取会话记忆
- 记忆分层（STM/MTM/LTM）
- 记忆去重和合并

**API**:
```python
GET /api/memories?page=1&limit=20
GET /api/memory/{memory_id}
POST /api/memory
PUT /api/memory/{memory_id}
DELETE /api/memory/{memory_id}
```

**数据结构**:
```json
{
  "id": "2026-03-14_0001",
  "session_key": "2026-03-14",
  "role": "system",
  "content": "记忆内容",
  "summary": "摘要",
  "kind": "daily_memory",
  "layer": "STM",
  "importance": "medium",
  "created_at": "2026-03-14T13:26:46",
  "dedup_status": "active"
}
```

### 2. Agent 积分系统

**文件**: `core/agent_credit.py`

**等级体系**:
| 等级 | 积分范围 | CPU | GPU | Token/天 | 优先级 |
|------|---------|-----|-----|----------|--------|
| 王牌 | 500+ | 8 核 | 独占 | 100,000 | 1.5x |
| 钻石 | 300-499 | 4 核 | 优先 | 50,000 | 1.3x |
| 金牌 | 200-299 | 2 核 | 正常 | 20,000 | 1.1x |
| 银牌 | 100-199 | 2 核 | 正常 | 10,000 | 1.0x |
| 普通 | 50-99 | 1 核 | 空闲 | 5,000 | 0.8x |
| 观察 | 0-49 | 0.5 核 | 禁止 | 1,000 | 0.5x |
| 隔离 | <0 | 0.5 核 | 禁止 | 500 | 0.0x |

**奖惩规则**:
```python
CREDIT_RULES = {
    # 奖励
    "on_time_task": 5,
    "quality_report": 2,
    "inspection_good": 3,
    "daily_perfect": 5,
    "complex_task": 10,
    "weekly_champion": 50,
    
    # 处罚
    "late_report": -5,
    "invalid_format": -3,
    "task_failed": -10,
    "inspection_issue": -5,
    "resource_waste": -3,
}
```

### 3. 主动巡察系统

**文件**: `scripts/active_inspection.py`

**检查项目**:

#### 服务健康检查
- Dashboard 服务 HTTP 可访问性
- 每小时汇报日志检查
- 定时任务 Cron 状态
- OpenClaw Gateway 运行状态

#### 安全检查
1. **敏感信息泄露**
   - CREDENTIALS.md 权限
   - 硬编码密钥检测
   - 日志文件扫描

2. **外网 IP 暴露**
   - Dashboard 绑定地址
   - 防火墙状态
   - 端口暴露扫描

3. **API 密钥安全**
   - .env 文件权限
   - 明文密钥检测
   - Git 历史扫描

4. **文件权限**
   - 关键文件权限验证
   - 脚本可执行权限

**执行周期**: 每 30 分钟

### 4. EvoMind 自改进

**文件**: `core/evomind.py`

**分析维度**:
- 任务失败原因分析
- 汇报延迟统计
- 资源使用优化建议

**执行周期**: 每 6 小时

**输出**:
- 改进建议（JSON 格式）
- HEARTBEAT.md 自动更新
- Dashboard API 数据源

### 5. 设备认证系统

**文件**: `core/device_auth.py`

**认证流程**:
```
1. 新设备访问 → 注册设备（生成设备 ID）
2. 生成设备指纹（UserAgent + IP + 屏幕）
3. 等待管理员审批
4. 审批通过 → 生成 30 天 Token
5. 后续访问自动认证
```

**API**:
```python
POST /api/device/register      # 注册设备
GET  /api/device/list          # 设备列表（管理员）
POST /api/device/approve       # 审批设备（管理员）
POST /api/device/revoke        # 撤销设备（管理员）
GET  /api/device/stats         # 设备统计（管理员）
```

---

## API 参考

### 基础 API

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | Dashboard 主页 | 公开 |
| GET | `/api/stats` | 统计数据 | Token |
| GET | `/api/analytics` | 数据分析 | Token |

### 记忆管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/memories?page=1&limit=20` | 记忆列表 |
| GET | `/api/memory/{id}` | 记忆详情 |
| POST | `/api/memory` | 创建记忆 |
| PUT | `/api/memory/{id}` | 更新记忆 |
| DELETE | `/api/memory/{id}` | 删除记忆 |

### 任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks?limit=20` | 任务列表 |
| GET | `/api/tasks/{id}` | 任务详情 |
| PUT | `/api/tasks/{id}` | 更新任务 |

### 技能中心

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/skills` | 技能列表 |
| GET | `/api/skills/search?q=xxx` | 技能搜索 |

### Layer0 规则

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/layer0/rules?page=1` | 规则列表 |
| POST | `/api/layer0/rules` | 创建规则 |
| PUT | `/api/layer0/rules/{id}` | 更新规则 |
| DELETE | `/api/layer0/rules/{id}` | 删除规则 |

### Agent 相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions?active=60` | Agent 会话 |
| GET | `/api/agent-credit` | Agent 积分 |
| GET | `/api/core/evomind` | EvoMind 改进 |
| GET | `/api/core/layers` | Layer0-3 配置 |

### 设备认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/device/register` | 注册设备 |
| GET | `/api/device/list` | 设备列表 |
| POST | `/api/device/approve` | 审批设备 |
| POST | `/api/device/revoke` | 撤销设备 |

---

## 数据库设计

### SQLite 表结构

#### tasks 表
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    channel TEXT,
    task_type TEXT,
    status TEXT,
    user_input TEXT,
    summary TEXT,
    created_at TEXT,
    completed_at TEXT
);
```

### JSON 数据文件

#### agent_credit.json
```json
{
  "main": {
    "agent_id": "main",
    "score": 100,
    "level": "普通",
    "total_earned": 0,
    "total_spent": 0,
    "records": [],
    "tasks_completed": 0,
    "perfect_days": 0
  }
}
```

#### evomind_history.json
```json
{
  "improvements": [
    {
      "id": "improvement_1773466006",
      "created_at": "2026-03-14T13:26:46",
      "type": "resource_optimization",
      "description": "优化资源分配",
      "impact": "提升低分 Agent 效率",
      "priority": "low"
    }
  ],
  "total_count": 1,
  "effectiveness": 0.85
}
```

#### devices.json
```json
{
  "dev_xxx": {
    "id": "dev_xxx",
    "name": "测试设备",
    "fingerprint": "abc123...",
    "ip_address": "10.2.0.16",
    "user_agent": "Mozilla/5.0...",
    "status": "approved",
    "created_at": "2026-03-14T14:00:00",
    "last_access": "2026-03-14T14:20:00",
    "access_count": 5
  }
}
```

---

## 部署指南

### 1. 服务器要求

- **CPU**: 2 核+
- **内存**: 4GB+
- **存储**: 20GB+
- **系统**: Ubuntu 20.04+ / Debian 11+

### 2. 安装步骤

```bash
# 克隆项目
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai

# 安装 Python 依赖
pip3 install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env  # 填写 API 密钥

# 启动 Dashboard
cd dashboard/v3
nohup python3 server.py > /tmp/dashboard.log 2>&1 &

# 配置定时任务
crontab -e
# 添加 HEARTBEAT.md 中的定时任务
```

### 3. 安全配置

#### 防火墙配置
```bash
# 启用防火墙
ufw enable

# 只允许信任 IP 访问 Dashboard
ufw allow from 信任 IP to any port 8765
ufw deny 8765

# 开放 SSH
ufw allow 22
```

#### Dashboard 绑定限制
```python
# 修改 dashboard/v3/server.py 启动参数
uvicorn server:app --host 127.0.0.1 --port 8765
```

#### 文件权限
```bash
chmod 600 CREDENTIALS.md
chmod 600 .env
chmod +x scripts/*.py
```

---

## 故障排查

### Dashboard 无法访问

```bash
# 检查服务状态
ps aux | grep server.py

# 查看日志
tail -f /tmp/dashboard.log

# 检查端口
ss -tlnp | grep 8765
```

### 定时任务未执行

```bash
# 检查 cron 状态
systemctl status cron

# 查看 cron 日志
grep CRON /var/log/syslog | tail -20

# 手动执行测试
python3 scripts/active_inspection.py
```

### Agent 积分异常

```bash
# 查看积分数据
cat data/agent_credit.json

# 手动重置
python3 core/agent_credit.py add main 100 "手动重置"
```

### 设备认证失败

```bash
# 查看设备列表
python3 core/device_auth.py list

# 清除设备数据
rm data/devices.json

# 重启 Dashboard
pkill -f server.py
python3 dashboard/v3/server.py &
```

---

## 性能优化

### 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created ON tasks(created_at);
```

### 缓存策略
- 记忆数据：5 分钟缓存
- 统计数据：1 分钟缓存
- 设备认证：30 天 Token

### 并发控制
- SQLite: WAL 模式
- 文件锁：flock
- API 限流：100 请求/分钟

---

**最后更新**: 2026-03-14  
**版本**: v3.3.6
