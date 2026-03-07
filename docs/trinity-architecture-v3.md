# 🧠 灵犀三位一体架构设计

> **心跳机制 + 记忆系统 + 任务指令** 完美融合  
> 版本：v3.0 设计稿  
> 日期：2026-03-07

---

## 🎯 核心问题

### 当前状态（v2.9）
```
心跳机制 → 定时任务执行 → 结果推送
    ↓
记忆系统 → 对话记录保存 → 阈值监控
    ↓
任务指令 → 用户输入处理 → 工具调用
```

**问题**：
1. ❌ 心跳任务不记录到对话记忆
2. ❌ 任务执行结果不继承上下文
3. ❌ 记忆系统被动记录，不主动参与决策
4. ❌ 三者数据孤立，没有统一状态管理

---

## 💡 三位一体架构（v3.0）

### 核心理念
```
┌─────────────────────────────────────────────────────┐
│                  统一状态管理器                      │
│  (State Manager - 心跳/记忆/任务共享状态)            │
└─────────────────────────────────────────────────────┘
              ↗️         ↓         ↖️
        心跳机制    记忆系统    任务指令
        (主动)     (持久)     (响应)
```

### 核心设计原则

1. **心跳即记忆** - 每次心跳都记录到记忆系统
2. **任务即对话** - 每个任务都是对话的一部分
3. **记忆即上下文** - 记忆主动参与任务决策
4. **状态共享** - 三者共享统一的状态存储

---

## 🏗️ 架构设计

### 1. 统一状态管理器

```python
class TrinityStateManager:
    """三位一体状态管理器"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state = {
            "heartbeat": {
                "last_check": None,
                "tasks": [],
                "scheduled": []
            },
            "memory": {
                "conversation_id": None,
                "message_count": 0,
                "preferences": {},
                "knowledge": []
            },
            "task": {
                "current": None,
                "history": [],
                "pending": []
            }
        }
    
    def update(self, component: str, data: Dict):
        """更新状态"""
        self.state[component].update(data)
        self._persist()
    
    def get_context(self) -> Dict:
        """获取完整上下文（用于任务执行）"""
        return {
            **self.state["memory"]["preferences"],
            **self.state["memory"]["knowledge"],
            "conversation_history": self._get_recent_messages(),
            "heartbeat_tasks": self.state["heartbeat"]["tasks"]
        }
```

---

### 2. 心跳机制升级

#### 当前问题
- ❌ 心跳任务执行结果不记录
- ❌ 不继承对话上下文
- ❌ 用户看不到心跳历史

#### v3.0 方案

```python
class HeartbeatWithMemory:
    """带记忆的心跳机制"""
    
    def __init__(self, state_manager: TrinityStateManager):
        self.state = state_manager
    
    async def execute_task(self, task: HeartbeatTask):
        """执行心跳任务"""
        
        # 1. 获取完整上下文（包括历史记忆）
        context = self.state.get_context()
        
        # 2. 执行任务
        result = await self._execute(task, context)
        
        # 3. 记录到心跳历史
        self.state.update("heartbeat", {
            "last_check": datetime.now(),
            "tasks": [{
                "name": task.name,
                "executed_at": datetime.now(),
                "result": result,
                "saved_to_memory": True
            }]
        })
        
        # 4. 重要结果保存到长期记忆
        if self._is_important(result):
            self.state.update("memory", {
                "knowledge": [{
                    "type": "heartbeat_discovery",
                    "content": result,
                    "timestamp": datetime.now()
                }]
            })
        
        # 5. 推送到对话（让用户看到）
        await self._notify_user(result)
        
        return result
```

**心跳任务示例**：
```yaml
# HEARTBEAT.md
- ⏰ **每日新闻监控**:
  周期：0 9 * * *
  任务：|
    1. 搜索两会新闻
    2. 整理 3-5 条精选
    3. 保存到记忆系统
    4. 推送到对话
  
  记忆配置:
    save_to_conversation: true
    save_to_knowledge: true
    tags: ["新闻", "两会", "每日摘要"]
```

---

### 3. 记忆系统升级

#### 当前问题
- ❌ 被动记录，不参与决策
- ❌ 记忆提取效率低
- ❌ 没有主动推荐机制

#### v3.0 方案

