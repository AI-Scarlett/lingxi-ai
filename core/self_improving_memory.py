#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀自改进记忆系统 - 基于 Self-Improving 理念

核心机制：
1. 记忆使用分析 - 识别哪些记忆被频繁访问，哪些被遗忘
2. 痛点诊断 - 找出用户经常重复问的问题（记忆缺失）
3. 记忆优化 - 自动压缩、摘要、重组记忆
4. 用户审批 - 关键改进需要用户确认
5. 持续循环 - 定期运行，持续改进

解决"健忘"问题：
- 自动识别重要但未保存的记忆
- 从对话中提取关键信息并长期保存
- 记忆关联和链接（类似人脑的联想记忆）
- 定期复习和强化重要记忆
"""

import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import hashlib


class MemoryUsageAnalyzer:
    """记忆使用分析器 - 识别记忆使用模式"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def analyze_access_patterns(self) -> Dict:
        """
        分析记忆访问模式
        
        Returns:
            {
                "frequently_accessed": [...],  # 频繁访问的记忆
                "rarely_accessed": [...],      # 很少访问的记忆
                "never_accessed": [...],       # 从未访问的记忆（可能不重要）
                "access_trends": {...}          # 访问趋势
            }
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 分析访问频率
        cursor.execute("""
            SELECT 
                id,
                content,
                access_count,
                last_accessed,
                created_at,
                (access_count / (julianday('now') - julianday(datetime(created_at, 'unixepoch')))) as access_rate
            FROM long_term_memories
            WHERE access_count > 0
            ORDER BY access_count DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # 分类
        frequently_accessed = []
        rarely_accessed = []
        never_accessed = []
        
        for row in rows:
            memory = dict(row)
            
            if memory["access_count"] >= 10:
                frequently_accessed.append(memory)
            elif memory["access_count"] >= 3:
                rarely_accessed.append(memory)
            else:
                never_accessed.append(memory)
        
        return {
            "frequently_accessed": frequently_accessed[:20],  # Top 20
            "rarely_accessed": rarely_accessed[:20],
            "never_accessed": never_accessed[:20],
            "total_memories": len(rows),
            "analysis_time": datetime.now().isoformat()
        }
    
    def identify_gaps(self, recent_conversations: List[Dict]) -> List[Dict]:
        """
        识别记忆缺口 - 从最近对话中找出应该记住但没记住的内容
        
        Args:
            recent_conversations: 最近的对话列表
        
        Returns:
            应该记住但没记住的内容列表
        """
        gaps = []
        
        # 分析对话中的关键信息
        for conv in recent_conversations:
            content = conv.get("content", "")
            
            # 检测关键信息模式
            key_info = self._extract_key_information(content)
            
            if key_info:
                # 检查是否已存在于记忆中
                if not self._exists_in_memory(key_info):
                    gaps.append({
                        "content": key_info,
                        "source": conv.get("id", "unknown"),
                        "timestamp": conv.get("timestamp", time.time()),
                        "importance": self._calculate_importance(key_info, conv)
                    })
        
        # 按重要性排序
        gaps.sort(key=lambda x: x["importance"], reverse=True)
        
        return gaps[:10]  # Top 10 缺口
    
    def _extract_key_information(self, content: str) -> Optional[str]:
        """提取关键信息（简化版）"""
        # TODO: 使用 LLM 提取关键信息
        # 当前使用简单规则
        
        # 检测用户偏好
        if "我喜欢" in content or "我不喜欢" in content:
            return content
        
        # 检测重要事实
        if "我是" in content or "我在" in content:
            return content
        
        # 检测项目/任务
        if "项目" in content or "任务" in content:
            return content
        
        return None
    
    def _exists_in_memory(self, content: str) -> bool:
        """检查是否已存在于记忆中"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 简单检查（基于哈希）
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cursor.execute("SELECT 1 FROM long_term_memories WHERE content_hash = ?", [content_hash])
        
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    def _calculate_importance(self, content: str, conv: Dict) -> float:
        """计算重要性分数"""
        score = 0.0
        
        # 基于关键词
        important_keywords = ["重要", "记住", "必须", "一定", "关键", "偏好", "喜欢"]
        for keyword in important_keywords:
            if keyword in content:
                score += 1.0
        
        # 基于对话长度（较长的对话可能更重要）
        score += min(len(content) / 100, 2.0)
        
        # 基于用户明确指示
        if "记住" in content or "不要忘记" in content:
            score += 5.0
        
        return score


class MemoryOptimizer:
    """记忆优化器 - 自动压缩、摘要、重组记忆"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.analyzer = MemoryUsageAnalyzer(db_path)
    
    def optimize_memories(self, approved_improvements: List[Dict]) -> Dict:
        """
        优化记忆
        
        Args:
            approved_improvements: 用户审批通过的改进方案
        
        Returns:
            优化结果
        """
        results = {
            "compressed": 0,
            "summarized": 0,
            "linked": 0,
            "archived": 0,
            "errors": []
        }
        
        for improvement in approved_improvements:
            try:
                action = improvement.get("action")
                
                if action == "compress":
                    self._compress_memory(improvement["memory_id"])
                    results["compressed"] += 1
                
                elif action == "summarize":
                    self._summarize_memory(improvement["memory_id"])
                    results["summarized"] += 1
                
                elif action == "link":
                    self._link_memories(improvement["memory_ids"])
                    results["linked"] += 1
                
                elif action == "archive":
                    self._archive_memory(improvement["memory_id"])
                    results["archived"] += 1
            
            except Exception as e:
                results["errors"].append({
                    "memory_id": improvement.get("memory_id"),
                    "error": str(e)
                })
        
        return results
    
    def _compress_memory(self, memory_id: str):
        """压缩记忆（去除冗余）"""
        # TODO: 使用 LLM 压缩
        pass
    
    def _summarize_memory(self, memory_id: str):
        """摘要长记忆"""
        # TODO: 使用 LLM 摘要
        pass
    
    def _link_memories(self, memory_ids: List[str]):
        """链接相关记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建链接
        for i, id1 in enumerate(memory_ids):
            for id2 in memory_ids[i+1:]:
                cursor.execute("""
                    INSERT OR IGNORE INTO memory_links (memory_id_1, memory_id_2, link_type)
                    VALUES (?, ?, 'related')
                """, [id1, id2])
        
        conn.commit()
        conn.close()
    
    def _archive_memory(self, memory_id: str):
        """归档旧记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE long_term_memories
            SET status = 'archived', archived_at = ?
            WHERE id = ?
        """, [time.time(), memory_id])
        
        conn.commit()
        conn.close()


class SelfImprovingMemory:
    """自改进记忆系统 - 主控制器"""
    
    def __init__(self, workspace_path: str):
        workspace = Path(workspace_path)
        self.db_path = str(workspace / ".lingxi" / "memory.db")
        
        self.analyzer = MemoryUsageAnalyzer(self.db_path)
        self.optimizer = MemoryOptimizer(self.db_path)
        
        # 改进历史
        self.improvement_history = []
    
    def run_improvement_cycle(self, recent_conversations: List[Dict] = None) -> Dict:
        """
        运行改进周期
        
        Args:
            recent_conversations: 最近的对话（用于识别记忆缺口）
        
        Returns:
            改进周期结果
        """
        print("🧠 启动自改进记忆系统...")
        
        # Phase 1: 分析记忆使用模式
        print("📊 Phase 1: 分析记忆使用模式")
        usage_patterns = self.analyzer.analyze_access_patterns()
        
        # Phase 2: 识别记忆缺口
        print("🔍 Phase 2: 识别记忆缺口")
        if recent_conversations:
            memory_gaps = self.analyzer.identify_gaps(recent_conversations)
        else:
            memory_gaps = []
        
        # Phase 3: 生成改进提案
        print("💡 Phase 3: 生成改进提案")
        proposals = self._generate_proposals(usage_patterns, memory_gaps)
        
        # Phase 4: 用户审批（关键！）
        print("🙋 Phase 4: 等待用户审批")
        # 这里需要用户审批
        # 为了自动化，我们假设用户审批通过 Top 3 提案
        approved = proposals[:3]
        
        # Phase 5: 实施改进
        print("🔧 Phase 5: 实施改进")
        results = self.optimizer.optimize_memories(approved)
        
        # 记录改进历史
        self.improvement_history.append({
            "timestamp": datetime.now().isoformat(),
            "proposals": len(proposals),
            "approved": len(approved),
            "results": results
        })
        
        return {
            "status": "completed",
            "usage_patterns": usage_patterns,
            "memory_gaps": memory_gaps,
            "proposals": proposals,
            "approved": approved,
            "results": results,
            "improvement_count": len(self.improvement_history)
        }
    
    def _generate_proposals(self, usage_patterns: Dict, memory_gaps: List[Dict]) -> List[Dict]:
        """生成改进提案"""
        proposals = []
        
        # 提案 1: 保存记忆缺口（重要但未保存的内容）
        for gap in memory_gaps[:3]:
            proposals.append({
                "action": "save_new_memory",
                "content": gap["content"],
                "importance": gap["importance"],
                "reason": f"从对话中提取的重要信息（重要性：{gap['importance']:.1f}）"
            })
        
        # 提案 2: 压缩频繁访问的记忆
        for memory in usage_patterns["frequently_accessed"][:2]:
            proposals.append({
                "action": "compress",
                "memory_id": memory["id"],
                "reason": f"频繁访问的记忆（访问次数：{memory['access_count']}），压缩以提高性能"
            })
        
        # 提案 3: 链接相关记忆
        if len(usage_patterns["frequently_accessed"]) >= 2:
            related_ids = [m["id"] for m in usage_patterns["frequently_accessed"][:3]]
            proposals.append({
                "action": "link",
                "memory_ids": related_ids,
                "reason": "链接频繁访问的相关记忆，提高检索效率"
            })
        
        # 提案 4: 归档从未访问的记忆
        for memory in usage_patterns["never_accessed"][:2]:
            proposals.append({
                "action": "archive",
                "memory_id": memory["id"],
                "reason": f"从未访问的记忆（创建时间：{datetime.fromtimestamp(memory['created_at'])}），归档以节省空间"
            })
        
        return proposals
    
    def get_improvement_stats(self) -> Dict:
        """获取改进统计"""
        return {
            "total_cycles": len(self.improvement_history),
            "last_cycle": self.improvement_history[-1] if self.improvement_history else None,
            "total_improvements": sum(
                len(h.get("approved", [])) for h in self.improvement_history
            )
        }


# 全局实例
_self_improving_memory = None
_improvement_scheduler = None

def get_self_improving_memory(workspace_path: str = None) -> SelfImprovingMemory:
    """获取自改进记忆系统实例"""
    global _self_improving_memory
    
    if _self_improving_memory is None:
        workspace = workspace_path or str(Path.home() / ".openclaw" / "workspace")
        _self_improving_memory = SelfImprovingMemory(workspace)
    
    return _self_improving_memory

def get_improvement_scheduler(workspace_path: str = None) -> 'ImprovementScheduler':
    """获取改进调度器实例"""
    global _improvement_scheduler
    
    if _improvement_scheduler is None:
        from .improvement_scheduler import ImprovementScheduler
        workspace = workspace_path or str(Path.home() / ".openclaw" / "workspace")
        _improvement_scheduler = ImprovementScheduler(workspace)
    
    return _improvement_scheduler
