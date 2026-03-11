#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀兼容性适配器 - 确保旧版数据和新架构无缝衔接

向后兼容：
- 旧版 JSONL 记忆数据
- 旧版任务格式
- 旧版配置文件
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from .memory import MemorySystem
from .task_queue import Task, TaskQueue


class LegacyAdapter:
    """旧版数据适配器"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.memory_system = None
        
        # 旧版数据路径
        self.legacy_paths = {
            "sessions": self.workspace / "agents" / "main" / "sessions",
            "task_state": self.workspace / ".learnings" / "task_state.json",
            "conversations": self.workspace / "conversations",
            "lingxi_db": self.workspace / ".lingxi" / "dashboard.db"
        }
    
    def migrate_legacy_memories(self, dry_run: bool = True) -> Dict:
        """
        迁移旧版 JSONL 记忆到新架构
        
        Args:
            dry_run: 如果为 True，只统计不迁移
            
        Returns:
            迁移统计信息
        """
        stats = {
            "total_sessions": 0,
            "total_messages": 0,
            "migrated": 0,
            "errors": 0,
            "details": []
        }
        
        sessions_dir = self.legacy_paths["sessions"]
        if not sessions_dir.exists():
            return stats
        
        # 扫描所有 session 文件
        for session_file in sessions_dir.glob("*.jsonl"):
            if ".reset" in session_file.name or ".deleted" in session_file.name:
                continue
            
            stats["total_sessions"] += 1
            
            try:
                lines = session_file.read_text(encoding="utf-8").strip().split("\n")
                session_id = session_file.stem
                
                for line in lines:
                    try:
                        event = json.loads(line)
                        if event.get("type") == "message":
                            stats["total_messages"] += 1
                            
                            if not dry_run:
                                # 迁移到新记忆系统
                                self._migrate_message(event, session_id)
                                stats["migrated"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        stats["details"].append({
                            "file": str(session_file),
                            "error": str(e)
                        })
                        
            except Exception as e:
                stats["errors"] += 1
                stats["details"].append({
                    "file": str(session_file),
                    "error": str(e)
                })
        
        return stats
    
    def _migrate_message(self, event: Dict, session_id: str):
        """迁移单条消息到新记忆系统"""
        if self.memory_system is None:
            self.memory_system = MemorySystem(str(self.workspace))
        
        msg = event.get("message", {})
        role = msg.get("role", "unknown")
        content_items = msg.get("content", [])
        
        # 提取文本内容
        content = ""
        for item in content_items:
            if isinstance(item, dict) and item.get("type") == "text":
                content = item.get("text", "")
                break
        
        if not content:
            return
        
        # 提取用户 ID
        user_id = "unknown"
        if "ou_" in content or "wx_" in content or "oc_" in content:
            import re
            match = re.search(r'(ou_|wx_|oc_)[a-z0-9]+', content)
            if match:
                user_id = match.group(0)
        
        # 解析时间戳
        timestamp = event.get("timestamp", "")
        created_at = time.time()
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace("Z", ""))
                created_at = dt.timestamp()
            except:
                pass
        
        # 添加到新记忆系统
        self.memory_system.add_message(
            session_id=session_id,
            role=role,
            content=content,
            user_id=user_id,
            created_at=created_at
        )
    
    def convert_legacy_task(self, legacy_task: Dict) -> Task:
        """将旧版任务格式转换为新格式"""
        return Task(
            id=legacy_task.get("id", f"task_{int(time.time()*1000)}"),
            type="realtime",
            priority=2,  # NORMAL
            status=legacy_task.get("status", "pending"),
            payload={
                "user_input": legacy_task.get("user_input", ""),
                "channel": legacy_task.get("channel", "unknown"),
                "user_id": legacy_task.get("user_id", "unknown")
            },
            created_at=legacy_task.get("created_at", time.time()),
            started_at=legacy_task.get("started_at"),
            completed_at=legacy_task.get("completed_at"),
            channel=legacy_task.get("channel", "unknown"),
            user_id=legacy_task.get("user_id", "unknown")
        )
    
    def load_legacy_config(self) -> Dict:
        """加载旧版配置"""
        config = {
            "skills": [],
            "models": {},
            "channels": {},
            "scheduled_tasks": []
        }
        
        # 尝试从不同位置加载配置
        config_paths = [
            self.workspace / "config.json",
            self.workspace / ".lingxi" / "config.json",
            Path.home() / ".openclaw" / "config.json"
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    legacy_config = json.loads(config_path.read_text())
                    # 合并配置
                    config.update(legacy_config)
                except:
                    pass
        
        return config
    
    def export_legacy_data(self, output_path: str) -> str:
        """导出旧版数据（备份用）"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "version": "1.0",
            "exported_at": time.time(),
            "sessions": [],
            "task_state": None
        }
        
        # 导出 sessions
        sessions_dir = self.legacy_paths["sessions"]
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.jsonl"):
                if ".reset" in session_file.name or ".deleted" in session_file.name:
                    continue
                
                try:
                    content = session_file.read_text(encoding="utf-8")
                    export_data["sessions"].append({
                        "file": session_file.name,
                        "content": content
                    })
                except:
                    pass
        
        # 导出 task_state
        task_state_file = self.legacy_paths["task_state"]
        if task_state_file.exists():
            try:
                export_data["task_state"] = json.loads(task_state_file.read_text())
            except:
                pass
        
        output.write_text(json.dumps(export_data, ensure_ascii=False, indent=2))
        
        return str(output)
    
    def backup_and_migrate(self, backup_path: str = None) -> Dict:
        """
        完整迁移流程：备份 → 迁移 → 验证
        
        Args:
            backup_path: 备份文件路径（可选）
            
        Returns:
            迁移报告
        """
        import shutil
        from datetime import datetime
        
        report = {
            "success": False,
            "backup_path": None,
            "migration_stats": None,
            "errors": []
        }
        
        try:
            # 步骤 1: 备份旧数据
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = str(self.workspace / f"backup_{timestamp}.json")
            
            export_path = self.export_legacy_data(backup_path)
            report["backup_path"] = export_path
            
            # 步骤 2: 执行迁移（先 dry_run）
            stats = self.migrate_legacy_memories(dry_run=True)
            report["migration_stats"] = stats
            
            # 步骤 3: 实际迁移
            if stats["total_messages"] > 0:
                self.migrate_legacy_memories(dry_run=False)
            
            report["success"] = True
            
        except Exception as e:
            report["errors"].append(str(e))
            report["success"] = False
        
        return report


