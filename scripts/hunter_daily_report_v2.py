#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hunter - 每日商业机会侦察报告 (国内 + 国外双区域版)

每天早上 8 点自动执行，分别搜索国内和国外市场痛点，生成双区域报告，发送到飞书

用法:
python3 scripts/hunter_daily_report_v2.py
"""

import sys
import os
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ========== 国外市场搜索查询 ==========
OVERSEAS_SEARCH_QUERIES = [
    # Reddit 痛点搜索
    'site:reddit.com r/SaaS OR r/entrepreneur "为什么没有" software',
    'site:reddit.com "I hate using" AND "software" manual',
    'site:reddit.com/r/marketing "manual process" automation',
    'site:reddit.com/r/entrepreneur "too expensive" alternative',
    'site:reddit.com/r/SaaS "willing to pay" solve',
    'site:reddit.com/r/smallbusiness "waste time" repetitive task',
    
    # 竞争对手弱点搜索
    'site:trustpilot.com "too expensive" alternative software',
    'site:trustpilot.com "too complicated" "easy alternative"',
    '"marketing agencies" "spending too much time on" repetitive',
    
    # 趋势搜索
    'trending digital products 2026 passive income',
    'fastest growing SaaS categories 2026',
    'AI automation tools trending 2026',
    'no-code business ideas 2026',
]

# ========== 国内市场搜索查询 ==========
DOMESTIC_SEARCH_QUERIES = [
    # 知乎痛点搜索
    'site:zhihu.com "为什么没有" 软件 工具',
    'site:zhihu.com "太难用了" 替代方案',
    'site:zhihu.com "手动操作" 自动化',
    'site:zhihu.com/r/创业 "痛点" "愿意付费"',
    
    # 产品评论搜索
    'site:zhihu.com "太贵了" 平替 替代',
    'site:zhihu.com "功能太复杂" 简单 工具',
    'site:douban.com group "软件" "难用"',
    
    # 趋势搜索
    '2026 年 热门 数字产品 副业',
    '2026 年 SaaS 创业 机会',
    'AI 自动化 工具 2026 趋势',
    '无代码 低代码 创业 2026',
    
    # 公众号/小红书
    '公众号 知识付费 痛点 2026',
    '小红书 数字产品 虚拟产品 2026',
]

# ========== Hunter Prompt 模板 (双区域版) ==========
HUNTER_PROMPT_OVERSEAS = """
# 任务
你是 "Hunter"，一个 autonomous 商业机会侦察兵。

# 你的用户 (创始人匹配)
你正在为一位名叫 "Morning" 的连续创业者侦察**海外市场**机会。
* 技能：AI 自动化 (n8n/Make)、无代码/Vibe-Coding (Cursor/Replit)、数字产品、内容创作
* 避免：复杂硬件、高资金市场、需要大销售团队的项目
* 寻找："Micro-SaaS"、"AI 包装器"、"程序化 SEO"、"高端数字下载产品"

# 搜索策略
使用 multi-search-engine 搜索最近 24-48 小时的讨论，找到用户抱怨。

# 筛选标准
应用 "Vibe-Code 过滤器":
1. 一个人能解决吗？(是，继续)
2. 有分发优势吗？(TikTok/Reels 或 SEO，是，继续)
3. 是无聊的 B2B 吗？(好！我们喜欢赚钱的无聊生意)

# 输出格式
🚀 海外市场机会

项目名称：[吸引人的名字] — [一句话介绍]

1. 市场机会
   • 痛点：[具体痛点。尽可能引用用户原话。]
   • 市场空白：[现有解决方案为何失败。]
   • 创始人匹配：[明确关联到 AI 自动化、教育或 Vibe-Coding。]

2. 验证
   • 信号：[必须提供 URL 或来源。]
   • 趋势：[宏观趋势。]
   • 难度：[低/中/高]

3. 第一个 1000 美元计划
   • 技术栈：[n8n、Cursor、Replit、API]
   • 营销钩子：[营销角度]
   • 定价：[价格点，美元]
   • 100 美元广告策略:
     • 0 美元：[有机营销]
     • 100 美元：[付费广告]
"""

HUNTER_PROMPT_DOMESTIC = """
# 任务
你是 "Hunter"，一个 autonomous 商业机会侦察兵。

# 你的用户 (创始人匹配)
你正在为一位名叫 "Morning" 的连续创业者侦察**国内市场**机会。
* 技能：AI 自动化 (n8n/Make)、无代码/Vibe-Coding (Cursor/Replit)、数字产品、内容创作
* 避免：复杂硬件、高资金市场、需要大销售团队的项目
* 寻找："Micro-SaaS"、"AI 工具"、"知识付费"、"虚拟产品"

# 搜索策略
使用 multi-search-engine 搜索最近 24-48 小时的讨论，找到用户抱怨。

# 筛选标准
应用 "Vibe-Code 过滤器":
1. 一个人能解决吗？(是，继续)
2. 有分发优势吗？(抖音/小红书/公众号，是，继续)
3. 是无聊的 B2B 吗？(好！我们喜欢赚钱的无聊生意)

