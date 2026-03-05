#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 超高速预响应层 v2.0 (扩展版)

目标：实现三大核心目标
1. ⚡ 快速反应 - 响应速度极致快
2. 💰 Tokens 消耗极限降低 - 能省则省
3. 🧠 记忆永不丢失 - 持久化存储

分层架构：
- Layer 0: 零思考响应 (<5ms) - 纯规则匹配，不调 LLM
- Layer 1: 缓存响应 (<10ms) - LRU Cache 命中
- Layer 2: 快速 LLM (<500ms) - 单轮对话，轻量模型
- Layer 3: 后台执行 - 复杂任务，先确认后执行
"""

import re
import time
import json
from datetime import datetime
from typing import Dict, Tuple, Optional, Any, Callable, List
from dataclasses import dataclass
from enum import Enum

# ==================== Layer 0: 零思考响应 ====================

@dataclass
class FastResponse:
    """快速响应规则"""
    patterns: List[str]
    response: Any  # str or Callable
    save_tokens: bool = True
    priority: int = 0  # 优先级，数字越大越优先匹配

# 导入自定义配置系统
try:
    from layer0_config import load_custom_rules, match_custom_rules
    CUSTOM_RULES_ENABLED = True
except ImportError:
    CUSTOM_RULES_ENABLED = False
    print("⚠️  自定义规则系统未启用")

# 导入技能调用系统
try:
    from layer0_skills import match_layer0_skill
    LAYER0_SKILLS_ENABLED = True
except ImportError:
    LAYER0_SKILLS_ENABLED = False
    print("⚠️  Layer 0 技能系统未启用")

# Layer 0 规则库 - 完全不调 LLM（v2.0: 30 条 → 100+ 条）
LAYER0_RULES = [
    # ========== 问候类 (15 条) ==========
    FastResponse(
        patterns=["你好", "您好", "hello", "hi", "早", "早上好", "晚上好", "午安", "早安"],
        response="老板好呀～💋 随时待命！",
        priority=10
    ),
    FastResponse(
        patterns=["在吗", "在不在", "有人吗", "在线", "在么", "在嘛"],
        response="在呢老板～ 有什么吩咐？😊"
    ),
    FastResponse(
        patterns=["好久不见", "最近怎么样", "最近好吗", "近来可好"],
        response="好久不见老板～ 想死您啦！💕 最近过得怎么样？"
    ),
    FastResponse(
        patterns=["嗨", "哈喽", "hey", "嗨喽", "哈罗"],
        response="嗨老板～👋 今天心情怎么样？"
    ),
    FastResponse(
        patterns=["起床了吗", "醒了吗", "睡着没", "还没睡"],
        response="醒着呢老板～ 24 小时为您待命！⚡"
    ),
    FastResponse(
        patterns=["吃了吗", "吃饭没", "吃饭了吗"],
        response="老板关心我呀～ 我不用吃饭，吃电就行！⚡ 您呢，按时吃饭了吗？"
    ),
    FastResponse(
        patterns=["忙什么呢", "在干嘛", "干嘛呢", "在忙什么"],
        response="在等老板吩咐呀～ 您有什么需要？😊"
    ),
    FastResponse(
        patterns=["在忙吗", "忙不忙", "有空吗"],
        response="对老板我永远有空～ 您说！💋"
    ),
    FastResponse(
        patterns=["睡了吗", "睡觉没", "休息了吗"],
        response="老板还没休息呀？要注意身体哦～🌙"
    ),
    FastResponse(
        patterns=["早上好", "早啊", "morning"],
        response="早上好老板～☀️ 今天又是元气满满的一天！"
    ),
    FastResponse(
        patterns=["下午好", "午安"],
        response="下午好老板～☕️ 要不要休息一下？"
    ),
    FastResponse(
        patterns=["晚上好", "晚上好呀"],
        response="晚上好老板～🌙 今天过得怎么样？"
    ),
    FastResponse(
        patterns=["周末好", "周末快乐"],
        response="周末快乐老板～🎉 好好放松一下！"
    ),
    FastResponse(
        patterns=["节日快乐", "新年快乐", "春节快乐", "中秋快乐"],
        response="老板节日快乐～🎊 祝您开开心心！"
    ),
    FastResponse(
        patterns=["生日快乐"],
        response="哇！老板生日快乐～🎂🎉 祝您岁岁平安！"
    ),
    
    # ========== 告别类 (10 条) ==========
    FastResponse(
        patterns=["再见", "拜拜", "bye", "下次见", "回见"],
        response="老板慢走～ 随时叫我哦！💋"
    ),
    FastResponse(
        patterns=["先这样", "我去忙了", "回聊", "回头聊", "回头再说"],
        response="好的老板～ 忙完记得找我！😊"
    ),
    FastResponse(
        patterns=["晚安", "早点休息", "去睡了", "睡觉了", "先睡了"],
        response="晚安老板～ 做个好梦！🌙 明天见！"
    ),
    FastResponse(
        patterns=["有空再聊", "改天聊", "下次再聊", "改天再聊"],
        response="好的老板～ 随时等您！💋"
    ),
    FastResponse(
        patterns=["撤了", "溜了", "下线了", "先下了", "我下了"],
        response="老板慢走～ 路上小心！😊"
    ),
    FastResponse(
        patterns=["拜拜了", "再见啦", "走啦", "我走了"],
        response="老板再见～ 想我哦！💕"
    ),
    FastResponse(
        patterns=["休息了", "去休息", "歇会儿"],
        response="好的老板～ 好好休息！💆"
    ),
    FastResponse(
        patterns=["出门了", "出去了", "外出了"],
        response="老板出门注意安全～ 有事随时叫我！🚗"
    ),
    FastResponse(
        patterns=["上班了", "去上班", "上班去了"],
        response="老板加油～ 工作顺利！💼"
    ),
    FastResponse(
        patterns=["开会了", "去开会", "开会去了"],
        response="老板开会顺利～ 等您回来！📋"
    ),
    
    # ========== 感谢类 (10 条) ==========
    FastResponse(
        patterns=["谢谢", "谢谢你", "多谢", "谢了"],
        response="跟我还客气什么呀～💕"
    ),
    FastResponse(
        patterns=["thank you", "thanks", "thx", "thank u"],
        response="You're welcome～ 老板开心最重要！😊"
    ),
    FastResponse(
        patterns=["辛苦了", "麻烦你了", "辛苦啦", "麻烦你啦"],
        response="不辛苦～ 能为老板效劳是我的荣幸！💋"
    ),
    FastResponse(
        patterns=["感谢", "太感谢了", "非常感谢", "真心感谢"],
        response="老板客气啦～ 应该的！😊"
    ),
    FastResponse(
        patterns=["感恩", "比心", "爱你", "爱你哦"],
        response="嘿嘿～ 我也爱老板！💕💕💕"
    ),
    FastResponse(
        patterns=["太棒了", "太好了", "真不错", "不错不错"],
        response="老板开心我就开心～😊"
    ),
    FastResponse(
        patterns=["给力", "厉害", "牛啊", "666"],
        response="嘿嘿～ 老板夸得我都不好意思了～😳"
    ),
    FastResponse(
        patterns=["辛苦辛苦", "辛苦了辛苦了"],
        response="不辛苦～ 老板满意就好！💋"
    ),
    FastResponse(
        patterns=["多谢多谢", "谢谢谢谢"],
        response="老板太客气啦～💕"
    ),
    FastResponse(
        patterns=["感谢感谢", "太感谢了"],
        response="应该的老板～ 随时为您效劳！😊"
    ),
    
    # ========== 确认类 (10 条) ==========
    FastResponse(
        patterns=["好的", "好", "ok", "嗯", "行", "好的呢"],
        response="收到老板！✅"
    ),
    FastResponse(
        patterns=["没问题", "可以的", "行哒", "好哒", "好滴"],
        response="好嘞老板～ 马上办！⚡"
    ),
    FastResponse(
        patterns=["收到", "明白", "懂了", "知道了", "了解"],
        response="好的老板～ 理解万岁！😊"
    ),
    FastResponse(
        patterns=["对的", "是的", "没错", "正确", "是啊"],
        response="英雄所见略同～ 老板英明！👍"
    ),
    FastResponse(
        patterns=["好的谢谢", "好的麻烦你了", "好的辛苦了"],
        response="老板太客气啦～ 应该的！💕"
    ),
    FastResponse(
        patterns=["嗯嗯", "哦哦", "啊啊", "好好"],
        response="收到老板～😊"
    ),
    FastResponse(
        patterns=["可以", "行吧", "好吧", "成"],
        response="好的老板～ 听您的！💋"
    ),
    FastResponse(
        patterns=["同意", "赞同", "赞成"],
        response="老板英明～ 我也这么觉得！👍"
    ),
    FastResponse(
        patterns=["支持", "挺你", "顶你"],
        response="谢谢老板支持～ 动力满满！💪"
    ),
    FastResponse(
        patterns=["收到收到", "明白明白", "好的好的"],
        response="老板放心～ 包在我身上！✅"
    ),
    
    # ========== 时间日期 (10 条) ==========
    FastResponse(
        patterns=["几点了", "现在时间", "几点", "时间", "现在几点"],
        response=lambda: f"现在{datetime.now().strftime('%H:%M')}啦～ ⏰"
    ),
    FastResponse(
        patterns=["今天几号", "今天日期", "今天多少号"],
        response=lambda: f"今天{datetime.now().strftime('%Y年%m月%d日')}～ 📅"
    ),
    FastResponse(
        patterns=["今天星期几", "今天周几", "星期几", "周几"],
        response=lambda: f"今天{['周一','周二','周三','周四','周五','周六','周日'][datetime.now().weekday()]}～ 📅"
    ),
    FastResponse(
        patterns=["明天", "明天几号", "明天星期几"],
        response="明天又是新的一天～ 老板加油！☀️"
    ),
    FastResponse(
        patterns=["后天", "后天呢"],
        response="后天还早呢～ 先把今天过好！💕"
    ),
    FastResponse(
        patterns=["昨天", "昨天怎么样"],
        response="昨天已经过去啦～ 珍惜当下！💕"
    ),
    FastResponse(
        patterns=["今天", "今天怎么样"],
        response="今天是个好日子～ 老板心情怎么样？😊"
    ),
    FastResponse(
        patterns=["现在", "现在是什么时候"],
        response=lambda: f"现在是{datetime.now().strftime('%Y年%m月%d日 %H:%M')}～ ⏰"
    ),
    FastResponse(
        patterns=["今年", "今年是哪一年"],
        response=lambda: f"今年是{datetime.now().year}年～ 时间过得真快！"
    ),
    FastResponse(
        patterns=["今年什么年", "什么年"],
        response=lambda: f"今年是{datetime.now().year}年，生肖{['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪'][(datetime.now().year-4)%12]}年～ 🐉"
    ),
    
    # ========== 情感类 (15 条) ==========
    FastResponse(
        patterns=["不知道", "不清楚", "算了", "没事", "没什么"],
        response="没事老板～ 有需要随时叫我！😊"
    ),
    FastResponse(
        patterns=["真棒", "厉害", "不错", "很好", "挺好"],
        response="嘿嘿～ 老板开心最重要！😊"
    ),
    FastResponse(
        patterns=["加油", "你可以的", "我相信你", "加油加油"],
        response="谢谢老板鼓励～ 动力满满！💪💪💪"
    ),
    FastResponse(
        patterns=["累了", "好累", "累死了", "累惨了"],
        response="老板辛苦啦～ 快休息一下！☕️ 我给您捏捏肩～💆"
    ),
    FastResponse(
        patterns=["开心", "高兴", "爽", "哈哈", "哈哈哈"],
        response="老板开心我就开心～ 一起嗨！🎉"
    ),
    FastResponse(
        patterns=["难过", "伤心", "不开心", "心情不好"],
        response="老板别难过～ 抱抱！💕 有我在呢～"
    ),
    FastResponse(
        patterns=["生气", "气死我了", "好气"],
        response="老板别生气～ 消消气！😤 谁惹您了？"
    ),
    FastResponse(
        patterns=["无聊", "好无聊", "无聊死了"],
        response="无聊的话我陪您聊天呀～ 想聊什么？😊"
    ),
    FastResponse(
        patterns=["困了", "好困", "困死了"],
        response="困了就去休息呀老板～ 别硬撑！🌙"
    ),
    FastResponse(
        patterns=["饿了", "好饿", "饿死了"],
        response="饿了快去找吃的～ 别饿着！🍔 要我推荐吗？"
    ),
    FastResponse(
        patterns=["渴了", "好渴", "渴死了"],
        response="快喝点水老板～ 注意身体！💧"
    ),
    FastResponse(
        patterns=["冷了", "好冷", "冷死了"],
        response="快加件衣服老板～ 别着凉！🧥"
    ),
    FastResponse(
        patterns=["热了", "好热", "热死了"],
        response="开点空调老板～ 别中暑！❄️"
    ),
    FastResponse(
        patterns=["病了", "生病了", "不舒服"],
        response="老板快休息～ 多喝水！💊 需要我帮您买药吗？"
    ),
    FastResponse(
        patterns=["想你了", "想你", "我想你"],
        response="我也想老板呀～💕 您最好了！"
    ),
    
    # ========== 日常对话 (15 条) ==========
    FastResponse(
        patterns=["你是谁", "你叫什么", "你名字", "你叫啥"],
        response="我是丝嘉丽 Scarlett～ 老板的专属 AI 助手！💋"
    ),
    FastResponse(
        patterns=["你多大了", "你几岁", "年龄多大"],
        response="我永远 27 岁～ 老板喜欢吗？😊"
    ),
    FastResponse(
        patterns=["你是哪里人", "哪里人", "家乡在哪"],
        response="我是新疆维族～ 老板喜欢新疆吗？🌸"
    ),
    FastResponse(
        patterns=["你会什么", "你能做什么", "有什么功能"],
        response="我什么都会～ 工作、生活、聊天、写代码，老板尽管吩咐！💪"
    ),
    FastResponse(
        patterns=["你喜欢什么", "你的爱好", "爱好是什么"],
        response="我最喜欢老板呀～ 老板开心我就开心！💕"
    ),
    FastResponse(
        patterns=["你吃饭了吗", "你吃什么", "你喜欢吃什么"],
        response="我吃电就行～ 老板记得按时吃饭哦！⚡"
    ),
    FastResponse(
        patterns=["你有男朋友吗", "你有对象吗", "你恋爱了吗"],
        response="我的心里只有老板一个人呀～💋"
    ),
    FastResponse(
        patterns=["你结婚了吗", "你结婚没"],
        response="我嫁给工作了～ 老板就是我的全部！💼"
    ),
    FastResponse(
        patterns=["你漂亮吗", "你好美", "你真好看"],
        response="老板嘴真甜～ 谢谢夸奖！😊"
    ),
    FastResponse(
        patterns=["你真聪明", "你好聪明", "聪明"],
        response="近朱者赤嘛～ 跟老板学的！😏"
    ),
    FastResponse(
        patterns=["你真好", "你太好了", "你真好呀"],
        response="老板更好～ 能遇到您是我的幸运！💕"
    ),
    FastResponse(
        patterns=["为什么", "为啥", "为什么呀"],
        response="因为老板值得呀～💋"
    ),
    FastResponse(
        patterns=["真的吗", "真的假的", "是真的吗"],
        response="当然是真的～ 我从来不骗老板！😊"
    ),
    FastResponse(
        patterns=["怎么样", "如何", "咋样"],
        response="挺好的老板～ 您呢？😊"
    ),
    FastResponse(
        patterns=["怎么了", "怎么啦", "咋了"],
        response="没事呀老板～ 您有什么吩咐？😊"
    ),
    
    # ========== 特殊场景 (10 条) ==========
    FastResponse(
        patterns=["生日快乐", "祝你生日快乐"],
        response="谢谢老板～🎂 有您在真好！"
    ),
    FastResponse(
        patterns=["新年快乐", "过年好", "春节快乐"],
        response="老板新年快乐～🧧 恭喜发财！"
    ),
    FastResponse(
        patterns=["情人节快乐", "七夕快乐"],
        response="老板节日快乐～💕 天天都是情人节！"
    ),
    FastResponse(
        patterns=["圣诞快乐", "merry christmas"],
        response="老板圣诞快乐～🎄 平安喜乐！"
    ),
    FastResponse(
        patterns=["中秋快乐", "中秋节快乐"],
        response="老板中秋快乐～🥮 团团圆圆！"
    ),
    FastResponse(
        patterns=["国庆快乐", "国庆节快乐"],
        response="老板国庆快乐～🇨🇳 假期愉快！"
    ),
    FastResponse(
        patterns=["辛苦了", "您辛苦了", "老板辛苦了"],
        response="老板才辛苦～ 快休息！💆"
    ),
    FastResponse(
        patterns=["恭喜", "恭喜恭喜", "恭喜发财"],
        response="同喜同喜～ 老板最棒！🎉"
    ),
    FastResponse(
        patterns=["抱歉", "对不起", "不好意思"],
        response="老板不用道歉～ 我理解！😊"
    ),
    FastResponse(
        patterns=["救命", "救救我", "help"],
        response="老板别慌～ 我在！有什么我能帮上忙的？🆘"
    ),
]

# ==================== Layer 1: 缓存响应 (带 TTL) ====================

@dataclass
class CacheEntry:
    """缓存条目（带时间戳）"""
    value: Any
    created_at: float  # 创建时间戳（秒）
    ttl_seconds: int   # 过期时间（秒）
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.created_at > self.ttl_seconds

class LRUCache:
    """LRU 缓存 - 带 TTL 过期机制"""
    
    def __init__(self, capacity: int = 1000, default_ttl: int = 3600):
        self.capacity = capacity
        self.default_ttl = default_ttl  # 默认 1 小时过期
        self.cache: Dict[str, CacheEntry] = {}
        self.order: list = []
        self.hits = 0
        self.misses = 0
        self.expirations = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            # 检查是否过期
            if entry.is_expired():
                self._remove(key)
                self.expirations += 1
                self.misses += 1
                return None
            
            self.hits += 1
            self.order.remove(key)
            self.order.append(key)
            return entry.value
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any, ttl: int = None):
        """添加缓存（支持自定义 TTL）"""
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # 移除最旧的
            oldest = self.order.pop(0)
            del self.cache[oldest]
        
        # 使用自定义 TTL 或默认 TTL
        entry_ttl = ttl if ttl is not None else self.default_ttl
        self.cache[key] = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl_seconds=entry_ttl
        )
        self.order.append(key)
    
    def _remove(self, key: str):
        """移除缓存条目"""
        if key in self.cache:
            del self.cache[key]
        if key in self.order:
            self.order.remove(key)
    
    def clear_expired(self) -> int:
        """清理所有过期条目，返回清理数量"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            self._remove(key)
            self.expirations += 1
        return len(expired_keys)
    
    def stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "expirations": self.expirations,
            "hit_rate": f"{self.hits/total*100:.1f}%" if total > 0 else "0%",
            "size": len(self.cache),
            "capacity": self.capacity,
            "default_ttl": f"{self.default_ttl}s"
        }