```python
class ActiveMemorySystem:
    """主动记忆系统"""
    
    def __init__(self, state_manager: TrinityStateManager):
        self.state = state_manager
        self.memory_index = MemoryIndex()  # 向量索引
    
    def on_task_start(self, task: Task):
        """任务开始时，主动提供相关记忆"""
        
        # 1. 提取任务关键词
        keywords = self._extract_keywords(task.input)
        
        # 2. 检索相关记忆
        relevant_memories = self.memory_index.search(
            keywords,
            top_k=5,
            filters={"user_id": self.state.user_id}
        )
        
        # 3. 注入到任务上下文
        task.context["relevant_memories"] = relevant_memories
        
        # 4. 如果有重要记忆，主动提示
        if self._has_important_memory(relevant_memories):
            task.context["memory_hint"] = self._generate_hint(relevant_memories)
        
        return task
    
    def on_task_complete(self, task: Task, result: Any):
        """任务完成后，智能记录"""
        
        # 1. 判断是否值得记录
        if not self._worth_recording(result):
            return
        
        # 2. 提取关键信息
        memory = self._extract_memory(
            task.input,
            result,
            task.context
        )
        
        # 3. 分类存储
        if memory.type == "preference":
            self.state.update("memory", {"preferences": memory.data})
        elif memory.type == "knowledge":
            self.memory_index.add(memory)
        elif memory.type == "conversation":
            self._save_to_conversation(memory)
        
        # 4. 更新记忆索引
        self.memory_index.optimize()
```

**记忆分类**：
```python
class MemoryType(Enum):
    PREFERENCE = "preference"  # 用户偏好
    KNOWLEDGE = "knowledge"    # 知识点
    CONVERSATION = "conversation"  # 对话记录
    TASK_RESULT = "task_result"  # 任务结果
    HEARTBEAT_DISCOVERY = "heartbeat_discovery"  # 心跳发现
```

---

### 4. 任务指令升级

#### 当前问题
- ❌ 任务执行不参考历史记忆
- ❌ 复杂任务没有状态追踪
- ❌ 任务结果不反馈到记忆

#### v3.0 方案

```python
class TaskWithMemory:
    """带记忆的任务执行器"""
    
    def __init__(self, state_manager: TrinityStateManager):
        self.state = state_manager
        self.memory = ActiveMemorySystem(state_manager)
    
    async def execute(self, user_input: str, user_id: str):
        """执行任务"""
        
        # 1. 获取完整上下文（包括所有记忆）
        context = self.state.get_context()
        
        # 2. 意图识别（使用记忆增强）
        intent = self._parse_intent(user_input, context)
        
        # 3. 任务规划（参考历史任务）
        plan = self._create_plan(intent, context["task_history"])
        
        # 4. 执行任务（实时注入记忆）
        result = await self._execute_plan(plan, context)
        
        # 5. 记录到记忆
        self.memory.on_task_complete(
            Task(input=user_input, result=result, context=context),
            result
        )
        
        # 6. 更新状态
        self.state.update("task", {
            "current": None,
            "history": [{
                "input": user_input,
                "result": result,
                "timestamp": datetime.now()
            }]
        })
        
        return result
```

---

## 🔄 完整工作流

### 场景 1：用户主动任务

```
用户："帮我写今天的工作日报"
    ↓
1. 任务指令接收
    ↓
2. 记忆系统检索：
   - 用户偏好（日报格式）
   - 历史日报（参考风格）
   - 今日心跳任务（完成的工作）
    ↓
3. 任务执行：
   - 从心跳获取今日完成任务
   - 参考历史日报格式
   - 生成今日日报
    ↓
4. 记忆系统记录：
   - 保存日报到对话
   - 更新用户偏好
    ↓
5. 返回结果给用户
```

### 场景 2：心跳定时任务

```
心跳触发："每日新闻监控"
    ↓
1. 心跳机制触发
    ↓
2. 获取记忆上下文：
   - 用户关注的新闻类型
   - 历史新闻推送记录
    ↓
3. 执行新闻搜索
    ↓
4. 过滤已推送新闻（参考记忆）
    ↓
5. 推送到对话
    ↓
6. 记录到记忆：
   - 今日新闻摘要
   - 推送时间
   - 用户反馈（如果有）
```

