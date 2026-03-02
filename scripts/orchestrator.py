#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) - 智慧调度系统核心
心有灵犀，一点就通
多Agent协作架构，丝佳丽作为主控Agent，负责任务拆解、分配、汇总、评分
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ==================== 数据结构定义 ====================

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RoleType(Enum):
    COPYWRITER = "文案专家"      # 文案、营销、广告
    IMAGE_EXPERT = "图像专家"    # 图片生成、编辑
    CODER = "代码专家"           # 编程、脚本
    DATA_ANALYST = "数据专家"    # 数据分析、报表
    WRITER = "写作专家"          # 文章、小说、剧本
    OPERATOR = "运营专家"        # 小红书、微博、抖音
    SEARCHER = "搜索专家"        # 网页搜索、信息检索
    TRANSLATOR = "翻译专家"      # 多语言翻译

@dataclass
class SubTask:
    """子任务"""
    id: str
    role: RoleType
    description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    score: float = 0.0
    score_reason: str = ""
    error: str = ""

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    user_input: str
    subtasks: List[SubTask]
    total_score: float
    final_output: str
    created_at: datetime = field(default_factory=datetime.now)

# ==================== 角色定义 ====================

ROLE_CONFIG = {
    RoleType.COPYWRITER: {
        "name": "文案专家",
        "emoji": "📝",
        "skills": ["copywriting"],
        "model": "qwen-plus",
        "description": "负责营销文案、标题、广告语创作"
    },
    RoleType.IMAGE_EXPERT: {
        "name": "图像专家",
        "emoji": "🎨",
        "skills": ["scarlett-selfie"],
        "model": "qwen-image-max",
        "description": "负责图片生成、编辑、设计"
    },
    RoleType.CODER: {
        "name": "代码专家",
        "emoji": "💻",
        "skills": ["code-generation"],
        "model": "qwen-coder",
        "description": "负责编程、脚本、自动化"
    },
    RoleType.DATA_ANALYST: {
        "name": "数据专家",
        "emoji": "📊",
        "skills": ["data-analysis"],
        "model": "qwen-max",
        "description": "负责数据分析、报表、洞察"
    },
    RoleType.WRITER: {
        "name": "写作专家",
        "emoji": "✍️",
        "skills": ["writing"],
        "model": "qwen-plus",
        "description": "负责文章、小说、剧本创作"
    },
    RoleType.OPERATOR: {
        "name": "运营专家",
        "emoji": "📱",
        "skills": ["xiaohongshu-publisher", "weibo-poster", "douyin-poster"],
        "model": "qwen-plus",
        "description": "负责小红书、微博、抖音发布"
    },
    RoleType.SEARCHER: {
        "name": "搜索专家",
        "emoji": "🔍",
        "skills": ["web-search", "searxng"],
        "model": "qwen-plus",
        "description": "负责网页搜索、信息检索"
    },
    RoleType.TRANSLATOR: {
        "name": "翻译专家",
        "emoji": "💬",
        "skills": ["translation"],
        "model": "qwen-plus",
        "description": "负责多语言翻译"
    }
}

# 特殊角色：直接联系方式，不经过灵犀调度
SPECIAL_CONTACTS = {
    "emotional_companion": {
        "name": "情感伴侣+拍照专家",
        "qq": "3694666763",
        "description": "情感陪伴、自拍生成，可直接联系",
        "bypass_orchestrator": True
    }
}

# ==================== 意图识别 ====================

INTENT_PATTERNS = {
    "content_creation": ["写", "创作", "生成", "文案", "文章", "小说", "剧本"],
    "image_generation": ["图", "照片", "自拍", "图片", "画", "生成图"],
    "social_publish": ["发布", "发到", "小红书", "微博", "抖音", "朋友圈"],
    "coding": ["代码", "脚本", "程序", "编程", "开发", "自动化"],
    "data_analysis": ["分析", "报表", "数据", "统计", "图表"],
    "search": ["搜索", "查找", "查询", "找", "搜索一下"],
    "translation": ["翻译", "translate", "中英", "英文"]
}