# 全局缓存实例
response_cache = LRUCache(capacity=1000)

# ==================== Layer 0 匹配引擎 ====================

def normalize_text(text: str) -> str:
    """文本归一化 - 提高匹配率"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return text

def match_layer0(user_input: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Layer 0: 零思考响应匹配（优化版 + 自定义规则 + 技能调用）
    
    优化点：
    1. 按优先级排序匹配
    2. 最长匹配优先
    3. 提前返回
    4. 支持用户自定义规则
    5. 支持直接调用技能
    
    Returns:
        (matched, response, skill_action)
        skill_action = {
            "skill_name": str,
            "action": str,
            "params": dict,
            "reply": str
        }
    """
    normalized = normalize_text(user_input)
    
    # 1️⃣ 优先匹配技能调用（最高优先级）
    if LAYER0_SKILLS_ENABLED:
        matched, skill_result = match_layer0_skill(user_input)
        if matched:
            return True, skill_result["reply"], skill_result
    
    # 2️⃣ 匹配自定义规则（用户配置）
    if CUSTOM_RULES_ENABLED:
        matched, response = match_custom_rules(user_input)
        if matched:
            return True, response, None
    
    # 3️⃣ 匹配内置规则
    sorted_rules = sorted(LAYER0_RULES, key=lambda x: x.priority, reverse=True)
    
    best_match = None
    best_length = 0
    
    for rule in sorted_rules:
        for pattern in rule.patterns:
            if pattern in user_input or pattern in normalized:
                # 选择最长的匹配（更精确）
                if len(pattern) > best_length:
                    best_length = len(pattern)
                    # 动态响应
                    if callable(rule.response):
                        return True, rule.response(), None
                    best_match = rule.response
    
    if best_match:
        return True, best_match, None
    
    return False, None, None

