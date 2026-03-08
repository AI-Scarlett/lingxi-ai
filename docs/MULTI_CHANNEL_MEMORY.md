# 🧠 灵犀多渠道记忆共享系统

> **版本**: v3.1  **日期**: 2026-03-08  **作者**: 斯嘉丽 Scarlett

---

## 📋 核心需求

**不同渠道（QQBot-1、QQBot-2、飞书、微信、钉钉）产生的记忆，存入一个共同的记忆文件。当用户通过其他渠道沟通时，在 Layer 2 优先调用共同的记忆库，然后才调用大模型回答。**

---

## 🏗️ 架构设计

### 1. 共享记忆用户 ID

所有渠道使用同一个用户 ID (`default`) 来存储和检索记忆：

```python
class MemoryService:
    # 共享记忆用户 ID - 所有渠道共用这个用户的记忆
    SHARED_USER_ID = "default"
    
    def __init__(self, user_id: str = None, channel: str = "unknown", ...):
        # 使用共享用户 ID，实现多渠道记忆共享
        self.user_id = user_id if user_id else self.SHARED_USER_ID
        self.channel = channel  # 记录来源渠道
```

### 2. 记忆项结构增强

添加 `channel` 字段来记录记忆来源：

```python
@dataclass
class MemoryItem:
    id: str
    category: str           # 所属分类
    topic: str              # 主题标签
    content: str            # 记忆内容
    source: str             # 来源（对话 ID/任务 ID）
    timestamp: float        # 创建时间戳
    user_id: str = "default"  # 共享用户 ID
    channel: str = "unknown"  # ✅ 新增：来源渠道
    embeddings: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 3. 记忆存储流程

```
用户输入 (任何渠道)
    ↓
MemoryService.memorize(conversation, conv_id, channel="qqbot")
    ↓
1. 保存原始对话（包含渠道信息）
2. 提取记忆项
3. 自动分类和关联
4. 设置 item.channel = channel  ✅
5. 保存到共享记忆文件 (memory/items/memories.jsonl)
```

### 4. 记忆检索流程（Layer 2 优先调用）

```
用户输入 (任何渠道)
    ↓
Layer 0: 快速响应匹配（规则匹配，<5ms）
    ↓ 未匹配
Layer 1: 缓存响应（LRU Cache，<10ms）
    ↓ 未命中
Layer 2: 优先调用共享记忆库 ✅
    ↓
1. MemoryService.get_context(cross_channel=True)  # 跨渠道检索
2. 获取所有渠道的记忆（qqbot + feishu + wechat + ...）
3. 最近记忆（top 10）+ 模式识别
4. 构建完整上下文
    ↓
Layer 3: 大模型回答（使用 Layer 2 提供的上下文）
```

---

## 🔧 关键修改

### 1. MemoryService 修改

```python
# 记忆存储 - 添加渠道信息
async def memorize(self, conversation: List[Dict], conv_id: str, channel: str = "unknown") -> Dict:
    # ...
    for item in items:
        item.channel = channel  # ✅ 记录来源渠道
        await self.store.save_memory_item(item)

# 记忆检索 - 跨渠道支持
async def get_context(self, user_id: str = None, channel: str = None, cross_channel: bool = True) -> Dict:
    """
    Layer 2 优先调用此方法获取共享记忆
    
    Args:
        cross_channel: True = 使用所有渠道的记忆（默认）
                       False = 只使用当前渠道的记忆
    """
    uid = user_id if user_id else self.SHARED_USER_ID
    return await self.retriever.proactive_context(uid, cross_channel=cross_channel)
