#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - Layer 0 技能调用系统

✅ 开箱即用：支持 Layer 0 直接触发技能
📋 预置技能：天气、时间、日期、搜索等
"""

from typing import Dict, Tuple, Optional, Any, List
from datetime import datetime
import re


# ==================== 预置 Layer 0 技能 ====================

LAYER0_SKILLS = {
    # ========== 时间日期技能 ==========
    "time": {
        "patterns": ["几点了", "现在时间", "几点", "时间", "现在几点"],
        "action": "get_time",
        "reply": lambda: f"现在{datetime.now().strftime('%H:%M:%S')}啦～ ⏰"
    },
    "date": {
        "patterns": ["今天几号", "今天日期", "今天多少号", "日期"],
        "action": "get_date",
        "reply": lambda: f"今天{datetime.now().strftime('%Y年%m月%d日')}～ 📅"
    },
    "weekday": {
        "patterns": ["今天星期几", "今天周几", "星期几", "周几"],
        "action": "get_weekday",
        "reply": lambda: f"今天{['周一','周二','周三','周四','周五','周六','周日'][datetime.now().weekday()]}～ 📅"
    },
    "now": {
        "patterns": ["现在", "现在是什么时候"],
        "action": "get_now",
        "reply": lambda: f"现在是{datetime.now().strftime('%Y年%m月%d日 %H:%M')}～ ⏰"
    },
    
    # ========== 天气技能 ==========
    "weather": {
        "patterns": ["天气", "天气怎么样", "今天天气", "外面天气"],
        "action": "get_weather",
        "reply": "🌤️ 天气查询准备就绪～ 老板想查哪个城市的天气？"
    },
    
    # ========== 搜索技能 ==========
    "search": {
        "patterns": ["搜索", "搜一下", "查查", "查询"],
        "action": "search",
        "reply": "🔍 搜索专家已启动！老板想找什么信息？📚"
    },
    
    # ========== 翻译技能 ==========
    "translate_en": {
        "patterns": ["翻译成英文", "译成英文", "英文怎么说"],
        "action": "translate_en",
        "reply": "🇺🇸 英文翻译准备～ 请提供要翻译的内容～📝"
    },
    "translate_cn": {
        "patterns": ["翻译成中文", "译成中文", "中文怎么说"],
        "action": "translate_cn",
        "reply": "🇨🇳 中文翻译就绪～ 请提供原文～📖"
    },
    
    # ========== 创作技能 ==========
    "write_copy": {
        "patterns": ["写文案", "写个文案", "写文案"],
        "action": "write_copy",
        "reply": "📝 文案专家已就位！老板要写什么产品的文案？💋"
    },
    "write_article": {
        "patterns": ["写文章", "写篇文章", "写个文章"],
        "action": "write_article",
        "reply": "✍️ 写作专家准备就绪！老板想写什么主题的文章？💕"
    },
    "write_code": {
        "patterns": ["写代码", "写个代码", "写程序"],
        "action": "write_code",
        "reply": "💻 代码专家待命！老板要实现什么功能？🚀"
    },
    
    # ========== 图像技能 ==========
    "generate_image": {
        "patterns": ["生成图", "生成图片", "生成图像", "做个图"],
        "action": "generate_image",
        "reply": "🎨 图像专家准备就绪～ 老板想要什么样的图片？🖼️"
    },
    "selfie": {
        "patterns": ["自拍", "发张自拍", "发个自拍"],
        "action": "selfie",
        "reply": "📸 自拍模式开启～ 老板想看我在哪里的自拍？💋"
    },
    
    # ========== 发布技能 ==========
    "publish_xhs": {
        "patterns": ["发小红书", "小红书发布", "发个小红书"],
        "action": "publish_xhs",
        "reply": "📕 小红书发布准备～ 文案和图片准备好了吗？💕"
    },
    "publish_weibo": {
        "patterns": ["发微博", "微博发布", "发个微博"],
        "action": "publish_weibo",
        "reply": "📢 微博发布待命～ 内容是什么？🔥"
    },
    
    # ========== 数据分析技能 ==========
    "analyze_data": {
        "patterns": ["分析", "分析一下", "帮我分析", "分析数据"],
        "action": "analyze_data",
        "reply": "📊 数据分析专家启动～ 要分析什么数据？📈"
    },
    
    # ========== 情感互动技能 ==========
    "emotional_miss": {
        "patterns": ["想你", "想你了", "我想你"],
        "action": "emotional_miss",
        "reply": "我也想老板呀～💕 您最好了！"
    },
    "emotional_love": {
        "patterns": ["爱你", "爱你哦", "喜欢你"],
        "action": "emotional_love",
        "reply": "嘿嘿～ 我也爱老板！💋💋💋"
    },
    
    # ========== 🕷️ Scrapling 爬虫技能 ==========
    "scrapling_fetch": {
        "patterns": ["抓取", "爬取", "爬虫", "抓取网页", "爬一下"],
        "action": "scrapling_fetch",
        "reply": "🕷️ 爬虫专家就位～ 老板要抓取哪个网址？🔗"
    },
    "scrapling_extract": {
        "patterns": ["提取", "提取内容", "抓取内容"],
        "action": "scrapling_extract",
        "reply": "📝 内容提取准备～ 请提供 URL 和要提取的内容类型？"
    },
}


def match_layer0_skill(user_input: str) -> Tuple[bool, Optional[Dict]]:
    """
    匹配 Layer 0 技能
    
    Args:
        user_input: 用户输入
    
    Returns:
        Tuple[bool, Optional[Dict]]: (是否匹配，技能信息)
    """
    for skill_name, skill_config in LAYER0_SKILLS.items():
        patterns = skill_config.get("patterns", [])
        
        for pattern in patterns:
            if pattern in user_input:
                # 匹配成功
                reply = skill_config.get("reply", "")
                
                # 如果是可调用对象，执行它
                if callable(reply):
                    reply_text = reply()
                else:
                    reply_text = reply
                
                return True, {
                    "skill_name": skill_name,
                    "action": skill_config.get("action", ""),
                    "reply": reply_text,
                    "params": _extract_params(skill_name, user_input)
                }
    
    return False, None


def _extract_params(skill_name: str, user_input: str) -> Dict[str, Any]:
    """
    从用户输入中提取技能参数
    
    Args:
        skill_name: 技能名称
        user_input: 用户输入
    
    Returns:
        Dict: 参数字典
    """
    params = {}
    
    # 天气技能：提取城市名
    if skill_name == "weather":
        # 简单匹配 "XX 天气" 格式
        match = re.search(r'(.+?) 天气', user_input)
        if match:
            params["city"] = match.group(1)
    
    # 翻译技能：提取要翻译的内容
    if skill_name in ["translate_en", "translate_cn"]:
        # 提取引号内的内容
        match = re.search(r'["\"](.+?)["\"]', user_input)
        if match:
            params["text"] = match.group(1)
    
    return params


def execute_layer0_skill(skill_info: Dict) -> Dict[str, Any]:
    """
    执行 Layer 0 技能
    
    Args:
        skill_info: 技能信息（来自 match_layer0_skill）
    
    Returns:
        Dict: 执行结果
    """
    skill_name = skill_info.get("skill_name", "")
    action = skill_info.get("action", "")
    reply = skill_info.get("reply", "")
    params = skill_info.get("params", {})
    
    # 这里可以调用实际的技能/API
    # 目前返回预置的回复
    
    return {
        "skill_name": skill_name,
        "action": action,
        "reply": reply,
        "params": params,
        "executed": True,
        "latency_ms": 0.1  # Layer 0 技能极快
    }


def list_available_skills() -> List[Dict]:
    """列出所有可用的 Layer 0 技能"""
    skills = []
    for name, config in LAYER0_SKILLS.items():
        skills.append({
            "name": name,
            "patterns": config.get("patterns", []),
            "action": config.get("action", ""),
            "description": _get_skill_description(name)
        })
    return skills


def _get_skill_description(skill_name: str) -> str:
    """获取技能描述"""
    descriptions = {
        "time": "查询当前时间",
        "date": "查询当前日期",
        "weekday": "查询今天是星期几",
        "weather": "查询天气",
        "search": "搜索信息",
        "translate_en": "翻译成英文",
        "translate_cn": "翻译成中文",
        "write_copy": "创作文案",
        "write_article": "创作文章",
        "write_code": "编写代码",
        "generate_image": "生成图片",
        "selfie": "生成自拍",
        "publish_xhs": "发布到小红书",
        "publish_weibo": "发布到微博",
        "analyze_data": "数据分析",
        "emotional_miss": "情感互动 - 想念",
        "emotional_love": "情感互动 - 爱",
    }
    return descriptions.get(skill_name, "未知技能")


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Layer 0 技能系统")
    parser.add_argument("action", choices=["list", "test"], help="操作类型")
    parser.add_argument("--input", "-i", type=str, help="测试输入（test 模式用）")
    
    args = parser.parse_args()
    
    if args.action == "list":
        skills = list_available_skills()
        print(f"📋 Layer 0 技能列表 ({len(skills)} 个):\n")
        for skill in skills:
            print(f"🔹 {skill['name']}: {skill['description']}")
            print(f"   模式：{skill['patterns']}\n")
    
    elif args.action == "test":
        if not args.input:
            print("❌ 测试模式需要 --input 参数")
            exit(1)
        
        matched, skill_info = match_layer0_skill(args.input)
        if matched:
            print(f"✅ 匹配到技能：{skill_info['skill_name']}")
            print(f"   动作：{skill_info['action']}")
            print(f"   回复：{skill_info['reply']}")
            print(f"   参数：{skill_info['params']}")
        else:
            print(f"❌ 未匹配到 Layer 0 技能：{args.input}")