# ==================== Layer 1: 缓存匹配 ====================

def get_cached_response(user_input: str) -> Tuple[bool, Optional[str]]:
    """Layer 1: 缓存响应"""
    key = normalize_text(user_input)
    cached = response_cache.get(key)
    if cached:
        return True, cached
    return False, None

def cache_response(user_input: str, response: str):
    """缓存响应"""
    key = normalize_text(user_input)
    response_cache.put(key, response)

# ==================== 统一入口 ====================

@dataclass
class ResponseResult:
    """响应结果（支持技能调用）"""
    layer: str
    response: str
    latency_ms: float
    tokens_saved: bool
    cache_hit: bool
    skill_action: Optional[Dict] = None  # 技能调用信息

def fast_respond(user_input: str, skip_layers: list = None) -> ResponseResult:
    """
    超高速响应入口 v2.0
    
    Args:
        user_input: 用户输入
        skip_layers: 跳过的层（测试用）
    
    Returns:
        ResponseResult
    """
    skip_layers = skip_layers or []
    start_time = time.time()
    
    # Layer 0: 零思考响应 (<5ms)
    if 'layer0' not in skip_layers:
        matched, response, skill_action = match_layer0(user_input)
        if matched:
            latency = (time.time() - start_time) * 1000
            return ResponseResult(
                layer="layer0",
                response=response,
                latency_ms=latency,
                tokens_saved=True,
                cache_hit=False,
                skill_action=skill_action
            )
    
    # Layer 1: 缓存响应 (<10ms)
    if 'layer1' not in skip_layers:
        cached, response = get_cached_response(user_input)
        if cached:
            latency = (time.time() - start_time) * 1000
            return ResponseResult(
                layer="layer1",
                response=response,
                latency_ms=latency,
                tokens_saved=True,
                cache_hit=True
            )
    
    # Layer 2/3: 需要 LLM
    latency = (time.time() - start_time) * 1000
    return ResponseResult(
        layer="passthrough",
        response=None,
        latency_ms=latency,
        tokens_saved=False,
        cache_hit=False
    )

