# 灵犀异步任务处理指南

> **多任务并行，后台不阻塞** ✨

## 🎯 核心能力

灵犀现在支持**多任务并行处理**，耗时任务在后台执行，不阻塞主对话！

### 之前 vs 现在

**之前（串行）：**
```
用户：发布公众号文章
灵犀：[执行 3 分钟...] 完成！
用户：（等待中无法插队）
用户：查天气
灵犀：[排队等待...] 北京晴，25°C
```

**现在（并行）：**
```
用户：发布公众号文章
灵犀：好的老板，正在后台发布，完成后 QQ 通知你～ 💋
用户：（立即可以发新指令）
用户：查天气
灵犀：北京晴，25°C ☀️
[2 分钟后]
灵犀：（主动 QQ）老板，文章发布成功啦！链接：xxx
```

---

## 📁 新增文件

```
lingxi/scripts/
├── task_manager.py          # 任务状态管理器
├── async_executor.py        # 异步任务执行器
├── orchestrator_async.py    # 异步编排器
└── ASYNC_GUIDE.md          # 本文件
```

---

## 🔧 核心组件

### 1️⃣ 任务管理器 (task_manager.py)

**功能：**
- 任务注册、更新、查询
- 状态持久化到 `~/.openclaw/workspace/task-state.json`
- 支持多任务并发追踪
- 线程安全

**使用示例：**
```python
from task_manager import get_task_manager, TaskInfo, TaskStatus, generate_task_id

# 获取管理器
manager = get_task_manager()

# 创建任务
task = TaskInfo(
    id=generate_task_id(),
    type="wechat-publish",
    description="发布公众号文章",
    user_id="7941E72A6252ADA08CC281AC26D9920B"
)

# 注册任务
manager.register(task)

# 更新状态
manager.update(task.id, status=TaskStatus.RUNNING)

# 查询任务
task = manager.get(task.id)
print(f"状态：{task.status.value}")

# 获取所有运行中的任务
running = manager.get_running()
```

---

### 2️⃣ 异步执行器 (async_executor.py)

**功能：**
- 后台执行耗时任务
- 完成后主动 QQ 通知用户
- 支持多任务并行

**使用示例：**
```python
from async_executor import get_executor

executor = get_executor()

# 执行后台任务
task_id = await executor.execute(
    task_type="wechat-publish",
    description="发布 AI 发展趋势文章",
    command="wenyan publish article.md --theme lapis",
    user_id="7941E72A6252ADA08CC281AC26D9920B",
    channel="qqbot",
    notify_on_complete=True
)

print(f"任务已启动：{task_id}")

# 查询状态
status = executor.get_task_status(task_id)
print(f"状态：{status['status']}")
```

---

### 3️⃣ 异步编排器 (orchestrator_async.py)

**功能：**
- 智能判断任务类型（即时 vs 耗时）
- 耗时任务自动后台执行
- 即时任务立即响应

**使用示例：**
```python
from orchestrator_async import get_async_orchestrator

orch = get_async_orchestrator()

# 耗时任务（自动后台执行）
reply = await orch.execute_async(
    user_input="帮我发布公众号文章，主题是 AI 发展",
    user_id="7941E72A6252ADA08CC281AC26D9920B",
    channel="qqbot",
    is_background=True  # 后台执行
)
# 立即返回："好的老板，正在后台处理..."

# 即时任务（立即响应）
reply = await orch.execute_async(
    user_input="北京明天天气怎么样",
    user_id="7941E72A6252ADA08CC281AC26D9920B",
    channel="qqbot",
    is_background=False  # 即时执行
)
# 立即返回天气信息
```

---

## 📋 任务类型

### 自动识别的耗时任务

| 任务类型 | 识别关键词 | 执行方式 |
|---------|-----------|---------|
| 微信公众号发布 | "公众号"、"微信"、"发布" | 后台异步 |
| 小红书发布 | "小红书"、"发布" | 后台异步 |
| 图片生成 | "图片"、"自拍"、"生成图" | 后台异步 |
| 微博发布 | "微博"、"发布" | 后台异步 |
| 抖音发布 | "抖音"、"发布" | 后台异步 |

### 即时任务

| 任务类型 | 识别关键词 | 执行方式 |
|---------|-----------|---------|
| 天气查询 | "天气" | 即时响应 |
| 搜索 | "搜索"、"查找" | 即时响应 |
| 翻译 | "翻译" | 即时响应 |
| 问答 | 一般问题 | 即时响应 |

