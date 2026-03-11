#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中期记忆 (Mid-Term Memory)

特性：
- 容量：最近 7 天
- 存储：SQLite
- 过期：7 天自动归档到 LTM
- 响应：<500ms
"""

import time
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid


class MidTermMemory:
    """中期记忆存储"""
    
    def __init__(self, db_path: str = "~/.openclaw/workspace/.lingxi/memos.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建中期记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mid_term_memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                importance REAL DEFAULT 5.0,
                metadata TEXT,
                created_at REAL,
                last_accessed REAL,
                access_count INTEGER DEFAULT 0,
                tags TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mtm_importance ON mid_term_memories(importance DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mtm_created ON mid_term_memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mtm_accessed ON mid_term_memories(last_accessed)")
        
        conn.commit()
        conn.close()
    
    async def add(self, content: str, importance: float = 5.0, metadata: dict = None) -> dict:
        """添加记忆"""
        memory_id = str(uuid.uuid4())[:8]
        now = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO mid_term_memories (id, content, importance, metadata, created_at, last_accessed, access_count, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            content,
            importance,
            json.dumps(metadata or {}),
            now,
            now,
            0,
            json.dumps(metadata.get("tags", []) if metadata else [])
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "id": memory_id,
            "content": content,
            "importance": importance,
            "created_at": now
        }
    
    async def get(self, memory_id: str) -> Optional[dict]:
        """获取记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM mid_term_memories WHERE id = ?
        """, (memory_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 更新访问时间
            await self._touch(memory_id)
            
            return dict(row)
        return None
    
    async def _touch(self, memory_id: str):
        """更新访问时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE mid_term_memories 
            SET last_accessed = ?, access_count = access_count + 1 
            WHERE id = ?
        """, (time.time(), memory_id))
        
        conn.commit()
        conn.close()
    
    async def search(self, query: str, top_k: int = 10) -> List[dict]:
        """搜索记忆（FTS5 全文检索）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 简单关键词搜索
        query_lower = f"%{query.lower()}%"
        
        cursor.execute("""
            SELECT * FROM mid_term_memories 
            WHERE LOWER(content) LIKE ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        """, (query_lower, top_k))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # 更新访问时间
        for result in results:
            await self._touch(result["id"])
        
        return results
    
    async def get_recent(self, days: int = 7, limit: int = 100) -> List[dict]:
        """获取最近 N 天的记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = time.time() - (days * 86400)
        
        cursor.execute("""
            SELECT * FROM mid_term_memories 
            WHERE created_at > ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (cutoff, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    async def delete(self, memory_id: str):
        """删除记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM mid_term_memories WHERE id = ?", (memory_id,))
        
        conn.commit()
        conn.close()
    
    async def cleanup_old(self, days: int = 7) -> List[str]:
        """清理超过 N 天的记忆（归档到 LTM）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = time.time() - (days * 86400)
        
        # 获取要归档的记忆
        cursor.execute("""
            SELECT id, content, importance, metadata, created_at 
            FROM mid_term_memories 
            WHERE created_at < ?
        """, (cutoff,))
        
        old_memories = [dict(row) for row in cursor.fetchall()]
        
        # 删除旧记忆
        cursor.execute("DELETE FROM mid_term_memories WHERE created_at < ?", (cutoff,))
        
        conn.commit()
        conn.close()
        
        return [m["id"] for m in old_memories]
    
    def stats(self) -> dict:
        """统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM mid_term_memories")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(importance) FROM mid_term_memories")
        avg_importance = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total": total,
            "avg_importance": round(avg_importance, 2)
        }
