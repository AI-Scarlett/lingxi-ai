# 🚀 灵犀数据看板 - 使用指南

**Lingxi Dashboard - 实时监控任务执行情况**

---

## 📋 功能特性

### 核心功能
- ✅ **实时任务监控** - 查看正在执行的任务
- ✅ **执行步骤追踪** - 任务在哪一步（接收→分析→拆解→执行→汇总）
- ✅ **LLM 调用记录** - 是否调用、调用哪个模型、token 消耗
- ✅ **错误追踪** - 报错信息、错误类型、发生位置
- ✅ **性能指标** - 响应时间、执行时间、等待时间
- ✅ **历史记录** - 查询历史任务记录
- ✅ **实时推送** - WebSocket 实时更新
- ✅ **外网访问** - 支持 ngrok/Cloudflare Tunnel

---

## 🚀 快速开始

### 1. 启动看板服务

```bash
cd /root/.openclaw/skills/lingxi
bash scripts/start_dashboard.sh
```

### 2. 访问看板

打开浏览器访问：
```
http://localhost:8765
```

### 3. 外网访问（可选）

```bash
# 启动外网隧道
bash scripts/expose_dashboard.sh
```

选择隧道工具：
- **ngrok** - 稳定，需要账号
- **Cloudflare Tunnel** - 推荐，免费
- **localtunnel** - 简单，临时使用

---

## 📊 API 接口

### 获取统计数据
```bash
curl http://localhost:8765/api/stats?hours=24
```

### 获取任务列表
```bash
curl http://localhost:8765/api/tasks?limit=50
```

### 获取任务详情
```bash
curl http://localhost:8765/api/tasks/{task_id}
```

### 获取最近错误
```bash
curl http://localhost:8765/api/errors?limit=20
```

### 健康检查
```bash
curl http://localhost:8765/api/health
```

---

## 🔌 WebSocket 实时推送

### 连接
```javascript
const ws = new WebSocket('ws://localhost:8765/ws');
```

### 消息类型

**任务开始:**
```json
{
  "type": "task_started",
  "task_id": "task_20260309014500",
  "task": {...}
}
```

**阶段更新:**
```json
{
  "type": "stage_update",
  "task_id": "task_20260309014500",
  "stage": "executing",
  "data": {...}
}
```

**任务完成:**
```json
{
  "type": "task_completed",
  "task_id": "task_20260309014500",
  "result": {...}
}
```

**任务错误:**
```json
{
  "type": "task_error",
  "task_id": "task_20260309014500",
  "error_type": "TimeoutError",
  "error_message": "..."
}
```

---

## 🔧 集成到灵犀主流程

### Python 调用示例

```python
from dashboard.server import (
    record_task_start,
    record_task_stage,
    record_task_complete,
    record_task_error
)

# 1. 记录任务开始
await record_task_start(
    task_id="task_123",
    user_id="user_456",
    channel="feishu",
    user_input="生成 Hunter 报告"
)

# 2. 记录阶段更新
await record_task_stage(
    task_id="task_123",
    stage="intent_analysis",
    data={"intent_types": ["content_creation"]}
)

await record_task_stage(
    task_id="task_123",
    stage="executing",
    data={"subtask_count": 2}
)

# 3. 记录 LLM 调用
await record_task_stage(
    task_id="task_123",
    stage="llm_call",
    data={
        "llm_called": True,
        "llm_model": "qwen-plus",
        "llm_tokens_in": 150,
        "llm_tokens_out": 300
    }
)

# 4. 记录任务完成
await record_task_complete(
    task_id="task_123",
    result={
        "response_time_ms": 50.5,
        "execution_time_ms": 1250.3,
        "final_output": "...",
        "score": 9.5
    }
)

# 5. 记录任务错误
await record_task_error(
    task_id="task_123",
    error_type="TimeoutError",
    error_message="LLM 调用超时",
    traceback="..."
)
```