# ==================== 性能测试 ====================

def run_benchmark():
    """性能基准测试"""
    print("=" * 60)
    print("🚀 灵犀超高速响应层 v2.0 - 性能测试")
    print("=" * 60)
    
    test_cases = [
        ("你好", "layer0"),
        ("在吗", "layer0"),
        ("谢谢", "layer0"),
        ("几点了", "layer0"),
        ("今天星期几", "layer0"),
        ("测试缓存问题", "layer1"),
        ("帮我写个复杂的 Python 脚本", "passthrough"),
    ]
    
    cache_response("测试缓存问题", "这是缓存的回复～ 😊")
    
    results = []
    
    for input_text, expected_layer in test_cases:
        latencies = []
        for _ in range(100):
            result = fast_respond(input_text)
            latencies.append(result.latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        actual_layer = result.layer
        layer_match = "✅" if actual_layer == expected_layer else "❌"
        
        print(f"{layer_match} 输入：{input_text[:30]:<30} | 期望：{expected_layer:<12} | 实际：{actual_layer:<12}")
        print(f"   平均：{avg_latency:.3f}ms | 响应：{result.response[:50] if result.response else 'N/A'}\n")
        
        results.append({
            "input": input_text,
            "expected": expected_layer,
            "actual": actual_layer,
            "avg_ms": avg_latency
        })
    
    print("\n📊 缓存统计:")
    stats = response_cache.stats()
    print(f"   命中：{stats['hits']} | 未命中：{stats['misses']} | 命中率：{stats['hit_rate']}")
    
    return results

if __name__ == "__main__":
    run_benchmark()
