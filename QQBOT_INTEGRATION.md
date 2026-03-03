# 灵犀 - QQ Bot 集成指南

> **方案 A：自动异步处理** ✨

## 🎯 集成效果

集成后，QQ Bot 自动支持多任务并行处理：

### 用户体验

```
用户：北京明天天气怎么样
灵犀：北京明天晴，25°C ☀️（立即响应）

用户：帮我发布公众号文章，主题是 AI 发展
灵犀：好的老板，正在后台发布，完成后 QQ 通知你～ 💋
      （后台执行，不阻塞）

用户：搜索最新的 AI 新闻
灵犀：[立即搜索并回复]（不等待文章发布）

[2 分钟后]
灵犀：（主动 QQ）老板，文章发布成功啦！链接：xxx 💋
```

---

## 📁 新增文件

```
lingxi/scripts/
├── lingxi_qqbot.py          # QQ Bot 集成入口 ⭐
└── QQBOT_INTEGRATION.md     # 本文件
```

---

## 🔧 使用方式

### 方式 1：直接导入调用

```python
from lingxi_qqbot import handle_qq_message

# QQ Bot 收到消息时调用
async def on_qq_message(user_id, message):
    reply = await handle_qq_message(user_id, message)
    await send_reply(user_id, reply)
```

### 方式 2：作为 HTTP 服务

```python
# server.py
from fastapi import FastAPI
from lingxi_qqbot import handle_qq_message

app = FastAPI()

@app.post("/qqbot/message")
async def qqbot_webhook(data: dict):
    user_id = data['user_id']
    message = data['message']
    
    reply = await handle_qq_message(user_id, message)
    return {"reply": reply}
```

---

## 📋 API 参考

### handle_qq_message

处理 QQ 消息的主函数

```python
reply = await handle_qq_message(
    user_id="7941E72A6252ADA08CC281AC26D9920B",  # 用户 ID
    message="帮我发布公众号文章",                  # 消息内容
    channel="qqbot"                               # 渠道
)
```

**返回值：**
- 即时任务：完整回复内容
- 耗时任务：接收确认消息（后台执行）

---

### query_task_status

查询任务状态

```python
# 查询所有任务
status = await query_task_status(user_id)

# 查询指定任务
status = await query_task_status(user_id, task_id="task_xxx")
```

---

### cancel_task

取消任务

```python
result = await cancel_task(user_id, task_id="task_xxx")
```

---

## ⚙️ 自动任务分类

系统根据关键词自动判断任务类型：

### 耗时任务（后台执行）

| 关键词 | 示例 |
|--------|------|
| 发布 | "发布公众号文章" |
| 公众号 | "发到微信公众号" |
| 微信 | "微信推送" |
| 小红书 | "发小红书" |
| 微博 | "发微博" |
| 抖音 | "发抖音" |
| 生成图片 | "生成一张图片" |
| 自拍 | "发张自拍" |
| 处理文件 | "处理这个 Excel" |
| 分析数据 | "分析销售数据" |
| 导出 | "导出为 PDF" |
| 转换 | "转换为 Markdown" |
| 上传 | "上传到云盘" |
| 下载 | "下载这个文件" |

### 即时任务（立即响应）

| 关键词 | 示例 |
|--------|------|
| 天气 | "北京天气怎么样" |
| 搜索 | "搜索 AI 新闻" |
| 翻译 | "翻译成英文" |
| 是什么 | "AI 是什么" |
| 为什么 | "为什么天空是蓝的" |
| 怎么 | "怎么用 Python" |
| 你好 | "你好" |
| 在吗 | "在吗" |
| 帮助 | "帮助" |

---

## 🎛️ 配置选项

在 `lingxi_qqbot.py` 中修改配置：

```python
# 是否启用异步处理（默认启用）
ENABLE_ASYNC = True

# 耗时任务关键词（自动后台执行）
LONG_RUNNING_KEYWORDS = [
    "发布", "公众号", "微信", "小红书",
    # ... 添加更多关键词
]

# 即时任务关键词（立即响应）
INSTANT_KEYWORDS = [
    "天气", "搜索", "翻译",
    # ... 添加更多关键词
]
```

---

## 🧪 测试

### 命令行测试

```bash
cd ~/.openclaw/skills/lingxi/scripts
python3 lingxi_qqbot.py
```

### Python 测试

