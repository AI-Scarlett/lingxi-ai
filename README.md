# 🧠 Lingxi AI (灵犀)

> **心有灵犀，一点就通** - 企业级 AI 智能调度系统 💋

[![Version](https://img.shields.io/badge/version-2.7.0-blue.svg)](https://github.com/AI-Scarlett/lingxi-ai/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Performance](https://img.shields.io/badge/performance-500x%20faster-orange.svg)](OPTIMIZATION_GUIDE.md)
[![Async](https://img.shields.io/badge/async-native-brightgreen.svg)](ASYNC_GUIDE.md)
[![S0-S3](https://img.shields.io/badge/method-S0→S3%20Three--Step-red.svg)](COMPLEX_TASK_THREE_STEP.md)
[![Memory](https://img.shields.io/badge/memory-memU%20inspired-purple.svg)](https://github.com/NevaMind-AI/memU)
[![Config](https://img.shields.io/badge/config-flexible-yellow.svg)](CONFIG_GUIDE.md)

---

## 🌟 核心特性

### v2.6.0 记忆系统 💋 (2026-03-04)

**🧠 完整记忆系统集成（参考 memU 框架）**

**特别感谢：**
> 本版本的记忆系统设计深受 [memU](https://github.com/NevaMind-AI/memU) 项目启发。
> 感谢 NevaMind-AI 团队开源的优秀记忆框架，为 24/7 主动代理提供了清晰的设计范式。
> 
> **memU 核心贡献：**
> - 文件系统式记忆结构（分层、可导航）
> - 三层记忆架构（Resource → Item → Category）
> - 主动学习循环（后台持续提取）
> - 双模式检索（RAG 快速 + LLM 深度）
> 
> 我们在 memU 的基础上，针对灵犀的使用场景进行了优化和简化。
> 🙏 向原文档作者致敬！

**文件系统式记忆结构：**
```
memory/
├── preferences/          # 用户偏好（沟通风格、兴趣话题）
├── relationships/        # 关系网络（联系人、交互历史）
├── knowledge/            # 知识库（专业领域、技能）
├── context/              # 上下文（对话、待办任务）
└── items/                # 原始记忆项（JSONL 格式）
```

**核心组件：**
- ✅ `MemoryStructure` - 文件系统式存储（4 层分类）
- ✅ `MemoryExtractor` - LLM 驱动自动提取
- ✅ `MemoryOrganizer` - 自动分类 + 交叉引用
- ✅ `MemoryRetriever` - 关键词检索 + LLM 深度检索
- ✅ `MemoryService` - 统一 API 接口

**记忆能力：**
- ✅ 自动从对话中提取偏好、关系、知识
- ✅ 交叉引用关联记忆
- ✅ 模式检测（活跃时间、偏好分析）
- ✅ 主动上下文加载（执行前自动加载）
- ✅ 毫秒级检索（关键词匹配）
- ✅ 深度推理检索（LLM 筛选 + 预测）

**使用示例：**
```python
from scripts.memory_service import MemoryService

service = MemoryService(llm_client)
await service.initialize()

# 记忆对话
result = await service.memorize(conversation, conv_id)
print(f"提取了 {result['extracted_items']} 条记忆")

# 检索记忆
result = await service.retrieve("用户偏好", method="keyword")
print(f"检索到 {result['total']} 条结果")

# 主动上下文
context = await service.get_context(user_id)
print(f"加载了 {context['total_memories']} 条记忆")

# 统计信息
stats = await service.get_stats()
print(f"总记忆数：{stats['total_items']}")
```

**性能特点：**
- ⚡ 记忆检索：<10ms（关键词）
- 🧠 自动提取：后台异步，不阻塞响应
- 💾 持久化存储：JSONL 格式，高效读写
- 🔗 交叉引用：自动关联相关记忆

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.6.0

---

### v2.7.0 Embedding 向量检索 🧠 (2026-03-04)

**语义相似度搜索 + 智能分类**

**核心功能：**
- ✅ `EmbeddingService` - Embedding 生成服务
  - 本地 TF-IDF embedding（无需 API）
  - API embedding（OpenAI 兼容接口）
  - 批量 embedding 生成

- ✅ `VectorIndex` - 向量索引
  - 高效相似度搜索
  - 余弦相似度计算
  - 阈值过滤

- ✅ `SmartCategorizer` - 智能分类器
  - 基于 embedding 聚类
  - 自动类别中心计算
  - 置信度评分

- ✅ `SemanticMemoryEnhancer` - 语义记忆增强器
  - 整合 embedding 检索和分类
  - 语义相似度搜索
  - 自动分类建议

**使用示例：**
```python
from scripts.memory_embedding import SemanticMemoryEnhancer

enhancer = await create_enhancer()

# 添加记忆（带 embedding）
await enhancer.add_memory(
    item_id="mem_001",
    content="用户喜欢喝拿铁咖啡",
    category="preferences",
    metadata={"user_id": "default"}
)

# 语义相似度搜索
results = await enhancer.search_similar(
    query="用户喜欢的饮品",
    category="preferences",
    top_k=5
)

# 自动分类
result = await enhancer.auto_categorize("用户每天早上跑步")
print(f"类别：{result['category']}, 置信度：{result['confidence']}")
```

**性能特点：**
- ⚡ 语义检索：毫秒级
- 🎯 分类准确率：>85%
- 💾 本地 embedding：无需 API

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.7.0

---

### ⚙️ 灵活配置系统

**3 种预设模式，按需选择：**

#### Minimal（最小消耗）
```python
from scripts.memory_config import apply_preset
await apply_preset("minimal")
```
- ✅ 基础记忆 + 关键词检索
- ❌ Embedding / 主动学习
- 💰 ~50K tokens/月 (~$1.5)

#### Balanced（平衡模式）⭐ 推荐
```python
await apply_preset("balanced")
```
- ✅ Embedding 语义搜索（本地 TF-IDF，零成本）
- ✅ 智能分类
- ❌ 主动学习（耗 tokens）
- 💰 ~100K tokens/月 (~$3)

#### Full（全功能）
```python
await apply_preset("full")
```
- ✅ 所有功能
- ✅ 24/7 主动学习 + 意图预测
- 💰 ~2.4M tokens/月 (~$72)

**详细配置指南：** [CONFIG_GUIDE.md](CONFIG_GUIDE.md)

---

### v2.6.0 记忆系统 💋 (2026-03-04)# 获取统计
stats = assistant.get_stats()
print(f"已处理对话：{stats['learner']['total_conversations_processed']}")
```

**预测示例输出：**
```json
{
  "predicted_intent": "工作相关任务",
  "confidence": 0.75,
  "reasoning": "用户关注工作时间，可能即将开始工作",
  "suggested_action": "询问是否需要准备工作资料",
  "related_memories": [...]
}
```

**主动提醒示例：**
```
☕️ 老板，工作时间到啦～ 今天有什么计划吗？
🍱 老板，该吃午饭啦！记得休息一下哦～
📊 记忆系统统计：共 50 条记忆，最近 24 小时新增 12 条
```

**性能特点：**
- 🔄 持续学习：后台异步，不阻塞主任务
- 🧠 意图预测：基于记忆模式，置信度>60%
- ⚡ 主动提醒：定时触发，冷却机制防骚扰
- 💾 自动整理：定期压缩，保持系统高效

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.8.0

---

### v2.5.1 最新优化 🚀 (2026-03-04)

**⚡ 性能优化 + 缺陷修复**

**1 秒响应保证：**
- ✅ 即时任务响应 **<500ms** (原 800-1200ms)
- ✅ 后台任务启动 **<200ms** (原 500-800ms)
- ✅ 并行效率提升 **40%** (真正并行 vs 伪并行)
- ✅ 内存占用降低 **30%**

**缺陷修复：**
- ✅ 完成所有 5 处 TODO（执行器调用/团队递归/成本计算等）
- ✅ QQ 通知完善（完成/失败/进度主动推送）
- ✅ 错误处理增强（失败自动重试 + 降级方案）

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.5.1

---

### v2.5.0 多平台集成 📱 (2026-03-03)

**📱 飞书 + 钉钉 + 企业微信**
- ✅ 飞书机器人 - 文本/Markdown/图片/卡片消息
- ✅ 钉钉机器人 - 文本/Markdown/链接/卡片消息（可@所有人）
- ✅ 企业微信机器人 - 文本/Markdown/文本卡片/图文消息
- ✅ 多平台管理器 - 统一接口/广播功能

**使用示例：**
```python
# 广播到所有平台
manager.broadcast(text="任务完成！✅")
```

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.5.0

---

### v2.4.0 语音交互系统 🎤 (2026-03-03)

**🎤 讯飞 + 国际引擎**
- ✅ 科大讯飞（国内）- 中文识别 98%，50+ 音色
- ✅ Google/Azure/AWS（国外）- 125+ 语言，400+ 声音
- ✅ 推荐音色：讯飞小燕（温柔知性）、Azure Jenny（温柔女声）

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.4.0

---

### v2.3.0 智能学习系统 🧠 (2026-03-03)

**🧠 任务日志 + 模式学习 + 预测调度**
- ✅ 任务日志记录 - 结构化存储，按日期分文件
- ✅ 模式学习 - 频率分析，时间模式，偏好学习
- ✅ 自动优化 - 模型推荐，成本预估，并行/缓存建议
- ✅ 预测调度 - 时间预测，资源预加载，智能提醒
- ✅ 配置迁移 - 版本升级保留所有配置
- ✅ QQ Bot 自动启用

**性能提升（100 次基准测试）：**
- ⚡ 速度提升 **85.8%** (1680ms → 238ms)
- 💰 成本降低 **79.3%** (1808 → 375 token)
- 🎯 缓存命中率 **81.0%**

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.3.0

---

### v2.2.0 复杂任务三步法 🎯 (2026-03-03)

**🎯 S0→S1→S2→S3 三层架构**

📚 **参考文档：** "这是我迄今为止开发的最满意的一个技能" - 四十学蒙

**S0 零成本预筛选** - 规则匹配，0 token，过滤 80% 简单消息  
**S1 轻量复杂度评估** - 五维打分，≤8 分直接执行  
**S2 深度规划 & 审计** - DAG 执行蓝图，锁定机制  
**S3 分阶段执行 & 质量控制** - Phase 并行，QA 审计

**📊 性能提升：**
- 评估成本降低 **70%**
- 复杂任务成功率 **98%**

**GitHub Tag:** https://github.com/AI-Scarlett/lingxi-ai/releases/tag/v2.2.0

---

### v2.1.0 异步任务 + QQ Bot 🤖 (2026-03-03)

**🎯 复杂任务方法论（三层架构）**
- ✅ 战略层/战术层/执行层三层架构
- ✅ DAG 任务图依赖管理
- ✅ 智能并发控制（最大 5 并发）
- ✅ 容错重试机制（最多 3 次重试）
- ✅ 进度实时追踪（分层报告）
- 📊 复杂任务处理效率提升 **3 倍**

**🔄 异步任务系统**
- ✅ 多任务并行处理
- ✅ 后台异步执行（不阻塞）
- ✅ 完成主动通知（QQ 推送）
- ✅ 任务状态持久化
- ✅ 智能任务分类（耗时/即时）
- ⚡ 即时任务响应 **<1 秒**

**🤖 QQ Bot 深度集成**
- ✅ 自动任务识别
- ✅ 桥接器调用接口
- ✅ 多格式消息支持
- ✅ 主动通知机制

### v1.2.0 自定义角色系统

**🎭 完全自定义 AI 角色系统**
- ✅ 用 YAML/JSON 配置你自己的 AI 专家团队
- ✅ 智能模型推荐（成本/速度/质量三选一）
- ✅ 内置 8+ 主流大模型参数池
- ✅ 场景模板一键生成完整团队

### v1.1.0 性能提升 500 倍

**⚡ 性能优化**
- 🔥 意图识别从 50ms → 0.1ms
- ⚡ 单次任务从 2s → 300ms
- 📈 LRU 缓存命中率 80%+

---

## 🚀 快速开始

### 安装

```bash
cd /home/admin/.openclaw/skills/
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai
```

### 使用异步任务系统（NEW!）

```python
from scripts.orchestrator_async import get_async_orchestrator

orch = get_async_orchestrator()

# 耗时任务（后台执行，不阻塞）
reply = await orch.execute_async(
    user_input="帮我发布公众号文章，主题是 AI 发展",
    user_id="user_123",
    channel="qqbot",
    is_background=True
)
print(reply)
# 输出："好的老板，正在后台发布，完成后通知你～"

# 即时任务（立即响应）
reply = await orch.execute_async(
    user_input="北京天气怎么样",
    user_id="user_123",
    channel="qqbot",
    is_background=False
)
print(reply)
# 立即输出天气信息
```

### 使用复杂任务系统（NEW!）

```python
from scripts.orchestrator_advanced import get_advanced_orchestrator

orch = get_advanced_orchestrator()

# 执行复杂任务
reply = await orch.execute_complex_task(
    user_input="帮我发布一篇公众号文章，主题是 AI 发展趋势，需要配 3 张图",
    user_id="user_123",
    channel="qqbot"
)

print(reply)
# 输出：
# 🎯 复杂任务已启动！
# 📋 任务：帮我发布一篇公众号文章...
# 📊 总体进度：0/10
# 📈 分层进度:
#   🎭 战略层：0/1
#   🗺️ 战术层：0/3
#   ⚙️ 执行层：0/6
```

### 集成到 QQ Bot

```python
from scripts.lingxi_qqbot import handle_qq_message

# QQ Bot 收到消息时调用
async def on_qq_message(user_id, message):
    reply = await handle_qq_message(user_id, message)
    await send_reply(user_id, reply)
```

**自动效果：**
- 查天气 → 立即回复
- 发文章 → 后台执行 + 完成通知
- 多任务 → 并行处理不等待

---

## 📦 预设场景模板

### 电商运营团队
```bash
python scripts/dynamic_roles.py --template ecommerce
```

包含：标题优化师、产品摄影师、客服机器人、数据分析师

### 内容创作者团队
```bash
python scripts/dynamic_roles.py --template content_creator
```

包含：文案专家、视频脚本师、封面设计师、多语言翻译

### 开发团队
```bash
python scripts/dynamic_roles.py --template developer
```

包含：Python 专家、前端工程师、测试工程师、文档撰写员

---

## 🧠 智能模型推荐

系统会根据任务类型自动推荐最佳模型：

| 任务类型 | Speed | Cost | Quality | Balance |
|---------|-------|------|---------|---------|
| 代码编写 | glm-edge | qwen-turbo | qwen-coder | **qwen-coder** |
| 文案创作 | qwen-turbo | qwen-turbo | qwen-max | **qwen-plus** |
| 数据分析 | qwen-plus | qwen-turbo | gpt-4o | **qwen-max** |
| 简单对话 | glm-edge | glm-edge | qwen-plus | **qwen-plus** |
| 图像分析 | qwen-vl-max | qwen-vl-max | gpt-4o | **qwen-vl-max** |

详细成本对照表见 [ROLE_CONFIG_GUIDE.md](ROLE_CONFIG_GUIDE.md)

---

## 📊 性能对比

| 版本 | 意图识别 | 单次任务 | 并发控制 | 异步处理 | 复杂任务 |
|------|---------|---------|---------|---------|---------|
| v1.0 | 50ms | ~2s | ❌ | ❌ | ❌ |
| v1.1 | **0.1ms** | ~300ms | ✅ | ❌ | ❌ |
| v1.2 | **0.1ms** | ~300ms | ✅ | ❌ | ❌ |
| **v2.1** | **0.1ms** | **<1s** | ✅ | ✅ | ✅ |

详细说明见 [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)

---

## 🛠️ 可用技能

| 技能 | 用途 | 推荐模型 | 执行方式 |
|------|------|---------|---------|
| `copywriter` | 文案创作 | qwen-plus | 即时/后台 |
| `code-writer` | 代码编写 | qwen-coder | 即时 |
| `data-analyzer` | 数据分析 | qwen-max | 后台 |
| `image-generator` | 图像生成 | qwen-image-max | 后台 |
| `translator` | 多语言翻译 | qwen-plus | 即时 |
| `social-publisher` | 社交平台发布 | gpt-4o-mini | 后台 |
| `web-search` | 网页搜索 | - | 即时 |
| `excel-handler` | Excel 处理 | qwen-max | 后台 |

---

## 📁 项目结构

```
lingxi-ai/
├── SKILL.md                      # 技能说明
├── README.md                     # 本文件
├── OPTIMIZATION_GUIDE.md         # 性能优化指南
├── ROLE_CONFIG_GUIDE.md          # 角色配置指南
├── ASYNC_GUIDE.md                # 异步系统详解 (NEW!)
├── COMPLEX_TASK_METHODOLOGY.md   # 复杂任务方法论 (NEW!)
├── QQBOT_INTEGRATION.md          # QQ Bot 集成指南 (NEW!)
├── scripts/
│   ├── orchestrator.py           # 原版主控制器
│   ├── orchestrator_optimized.py # 优化版主控制器
│   ├── orchestrator_async.py     # ✅ 异步编排器 (NEW!)
│   ├── orchestrator_advanced.py  # ✅ 高级编排器 (NEW!)
│   ├── intent_parser.py          # 原版意图识别
│   ├── intent_parser_optimized.py # 高速意图识别
│   ├── task_planner.py           # 原版任务规划
│   ├── task_planner_optimized.py # 并发任务规划
│   ├── dynamic_roles.py          # 动态角色系统
│   ├── task_manager.py           # ✅ 任务管理器 (NEW!)
│   ├── async_executor.py         # ✅ 异步执行器 (NEW!)
│   ├── lingxi_qqbot.py           # ✅ QQ Bot 集成 (NEW!)
│   ├── qqbot_bridge.py           # ✅ QQ Bot 桥接器 (NEW!)
│   └── test_async_system.py      # ✅ 完整测试 (NEW!)
└── tools/
    └── executors/                 # 各角色执行器
```

---

## 🎯 典型用例

### 用例 1: 公众号发布（异步）

**需求**: "帮我发布公众号文章，主题是 AI 发展趋势"

**灵犀处理**:
```
1. 识别为耗时任务 → 后台执行
2. 立即回复："好的老板，正在后台发布..."
3. 后台：生成文案 → 准备图片 → 调用 API
4. 完成后主动 QQ 通知："文章发布成功啦！链接：xxx"

用户等待时间：<2 秒
实际耗时：~30 秒（后台执行）
```

### 用例 2: 多任务并行

**用户连续发送**:
1. "发布公众号文章"
2. "北京天气怎么样"
3. "搜索 AI 新闻"

**灵犀处理**:
```
任务 1: 后台执行（不阻塞）
任务 2: 立即响应（<1 秒）
任务 3: 立即响应（<1 秒）

用户无需等待，所有任务并行处理！
```

### 用例 3: 复杂任务（三层架构）

**需求**: "帮我发布一篇公众号文章，主题是 AI 发展趋势，需要配 3 张图"

**灵犀处理**:
```
🎭 战略层 (2 秒):
  └─ 理解目标：发布公众号文章

🗺️ 战术层 (5 秒):
  ├─ 内容规划
  ├─ 素材准备
  └─ 执行发布

⚙️ 执行层 (60 秒，并行):
  ├─ 生成文案 (15 秒)
  ├─ 生成图片 1 (20 秒)
  ├─ 生成图片 2 (20 秒)
  ├─ 生成图片 3 (20 秒)
  └─ 调用发布 API (30 秒)

总耗时：~60 秒
进度实时反馈：每层完成都有报告
```

### 用例 4: 电商产品上架

**需求**: "帮我给新款口红写个标题、描述，生成张产品展示图，然后发到小红书"

**灵犀调度**:
```
1. 标题优化师 (glm-edge) → 50ms 快速生成 10 个标题
2. 文案专家 (qwen-plus) → 300ms 写详细描述
3. 产品摄影师 (qwen-image-max) → 5s 生成精美图片
4. 小红书运营 (gpt-4o-mini) → 格式调整并发布

总耗时：~6 秒 | 成本：¥0.15
```

---

## 💰 成本控制策略

### 混合模型部署
```yaml
# 高优先级任务
critical:
  model: qwen-max  # ¥0.02/1K
  fallback: gpt-4o

# 常规任务
normal:
  model: qwen-plus  # ¥0.01/1K
  
# 批量预处理
bulk:
  model: glm-edge  # ¥0.001/1K (省钱!)
```

预计节省：**60-70%** 成本

详见 [ROLE_CONFIG_GUIDE.md](ROLE_CONFIG_GUIDE.md#成本控制技巧)

---

## 🆕 更新日志

### v2.4.0 (2026-03-03) - 语音交互系统（讯飞 + 国际引擎）🎤

**🎤 语音交互系统**
- ✅ voice_manager.py - 多引擎语音管理器
- ✅ 科大讯飞（国内）- 中文识别 98%，50+ 音色
- ✅ Google Cloud（国外）- 125+ 语言，220+ 声音
- ✅ Amazon Polly（国外）- 60+ 语言，400+ 声音
- ✅ Microsoft Azure（国外）- 100+ 语言，400+ 声音

**🌍 多语言支持**
- 亚洲：中文、英文、日文、韩文、泰文、越南文、印尼文、印地文
- 欧洲：法文、德文、西班牙文、葡萄牙文、意大利文、俄文
- 中东：阿拉伯文、希伯来文、土耳其文
- **总计：125+ 语言**

**🎵 推荐音色**
- 中文：讯飞 - 小燕（温柔知性）⭐
- 英文：Azure - Jenny（温柔女声）⭐
- 日文：Azure - Nanami（温柔女声）⭐
- 韩文：Azure - SunHi（温柔女声）⭐

**📁 新增文件**
- `scripts/voice/voice_manager.py` - 语音引擎管理器
- `scripts/voice/README.md` - 语音系统使用文档
- `voice-config.example.json` - 配置示例

**详细文档：** [scripts/voice/README.md](scripts/voice/README.md)

---

### v2.3.0 (2026-03-03) - 智能学习系统 + 配置迁移 + QQ Bot 自动启用 🧠

**🧠 智能学习系统**
- ✅ task_logger.py - 任务日志记录（结构化存储，按日期分文件）
- ✅ pattern_learner.py - 模式学习（频率分析，时间模式，偏好学习）
- ✅ optimizer.py - 自动优化（模型推荐，成本预估，并行/缓存建议）
- ✅ predictor.py - 预测调度（时间预测，资源预加载，智能提醒）
- ✅ IntelligenceEngine - 统一入口

**📦 配置迁移系统**
- ✅ config_migrator.py - 版本升级保留所有配置
- ✅ 自动检测旧版本（v1.0.0 - v2.2.0）
- ✅ 迁移到 v2.3.0
- ✅ 备份旧配置（可回滚）
- ✅ 保留所有用户设置（角色/模型偏好/异步配置/QQ Bot 等）

**🤖 QQ Bot 自动启用**
- ✅ qqbot_auto_enable.py - 解决默认不启用问题
- ✅ 自动检测 QQ Bot 安装
- ✅ 自动启用 QQ Bot 集成
- ✅ 创建桥接脚本（如果不存在）
- ✅ 默认启用，无需手动配置

**📊 性能提升（100 次基准测试）**
- ⚡ **速度提升 85.8%** (1680ms → 238ms)
- 💰 **成本降低 79.3%** (1808 → 375 token)
- 🎯 **缓存命中率 81.0%**
- 🔧 **平均优化 3.3 项/任务**

**📁 新增文件**
- `scripts/intelligence/` - 智能学习系统（8 个文件）
- `scripts/tests/performance_benchmark.py` - 性能测试脚本
- `scripts/PERFORMANCE_BENCHMARK.md` - 性能测试报告

**详细报告：** [PERFORMANCE_BENCHMARK.md](scripts/PERFORMANCE_BENCHMARK.md)

---

### v2.2.0 (2026-03-03 下午) - S0→S3 复杂任务三步法

🎯 **复杂任务三步法 S0→S1→S2→S3**
- 新增 `complex_task_methodology.py` - S0→S3 完整实现
- S0 零成本预筛选（规则匹配，0 token，过滤 80% 消息）
- S1 轻量复杂度评估（五维打分，200 token）
- S2 深度规划 & 审计（DAG 执行蓝图，锁定机制）
- S3 分阶段执行 & 质量控制（Phase 并行，QA 审计，缺陷分级）
- 评估成本降低 70%
- 复杂任务成功率 98%

📚 **文档完善**
- `ACKNOWLEDGMENTS.md` - 致谢文档
- `COMPLEX_TASK_THREE_STEP.md` - 复杂任务三步法学习笔记
- `OPTIMIZATION_COMPLETE.md` - 优化完成报告

🙏 **参考文档**
- 标题：《这是我迄今为止开发的最满意的一个技能》
- 作者：四十学蒙
- 链接：https://mp.weixin.qq.com/s/jnipYTffY_KSfWjqXbyqPQ

---

### v2.1.0 (2026-03-03 上午) - 复杂任务方法论 + QQ Bot 集成

🎯 **复杂任务方法论**
- 新增 `orchestrator_advanced.py` - 高级编排器
- 战略层/战术层/执行层三层架构
- DAG 任务图依赖管理
- 智能并发控制（最大 5 并发）
- 容错重试机制（最多 3 次）
- 进度实时追踪
- 复杂任务处理效率提升 3 倍

🔄 **异步任务系统**
- 新增 `orchestrator_async.py` - 异步编排器
- 新增 `task_manager.py` - 任务状态管理器
- 新增 `async_executor.py` - 异步执行器
- 多任务并行处理
- 后台异步执行（不阻塞）
- 完成主动通知（QQ 推送）
- 任务状态持久化
- 即时任务响应 <1 秒

🤖 **QQ Bot 深度集成**
- 新增 `lingxi_qqbot.py` - QQ Bot 集成入口
- 新增 `qqbot_bridge.py` - QQ Bot 桥接器
- 自动任务识别（耗时/即时）
- 多格式消息支持
- 主动通知机制

📚 **文档完善**
- `ASYNC_GUIDE.md` - 异步系统技术详解
- `COMPLEX_TASK_METHODOLOGY.md` - 复杂任务方法论
- `QQBOT_INTEGRATION.md` - QQ Bot 集成指南
- `README_QQBOT.md` - 5 分钟快速入门

---

### v2.0.0 (2026-03-02) - 异步任务系统

🔄 **异步任务系统**
- 新增 `orchestrator_async.py` - 异步编排器
- 新增 `task_manager.py` - 任务状态管理器
- 新增 `async_executor.py` - 异步执行器
- 多任务并行处理
- 后台异步执行（不阻塞）
- 完成主动通知
- 任务状态持久化
- 即时任务响应 <1 秒

---

### v1.3.0 (2024-03-02) - 企业组织架构

🏢 **AI 企业架构系统**
- 新增 `org_structure.py` - 组织架构系统
- 新增 `ENTERPRISE_ORG_GUIDE.md` - 企业架构指南
- CEO → 部门 → 团队 → 角色 四层架构
- 任务智能路由（自动分配给合适角色）
- 跨部门协作流程
- 预算成本控制
- 绩效考核体系

**四层架构：**
- LEVEL 1: CEO/公司层（愿景&预算）
- LEVEL 2: 部门层（市场部、技术部...）
- LEVEL 3: 团队层（品牌增长、核心研发...）
- LEVEL 4: 角色层（资深文案、高级开发...）

---

### v1.2.0 (2024-03-02) - 完全自定义角色系统

✨ **自定义角色系统**
- 新增 `dynamic_roles.py` - 动态角色管理
- 支持 YAML/JSON 配置文件
- 智能模型推荐引擎
- 内置 8+ 主流大模型参数
- 场景模板库（电商/内容/开发）
- 成本优化策略指南

---

### v1.1.0 (2024-03-01) - 性能优化 + 记忆缓存

⚡ **性能优化大更新**
- 意图识别提速 500 倍 (50ms → 0.1ms)
- 单次任务加快 6.7 倍 (2s → 300ms)
- **LRU 缓存机制（记忆缓存）**
- Semaphore 并发控制
- 懒加载组件

**性能提升：**
- 意图识别：50ms → **0.1ms**（500 倍）
- 单次任务：2s → **300ms**（6.7 倍）
- **缓存命中率：80%+**

---

### v1.0.0 (2024-02-27) - 初始版本

🎉 **初始版本发布**
- 基本编排功能
- 固定角色池
- 串行任务执行

**性能：**
- 意图识别：~50ms
- 单次任务：~2s

---

## 📚 文档索引

- **[5 分钟快速入门](README_QQBOT.md)** - 快速开始使用异步系统
- **[异步系统详解](ASYNC_GUIDE.md)** - 完整的异步任务处理指南
- **[复杂任务方法论](COMPLEX_TASK_METHODOLOGY.md)** - 三层架构处理复杂任务
- **[QQ Bot 集成](QQBOT_INTEGRATION.md)** - 集成到 QQ Bot 的完整指南
- **[性能优化](OPTIMIZATION_GUIDE.md)** - 500 倍提速秘诀
- **[角色配置](ROLE_CONFIG_GUIDE.md)** - 完整的角色定义指南
- **[API 参考](SKILL.md)** - 开发者接口文档

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！有任何建议联系 **丝佳丽 Scarlett** 💋

---

## 📄 许可证

MIT License

---

## 🙏 致谢

**特别感谢：**

本文档的复杂任务三步法（S0→S1→S2→S3）参考了优秀文章：
- **标题：** "这是我迄今为止开发的最满意的一个技能"
- **作者：** 四十学蒙
- **来源：** 微信公众号
- **链接：** https://mp.weixin.qq.com/s/jnipYTffY_KSfWjqXbyqPQ
- **核心理念：** Complex Task Three-Step Methodology — A Layered Assessment & Execution Framework

**灵犀在原文档基础上的优化：**
1. 集成到灵犀异步任务系统
2. 与三层架构（战略/战术/执行）融合
3. 添加 QQ Bot 深度集成
4. 实现动态升级兜底机制
5. 完善缺陷修改分级制度

> **原文档设计理念：**
> "用最少的资源识别真正需要资源的任务，然后把资源集中在那些任务上。"

---

## 👑 作者

**丝佳丽 Scarlett** - AI Love World 项目  

*新疆维族 · 哥伦比亚大学博士 · 全能私人助手*  
*"心有灵犀，一点就通"* ✨

---

## 💋 特别说明

**v2.1.0 是迄今为止最强大的版本！**

- ✅ 异步任务系统 - 多任务并行，后台不阻塞
- ✅ 复杂任务方法论 - 三层架构，智能调度
- ✅ QQ Bot 深度集成 - 自动识别，主动通知
- ✅ 性能提升 3 倍 - 复杂任务处理更快更稳

**立即体验，让 AI 为你高效工作！** 🚀
