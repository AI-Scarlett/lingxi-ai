#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 任务状态管理器
负责任务状态的持久化、查询、更新
支持多任务并发追踪
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading

# ==================== 任务状态定义 ====================

class TaskStatus(Enum):
    PENDING = "pending"       # 等待执行
    RUNNING = "running"       # 执行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消

@dataclass
class TaskInfo:
    """任务信息"""
    id: str
    type: str                    # 任务类型：wechat-publish, xhs-post, etc.
    description: str             # 任务描述
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=lambda: datetime.now().timestamp() * 1000)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    session_id: Optional[str] = None  # 执行 session ID
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    notify_on_complete: bool = True
    user_id: Optional[str] = None  # 用户 ID (QQ openid)
    channel: str = "qqbot"       # 通知渠道
    priority: int = 0            # 优先级，数字越大优先级越高

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "session_id": self.session_id,
            "result": self.result,
            "error": self.error,
            "notify_on_complete": self.notify_on_complete,
            "user_id": self.user_id,
            "channel": self.channel,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskInfo":
        """从字典创建"""
        return cls(
            id=data["id"],
            type=data["type"],
            description=data["description"],
            status=TaskStatus(data["status"]),
            created_at=data.get("created_at", datetime.now().timestamp() * 1000),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            session_id=data.get("session_id"),
            result=data.get("result"),
            error=data.get("error"),
            notify_on_complete=data.get("notify_on_complete", True),
            user_id=data.get("user_id"),
            channel=data.get("channel", "qqbot"),
            priority=data.get("priority", 0)
        )

# ==================== 任务管理器 ====================

class TaskManager:
    """任务状态管理器
    
    功能:
    - 任务注册、更新、查询
    - 状态持久化到文件
    - 支持多任务并发追踪
    - 线程安全
    """
    
    def __init__(self, state_file: str = None):
        """初始化任务管理器
        
        Args:
            state_file: 状态文件路径，默认 ~/.openclaw/workspace/task-state.json
        """
        if state_file is None:
            state_file = os.path.expanduser("~/.openclaw/workspace/task-state.json")
        
        self.state_file = state_file
        self.tasks: Dict[str, TaskInfo] = {}
        self.lock = threading.Lock()
        
        # 加载已有状态
        self._load_state()
    
    def _load_state(self):
        """从文件加载状态"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_id, task_data in data.get("tasks", {}).items():
                        self.tasks[task_id] = TaskInfo.from_dict(task_data)
                print(f"📋 已加载 {len(self.tasks)} 个任务状态")
        except Exception as e:
            print(f"⚠️ 加载状态文件失败：{e}")
            self.tasks = {}
    
    def _save_state(self):
        """保存状态到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            data = {
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存状态文件失败：{e}")
    
    def register(self, task: TaskInfo) -> str:
        """注册新任务
        
        Args:
            task: 任务信息
            
        Returns:
            任务 ID
        """
        with self.lock:
            self.tasks[task.id] = task
            self._save_state()
            print(f"✅ 任务已注册：{task.id} ({task.type})")
            return task.id
    
    def update(self, task_id: str, **kwargs) -> Optional[TaskInfo]:
        """更新任务状态
        
        Args:
            task_id: 任务 ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的任务信息，不存在则返回 None
        """
        with self.lock:
            if task_id not in self.tasks:
                print(f"⚠️ 任务不存在：{task_id}")
                return None
            
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            self._save_state()
            print(f"🔄 任务已更新：{task_id} - {task.status.value}")
            return task
    
    def get(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务信息，不存在则返回 None
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all(self, status: Optional[TaskStatus] = None) -> List[TaskInfo]:
        """获取所有任务（可按状态过滤）
        
        Args:
            status: 状态过滤
            
        Returns:
            任务列表
        """
        with self.lock:
            if status is None:
                return list(self.tasks.values())
            return [t for t in self.tasks.values() if t.status == status]
    
    def get_running(self) -> List[TaskInfo]:
        """获取所有运行中的任务"""
        return self.get_all(TaskStatus.RUNNING)
    
    def get_pending(self) -> List[TaskInfo]:
        """获取所有等待中的任务"""
        return self.get_all(TaskStatus.PENDING)
    
    def delete(self, task_id: str) -> bool:
        """删除任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否删除成功
        """
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                self._save_state()
                print(f"🗑️ 任务已删除：{task_id}")
                return True
            return False
    
    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """清理已完成的任务
        
        Args:
            max_age_hours: 保留最近 N 小时的任务
            
        Returns:
            清理的任务数量
        """
        with self.lock:
            now = datetime.now().timestamp() * 1000
            cutoff = now - (max_age_hours * 3600 * 1000)
            
            to_delete = []
            for task_id, task in self.tasks.items():
                if task.status == TaskStatus.COMPLETED and task.completed_at < cutoff:
                    to_delete.append(task_id)
            
            for task_id in to_delete:
                del self.tasks[task_id]
            
            if to_delete:
                self._save_state()
                print(f"🧹 已清理 {len(to_delete)} 个过期任务")
            
            return len(to_delete)

# ==================== 工具函数 ====================

def generate_task_id(prefix: str = "task") -> str:
    """生成任务 ID"""
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}"

# ==================== 单例实例 ====================

# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None

def get_task_manager() -> TaskManager:
    """获取全局任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager

# ==================== 测试 ====================

if __name__ == "__main__":
    # 测试任务管理器
    manager = TaskManager()
    
    # 创建测试任务
    task = TaskInfo(
        id=generate_task_id(),
        type="wechat-publish",
        description="测试公众号发布",
        user_id="test_user_123"
    )
    
    # 注册任务
    manager.register(task)
    
    # 更新状态
    manager.update(task.id, status=TaskStatus.RUNNING, started_at=datetime.now().timestamp() * 1000)
    
    # 查询任务
    retrieved = manager.get(task.id)
    print(f"\n📋 任务状态：{retrieved.status.value}")
    
    # 完成任务
    manager.update(
        task.id,
        status=TaskStatus.COMPLETED,
        completed_at=datetime.now().timestamp() * 1000,
        result={"success": True, "url": "https://example.com"}
    )
    
    # 获取所有运行中的任务
    running = manager.get_running()
    print(f"🔄 运行中的任务数：{len(running)}")
    
    print("\n✅ 测试完成")
