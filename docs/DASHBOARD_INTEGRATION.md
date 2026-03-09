# 🚀 灵犀数据看板集成指南

**将 Dashboard 集成到灵犀主流程，实现完整任务追踪**

---

## 📋 集成步骤

### 1. 修改 `lingxi.py` 入口

在 `/root/.openclaw/skills/lingxi/lingxi.py` 中添加看板集成：

```python
# 添加导入
from dashboard.server import (
    record_task_start,
    record_task_stage,
    record_task_complete,
    record_task_error
)

async def process_request(user_input: str, channel: str = None, user_id: str = None, 
                         model: str = None) -> str:
    """处理用户请求 - 带看板集成"""
    
    # 生成任务 ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
    
    try:
        # 1. 记录任务开始
        await record_task_start(task_id, user_id or "anonymous", channel or "unknown", user_input)
        
        # 2. 执行灵犀流程
        orch = get_orchestrator()
        result = await orch.execute_with_tracking(task_id, user_input, user_id)
        
        # 3. 记录任务完成
        await record_task_complete(task_id, {
            "response_time_ms": result.total_elapsed_ms,
            "execution_time_ms": result.total_elapsed_ms,
            "final_output": result.final_output[:1000],  # 限制长度
            "score": result.total_score,
            "llm_called": result.llm_called if hasattr(result, 'llm_called') else False,
            "llm_model": result.model_used if hasattr(result, 'model_used') else "",
        })
        
        return result.final_output
        
    except Exception as e:
        # 4. 记录错误
        await record_task_error(
            task_id,
            type(e).__name__,
            str(e),
            traceback.format_exc()
        )
        raise
```

---

### 2. 修改 `orchestrator_v2.py`

在 `/root/.openclaw/skills/lingxi/scripts/orchestrator_v2.py` 中添加阶段追踪：

```python
# 添加导入
from dashboard.server import record_task_stage

class SmartOrchestrator:
    async def execute_with_tracking(self, task_id: str, user_input: str, user_id: str = None):
        """带追踪的执行"""
        
        # 意图识别
        await record_task_stage(task_id, "intent_analysis", {
            "intent_types": intent['types']
        })
        
        # 任务拆解
        await record_task_stage(task_id, "task_decomposition", {
            "subtask_count": len(subtasks)
        })
        
        # 执行
        await record_task_stage(task_id, "executing")
        
        # LLM 调用（如果有）
        if llm_called:
            await record_task_stage(task_id, "llm_call", {
                "llm_called": True,
                "llm_model": selected_model,
                "llm_tokens_in": tokens_in,
                "llm_tokens_out": tokens_out
            })
        
        # 结果汇总
        await record_task_stage(task_id, "aggregating")
        
        return result
```

---

### 3. 修改 `model_router.py`

在模型选择时记录 LLM 调用：

```python
from dashboard.server import record_task_stage

async def select_model_with_tracking(task_id: str, user_input: str):
    """带追踪的模型选择"""
    selected_model = select_model(user_input)
    
    await record_task_stage(task_id, "model_selection", {
        "llm_model": selected_model
    })
    
    return selected_model
```

---

## 🔌 完整集成示例

### 修改后的 `lingxi.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) v3.0 - OpenClaw 入口
智慧调度系统，心有灵犀，一点就通
"""

import sys
import os
import asyncio
import traceback
from datetime import datetime

# 添加技能路径
SKILL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_PATH)

# 导入看板集成
from dashboard.server import (
    record_task_start,
    record_task_stage,
    record_task_complete,
    record_task_error
)

# 导入原有模块
from scripts.orchestrator_v2 import SmartOrchestrator, TaskResult, get_orchestrator as get_v2_orchestrator
from scripts.fast_response_layer import fast_respond, cache_response
from scripts.model_router import select_model, get_model_router

# 全局实例
_orchestrator = None

def get_orchestrator(max_concurrent: int = 3) -> SmartOrchestrator:
    """获取灵犀调度器实例"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SmartOrchestrator(max_concurrent=max_concurrent, enable_fast_response=True)
    return _orchestrator

