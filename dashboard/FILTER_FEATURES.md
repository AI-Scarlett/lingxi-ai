# 灵犀 Dashboard 筛选功能更新

**更新日期:** 2026-03-10 10:00  
**版本:** v2.0

---

## ✅ 新增功能

### 1️⃣ 任务类型筛选
- **⏰ 定时任务** - 周期性执行的任务（如每小时汇报、两会监控）
- **⚡ 实时任务** - 用户临时发起的任务

### 2️⃣ 任务来源（渠道）筛选
- 📘 飞书 (feishu)
- 💬 QQ (qqbot)
- 🟢 企业微信 (wecom)
- 🔵 钉钉 (dingtalk)
- 💚 微信 (wechat)

### 3️⃣ 任务进度筛选
- 🔄 进行中 (processing)
- ✅ 已完成 (completed)
- ❌ 失败 (failed)
- ⏳ 等待中 (pending)

### 4️⃣ 时间范围筛选
- **今日** - 当天 0 点至今
- **最近 7 天** - 滚动 7 天
- **最近 30 天** - 滚动 30 天
- **全部时间** - 所有历史数据

### 5️⃣ 定时任务名称筛选
- 支持搜索特定定时任务（如"两会新闻监控"、"每小时汇报"）

---

## 🎯 使用方式

### 网页筛选

访问 Dashboard，使用顶部的筛选栏：

```
http://106.52.101.202:8765/?token=<你的 token>
```

**筛选控件:**
1. 任务类型下拉框
2. 渠道来源下拉框
3. 任务状态下拉框
4. 时间范围下拉框
5. 定时任务名称搜索框

### API 调用

```bash
# 获取所有实时任务
GET /api/tasks?task_type=realtime&token=<token>

# 获取飞书渠道今日任务
GET /api/tasks?channel=feishu&date_range=today&token=<token>

# 获取两会新闻监控的所有执行记录
GET /api/tasks?schedule_name=两会新闻监控&token=<token>

# 组合筛选
GET /api/tasks?task_type=scheduled&channel=feishu&status=completed&date_range=7d&token=<token>
```

---

## 📊 数据库变更

### 新增字段

```sql
ALTER TABLE tasks ADD COLUMN task_type TEXT DEFAULT 'realtime';
ALTER TABLE tasks ADD COLUMN schedule_name TEXT DEFAULT '';
ALTER TABLE tasks ADD COLUMN cron_expr TEXT DEFAULT '';
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_type` | TEXT | `scheduled`=定时任务，`realtime`=实时任务 |
| `schedule_name` | TEXT | 定时任务名称（如"两会新闻监控"） |
| `cron_expr` | TEXT | Cron 表达式（如"0 * * * *"） |

---

## 🔧 技术实现

### 后端 API

**文件:** `dashboard/server.py`

```python
@app.get("/api/tasks")
async def get_tasks(
    token: str = Depends(verify_token),
    limit: int = 50,
    task_type: str = None,      # scheduled/realtime
    channel: str = None,        # feishu/qqbot/...
    status: str = None,         # processing/completed/...
    date_range: str = None,     # today/7d/30d/all
    schedule_name: str = None   # 定时任务名称
):
    ...
```

### 数据库查询

**文件:** `dashboard/database.py`

新增 `get_tasks_v2()` 和 `count_tasks()` 方法，支持多条件组合筛选。

### 前端界面

**文件:** `dashboard/index.html`

- 添加筛选控件栏（filter-bar）
- 修改 `loadTasks()` 函数支持筛选参数
- 自动根据筛选条件刷新任务列表

---

## 📝 任务类型说明

### 定时任务 (scheduled)

通过 cron 调度的周期性任务：

| 任务名称 | Cron 表达式 | 说明 |
|---------|------------|------|
| 灵犀每小时进度汇报 | `0 * * * *` | 每小时整点汇报任务进度 |
| 两会新闻监控 | `0 */4 * * *` | 每 4 小时搜集两会新闻 |

### 实时任务 (realtime)

用户临时发起的任务：

- 飞书消息触发
- QQ 消息触发
- 微信消息触发
- API 直接调用

---

## 🎯 典型使用场景

### 场景 1: 查看今天飞书的所有任务
```
任务类型：全部
渠道：飞书
时间：今日
```

### 场景 2: 查看定时任务执行情况
```
任务类型：定时任务
状态：已完成
时间：最近 7 天
```

### 场景 3: 查看某个定时任务的历史记录
```
定时任务名称：两会新闻监控
时间：最近 30 天
```

### 场景 4: 查看失败任务
```
状态：失败
时间：最近 7 天
```

---

## 🚀 访问地址

**公网访问:**
```
http://106.52.101.202:8765/?token=iOtZIA7A8DX7CJoQ50jMXEqVjZXlAVBo8THgJ1fZ-iY
```

**本地访问:**
```
http://localhost:8765/?token=iOtZIA7A8DX7CJoQ50jMXEqVjZXlAVBo8THgJ1fZ-iY
```

---

## 📋 下一步计划

- [ ] 添加任务导出功能（CSV/Excel）
- [ ] 添加任务统计图表（趋势图、饼图）
- [ ] 支持自定义筛选条件保存
- [ ] 添加任务详情弹窗
- [ ] 支持批量操作（重试、取消）

---

**作者:** 丝嘉丽 Scarlett 💋  
**更新日期:** 2026-03-10
