#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - HEARTBEAT 任务同步器

功能:
1. 任务收到时自动写入 HEARTBEAT.md
2. 任务完成时自动删除对应内容
3. 支持渠道追踪（QQ/微信/钉钉等）
4. 定时任务固定保留
5. 心跳检查时展示实时任务状态

使用方式:
    from heartbeat_task_sync import HeartbeatTaskSync
    
    sync = HeartbeatTaskSync()
    
    # 任务收到时
    sync.add_task(task_id, description, channel, user_id)
    
    # 任务完成时
    sync.complete_task(task_id)
    
    # 心跳检查时
    status = sync.get_status()
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# ==================== 配置 ====================

HEARTBEAT_FILE = Path.home() / ".openclaw" / "workspace" / "HEARTBEAT.md"
TASK_STATE_FILE = Path.home() / ".openclaw" / "workspace" / ".learnings" / "task_state.json"

# 渠道映射
CHANNEL_EMOJIS = {
    "qqbot": "💬",
    "wechat": "💚",
    "feishu": "📘",
    "dingtalk": "🔵",
    "wecom": "🟢",
    "telegram": "✈️",
    "discord": "🎮",
    "default": "📋"
}

# ==================== 数据结构 ====================

@dataclass
class Task:
    """任务数据结构"""
    task_id: str
    description: str
    channel: str
    user_id: str
    created_at: str
    status: str = "pending"  # pending, running, completed
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "channel": self.channel,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "status": self.status,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        return cls(**data)

# ==================== 任务同步器 ====================

