#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 三位一体状态管理器 v3.0

统一管理心跳、记忆、任务的状态，实现三者完美融合
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class TrinityState:
    """三位一体状态"""
    user_id: str
    updated_at: str
    heartbeat: Dict[str, Any]
    memory: Dict[str, Any]
    task: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """转换为字典（避免循环引用）"""
        return {
            "user_id": self.user_id,
            "updated_at": self.updated_at,
            "heartbeat": self.heartbeat,
            "memory": self.memory,
            "task": self.task
        }
    
    def to_json(self) -> str:
        """转换为 JSON（安全版本）"""
        try:
            return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        except (TypeError, RecursionError) as e:
            # 如果转换失败，返回简化版本
            print(f"⚠️ JSON 转换失败：{e}，使用简化版本")
            return json.dumps({
                "user_id": self.user_id,
                "updated_at": self.updated_at,
                "heartbeat": {"tasks": len(self.heartbeat.get("tasks", []))},
                "memory": {"preferences": len(self.memory.get("preferences", {}))},
                "task": {"history": len(self.task.get("history", []))}
            }, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TrinityState':
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TrinityState':
        return cls.from_dict(json.loads(json_str))

class TrinityStateManager:
    """
    三位一体状态管理器
    
    功能：
    - 统一存储心跳、记忆、任务状态
    - 提供完整上下文给任务执行
    - 自动持久化到文件系统
    """
    
    def __init__(self, user_id: str, storage_path: str = "~/.openclaw/workspace/trinity_state"):
        self.user_id = user_id
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 状态文件路径
        self.state_file = self.storage_path / f"{user_id}.json"
        
        # 加载或创建状态
        self.state = self._load_state()
    
    def _load_state(self) -> TrinityState:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return TrinityState.from_dict(data)
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}，创建新状态")
        
        # 创建默认状态
        return self._create_default_state()
    
    def _create_default_state(self) -> TrinityState:
        """创建默认状态"""
        return TrinityState(
            user_id=self.user_id,
            updated_at=datetime.now().isoformat(),
            heartbeat={
                "last_check": None,
                "tasks": [],
                "history": [],
                "scheduled": []
            },
            memory={
                "conversation_id": None,
                "message_count": 0,
                "preferences": {},
                "knowledge": [],
                "relationships": {}
            },
            task={
                "current": None,
                "history": [],
                "pending": []
            }
        )
    
    def _save_state(self):
        """保存状态"""
        self.state.updated_at = datetime.now().isoformat()
        
        # 直接序列化 state 对象（不使用 to_json 方法）
        try:
            data = {
                "user_id": self.state.user_id,
                "updated_at": self.state.updated_at,
                "heartbeat": self.state.heartbeat,
                "memory": self.state.memory,
                "task": self.state.task
            }
            
            # 原子写入（先写临时文件，再重命名）
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            temp_file.rename(self.state_file)
        except Exception as e:
            print(f"⚠️ 保存状态失败：{e}")
    
    # ========== 心跳相关方法 ==========
    
    def update_heartbeat(self, **kwargs):
        """更新心跳状态"""
        self.state.heartbeat.update(kwargs)
        self._save_state()
    
    def add_heartbeat_task(self, task: Dict):
        """添加心跳任务"""
        self.state.heartbeat["tasks"].append(task)
        self._save_state()
    
    def add_heartbeat_history(self, entry: Dict):
        """添加心跳历史"""
        self.state.heartbeat["history"].append({
            **entry,
            "timestamp": datetime.now().isoformat()
        })
        # 保留最近 100 条
        self.state.heartbeat["history"] = self.state.heartbeat["history"][-100:]
        self._save_state()
    
    # ========== 记忆相关方法 ==========
    
    def update_memory(self, **kwargs):
        """更新记忆状态"""
        self.state.memory.update(kwargs)
        self._save_state()
    
    def add_preference(self, key: str, value: Any):
        """添加用户偏好"""
        self.state.memory["preferences"][key] = value
        self._save_state()
    
    def add_knowledge(self, knowledge: Dict):
        """添加知识点"""
        knowledge_entry = {
            **knowledge,
            "id": self._generate_id(knowledge),
            "created_at": datetime.now().isoformat()
        }
        self.state.memory["knowledge"].append(knowledge_entry)
        self._save_state()
        return knowledge_entry["id"]
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索知识点（简单关键词匹配）"""
        keywords = query.lower().split()
        scored = []
        
        for knowledge in self.state.memory["knowledge"]:
            score = 0
            content = str(knowledge.get("content", "")).lower()
            tags = knowledge.get("tags", [])
            
            # 关键词匹配
            for kw in keywords:
                if kw in content:
                    score += 2
                if kw in tags:
                    score += 1
            
            if score > 0:
                scored.append((score, knowledge))
        
        # 按分数排序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
    
    # ========== 任务相关方法 ==========
    
    def update_task(self, **kwargs):
        """更新任务状态"""
        self.state.task.update(kwargs)
        self._save_state()
    
    def set_current_task(self, task: Dict):
        """设置当前任务"""
        self.state.task["current"] = {
            **task,
            "started_at": datetime.now().isoformat()
        }
        self._save_state()
    
    def complete_current_task(self, result: Any):
        """完成当前任务"""
        if self.state.task["current"]:
            # 移动到历史
            completed = self.state.task["current"]
            completed["result"] = result
            completed["completed_at"] = datetime.now().isoformat()
            self.state.task["history"].append(completed)
            
            # 清空当前
            self.state.task["current"] = None
            
            # 保留最近 50 条历史
            self.state.task["history"] = self.state.task["history"][-50:]
            
            self._save_state()
    
    def add_pending_task(self, task: Dict):
        """添加待办任务"""
        self.state.task["pending"].append({
            **task,
            "created_at": datetime.now().isoformat()
        })
        self._save_state()
    
    # ========== 上下文获取 ==========
    
    def get_context(self) -> Dict:
        """获取完整上下文（用于任务执行）"""
        return {
            "user_id": self.user_id,
            "preferences": self.state.memory["preferences"],
            "knowledge": self.state.memory["knowledge"][-10:],  # 最近 10 条
            "conversation_id": self.state.memory["conversation_id"],
            "message_count": self.state.memory["message_count"],
            "heartbeat_tasks": self.state.heartbeat["tasks"],
            "recent_heartbeat_history": self.state.heartbeat["history"][-5:],
            "task_history": self.state.task["history"][-10:],
            "pending_tasks": self.state.task["pending"]
        }
    
    def get_full_state(self) -> Dict:
        """获取完整状态（用于调试）"""
        return self.state.to_dict()
    
    # ========== 工具方法 ==========
    
    def _generate_id(self, data: Dict) -> str:
        """生成唯一 ID"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def clear(self):
        """清空状态（慎用）"""
        self.state = self._create_default_state()
        self._save_state()
    
    def export(self, output_path: str):
        """导出状态到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.state.to_json())
    
    def import_state(self, input_path: str):
        """从文件导入状态"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.state = TrinityState.from_dict(data)
            self._save_state()