```

### 2. MemoryRetriever 修改

```python
async def proactive_context(self, user_id: str = "default", channel: str = None, cross_channel: bool = True) -> Dict:
    items = await self.store.load_all_items()
    
    # 跨渠道检索：使用所有记忆（默认行为）✅
    if not cross_channel and channel:
        items = [i for i in items if i.channel == channel]
    
    # 获取最近记忆（所有渠道共享）
    recent = sorted(items, key=lambda x: x.timestamp, reverse=True)[:10]
    
    return {
        "recent_context": [r.to_dict() for r in recent],
        "predicted_needs": patterns,
        "total_memories": len(items),
        "cross_channel": cross_channel,  # ✅ 标记是否跨渠道
        "channel_stats": self._get_channel_stats(items)  # ✅ 各渠道统计
    }
```

---

## 📊 记忆文件结构

```
~/.openclaw/workspace/memory/
├── items/
│   └── memories.jsonl          # ✅ 所有渠道的共享记忆（JSONL 格式）
├── context/
│   └── conversations/          # 对话记录（按渠道分开）
│       ├── qqbot_conv_001.json
│       ├── feishu_conv_001.json
│       └── wechat_conv_001.json
├── preferences/                 # 用户偏好（共享）
├── relationships/               # 关系网络（共享）
└── knowledge/                   # 知识库（共享）
```

### memories.jsonl 示例

```jsonl
{"id":"abc123","category":"preferences","topic":"称呼偏好","content":"用户喜欢被称呼为'老板'","source":"conv_qqbot_001","timestamp":1709856000,"user_id":"default","channel":"qqbot","confidence":0.9}
{"id":"def456","category":"knowledge","topic":"工作内容","content":"用户从事 AI 开发工作","source":"conv_feishu_001","timestamp":1709856100,"user_id":"default","channel":"feishu","confidence":0.95}
{"id":"ghi789","category":"preferences","topic":"回复风格","content":"喜欢幽默风趣的回复风格","source":"conv_wechat_001","timestamp":1709856200,"user_id":"default","channel":"wechat","confidence":0.9}
```

---

## 🚀 使用示例

### 场景 1：QQBot 聊天后，飞书聊天时自动调用 QQBot 的记忆

```python
# 1. QQBot 聊天
await memory.memorize(
    conversation=[{"role": "user", "content": "我喜欢喝奶茶"}],
    conv_id="qqbot_conv_001",
    channel="qqbot"  # ✅ 记录渠道
)

# 2. 飞书聊天时，Layer 2 自动获取 QQBot 的记忆
context = await memory.get_context(
    channel="feishu",
    cross_channel=True  # ✅ 跨渠道检索（默认）
)
# context 包含 QQBot 的记忆："我喜欢喝奶茶"

# 3. 用户在飞书问："我喜欢喝什么？"
# Layer 2 从共享记忆中检索到答案，无需调用大模型
```

### 场景 2：查看各渠道记忆统计

```python
context = await memory.get_context()
print(context["channel_stats"])
# 输出：{"qqbot": 15, "feishu": 8, "wechat": 12, "dingtalk": 5}
```

### 场景 3：仅使用当前渠道的记忆（特殊场景）

```python
context = await memory.get_context(
    channel="qqbot",
    cross_channel=False  # ❌ 不跨渠道，只使用 QQBot 的记忆
)
```

---

## ✅ 核心优势

1. **统一记忆库** - 所有渠道共享一个记忆文件，避免信息孤岛
2. **渠道可追溯** - 每条记忆记录来源渠道，便于分析和调试
3. **Layer 2 优先** - 在调用大模型之前，优先从共享记忆库检索
4. **灵活配置** - 支持跨渠道/单渠道检索切换
5. **性能优化** - 共享记忆减少重复存储，提高检索效率

---

## 📝 待办事项

- [ ] 更新 orchestrator_v2.py，确保 Layer 2 执行时调用 `memory.get_context(cross_channel=True)`
- [ ] 添加渠道统计 Dashboard，可视化各渠道记忆分布
- [ ] 优化记忆去重逻辑，避免多渠道重复记忆
- [ ] 添加记忆迁移工具，支持用户 ID 合并

---

**❤️ 心有灵犀，一点就通 - 无论用户从哪个渠道来，都能记住他的一切**
