"""
灵犀记忆系统 - 24/7 持续学习与主动预测
Continuous Learning and Proactive Prediction for Lingxi Memory

版本：v2.8.0
参考：memU 的主动学习循环机制
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from pathlib import Path
import aiofiles

# 使用绝对导入（兼容脚本直接运行）
try:
    from .memory_service import MemoryService, MemoryItem
    from .memory_embedding import SemanticMemoryEnhancer, EmbeddingConfig
except ImportError:
    from memory_service import MemoryService, MemoryItem
    from memory_embedding import SemanticMemoryEnhancer, EmbeddingConfig


class ProactiveTask:
    """主动任务"""
    
    def __init__(
        self,
        task_id: str,
        description: str,
        trigger_condition: str,
        action: Callable,
        priority: int = 5,
        cooldown_seconds: int = 3600
    ):
        self.id = task_id
        self.description = description
        self.trigger_condition = trigger_condition
        self.action = action
        self.priority = priority  # 1-10，越高越优先
        self.cooldown = cooldown_seconds
        self.last_triggered = 0
        self.enabled = True
    
    def can_trigger(self) -> bool:
        """检查是否可以触发"""
        if not self.enabled:
            return False
        
        now = time.time()
        return (now - self.last_triggered) >= self.cooldown
    
    def mark_triggered(self):
        """标记为已触发"""
        self.last_triggered = time.time()


class ContinuousLearner:
    """
    持续学习器
    
    24/7 后台运行，自动：
    - 监控新对话
    - 提取记忆
    - 检测模式
    - 更新用户画像
    """
    
    def __init__(self, memory_service: MemoryService, embedding_enhancer: SemanticMemoryEnhancer):
        self.memory = memory_service
        self.enhancer = embedding_enhancer
        self.running = False
        self._task = None
        
        # 学习配置
        self.check_interval = 30  # 秒
        self.batch_size = 10  # 每次处理的对话数
        self.pattern_detection_interval = 300  # 5 分钟检测一次模式
        
        # 状态追踪
        self._processed_convs = set()
        self._last_pattern_detection = 0
        self._learning_stats = {
            "total_conversations_processed": 0,
            "total_memories_extracted": 0,
            "patterns_detected": 0,
            "last_learning_time": None
        }
    
    async def start(self):
        """启动持续学习"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._learning_loop())
        print("🧠 持续学习已启动")
    
    async def stop(self):
        """停止持续学习"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("🧠 持续学习已停止")
    
    async def _learning_loop(self):
        """学习循环"""
        while self.running:
            try:
                # 1. 检查新对话
                await self._process_new_conversations()
                
                # 2. 定期模式检测
                if time.time() - self._last_pattern_detection > self.pattern_detection_interval:
                    await self._detect_and_learn_patterns()
                    self._last_pattern_detection = time.time()
                
                # 3. 休眠
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"持续学习错误：{e}")
                await asyncio.sleep(self.check_interval)
    
    async def _process_new_conversations(self):
        """处理新对话"""
        # 从文件系统加载未处理的对话
        conv_dir = self.memory.store.dirs["conversations"]
        
        if not conv_dir.exists():
            return
        
        # 扫描对话文件
        new_convs = []
        for conv_file in conv_dir.glob("*.json"):
            conv_id = conv_file.stem
            if conv_id not in self._processed_convs:
                new_convs.append(conv_file)
        
        # 批量处理
        for conv_file in new_convs[:self.batch_size]:
            try:
                await self._process_single_conversation(conv_file)
            except Exception as e:
                print(f"处理对话失败：{conv_file}, 错误：{e}")
    
    async def _process_single_conversation(self, conv_file: Path):
        """处理单个对话"""
        async with aiofiles.open(conv_file, 'r', encoding='utf-8') as f:
            conv_data = json.loads(await f.read())
        
        conv_id = conv_data.get("id", conv_file.stem)
        messages = conv_data.get("messages", [])
        
        if not messages:
            return
        
        # 提取记忆
        result = await self.memory.memorize(messages, conv_id)
        
        # 添加到 embedding 索引
        for item_data in result.get("items", []):
            await self.enhancer.add_memory(
                item_id=item_data["id"],
                content=item_data["content"],
                category=item_data["category"],
                metadata=item_data
            )
        
        # 更新状态
        self._processed_convs.add(conv_id)
        self._learning_stats["total_conversations_processed"] += 1
        self._learning_stats["total_memories_extracted"] += result.get("extracted_items", 0)
        self._learning_stats["last_learning_time"] = datetime.now().isoformat()
    
    async def _detect_and_learn_patterns(self):
        """检测和学**模式"""
        # 这里可以实现更复杂的模式检测逻辑
        # 例如：时间模式、话题模式、行为模式等
        
        patterns = await self.memory.organizer.detect_patterns()
        
        if patterns:
            self._learning_stats["patterns_detected"] += len(patterns)
            
            # 保存模式到文件
            pattern_file = self.memory.store.base / "patterns.json"
            async with aiofiles.open(pattern_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps({
                    "patterns": patterns,
                    "updated_at": datetime.now().isoformat()
                }, ensure_ascii=False, indent=2))
    
    def get_stats(self) -> Dict:
        """获取学习统计"""
        return {
            **self._learning_stats,
            "running": self.running,
            "processed_conversation_ids": len(self._processed_convs)
        }


class IntentPredictor:
    """
    意图预测器
    
    基于历史记忆预测用户下一步需求
    """
    
    def __init__(self, memory_service: MemoryService, embedding_enhancer: SemanticMemoryEnhancer):
        self.memory = memory_service
        self.enhancer = embedding_enhancer
        
        # 预测配置
        self.context_window = 10  # 考虑最近 10 条记忆
        self.confidence_threshold = 0.6  # 置信度阈值
    
    async def predict_next_action(self, user_id: str = "default") -> Dict:
        """
        预测用户下一步行动
        
        Args:
            user_id: 用户 ID
        
        Returns:
            {
                "predicted_intent": str,
                "confidence": float,
                "reasoning": str,
                "suggested_action": str,
                "related_memories": List
            }
        """
        # 获取最近记忆
        context = await self.memory.get_context(user_id)
        recent = context.get("recent_context", [])[:self.context_window]
        
        if not recent:
            return self._default_prediction()
        
        # 分析记忆模式
        categories = {}
        topics = {}
        
        for item in recent:
            cat = item.get("category", "unknown")
            topic = item.get("topic", "unknown")
            
            categories[cat] = categories.get(cat, 0) + 1
            topics[topic] = topics.get(topic, 0) + 1
        
        # 找出主导类别和话题
        dominant_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "context"
        dominant_topic = max(topics.items(), key=lambda x: x[1])[0] if topics else "unknown"
        
        # 基于模式生成预测
        prediction = await self._generate_prediction(dominant_category, dominant_topic, recent)
        
        return prediction
    
    async def _generate_prediction(
        self, 
        category: str, 
        topic: str, 
        recent_memories: List[Dict]
    ) -> Dict:
        """生成预测"""
        
        # 预定义的预测规则
        prediction_rules = {
            ("preferences", "工作时间"): {
                "intent": "工作相关任务",
                "suggested_action": "询问是否需要准备工作资料",
                "reasoning": "用户关注工作时间，可能即将开始工作"
            },
            ("knowledge", "技能"): {
                "intent": "学习或应用技能",
                "suggested_action": "提供相关技能资源或教程",
                "reasoning": "用户在积累某领域知识，可能需要深入学习"
            },
            ("context", "任务"): {
                "intent": "任务执行",
                "suggested_action": "提醒待办事项或提供进度更新",
                "reasoning": "用户有进行中的任务，可能需要跟进"
            },
            ("relationships", "联系人"): {
                "intent": "社交或沟通",
                "suggested_action": "提醒重要联系人或最近互动",
                "reasoning": "用户关注人际关系，可能需要维护联系"
            }
        }
        
        # 查找匹配规则
        key = (category, topic)
        if key in prediction_rules:
            rule = prediction_rules[key]
            return {
                "predicted_intent": rule["intent"],
                "confidence": 0.75,
                "reasoning": rule["reasoning"],
                "suggested_action": rule["suggested_action"],
                "related_memories": recent_memories[:3]
            }
        
        # 默认预测
        return {
            "predicted_intent": f"{category}相关活动",
            "confidence": 0.5,
            "reasoning": f"基于用户最近的{category}类记忆",
            "suggested_action": "提供相关支持",
            "related_memories": recent_memories[:3]
        }
    
    def _default_prediction(self) -> Dict:
        """默认预测（无记忆时）"""
        hour = datetime.now().hour
        
        if 6 <= hour < 9:
            intent = "早晨准备"
            action = "提供天气、新闻、日程摘要"
        elif 9 <= hour < 12:
            intent = "上午工作"
            action = "询问工作任务或会议安排"
        elif 12 <= hour < 14:
            intent = "午餐休息"
            action = "推荐餐厅或提醒休息"
        elif 14 <= hour < 18:
            intent = "下午工作"
            action = "提供工作支持或咖啡提醒"
        elif 18 <= hour < 22:
            intent = "晚间活动"
            action = "询问晚餐、娱乐或学习计划"
        else:
            intent = "休息准备"
            action = "提醒休息或提供睡前建议"
        
        return {
            "predicted_intent": intent,
            "confidence": 0.4,
            "reasoning": f"基于当前时间 {hour}:00",
            "suggested_action": action,
            "related_memories": []
        }


class ProactiveAssistant:
    """
    主动助手
    
    整合持续学习和意图预测，实现主动服务
    """
    
    def __init__(self, memory_service: MemoryService, embedding_enhancer: SemanticMemoryEnhancer):
        self.memory = memory_service
        self.enhancer = embedding_enhancer
        self.learner = ContinuousLearner(memory_service, embedding_enhancer)
        self.predictor = IntentPredictor(memory_service, embedding_enhancer)
        
        # 主动任务注册表
        self._tasks = {}
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """设置默认主动任务"""
        
        # 任务 1: 工作时间提醒
        self.register_task(ProactiveTask(
            task_id="work_hours_reminder",
            description="工作时间开始提醒",
            trigger_condition="hour == 9",
            action=self._work_hours_action,
            priority=7,
            cooldown_seconds=86400  # 每天一次
        ))
        
        # 任务 2: 午休提醒
        self.register_task(ProactiveTask(
            task_id="lunch_reminder",
            description="午休提醒",
            trigger_condition="hour == 12",
            action=self._lunch_reminder_action,
            priority=6,
            cooldown_seconds=86400
        ))
        
        # 任务 3: 任务跟进
        self.register_task(ProactiveTask(
            task_id="task_followup",
            description="待办任务跟进",
            trigger_condition="pending_tasks > 0",
            action=self._task_followup_action,
            priority=8,
            cooldown_seconds=3600  # 每小时一次
        ))
        
        # 任务 4: 记忆整理
        self.register_task(ProactiveTask(
            task_id="memory_cleanup",
            description="记忆整理和压缩",
            trigger_condition="memory_count > 1000",
            action=self._memory_cleanup_action,
            priority=3,
            cooldown_seconds=604800  # 每周一次
        ))
    
    def register_task(self, task: ProactiveTask):
        """注册主动任务"""
        self._tasks[task.id] = task
    
    async def start(self):
        """启动主动助手"""
        await self.learner.start()
        print("✨ 主动助手已启动")
    
    async def stop(self):
        """停止主动助手"""
        await self.learner.stop()
        print("✨ 主动助手已停止")
    
    async def check_and_execute_tasks(self) -> List[Dict]:
        """检查并执行可触发的任务"""
        executed = []
        
        for task in self._tasks.values():
            if task.can_trigger():
                try:
                    result = await task.action()
                    task.mark_triggered()
                    executed.append({
                        "task_id": task.id,
                        "description": task.description,
                        "result": result
                    })
                except Exception as e:
                    print(f"执行任务失败 {task.id}: {e}")
        
        return executed
    
    # 默认任务动作
    async def _work_hours_action(self) -> Dict:
        """工作时间提醒"""
        return {
            "message": "老板，工作时间到啦～ ☕️ 今天有什么计划吗？",
            "type": "reminder"
        }
    
    async def _lunch_reminder_action(self) -> Dict:
        """午休提醒"""
        return {
            "message": "老板，该吃午饭啦！🍱 记得休息一下哦～",
            "type": "reminder"
        }
    
    async def _task_followup_action(self) -> Dict:
        """任务跟进"""
        stats = await self.memory.get_stats()
        
        return {
            "message": f"📊 记忆系统统计：共{stats['total_items']}条记忆，最近 24 小时新增{stats['recent_items']}条",
            "type": "update"
        }
    
    async def _memory_cleanup_action(self) -> Dict:
        """记忆整理"""
        # 这里可以实现记忆压缩、去重等逻辑
        return {
            "message": "🧹 记忆整理完成",
            "type": "maintenance"
        }
    
    async def get_proactive_suggestions(self, user_id: str = "default") -> List[Dict]:
        """获取主动建议"""
        suggestions = []
        
        # 1. 意图预测
        prediction = await self.predictor.predict_next_action(user_id)
        
        if prediction["confidence"] >= self.predictor.confidence_threshold:
            suggestions.append({
                "type": "prediction",
                "content": prediction["suggested_action"],
                "reasoning": prediction["reasoning"],
                "confidence": prediction["confidence"]
            })
        
        # 2. 检查可执行任务
        tasks = await self.check_and_execute_tasks()
        for task in tasks:
            suggestions.append({
                "type": "task",
                "content": task["result"].get("message", ""),
                "task_id": task["task_id"]
            })
        
        return suggestions
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "learner": self.learner.get_stats(),
            "registered_tasks": len(self._tasks),
            "enabled_tasks": sum(1 for t in self._tasks.values() if t.enabled)
        }


# 便捷函数
async def create_proactive_assistant() -> ProactiveAssistant:
    """创建主动助手"""
    memory = MemoryService()
    await memory.initialize()
    
    enhancer = SemanticMemoryEnhancer()
    
    return ProactiveAssistant(memory, enhancer)
