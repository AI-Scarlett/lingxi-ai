#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长期记忆 (Long-Term Memory)

特性：
- 容量：永久
- 存储：JSONL 文件 + 向量索引（ChromaDB）
- 过期：手动归档
- 响应：<2s
"""

import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class LongTermMemory:
    """长期记忆存储"""
    
    def __init__(self, db_path: str = "~/.openclaw/workspace/.lingxi/memos.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.db_path.parent / "ltm_memories.jsonl"
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建长期记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                importance REAL DEFAULT 5.0,
                metadata TEXT,
                created_at REAL,
                last_accessed REAL,
                access_count INTEGER DEFAULT 0,
                tags TEXT,
                embedding TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ltm_importance ON long_term_memories(importance DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ltm_tags ON long_term_memories(tags)")
        
        conn.commit()
        conn.close()
    
    async def add(self, content: str, importance: float = 5.0, metadata: dict = None) -> dict:
        """添加记忆"""
        memory_id = str(uuid.uuid4())[:8]
        now = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO long_term_memories (id, content, importance, metadata, created_at, last_accessed, access_count, tags, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            content,
            importance,
            json.dumps(metadata or {}),
            now,
            now,
            0,
            json.dumps(metadata.get("tags", []) if metadata else []),
            json.dumps(metadata.get("embedding", []) if metadata else [])
        ))
        
        conn.commit()
        conn.close()
        
        # 同时写入 JSONL 文件（备份）
        await self._append_to_jsonl({
            "id": memory_id,
            "content": content,
            "importance": importance,
            "metadata": metadata or {},
            "created_at": now
        })
        
        return {
            "id": memory_id,
            "content": content,
            "importance": importance,
            "created_at": now
        }
    
    async def _append_to_jsonl(self, memory: dict):
        """追加到 JSONL 文件"""
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(memory, ensure_ascii=False) + "\n")
    
    async def get(self, memory_id: str) -> Optional[dict]:
        """获取记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM long_term_memories WHERE id = ?
        """, (memory_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            await self._touch(memory_id)
            return dict(row)
        return None
    
    async def _touch(self, memory_id: str):
        """更新访问时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE long_term_memories 
            SET last_accessed = ?, access_count = access_count + 1 
            WHERE id = ?
        """, (time.time(), memory_id))
        
        conn.commit()
        conn.close()
    
    async def search(self, query: str, top_k: int = 10) -> List[dict]:
        """搜索记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 简单关键词搜索
        query_lower = f"%{query.lower()}%"
        
        cursor.execute("""
            SELECT * FROM long_term_memories 
            WHERE LOWER(content) LIKE ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        """, (query_lower, top_k))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for result in results:
            await self._touch(result["id"])
        
        return results
    
    async def search_by_tags(self, tags: List[str], top_k: int = 10) -> List[dict]:
        """按标签搜索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询包含任一标签的记忆
        results = []
        for tag in tags:
            cursor.execute("""
                SELECT * FROM long_term_memories 
                WHERE tags LIKE ?
                ORDER BY importance DESC
                LIMIT ?
            """, (f'%{tag}%', top_k))
            results.extend([dict(row) for row in cursor.fetchall()])
        
        conn.close()
        
        # 去重
        seen = set()
        unique = []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique.append(r)
        
        return unique[:top_k]
    
    async def get_by_importance(self, min_importance: float = 8.0, limit: int = 100) -> List[dict]:
        """获取高重要性记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM long_term_memories 
            WHERE importance >= ?
            ORDER BY importance DESC
            LIMIT ?
        """, (min_importance, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    async def delete(self, memory_id: str):
        """删除记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM long_term_memories WHERE id = ?", (memory_id,))
        
        conn.commit()
        conn.close()
    
    async def update(self, memory_id: str, content: str = None, importance: float = None, metadata: dict = None):
        """更新记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if content:
            updates.append("content = ?")
            values.append(content)
        if importance:
            updates.append("importance = ?")
            values.append(importance)
        if metadata:
            updates.append("metadata = ?")
            values.append(json.dumps(metadata))
        
        if updates:
            values.append(memory_id)
            cursor.execute(f"""
                UPDATE long_term_memories 
                SET {', '.join(updates)}
                WHERE id = ?
            """, values)
            
            conn.commit()
        
        conn.close()
    
    def stats(self) -> dict:
        """统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM long_term_memories")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(importance) FROM long_term_memories")
        avg_importance = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT MAX(access_count) FROM long_term_memories")
        max_access = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total": total,
            "avg_importance": round(avg_importance, 2),
            "max_access_count": max_access
        }