---

## 📁 数据库结构

### tasks 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 任务 ID |
| user_id | TEXT | 用户 ID |
| channel | TEXT | 渠道 (feishu/qqbot 等) |
| user_input | TEXT | 用户输入 |
| status | TEXT | 状态 (pending/processing/completed/failed) |
| stage | TEXT | 阶段 (received/intent_analysis/...) |
| created_at | REAL | 创建时间戳 |
| started_at | REAL | 开始时间戳 |
| completed_at | REAL | 完成时间戳 |
| response_time_ms | REAL | 首次响应时间 |
| execution_time_ms | REAL | 总执行时间 |
| wait_time_ms | REAL | 等待时间 |
| llm_called | INTEGER | 是否调用 LLM |
| llm_model | TEXT | LLM 模型名称 |
| llm_tokens_in | INTEGER | 输入 tokens |
| llm_tokens_out | INTEGER | 输出 tokens |
| llm_cost | REAL | LLM 成本 |
| intent_types | TEXT | 意图类型 (JSON) |
| subtask_count | INTEGER | 子任务数量 |
| subtasks | TEXT | 子任务详情 (JSON) |
| error_type | TEXT | 错误类型 |
| error_message | TEXT | 错误消息 |
| error_traceback | TEXT | 错误堆栈 |
| final_output | TEXT | 最终输出 |
| score | REAL | 评分 |

---

## 🎯 看板界面说明

### 顶部统计卡片
- **总任务数** - 24 小时内任务总数
- **LLM 调用次数** - 调用大模型的次数
- **平均响应时间** - 首次响应平均耗时
- **错误率** - 失败任务占比
- **LLM 成本** - 总 token 成本
- **输入 Tokens** - 总输入 token 数

### 任务列表
- 任务 ID
- 用户输入
- 状态标签（处理中/已完成/失败）
- 渠道标识
- 执行时间
- LLM 调用标识
- 模型名称
- 执行阶段指示器

### 错误面板
- 错误类型
- 错误消息
- 发生时间

---

## 🔐 安全建议

### 生产环境部署

1. **启用认证**
   - 添加 API Key 验证
   - WebSocket 连接认证

2. **限制访问**
   - IP 白名单
   - 内网部署 + 隧道访问

3. **数据加密**
   - HTTPS/WSS
   - 敏感数据加密存储

4. **日志审计**
   - 记录所有访问日志
   - 定期审计异常访问

---

## 🛠️ 故障排查

### 服务无法启动

```bash
# 检查端口占用
lsof -i :8765

# 查看日志
tail -f /tmp/lingxi_dashboard.log
```

### WebSocket 连接失败

```bash
# 检查防火墙
ufw status

# 测试连接
curl http://localhost:8765/api/health
```

### 数据库错误

```bash
# 重置数据库
rm ~/.openclaw/workspace/.lingxi/dashboard.db

# 重启服务
bash scripts/start_dashboard.sh
```

---

## 📈 性能优化

### 数据库优化
- 定期清理旧数据（>30 天）
- 添加索引（已默认添加）
- 使用连接池

### WebSocket 优化
- 限制连接数
- 消息去重
- 心跳检测

### 前端优化
- 减少刷新频率（默认 5 秒）
- 虚拟滚动（大数据量）
- 缓存静态资源

---

## 📝 更新日志

### v1.0.0 (2026-03-09)
- ✅ 初始版本发布
- ✅ 实时任务监控
- ✅ WebSocket 推送
- ✅ 外网访问支持
- ✅ 错误追踪
- ✅ 性能指标

---

## 💡 未来计划

- [ ] 用户认证系统
- [ ] 自定义告警规则
- [ ] 数据导出功能
- [ ] 多维度数据分析
- [ ] 移动端适配
- [ ] 多语言支持

---

**作者:** 斯嘉丽 Scarlett  
**日期:** 2026-03-09  
**版本:** v1.0.0
