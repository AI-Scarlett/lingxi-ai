#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 对话管理器 (v2.8.1)

核心功能：
1. 📊 对话长度监控 - 超过阈值自动提醒
2. 🔄 一键续对话 - 保留所有记忆
3. 🧠 记忆继承 - 偏好/关系/知识全部带走
4. ⚡ 无缝切换 - 用户无感知
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# ==================== 数据模型 ====================

@dataclass
class Conversation:
    """对话模型"""
    id: str
    user_id: str
    created_at: str
    updated_at: str
    message_count: int = 0
    total_tokens: int = 0
    status: str = "active"  # active, archived, continued
    continued_from: Optional[str] = None  # 继承自哪个对话
    continued_to: Optional[str] = None  # 延续到哪个对话
    summary: Optional[str] = None  # 对话摘要
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Conversation':
        return cls(**data)
    
    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_jsonl(cls, line: str) -> 'Conversation':
        return cls.from_dict(json.loads(line))

# ==================== 对话管理器 ====================

class ConversationManager:
    """
    对话管理器
    
    功能：
    - 创建/切换对话
    - 长度监控
    - 自动续对话
    - 记忆继承
    """
    
    def __init__(self, storage_path: str = "~/.openclaw/workspace/conversations"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.max_messages = 100  # 最大消息数
        self.max_tokens = 50000  # 最大 tokens
        self.warning_threshold = 0.8  # 80% 时警告
        
        # 当前对话缓存
        self._current_conversations: Dict[str, Conversation] = {}
        
        # 加载现有对话
        self._load_conversations()
    
    def _get_user_file(self, user_id: str) -> Path:
        """获取用户对话文件"""
        return self.storage_path / f"{user_id}.jsonl"
    
    def _load_conversations(self):
        """加载所有对话"""
        for file_path in self.storage_path.glob("*.jsonl"):
            user_id = file_path.stem
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        conv = Conversation.from_jsonl(line)
                        key = f"{user_id}:{conv.id}"
                        self._current_conversations[key] = conv
                    except Exception as e:
                        print(f"⚠️ 加载对话失败：{e}")
    
    def create_conversation(self, user_id: str, continued_from: str = None) -> Conversation:
        """创建新对话"""
        conv = Conversation(
            id=str(uuid.uuid4())[:8],
            user_id=user_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            message_count=0,
            total_tokens=0,
            status="active",
            continued_from=continued_from
        )
        
        # 保存
        self._save_conversation(conv)
        
        # 如果有前驱对话，更新前驱的状态
        if continued_from:
            self._mark_continued(user_id, continued_from, conv.id)
        
        return conv
    
    def _save_conversation(self, conv: Conversation):
        """保存对话"""
        file_path = self._get_user_file(conv.user_id)
        
        # 追加到文件
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(conv.to_jsonl() + '\n')
        
        # 更新缓存
        key = f"{conv.user_id}:{conv.id}"
        self._current_conversations[key] = conv
    
    def _mark_continued(self, user_id: str, from_id: str, to_id: str):
        """标记对话已延续"""
        key = f"{user_id}:{from_id}"
        if key in self._current_conversations:
            conv = self._current_conversations[key]
            conv.status = "continued"
            conv.continued_to = to_id
            conv.updated_at = datetime.now().isoformat()
            self._save_conversation(conv)
    
    def get_current(self, user_id: str) -> Optional[Conversation]:
        """获取当前活跃对话"""
        # 查找最新的活跃对话
        for key, conv in self._current_conversations.items():
            if conv.user_id == user_id and conv.status == "active":
                return conv
        return None
    
    def get_conversation(self, user_id: str, conv_id: str) -> Optional[Conversation]:
        """获取指定对话"""
        key = f"{user_id}:{conv_id}"
        return self._current_conversations.get(key)
    
    def add_message(self, user_id: str, conv_id: str, tokens: int = 0) -> Dict:
        """
        添加消息到对话
        
        Returns:
            {
                "status": "ok|warning|exceeded",
                "message_count": 123,
                "max_messages": 100,
                "usage_percent": 0.85,
                "should_continue": True/False,
                "suggestion": "建议开启新对话"
            }
        """
        conv = self.get_conversation(user_id, conv_id)
        if not conv:
            return {"error": "对话不存在"}
        
        conv.message_count += 1
        conv.total_tokens += tokens
        conv.updated_at = datetime.now().isoformat()
        
        self._save_conversation(conv)
        
        # 检查是否超限
        msg_usage = conv.message_count / self.max_messages
        token_usage = conv.total_tokens / self.max_tokens
        usage = max(msg_usage, token_usage)
        
        result = {
            "status": "ok",
            "message_count": conv.message_count,
            "max_messages": self.max_messages,
            "total_tokens": conv.total_tokens,
            "max_tokens": self.max_tokens,
            "usage_percent": round(usage * 100, 1),
            "should_continue": False,
            "suggestion": None
        }
        
        # 超过阈值
        if usage >= 1.0:
            result["status"] = "exceeded"
            result["should_continue"] = True
            result["suggestion"] = f"📊 对话已达上限（{conv.message_count}/{self.max_messages} 消息），建议开启新对话"
        elif usage >= self.warning_threshold:
            result["status"] = "warning"
            result["suggestion"] = f"⚠️ 对话即将达上限（{usage*100:.0f}%），建议准备开启新对话"
        
        return result
    
    def continue_conversation(self, user_id: str, old_conv_id: str = None) -> Dict:
        """
        开启新对话（继承记忆）
        
        Returns:
            {
                "new_conv_id": "xxx",
                "old_conv_id": "yyy",
                "inherited_memories": 123,
                "message": "新对话已开启，继承了 XXX 条记忆"
            }
        """
        # 如果没有指定旧对话，使用当前活跃的
        if not old_conv_id:
            old_conv = self.get_current(user_id)
            old_conv_id = old_conv.id if old_conv else None
        
        # 创建新对话
        new_conv = self.create_conversation(user_id, continued_from=old_conv_id)
        
        # 继承记忆（从记忆系统）
        inherited_count = 0
        try:
            from memory_persistence import MemoryPersistence
            persistence = MemoryPersistence()
            
            # 获取用户所有记忆
            stats = persistence.get_stats(user_id)
            inherited_count = stats.get('total_memories', 0)
            
        except Exception as e:
            print(f"⚠️ 继承记忆失败：{e}")
        
        return {
            "new_conv_id": new_conv.id,
            "old_conv_id": old_conv_id,
            "inherited_memories": inherited_count,
            "message": f"✅ 新对话已开启 (ID: {new_conv.id})，继承了 {inherited_count} 条记忆",
            "conversation_url": f"conv://{user_id}/{new_conv.id}"
        }
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Conversation]:
        """获取对话历史"""
        user_convs = [
            conv for key, conv in self._current_conversations.items()
            if conv.user_id == user_id
        ]
        
        # 按创建时间排序
        user_convs.sort(key=lambda c: c.created_at, reverse=True)
        
        return user_convs[:limit]
    
    def get_chain(self, user_id: str, conv_id: str) -> List[Conversation]:
        """获取对话链（所有祖先和后代）"""
        chain = []
        
        # 向前找祖先
        current = self.get_conversation(user_id, conv_id)
        while current:
            chain.insert(0, current)
            if current.continued_from:
                current = self.get_conversation(user_id, current.continued_from)
            else:
                break
        
        # 向后找后代
        current = self.get_conversation(user_id, conv_id)
        while current and current.continued_to:
            current = self.get_conversation(user_id, current.continued_to)
            if current:
                chain.append(current)
        
        return chain
    
    def summarize_conversation(self, user_id: str, conv_id: str, summary: str):
        """保存对话摘要"""
        conv = self.get_conversation(user_id, conv_id)
        if conv:
            conv.summary = summary
            self._save_conversation(conv)
    
    def get_stats(self, user_id: str = None) -> Dict:
        """获取统计信息"""
        if user_id:
            user_convs = [
                conv for key, conv in self._current_conversations.items()
                if conv.user_id == user_id
            ]
            
            active = sum(1 for c in user_convs if c.status == "active")
            archived = sum(1 for c in user_convs if c.status == "archived")
            continued = sum(1 for c in user_convs if c.status == "continued")
            
            return {
                "user_id": user_id,
                "total_conversations": len(user_convs),
                "active": active,
                "archived": archived,
                "continued": continued,
                "current_conv": self.get_current(user_id).id if self.get_current(user_id) else None
            }
        else:
            return {
                "total_users": len(set(c.user_id for c in self._current_conversations.values())),
                "total_conversations": len(self._current_conversations)
            }
    
    def auto_check(self, user_id: str, conv_id: str) -> Optional[Dict]:
        """
        自动检查对话状态
        
        Returns:
            None - 正常
            Dict - 需要处理（包含建议）
        """
        result = self.add_message(user_id, conv_id, 0)
        
        if result["should_continue"]:
            return {
                "action": "continue",
                "reason": result["suggestion"],
                "usage_percent": result["usage_percent"]
            }
        
        return None