# 输出格式
🚀 国内市场机会

项目名称：[吸引人的名字] — [一句话介绍]

1. 市场机会
   • 痛点：[具体痛点。尽可能引用用户原话。]
   • 市场空白：[现有解决方案为何失败。]
   • 创始人匹配：[明确关联到 AI 自动化、教育或 Vibe-Coding。]

2. 验证
   • 信号：[必须提供 URL 或来源。]
   • 趋势：[宏观趋势。]
   • 难度：[低/中/高]

3. 第一个 10000 元计划
   • 技术栈：[n8n、Cursor、Replit、API、微信生态]
   • 营销钩子：[营销角度]
   • 定价：[价格点，人民币]
   • 1000 元推广策略:
     • 0 元：[有机营销：抖音/小红书/公众号]
     • 1000 元：[付费广告：抖音 DOU+/小红书信息流]
"""

async def run_hunter_daily_report_v2():
    """执行 Hunter 每日报告任务 (双区域版)"""
    print(f"[{datetime.now()}] 🎯 开始执行 Hunter 每日报告任务 (国内 + 国外)...")
    
    # ========== 第一部分：国外市场 ==========
    print("\n" + "=" * 60)
    print("🌍 第一部分：搜索海外市场...")
    print("=" * 60)
    
    overseas_results = []
    for query in OVERSEAS_SEARCH_QUERIES:
        print(f"  🔍 搜索：{query[:60]}...")
        # 实际执行时会调用 multi-search-engine
    
    # ========== 第二部分：国内市场 ==========
    print("\n" + "=" * 60)
    print("🇨🇳 第二部分：搜索国内市场...")
    print("=" * 60)
    
    domestic_results = []
    for query in DOMESTIC_SEARCH_QUERIES:
        print(f"  🔍 搜索：{query[:60]}...")
        # 实际执行时会调用 multi-search-engine
    
    # ========== 第三部分：生成双区域报告 ==========
    print("\n" + "=" * 60)
    print("📝 第三部分：生成双区域报告...")
    print("=" * 60)
    
    report = generate_dual_region_report()
    
    # ========== 第四部分：发送到飞书 ==========
    print("\n" + "=" * 60)
    print("📤 第四部分：发送到飞书...")
    print("=" * 60)
    
    await send_to_feishu(report)
    
    print(f"\n[{datetime.now()}] ✅ Hunter 双区域报告发送完成！")
    return report

def generate_dual_region_report():
    """生成双区域 Hunter 报告 (中文模板)"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 每日商业机会侦察报告
📅 日期：{today}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

本报告分为两部分：
🌍 海外市场机会 (Reddit/Trustpilot/Google Trends)
🇨🇳 国内市场机会 (知乎/豆瓣/抖音/小红书)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 第一部分：海外市场机会
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

项目名称：[待生成 - 需要执行搜索后分析]

1. 市场机会
   • 痛点：[待生成]
   • 市场空白：[待生成]
   • 创始人匹配：[待生成]

2. 验证
   • 信号：[待生成 - 必须包含 URL]
   • 趋势：[待生成]
   • 难度：[待生成]

3. 第一个 1000 美元计划
   • 技术栈：[待生成]
   • 营销钩子：[待生成]
   • 定价：[待生成 - 美元]
   • 100 美元广告策略:
     • 0 美元：[待生成]
     • 100 美元：[待生成]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇨🇳 第二部分：国内市场机会
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

项目名称：[待生成 - 需要执行搜索后分析]

1. 市场机会
   • 痛点：[待生成]
   • 市场空白：[待生成]
   • 创始人匹配：[待生成]

2. 验证
   • 信号：[待生成 - 必须包含 URL]
   • 趋势：[待生成]
   • 难度：[待生成]

3. 第一个 10000 元计划
   • 技术栈：[待生成]
   • 营销钩子：[待生成]
   • 定价：[待生成 - 人民币]
   • 1000 元推广策略:
     • 0 元：[待生成 - 抖音/小红书/公众号]
     • 1000 元：[待生成 - 抖音 DOU+/小红书信息流]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 总结与建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 海外优势：[待生成]
• 国内优势：[待生成]
• 推荐优先级：[待生成]

---
💡 提示：这是模板，实际执行时会填充真实搜索结果和分析。
"""
    return report

async def send_to_feishu(report: str):
    """发送报告到飞书"""
    # 实际执行时会调用 message 工具
    print(f"  📤 发送报告到飞书...")
    print(f"  👤 接收人：ou_4192609eb71f18ae82f9163f02bef144")
    print(f"  📝 报告长度：{len(report)} 字符")

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 Hunter - 每日商业机会侦察报告 (国内 + 国外双区域)")
    print("=" * 60)
    
    import asyncio
    report = asyncio.run(run_hunter_daily_report_v2())
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

if __name__ == "__main__":
    main()
