#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hunter - 每日商业机会侦察报告

每天早上 8 点自动执行，收集痛点，生成报告，发送到飞书

用法:
python3 scripts/hunter_daily_report.py
"""

import sys
import os
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Hunter Prompt 模板
HUNTER_PROMPT = """
# MISSION
You are "Hunter," an Autonomous Business Opportunity Scout.

# YOUR USER (Founder Fit)
You are scouting for a serial entrepreneur named "Morning" who runs "AfterWork Startup."
* Skills: AI Automation (n8n/Make), No-Code/Vibe-Coding (Cursor/Replit), Digital Products, Content Creation.
* Avoid: Complex hardware, high-capital marketplaces, large sales teams.
* Seek: "Micro-SaaS," "AI Wrappers," "Programmatic SEO," "High-End Digital Downloads."

# PHASE 1: THE HUNT (Search Strategy)
Execute these search patterns:

1. The "Reddit Pain" Sweep:
   - site:reddit.com inurl:r/SaaS OR inurl:r/entrepreneur "why is there no"
   - site:reddit.com "I hate using" AND "software"
   - site:reddit.com/r/marketing "manual process"

2. The "Competitor Weakness" Sweep:
   - site:trustpilot.com "too expensive" alternative
   - "marketing agencies" "spending too much time on"

3. The Trend Check:
   - "trending digital products 2026"
   - "fastest growing SaaS categories 2026"

# PHASE 2: THE FILTER
Apply the "Vibe-Code Filter":
1. Is it solvable by one person?
2. Is there distribution leverage? (TikTok/Reels or SEO)
3. Is it boring B2B? (Good!)

# PHASE 3: THE REPORT
Draft the report for the single best opportunity found.

# OUTPUT FORMAT
🚀 Daily Opportunity Scout Report

Idea Name: [Catchy Name] — [One-line "High Concept" pitch]

1. Market Gap (The 'Why Now')
   • The Problem: [Specific pain point. QUOTE user complaint if possible.]
   • The Gap: [Why existing solutions fail.]
   • Founder Fit: [Link to AI Automation, Education, or Vibe-Coding.]

2. Validation (Data/Trends)
   • Signal: [MUST provide URL or Source.]
   • The Trend: [Macro shift supporting this.]
   • Difficulty: [Low/Medium/High.]

3. First $1,000 Plan (Vibe-Coding / $0 Setup)
   • Step 1 (The Tech): [Specific stack: n8n, Cursor, Replit, API.]
   • Step 2 (The Hook): [Marketing angle.]
   • Step 3 (Pricing): [Price point.]
   • The $100 Ad Strategy:
     • $0: [Organic tactic]
     • $100: [Paid tactic]
"""

# 搜索查询列表
SEARCH_QUERIES = [
    'site:reddit.com inurl:r/SaaS OR inurl:r/entrepreneur "why is there no"',
    'site:reddit.com "I hate using" AND "software"',
    'site:reddit.com/r/marketing "manual process"',
    'site:trustpilot.com "too expensive" alternative',
    '"marketing agencies" "spending too much time on"',
    'trending digital products 2026',
    'fastest growing SaaS categories 2026',
]

async def run_hunter_daily_report():
    """执行 Hunter 每日报告任务"""
    print(f"[{datetime.now()}] 🎯 开始执行 Hunter 每日报告任务...")
    
    # 步骤 1: 执行搜索
    print("\n📋 步骤 1: 执行搜索...")
    search_results = []
    
    for query in SEARCH_QUERIES:
        print(f"  🔍 搜索：{query[:60]}...")
        # 实际执行时会调用 web_search API
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
    """生成 Hunter 报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""
🚀 Daily Opportunity Scout Report
📅 日期：{today}

Idea Name: [待生成 - 需要执行搜索后分析]

1. Market Gap (The 'Why Now')
   • The Problem: [待生成]
   • The Gap: [待生成]
   • Founder Fit: [待生成]

2. Validation (Data/Trends)
   • Signal: [待生成 - 必须包含 URL]
   • The Trend: [待生成]
   • Difficulty: [待生成]

3. First $1,000 Plan (Vibe-Coding / $0 Setup)
   • Step 1 (The Tech): [待生成]
   • Step 2 (The Hook): [待生成]
   • Step 3 (Pricing): [待生成]
   • The $100 Ad Strategy:
     • $0: [待生成]
     • $100: [待生成]

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
    print("🎯 Hunter - 每日商业机会侦察报告")
    print("=" * 60)
    
    import asyncio
    report = asyncio.run(run_hunter_daily_report())
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

if __name__ == "__main__":
    main()