---

## 🔄 完整流程示例

### 场景：发布公众号文章 + 查天气

```python
from orchestrator_async import get_async_orchestrator

orch = get_async_orchestrator()
user_id = "7941E72A6252ADA08CC281AC26D9920B"

# 用户指令 1: 发布文章（耗时）
reply1 = await orch.execute_async(
    user_input="帮我发布公众号文章，主题是 AI 发展趋势",
    user_id=user_id,
    channel="qqbot",
    is_background=True
)
# 立即回复："好的老板，正在后台发布..."

# 用户指令 2: 查天气（即时，不等待文章发布）
reply2 = await orch.execute_async(
    user_input="北京明天天气怎么样",
    user_id=user_id,
    channel="qqbot",
    is_background=False
)
# 立即回复："北京明天晴，25°C ☀️"

# 用户指令 3: 查询任务状态
status = await orch.check_task_status(task_id)
# 返回：{"status": "running", ...}

# [2 分钟后，文章发布完成]
# 灵犀自动 QQ 通知："老板，文章发布成功啦！链接：xxx 💋"
```

---

## 💡 高级用法

### 1. 任务优先级

```python
# 高优先级任务（插队）
task_id = await executor.execute(
    task_type="urgent-task",
    description="紧急任务",
    command="...",
    user_id=user_id,
    priority=10  # 数字越大优先级越高
)
```

### 2. 取消任务

```python
# 取消未完成的任务
success = await orch.cancel_task(task_id)
if success:
    print("任务已取消")
```

### 3. 列出所有任务

```python
# 列出所有运行中的任务
running = await orch.list_tasks(status=TaskStatus.RUNNING)
for task in running:
    print(f"{task['id']}: {task['description']}")

# 列出最近 10 个任务
all_tasks = await orch.list_tasks(limit=10)
```

### 4. 自定义通知消息

```python
# 在 async_executor.py 中修改 _send_completion_notification()
# 根据不同任务类型自定义通知内容
```

---

## 🧩 集成到 QQ Bot

### 在 QQ Bot 中调用

```python
# qqbot_handler.py
from orchestrator_async import get_async_orchestrator

async def handle_qq_message(user_id: str, message: str):
    orch = get_async_orchestrator()
    
    # 判断是否为耗时任务
    if is_long_running(message):
        # 后台执行
        reply = await orch.execute_async(
            user_input=message,
            user_id=user_id,
            channel="qqbot",
            is_background=True
        )
    else:
        # 即时执行
        reply = await orch.execute_async(
            user_input=message,
            user_id=user_id,
            channel="qqbot",
            is_background=False
        )
    
    # 发送回复
    await send_qq_message(user_id, reply)
```

---

## 📊 状态文件

任务状态持久化在 `~/.openclaw/workspace/task-state.json`：

```json
{
  "tasks": {
    "task_20260302232000_abc123": {
      "id": "task_20260302232000_abc123",
      "type": "wechat-publish",
      "description": "发布公众号文章",
      "status": "completed",
      "created_at": 1772505600000,
      "started_at": 1772505601000,
      "completed_at": 1772505720000,
      "result": {
        "success": true,
        "url": "https://mp.weixin.qq.com/s/xxx"
      },
      "user_id": "7941E72A6252ADA08CC281AC26D9920B",
      "channel": "qqbot"
    }
  },
  "last_updated": "2026-03-02T23:22:00"
}
```

---

## ⚠️ 注意事项

1. **状态文件清理** - 定期清理已完成的任务，避免文件过大
   ```python
   manager.cleanup_completed(max_age_hours=24)
   ```

2. **并发限制** - 建议限制同时运行的任务数量（如最多 5 个）

3. **错误处理** - 任务失败时会主动通知用户，包含错误信息

4. **通知频率** - 避免短时间内发送大量通知消息

---

## 🚀 下一步优化

- [ ] 任务优先级队列
- [ ] 任务依赖关系（任务 B 依赖任务 A 完成）
- [ ] 任务进度实时推送（如：发布进度 50%...）
- [ ] 任务重试机制
- [ ] 任务历史记录查询接口
- [ ] Web UI 管理面板

---

## 💬 联系

有问题随时找老板反馈～ 💋

**灵犀团队** | 心有灵犀，一点就通 ✨