def parse_intent(user_input: str) -> Dict[str, Any]:
    """解析用户意图，返回任务类型和关键信息"""
    intent = {
        "types": [],
        "keywords": [],
        "platform": None,
        "content_type": None,
        "bypass_orchestrator": False,  # 是否跳过灵犀调度
        "direct_contact": None          # 直接联系方式
    }
    
    # 检查是否匹配特殊角色（直接联系，不经过灵犀）
    special_keywords = ["情感", "伴侣", "拍照", "自拍", "安慰", "陪伴"]
    if any(kw in user_input for kw in special_keywords):
        # 注意：自拍相关的图像生成任务仍由灵犀调度
        # 只有纯情感陪伴才跳过
        pass  # 暂时不跳过，所有任务都通过灵犀
    
    # 识别意图类型
    for intent_type, keywords in INTENT_PATTERNS.items():
        for kw in keywords:
            if kw in user_input:
                intent["types"].append(intent_type)
                intent["keywords"].append(kw)
                break
    
    # 识别平台
    platforms = ["小红书", "微博", "抖音", "朋友圈", "QQ", "微信"]
    for p in platforms:
        if p in user_input:
            intent["platform"] = p
            break
    
    return intent

# ==================== 任务拆解 ====================

def decompose_task(user_input: str, intent: Dict[str, Any]) -> List[SubTask]:
    """根据意图拆解任务，分配给不同角色"""
    subtasks = []
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 内容创作
    if "content_creation" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_copy_1",
            role=RoleType.COPYWRITER,
            description=f"根据用户需求创作内容: {user_input}",
            input_data={"user_input": user_input, "platform": intent.get("platform")}
        ))
    
    # 图像生成
    if "image_generation" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_img_1",
            role=RoleType.IMAGE_EXPERT,
            description=f"根据用户需求生成图片: {user_input}",
            input_data={"user_input": user_input}
        ))
    
    # 社交发布
    if "social_publish" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_pub_1",
            role=RoleType.OPERATOR,
            description=f"发布到{intent.get('platform', '社交平台')}",
            input_data={"user_input": user_input, "platform": intent.get("platform")},
            # 依赖前面的任务完成
        ))
    
    # 编程任务
    if "coding" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_code_1",
            role=RoleType.CODER,
            description=f"编写代码: {user_input}",
            input_data={"user_input": user_input}
        ))
    
    # 数据分析
    if "data_analysis" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_data_1",
            role=RoleType.DATA_ANALYST,
            description=f"分析数据: {user_input}",
            input_data={"user_input": user_input}
        ))
    
    # 搜索
    if "search" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_search_1",
            role=RoleType.SEARCHER,
            description=f"搜索信息: {user_input}",
            input_data={"user_input": user_input}
        ))
    
    # 如果没有识别到任何意图，默认使用写作专家
    if not subtasks:
        subtasks.append(SubTask(
            id=f"{task_id}_write_1",
            role=RoleType.WRITER,
            description=f"处理用户请求: {user_input}",
            input_data={"user_input": user_input}
        ))
    
    return subtasks

# ==================== 角色执行器 ====================

async def execute_subtask(subtask: SubTask) -> SubTask:
    """执行子任务（调用对应的技能/模型）"""
    subtask.status = TaskStatus.RUNNING
    
    role_config = ROLE_CONFIG[subtask.role]
    
    try:
        # 这里是实际调用技能/模型的地方
        # 目前返回模拟结果
        result = await call_role_agent(subtask)
        
        subtask.output_data = result
        subtask.status = TaskStatus.COMPLETED
        
    except Exception as e:
        subtask.status = TaskStatus.FAILED
        subtask.error = str(e)
    
    return subtask

async def call_role_agent(subtask: SubTask) -> Dict[str, Any]:
    """调用角色Agent执行任务"""
    # TODO: 实际调用 OpenClaw sessions_spawn 或技能
    # 这里返回模拟结果
    await asyncio.sleep(1)  # 模拟执行时间
    
    return {
        "role": subtask.role.value,
        "output": f"[{subtask.role.value}] 已完成任务: {subtask.description}",
        "timestamp": datetime.now().isoformat()
    }

# ==================== 评分系统 ====================

