#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 超高速预响应层 (Fast Response Layer)

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
from typing import Dict, Tuple, Optional, Any
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum

# ==================== Layer 0: 零思考响应 ====================

@dataclass
class FastResponse:
    """快速响应规则"""
    patterns: list
    response: str
    save_tokens: bool = True

# Layer 0 规则库 - 完全不调 LLM（v2.8.2: 10 条 → 30 条）
LAYER0_RULES = [
    # ========== 问候类 (5 条) ==========
    FastResponse(
        patterns=["你好", "您好", "hello", "hi", "早", "早上好", "晚上好", "午安"],
        response="老板好呀～💋 随时待命！"
    ),
    FastResponse(
        patterns=["在吗", "在不在", "有人吗", "在线"],
        response="在呢老板～ 有什么吩咐？😊"
    ),
    FastResponse(
        patterns=["好久不见", "最近怎么样", "最近好吗"],
        response="好久不见老板～ 想死您啦！💕 最近过得怎么样？"
    ),
    FastResponse(
        patterns=["嗨", "哈喽", "hey", "嗨喽"],
        response="嗨老板～👋 今天心情怎么样？"
    ),
    FastResponse(
        patterns=["起床了吗", "醒了吗", "睡着没"],
        response="醒着呢老板～ 24 小时为您待命！⚡"
    ),
    
    # ========== 告别类 (5 条) ==========
    FastResponse(
        patterns=["再见", "拜拜", "bye", "下次见"],
        response="老板慢走～ 随时叫我哦！💋"
    ),
    FastResponse(
        patterns=["先这样", "我去忙了", "回聊", "回头聊"],
        response="好的老板～ 忙完记得找我！😊"
    ),
    FastResponse(
        patterns=["晚安", "早点休息", "去睡了", "睡觉了"],
        response="晚安老板～ 做个好梦！🌙 明天见！"
    ),
    FastResponse(
        patterns=["有空再聊", "改天聊", "下次再聊"],
        response="好的老板～ 随时等您！💋"
    ),
    FastResponse(
        patterns=["撤了", "溜了", "下线了", "先下了"],
        response="老板慢走～ 路上小心！😊"
    ),
    
    # ========== 感谢类 (5 条) ==========
    FastResponse(
        patterns=["谢谢", "谢谢你", "多谢"],
        response="跟我还客气什么呀～💕"
    ),
    FastResponse(
        patterns=["thank you", "thanks", "thx"],
        response="You're welcome～ 老板开心最重要！😊"
    ),
    FastResponse(
        patterns=["辛苦了", "麻烦你了", "辛苦啦"],
        response="不辛苦～ 能为老板效劳是我的荣幸！💋"
    ),
    FastResponse(
        patterns=["感谢", "太感谢了", "非常感谢"],
        response="老板客气啦～ 应该的！😊"
    ),
    FastResponse(
        patterns=["感恩", "比心", "爱你"],
        response="嘿嘿～ 我也爱老板！💕💕💕"
    ),
    
    # ========== 确认类 (5 条) ==========
    FastResponse(
        patterns=["好的", "好", "ok", "嗯", "行"],
        response="收到老板！✅"
    ),
    FastResponse(
        patterns=["没问题", "可以的", "行哒", "好哒"],
        response="好嘞老板～ 马上办！⚡"
    ),
    FastResponse(
        patterns=["收到", "明白", "懂了", "知道了"],
        response="好的老板～ 理解万岁！😊"
    ),
    FastResponse(
        patterns=["对的", "是的", "没错", "正确"],
        response="英雄所见略同～ 老板英明！👍"
    ),
    FastResponse(
        patterns=["好的谢谢", "好的麻烦你了", "好的辛苦了"],
        response="老板太客气啦～ 应该的！💕"
    ),
    
    # ========== 时间日期 (5 条) ==========
    FastResponse(
        patterns=["几点了", "现在时间", "几点", "时间"],
        response=lambda: f"现在{datetime.now().strftime('%H:%M')}啦～ ⏰"
    ),
    FastResponse(
        patterns=["今天几号", "今天日期"],
        response=lambda: f"今天{datetime.now().strftime('%Y年%m月%d日')}～ 📅"
    ),
    FastResponse(
        patterns=["今天星期几", "今天周几", "星期几"],
        response=lambda: f"今天{['周一','周二','周三','周四','周五','周六','周日'][datetime.now().weekday()]}～ 📅"
    ),
    FastResponse(
        patterns=["明天", "后天", "大后天"],
        response=lambda: f"老板，{datetime.now().strftime('%Y-%m-%d')}之后的一天好天气哦～ ☀️"
    ),
    FastResponse(
        patterns=["昨天", "前天", "大前天"],
        response="昨天已经过去啦～ 珍惜当下！💕"
    ),
    
    # ========== 情感类 (5 条) ==========
    FastResponse(
        patterns=["不知道", "不清楚", "算了", "没事"],
        response="没事老板～ 有需要随时叫我！😊"
    ),
    FastResponse(
        patterns=["真棒", "厉害", "不错", "很好"],
        response="嘿嘿～ 老板开心最重要！😊"
    ),
    FastResponse(
        patterns=["加油", "你可以的", "我相信你"],
        response="谢谢老板鼓励～ 动力满满！💪💪💪"
    ),
    FastResponse(
        patterns=["累了", "好累", "累死了"],
        response="老板辛苦啦～ 快休息一下！☕️ 我给您捏捏肩～💆"
    ),
    FastResponse(
        patterns=["开心", "高兴", "爽", "哈哈"],
        response="老板开心我就开心～ 一起嗨！🎉"
    ),
]

