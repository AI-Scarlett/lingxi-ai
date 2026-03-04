# 🔄 灵犀对话管理器 - 使用指南 (v2.8.1)

**版本:** v2.8.1  
**日期:** 2026-03-04  
**核心功能:** 自动续对话 + 记忆继承

---

## 🎯 核心功能

1. **📊 对话长度监控** - 超过阈值自动提醒
2. **🔄 一键续对话** - 保留所有记忆
3. **🧠 记忆继承** - 偏好/关系/知识全部带走
4. **⚡ 无缝切换** - 用户无感知

---

## 🚀 快速开始

### 基础使用

```python
from conversation_manager import ConversationManager

# 初始化
manager = ConversationManager()

# 创建对话
conv = manager.create_conversation("user_123")
print(f"对话 ID: {conv.id}")

# 添加消息（自动计数）
result = manager.add_message("user_123", conv.id, tokens=200)
print(f"消息数：{result['message_count']}/{result['max_messages']}")
print(f"使用率：{result['usage_percent']}%")

# 检查是否需要续对话
if result["should_continue"]:
    print(f"⚠️ {result['suggestion']}")
```

---

### 开启新对话（继承记忆）

```python
# 方式 1: 指定旧对话
result = manager.continue_conversation("user_123", old_conv_id="abc123")
print(result["message"])
# ✅ 新对话已开启 (ID: def456)，继承了 123 条记忆

# 方式 2: 自动使用当前活跃对话
result = manager.continue_conversation("user_123")
print(f"新对话 ID: {result['new_conv_id']}")
```

---

### 对话历史

```python
# 获取最近 10 个对话
history = manager.get_conversation_history("user_123", limit=10)
for conv in history:
    print(f"{conv.id}: {conv.message_count} 消息，状态：{conv.status}")

# 获取对话链（所有祖先和后代）
chain = manager.get_chain("user_123", "current_conv_id")
for conv in chain:
    print(f"{conv.id} ← {conv.continued_from or '起点'}")
```

---

## 📊 配置说明

### 默认配置

```python
manager = ConversationManager(
    storage_path="~/.openclaw/workspace/conversations"
)

# 阈值配置
manager.max_messages = 100      # 最大消息数
manager.max_tokens = 50000      # 最大 tokens
manager.warning_threshold = 0.8 # 80% 时警告
```

### 自定义配置

```python
# 更严格的限制
manager.max_messages = 50
manager.max_tokens = 30000
manager.warning_threshold = 0.7 # 70% 就警告
```

---

## 🔔 自动监控

### 集成到对话系统

```python
from conversation_manager import ConversationManager

class ChatSystem:
    def __init__(self):
        self.conv_manager = ConversationManager()
        self.current_conv_id = None
    
    async def handle_message(self, user_id: str, message: str):
        # 如果没有当前对话，创建一个新的
        if not self.current_conv_id:
            conv = self.conv_manager.create_conversation(user_id)
            self.current_conv_id = conv.id
        
        # 添加消息并检查状态
        result = self.conv_manager.add_message(
            user_id, 
            self.current_conv_id,
            tokens=estimate_tokens(message)
        )
        
        # 检查是否需要续对话
        if result["should_continue"]:
            # 自动开启新对话
            new_result = self.conv_manager.continue_conversation(
                user_id, 
                self.current_conv_id
            )
            self.current_conv_id = new_result["new_conv_id"]
            
            # 通知用户
            await send_message(user_id, new_result["message"])
        
        # 继续处理消息...
```

---

### 定时检查

```python
import schedule

def check_conversation_status(user_id: str):
    manager = ConversationManager()
    conv = manager.get_current(user_id)
    
    if conv:
        result = manager.add_message(user_id, conv.id, 0)
        
        if result["status"] == "warning":
            send_notification(user_id, f"⚠️ {result['suggestion']}")
        elif result["status"] == "exceeded":
            send_notification(user_id, f"📊 {result['suggestion']}")

# 每小时检查一次
schedule.every().hour.do(check_conversation_status, user_id="user_123")
```

---

## 🧠 记忆继承

### 继承的记忆类型

| 类型 | 说明 | 继承方式 |
|------|------|---------|
| `preferences` | 用户偏好 | 自动继承 |
| `relationships` | 关系网络 | 自动继承 |
| `knowledge` | 知识库 | 自动继承 |
| `context` | 上下文 | 自动继承 |
| `items` | 原始记忆 | 自动继承 |

### 记忆继承流程

```
旧对话 (conv_abc123)
    ↓ 用户触发续对话
新对话 (conv_def456)
    ↓ 自动从记忆系统加载
继承所有记忆 ✅
```

### 验证继承

```python
from memory_persistence import MemoryPersistence

# 续对话前
persistence = MemoryPersistence()
stats_before = persistence.get_stats("user_123")
print(f"续对话前：{stats_before['total_memories']} 条记忆")

# 续对话
result = manager.continue_conversation("user_123")

# 续对话后
stats_after = persistence.get_stats("user_123")
print(f"续对话后：{stats_after['total_memories']} 条记忆")
print(f"继承了 {result['inherited_memories']} 条记忆")
```

---

## 📈 对话链

