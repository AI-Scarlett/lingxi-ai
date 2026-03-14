#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Agent 积分管理系统 v1.0

功能：
1. Agent 积分计算、存储、查询
2. 等级评定
3. 奖惩记录管理
4. 资源分配策略

作者：Scarlett
创建时间：2026-03-14
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


# ============ 配置 ============

class AgentLevel(Enum):
    """Agent 等级"""
    ACE = "王牌"           # 500+
    DIAMOND = "钻石"       # 300-499
    GOLD = "金牌"          # 200-299
    SILVER = "银牌"        # 100-199
    NORMAL = "普通"        # 50-99
    WATCH = "观察"         # 0-49
    ISOLATED = "隔离"      # <0


# 积分规则
CREDIT_RULES = {
    # 奖励
    "on_time_task": 5,          # 按时完成任务
    "quality_report": 2,        # 高质量汇报
    "inspection_good": 3,       # 巡察优秀
    "daily_perfect": 5,         # 每日无失误
    "complex_task": 10,         # 复杂任务
    "weekly_champion": 50,      # 周冠军
    
    # 处罚
    "late_report": -5,          # 汇报延迟
    "invalid_format": -3,       # 格式错误
    "task_failed": -10,         # 任务失败
    "inspection_issue": -5,     # 巡察问题
    "resource_waste": -3,       # 资源浪费
}

# 等级阈值
LEVEL_THRESHOLDS = {
    AgentLevel.ACE: 500,
    AgentLevel.DIAMOND: 300,
    AgentLevel.GOLD: 200,
    AgentLevel.SILVER: 100,
    AgentLevel.NORMAL: 50,
    AgentLevel.WATCH: 0,
}

# 资源分配策略
RESOURCE_POLICY = {
    AgentLevel.ACE: {
        "cpu_cores": 8,
        "gpu_priority": "exclusive",
        "token_quota": 100000,
        "task_priority": 1.5,
    },
    AgentLevel.DIAMOND: {
        "cpu_cores": 4,
        "gpu_priority": "preferred",
        "token_quota": 50000,
        "task_priority": 1.3,
    },
    AgentLevel.GOLD: {
        "cpu_cores": 2,
        "gpu_priority": "normal",
        "token_quota": 20000,
        "task_priority": 1.1,
    },
    AgentLevel.SILVER: {
        "cpu_cores": 2,
        "gpu_priority": "normal",
        "token_quota": 10000,
        "task_priority": 1.0,
    },
    AgentLevel.NORMAL: {
        "cpu_cores": 1,
        "gpu_priority": "idle_only",
        "token_quota": 5000,
        "task_priority": 0.8,
    },
    AgentLevel.WATCH: {
        "cpu_cores": 0.5,
        "gpu_priority": "forbidden",
        "token_quota": 1000,
        "task_priority": 0.5,
    },
    AgentLevel.ISOLATED: {
        "cpu_cores": 0.5,
        "gpu_priority": "forbidden",
        "token_quota": 500,
        "task_priority": 0.0,
    },
}


# ============ 数据模型 ============

@dataclass
class CreditRecord:
    """积分记录"""
    timestamp: str
    action: str           # 行为类型
    points: int           # 积分变化
    reason: str           # 原因描述
    task_id: Optional[str] = None
    inspector: Optional[str] = None


@dataclass
class AgentCredit:
    """Agent 积分数据"""
    agent_id: str
    score: int = 100      # 初始 100 分
    level: str = "普通"
    total_earned: int = 0
    total_spent: int = 0
    records: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 统计
    tasks_completed: int = 0
    tasks_failed: int = 0
    perfect_days: int = 0
    current_streak: int = 0
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


# ============ 积分管理器 ============

