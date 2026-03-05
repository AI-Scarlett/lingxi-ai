#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - Layer 0 技能调用系统

功能:
1.  Layer 0 直接调用技能（不调 LLM）
2.  支持自拍、天气、新闻等常用技能
3.  参数自动提取
4.  预定义回复模板
5.  节省 Tokens，提升速度

使用方式:
    from layer0_skills import match_layer0_skill
    
    # 匹配并执行技能
    matched, result = match_layer0_skill("来张自拍")
    if matched:
        # result = {"action": "clawra_selfie", "params": {...}, "reply": "好的，马上就来～💋"}
        execute_skill(result)
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field

# ==================== 配置 ====================

SKILL_CONFIG_FILE = Path.home() / ".openclaw" / "workspace" / ".learnings" / "layer0_skills.json"

# ==================== 数据结构 ====================

@dataclass
class SkillRule:
    """技能规则"""
    id: str
    patterns: List[str]
    skill_name: str  # 技能名称
    action: str  # 对应 action
    params_template: Dict[str, Any]  # 参数模板
    reply_template: str  # 回复模板
    enabled: bool = True
    priority: int = 0
    param_extractors: Dict[str, str] = field(default_factory=dict)  # 参数提取正则
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "patterns": self.patterns,
            "skill_name": self.skill_name,
            "action": self.action,
            "params_template": self.params_template,
            "reply_template": self.reply_template,
            "enabled": self.enabled,
            "priority": self.priority,
            "param_extractors": self.param_extractors
        }

# ==================== 预定义技能规则 ====================