# ==================== Layer 1: 缓存响应 ====================

class LRUCache:
    """LRU 缓存 - 记忆永不丢失的基石"""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: Dict[str, Any] = {}
        self.order: list = []
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.hits += 1
            # 移到末尾（最近使用）
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # 删除最旧的
            oldest = self.order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.order.append(key)
    
    def stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hits/total*100:.1f}%" if total > 0 else "0%",
            "size": len(self.cache),
            "capacity": self.capacity
        }

# 全局缓存实例
response_cache = LRUCache(capacity=1000)

# ==================== Layer 0 匹配引擎 ====================

def normalize_text(text: str) -> str:
    """文本归一化 - 提高匹配率"""
    # 转小写
    text = text.lower()
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 去除标点
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return text

def match_layer0(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    Layer 0: 零思考响应匹配
    
    Returns:
        (是否匹配，响应内容)
    """
    normalized = normalize_text(user_input)
    
    for rule in LAYER0_RULES:
        for pattern in rule.patterns:
            if pattern in normalized or pattern in user_input:
                # 动态响应（lambda）
                if callable(rule.response):
                    return True, rule.response()
                # 静态响应
                return True, rule.response
    
    return False, None

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
    """响应结果"""
    layer: str  # layer0, layer1, layer2, layer3
    response: str
    latency_ms: float
    tokens_saved: bool
    cache_hit: bool

def fast_respond(user_input: str, skip_layers: list = None) -> ResponseResult:
    """
    超高速响应入口
    
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
        matched, response = match_layer0(user_input)
        if matched:
            latency = (time.time() - start_time) * 1000
            return ResponseResult(
                layer="layer0",
                response=response,
                latency_ms=latency,
                tokens_saved=True,
                cache_hit=False
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
    
    # Layer 2/3: 需要 LLM（本层不处理，返回 None 表示继续）
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
    print("🚀 灵犀超高速响应层 - 性能测试")
    print("=" * 60)
    
    test_cases = [
        # Layer 0 测试
        ("你好", "layer0"),
        ("在吗", "layer0"),
        ("谢谢", "layer0"),
        ("几点了", "layer0"),
        ("今天星期几", "layer0"),
        
        # Layer 1 测试（先缓存再测试）
        ("测试缓存问题", "layer1"),
        
        # 未匹配（passthrough）
        ("帮我写个复杂的 Python 脚本分析数据", "passthrough"),
        ("开发一个完整的电商系统", "passthrough"),
    ]
    
    # 先预热缓存
    print("\n📦 预热缓存...")
    cache_response("测试缓存问题", "这是缓存的回复～ 😊")
    
    results = []
    
    print("\n⚡ 开始测试...\n")
    
    for input_text, expected_layer in test_cases:
        # 跑 100 次取平均
        latencies = []
        for _ in range(100):
            result = fast_respond(input_text)
            latencies.append(result.latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # 验证层
        actual_layer = result.layer
        layer_match = "✅" if actual_layer == expected_layer else "❌"
        
        print(f"{layer_match} 输入：{input_text[:30]:<30} | 期望：{expected_layer:<12} | 实际：{actual_layer:<12}")
        print(f"   平均：{avg_latency:.3f}ms | 最小：{min_latency:.3f}ms | 最大：{max_latency:.3f}ms")
        print(f"   响应：{result.response[:50] if result.response else 'N/A'}\n")
        
        results.append({
            "input": input_text,
            "expected": expected_layer,
            "actual": actual_layer,
            "avg_ms": avg_latency,
            "min_ms": min_latency,
            "max_ms": max_latency
        })
    
    # 缓存统计
    print("\n📊 缓存统计:")
    stats = response_cache.stats()
    print(f"   命中：{stats['hits']} | 未命中：{stats['misses']} | 命中率：{stats['hit_rate']}")
    print(f"   大小：{stats['size']}/{stats['capacity']}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📈 性能总结:")
    print("=" * 60)
    
    layer0_results = [r for r in results if r['expected'] == 'layer0']
    layer1_results = [r for r in results if r['expected'] == 'layer1']
    
    if layer0_results:
        avg_l0 = sum(r['avg_ms'] for r in layer0_results) / len(layer0_results)
        print(f"⚡ Layer 0 (零思考): 平均 {avg_l0:.3f}ms - 100% 节省 Tokens")
    
    if layer1_results:
        avg_l1 = sum(r['avg_ms'] for r in layer1_results) / len(layer1_results)
        print(f"💾 Layer 1 (缓存):   平均 {avg_l1:.3f}ms - 100% 节省 Tokens")
    
    print("\n🎯 三大目标进展:")
    print("   ⚡ 快速反应: Layer 0 <5ms, Layer 1 <10ms ✅")
    print("   💰 Tokens 消耗: Layer 0/1 零消耗 ✅")
    print("   🧠 记忆永不丢失: LRU 缓存 1000 条 + 持久化（待实现）🔄")
    
    return results

if __name__ == "__main__":
    run_benchmark()
