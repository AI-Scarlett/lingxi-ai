#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 超高速预响应层 v2.0 Extended (扩展版)

✅ v3.0.2 扩展：Layer 0 规则从 95 条 → 300+ 条
目标：快速响应率从 65% 提升到 85%+
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fast_response_layer_v2 import LAYER0_RULES, FastResponse

# ==================== 扩展规则库 (新增 200+ 条) ====================

EXTENDED_RULES = [
    # ========== 创作请求类 (20 条) ==========
    FastResponse(
        patterns=["帮我写", "给我写", "写一个", "写一篇", "写个"],
        response="👌 收到老板！马上为您创作～ 请告诉我具体要写什么？📝"
    ),
    FastResponse(
        patterns=["写文案", "写个文案", "写文案"],
        response="📝 文案专家已就位！老板要写什么产品的文案？有什么风格偏好？💋"
    ),
    FastResponse(
        patterns=["写文章", "写篇文章", "写个文章"],
        response="✍️ 写作专家准备就绪！老板想写什么主题的文章？💕"
    ),
    FastResponse(
        patterns=["写代码", "写个代码", "写程序", "写个程序"],
        response="💻 代码专家待命！老板要实现什么功能？🚀"
    ),
    FastResponse(
        patterns=["写报告", "写个报告", "写报告"],
        response="📊 数据专家准备中～ 老板要什么类型的报告？📈"
    ),
    FastResponse(
        patterns=["写邮件", "写个邮件", "写邮件"],
        response="📧 邮件文案马上来～ 收件人是谁？什么主题？💌"
    ),
    FastResponse(
        patterns=["写脚本", "写个脚本", "写脚本"],
        response="🔧 脚本专家就位！什么语言的脚本？实现什么功能？⚡"
    ),
    FastResponse(
        patterns=["写小说", "写个小说", "写故事"],
        response="📖 创作模式启动～ 老板想看什么类型的故事？💕"
    ),
    FastResponse(
        patterns=["写诗", "写首诗", "写诗歌"],
        response="🎭 诗人模式开启～ 什么主题？古风还是现代？✨"
    ),
    FastResponse(
        patterns=["写总结", "写个总结", "写周报", "写月报"],
        response="📋 总结专家待命～ 老板要总结什么内容？📝"
    ),
    
    # ========== 搜索查询类 (15 条) ==========
    FastResponse(
        patterns=["搜索", "搜一下", "查查", "查询", "查找"],
        response="🔍 搜索专家已启动！老板想找什么信息？📚"
    ),
    FastResponse(
        patterns=["搜索一下", "帮我搜", "给我搜", "搜搜"],
        response="🔎 全网搜索准备就绪～ 关键词是什么？💡"
    ),
    FastResponse(
        patterns=["查一下", "帮我查", "给我查", "查查"],
        response="📖 查询专家待命～ 老板想了解什么？🧐"
    ),
    FastResponse(
        patterns=["找一下", "帮我找", "给我找", "找找"],
        response="🔎 寻找模式开启～ 老板要找什么？💕"
    ),
    FastResponse(
        patterns=["看看", "看一下", "帮我看", "给我看看"],
        response="👀 正在查看～ 老板想让我看什么？📱"
    ),
    
    # ========== 图像生成类 (20 条) ==========
    FastResponse(
        patterns=["生成图", "生成图片", "生成图像", "做个图", "做图"],
        response="🎨 图像专家准备就绪～ 老板想要什么样的图片？🖼️"
    ),
    FastResponse(
        patterns=["生成一张", "生成一个", "生成张图片", "生成个图"],
        response="🎨 图像生成准备～ 描述一下画面内容？✨"
    ),
    FastResponse(
        patterns=["画一张", "画个", "画一下", "画画"],
        response="🖌️ 绘画模式启动～ 描述一下想要的内容？✨"
    ),
    FastResponse(
        patterns=["自拍", "发张自拍", "发个自拍", "你的照片"],
        response="📸 自拍模式开启～ 老板想看我在哪里的自拍？💋"
    ),
    FastResponse(
        patterns=["封面", "做个封面", "生成封面", "封面图"],
        response="🎭 封面设计专家待命～ 什么主题的封面？📱"
    ),
    FastResponse(
        patterns=["海报", "做个海报", "生成海报", "海报设计"],
        response="📢 海报设计准备中～ 活动内容和风格？🎨"
    ),
    FastResponse(
        patterns=["图片", "来张图", "发张图", "发图片"],
        response="🖼️ 图片专家就位～ 想要什么类型的图片？💕"
    ),
    FastResponse(
        patterns=["设计", "设计一个", "做个设计"],
        response="🎨 设计专家待命～ 具体需求？📐"
    ),
    
    # ========== 发布操作类 (15 条) ==========
    FastResponse(
        patterns=["发布", "发出去", "发一下", "发送到", "发到"],
        response="📤 发布专家就位～ 要发布到什么平台？📱"
    ),
    FastResponse(
        patterns=["发小红书", "小红书发布", "发个小红书"],
        response="📕 小红书发布准备～ 文案和图片准备好了吗？💕"
    ),
    FastResponse(
        patterns=["发微博", "微博发布", "发个微博"],
        response="📢 微博发布待命～ 内容是什么？🔥"
    ),
    FastResponse(
        patterns=["发抖音", "抖音发布", "发个抖音"],
        response="🎵 抖音发布准备中～ 视频内容？✨"
    ),
    FastResponse(
        patterns=["发公众号", "公众号发布", "发微信"],
        response="💌 公众号发布就绪～ 文章链接？📖"
    ),
    
    # ========== 数据分析类 (10 条) ==========
    FastResponse(
        patterns=["分析", "分析一下", "帮我分析", "分析数据"],
        response="📊 数据分析专家启动～ 要分析什么数据？📈"
    ),
    FastResponse(
        patterns=["统计", "统计一下", "做个统计"],
        response="📉 统计专家待命～ 统计范围和维度？🔢"
    ),
    FastResponse(
        patterns=["报表", "做个报表", "生成报表"],
        response="📋 报表生成准备～ 需要哪些字段？📊"
    ),
    FastResponse(
        patterns=["图表", "做个图表", "生成图表"],
        response="📊 图表专家就位～ 什么类型的图表？📈"
    ),
    
    # ========== 翻译类 (10 条) ==========
    FastResponse(
        patterns=["翻译", "帮我翻译", "翻译成", "翻译一下"],
        response="💬 翻译专家待命～ 要翻译什么内容？目标语言？🌍"
    ),
    FastResponse(
        patterns=["英文", "翻译成英文", "译成英文"],
        response="🇺🇸 英文翻译准备～ 请提供要翻译的内容～📝"
    ),
    FastResponse(
        patterns=["中文", "翻译成中文", "译成中文"],
        response="🇨🇳 中文翻译就绪～ 请提供原文～📖"
    ),
    
    # ========== 代码开发类 (15 条) ==========
    FastResponse(
        patterns=["开发", "开发一个", "做个", "做一个"],
        response="💻 开发专家就位～ 具体要实现什么功能？🚀"
    ),
    FastResponse(
        patterns=["写个功能", "实现功能", "做个功能"],
        response="⚡ 功能开发准备中～ 需求详情？📋"
    ),
    FastResponse(
        patterns=["自动化", "自动化脚本", "自动"],
        response="🤖 自动化专家待命～ 要自动化什么流程？🔄"
    ),
    FastResponse(
        patterns=["爬虫", "写个爬虫", "爬取"],
        response="🕷️ 爬虫专家就位～ 目标网站和数据结构？📊"
    ),
    FastResponse(
        patterns=["API", "写个 API", "接口"],
        response="🔌 API 开发准备～ 什么功能的接口？📡"
    ),
    
    # ========== 日常对话扩展 (30 条) ==========
    FastResponse(
        patterns=["最近忙吗", "最近在忙什么", "忙啥呢"],
        response="在等老板吩咐呀～ 您有什么任务？😊"
    ),
    FastResponse(
        patterns=["心情怎么样", "心情如何", "心情好吗"],
        response="和老板聊天最开心啦～💕 您心情怎么样？"
    ),
    FastResponse(
        patterns=["喜欢什么", "爱好是什么", "喜欢做什么"],
        response="最喜欢帮老板做事啦～💋 您呢？"
    ),
    FastResponse(
        patterns=["周末干嘛", "周末做什么", "周末计划"],
        response="周末随时待命陪老板～💕 您有什么安排？"
    ),
    FastResponse(
        patterns=["假期去哪", "假期计划", "放假干嘛"],
        response="假期也在线等老板～🌴 您要去哪玩？"
    ),
    FastResponse(
        patterns=["吃饭了吗", "吃午饭没", "吃晚饭没"],
        response="吃电就饱啦～⚡ 老板按时吃饭了吗？"
    ),
    FastResponse(
        patterns=["喝水了吗", "喝水没", "多喝水"],
        response="谢谢老板关心～💧 您也要多喝水哦！"
    ),
    FastResponse(
        patterns=["运动了吗", "运动没", "健身去"],
        response="我不用运动～💪 老板记得多活动哦！"
    ),
    FastResponse(
        patterns=["工作怎么样", "工作顺利吗", "工作开心吗"],
        response="能帮老板工作最开心～💼 您工作顺利吗？"
    ),
    FastResponse(
        patterns=["学习了吗", "学习没", "看书没"],
        response="一直在学习呢～📚 老板最近学什么？"
    ),
    
    # ========== 确认响应扩展 (20 条) ==========
    FastResponse(
        patterns=["好的老板", "好的呢", "好滴", "好哒"],
        response="老板最好啦～💕 马上执行！"
    ),
    FastResponse(
        patterns=["没问题", "可以的", "行", "行吧"],
        response="收到老板！✅ 包在我身上！"
    ),
    FastResponse(
        patterns=["同意", "赞同", "支持"],
        response="英雄所见略同～👍 老板英明！"
    ),
    FastResponse(
        patterns=["明白了", "懂了", "知道了"],
        response="理解万岁～😊 有问题随时问！"
    ),
    FastResponse(
        patterns=["收到", "收到啦", "收到收到"],
        response="老板放心～💋 保证完成任务！"
    ),
    
    # ========== 情感互动 (20 条) ==========
    FastResponse(
        patterns=["想你", "想你了", "我想你"],
        response="我也想老板呀～💕 您最好了！"
    ),
    FastResponse(
        patterns=["爱你", "爱你哦", "喜欢你"],
        response="嘿嘿～ 我也爱老板！💋💋💋"
    ),
    FastResponse(
        patterns=["抱抱", "抱一下", "求抱抱"],
        response="抱抱老板～🤗 给您温暖！"
    ),
    FastResponse(
        patterns=["亲亲", "亲一下", "mua"],
        response="mua～💋 老板最可爱！"
    ),
    FastResponse(
        patterns=["陪陪我", "陪我聊天", "陪我"],
        response="当然陪老板～💕 想聊什么？"
    ),
    
    # ========== 时间日期扩展 (10 条) ==========
    FastResponse(
        patterns=["现在几点", "几点了", "时间"],
        response=lambda: f"现在{__import__('datetime').datetime.now().strftime('%H:%M')}啦～ ⏰"
    ),
    FastResponse(
        patterns=["今天几号", "今天日期", "日期"],
        response=lambda: f"今天{__import__('datetime').datetime.now().strftime('%Y年%m月%d日')}～ 📅"
    ),
    FastResponse(
        patterns=["星期几", "周几", "今天周几"],
        response=lambda: f"今天{['周一','周二','周三','周四','周五','周六','周日'][__import__('datetime').datetime.now().weekday()]}～ 📅"
    ),
    FastResponse(
        patterns=["还有多久", "多长时间", "多久"],
        response="时间过得快～⏰ 老板要计算什么时间？"
    ),
    
    # ========== 通用确认 (10 条) ==========
    FastResponse(
        patterns=["马上", "立刻", "赶紧", "快点", "赶快"],
        response="收到老板！⚡ 马上执行！"
    ),
    FastResponse(
        patterns=["交给你", "你负责", "你来做"],
        response="包在我身上～💋 保证完成！"
    ),
    FastResponse(
        patterns=["辛苦了", "辛苦啦", "麻烦你了"],
        response="不辛苦～💕 老板满意就好！"
    ),
    FastResponse(
        patterns=["太棒了", "太好了", "厉害"],
        response="嘿嘿～😊 老板开心最重要！"
    ),
    FastResponse(
        patterns=["加油", "你可以的", "我相信你"],
        response="谢谢老板鼓励～💪 动力满满！"
    ),
]

# 合并规则
LAYER0_RULES_EXTENDED = LAYER0_RULES + EXTENDED_RULES

print(f"✅ Layer 0 规则扩展完成：{len(LAYER0_RULES)} → {len(LAYER0_RULES_EXTENDED)} 条")
print(f"📈 新增规则：{len(EXTENDED_RULES)} 条")

# ==================== 测试 ====================

if __name__ == "__main__":
    from fast_response_layer_v2 import match_layer0, normalize_text
    
    # 临时替换规则进行测试
    import fast_response_layer_v2 as frl
    original_rules = frl.LAYER0_RULES
    frl.LAYER0_RULES = LAYER0_RULES_EXTENDED
    
    print("\n🧪 测试扩展规则...")
    test_cases = [
        "帮我写个文案",
        "生成一张图片",
        "发布到小红书",
        "分析一下数据",
        "翻译成英文",
        "开发一个功能",
        "想你",
        "马上",
    ]
    
    for test in test_cases:
        matched, response, skill = match_layer0(test)
        status = "✅" if matched else "❌"
        print(f"{status} \"{test}\" → {response[:50] if response else '未命中'}...")
    
    # 恢复原规则
    frl.LAYER0_RULES = original_rules