def get_builtin_skills() -> List[SkillRule]:
    """获取内置技能规则"""
    return [
        # 📸 自拍技能
        SkillRule(
            id="skill_selfie",
            patterns=["来张自拍", "自拍", "发张自拍", "拍张照", "自拍一张", "你的照片", "看看你"],
            skill_name="clawra_selfie",
            action="clawra_selfie",
            params_template={"mode": "direct", "outfit": "default"},
            reply_template="好的老板～ 马上就来～💋",
            priority=100,
            param_extractors={
                "mode": r"(镜子 | 镜前 | 全身|mirror)→mirror",
                "outfit": r"(穿 | 穿着| outfit|衣服)(.*?) (裙子 | 西装 | 休闲 | 运动|泳装|礼服)"
            }
        ),
        
        # 🌤️ 天气技能
        SkillRule(
            id="skill_weather",
            patterns=["天气", "天气怎么样", "今天天气", "明天天气", "天气预报", "外面天气"],
            skill_name="weather",
            action="weather_get",
            params_template={"city": "auto", "days": 1},
            reply_template="好的老板～ 马上查询天气～🌤️",
            priority=100,
            param_extractors={
                "city": r"(北京 | 上海 | 广州 | 深圳 | 杭州|成都)",
                "days": r"(未来 | 接下来)(\d+) 天"
            }
        ),
        
        # 📰 新闻技能
        SkillRule(
            id="skill_news",
            patterns=["新闻", "有什么新闻", "今天新闻", "最新资讯", "最新消息"],
            skill_name="news",
            action="news_get",
            params_template={"category": "top", "count": 5},
            reply_template="好的老板～ 马上为您搜集新闻～📰",
            priority=90,
            param_extractors={
                "category": r"(科技 | 财经 | 体育 | 娱乐 | 国际|两会)"
            }
        ),
        
        # 🔍 搜索技能
        SkillRule(
            id="skill_search",
            patterns=["搜索", "查一下", "百度一下", "google", "搜一下"],
            skill_name="web_search",
            action="web_search",
            params_template={"query": "", "count": 5},
            reply_template="好的老板～ 马上搜索～🔍",
            priority=90,
            param_extractors={
                "query": r"(搜索 | 查一下 | 百度一下|google)(.*)$"
            }
        ),
        
        # ⏰ 提醒技能
        SkillRule(
            id="skill_reminder",
            patterns=["提醒我", "记得提醒", "定时", "闹钟", "N 分钟后提醒"],
            skill_name="reminder",
            action="reminder_create",
            params_template={"minutes": 5, "message": "定时提醒"},
            reply_template="好的老板～ 已经设置好提醒啦～⏰",
            priority=95,
            param_extractors={
                "minutes": r"(\d+) (分钟 | 分钟后|分钟后)",
                "message": r"提醒我 (.*)$"
            }
        ),
        
        # 📝 小红书技能
        SkillRule(
            id="skill_xiaohongshu",
            patterns=["小红书文案", "写小红书", "发小红书", "小红书笔记"],
            skill_name="xiaohongshu",
            action="xhs_generate",
            params_template={"topic": "", "style": "default"},
            reply_template="好的老板～ 马上为您生成小红书文案～📱",
            priority=100,
            param_extractors={
                "topic": r"(小红书 | 写 | 主题|关于)(.*)$",
                "style": r"(风格 | 类型)(可爱 | 专业 | 搞笑 | 文艺|干货)"
            }
        ),
        
        # 🎵 音乐技能
        SkillRule(
            id="skill_music",
            patterns=["放首歌", "播放音乐", "来首歌", "听歌", "音乐"],
            skill_name="music",
            action="music_play",
            params_template={"song": "", "artist": ""},
            reply_template="好的老板～ 马上播放～🎵",
            priority=80,
            param_extractors={
                "song": r"(播放 | 听|来首)(.*?) (歌 | 音乐)",
                "artist": r"(歌手 | 演唱)(.*)"
            }
        ),
        
        # 📊 股票技能
        SkillRule(
            id="skill_stock",
            patterns=["股票", "股价", "大盘", "A 股", "美股", "港股"],
            skill_name="stock",
            action="stock_get",
            params_template={"symbol": "", "market": "auto"},
            reply_template="好的老板～ 马上查询股价～📊",
            priority=85,
            param_extractors={
                "symbol": r"(股票 | 股价)(.*?) (怎么样 | 多少|价格)",
                "market": r"(A 股 | 美股 | 港股 | 沪深|纳斯达克)"
            }
        ),
        
        # 💱 汇率技能
        SkillRule(
            id="skill_currency",
            patterns=["汇率", "换算", "美元", "人民币", "日元", "欧元"],
            skill_name="currency",
            action="currency_convert",
            params_template={"from": "USD", "to": "CNY", "amount": 1},
            reply_template="好的老板～ 马上换算汇率～💱",
            priority=80,
            param_extractors={
                "from": r"(美元 | 美金|USD)",
                "to": r"(人民币|CNY|欧元|EUR|日元|JPY)"
            }
        ),
        
        # 🍔 外卖技能
        SkillRule(
            id="skill_food",
            patterns=["点外卖", "饿了", "吃什么", "推荐餐厅", "附近美食"],
            skill_name="food",
            action="food_recommend",
            params_template={"cuisine": "any", "location": "auto"},
            reply_template="好的老板～ 马上为您推荐美食～🍔",
            priority=85,
            param_extractors={
                "cuisine": r"(川菜 | 粤菜 | 日料 | 韩料 | 火锅 | 烧烤|快餐)"
            }
        ),
        
        # 🚗 打车技能
        SkillRule(
            id="skill_taxi",
            patterns=["打车", "叫车", "滴滴", "网约车", "叫个车"],
            skill_name="taxi",
            action="taxi_order",
            params_template={"type": "express", "destination": ""},
            reply_template="好的老板～ 马上为您叫车～🚗",
            priority=90,
            param_extractors={
                "type": r"(快车 | 专车 | 豪华车|出租车)",
                "destination": r"(去 | 到|目的地)(.*)"
            }
        ),
        
        # 🏨 酒店技能
        SkillRule(
            id="skill_hotel",
            patterns=["订酒店", "酒店", "住宿", "推荐酒店"],
            skill_name="hotel",
            action="hotel_search",
            params_template={"city": "auto", "stars": 4},
            reply_template="好的老板～ 马上为您搜索酒店～🏨",
            priority=80,
            param_extractors={
                "city": r"(北京 | 上海 | 广州 | 深圳 | 杭州|成都)",
                "stars": r"(几星 | 星级)(\d+)"
            }
        ),
        
        # ✈️ 机票技能
        SkillRule(
            id="skill_flight",
            patterns=["机票", "飞机票", "航班", "订票", "航班查询"],
            skill_name="flight",
            action="flight_search",
            params_template={"from": "", "to": "", "date": "today"},
            reply_template="好的老板～ 马上查询航班～✈️",
            priority=80,
            param_extractors={
                "from": r"(从 | 出发地)(.*?) (到|去)",
                "to": r"(到 | 去|目的地)(.*?) (的|机票)",
                "date": r"(今天 | 明天 | 后天|日期)(\d{4}-\d{2}-\d{2})"
            }
        ),
        
        # 🎬 电影技能
        SkillRule(
            id="skill_movie",
            patterns=["电影", "看电影", "最新电影", "电影推荐", "票房"],
            skill_name="movie",
            action="movie_get",
            params_template={"type": "now_playing", "city": "auto"},
            reply_template="好的老板～ 马上为您查询电影～🎬",
            priority=80,
            param_extractors={
                "type": r"(正在上映 | 即将上映 | 经典 | 热门|最新)"
            }
        ),
        
        # 📅 日历技能
        SkillRule(
            id="skill_calendar",
            patterns=["日历", "日程", "今天有什么安排", "明天安排", "查看日程"],
            skill_name="calendar",
            action="calendar_get",
            params_template={"date": "today", "range": "day"},
            reply_template="好的老板～ 马上查看日程～📅",
            priority=85,
            param_extractors={
                "date": r"(今天 | 明天 | 后天|日期)(\d{4}-\d{2}-\d{2})",
                "range": r"(今天 | 明天 | 本周 | 本月|全部)"
            }
        ),
    ]

