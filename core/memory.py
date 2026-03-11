#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀记忆系统 - 三层架构（MemOS 启发）

- 短期记忆：Session 级，内存存储，快速访问
- 中期记忆：天级，SQLite 存储，支持检索
- 长期记忆：永久，JSONL + 向量，可迁移
"""

import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

class ShortTermMemory:
    """短期记忆 - Session 级，内存存储"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.sessions: Dict[str, List[Dict]] = {}
    
    def add(self, session_id: str, message: Dict):
        """添加消息到短期记忆"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            **message,
            "timestamp": time.time()
        })
        
        # 限制大小
        if len(self.sessions[session_id]) > self.max_size:
            self.sessions[session_id] = self.sessions[session_id][-self.max_size:]
    
    def get(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取最近的消息"""
        return self.sessions.get(session_id, [])[-limit:]
    
    def clear(self, session_id: str = None):
        """清除记忆"""
        if session_id:
            self.sessions.pop(session_id, None)
        else:
            self.sessions.clear()


class MidTermMemory:
    """中期记忆 - 天级，SQLite 存储"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                tokens INTEGER DEFAULT 0,
                summary TEXT,
                created_at REAL,
                channel TEXT,
                user_id TEXT
            )
        """)
        
        # 索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON conversations(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON conversations(user_id)")
        
        conn.commit()
        conn.close()
    
    def add(self, conversation: Dict):
        """添加对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO conversations (
                id, session_id, role, content, tokens, summary, 
                created_at, channel, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            conversation.get("id", f"conv_{int(time.time()*1000)}"),
            conversation.get("session_id"),
            conversation.get("role"),
            conversation.get("content", "")[:5000],
            conversation.get("tokens", 0),
            conversation.get("summary", ""),
            conversation.get("created_at", time.time()),
            conversation.get("channel", "unknown"),
            conversation.get("user_id", "unknown")
        ])
        
        conn.commit()
        conn.close()
    
    def get_by_session(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取指定 session 的对话"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, [session_id, limit])
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_by_time_range(self, start: float, end: float, limit: int = 100) -> List[Dict]:
        """获取指定时间范围的对话"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE created_at BETWEEN ? AND ?
            ORDER BY created_at DESC 
            LIMIT ?
        """, [start, end, limit])
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_old(self, days: int = 7):
        """删除旧数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = time.time() - (days * 86400)
        cursor.execute("DELETE FROM conversations WHERE created_at < ?", [cutoff])
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted


