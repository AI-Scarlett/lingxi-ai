#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 审计日志层 (Audit Log Layer)

功能:
1. 完整任务流转记录
2. 5 阶段时间线
3. 结构化存储
4. 可复现可审计
5. 新旧版本兼容

使用方式:
    from audit_layer import AuditLayer
    
    audit = AuditLayer()
    
    # 开始任务
    audit.start_task(task_id, user_input)
    
    # 记录阶段
    audit.record_stage(task_id, "中书省", {"plan": "..."})
    audit.record_stage(task_id, "门下省", {"review": "..."})
    audit.record_stage(task_id, "六部", {"result": "..."})
    
    # 完成任务
    audit.complete_task(task_id, final_output)
    
    # 查询审计日志
    log = audit.get_task_log(task_id)
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

# ==================== 数据结构 ====================

class TaskStage(Enum):
    """任务阶段"""
    RECEIVED = "received"  # 收到任务
    PLANNING = "planning"  # 任务规划
    REVIEWING = "reviewing"  # 质量审核
    EXECUTING = "executing"  # 任务执行
    COMPLETED = "completed"  # 完成

@dataclass
class StageRecord:
    """阶段记录"""
    stage: TaskStage
    timestamp: str
    data: Dict[str, Any]
    duration_ms: float = 0.0
    status: str = "ok"  # ok/error/warning
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "stage": self.stage.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error": self.error
        }

@dataclass
class TaskAudit:
    """任务审计日志"""
    task_id: str
    user_id: str
    user_input: str
    created_at: str
    completed_at: Optional[str] = None
    stages: List[StageRecord] = field(default_factory=list)
    final_output: Optional[str] = None
    total_duration_ms: float = 0.0
    status: str = "pending"  # pending/running/completed/failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "user_input": self.user_input,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "stages": [s.to_dict() for s in self.stages],
            "final_output": self.final_output,
            "total_duration_ms": self.total_duration_ms,
            "status": self.status,
            "metadata": self.metadata
        }
    
    def to_timeline(self) -> str:
        """生成时间线文本"""
        lines = [f"📊 **任务 {self.task_id}**\n"]
        lines.append(f"**用户**: {self.user_id}")
        lines.append(f"**输入**: {self.user_input[:50]}...")
        lines.append("")
        lines.append("**执行时间线**:")
        
        stage_names = {
            TaskStage.RECEIVED: "任务接收",
            TaskStage.PLANNING: "任务规划",
            TaskStage.REVIEWING: "质量审核",
            TaskStage.EXECUTING: "任务执行",
            TaskStage.COMPLETED: "任务完成"
        }
        
        stage_emojis = {
            TaskStage.RECEIVED: "📨",
            TaskStage.PLANNING: "📝",
            TaskStage.REVIEWING: "🔍",
            TaskStage.EXECUTING: "⚙️",
            TaskStage.COMPLETED: "✅"
        }
        
        for stage in self.stages:
            emoji = stage_emojis.get(stage.stage, "📌")
            name = stage_names.get(stage.stage, stage.stage.value)
            time_str = stage.timestamp.split("T")[1].split(".")[0]
            status_icon = "✅" if stage.status == "ok" else "❌"
            lines.append(f"  {emoji} {name:12} {time_str} {status_icon}")
            if stage.error:
                lines.append(f"      └─ {stage.error}")
        
        if self.final_output:
            lines.append("")
            lines.append(f"**输出**: {self.final_output[:100]}...")
        
        lines.append("")
        lines.append(f"**总耗时**: {self.total_duration_ms:.0f}ms")
        
        return "\n".join(lines)
    
    def to_markdown(self) -> str:
        """生成 Markdown 格式"""
        return self.to_timeline()

# ==================== 审计层 ====================

