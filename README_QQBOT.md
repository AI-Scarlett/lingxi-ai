# 灵犀异步任务系统 - QQ Bot 快速集成

> **5 分钟让你的 QQ Bot 支持多任务并行！** 💋

---

## 🚀 快速开始

### 1. 测试功能

```bash
cd ~/.openclaw/skills/lingxi/scripts

# 测试即时任务
python3 qqbot_bridge.py --user-id "你的 QQ openid" --message "北京天气怎么样"

# 测试耗时任务
python3 qqbot_bridge.py --user-id "你的 QQ openid" --message "发布公众号文章"
```

### 2. 集成到 QQ Bot

在 QQ Bot Gateway 的消息处理函数中调用桥接器：

```typescript
// gateway.ts 或消息处理文件
import { exec } from 'child_process';
import { promisify } from 'util';
const execAsync = promisify(exec);

async function handleMessage(user_id: string, message: string) {
  // 调用灵犀桥接器
  const { stdout } = await execAsync(
    `python3 ~/.openclaw/skills/lingxi/scripts/qqbot_bridge.py ` +
    `--user-id "${user_id}" ` +
    `--message "${message.replace(/"/g, '\\"')}" ` +
    `--json`
  );
  
  const result = JSON.parse(stdout);
  
  if (result.success) {
    // 发送回复给用户
    await sendText(user_id, result.reply);
  } else {
    await sendText(user_id, `抱歉，出错了：${result.error}`);
  }
}
```

### 3. 完成！

现在你的 QQ Bot 自动支持：
- ✅ 即时任务立即响应
- ✅ 耗时任务后台执行
- ✅ 多任务并行处理
- ✅ 完成后主动通知

---

## 📊 效果对比

### 之前（串行）

```
用户：发布公众号文章
灵犀：[执行 3 分钟...] 完成！
用户：（等待中无法发新消息）
用户：查天气
灵犀：[排队等待...] 北京晴
```

### 现在（并行）

```
用户：发布公众号文章
灵犀：好的老板，正在后台发布，完成后通知你～ 💋
用户：（立即可以发新消息）
用户：查天气
灵犀：北京晴，25°C ☀️
[2 分钟后]
灵犀：（主动通知）老板，文章发布成功啦！
```

---

## 🎯 自动任务分类

### 耗时任务（后台执行）

发布、公众号、微信、小红书、微博、抖音、生成图片、自拍、处理文件、分析数据、导出、转换、上传、下载

### 即时任务（立即响应）

天气、搜索、翻译、是什么、为什么、怎么、你好、在吗、帮助

---

## 📁 核心文件

| 文件 | 功能 |
|------|------|
| `scripts/lingxi_qqbot.py` | QQ Bot 集成入口 |
| `scripts/qqbot_bridge.py` | 桥接器（供 Gateway 调用） |
| `scripts/qqbot-bridge.sh` | Shell 包装器 |
| `scripts/task_manager.py` | 任务管理器 |
| `scripts/async_executor.py` | 异步执行器 |

---

## 🔧 配置

### 修改任务分类关键词

编辑 `scripts/lingxi_qqbot.py`：

```python
LONG_RUNNING_KEYWORDS = [
    "发布", "公众号", "微信",
    # 添加你的关键词
]
```

### 启用/禁用异步

```python
ENABLE_ASYNC = True  # False 禁用异步
```

---

## 📚 详细文档

- **INTEGRATION_COMPLETE.md** - 完整集成文档
- **QQBOT_INTEGRATION.md** - 集成指南
- **ASYNC_GUIDE.md** - 技术详解
- **scripts/demo.py** - 示例代码

---

## 🐛 故障排查

### 测试桥接器

```bash
python3 qqbot_bridge.py --user-id "xxx" --message "测试" 2>&1
```

### 查看任务状态

```bash
cat ~/.openclaw/workspace/task-state.json
```

### 清理过期任务

```python
python3 -c "from task_manager import get_task_manager; get_task_manager().cleanup_completed(24)"
```

---

## 💋 有问题？

随时找老板反馈！💋

**灵犀团队** | 心有灵犀，一点就通 ✨
