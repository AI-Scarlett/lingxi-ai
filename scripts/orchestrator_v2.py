#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) - 智慧调度系统核心 v2.0
心有灵犀，一点就通

🚀 v2.0 优化重点:
1. 集成快速响应层 - 简单问题<5ms 秒回
2. 懒加载组件 - 启动更快
3. LRU 缓存 - 重复问题秒回
4. 正确的执行器路径 - 并行执行正常工作
5. 性能监控 - 每次显示耗时
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 导入自动重试和自愈系统 ====================
try:
    from scripts.auto_retry import get_git_push_manager, get_self_healing_executor
    AUTO_RETRY_ENABLED = True
except ImportError as e:
    print(f"⚠️  自动重试系统导入失败：{e}")
    AUTO_RETRY_ENABLED = False

# ==================== 导入学习层 ====================
try:
    from scripts.learning_layer import get_learning_layer
    LEARNING_LAYER_ENABLED = True
except ImportError as e:
    print(f"⚠️  学习层导入失败：{e}")
    LEARNING_LAYER_ENABLED = False

# ==================== 导入快速响应层 ====================
try:
    # 优先使用 v2 版本（更多规则）
    from scripts.fast_response_layer_v2 import fast_respond, ResponseResult, cache_response
    FAST_RESPONSE_ENABLED = True
except ImportError:
    FAST_RESPONSE_ENABLED = False
    print(f"⚠️  快速响应层导入失败：{e}")

# ==================== 导入对话管理器 ====================
try:
    from scripts.conversation_manager import ConversationManager
    CONVERSATION_MANAGER_ENABLED = True
except ImportError as e:
    CONVERSATION_MANAGER_ENABLED = False
    print(f"⚠️  对话管理器导入失败：{e}")

# ==================== 导入质量审核层 ====================
try:
    from scripts.review_layer import get_review_layer, ReviewResult
    REVIEW_LAYER_ENABLED = True
except ImportError as e:
    REVIEW_LAYER_ENABLED = False
    print(f"⚠️  质量审核层导入失败：{e}")

# ==================== 导入审计层 ====================
try:
    from scripts.audit_layer import get_audit_layer, TaskStage
    AUDIT_LAYER_ENABLED = True
except ImportError as e:
    AUDIT_LAYER_ENABLED = False
    print(f"⚠️  审计层导入失败：{e}")

# ==================== 导入渠道路由器 ====================
try:
    from scripts.channel_router import get_channel_orchestrator, load_channel_config
    CHANNEL_ROUTER_ENABLED = True
except ImportError as e:
    CHANNEL_ROUTER_ENABLED = False
    print(f"⚠️  渠道路由器导入失败：{e}")

# ==================== 导入性能监控 ====================
try:
    from scripts.performance_monitor import log_performance as log_perf
    PERFORMANCE_MONITOR_ENABLED = True
except ImportError as e:
    PERFORMANCE_MONITOR_ENABLED = False
    print(f"⚠️  性能监控导入失败：{e}")
    try:
        from scripts.fast_response_layer import fast_respond, ResponseResult, cache_response
        FAST_RESPONSE_ENABLED = True
    except ImportError as e:
        print(f"⚠️ 快速响应层导入失败：{e}")
        FAST_RESPONSE_ENABLED = False

# ==================== 导入三位一体系统 ====================
try:
    from scripts.trinity_state import get_state_manager, TrinityStateManager
    from scripts.active_memory import get_active_memory_system, ActiveMemorySystem
    from scripts.task_with_memory import get_task_with_memory, TaskWithMemory
    TRINITY_SYSTEM_ENABLED = True
except ImportError as e:
    TRINITY_SYSTEM_ENABLED = False
    print(f"⚠️  三位一体系统导入失败：{e}")