# ========== 全局单例 ==========

_instances: Dict[str, TrinityStateManager] = {}

def get_state_manager(user_id: str) -> TrinityStateManager:
    """获取状态管理器单例"""
    if user_id not in _instances:
        _instances[user_id] = TrinityStateManager(user_id)
    return _instances[user_id]

def reload_state_manager(user_id: str) -> TrinityStateManager:
    """重新加载状态管理器"""
    if user_id in _instances:
        del _instances[user_id]
    return get_state_manager(user_id)

# ========== 测试入口 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 测试三位一体状态管理器")
    print("=" * 60)
    
    # 创建管理器
    user_id = "test_user_123"
    state = TrinityStateManager(user_id)
    
    print(f"\n1️⃣ 初始状态")
    print(f"   用户：{state.user_id}")
    print(f"   更新时间：{state.state.updated_at}")
    
    print(f"\n2️⃣ 测试心跳更新")
    state.update_heartbeat(last_check=datetime.now().isoformat())
    state.add_heartbeat_task({
        "name": "测试任务",
        "schedule": "0 9 * * *"
    })
    print(f"   ✅ 心跳任务数：{len(state.state.heartbeat['tasks'])}")
    
    print(f"\n3️⃣ 测试记忆更新")
    state.add_preference("news_topics", ["创新创业", "社会保障"])
    state.add_preference("response_style", "humorous")
    state.add_knowledge({
        "type": "news_summary",
        "content": "2026-03-07 两会新闻摘要",
        "tags": ["两会", "新闻"]
    })
    print(f"   ✅ 偏好数：{len(state.state.memory['preferences'])}")
    print(f"   ✅ 知识点数：{len(state.state.memory['knowledge'])}")
    
    print(f"\n4️⃣ 测试任务更新")
    state.set_current_task({
        "input": "写工作日报",
        "type": "content_creation"
    })
    state.complete_current_task("已生成日报")
    print(f"   ✅ 任务历史数：{len(state.state.task['history'])}")
    
    print(f"\n5️⃣ 测试上下文获取")
    context = state.get_context()
    print(f"   ✅ 上下文键：{list(context.keys())}")
    
    print(f"\n6️⃣ 测试知识搜索")
    results = state.search_knowledge("两会新闻", top_k=3)
    print(f"   ✅ 搜索结果：{len(results)} 条")
    for result in results:
        print(f"      - {result['content']}")
    
    print(f"\n7️⃣ 存储文件位置")
    print(f"   📁 {state.state_file}")
    print(f"   📊 文件大小：{state.state_file.stat().st_size} bytes")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