class AgentCreditManager:
    """Agent 积分管理器"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".openclaw" / "workspace" / "data"
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.agents_file = self.data_dir / "agent_credit.json"
        self.history_file = self.data_dir / "agent_credit_history.json"
        
        self.agents: Dict[str, AgentCredit] = {}
        self.load()
    
    def load(self):
        """加载积分数据"""
        if self.agents_file.exists():
            try:
                data = json.loads(self.agents_file.read_text(encoding='utf-8'))
                for agent_id, agent_data in data.items():
                    self.agents[agent_id] = AgentCredit.from_dict(agent_data)
                print(f"✅ 加载 {len(self.agents)} 个 Agent 积分数据")
            except Exception as e:
                print(f"⚠️ 加载积分数据失败：{e}")
                self.agents = {}
    
    def save(self):
        """保存积分数据"""
        try:
            data = {aid: agent.to_dict() for aid, agent in self.agents.items()}
            self.agents_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            print(f"❌ 保存积分数据失败：{e}")
    
    def get_or_create(self, agent_id: str) -> AgentCredit:
        """获取或创建 Agent 积分"""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentCredit(agent_id=agent_id)
            self.save()
        return self.agents[agent_id]
    
    def add_points(self, agent_id: str, points: int, action: str, reason: str, task_id: Optional[str] = None):
        """添加/扣除积分"""
        agent = self.get_or_create(agent_id)
        agent.score += points
        agent.total_earned += max(0, points)
        agent.total_spent += max(0, -points)
        agent.updated_at = datetime.now().isoformat()
        
        # 记录
        record = CreditRecord(
            timestamp=datetime.now().isoformat(),
            action=action,
            points=points,
            reason=reason,
            task_id=task_id
        )
        agent.records.append(asdict(record))
        
        # 保留最近 100 条记录
        if len(agent.records) > 100:
            agent.records = agent.records[-100:]
        
        # 更新等级
        agent.level = self._calculate_level(agent.score).value
        
        # 统计
        if action == "on_time_task":
            agent.tasks_completed += 1
            agent.current_streak += 1
        elif action == "task_failed":
            agent.tasks_failed += 1
            agent.current_streak = 0
        
        self.save()
        print(f"📊 Agent {agent_id}: {points:+d} 分 → {agent.score} 分 ({agent.level})")
        return agent
    
    def _calculate_level(self, score: int) -> AgentLevel:
        """根据积分计算等级"""
        for level, threshold in LEVEL_THRESHOLDS.items():
            if score >= threshold:
                return level
        return AgentLevel.ISOLATED
    
    def get_level(self, agent_id: str) -> AgentLevel:
        """获取 Agent 等级"""
        agent = self.get_or_create(agent_id)
        return AgentLevel(agent.level) if agent.level in [e.value for e in AgentLevel] else AgentLevel.NORMAL
    
    def get_resource_policy(self, agent_id: str) -> Dict:
        """获取资源分配策略"""
        level = self.get_level(agent_id)
        return RESOURCE_POLICY.get(level, RESOURCE_POLICY[AgentLevel.NORMAL])
    
    def get_ranking(self, limit: int = 10) -> List[AgentCredit]:
        """获取积分排行榜"""
        agents = list(self.agents.values())
        agents.sort(key=lambda a: a.score, reverse=True)
        return agents[:limit]
    
    def get_history(self, agent_id: str, days: int = 7) -> List[Dict]:
        """获取积分历史记录"""
        agent = self.get_or_create(agent_id)
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return [r for r in agent.records if r['timestamp'] >= cutoff]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.agents:
            return {
                "total_agents": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
            }
        
        scores = [a.score for a in self.agents.values()]
        return {
            "total_agents": len(self.agents),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "level_distribution": self._get_level_distribution(),
        }
    
    def _get_level_distribution(self) -> Dict[str, int]:
        """获取等级分布"""
        dist = {level.value: 0 for level in AgentLevel}
        for agent in self.agents.values():
            if agent.level in dist:
                dist[agent.level] += 1
        return dist
    
    def reset_daily(self):
        """每日重置（检查连续表现）"""
        now = datetime.now()
        for agent in self.agents.values():
            # 检查昨日表现
            yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_records = [
                r for r in agent.records 
                if r['timestamp'].startswith(yesterday) and r['points'] < 0
            ]
            
            if not yesterday_records:
                # 昨日无违规，奖励
                agent.perfect_days += 1
                if agent.perfect_days >= 7:
                    self.add_points(agent.agent_id, CREDIT_RULES["weekly_champion"], 
                                  "weekly_champion", "连续 7 天无违规")
                    agent.perfect_days = 0
            else:
                agent.perfect_days = 0
        
        self.save()


# ============ 工具函数 ============

def get_credit_manager() -> AgentCreditManager:
    """获取积分管理器单例"""
    if not hasattr(get_credit_manager, '_instance'):
        get_credit_manager._instance = AgentCreditManager()
    return get_credit_manager._instance


# ============ 命令行接口 ============

if __name__ == "__main__":
    import sys
    
    manager = AgentCreditManager()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python agent_credit.py list              # 列出所有 Agent")
        print("  python agent_credit.py rank              # 排行榜")
        print("  python agent_credit.py add <id> <points> <reason>")
        print("  python agent_credit.py info <id>         # 查看 Agent 信息")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        for aid, agent in manager.agents.items():
            print(f"{aid}: {agent.score} 分 ({agent.level})")
    
    elif cmd == "rank":
        ranking = manager.get_ranking()
        print("🏆 Agent 积分排行榜")
        print("=" * 50)
        for i, agent in enumerate(ranking, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal} {agent.agent_id}: {agent.score} 分 ({agent.level})")
    
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("用法：python agent_credit.py add <agent_id> <points> <reason>")
            sys.exit(1)
        agent_id = sys.argv[2]
        points = int(sys.argv[3])
        reason = " ".join(sys.argv[4:])
        manager.add_points(agent_id, points, "manual", reason)
    
    elif cmd == "info":
        if len(sys.argv) < 3:
            print("用法：python agent_credit.py info <agent_id>")
            sys.exit(1)
        agent_id = sys.argv[2]
        agent = manager.get_or_create(agent_id)
        print(f"Agent: {agent.agent_id}")
        print(f"积分：{agent.score}")
        print(f"等级：{agent.level}")
        print(f"完成任务：{agent.tasks_completed}")
        print(f"失败任务：{agent.tasks_failed}")
        print(f"完美天数：{agent.perfect_days}")
        print(f"当前连胜：{agent.current_streak}")
        
        policy = manager.get_resource_policy(agent_id)
        print(f"\n资源分配:")
        print(f"  CPU: {policy['cpu_cores']} 核")
        print(f"  GPU: {policy['gpu_priority']}")
        print(f"  Token: {policy['token_quota']}/天")
        print(f"  任务优先级：{policy['task_priority']}x")
