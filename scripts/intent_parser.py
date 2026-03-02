#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图识别器 - Intent Parser
解析用户输入，识别任务类型和关键信息
"""

import re
from typing import Dict, List, Any, Tuple
from enum import Enum

class IntentType(Enum):
    """意图类型"""
    CONTENT_CREATION = "content_creation"    # 内容创作
    IMAGE_GENERATION = "image_generation"    # 图像生成
    SOCIAL_PUBLISH = "social_publish"        # 社交发布
    CODING = "coding"                        # 编程
    DATA_ANALYSIS = "data_analysis"          # 数据分析
    SEARCH = "search"                        # 搜索
    TRANSLATION = "translation"              # 翻译
    REMINDER = "reminder"                    # 提醒
    CHAT = "chat"                            # 普通对话
    UNKNOWN = "unknown"                      # 未知

class IntentParser:
    """意图识别器"""
    
    def __init__(self):
        # 意图关键词配置
        self.intent_keywords = {
            IntentType.CONTENT_CREATION: [
                "写", "创作", "生成", "文案", "文章", "小说", "剧本",
                "标题", "广告", "营销", "推广", "海报文案"
            ],
            IntentType.IMAGE_GENERATION: [
                "图", "照片", "自拍", "图片", "画", "生成图", "做图",
                "头像", "封面", "海报", "泳装", "性感"
            ],
            IntentType.SOCIAL_PUBLISH: [
                "发布", "发到", "小红书", "微博", "抖音", "朋友圈",
                "发一条", "推送", "更新"
            ],
            IntentType.CODING: [
                "代码", "脚本", "程序", "编程", "开发", "自动化",
                "写个", "帮我写", "实现", "功能"
            ],
            IntentType.DATA_ANALYSIS: [
                "分析", "报表", "数据", "统计", "图表", "报告",
                "汇总", "对比", "趋势"
            ],
            IntentType.SEARCH: [
                "搜索", "查找", "查询", "找", "搜索一下", "查一下",
                "了解一下", "看看"
            ],
            IntentType.TRANSLATION: [
                "翻译", "translate", "中英", "英文", "日语", "韩语"
            ],
            IntentType.REMINDER: [
                "提醒", "定时", "闹钟", "记得", "别忘了"
            ],
            IntentType.CHAT: [
                "你好", "在吗", "怎么样", "怎么样", "聊天", "说说话"
            ]
        }
        
        # 平台识别
        self.platforms = {
            "小红书": ["小红书", "红书", "xhs"],
            "微博": ["微博", "wb"],
            "抖音": ["抖音", "douyin", "tiktok"],
            "朋友圈": ["朋友圈", "pyq"],
            "QQ": ["QQ", "qq"],
            "微信": ["微信", "wechat"]
        }
        
        # 内容类型识别
        self.content_types = {
            "自拍": ["自拍", "照片", "写真"],
            "文案": ["文案", "标题", "广告语"],
            "文章": ["文章", "博客", "推文"],
            "视频": ["视频", "vlog", "短视频"]
        }
    
    def parse(self, user_input: str) -> Dict[str, Any]:
        """解析用户输入"""
        result = {
            "original_input": user_input,
            "intents": [],
            "platform": None,
            "content_type": None,
            "keywords": [],
            "confidence": 0.0
        }
        
        # 识别意图
        for intent_type, keywords in self.intent_keywords.items():
            matched = []
            for kw in keywords:
                if kw in user_input:
                    matched.append(kw)
            
            if matched:
                result["intents"].append({
                    "type": intent_type.value,
                    "matched_keywords": matched,
                    "confidence": len(matched) / len(keywords)
                })
                result["keywords"].extend(matched)
        
        # 识别平台
        for platform, aliases in self.platforms.items():
            for alias in aliases:
                if alias in user_input.lower():
                    result["platform"] = platform
                    break
        
        # 识别内容类型
        for content_type, aliases in self.content_types.items():
            for alias in aliases:
                if alias in user_input:
                    result["content_type"] = content_type
                    break
        
        # 计算总体置信度
        if result["intents"]:
            result["confidence"] = sum(i["confidence"] for i in result["intents"]) / len(result["intents"])
        
        return result
    
    def get_primary_intent(self, user_input: str) -> Tuple[IntentType, float]:
        """获取主要意图"""
        result = self.parse(user_input)
        
        if not result["intents"]:
            return IntentType.UNKNOWN, 0.0
        
        # 按置信度排序
        sorted_intents = sorted(result["intents"], key=lambda x: x["confidence"], reverse=True)
        primary = sorted_intents[0]
        
        return IntentType(primary["type"]), primary["confidence"]
    
    def is_multi_intent(self, user_input: str) -> bool:
        """判断是否是多意图任务"""
        result = self.parse(user_input)
        return len(result["intents"]) > 1
    
    def extract_entities(self, user_input: str) -> Dict[str, List[str]]:
        """提取实体信息"""
        entities = {
            "time": [],      # 时间
            "location": [],  # 地点
            "person": [],    # 人物
            "topic": []      # 主题
        }
        
        # 时间提取（简单匹配）
        time_patterns = [
            r'\d+点', r'今天', r'明天', r'后天', r'下周',
            r'上午', r'下午', r'晚上', r'早上'
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, user_input)
            entities["time"].extend(matches)
        
        # 地点提取
        location_keywords = ["在", "去", "到"]
        for kw in location_keywords:
            if kw in user_input:
                # 提取后面的词
                parts = user_input.split(kw)
                if len(parts) > 1:
                    entities["location"].append(parts[1][:10])
        
        return entities

# 测试
if __name__ == "__main__":
    parser = IntentParser()
    
    test_cases = [
        "帮我写个小红书文案，配张性感自拍",
        "搜索一下最新的AI新闻",
        "明天下午3点提醒我开会",
        "写个Python脚本分析Excel数据"
    ]
    
    for text in test_cases:
        result = parser.parse(text)
        print(f"\n输入: {text}")
        print(f"意图: {result['intents']}")
        print(f"平台: {result['platform']}")
        print(f"置信度: {result['confidence']:.2f}")