# 便捷函数
def check_compatibility(workspace_path: str) -> Dict:
    """
    检查旧版数据兼容性
    
    Returns:
        兼容性报告
    """
    adapter = LegacyAdapter(workspace_path)
    
    report = {
        "workspace": workspace_path,
        "legacy_data_found": False,
        "sessions_count": 0,
        "messages_count": 0,
        "task_state_exists": False,
        "recommendations": []
    }
    
    # 检查 sessions
    sessions_dir = Path(workspace_path) / "agents" / "main" / "sessions"
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*.jsonl"))
        valid_files = [f for f in session_files if ".reset" not in f.name and ".deleted" not in f.name]
        
        if valid_files:
            report["legacy_data_found"] = True
            report["sessions_count"] = len(valid_files)
            
            # 估算消息数
            total_lines = 0
            for f in valid_files[:10]:  # 抽样检查前 10 个文件
                try:
                    lines = f.read_text(encoding="utf-8").strip().split("\n")
                    total_lines += len(lines)
                except:
                    pass
            
            if valid_files:
                avg_lines = total_lines / min(len(valid_files), 10)
                report["messages_count"] = int(avg_lines * len(valid_files))
            
            report["recommendations"].append(
                f"发现 {len(valid_files)} 个旧版 session 文件，建议迁移到新记忆系统"
            )
    
    # 检查 task_state
    task_state_file = Path(workspace_path) / ".learnings" / "task_state.json"
    if task_state_file.exists():
        report["task_state_exists"] = True
        report["recommendations"].append("发现旧版任务状态文件，建议迁移到任务队列系统")
    
    return report