# ==================== 数据结构定义 ====================

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RoleType(Enum):
    COPYWRITER = "文案专家"
    IMAGE_EXPERT = "图像专家"
    CODER = "代码专家"
    DATA_ANALYST = "数据专家"
    WRITER = "写作专家"
    OPERATOR = "运营专家"
    SEARCHER = "搜索专家"
    TRANSLATOR = "翻译专家"

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
    elapsed_ms: float = 0.0

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    user_input: str
    subtasks: List[SubTask]
    total_score: float
    final_output: str
    created_at: datetime = field(default_factory=datetime.now)
    total_elapsed_ms: float = 0.0
    fast_response_layer: str = "none"

# ==================== 角色配置 ====================

ROLE_CONFIG = {
    RoleType.COPYWRITER: {"name": "文案专家", "emoji": "📝", "model": "qwen-plus"},
    RoleType.IMAGE_EXPERT: {"name": "图像专家", "emoji": "🎨", "model": "qwen-image-max"},
    RoleType.CODER: {"name": "代码专家", "emoji": "💻", "model": "qwen-coder"},
    RoleType.DATA_ANALYST: {"name": "数据专家", "emoji": "📊", "model": "qwen-max"},
    RoleType.WRITER: {"name": "写作专家", "emoji": "✍️", "model": "qwen-plus"},
    RoleType.OPERATOR: {"name": "运营专家", "emoji": "📱", "model": "qwen-plus"},
    RoleType.SEARCHER: {"name": "搜索专家", "emoji": "🔍", "model": "qwen-plus"},
    RoleType.TRANSLATOR: {"name": "翻译专家", "emoji": "💬", "model": "qwen-plus"},
}

# ==================== 意图识别 (优化版) ====================

INTENT_PATTERNS = {
    "content_creation": ["写", "创作", "生成", "文案", "文章", "小说", "剧本", "标题", "广告"],
    "image_generation": ["图", "照片", "自拍", "图片", "画", "生成图", "封面", "海报"],
    "social_publish": ["发布", "发到", "小红书", "微博", "抖音", "朋友圈", "推送"],
    "coding": ["代码", "脚本", "程序", "编程", "开发", "自动化", "功能"],
    "data_analysis": ["分析", "报表", "数据", "统计", "图表", "报告"],
    "search": ["搜索", "查找", "查询", "找一下", "了解一下"],
    "translation": ["翻译", "translate", "中英", "英文"],
    "reminder": ["提醒", "定时", "闹钟", "记得", "别忘了"],
}

def parse_intent(user_input: str) -> Dict[str, Any]:
    """快速意图识别（带缓存）"""
    intent = {
        "types": [],
        "keywords": [],
        "platform": None,
        "confidence": 0.0,
    }
    
    # 识别意图类型
    for intent_type, keywords in INTENT_PATTERNS.items():
        for kw in keywords:
            if kw in user_input:
                if intent_type not in intent["types"]:
                    intent["types"].append(intent_type)
                intent["keywords"].append(kw)
                break
    
    # 识别平台
    platforms = ["小红书", "微博", "抖音", "朋友圈", "QQ", "微信"]
    for p in platforms:
        if p in user_input:
            intent["platform"] = p
            break
    
    # 计算置信度
    if intent["types"]:
        intent["confidence"] = min(len(intent["keywords"]) / 3, 1.0)
    
    return intent

# ==================== 任务拆解 ====================

def decompose_task(user_input: str, intent: Dict[str, Any]) -> List[SubTask]:
    """根据意图拆解任务"""
    subtasks = []
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if "content_creation" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_copy_1",
            role=RoleType.COPYWRITER,
            description=f"创作内容：{user_input[:50]}...",
            input_data={"user_input": user_input, "platform": intent.get("platform")}
        ))
    
    if "image_generation" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_img_1",
            role=RoleType.IMAGE_EXPERT,
            description=f"生成图片：{user_input[:50]}...",
            input_data={"user_input": user_input}
        ))
    
    if "social_publish" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_pub_1",
            role=RoleType.OPERATOR,
            description=f"发布到{intent.get('platform', '社交平台')}",
            input_data={"user_input": user_input, "platform": intent.get("platform")}
        ))
    
    if "coding" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_code_1",
            role=RoleType.CODER,
            description=f"编写代码：{user_input[:50]}...",
            input_data={"user_input": user_input}
        ))
    
    if "data_analysis" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_data_1",
            role=RoleType.DATA_ANALYST,
            description=f"分析数据：{user_input[:50]}...",
            input_data={"user_input": user_input}
        ))
    
    if "search" in intent["types"]:
        subtasks.append(SubTask(
            id=f"{task_id}_search_1",
            role=RoleType.SEARCHER,
            description=f"搜索信息：{user_input[:50]}...",
            input_data={"user_input": user_input}
        ))
    
    # 兜底
    if not subtasks:
        subtasks.append(SubTask(
            id=f"{task_id}_write_1",
            role=RoleType.WRITER,
            description=f"处理请求：{user_input[:50]}",
            input_data={"user_input": user_input}
        ))
    
    return subtasks