class HeartbeatTaskSync:
    """HEARTBEAT 任务同步器"""
    
    def __init__(self):
        self.state_file = TASK_STATE_FILE
        self.heartbeat_file = HEARTBEAT_FILE
        
        # 确保目录存在
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载任务状态
        self.tasks = self._load_state()
        
        # 初始化 HEARTBEAT.md
        self._init_heartbeat_file()
    
    def _default_state(self) -> Dict:
        """默认状态"""
        return {
            "tasks": {},
            "scheduled_tasks": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_state(self) -> Dict:
        """加载任务状态"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                result = {**self._default_state(), **data}
                
                # 将字典转换回 Task 对象
                if "tasks" in result:
                    converted_tasks = {}
                    for k, v in result["tasks"].items():
                        if isinstance(v, dict):
                            converted_tasks[k] = Task.from_dict(v)
                        else:
                            converted_tasks[k] = v
                    result["tasks"] = converted_tasks
                
                return result
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}")
        return self._default_state()
    
    def _save_state(self):
        """保存任务状态"""
        self.state_file.write_text(
            json.dumps(self.state, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    @property
    def state(self) -> Dict:
        """获取当前状态"""
        return {
            "tasks": {k: v.to_dict() if isinstance(v, Task) else v for k, v in self.tasks.get("tasks", {}).items()},
            "scheduled_tasks": self.tasks.get("scheduled_tasks", []),
            "last_updated": datetime.now().isoformat()
        }
    
    def _init_heartbeat_file(self):
        """初始化 HEARTBEAT.md"""
        if not self.heartbeat_file.exists():
            self._write_heartbeat_content(self._get_default_content())
    
    def _get_default_content(self) -> str:
        """获取默认内容"""
        return """# HEARTBEAT.md - 心跳检查

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

---

## 📋 实时任务状态

> 自动更新 - 最后更新：{last_updated}

{task_list}

---

## ⏰ 定时任务

{scheduled_tasks}

---

## 📊 统计信息

- 进行中任务：{pending_count}
- 已完成任务：{completed_count}
- 定时任务：{scheduled_count}

---

*本文件由灵犀 Heartbeat Task Sync 自动维护*
"""
    
    def _write_heartbeat_content(self, content: str):
        """写入 HEARTBEAT.md"""
        self.heartbeat_file.write_text(content, encoding='utf-8')
    
    def add_task(self, task_id: str, description: str, channel: str, user_id: str):
        """添加任务（收到新任务时调用）"""
        task = Task(
            task_id=task_id,
            description=description,
            channel=channel,
            user_id=user_id,
            created_at=datetime.now().isoformat()
        )
        
        self.tasks.setdefault("tasks", {})[task_id] = task
        self._save_state()
        
        # 更新 HEARTBEAT.md
        self._update_heartbeat()
        
        print(f"✅ 任务已添加：{task_id} ({channel})")
    
    def complete_task(self, task_id: str):
        """完成任务（任务执行完成时调用）"""
        if task_id in self.tasks.get("tasks", {}):
            task = self.tasks["tasks"][task_id]
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            
            # 从活动任务中移除（保留历史记录）
            self._save_state()
            
            # 更新 HEARTBEAT.md
            self._update_heartbeat()
            
            print(f"✅ 任务已完成：{task_id}")
        else:
            print(f"⚠️  任务不存在：{task_id}")
    
    def add_scheduled_task(self, name: str, schedule: str, description: str):
        """添加定时任务"""
        scheduled_task = {
            "name": name,
            "schedule": schedule,
            "description": description,
            "added_at": datetime.now().isoformat()
        }
        
        self.tasks.setdefault("scheduled_tasks", []).append(scheduled_task)
        self._save_state()
        
        # 更新 HEARTBEAT.md
        self._update_heartbeat()
        
        print(f"✅ 定时任务已添加：{name}")
    
    def remove_scheduled_task(self, name: str):
        """移除定时任务"""
        scheduled_tasks = self.tasks.get("scheduled_tasks", [])
        self.tasks["scheduled_tasks"] = [t for t in scheduled_tasks if t["name"] != name]
        self._save_state()
        
        # 更新 HEARTBEAT.md
        self._update_heartbeat()
        
        print(f"✅ 定时任务已移除：{name}")
    
    def _update_heartbeat(self):
        """更新 HEARTBEAT.md 内容"""
        content = self._generate_heartbeat_content()
        self._write_heartbeat_content(content)
    
    def _generate_heartbeat_content(self) -> str:
        """生成 HEARTBEAT.md 内容"""
        tasks = self.tasks.get("tasks", {})
        scheduled_tasks = self.tasks.get("scheduled_tasks", [])
        
        # 活动任务列表
        pending_tasks = [t for t in tasks.values() if t.status == "pending"]
        running_tasks = [t for t in tasks.values() if t.status == "running"]
        completed_tasks = [t for t in tasks.values() if t.status == "completed"]
        
        task_list = []
        
        if pending_tasks or running_tasks:
            task_list.append("### 🔄 进行中任务\n")
            
            for task in pending_tasks + running_tasks:
                emoji = CHANNEL_EMOJIS.get(task.channel, CHANNEL_EMOJIS["default"])
                status_icon = "⏳" if task.status == "pending" else "🚀"
                task_list.append(f"- {status_icon} {emoji} **{task.task_id}**: {task.description}")
                task_list.append(f"  - 渠道：{task.channel} | 用户：{task.user_id}")
                task_list.append(f"  - 创建时间：{task.created_at}")
                task_list.append("")
        
        if completed_tasks:
            task_list.append("### ✅ 最近完成\n")
            for task in completed_tasks[-5:]:  # 只显示最近 5 个
                emoji = CHANNEL_EMOJIS.get(task.channel, CHANNEL_EMOJIS["default"])
                task_list.append(f"- ✅ {emoji} **{task.task_id}**: {task.description}")
                task_list.append(f"  - 完成时间：{task.completed_at}")
                task_list.append("")
        
        # 定时任务列表
        scheduled_list = []
        if scheduled_tasks:
            for st in scheduled_tasks:
                scheduled_list.append(f"- ⏰ **{st['name']}**: {st['description']}")
                scheduled_list.append(f"  - 周期：{st['schedule']}")
                scheduled_list.append("")
        else:
            scheduled_list.append("*暂无定时任务*\n")
        
        # 统计信息
        return self._get_default_content().format(
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            task_list="\n".join(task_list) if task_list else "*暂无进行中任务*\n",
            scheduled_tasks="\n".join(scheduled_list),
            pending_count=len(pending_tasks) + len(running_tasks),
            completed_count=len(completed_tasks),
            scheduled_count=len(scheduled_tasks)
        )
    
    def get_status(self) -> Dict:
        """获取任务状态（心跳检查时调用）"""
        tasks = self.tasks.get("tasks", {})
        scheduled_tasks = self.tasks.get("scheduled_tasks", [])
        
        pending = [t for t in tasks.values() if t.status == "pending"]
        running = [t for t in tasks.values() if t.status == "running"]
        completed = [t for t in tasks.values() if t.status == "completed"]
        
        return {
            "pending_count": len(pending),
            "running_count": len(running),
            "completed_count": len(completed),
            "scheduled_count": len(scheduled_tasks),
            "tasks": {
                "pending": [t.to_dict() for t in pending],
                "running": [t.to_dict() for t in running],
                "completed": [t.to_dict() for t in completed[-5:]]
            },
            "scheduled_tasks": scheduled_tasks
        }
    
    def generate_heartbeat_report(self, format: str = "text") -> str:
        """生成心跳检查报告（用于回复用户）"""
        status = self.get_status()
        
        if format == "kanban":
            # 看板格式
            report = "📊 **任务看板**\n\n"
            report += "```\n"
            report += f"🔄 进行中  |  ✅ 已完成  |  ⏰ 定时\n"
            report += f"{'─'*12} | {'─'*12} | {'─'*12}\n"
            report += f"{status['pending_count'] + status['running_count']:^12} | {status['completed_count']:^12} | {status['scheduled_count']:^12}\n"
            report += "```\n\n"
            
            # Agent 健康状态
            report += "**Agent 健康状态**\n"
            report += f"- 🟢 活跃：灵犀主服务\n"
            report += f"- 📊 总任务：{status['pending_count'] + status['running_count'] + status['completed_count']}\n"
        else:
            # 文本格式
            report = "💓 **心跳检查报告**\n\n"
            
            if status["pending_count"] > 0 or status["running_count"] > 0:
                report += f"🔄 进行中任务：{status['pending_count'] + status['running_count']}\n"
                for task in status["tasks"]["pending"][:3]:
                    report += f"  - ⏳ {task['task_id']}: {task['description']}\n"
            
            if status["completed_count"] > 0:
                report += f"\n✅ 最近完成：{min(status['completed_count'], 5)}\n"
                for task in status["tasks"]["completed"]:
                    report += f"  - ✅ {task['task_id']}\n"
            
            if status["scheduled_count"] > 0:
                report += f"\n⏰ 定时任务：{status['scheduled_count']}\n"
                for st in status["scheduled_tasks"][:3]:
                    report += f"  - ⏰ {st['name']}: {st['schedule']}\n"
            
            if status["pending_count"] == 0 and status["running_count"] == 0:
                report += "✨ 当前无进行中任务，一切正常！\n"
        
        return report

# ==================== 全局实例 ====================

_sync: Optional[HeartbeatTaskSync] = None

def get_heartbeat_sync() -> HeartbeatTaskSync:
    """获取全局实例"""
    global _sync
    if _sync is None:
        _sync = HeartbeatTaskSync()
    return _sync

# ==================== 便捷函数 ====================

def on_task_received(task_id: str, description: str, channel: str, user_id: str):
    """任务收到时的 Hook"""
    sync = get_heartbeat_sync()
    sync.add_task(task_id, description, channel, user_id)

def on_task_completed(task_id: str):
    """任务完成时的 Hook"""
    sync = get_heartbeat_sync()
    sync.complete_task(task_id)

def get_heartbeat_status() -> str:
    """获取心跳状态报告"""
    sync = get_heartbeat_sync()
    return sync.generate_heartbeat_report()

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🔁 灵犀 HEARTBEAT 任务同步器测试")
    print("=" * 60)
    
    sync = get_heartbeat_sync()
    
    # 测试添加任务
    print("\n1️⃣ 添加任务")
    sync.add_task("task_001", "测试任务 1", "qqbot", "user_123")
    sync.add_task("task_002", "测试任务 2", "wechat", "user_456")
    
    # 测试完成任务
    print("\n2️⃣ 完成任务")
    sync.complete_task("task_001")
    
    # 测试添加定时任务
    print("\n3️⃣ 添加定时任务")
    sync.add_scheduled_task("两会新闻监控", "0 */4 * * *", "搜集两会相关新闻")
    
    # 获取状态
    print("\n4️⃣ 获取状态")
    status = sync.get_status()
    print(f"   进行中：{status['pending_count']}")
    print(f"   已完成：{status['completed_count']}")
    print(f"   定时任务：{status['scheduled_count']}")
    
    # 生成报告
    print("\n5️⃣ 生成报告")
    report = sync.generate_heartbeat_report()
    print(report)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！查看 HEARTBEAT.md 文件")
    print("=" * 60)