### 查看完整对话历史

```python
# 获取对话链
chain = manager.get_chain("user_123", "current_conv_id")

print("对话历史:")
for i, conv in enumerate(chain):
    icon = "✅" if conv.status == "active" else "🔗"
    print(f"  {i+1}. {icon} {conv.id}")
    print(f"     消息数：{conv.message_count}")
    print(f"     创建时间：{conv.created_at}")
    if conv.summary:
        print(f"     摘要：{conv.summary}")
```

### 添加对话摘要

```python
# 在对话结束前保存摘要
manager.summarize_conversation(
    user_id="user_123",
    conv_id="abc123",
    summary="讨论了灵犀 v2.8.1 的对话管理功能，包括自动续对话和记忆继承"
)
```

---

## 🎯 典型场景

### 场景 1: 长对话自动续

```python
# 用户连续聊天超过 100 条消息
for i in range(105):
    result = manager.add_message("user_123", conv_id, tokens=100)
    
    if result["should_continue"]:
        # 自动续对话
        new_result = manager.continue_conversation("user_123")
        conv_id = new_result["new_conv_id"]
        
        # 通知用户
        print(f"📊 {new_result['message']}")
        print("   之前的对话记忆已全部继承，请放心聊天～")
```

### 场景 2: 用户主动 /new

```python
# 用户输入 /new
if message == "/new":
    # 保存旧对话摘要
    old_conv = manager.get_current(user_id)
    if old_conv:
        manager.summarize_conversation(
            user_id, 
            old_conv.id, 
            summary="旧对话摘要..."
        )
    
    # 开启新对话
    result = manager.continue_conversation(user_id)
    send_message(user_id, result["message"])
    send_message(user_id, "✨ 新对话已开启！之前的记忆都保留着哦～💋")
```

### 场景 3: 跨设备续对话

```python
# 设备 A：导出对话
conv = manager.get_current("user_123")
export_data = {
    "conversation_id": conv.id,
    "continued_from": conv.continued_from,
    "message_count": conv.message_count
}

# 设备 B：导入对话
# （通过记忆系统自动同步）
```

---

## 📊 统计信息

```python
# 用户级统计
stats = manager.get_stats("user_123")
print(f"总对话数：{stats['total_conversations']}")
print(f"活跃对话：{stats['active']}")
print(f"已延续：{stats['continued']}")
print(f"当前对话：{stats['current_conv']}")

# 全局统计
global_stats = manager.get_stats()
print(f"总用户数：{global_stats['total_users']}")
print(f"总对话数：{global_stats['total_conversations']}")
```

---

## 🔧 命令行工具

```bash
# 查看对话统计
python3 conversation_manager.py stats user_123

# 开启新对话
python3 conversation_manager.py continue user_123

# 查看对话历史
python3 conversation_manager.py history user_123 --limit 10

# 查看对话链
python3 conversation_manager.py chain user_123 conv_id
```

---

## 🛡️ 最佳实践

### 1. 定期清理旧对话

```python
# 清理超过 30 天的非活跃对话
def cleanup_old_conversations(user_id: str, days: int = 30):
    manager = ConversationManager()
    history = manager.get_conversation_history(user_id, limit=1000)
    
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for conv in history:
        if conv.status != "active":
            created = datetime.fromisoformat(conv.created_at).timestamp()
            if created < cutoff:
                # 归档或删除
                conv.status = "archived"
                manager._save_conversation(conv)
```

### 2. 智能摘要

```python
# 使用 LLM 生成对话摘要
async def auto_summarize(user_id: str, conv_id: str):
    manager = ConversationManager()
    
    # 获取对话内容
    messages = get_conversation_messages(user_id, conv_id)
    
    # 调用 LLM 生成摘要
    summary = await llm_summarize(messages)
    
    # 保存摘要
    manager.summarize_conversation(user_id, conv_id, summary)
```

### 3. 预警通知

```python
# 在 80% 时预警，100% 时自动续
def check_and_notify(user_id: str):
    manager = ConversationManager()
    conv = manager.get_current(user_id)
    
    if not conv:
        return
    
    result = manager.add_message(user_id, conv.id, 0)
    
    if result["status"] == "warning":
        # 80% - 发送预警
        send_notification(user_id, f"⚠️ {result['suggestion']}")
    elif result["status"] == "exceeded":
        # 100% - 自动续对话
        new_result = manager.continue_conversation(user_id)
        send_notification(user_id, f"📊 {new_result['message']}")
```

---

## 🎉 总结

**v2.8.1 对话管理器实现：**

1. ✅ **📊 长度监控** - 实时统计消息数和 tokens
2. ✅ **🔄 一键续对话** - 自动创建新对话
3. ✅ **🧠 记忆继承** - 所有记忆自动带走
4. ✅ **⚡ 无缝切换** - 用户无感知

**使用场景：**
- 长对话自动续（超过 100 条消息）
- 用户主动 `/new`
- 跨设备续对话
- 定期清理旧对话

**优势：**
- 不再失忆
- 记忆完整保留
- 对话历史可追溯

---

**作者:** 丝佳丽 Scarlett  
**日期:** 2026-03-04  
**状态:** ✅ 完成，待测试推送