class LongTermMemory:
    """长期记忆 - 永久，JSONL 存储，可迁移"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 记忆文件按日期分片
        self.current_file = self._get_today_file()
        self.index = self._load_index()
    
    def _get_today_file(self) -> Path:
        """获取今日文件"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.storage_path / f"memories_{today}.jsonl"
    
    def _load_index(self) -> Dict:
        """加载索引"""
        index_file = self.storage_path / "index.json"
        if index_file.exists():
            return json.loads(index_file.read_text())
        return {"memories": [], "summaries": {}}
    
    def add(self, memory: Dict, auto_summary: bool = True):
        """添加记忆"""
        memory_id = memory.get("id", f"mem_{int(time.time()*1000)}")
        
        # 生成记忆哈希（用于去重）
        content_hash = hashlib.md5(
            f"{memory.get('role')}:{memory.get('content', '')[:500]}".encode()
        ).hexdigest()
        
        memory_entry = {
            "id": memory_id,
            "content_hash": content_hash,
            "timestamp": time.time(),
            "date": datetime.now().isoformat(),
            **memory
        }
        
        # 自动摘要（如果内容较长）
        if auto_summary and len(memory.get("content", "")) > 500:
            memory_entry["summary"] = self._auto_summarize(memory.get("content", ""))
        
        # 写入 JSONL
        with open(self.current_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(memory_entry, ensure_ascii=False) + "\n")
        
        # 更新索引
        self.index["memories"].append({
            "id": memory_id,
            "file": self.current_file.name,
            "timestamp": memory_entry["timestamp"],
            "summary": memory_entry.get("summary", "")[:100]
        })
        
        self._save_index()
        
        return memory_id
    
    def _auto_summarize(self, content: str, max_length: int = 200) -> str:
        """自动摘要（简单版）"""
        # TODO: 使用 LLM 进行智能摘要
        # 当前使用简单截断
        return content[:max_length] + "..." if len(content) > max_length else content
    
    def _save_index(self):
        """保存索引"""
        index_file = self.storage_path / "index.json"
        index_file.write_text(json.dumps(self.index, ensure_ascii=False, indent=2))
    
    def search(self, query: str = None, date_range: tuple = None, limit: int = 50) -> List[Dict]:
        """搜索记忆"""
        results = []
        
        # 从索引开始
        for mem_info in reversed(self.index["memories"][-limit*2:]):
            file_path = self.storage_path / mem_info["file"]
            if not file_path.exists():
                continue
            
            # 读取文件查找
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        memory = json.loads(line)
                        
                        # 过滤
                        if query and query.lower() not in memory.get("content", "").lower():
                            continue
                        
                        if date_range:
                            ts = memory.get("timestamp", 0)
                            if ts < date_range[0] or ts > date_range[1]:
                                continue
                        
                        results.append(memory)
                        
                        if len(results) >= limit:
                            return results
                    except:
                        continue
        
        return results
    
    def export(self, output_path: str) -> str:
        """导出记忆（可迁移）"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "memories": []
        }
        
        # 收集所有记忆
        for mem_info in self.index["memories"]:
            file_path = self.storage_path / mem_info["file"]
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            export_data["memories"].append(json.loads(line))
                        except:
                            continue
        
        output.write_text(json.dumps(export_data, ensure_ascii=False, indent=2))
        
        return str(output)
    
    def import_from(self, input_path: str) -> int:
        """导入记忆（从迁移文件）"""
        input_file = Path(input_path)
        if not input_file.exists():
            return 0
        
        try:
            data = json.loads(input_file.read_text())
            imported = 0
            
            for memory in data.get("memories", []):
                # 避免重复
                content_hash = hashlib.md5(
                    f"{memory.get('role')}:{memory.get('content', '')[:500]}".encode()
                ).hexdigest()
                
                # 检查是否已存在
                exists = False
                for mem_info in self.index["memories"]:
                    if mem_info.get("content_hash") == content_hash:
                        exists = True
                        break
                
                if not exists:
                    self.add(memory, auto_summary=False)
                    imported += 1
            
            return imported
        except Exception as e:
            print(f"导入失败：{e}")
            return 0


class MemorySystem:
    """统一记忆系统接口"""
    
    def __init__(self, workspace_path: str):
        workspace = Path(workspace_path)
        
        # 三层记忆
        self.short_term = ShortTermMemory(max_size=100)
        self.mid_term = MidTermMemory(str(workspace / ".lingxi" / "memory.db"))
        self.long_term = LongTermMemory(str(workspace / ".lingxi" / "memories"))
        
        # 自动清理策略
        self.auto_cleanup_days = 7
    
    def add_message(self, session_id: str, role: str, content: str, **kwargs):
        """添加消息到所有层级"""
        message = {
            "session_id": session_id,
            "role": role,
            "content": content,
            **kwargs
        }
        
        # 短期记忆
        self.short_term.add(session_id, message)
        
        # 中期记忆
        self.mid_term.add({
            "id": f"conv_{int(time.time()*1000)}",
            **message
        })
        
        # 长期记忆（重要对话）
        if len(content) > 100 or role == "user":
            self.long_term.add(message)
    
    def get_context(self, session_id: str, limit: int = 20) -> List[Dict]:
        """获取对话上下文"""
        # 优先从短期记忆获取
        context = self.short_term.get(session_id, limit)
        
        # 如果不足，从中期记忆补充
        if len(context) < limit:
            mid_term = self.mid_term.get_by_session(session_id, limit - len(context))
            context = mid_term + context
        
        return context[-limit:]
    
    def cleanup(self):
        """清理旧数据"""
        deleted = self.mid_term.delete_old(self.auto_cleanup_days)
        print(f"清理了 {deleted} 条中期记忆")
    
    def export_memory(self, output_path: str) -> str:
        """导出记忆"""
        return self.long_term.export(output_path)
    
    def import_memory(self, input_path: str) -> int:
        """导入记忆"""
        return self.long_term.import_from(input_path)


# 单例
_memory_system = None

def get_memory_system(workspace_path: str = None) -> MemorySystem:
    """获取记忆系统实例"""
    global _memory_system
    
    if _memory_system is None:
        workspace = workspace_path or Path.home() / ".openclaw" / "workspace"
        _memory_system = MemorySystem(str(workspace))
    
    return _memory_system
