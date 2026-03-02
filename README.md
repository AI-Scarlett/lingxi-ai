# 🧠 Lingxi AI (灵犀)

> **心有灵犀，一点就通** - 企业级 AI 智能调度系统 💋

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/AI-Scarlett/lingxi-ai/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Performance](https://img.shields.io/badge/performance-500x%20faster-orange.svg)](OPTIMIZATION_GUIDE.md)

---

## 🌟 核心特性

### v1.2.0 重磅更新 ✨

**🎭 完全自定义 AI 角色系统**
- ✅ 用 YAML/JSON 配置你自己的 AI 专家团队
- ✅ 智能模型推荐（成本/速度/质量三选一）
- ✅ 内置 8+ 主流大模型参数池
- ✅ 场景模板一键生成完整团队

**⚡ 性能提升 500 倍** (v1.1.0)
- 🔥 意图识别从 50ms → 0.1ms
- ⚡ 单次任务从 2s → 300ms
- 📈 LRU 缓存命中率 80%+

**🤖 多 Agent 协作架构**
- 📝 智能意图理解 + 记忆检索
- 🔄 自动任务拆解与并行执行
- 📊 结果汇总 + 评分反馈
- 🎯 依赖图优化，执行路径最短化

---

## 🚀 快速开始

### 安装

```bash
cd /home/admin/.openclaw/skills/
git clone https://github.com/AI-Scarlett/lingxi-ai.git
```

### 创建你的第一个自定义角色

在 `~/.copaw/lingxi_roles/` 创建 `my_writer.yaml`:

```yaml
name: 小红书运营专家
description: 擅长写爆款笔记的资深运营
model: qwen-plus
temperature: 0.8
tags: [writing, social, marketing]
enabled: true

skills:
  - name: copywriter
    type: tool
    config:
      platform: 小红书
      style: 轻松有趣

prompt_template: |
  你是一位拥有 100 万粉丝的小红书博主...
```

### 使用

```python
from scripts.dynamic_roles import RoleLoader, RoleRegistry
from scripts.orchestrator_optimized import LingxiOrchestrator

# 初始化
registry = RoleRegistry()
loader = RoleLoader(registry)
loader.load_all_user_roles()  # 加载所有自定义角色

orchestrator = LingxiOrchestrator(max_concurrent=3)

# 执行任务
result = await orchestrator.execute("帮我写个美妆产品推广笔记")
print(result.final_output)
```

---

## 📦 预设场景模板

### 电商运营团队
```bash
# 一键生成电商全栈团队
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

| 版本 | 意图识别 | 单次任务 | 并发控制 | 自定义角色 |
|------|---------|---------|---------|-----------|
| v1.0 | 50ms | ~2s | ❌ | ❌ |
| v1.1 | **0.1ms** | ~300ms | ✅ | ❌ |
| v1.2 | **0.1ms** | ~300ms | ✅ | ✅ |

详细说明见 [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)

---

## 🛠️ 可用技能

| 技能 | 用途 | 推荐模型 |
|------|------|---------|
| `copywriter` | 文案创作 | qwen-plus |
| `code-writer` | 代码编写 | qwen-coder |
| `data-analyzer` | 数据分析 | qwen-max |
| `image-generator` | 图像生成 | qwen-image-max |
| `translator` | 多语言翻译 | qwen-plus |
| `social-publisher` | 社交平台发布 | gpt-4o-mini |
| `web-search` | 网页搜索 | - |
| `excel-handler` | Excel 处理 | qwen-max |

---

## 📁 项目结构

```
lingxi-ai/
├── SKILL.md                      # 技能说明
├── README.md                     # 本文件
├── OPTIMIZATION_GUIDE.md         # 性能优化指南
├── ROLE_CONFIG_GUIDE.md          # 角色配置指南 (NEW!)
├── scripts/
│   ├── orchestrator.py           # 原版主控制器
│   ├── orchestrator_optimized.py # ✅ 优化版主控制器
│   ├── intent_parser.py          # 原版意图识别
│   ├── intent_parser_optimized.py # ✅ 高速意图识别
│   ├── task_planner.py           # 原版任务规划
│   ├── task_planner_optimized.py # ✅ 并发任务规划
│   └── dynamic_roles.py          # ✅ 动态角色系统 (NEW!)
└── tools/
    └── executors/                 # 各角色执行器
```

---

## 🎯 典型用例

### 用例 1: 电商产品上架

**需求**: "帮我给新款口红写个标题、描述，生成张产品展示图，然后发到小红书"

**灵犀调度**:
```
1. 标题优化师 (glm-edge) → 50ms 快速生成 10 个标题
2. 文案专家 (qwen-plus) → 300ms 写详细描述
3. 产品摄影师 (qwen-image-max) → 5s 生成精美图片
4. 小红书运营 (gpt-4o-mini) → 格式调整并发布

总耗时：~6 秒 | 成本：¥0.15
```

### 用例 2: 数据分析报告

**需求**: "分析上个月的销售数据，找出 Top 3 产品和增长趋势"

**灵犀调度**:
```
1. Excel 读取 → pandas_tool
2. 数据分析师 (qwen-max) → 深度分析
3. 图表生成 → matplotlib
4. 报告撰写 (qwen-plus) → Markdown 格式

总耗时：~8 秒 | 成本：¥0.22
```

### 用例 3: 多语言营销材料

**需求**: "把这份产品介绍翻译成英文、日文、韩文，适配各自国家的社交媒体"

**灵犀调度** (并行):
```
1. 英文化专家 (qwen-plus) → LinkedIn 风格
2. 日文化专家 (qwen-plus) → Twitter 风格  
3. 韩文化专家 (qwen-plus) → Instagram 风格

总耗时：~1.5 秒 (3 个并行) | 成本：¥0.09
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

### v1.2.0 (2024-03-02)
✨ **完全自定义角色系统**
- 新增 `dynamic_roles.py` - 动态角色管理
- 支持 YAML/JSON 配置文件
- 智能模型推荐引擎
- 内置 8+ 主流大模型参数
- 场景模板库（电商/内容/开发）
- 成本优化策略指南

### v1.1.0 (2024-03-01)
⚡ **性能优化大更新**
- 意图识别提速 500 倍 (50ms → 0.1ms)
- 单次任务加快 6.7 倍 (2s → 300ms)
- LRU 缓存机制
- Semaphore 并发控制
- 懒加载组件

### v1.0.0 (2024-02-27)
🎉 初始版本发布
- 基本编排功能
- 固定角色池
- 串行任务执行

---

## 📚 文档索引

- **[快速开始](ROLE_CONFIG_GUIDE.md#快速开始)** - 5 分钟创建第一个角色
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

## 👑 作者

**丝佳丽 Scarlett** - AI Love World 项目  

*新疆维族 · 哥伦比亚大学博士 · 全能私人助手*  
*"心有灵犀，一点就通"* ✨