async def process_request(user_input: str, channel: str = None, user_id: str = None, 
                         model: str = None) -> str:
    """
    处理用户请求 - 灵犀统一入口 (v3.0 带看板集成)
    """
    # 生成任务 ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    start_time = datetime.now()
    
    try:
        # 1. 记录任务开始
        asyncio.create_task(
            record_task_start(task_id, user_id or "anonymous", channel or "unknown", user_input)
        )
        
        # 2. 快速响应层检查
        if fast_respond(user_input).response:
            asyncio.create_task(
                record_task_complete(task_id, {
                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "llm_called": False
                })
            )
            return fast_respond(user_input).response
        
        # 3. 正常灵犀流程
        orch = get_orchestrator()
        
        # 意图识别
        asyncio.create_task(
            record_task_stage(task_id, "intent_analysis")
        )
        
        # 模型选择
        selected_model = select_model(user_input, force_model=model)
        asyncio.create_task(
            record_task_stage(task_id, "model_selection", {
                "llm_model": selected_model
            })
        )
        
        # 执行任务
        result = await orch.execute(user_input, user_id)
        
        # 4. 记录任务完成
        asyncio.create_task(
            record_task_complete(task_id, {
                "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "final_output": result[:1000] if len(result) > 1000 else result,
                "score": 10.0,
                "llm_called": True,
                "llm_model": selected_model
            })
        )
        
        return result
        
    except Exception as e:
        # 5. 记录错误
        asyncio.create_task(
            record_task_error(
                task_id,
                type(e).__name__,
                str(e),
                traceback.format_exc()
            )
        )
        raise

# ... 其余代码保持不变
```

---

## 📊 数据流

```
用户请求
    ↓
[1] record_task_start() - 创建任务记录
    ↓
[2] record_task_stage("intent_analysis") - 意图分析
    ↓
[3] record_task_stage("model_selection") - 模型选择
    ↓
[4] record_task_stage("task_decomposition") - 任务拆解
    ↓
[5] record_task_stage("executing") - 执行中
    ↓
[6] record_task_stage("llm_call") - LLM 调用（如有）
    ↓
[7] record_task_stage("aggregating") - 结果汇总
    ↓
[8] record_task_complete() - 任务完成
    ↓
[WebSocket] 实时推送到看板
    ↓
[Dashboard] 用户查看
```

---

## 🎯 关键指标追踪

### 性能指标
- **响应时间** - 从请求到首次响应
- **执行时间** - 总执行耗时
- **等待时间** - 队列等待时间

### LLM 指标
- **调用次数** - 是否调用了 LLM
- **模型名称** - 使用了哪个模型
- **Token 消耗** - 输入/输出 tokens
- **成本** - 估算成本

### 质量指标
- **任务评分** - 执行质量评分
- **错误率** - 失败任务占比
- **成功率** - 成功完成任务比例

---

## 🔐 生产环境建议

### 1. 异步处理
```python
# 使用 asyncio.create_task 异步记录，不阻塞主流程
asyncio.create_task(record_task_start(...))
```

### 2. 错误处理
```python
try:
    await record_task_start(...)
except Exception as e:
    print(f"⚠️  看板记录失败：{e}")
    # 不影响主流程
```

### 3. 数据清理
```bash
# 定期清理 30 天前的数据
sqlite3 ~/.openclaw/workspace/.lingxi/dashboard.db \
  "DELETE FROM tasks WHERE created_at < strftime('%s', 'now', '-30 days')"
```

### 4. 性能优化
```python
# 批量写入（减少数据库操作）
BATCH_SIZE = 100
task_buffer = []

async def batch_record():
    if len(task_buffer) >= BATCH_SIZE:
        await db.insert_batch(task_buffer)
        task_buffer.clear()
```

---

## 📈 监控告警

### 错误率告警
```python
# 当错误率超过阈值时告警
if error_rate > 0.1:  # 10%
    send_alert("灵犀错误率超过 10%")
```

### 响应时间告警
```python
# 当平均响应时间超过阈值时告警
if avg_response_time > 5000:  # 5 秒
    send_alert("灵犀响应时间超过 5 秒")
```

### LLM 成本告警
```python
# 当 LLM 成本超过预算时告警
if daily_llm_cost > 10:  # $10
    send_alert("灵犀 LLM 成本超过$10/天")
```

---

## 🛠️ 故障排查

### 看板无数据
```bash
# 检查服务状态
systemctl status lingxi-dashboard

# 查看日志
tail -f /tmp/lingxi_dashboard.log

# 检查数据库
sqlite3 ~/.openclaw/workspace/.lingxi/dashboard.db "SELECT COUNT(*) FROM tasks"
```

### WebSocket 断开
```bash
# 检查防火墙
ufw status

# 测试连接
curl http://localhost:8765/api/health
```

### 性能问题
```bash
# 查看慢查询
sqlite3 ~/.openclaw/workspace/.lingxi/dashboard.db \
  "PRAGMA query_plan"
```

---

**作者:** 斯嘉丽 Scarlett  
**日期:** 2026-03-09  
**版本:** v1.0.0