class AuditLayer:
    """
    审计日志层（Audit Log Layer）
    
    功能：
    - 完整任务流转记录
    - 5 阶段时间线
    - 结构化存储
    - 可复现可审计
    """
    
    def __init__(self, storage_path: str = "~/.openclaw/workspace/.learnings/audits",
                 auto_save: bool = True):
        """
        初始化审计层
        
        Args:
            storage_path: 存储路径
            auto_save: 是否自动保存（默认 True，设为 False 兼容旧版本）
        """
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.auto_save = auto_save
        self.tasks: Dict[str, TaskAudit] = {}
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0
        }
    
    def start_task(self, task_id: str, user_input: str, user_id: str = "unknown",
                   metadata: Dict = None) -> TaskAudit:
        """开始任务"""
        audit = TaskAudit(
            task_id=task_id,
            user_id=user_id,
            user_input=user_input,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # 记录收到阶段
        self._record_stage(audit, TaskStage.RECEIVED, {"input": user_input})
        
        self.tasks[task_id] = audit
        self.stats["total_tasks"] += 1
        
        if self.auto_save:
            self._save_task(audit)
        
        return audit
    
    def record_stage(self, task_id: str, stage: TaskStage, data: Dict,
                     duration_ms: float = 0.0, status: str = "ok",
                     error: str = None):
        """记录阶段"""
        if task_id not in self.tasks:
            print(f"⚠️  任务不存在：{task_id}")
            return
        
        audit = self.tasks[task_id]
        stage_record = StageRecord(
            stage=stage,
            timestamp=datetime.now().isoformat(),
            data=data,
            duration_ms=duration_ms,
            status=status,
            error=error
        )
        
        audit.stages.append(stage_record)
        
        if status != "ok":
            audit.status = "failed" if error else "warning"
        
        if self.auto_save:
            self._save_task(audit)
    
    def complete_task(self, task_id: str, final_output: str,
                      total_duration_ms: float = 0.0):
        """完成任务"""
        if task_id not in self.tasks:
            print(f"⚠️  任务不存在：{task_id}")
            return
        
        audit = self.tasks[task_id]
        audit.completed_at = datetime.now().isoformat()
        audit.final_output = final_output
        audit.total_duration_ms = total_duration_ms
        audit.status = "completed"
        
        # 记录完成阶段
        self._record_stage(audit, TaskStage.COMPLETED, {
            "output": final_output,
            "duration_ms": total_duration_ms
        })
        
        self.stats["completed_tasks"] += 1
        
        if self.auto_save:
            self._save_task(audit)
    
    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        if task_id not in self.tasks:
            return
        
        audit = self.tasks[task_id]
        audit.completed_at = datetime.now().isoformat()
        audit.status = "failed"
        audit.metadata["error"] = error
        
        self.stats["failed_tasks"] += 1
        
        if self.auto_save:
            self._save_task(audit)
    
    def _record_stage(self, audit: TaskAudit, stage: TaskStage, data: Dict):
        """内部方法：记录阶段"""
        stage_record = StageRecord(
            stage=stage,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        audit.stages.append(stage_record)
    
    def _save_task(self, audit: TaskAudit):
        """保存任务审计日志"""
        file_path = self.storage_path / f"{audit.task_id}.json"
        file_path.write_text(
            json.dumps(audit.to_dict(), indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def get_task_log(self, task_id: str) -> Optional[TaskAudit]:
        """获取任务审计日志"""
        if task_id in self.tasks:
            return self.tasks[task_id]
        
        # 从文件加载
        file_path = self.storage_path / f"{task_id}.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text(encoding='utf-8'))
                return self._dict_to_audit(data)
            except:
                pass
        
        return None
    
    def _dict_to_audit(self, data: Dict) -> TaskAudit:
        """字典转 TaskAudit"""
        stages = [
            StageRecord(
                stage=TaskStage(s["stage"]),
                timestamp=s["timestamp"],
                data=s["data"],
                duration_ms=s.get("duration_ms", 0),
                status=s.get("status", "ok"),
                error=s.get("error")
            )
            for s in data.get("stages", [])
        ]
        
        return TaskAudit(
            task_id=data["task_id"],
            user_id=data["user_id"],
            user_input=data["user_input"],
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
            stages=stages,
            final_output=data.get("final_output"),
            total_duration_ms=data.get("total_duration_ms", 0),
            status=data.get("status", "pending"),
            metadata=data.get("metadata", {})
        )
    
    def get_recent_tasks(self, limit: int = 10) -> List[TaskAudit]:
        """获取最近任务"""
        # 从内存获取
        recent = list(self.tasks.values())[-limit:]
        if len(recent) >= limit:
            return recent
        
        # 从文件补充
        files = sorted(self.storage_path.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        for file_path in files[:limit - len(recent)]:
            try:
                data = json.loads(file_path.read_text(encoding='utf-8'))
                recent.append(self._dict_to_audit(data))
            except:
                pass
        
        return recent
    
    def export_task_timeline(self, task_id: str) -> str:
        """导出任务时间线（Markdown）"""
        audit = self.get_task_log(task_id)
        if audit:
            return audit.to_markdown()
        return f"❌ 任务不存在：{task_id}"
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": f"{self.stats['completed_tasks']/self.stats['total_tasks']*100:.1f}%" if self.stats['total_tasks'] > 0 else "N/A"
        }

# ==================== 全局实例 ====================

_audit: Optional[AuditLayer] = None

def get_audit_layer(auto_save: bool = True) -> AuditLayer:
    """获取全局实例"""
    global _audit
    if _audit is None:
        _audit = AuditLayer(auto_save=auto_save)
    return _audit

def start_audit(task_id: str, user_input: str, user_id: str = "unknown"):
    """便捷函数：开始审计"""
    layer = get_audit_layer()
    return layer.start_task(task_id, user_input, user_id)

def complete_audit(task_id: str, output: str, duration_ms: float = 0.0):
    """便捷函数：完成审计"""
    layer = get_audit_layer()
    layer.complete_task(task_id, output, duration_ms)

def get_task_audit(task_id: str) -> Optional[TaskAudit]:
    """便捷函数：获取审计日志"""
    layer = get_audit_layer()
    return layer.get_task_log(task_id)

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("📜 灵犀审计层测试")
    print("=" * 60)
    
    layer = get_audit_layer()
    
    # 测试任务
    audit = layer.start_task("test_001", "写小红书文案", "user_123")
    layer.record_stage("test_001", TaskStage.PLANNING, {"plan": "拆解任务"}, 50)
    layer.record_stage("test_001", TaskStage.REVIEWING, {"review": "通过"}, 30)
    layer.record_stage("test_001", TaskStage.EXECUTING, {"result": "完成"}, 200)
    layer.complete_task("test_001", "这是小红书文案...", 280)
    
    # 获取审计日志
    log = layer.get_task_log("test_001")
    print("\n📋 任务审计日志:\n")
    print(log.to_timeline())
    
    print("\n📊 统计信息:")
    stats = layer.get_stats()
    print(f"  总任务：{stats['total_tasks']}")
    print(f"  完成率：{stats['success_rate']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
