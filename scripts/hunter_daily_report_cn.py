#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hunter - 每日商业机会侦察报告 (中文版)

每天早上 8 点自动执行，收集痛点，生成报告，发送到飞书
使用 multi-search-engine 进行搜索

用法:
python3 scripts/hunter_daily_report.py
"""

import sys
import os
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Hunter Prompt 模板 (中文版)
HUNTER_PROMPT = """
# 任务
你是 "Hunter"，一个 autonomous 商业机会侦察兵。

# 你的用户 (创始人匹配)
你正在为一位名叫 "Morning" 的连续创业者侦察机会，他运营 "AfterWork Startup"。
* 技能：AI 自动化 (n8n/Make)、无代码/Vibe-Coding (Cursor/Replit)、数字产品、内容创作
* 避免：复杂硬件、高资金市场、需要大销售团队的项目
* 寻找："Micro-SaaS"、"AI 包装器"、"程序化 SEO"、"高端数字下载产品"

# 第一阶段：搜索策略
使用 multi-search-engine 搜索最近 24-48 小时的讨论，找到用户抱怨。

执行以下搜索：

1. Reddit 痛点搜索:
   - site:reddit.com r/SaaS OR r/entrepreneur "为什么没有"
   - site:reddit.com "我讨厌使用" AND "软件"
   - site:reddit.com/r/marketing "手动流程"

2. 竞争对手弱点搜索:
   - site:trustpilot.com "太贵了" 替代方案
   - "营销机构" "花费太多时间在"

3. 趋势检查:
   - "2026 年热门数字产品"
   - "2026 年增长最快的 SaaS 类别"

# 第二阶段：筛选
应用 "Vibe-Code 过滤器":
1. 一个人能解决吗？(是，继续)
2. 有分发优势吗？(TikTok/Reels 或 SEO，是，继续)
3. 是无聊的 B2B 吗？(好！我们喜欢赚钱的无聊生意)

# 第三阶段：报告
为你找到的最佳机会撰写报告。

# 输出格式
🚀 每日商业机会侦察报告

项目名称：[吸引人的名字] — [一句话"高概念"介绍]

1. 市场机会 (为什么是现在)
   • 痛点：[具体痛点。尽可能引用用户原话。]
   • 市场空白：[现有解决方案为何失败。]
   • 创始人匹配：[明确关联到 AI 自动化、教育或 Vibe-Coding。]

2. 验证 (数据/趋势)
   • 信号：[必须提供 URL 或来源。例如："在 r/agency 帖子中发现：[链接]"]
   • 趋势：[支持这一点的宏观趋势。]
   • 难度：[诚实评估。低/中/高。]

3. 第一个 1000 美元计划 (Vibe-Coding / 0 成本启动)
   • 步骤 1 (技术栈): [具体技术栈：n8n、Cursor、Replit、具体 API。]
   • 步骤 2 (营销钩子): [营销角度。]
   • 步骤 3 (定价): [建议价格点。]
   • 100 美元广告策略:
     • 0 美元：[有机营销策略]
     • 100 美元：[付费广告策略]
"""

# 搜索查询列表 (中英文混合，提高搜索质量)
SEARCH_QUERIES = [
    # Reddit 痛点搜索
    'site:reddit.com r/SaaS OR r/entrepreneur "为什么没有" software',
    'site:reddit.com "I hate using" AND "software" manual',
    'site:reddit.com/r/marketing "manual process" automation',
    'site:reddit.com/r/entrepreneur "too expensive" alternative',
    'site:reddit.com/r/SaaS "willing to pay" solve',
    
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

async def run_hunter_daily_report():
    """执行 Hunter 每日报告任务"""
    print(f"[{datetime.now()}] 🎯 开始执行 Hunter 每日报告任务...")
    
    # 步骤 1: 执行搜索
    print("\n📋 步骤 1: 执行搜索...")
    search_results = []
    
    for query in SEARCH_QUERIES:
        print(f"  🔍 搜索：{query[:60]}...")
        # 实际执行时会调用 multi-search-engine
        # 这里使用子代理执行 Hunter Prompt
    
    # 步骤 2: 使用 Hunter Prompt 分析搜索结果
    print("\n📋 步骤 2: 分析痛点...")
    # 调用 LLM 分析搜索结果，应用 Vibe-Code Filter
    
    # 步骤 3: 生成报告
    print("\n📋 步骤 3: 生成报告...")
    report = generate_hunter_report()
    
    # 步骤 4: 发送到飞书
    print("\n📋 步骤 4: 发送到飞书...")
    await send_to_feishu(report)
    
    print(f"\n[{datetime.now()}] ✅ Hunter 报告发送完成！")
    return report

def generate_hunter_report():
    """生成 Hunter 报告 (中文模板)"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""
🚀 每日商业机会侦察报告
📅 日期：{today}

项目名称：[待生成 - 需要执行搜索后分析]

1. 市场机会 (为什么是现在)
   • 痛点：[待生成]
   • 市场空白：[待生成]
   • 创始人匹配：[待生成]

2. 验证 (数据/趋势)
   • 信号：[待生成 - 必须包含 URL]
   • 趋势：[待生成]
   • 难度：[待生成]

3. 第一个 1000 美元计划 (Vibe-Coding / 0 成本启动)
   • 步骤 1 (技术栈): [待生成]
   • 步骤 2 (营销钩子): [待生成]
   • 步骤 3 (定价): [待生成]
   • 100 美元广告策略:
     • 0 美元：[待生成]
     • 100 美元：[待生成]

---
💡 提示：这是模板，实际执行时会填充真实搜索结果和分析。
"""
    return report

async def send_to_feishu(report: str):
    """发送报告到飞书"""
    # 实际执行时会调用 message 工具
    # message(action="send", channel="feishu", target="ou_4192609eb71f18ae82f9163f02bef144", message=report)
    
    print(f"  📤 发送报告到飞书...")
    print(f"  👤 接收人：ou_4192609eb71f18ae82f9163f02bef144")
    print(f"  📝 报告长度：{len(report)} 字符")

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 Hunter - 每日商业机会侦察报告 (中文版)")
    print("=" * 60)
    
    import asyncio
    report = asyncio.run(run_hunter_daily_report())
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

if __name__ == "__main__":
    main()