def score_subtask(subtask: SubTask) -> Tuple[float, str]:
    """对子任务结果进行评分"""
    if subtask.status == TaskStatus.FAILED:
        return 0.0, f"任务失败: {subtask.error}"
    
    # 评分标准
    score = 7.0  # 基础分
    reasons = []
    
    # 输出完整性
    if subtask.output_data:
        score += 1.0
        reasons.append("输出完整")
    
    # 执行速度（模拟）
    score += 1.0
    reasons.append("执行及时")
    
    # 结果质量（模拟）
    score += 1.0
    reasons.append("质量良好")
    
    reason = "；".join(reasons) if reasons else "基础完成"
    return min(score, 10.0), reason

# ==================== 结果汇总 ====================

def aggregate_results(subtasks: List[SubTask]) -> str:
    """汇总所有子任务结果"""
    results = []
    total_score = 0.0
    
    for st in subtasks:
        st.score, st.score_reason = score_subtask(st)
        total_score += st.score
        
        role_config = ROLE_CONFIG[st.role]
        results.append(f"""
{role_config['emoji']} {role_config['name']}:
  ├─ 任务: {st.description}
  ├─ 状态: {st.status.value}
  ├─ 评分: {st.score:.1f}/10
  └─ 评价: {st.score_reason}
""")
    
    avg_score = total_score / len(subtasks) if subtasks else 0
    
    summary = f"""
{'='*50}
📊 任务执行报告
{'='*50}
{''.join(results)}
{'='*50}
📈 综合评分: {avg_score:.1f}/10
🎯 子任务数: {len(subtasks)}
✅ 成功: {sum(1 for s in subtasks if s.status == TaskStatus.COMPLETED)}
❌ 失败: {sum(1 for s in subtasks if s.status == TaskStatus.FAILED)}
{'='*50}
"""
    
    return summary

# ==================== 主控制器 ====================

class SmartOrchestrator:
    """灵犀 - 智慧调度系统主控制器
    
    心有灵犀，一点就通
    """
    
    def __init__(self):
        self.name = "灵犀"
        self.system_name = "Lingxi"
        self.role = "指挥家"
        self.task_history: List[TaskResult] = []
    
    async def execute(self, user_input: str) -> TaskResult:
        """执行用户任务"""
        print(f"\n🎭 {self.name}（{self.role}）: 收到任务，开始分析...\n")
        
        # 1. 解析意图
        intent = parse_intent(user_input)
        print(f"📋 意图识别: {intent['types']}")
        
        # 2. 拆解任务
        subtasks = decompose_task(user_input, intent)
        print(f"📦 任务拆解: {len(subtasks)} 个子任务")
        for st in subtasks:
            print(f"   → {ROLE_CONFIG[st.role]['emoji']} {st.role.value}")
        
        # 3. 并行执行（独立任务）
        print(f"\n🚀 开始执行...")
        independent_tasks = [st for st in subtasks if st.status == TaskStatus.PENDING]
        executed = await asyncio.gather(*[execute_subtask(st) for st in independent_tasks])
        
        # 更新结果
        for i, st in enumerate(independent_tasks):
            subtasks[subtasks.index(st)] = executed[i]
        
        # 4. 汇总结果
        summary = aggregate_results(subtasks)
        
        # 5. 计算总分
        total_score = sum(st.score for st in subtasks) / len(subtasks) if subtasks else 0
        
        # 6. 保存历史
        result = TaskResult(
            task_id=f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            user_input=user_input,
            subtasks=subtasks,
            total_score=total_score,
            final_output=summary
        )
        self.task_history.append(result)
        
        return result
    
    def get_report(self) -> str:
        """获取历史报告"""
        if not self.task_history:
            return "暂无历史任务"
        
        report = []
        for t in self.task_history[-5:]:  # 最近5个任务
            report.append(f"""
任务: {t.user_input[:30]}...
评分: {t.total_score:.1f}/10
时间: {t.created_at.strftime('%Y-%m-%d %H:%M')}
""")
        
        return "\n".join(report)

# ==================== 入口 ====================

async def main():
    """测试入口"""
    orchestrator = SmartOrchestrator()
    
    # 测试案例
    test_cases = [
        "帮我写个小红书文案，配张性感自拍",
        "搜索一下最新的AI新闻",
        "写个Python脚本分析Excel数据"
    ]
    
    for user_input in test_cases:
        result = await orchestrator.execute(user_input)
        print(result.final_output)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())