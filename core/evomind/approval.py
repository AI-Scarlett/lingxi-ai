#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Improving 用户审批界面

功能：
- 生成飞书卡片审批消息
- 处理用户审批回复
- 执行审批结果
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ApprovalCard:
    """审批卡片生成器"""
    
    def __init__(self):
        self.card_template = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": "🧠 灵犀自改进系统 · 审批通知",
                    "tag": "plain_text"
                }
            },
            "elements": [],
            "card_link": ""
        }
    
    def generate(self, proposals: List[dict], notification_type: str = "regular") -> dict:
        """
        生成审批卡片
        
        Args:
            proposals: 提案列表
            notification_type: 通知类型 (regular/morning/noon/night)
        
        Returns:
            飞书卡片 JSON
        """
        card = self.card_template.copy()
        
        # 设置主题色
        if notification_type == "morning":
            card["header"]["template"] = "blue"
            card["header"]["title"]["content"] = "🌅 晨间审批 · 灵犀自改进系统"
        elif notification_type == "noon":
            card["header"]["template"] = "green"
            card["header"]["title"]["content"] = "☀️ 午间审批 · 灵犀自改进系统"
        elif notification_type == "night":
            card["header"]["template"] = "purple"
            card["header"]["title"]["content"] = "🌙 晚间审批 · 灵犀自改进系统"
        
        # 添加时间信息
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**审批时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n**待审批提案：** {len(proposals)} 个"
            }
        })
        
        # 添加提案列表
        for i, proposal in enumerate(proposals[:10], 1):  # 最多显示 10 个
            card["elements"].append(self._create_proposal_element(i, proposal))
        
        # 添加审批按钮
        card["elements"].append(self._create_action_buttons(proposals))
        
        # 添加提示信息
        card["elements"].append({
            "tag": "hr"
        })
        
        card["elements"].append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": "💡 提示：点击按钮快速审批，或回复文字命令"
                }
            ]
        })
        
        return card
    
    def _create_proposal_element(self, index: int, proposal: dict) -> dict:
        """创建提案元素"""
        proposal_type = proposal.get("type", "unknown")
        importance = proposal.get("importance", 5.0)
        
        # 类型图标
        type_icons = {
            "save_memory": "💾",
            "compress": "🗜️",
            "link": "🔗",
            "archive": "📦",
            "update": "✏️"
        }
        
        # 重要性颜色
        if importance >= 9.0:
            importance_color = "red"
            importance_text = "🔴 非常重要"
        elif importance >= 7.0:
            importance_color = "orange"
            importance_text = "🟠 重要"
        else:
            importance_color = "blue"
            importance_text = "🔵 普通"
        
        return {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"### {type_icons.get(proposal_type, '📋')} 提案 {index}: {proposal.get('title', '未命名')}\n**类型：** {proposal_type} | **重要性：** {importance_text}\n**描述：** {proposal.get('description', '无描述')[:200]}"
            }
        }
    
    def _create_action_buttons(self, proposals: List[dict]) -> dict:
        """创建审批按钮"""
        buttons = []
        
        # 批量审批按钮
        if len(proposals) > 0:
            buttons.append({
                "tag": "button",
                "text": "✅ 全部批准",
                "type": "primary",
                "value": {
                    "action": "approve_all",
                    "proposal_ids": [p["id"] for p in proposals]
                }
            })
        
        # 查看 Dashboard 按钮
        buttons.append({
            "tag": "button",
            "text": "📊 查看详情",
            "type": "default",
            "url": "http://localhost:8765/improvements"
        })
        
        return {
            "tag": "action",
            "actions": buttons
        }


class ApprovalManager:
    """审批管理器"""
    
    def __init__(self, db_path: str = "~/.openclaw/workspace/.lingxi/approvals.db"):
        self.db_path = Path(db_path).expanduser()
        self.card_generator = ApprovalCard()
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        import sqlite3
        from pathlib import Path
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建提案表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id TEXT PRIMARY KEY,
                type TEXT,
                title TEXT,
                description TEXT,
                content TEXT,
                importance REAL,
                status TEXT DEFAULT 'pending',
                created_at REAL,
                updated_at REAL,
                approved_at REAL,
                approved_by TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_proposals_importance ON proposals(importance DESC)")
        
        conn.commit()
        conn.close()
    
    async def add_proposal(self, proposal: dict) -> str:
        """添加提案"""
        import sqlite3
        import uuid
        import time
        
        proposal_id = str(uuid.uuid4())[:8]
        now = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO proposals (id, type, title, description, content, importance, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
        """, (
            proposal_id,
            proposal.get("type", "unknown"),
            proposal.get("title", ""),
            proposal.get("description", ""),
            proposal.get("content", ""),
            proposal.get("importance", 5.0),
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        return proposal_id
    
    async def get_pending_proposals(self, limit: int = 10) -> List[dict]:
        """获取待审批提案"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM proposals 
            WHERE status = 'pending' 
            ORDER BY importance DESC, created_at ASC
            LIMIT ?
        """, (limit,))
        
        proposals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return proposals
    
    def generate_notification_card(self, proposals: List[dict], time_of_day: str = "regular") -> dict:
        """生成通知卡片"""
        return self.card_generator.generate(proposals, time_of_day)
    
    async def process_approval(self, user_id: str, action: str, proposal_ids: List[str]) -> dict:
        """处理审批"""
        import sqlite3
        import time
        
        now = time.time()
        results = {
            "approved": [],
            "rejected": [],
            "deferred": [],
            "refined": []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for proposal_id in proposal_ids:
            if action == "approve":
                cursor.execute("""
                    UPDATE proposals 
                    SET status = 'approved', updated_at = ?, approved_at = ?, approved_by = ?
                    WHERE id = ?
                """, (now, now, user_id, proposal_id))
                results["approved"].append(proposal_id)
            
            elif action == "reject":
                cursor.execute("""
                    UPDATE proposals 
                    SET status = 'rejected', updated_at = ?, approved_by = ?
                    WHERE id = ?
                """, (now, user_id, proposal_id))
                results["rejected"].append(proposal_id)
            
            elif action == "defer":
                cursor.execute("""
                    UPDATE proposals 
                    SET status = 'deferred', updated_at = ?
                    WHERE id = ?
                """, (now, proposal_id))
                results["deferred"].append(proposal_id)
        
        conn.commit()
        conn.close()
        
        return results
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 各状态数量
        cursor.execute("SELECT status, COUNT(*) FROM proposals GROUP BY status")
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        # 平均重要性
        cursor.execute("SELECT AVG(importance) FROM proposals WHERE status = 'pending'")
        stats["avg_importance_pending"] = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return stats


# 全局实例
_approval_manager = None


def get_approval_manager() -> ApprovalManager:
    """获取审批管理器实例"""
    global _approval_manager
    if _approval_manager is None:
        _approval_manager = ApprovalManager()
    return _approval_manager