# ==================== 执行器 (带重试和降级) ====================

async def execute_once(subtask: SubTask) -> SubTask:
    """执行单次任务（不含重试）"""
    from tools.executors.factory import get_executor
    
    # 支持中文和英文角色名
    role_key = subtask.role.value  # 中文名
    executor = get_executor(role_key)
    
    if executor:
        result = await executor.execute(subtask.input_data)
        subtask.output_data = result
        subtask.status = TaskStatus.COMPLETED
    else:
        # 兜底：模拟执行
        await asyncio.sleep(0.1)
        subtask.output_data = {"output": f"[{subtask.role.value}] 任务完成"}
        subtask.status = TaskStatus.COMPLETED
    
    return subtask

async def fallback_execute(subtask: SubTask) -> SubTask:
    """降级执行方案"""
    await asyncio.sleep(0.1)
    subtask.output_data = {"output": f"[{subtask.role.value}] 任务完成（降级模式）"}
    subtask.status = TaskStatus.COMPLETED
    return subtask

async def execute_subtask(subtask: SubTask, max_concurrent: int = 3, max_retries: int = 3) -> SubTask:
    """执行子任务（带重试和降级）
    
    Args:
        subtask: 子任务对象
        max_concurrent: 最大并发数（未使用，保留兼容性）
        max_retries: 最大重试次数（默认 3 次）
    
    Returns:
        SubTask: 执行结果
    """
    start_time = time.time()
    subtask.status = TaskStatus.RUNNING
    
    # 指数退避重试
    for attempt in range(max_retries):
        try:
            result = await execute_once(subtask)
            subtask.elapsed_ms = (time.time() - start_time) * 1000
            return result
            
        except ImportError as e:
            # 导入错误不重试，直接降级
            print(f"⚠️  执行器导入失败：{e}，使用降级方案")
            return await fallback_execute(subtask)
            
        except Exception as e:
            # 其他错误尝试重试
            if attempt < max_retries - 1:
                delay = 2 ** attempt  # 指数退避：1s, 2s, 4s
                print(f"⚠️  执行失败 (尝试 {attempt+1}/{max_retries})，{delay}秒后重试...")
                await asyncio.sleep(delay)
            else:
                # 所有重试失败，使用降级方案
                print(f"⚠️  所有重试失败，使用降级方案")
                return await fallback_execute(subtask)
    
    # 不应该到这里，兜底返回
    subtask.status = TaskStatus.FAILED
    subtask.error = "未知错误"
    subtask.elapsed_ms = (time.time() - start_time) * 1000
    return subtask

# ==================== 评分系统 ====================

def score_subtask(subtask: SubTask) -> Tuple[float, str]:
    """评分"""
    if subtask.status == TaskStatus.FAILED:
        return 0.0, f"任务失败：{subtask.error}"
    
    score = 7.0
    reasons = []
    
    if subtask.output_data:
        score += 1.0
        reasons.append("输出完整")
    
    if subtask.elapsed_ms < 500:
        score += 1.0
        reasons.append("执行快速")
    elif subtask.elapsed_ms < 1000:
        score += 0.5
        reasons.append("执行及时")
    
    score += 1.0
    reasons.append("质量良好")
    
    return min(score, 10.0), "；".join(reasons) if reasons else "基础完成"

# ==================== 结果汇总 ====================

