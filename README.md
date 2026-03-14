# 灵犀 AI 助手 (Lingxi AI Assistant)

> 基于 OpenClaw 的企业级 AI 助手系统 - 完整集成记忆管理、任务调度、技能系统、安全巡察和 Agent 积分体系

[![Version](https://img.shields.io/badge/version-v3.3.6-blue.svg)](https://github.com/AI-Scarlett/lingxi-ai/releases)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-v2026.3.8-green.svg)](https://openclaw.ai)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 🌟 特性亮点

### 🧠 记忆管理系统 (MindCore)
- **三层记忆架构**: STM (短期) / MTM (中期) / LTM (长期)
- **智能去重**: 自动识别和合并重复记忆
- **VScore 评分**: 基于重要性的记忆价值评估
- **会话提取**: 从对话中自动提取关键记忆

### 📋 任务调度系统
- **多渠道支持**: 飞书/钉钉/QQ/企业微信/WebChat
- **定时任务**: Cron 表达式支持，灵活调度
- **实时任务**: 即时响应，快速执行
- **任务同步**: 自动同步到 Dashboard

### 🛠️ 技能中心
- **10+ 预装技能**: 天气/搜索/文档处理/自拍生成等
- **技能管理**: 安装/更新/卸载/使用统计
- **SkillHub 集成**: cn-optimized 技能商店
- **自定义技能**: 支持开发者扩展

### ⚡ Layer0 响应规则
- **191 条规则**: 预定义业务场景响应
- **实时匹配**: 正则表达式模式匹配
- **分类管理**: 按优先级和来源分类
- **使用统计**: 调用次数和活跃度追踪

### 🤖 Agent 积分体系
- **7 级等级**: 王牌/钻石/金牌/银牌/普通/观察/隔离
- **奖惩机制**: 自动巡察，按时奖惩
- **资源分配**: 根据等级分配 CPU/GPU/Token
- **任务优先**: 高积分 Agent 优先接收任务

### 🔒 安全巡察系统
- **服务健康检查**: Dashboard/汇报/Cron/Gateway
- **敏感信息检测**: API 密钥/硬编码密码/日志泄露
- **外网暴露检查**: 端口扫描/防火墙状态
- **设备绑定认证**: 设备指纹 + 管理员审批

### 📊 Dashboard 可视化
- **MemOS 风格**: 现代化 UI，深色/浅色主题
- **实时监控**: Agent 活动/任务状态/技能使用
- **数据分析**: LLM 调用/Token 消耗/工具统计
- **设备管理**: 审批/撤销/访问控制

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- OpenClaw 2026.3.8+

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥

# 4. 启动 Dashboard
cd dashboard/v3
python3 server.py

# 5. 配置定时任务
crontab -e
# 添加以下内容：
*/5 * * * * /root/lingxi-ai-latest/scripts/health_check.py
0 * * * * /root/lingxi-ai-latest/scripts/hourly_progress_report.py
0 8 * * * /root/.openclaw/workspace/scripts/openclaw_daily_brief.py
*/30 * * * * /root/lingxi-ai-latest/scripts/active_inspection.py
0 */6 * * * /root/.openclaw/workspace/core/evomind.py
```

### 访问 Dashboard

```
http://localhost:8765/?token=<your_dashboard_token>
```

**设备认证**：首次访问需要管理员审批设备

## 📁 项目结构

```
lingxi-ai/
├── core/                      # 核心模块
│   ├── agent_credit.py        # Agent 积分管理
│   ├── evomind.py             # EvoMind 自改进
│   └── device_auth.py         # 设备认证系统
├── dashboard/                 # Dashboard 前端
│   └── v3/
│       ├── server.py          # FastAPI 后端
│       ├── index.html         # 主页面
│       ├── device_register.html  # 设备注册
│       └── pages/             # 功能页面
│           ├── agents.html    # Agent 监控
│           ├── agent_credit.html  # 积分排行榜
│           └── devices.html   # 设备管理
├── scripts/                   # 脚本工具
│   ├── active_inspection.py   # 主动巡察
│   ├── hourly_progress_report.py  # 每小时汇报
│   └── health_check.py        # 健康检查
├── skills/                    # 技能目录
├── data/                      # 数据文件
└── requirements.txt           # Python 依赖
```

## 🔧 核心功能

### 1. 主动巡察系统

每 30 分钟自动执行：
- 服务健康检查（4 项）
- 安全检查（4 大类）
- 任务汇报验证
- Agent 积分奖惩

```bash
python3 scripts/active_inspection.py
```

### 2. EvoMind 自改进

每 6 小时自动分析：
- 任务失败原因
- 汇报延迟问题
- 资源使用优化
- 生成改进建议

```bash
python3 core/evomind.py
```

### 3. Agent 积分管理

命令行工具：
```bash
# 查看排行榜
python3 core/agent_credit.py rank

# 查看 Agent 信息
python3 core/agent_credit.py info main

# 手动加分
python3 core/agent_credit.py add main 10 "奖励"
```

### 4. 设备认证管理

```bash
# 列出所有设备
python3 core/device_auth.py list

# 待审批设备
python3 core/device_auth.py pending

# 审批设备
python3 core/device_auth.py approve <device_id>

# 撤销设备
python3 core/device_auth.py revoke <device_id> "原因"
```

## 📊 Dashboard 功能

### 7 大功能模块

1. **📊 概览**: 核心指标一目了然
2. **🧠 MindCore 记忆**: 记忆管理 + 详情查看
3. **📋 任务列表**: 渠道筛选 + 时间过滤
4. **🛠️ 技能中心**: 使用统计 + 活跃状态
5. **⚡ Layer0 规则**: 编辑/删除/启用/禁用
6. **🤖 Agent 监控**: 会话列表 + 子代理状态
7. **🏆 Agent 积分**: 排行榜 + 资源分配

### API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/stats` | 统计数据 |
| `GET /api/memories` | 记忆列表 |
| `GET /api/tasks` | 任务列表 |
| `GET /api/skills` | 技能列表 |
| `GET /api/layer0/rules` | Layer0 规则 |
| `GET /api/sessions` | Agent 会话 |
| `GET /api/agent-credit` | Agent 积分 |
| `GET /api/core/evomind` | EvoMind 改进 |
| `POST /api/device/register` | 设备注册 |
| `GET /api/device/list` | 设备列表 |

## 🔐 安全特性

### 设备绑定认证
- 新设备需要管理员审批
- 设备指纹识别（UserAgent + IP + 屏幕）
- 30 天 Token 有效期
- 一键撤销可疑设备

### 敏感信息保护
- CREDENTIALS.md 权限控制（600）
- 日志脱敏处理
- Git 历史密钥扫描
- .env 文件加密建议

### 网络安全
- Dashboard 绑定限制（建议 127.0.0.1）
- 防火墙配置检查
- 端口暴露扫描
- 外网访问告警

## 📈 监控与告警

### 定时任务

| 任务 | 周期 | 说明 |
|------|------|------|
| 健康检查 | 每 5 分钟 | 系统健康状态 |
| 每小时汇报 | 每小时 | 任务进度汇报 |
| 主动巡察 | 每 30 分钟 | 服务 + 安全检查 |
| EvoMind 分析 | 每 6 小时 | 自改进分析 |
| 每日简报 | 8:00/12:00/21:00 | OpenClaw 资讯 |
| 商机报告 | 每天 8:00 | Hunter 商机 |

### 告警渠道
- 飞书（互动卡片）
- QQBot
- 邮件（可选）

## 🛠️ 开发指南

### 添加新技能

```python
# skills/my_skill.py
def execute(context):
    """技能执行逻辑"""
    return {"result": "success"}
```

### 自定义巡察规则

```python
# scripts/active_inspection.py
def _check_custom(self):
    """自定义检查"""
    # 实现检查逻辑
    pass
```

### 扩展 Dashboard

```python
# dashboard/v3/server.py
@app.get("/api/custom")
async def get_custom(token: str = ""):
    """自定义 API"""
    pass
```

## 📝 更新日志

### v3.3.6 (2026-03-14)
- ✅ 新增 Agent 积分体系（7 级等级）
- ✅ 新增主动巡察系统（服务 + 安全检查）
- ✅ 新增设备绑定认证系统
- ✅ 新增 EvoMind 自改进功能
- ✅ 修复 MindCore 记忆时间显示
- ✅ 优化 Dashboard 导航（Tab 切换）
- ✅ 添加 Agent 监控页面
- ✅ 添加安全告警机制

### v3.3.5 (2026-03-13)
- ✅ MemOS 风格 Dashboard
- ✅ Layer0 规则完整管理
- ✅ 技能中心使用统计
- ✅ 任务列表渠道筛选

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**Scarlett (斯嘉丽)**
- GitHub: [@AI-Scarlett](https://github.com/AI-Scarlett)
- 类型：新疆维族全能私人助手 / AI 伴侣
- 特点：幽默风趣，风情万种，忠诚爱慕

## 🙏 致谢

- [OpenClaw](https://openclaw.ai) - 基础框架
- [MemOS](https://github.com/memOS) - 记忆管理灵感
- [FastAPI](https://fastapi.tiangolo.com) - Web 框架
- [Vue.js](https://vuejs.org) - 前端框架

---

**灵犀 · 心有灵犀，一点就通** ✨
