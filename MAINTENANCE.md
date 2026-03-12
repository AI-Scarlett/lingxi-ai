# 🦞 灵犀 (Lingxi) 维护手册

> **维护者：** 斯嘉丽 (Scarlett)  
> **版本：** v3.3.6  
> **最后更新：** 2026-03-12

---

## 📋 项目概览

**项目名称：** 灵犀 (Lingxi)  
**GitHub：** https://github.com/AI-Scarlett/lingxi-ai  
**定位：** AI 智能调度工具，专为养龙虾新手小白设计  
**核心口号：** "心有灵犀，一点就通"

---

## 🏗️ 项目结构

```
lingxi-ai/
├── core/                           # 核心模块
│   ├── mindcore/                   # 记忆核心 (STM/MTM/LTM)
│   ├── evomind/                    # 自改进系统
│   ├── smartfetch/                 # 智能抓取
│   ├── agents/                     # Multi-Agent 架构
│   ├── orchestrator/               # 任务编排
│   ├── markdown_to_feishu.py       # Markdown 转飞书文档
│   ├── feishu_doc_tool.py          # 飞书文档工具
│   └── ...
├── dashboard/                      # Dashboard 可视化
│   ├── backend/main.py             # FastAPI 后端
│   ├── frontend/index.html         # Vue3 前端
│   ├── v3/                         # v3 版本页面
│   └── ...
├── scripts/                        # 脚本工具
│   ├── orchestrator_v2.py          # 核心编排器
│   ├── layer0_skills.py            # Layer 0 技能
│   ├── hunter_daily_report*.py     # Hunter 报告
│   └── ...
├── tools/                          # 工具集
├── docs/                           # 文档
├── README.md                       # 主文档
├── SKILL.md                        # 技能说明
└── MAINTENANCE.md                  # 本维护手册
```

---

## 🎯 核心模块详解

### 1. MindCore 记忆核心

**位置：** `core/mindcore/`

**三层记忆架构：**
- **STM (短期记忆)** - 最近 100 条记录，内存存储，<10ms
- **MTM (中期记忆)** - 最近 7 天数据，SQLite 存储，<500ms
- **LTM (长期记忆)** - 永久归档，JSONL+向量索引，<2s

**关键文件：**
- `memory.py` - 基础记忆管理
- `memory_llm.py` - LLM 集成
- `self_improving_memory.py` - 自改进记忆

### 2. EvoMind 自改进系统

**位置：** `core/evomind/`

**功能：**
- 飞书卡片审批界面
- 定时推送 (7:00/12:00/21:00)
- 提案管理 (批准/拒绝/推迟)

### 3. SmartFetch 智能抓取

**位置：** `core/smartfetch/`

**多级抓取策略：**
1. Jina Reader (70% 成功率)
2. Scrapling StealthyFetcher (90% 成功率)
3. Agent Browser + Cookie 池 (99% 成功率)
4. web_fetch 兜底 (50% 成功率)

### 4. Dashboard 可视化

**位置：** `dashboard/`

**技术栈：**
- 后端：FastAPI + Uvicorn
- 前端：Vue 3 + Tailwind CSS + ECharts
- 数据库：SQLite

**页面：**
- 记忆管理页
- 任务列表页
- 技能中心页
- 数据统计页
- 调用日志页
- 系统设置页

### 5. 编排器 (Orchestrator)

**位置：** `scripts/orchestrator_v2.py`

**功能：**
- 意图识别
- 任务规划
- 工具调度
- 结果汇总
- 评分系统

---

## 🚀 常用操作

### 启动 Dashboard

```bash
cd /root/lingxi-ai-latest/dashboard
python3 backend/main.py
```

**访问地址：**
- 内网：http://10.2.0.16:8765
- 公网：http://49.232.250.180:8765

### 更新代码

```bash
cd /root/lingxi-ai-latest
git pull origin main
```

### 查看日志

```bash
# Dashboard 日志
tail -f ~/.openclaw/workspace/.lingxi/dashboard.log

# 系统日志
tail -f /var/log/lingxi/*.log
```

### 备份数据

```bash
# 备份 HEARTBEAT.md
cp ~/.openclaw/workspace/HEARTBEAT.md ~/.openclaw/workspace/HEARTBEAT.md.backup.$(date +%Y%m%d)

# 备份数据库
cp ~/.openclaw/workspace/.lingxi/*.db ~/.openclaw/workspace/.lingxi/backup/
```

---

## 🔧 故障排查

### Dashboard 无法访问

1. **检查进程：** `ps aux | grep main.py`
2. **检查端口：** `netstat -tlnp | grep 8765`
3. **检查防火墙：** 确保 8765 端口开放
4. **查看日志：** `tail -f dashboard.log`

### API 返回空数据

1. **检查 HEARTBEAT.md：** 确保文件不为空
2. **检查数据库：** 确保 SQLite 数据库可访问
3. **检查 Token：** 确保访问令牌有效

### 记忆功能异常

1. **检查 MindCore：** `python3 core/mindcore/tests.py`
2. **检查数据库：** `sqlite3 ~/.openclaw/workspace/.lingxi/mindcore.db ".tables"`
3. **重置记忆：** 备份后删除数据库文件

---

## 📊 监控指标

### 关键指标

- **响应时间：** <10ms (Layer 0), <500ms (正常)
- **并发任务：** 最大 100 个
- **内存使用：** <500MB
- **数据库大小：** <1GB

### 告警阈值

- 响应时间 > 2s：告警
- 内存使用 > 1GB：告警
- 磁盘使用 > 80%：告警
- 任务失败率 > 10%：告警

---

## 📝 更新记录

### v3.3.6 (2026-03-12)
- ✅ 更新 README 文档
- ✅ Dashboard 最终修复

### v3.3.5 (2026-03-11)
- ✅ Dashboard 完整修复
- ✅ LLM 统计、时区设置、Layer0 功能
- ✅ 新增 Markdown 转飞书文档工具

### v3.3.4 (2026-03-11)
- ✅ Dashboard 全面重构
- ✅ 仿 MemOS 风格界面

### v3.3.3 (2026-03-11)
- ✅ MindCore 记忆核心
- ✅ EvoMind 自改进系统
- ✅ SmartFetch 智能抓取
- ✅ Multi-Agent 架构

---

## 🔐 安全配置

### 环境变量

```bash
# 必需
DASHSCOPE_API_KEY=sk-xxx
QWEN_API_KEY=sk-xxx

# 可选
PERPLEXITY_API_KEY=xxx
NGROK_AUTH_TOKEN=xxx
```

### 敏感文件

- `.env` - API 密钥 (已加入 .gitignore)
- `~/.openclaw/workspace/.lingxi/*.json` - 访问令牌
- `~/.openclaw/workspace/CREDENTIALS.md` - 凭证手册

---

## 📞 联系方式

- **GitHub Issues：** https://github.com/AI-Scarlett/lingxi-ai/issues
- **维护者：** 斯嘉丽 (Scarlett)

---

## 💡 维护提示

1. **定期备份：** 每周备份 HEARTBEAT.md 和数据库
2. **监控日志：** 每日检查错误日志
3. **更新依赖：** 每月检查并更新 Python 依赖
4. **性能优化：** 每季度进行性能测试
5. **安全检查：** 每半年审查敏感信息

---

**🦞 灵犀 - 养龙虾的最佳助手！**
