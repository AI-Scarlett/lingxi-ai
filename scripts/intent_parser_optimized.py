#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图识别器 - Intent Parser (优化版)
- 使用 LRUCache 缓存结果
- 正则预编译加速匹配
- 短路逻辑提前返回
"""

import re
from typing import Dict, List, Any, Tuple
from functools import lru_cache
from enum import Enum

class IntentType(Enum):
    """意图类型"""
    CONTENT_CREATION = "content_creation"
    IMAGE_GENERATION = "image_generation"
    SOCIAL_PUBLISH = "social_publish"
    CODING = "coding"
    DATA_ANALYSIS = "data_analysis"
    SEARCH = "search"
    TRANSLATION = "translation"
    REMINDER = "reminder"
    CHAT = "chat"
    UNKNOWN = "unknown"

class FastIntentParser:
    """高速意图识别器 - 优化版本"""
    
    def __init__(self):
        # 预编译正则表达式 (加速匹配)
        self.compiled_patterns = {
            IntentType.CONTENT_CREATION: re.compile(r'(写 | 创作 | 生成 | 文案 | 文章 | 小说 | 剧本|标题 | 广告 | 营销 | 推广)'),
            IntentType.IMAGE_GENERATION: re.compile(r'(图 | 照片 | 自拍 | 图片 | 画 | 生成图 | 做图|头像 | 封面 | 海报)'),
            IntentType.SOCIAL_PUBLISH: re.compile(r'(发布 | 发到 | 小红书 | 微博 | 抖音 | 朋友圈 | 发一条|推送 | 更新)'),
            IntentType.CODING: re.compile(r'(代码 | 脚本 | 程序 | 编程 | 开发 | 自动化|实现 | 功能)'),
            IntentType.DATA_ANALYSIS: re.compile(r'(分析 | 报表 | 数据 | 统计 | 图表|报告 | 汇总 | 对比 | 趋势)'),
            IntentType.SEARCH: re.compile(r'(搜索 | 查找 | 查询 | 找一下 | 了解一下|看看 | 打听)'),
            IntentType.TRANSLATION: re.compile(r'(翻译|translate|中英|英文 | 日语 | 韩语)'),
            IntentType.REMINDER: re.compile(r'(提醒 | 定时 | 闹钟 | 记得 | 别忘了)'),
        }
        
        # 平台映射 (简化版)
        self.platform_map = {
            '小红书': ['xhs', '红书'],
            '微博': ['wb'],
            '抖音': ['douyin', 'tiktok'],
            '微信': ['wechat', 'pyq', '朋友圈'],
        }
        
        # 缓存最近 100 个输入结果 (避免重复解析)
        self._cache = {}
        self._max_cache = 100
    
    @lru_cache(maxsize=256)
    def parse(self, user_input: str) -> Dict[str, Any]:
        """解析用户输入 - 带缓存"""
        result = {
            "original_input": user_input,
            "intents": [],
            "platform": None,
            "keywords": [],
            "confidence": 0.0
        }
        
        input_lower = user_input.lower()
        
        # ✅ 优化 1: 使用预编译正则 + findall (一次扫描搞定)
        for intent_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(user_input)
            if matches:
                result["intents"].append({
                    "type": intent_type.value,
                    "matched": list(set(matches)),  # 去重
                    "count": len(matches)
                })
                result["keywords"].extend(matches)
        
        # ✅ 优化 2: 平台识别一次性完成
        for platform, aliases in self.platform_map.items():
            if any(a in input_lower for a in [platform] + aliases):
                result["platform"] = platform
                break
        
        # ✅ 优化 3: 快速计算置信度
        if result["intents"]:
            total_confidence = sum(i["count"] for i in result["intents"])
            result["confidence"] = min(total_confidence / 3, 1.0)  # 归一化到 0-1
        
        return result
    
    def get_primary_intent(self, user_input: str) -> Tuple[IntentType, float]:
        """获取主要意图 - 最快路径"""
        result = self.parse(user_input)
        
        if not result["intents"]:
            return IntentType.UNKNOWN, 0.0
        
        # 按匹配数量排序
        sorted_intents = sorted(result["intents"], key=lambda x: x["count"], reverse=True)
        primary = sorted_intents[0]
        
        return IntentType(primary["type"]), primary["count"] / 3
    
    def is_multi_intent(self, user_input: str) -> bool:
        """判断是否多意图"""
        result = self.parse(user_input)
        return len(result["intents"]) > 1


# 性能对比测试
if __name__ == "__main__":
    import time
    
    parser = FastIntentParser()
    
    test_cases = [
        "帮我写个小红书文案，配张性感自拍",
        "搜索一下最新的 AI 新闻",
        "明天下午 3 点提醒我开会",
        "写个 Python 脚本分析 Excel 数据"
    ]
    
    # 测试速度
    start = time.time()
    for _ in range(100):  # 跑 100 次
        for text in test_cases:
            parser.parse(text)
    end = time.time()
    
    print(f"✅ 100 轮测试耗时：{(end-start)*1000:.2f}ms")
    print(f"✅ 平均单次解析：{(end-start)/400*1000:.3f}ms")
    
    # 测试缓存效果
    print("\n📊 测试单个输入:")
    text = "帮我写个小红书文案"
    start = time.time()
    for _ in range(100):
        parser.parse(text)  # 应该走缓存
    print(f"  缓存命中：{(time.time()-start)*10:.3f}ms/100 次")