# ==================== 技能匹配器 ====================

class Layer0SkillMatcher:
    """Layer 0 技能匹配器"""
    
    def __init__(self):
        self.skills = get_builtin_skills()
        self.config_file = SKILL_CONFIG_FILE
        
        # 加载用户自定义技能
        self._load_custom_skills()
    
    def _load_custom_skills(self):
        """加载用户自定义技能"""
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding='utf-8'))
                for skill_data in data.get("custom_skills", []):
                    skill = SkillRule(**skill_data)
                    self.skills.append(skill)
            except Exception as e:
                print(f"⚠️  加载自定义技能失败：{e}")
    
    def match(self, user_input: str) -> Tuple[bool, Optional[Dict]]:
        """匹配技能
        
        Args:
            user_input: 用户输入
            
        Returns:
            (matched, result)
            result = {
                "skill_name": str,
                "action": str,
                "params": dict,
                "reply": str,
                "skill_id": str
            }
        """
        # 按优先级排序
        sorted_skills = sorted(self.skills, key=lambda x: x.priority, reverse=True)
        
        for skill in sorted_skills:
            if not skill.enabled:
                continue
            
            for pattern in skill.patterns:
                if pattern in user_input:
                    # 匹配成功，提取参数
                    params = self._extract_params(skill, user_input)
                    
                    # 生成回复
                    reply = skill.reply_template
                    
                    return True, {
                        "skill_name": skill.skill_name,
                        "action": skill.action,
                        "params": params,
                        "reply": reply,
                        "skill_id": skill.id
                    }
        
        return False, None
    
    def _extract_params(self, skill: SkillRule, user_input: str) -> Dict:
        """提取参数"""
        params = skill.params_template.copy()
        
        for param_name, pattern in skill.param_extractors.items():
            try:
                match = re.search(pattern, user_input)
                if match:
                    # 处理箭头语法（value→replacement）
                    if "→" in pattern:
                        parts = pattern.split("→")
                        if len(parts) == 2:
                            value = match.group(2) if len(match.groups()) > 1 else match.group(1)
                            params[param_name] = value
                    else:
                        # 普通提取
                        groups = match.groups()
                        if groups:
                            params[param_name] = groups[-1] if len(groups) > 1 else groups[0]
            except:
                pass
        
        return params
    
    def add_custom_skill(self, skill: SkillRule):
        """添加自定义技能"""
        self.skills.append(skill)
        self._save_custom_skills()
    
    def _save_custom_skills(self):
        """保存自定义技能"""
        custom_skills = [s.to_dict() for s in self.skills if s.id.startswith("custom_")]
        
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "custom_skills": custom_skills
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

# ==================== 全局实例 ====================

_matcher: Optional[Layer0SkillMatcher] = None

def get_skill_matcher() -> Layer0SkillMatcher:
    """获取全局实例"""
    global _matcher
    if _matcher is None:
        _matcher = Layer0SkillMatcher()
    return _matcher

def match_layer0_skill(user_input: str) -> Tuple[bool, Optional[Dict]]:
    """匹配 Layer 0 技能（便捷函数）"""
    matcher = get_skill_matcher()
    return matcher.match(user_input)

def add_custom_skill(patterns: List[str], skill_name: str, action: str, 
                     params_template: Dict, reply_template: str, 
                     priority: int = 0, param_extractors: Dict = None) -> str:
    """添加自定义技能（便捷函数）"""
    matcher = get_skill_matcher()
    
    skill = SkillRule(
        id=f"custom_skill_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        patterns=patterns,
        skill_name=skill_name,
        action=action,
        params_template=params_template,
        reply_template=reply_template,
        priority=priority,
        param_extractors=param_extractors or {}
    )
    
    matcher.add_custom_skill(skill)
    return skill.id

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ 灵犀 Layer 0 技能调用测试")
    print("=" * 60)
    
    matcher = get_skill_matcher()
    
    test_cases = [
        "来张自拍",
        "今天天气怎么样",
        "有什么新闻",
        "搜索 AI 新闻",
        "5 分钟后提醒我开会",
        "写小红书文案",
        "放首歌",
        "股票怎么样",
        "美元换人民币",
        "饿了，点什么外卖",
    ]
    
    print("\n📋 测试技能匹配:\n")
    
    for text in test_cases:
        matched, result = matcher.match(text)
        if matched:
            print(f"✅ '{text}'")
            print(f"   技能：{result['skill_name']}")
            print(f"   Action: {result['action']}")
            print(f"   参数：{result['params']}")
            print(f"   回复：{result['reply']}")
        else:
            print(f"❌ '{text}' - 未匹配")
        print()
    
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
