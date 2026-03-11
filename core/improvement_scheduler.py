#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀改进提案定时调度器

功能：
- 累积改进提案
- 定时推送审批（7:00/12:00/21:00）
- 飞书消息推送
- 审批结果处理
"""

import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class ImprovementProposal:
    """改进提案"""
    id: str
    type: str  # save_memory/compress/link/archive
    title: str
    description: str
    importance: float  # 1-10
    created_at: float
    data: Dict
    status: str = "pending"  # pending/approved/deferred/rejected


class ImprovementScheduler:
    """改进提案调度器"""
    
    def __init__(self, workspace_path: str):
        workspace = Path(workspace_path)
        self.db_path = str(workspace / ".lingxi" / "improvements.db")
        self.config_path = workspace / ".lingxi" / "improvement_config.json"
        
        # 审批时间配置
        self.approval_times = ["07:00", "12:00", "21:00"]
        
        # 飞书配置
        self.feishu_enabled = False
        self.feishu_user_id = None
        
        self._init_db()
        self._load_config()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id TEXT PRIMARY KEY,
                type TEXT,
                title TEXT,
                description TEXT,
                importance REAL,
                created_at REAL,
                data TEXT,
                status TEXT DEFAULT 'pending',
                approved_at REAL,
                approved_by TEXT,
                feedback TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON proposals(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON proposals(created_at)")
        
        conn.commit()
        conn.close()
    
    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text())
            self.approval_times = config.get("approval_times", self.approval_times)
            self.feishu_enabled = config.get("feishu_enabled", False)
            self.feishu_user_id = config.get("feishu_user_id")
    
    def add_proposal(self, proposal: ImprovementProposal):
        """添加改进提案"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO proposals (
                id, type, title, description, importance, 
                created_at, data, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            proposal.id,
            proposal.type,
            proposal.title,
            proposal.description,
            proposal.importance,
            proposal.created_at,
            json.dumps(proposal.data),
            proposal.status
        ])
        
        conn.commit()
        conn.close()
    
    def get_pending_proposals(self, since: float = None) -> List[ImprovementProposal]:
        """获取待审批的提案"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if since:
            cursor.execute("""
                SELECT * FROM proposals 
                WHERE status = 'pending' AND created_at >= ?
                ORDER BY importance DESC
            """, [since])
        else:
            cursor.execute("""
                SELECT * FROM proposals 
                WHERE status = 'pending'
                ORDER BY importance DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        proposals = []
        for row in rows:
            data = dict(row)
            data["data"] = json.loads(data["data"])
            proposals.append(ImprovementProposal(**data))
        
        return proposals
    
    def format_approval_message(self, proposals: List[ImprovementProposal]) -> str:
        """格式化审批消息"""
        if not proposals:
            return "🎉 暂无待审批的改进提案"
        
        message = f"""# 🧠 灵犀自改进系统 · 审批通知

**时间：** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**待审批提案：** {len(proposals)} 个

---

"""
        
        for i, proposal in enumerate(proposals[:10], 1):  # 最多显示 10 个
            importance_emoji = "🔥" if proposal.importance >= 8 else "⚠️" if proposal.importance >= 5 else "💡"
            
            message += f"""## {importance_emoji} 提案 {i}: {proposal.title}

**类型：** {self._get_type_name(proposal.type)}
**重要性：** {proposal.importance:.1f}/10
**描述：** {proposal.description}

**审批选项：**
- ✅ 批准 - 立即实施
- 🔧 调整 - 修改后实施
- ⏸️ 推迟 - 稍后再说
- ❌ 拒绝 - 不予实施

---

"""
        
        if len(proposals) > 10:
            message += f"\n*还有 {len(proposals) - 10} 个提案，请在 Dashboard 中查看*\n"
        
        message += """---

**快速审批：**
回复以下命令进行审批：
- `批准 1,2,3` - 批准提案 1,2,3
- `调整 1 修改内容...` - 调整提案 1
- `推迟 4,5` - 推迟提案 4,5
- `拒绝 6` - 拒绝提案 6

**Dashboard 查看：** http://localhost:8765/improvements
"""
        
        return message
    
    def _get_type_name(self, proposal_type: str) -> str:
        """获取类型名称"""
        type_names = {
            "save_memory": "💾 保存记忆",
            "compress": "🗜️ 压缩记忆",
            "link": "🔗 链接记忆",
            "archive": "📦 归档记忆",
            "optimize": "⚡ 性能优化"
        }
        return type_names.get(proposal_type, proposal_type)
    
    async def send_approval_notification(self):
        """发送审批通知"""
        # 获取待审批提案
        proposals = self.get_pending_proposals()
        
        if not proposals:
            print("✅ 无待审批提案，跳过通知")
            return
        
        # 格式化消息
        message = self.format_approval_message(proposals)
        
        # 发送到飞书
        if self.feishu_enabled and self.feishu_user_id:
            await self._send_feishu_message(message)
        
        # 保存到发送历史
        self._save_notification_history(proposals)
        
        print(f"✅ 已发送 {len(proposals)} 个改进提案的审批通知")
    
    async def _send_feishu_message(self, message: str):
        """发送飞书消息"""
        try:
            # 使用 OpenClaw 的消息发送功能
            from openclaw.runtime import get_runtime
            runtime = get_runtime()
            
            await runtime.send_message(
                channel="feishu",
                target=f"user:{self.feishu_user_id}",
                message=message
            )
        except Exception as e:
            print(f"❌ 发送飞书消息失败：{e}")
    
    def _save_notification_history(self, proposals: List[ImprovementProposal]):
        """保存通知历史"""
        history_file = Path(self.db_path).parent / "notification_history.json"
        
        history = []
        if history_file.exists():
            history = json.loads(history_file.read_text())
        
        history.append({
            "timestamp": time.time(),
            "count": len(proposals),
            "proposal_ids": [p.id for p in proposals]
        })
        
        # 保留最近 30 天的记录
        cutoff = time.time() - (30 * 86400)
        history = [h for h in history if h["timestamp"] > cutoff]
        
        history_file.write_text(json.dumps(history, indent=2))
    
    def process_approval(self, user_id: str, action: str, proposal_ids: List[str], feedback: str = None):
        """处理用户审批"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        status_map = {
            "批准": "approved",
            "调整": "refined",
            "推迟": "deferred",
            "拒绝": "rejected"
        }
        
        status = status_map.get(action, "pending")
        
        for proposal_id in proposal_ids:
            cursor.execute("""
                UPDATE proposals 
                SET status = ?, approved_at = ?, approved_by = ?, feedback = ?
                WHERE id = ?
            """, [status, time.time(), user_id, feedback, proposal_id])
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已处理审批：{action} 提案 {proposal_ids}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 总数统计
        cursor.execute("SELECT COUNT(*) FROM proposals")
        stats["total"] = cursor.fetchone()[0]
        
        # 状态统计
        cursor.execute("SELECT status, COUNT(*) FROM proposals GROUP BY status")
        stats["by_status"] = dict(cursor.fetchall())
        
        # 类型统计
        cursor.execute("SELECT type, COUNT(*) FROM proposals GROUP BY type")
        stats["by_type"] = dict(cursor.fetchall())
        
        # 最近 7 天趋势
        seven_days_ago = time.time() - (7 * 86400)
        cursor.execute("""
            SELECT date(datetime(created_at, 'unixepoch')) as date, COUNT(*) 
            FROM proposals 
            WHERE created_at > ?
            GROUP BY date
        """, [seven_days_ago])
        stats["trend"] = dict(cursor.fetchall())
        
        conn.close()
        
        return stats
    
    def cleanup_old_proposals(self, days: int = 30):
        """清理旧提案"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = time.time() - (days * 86400)
        
        cursor.execute("""
            DELETE FROM proposals 
            WHERE status IN ('deferred', 'rejected') AND created_at < ?
        """, [cutoff])
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ 已清理 {deleted} 个旧提案")


# 定时任务调度
async def run_scheduler():
    """运行定时调度器"""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    workspace = str(Path.home() / ".openclaw" / "workspace")
    scheduler = ImprovementScheduler(workspace)
    
    # 创建调度器
    sched = AsyncIOScheduler()
    
    # 添加定时任务（7:00/12:00/21:00）
    for time_str in scheduler.approval_times:
        hour, minute = map(int, time_str.split(":"))
        
        sched.add_job(
            scheduler.send_approval_notification,
            CronTrigger(hour=hour, minute=minute),
            id=f"approval_{time_str}",
            name=f"改进审批通知 - {time_str}"
        )
    
    # 启动调度器
    sched.start()
    print(f"✅ 改进审批调度器已启动 - 审批时间：{scheduler.approval_times}")
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        sched.shutdown()


# 便捷函数
def get_improvement_scheduler(workspace_path: str = None) -> ImprovementScheduler:
    """获取改进调度器实例"""
    workspace = workspace_path or str(Path.home() / ".openclaw" / "workspace")
    return ImprovementScheduler(workspace)


if __name__ == "__main__":
    # 测试运行
    asyncio.run(run_scheduler())