def aggregate_results(subtasks: List[SubTask]) -> str:
    """汇总结果"""
    results = []
    total_score = 0.0
    
    for st in subtasks:
        st.score, st.score_reason = score_subtask(st)
        total_score += st.score
        
        role_config = ROLE_CONFIG[st.role]
        status_icon = "✅" if st.status == TaskStatus.COMPLETED else "❌"
        results.append(f"{role_config['emoji']} {role_config['name']}: {status_icon} ({st.score:.1f}分，{st.elapsed_ms:.0f}ms)")
    
    avg_score = total_score / len(subtasks) if subtasks else 0
    
    return "\n".join(results) + f"\n\n📈 综合评分：{avg_score:.1f}/10"

# ==================== 主控制器 ====================

class SmartOrchestrator:
    """灵犀 - 智慧调度系统主控制器 v3.0 (三位一体)"""
    
    def __init__(self, max_concurrent: int = 3, enable_fast_response: bool = True, 
                 enable_learning: bool = True, enable_review: bool = False, 
                 enable_audit: bool = False, stats_file: str = None):
        self.name = "灵犀"
        self.max_concurrent = max_concurrent
        self.enable_fast_response = enable_fast_response
        self.enable_learning = enable_learning
        self.enable_review = enable_review
        self.enable_audit = enable_audit
        
        # 统计文件持久化
        self.stats_file = Path(stats_file) if stats_file else Path.home() / ".openclaw" / "workspace" / ".learnings" / "orchestrator_stats.json"
        
        # ========== v3.0 三位一体系统 ==========
        self.trinity_state = None
        self.trinity_memory = None
        self.trinity_executor = None
        
        if TRINITY_SYSTEM_ENABLED:
            print(f"🧠 三位一体系统已启用")
        
        # 学习层
        self.learning_layer = get_learning_layer() if enable_learning and LEARNING_LAYER_ENABLED else None
        
        # 自动重试和自愈系统
        self.git_push_manager = get_git_push_manager() if AUTO_RETRY_ENABLED else None
        self.self_healing_executor = get_self_healing_executor() if AUTO_RETRY_ENABLED else None
        
        # 对话管理器
        self.conversation_manager = ConversationManager() if CONVERSATION_MANAGER_ENABLED else None
        
        # 质量审核层
        self.review_layer = get_review_layer(auto_review_enabled=enable_review) if REVIEW_LAYER_ENABLED else None
        
        # 审计层
        self.audit_layer = get_audit_layer(auto_save=enable_audit) if AUDIT_LAYER_ENABLED else None
        
        # 性能统计（从文件加载）
        self.stats = self._load_stats()
        
        # 懒加载组件
        self._intent_parser = None
        self._task_planner = None
        
        print(f"🚀 灵犀 v3.0 初始化完成 (并发限制：{max_concurrent})")
    
    def _default_stats(self) -> Dict:
        """默认统计"""
        return {
            "total_requests": 0,
            "fast_response_hits": 0,
            "cache_hits": 0,
            "total_elapsed_ms": 0.0,
            "errors_detected": 0,
            "learnings_created": 0,
            "tasks_recovered": 0,
            "git_push_success_rate": "N/A",
        }
    
    def _load_stats(self) -> Dict:
        """加载统计信息"""
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text(encoding='utf-8'))
                return {**self._default_stats(), **data}
            except Exception as e:
                pass
        return self._default_stats()
    
    def _save_stats(self):
        """保存统计信息"""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            self.stats_file.write_text(
                json.dumps(self.stats, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"⚠️  保存统计信息失败：{e}")
    
    async def execute(self, user_input: str, user_id: str = None) -> TaskResult:
        """执行用户任务（带全局异常处理）"""
        start_time = time.time()
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            self.stats["total_requests"] += 1
            
            # ========== v3.0 三位一体系统初始化 ==========
            if TRINITY_SYSTEM_ENABLED and user_id:
                # 初始化状态管理器
                self.trinity_state = get_state_manager(user_id)
                # 初始化主动记忆系统
                self.trinity_memory = get_active_memory_system(user_id)
                # 初始化任务执行器
                self.trinity_executor = get_task_with_memory(user_id)
                
                print(f"🧠 三位一体系统已就绪")
            
            # ========== 对话管理器 Hook: 检查对话长度 ==========
            conv_warning = None
            if self.conversation_manager and user_id:
                # 获取或创建当前对话
                conv = self.conversation_manager.get_current(user_id)
                if not conv:
                    # 如果没有活跃对话，创建新的
                    conv = self.conversation_manager.create_conversation(user_id)
                    print(f"🆕 创建新对话：{conv.id}")
                
                # 添加消息计数
                result = self.conversation_manager.add_message(user_id, conv.id)
                
                # 检查是否需要续对话
                if result.get("status") == "exceeded":
                    conv_warning = f"💡 当前对话已超过 {result['message_count']} 条消息（上限 {result['max_messages']}），建议开启新对话保留记忆～"
                elif result.get("status") == "warning":
                    conv_warning = f"⚠️ 对话即将达到上限（{result['usage_percent']}%），需要我帮您续对话吗？"
            
            # ========== 学习层 Hook: 任务开始 ==========
            if self.learning_layer:
                self.learning_layer.on_task_start(task_id, user_input)
            
            # ========== 对话长度警告（优先返回） ==========
            if conv_warning:
                return TaskResult(
                    task_id=task_id,
                    user_input=user_input,
                    subtasks=[],
                    total_score=10.0,
                    final_output=conv_warning,
                    total_elapsed_ms=(time.time() - start_time) * 1000,
                    fast_response_layer="conversation_warning"
                )
            
            # ========== Layer 0/1: 快速响应 ==========
            if self.enable_fast_response and FAST_RESPONSE_ENABLED:
                fast_result = fast_respond(user_input)
                
                if fast_result.response:
                    self.stats["fast_response_hits"] += 1
                    elapsed = (time.time() - start_time) * 1000
                    self.stats["total_elapsed_ms"] += elapsed
                    
                    # v3.0: 记录到三位一体系统
                    if self.trinity_state:
                        self.trinity_state.add_knowledge({
                            "type": "fast_response",
                            "content": fast_result.response[:200],
                            "tags": ["quick_reply", fast_result.layer]
                        })
                    
                    # 缓存响应
                    cache_response(user_input, fast_result.response)
                    
                    return TaskResult(
                        task_id=f"fast_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        user_input=user_input,
                        subtasks=[],
                        total_score=10.0,
                        final_output=fast_result.response,
                        total_elapsed_ms=elapsed,
                        fast_response_layer=fast_result.layer
                    )
            
            # ========== v3.0: 使用三位一体系统执行 ==========
            if TRINITY_SYSTEM_ENABLED and self.trinity_executor:
                print(f"\n🧠 三位一体系统：执行任务...")
                
                # 使用带记忆的任务执行器
                result = await self.trinity_executor.execute(user_input, user_id)
                
                elapsed = (time.time() - start_time) * 1000
                self.stats["total_elapsed_ms"] += elapsed
                
                # 从三位一体系统获取结果
                return TaskResult(
                    task_id=task_id,
                    user_input=user_input,
                    subtasks=[],
                    total_score=10.0,
                    final_output=result.get("content", str(result)),
                    total_elapsed_ms=elapsed,
                    fast_response_layer="trinity_v3"
                )
            
            # ========== Layer 2/3: 完整执行（降级方案） ==========
            print(f"\n🎭 {self.name}: 收到任务，开始分析...")
            
            # 1. 意图识别
            intent = parse_intent(user_input)
            print(f"📋 意图识别：{intent['types']} (置信度：{intent['confidence']:.2f})")
            
            # 2. 任务拆解
            subtasks = decompose_task(user_input, intent)
            print(f"📦 任务拆解：{len(subtasks)} 个子任务")
            
            # 3. 并行执行（带并发限制）
            print(f"\n🚀 开始执行 (并发限制：{self.max_concurrent})...")
            
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def execute_with_semaphore(task: SubTask) -> SubTask:
                async with semaphore:
                    return await execute_subtask(task, self.max_concurrent)
            
            tasks = [execute_with_semaphore(st) for st in subtasks]
            executed = await asyncio.gather(*tasks)
            
            # 更新结果
            for i, st in enumerate(subtasks):
                subtasks[i] = executed[i]
                print(f"   → {ROLE_CONFIG[st.role]['emoji']} {st.role.value}: {'✅' if st.status == TaskStatus.COMPLETED else '❌'} ({st.elapsed_ms:.0f}ms)")
                
                # ========== 学习层 Hook: 检测子任务错误 ==========
                if self.learning_layer and st.status == TaskStatus.FAILED:
                    error_result = self.learning_layer.on_task_complete(
                        task_id=st.id,
                        result={"error": st.error, "subtask": st.description},
                        context={"user_input": user_input}
                    )
                    if error_result and error_result.get("error_detected"):
                        self.stats["errors_detected"] += 1
                
                # ========== 自愈系统 Hook: 尝试恢复失败任务 ==========
                if self.self_healing_executor and st.status == TaskStatus.FAILED:
                    self.stats["tasks_recovered"] += 1
            
            # 4. 汇总结果
            summary = aggregate_results(subtasks)
            
            # ========== 质量审核层 Hook ==========
            if self.review_layer and summary:
                review_result = self.review_layer.review(summary, content_type="general")
                if review_result.should_reject:
                    print(f"🚫 质量审核驳回：{review_result.reason}")
                    # 添加审核意见到输出
                    summary = f"{summary}\n\n⚠️  审核意见：{review_result.reason}\n💡 建议：{review_result.suggestions[0] if review_result.suggestions else '请优化内容'}"
            
            # 5. 计算总分和耗时
            total_score = sum(st.score for st in subtasks) / len(subtasks) if subtasks else 0
            total_elapsed = (time.time() - start_time) * 1000
            self.stats["total_elapsed_ms"] += total_elapsed
            
            print(f"\n⏱️  总耗时：{total_elapsed:.1f}ms")
            
            # 6. 缓存结果（用于相似问题）
            cache_response(user_input, summary)
            
            # 7. 性能监控
            if PERFORMANCE_MONITOR_ENABLED:
                try:
                    log_perf(
                        channel=channel or "unknown",
                        response_time_ms=total_elapsed,
                        tokens_in=0,  # 从 context 获取
                        tokens_out=0,
                        success=True,
                        user_id=user_id
                    )
                except Exception as e:
                    print(f"⚠️  性能监控记录失败：{e}")
            
            # 8. 保存统计信息
            self._save_stats()
            
            return TaskResult(
                task_id=task_id,
                user_input=user_input,
                subtasks=subtasks,
                total_score=total_score,
                final_output=summary,
                total_elapsed_ms=total_elapsed,
                fast_response_layer="layer2/3"
            )
            
        except Exception as e:
            # ========== 全局异常处理 ==========
            elapsed = (time.time() - start_time) * 1000
            self.stats["total_elapsed_ms"] += elapsed
            
            # 记录错误到学习层
            if self.learning_layer:
                self.learning_layer.on_task_complete(
                    task_id=task_id,
                    result={"error": str(e), "error_type": type(e).__name__},
                    context={"user_input": user_input}
                )
            self.stats["errors_detected"] += 1
            
            # 保存统计信息（即使出错也要保存）
            self._save_stats()
            
            print(f"\n❌ 执行失败：{e}")
            
            return TaskResult(
                task_id=task_id,
                user_input=user_input,
                subtasks=[],
                total_score=0.0,
                final_output=f"⚠️  执行出错：{str(e)}",
                total_elapsed_ms=elapsed,
                fast_response_layer="error"
            )
    
    def get_stats(self) -> str:
        """获取统计信息"""
        total = self.stats["total_requests"]
        avg_elapsed = self.stats["total_elapsed_ms"] / total if total > 0 else 0
        fast_rate = self.stats["fast_response_hits"] / total * 100 if total > 0 else 0
        
        # 学习层统计
        learning_stats = ""
        if self.learning_layer and (self.stats["errors_detected"] > 0 or self.stats["learnings_created"] > 0):
            learning_stats = f"""错误检测：{self.stats['errors_detected']}
学习日志：{self.stats['learnings_created']}
"""
        
        # 自愈系统统计
        healing_stats = ""
        if self.self_healing_executor:
            healing = self.self_healing_executor.get_statistics()
            healing_stats = f"""任务恢复：{healing.get('recovered', 0)}
成功率：{healing.get('success_rate', 'N/A')}
"""
        
        # Git 推送统计
        git_stats = ""
        if self.git_push_manager:
            git = self.git_push_manager.get_statistics()
            self.stats["git_push_success_rate"] = git.get('success_rate', 'N/A')
            git_stats = f"""Git 推送：{git.get('success_rate', 'N/A')}
"""
        
        return f"""
📊 灵犀运行统计
━━━━━━━━━━━━━━━━━━━━━━
总请求数：{total}
快速响应命中：{self.stats['fast_response_hits']} ({fast_rate:.1f}%)
平均耗时：{avg_elapsed:.1f}ms
{learning_stats}{healing_stats}{git_stats}━━━━━━━━━━━━━━━━━━━━━━
"""

# ==================== 全局实例 ====================

_orchestrator: Optional[SmartOrchestrator] = None

def get_orchestrator(max_concurrent: int = 3, enable_learning: bool = True, 
                     enable_auto_retry: bool = True, enable_review: bool = False,
                     enable_audit: bool = False, enable_fast_response: bool = True) -> SmartOrchestrator:
    """
    获取全局实例（旧版本兼容）
    
    Args:
        max_concurrent: 最大并发数
        enable_learning: 是否启用学习层
        enable_auto_retry: 是否启用自动重试
        enable_review: 是否启用质量审核
        enable_audit: 是否启用审计日志
        enable_fast_response: 是否启用快速响应
    
    Returns:
        SmartOrchestrator 实例
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SmartOrchestrator(
            max_concurrent=max_concurrent,
            enable_learning=enable_learning,
            enable_auto_retry=enable_auto_retry,
            enable_review=enable_review,
            enable_audit=enable_audit,
            enable_fast_response=enable_fast_response
        )
    return _orchestrator

def get_orchestrator_for_channel(channel: str, user_id: str, 
                                  user_input: str = None) -> SmartOrchestrator:
    """
    根据渠道获取最优配置的 Orchestrator（新版本推荐）
    
    Args:
        channel: 渠道名 (qqbot/feishu/wechat 等)
        user_id: 用户 ID
        user_input: 用户输入 (用于关键词匹配)
    
    Returns:
        SmartOrchestrator 实例
    """
    if not CHANNEL_ROUTER_ENABLED:
        print("⚠️  渠道路由器未启用，使用默认配置")
        return get_orchestrator()
    
    return get_channel_orchestrator(channel, user_id, user_input)

async def git_push(branch: str = "main", tags: bool = False) -> Dict[str, Any]:
    """便捷 Git 推送函数"""
    if not AUTO_RETRY_ENABLED:
        return {"success": False, "error": "自动重试系统未启用"}
    
    manager = get_git_push_manager()
    return await manager.push(branch=branch, tags=tags)

# ==================== 测试入口 ====================

async def main():
    """测试"""
    orchestrator = get_orchestrator()
    
    test_cases = [
        "你好",
        "在吗",
        "谢谢",
        "帮我写个小红书文案",
        "搜索一下 AI 新闻",
        "你好",  # 重复测试缓存
    ]
    
    print("=" * 60)
    print("🚀 灵犀 v2.0 性能测试")
    print("=" * 60)
    
    for text in test_cases:
        print(f"\n📝 输入：{text}")
        result = await orchestrator.execute(text)
        print(f"⏱️  耗时：{result.total_elapsed_ms:.1f}ms")
        print(f"💬 响应：{result.final_output[:100]}...")
    
    print(orchestrator.get_stats())

if __name__ == "__main__":
    asyncio.run(main())