```python
from lingxi_qqbot import handle_qq_message, query_task_status

async def test():
    # 测试即时任务
    reply = await handle_qq_message("user_123", "北京天气怎么样")
    print(f"回复：{reply}")
    
    # 测试耗时任务
    reply = await handle_qq_message("user_123", "发布公众号文章")
    print(f"回复：{reply}")
    
    # 查询任务
    status = await query_task_status("user_123")
    print(f"任务状态：{status}")
```

---

## 📊 完整流程示例

### 示例 1：公众号发布

```python
# 用户发送
"帮我发布公众号文章，主题是 AI 发展趋势"

# 系统处理
1. 识别关键词"发布"、"公众号" → 耗时任务
2. 后台启动任务
3. 立即回复："好的老板，正在后台发布..."
4. 后台执行发布命令
5. 完成后主动 QQ 通知

# 用户收到
立即回复："好的老板，任务已接收～ 💋
          📋 帮我发布公众号文章，主题是 AI 发展趋势...
          ⚙️ 正在后台处理中，完成后我马上 QQ 通知你！
          任务 ID: `task_xxx`"

[2 分钟后]
主动通知："老板，文章发布成功啦！💋
          📝 任务：帮我发布公众号文章，主题是 AI 发展趋势
          🔗 链接：https://mp.weixin.qq.com/s/xxx
          快去看看吧～ ✨"
```

---

### 示例 2：多任务并行

```python
# 用户连续发送
1. "发布公众号文章，主题是 AI"
2. "北京明天天气怎么样"
3. "搜索最新的 AI 新闻"

# 系统处理
任务 1: 后台执行（不阻塞）
任务 2: 立即响应
任务 3: 立即响应

# 用户收到
回复 1: "好的老板，正在后台发布..."
回复 2: "北京明天晴，25°C ☀️"
回复 3: "[搜索结果]..."

[2 分钟后]
主动通知："老板，文章发布成功啦！..."
```

---

## 🔍 故障排查

### 问题 1：任务不执行

**检查：**
```bash
# 查看任务状态文件
cat ~/.openclaw/workspace/task-state.json

# 查看任务管理器
python3 -c "from task_manager import get_task_manager; m = get_task_manager(); print(m.get_all())"
```

### 问题 2：通知不发送

**检查：**
- 确认 `notify_on_complete=True`
- 检查 OpenClaw cron 是否正常
- 查看日志：`openclaw logs`

### 问题 3：任务分类错误

**解决：**
修改 `lingxi_qqbot.py` 中的关键词列表：

```python
LONG_RUNNING_KEYWORDS = [
    # 添加你的关键词
    "你的关键词",
]
```

---

## 🚀 高级用法

### 1. 自定义任务类型

```python
from async_executor import get_executor

executor = get_executor()

# 执行自定义任务
task_id = await executor.execute(
    task_type="custom-task",
    description="自定义任务描述",
    command="your-command here",
    user_id=user_id,
    channel="qqbot",
    notify_on_complete=True
)
```

### 2. 任务优先级

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

### 3. 静默任务（不通知）

```python
task_id = await executor.execute(
    task_type="silent-task",
    description="静默任务",
    command="...",
    user_id=user_id,
    notify_on_complete=False  # 不发送通知
)
```

---

## 📈 监控与统计

### 查看任务统计

```python
from task_manager import get_task_manager

manager = get_task_manager()

# 所有任务
all_tasks = manager.get_all()
print(f"总任务数：{len(all_tasks)}")

# 按状态统计
completed = len(manager.get_all(TaskStatus.COMPLETED))
running = len(manager.get_all(TaskStatus.RUNNING))
failed = len(manager.get_all(TaskStatus.FAILED))

print(f"完成：{completed}, 运行中：{running}, 失败：{failed}")
```

### 清理过期任务

```python
# 清理 24 小时前的已完成任务
count = manager.cleanup_completed(max_age_hours=24)
print(f"清理了 {count} 个任务")
```

---

## 💡 最佳实践

1. **合理设置关键词** - 根据实际业务调整耗时/即时任务分类
2. **定期清理状态** - 避免状态文件过大
3. **监控任务失败** - 设置告警机制
4. **限制并发数** - 避免资源耗尽（建议最多 10 个并发）
5. **测试通知流程** - 确保 QQ 通知正常发送

---

## 🎉 集成完成！

现在你的 QQ Bot 已经支持：

✅ 多任务并行处理  
✅ 耗时任务后台执行  
✅ 完成后主动通知  
✅ 智能任务分类  
✅ 任务状态查询  

**开始使用吧，老板！** 💋

---

**灵犀团队** | 心有灵犀，一点就通 ✨