# ==================== 使用示例 ====================

async def demo():
    """演示使用"""
    print("🚀 灵犀对话管理器演示\n")
    
    manager = ConversationManager()
    
    # 创建对话
    print("📝 创建对话...")
    conv1 = manager.create_conversation("user_123")
    print(f"  对话 1: {conv1.id}")
    
    # 添加消息
    print("\n💬 添加消息...")
    for i in range(5):
        result = manager.add_message("user_123", conv1.id, tokens=100)
        print(f"  消息 {i+1}: {result['message_count']}/{result['max_messages']} ({result['usage_percent']}%)")
    
    # 开启新对话
    print("\n🔄 开启新对话...")
    result = manager.continue_conversation("user_123", conv1.id)
    print(f"  {result['message']}")
    
    # 获取对话链
    print("\n🔗 对话链:")
    chain = manager.get_chain("user_123", result['new_conv_id'])
    for conv in chain:
        status_icon = "✅" if conv.status == "active" else "🔗" if conv.status == "continued" else "📦"
        print(f"  {status_icon} {conv.id} (消息数：{conv.message_count})")
    
    # 统计
    print("\n📊 统计:")
    stats = manager.get_stats("user_123")
    print(f"  总对话数：{stats['total_conversations']}")
    print(f"  活跃：{stats['active']}")
    print(f"  已延续：{stats['continued']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