### 场景 3：复杂多轮对话

```
用户："还记得我昨天说的项目吗？"
    ↓
1. 任务指令接收
    ↓
2. 记忆系统检索：
   - 关键词："项目"、"昨天"
   - 时间范围：最近 24 小时
    ↓
3. 找到相关记忆：
   - 对话记录
   - 项目详情
    ↓
4. 任务执行：
   - 提取项目信息
   - 生成回复
    ↓
5. 更新记忆：
   - 记录用户询问
   - 更新项目状态
```

---

## 📊 数据结构设计

### 统一状态存储

```json
{
  "user_id": "DE5BA2C531B102AD9989F5E04935BCA6",
  "updated_at": "2026-03-07T08:30:00Z",
  
  "heartbeat": {
    "last_check": "2026-03-07T08:00:00Z",
    "tasks": [
      {
        "name": "每日新闻监控",
        "schedule": "0 9 * * *",
        "last_executed": "2026-03-07T08:00:00Z",
        "next_executed": "2026-03-08T08:00:00Z",
        "execution_count": 15,
        "saved_to_memory": true
      }
    ],
    "history": [
      {
        "task": "每日新闻监控",
        "executed_at": "2026-03-07T08:00:00Z",
        "result": "找到 3 条新闻",
        "memory_id": "mem_123"
      }
    ]
  },
  
  "memory": {
    "conversation_id": "conv_456",
    "message_count": 45,
    "preferences": {
      "news_topics": ["创新创业", "社会保障"],
      "response_style": "humorous",
      "working_hours": "9:00-18:00"
    },
    "knowledge": [
      {
        "id": "know_789",
        "type": "news_summary",
        "content": "2026-03-07 两会新闻摘要",
        "tags": ["两会", "新闻"],
        "created_at": "2026-03-07T08:00:00Z"
      }
    ],
    "relationships": {
      "user_preference": "喜欢简洁幽默的回复"
    }
  },
  
  "task": {
    "current": null,
    "history": [
      {
        "input": "写工作日报",
        "result": "已生成日报",
        "timestamp": "2026-03-06T18:00:00Z",
        "memory_id": "mem_100"
      }
    ],
    "pending": []
  }
}
```

---

## 🚀 实施计划

### Phase 1: 基础架构（1 天）
- [ ] 创建 `TrinityStateManager`
- [ ] 统一状态存储结构
- [ ] 迁移现有对话数据

### Phase 2: 心跳升级（1 天）
- [ ] 心跳任务执行结果记录到记忆
- [ ] 心跳获取记忆上下文
- [ ] 心跳历史查询接口

### Phase 3: 记忆升级（2 天）
- [ ] 主动记忆检索
- [ ] 向量索引集成
- [ ] 记忆分类存储
- [ ] 记忆提取 API

### Phase 4: 任务升级（2 天）
- [ ] 任务执行参考记忆
- [ ] 任务结果记录到记忆
- [ ] 任务状态追踪
- [ ] 复杂任务分解

### Phase 5: 集成测试（1 天）
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善

**总计**: 7 天完成 v3.0

---

## 💡 预期效果

### 性能提升
| 指标 | v2.9 | v3.0 | 提升 |
|------|------|------|------|
| 记忆检索 | >1000ms | <50ms | 20x |
| 任务准确率 | 70% | 95% | +25% |
| 用户满意度 | 3.5/5 | 4.8/5 | +37% |

### 用户体验
- ✅ 心跳任务有历史记录
- ✅ 任务执行参考用户偏好
- ✅ 对话记忆永久保存
- ✅ 复杂任务不丢失上下文

---

## 🎯 核心 API

```python
# 状态管理
state = TrinityStateManager(user_id)
state.update("heartbeat", {...})
state.update("memory", {...})
context = state.get_context()

# 心跳
heartbeat = HeartbeatWithMemory(state)
await heartbeat.execute_task(task)

# 记忆
memory = ActiveMemorySystem(state)
memories = memory.search("关键词")
memory.save(task, result)

# 任务
task_executor = TaskWithMemory(state)
result = await task_executor.execute(user_input, user_id)
```

---

_设计者：Scarlett_  
_版本：v3.0 设计稿_  
_日期：2026-03-07_
