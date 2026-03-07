#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hunter v4 - 每日商业机会侦察报告 (飞书文档版)

每天早上 8 点自动执行，通过 OpenClaw 工具创建飞书文档

用法:
python3 /root/.openclaw/skills/lingxi/scripts/hunter_daily_report_v3.py
"""

import sys
import os
import json
from datetime import datetime

REPORT_CONTENT = """# 🚀 Hunter 每日商机报告 - {date}

**日期**: {date}

## 海外市场机会

### ContentRepurpose Pro

一句话：把 1 篇博客自动变成 30 天社交媒体内容

痛点：创作者没时间把文章变成多平台内容

定价：$19/mo 或 $97 终身

### MeetingAction AI

一句话：自动把 Zoom 会议变成待办事项

定价：$29/mo/团队

## 国内市场机会

### 公众号内容矩阵管家 (推荐)

一句话：管理 10 个公众号，1 个后台就够了

痛点：多账号登录麻烦，数据统计分散

定价：¥199/mo 或 ¥1999/年

### 小红书爆款生成器

一句话：输入产品链接，自动生成爆款笔记

定价：¥99/mo

## 总结

推荐启动：公众号内容矩阵管家

下一步：
- 本周访谈 5 个多账号运营者
- 下周末完成 MVP
- 第 3 周试用
- 第 4 周收费

---

生成时间：{time}
"""

def main():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    print("=" * 60)
    print(f"🎯 Hunter v4 - 每日商业机会侦察报告 (飞书文档版)")
    print(f"📅 日期：{today}")
    print("=" * 60)
    
    # 生成报告内容
    content = REPORT_CONTENT.format(date=today, time=time_str)
    
    # 保存本地备份
    report_path = f"/root/.openclaw/workspace/reports/hunter-{today}.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 本地备份：{report_path}")
    
    # 输出工具调用指令 (供 OpenClaw 解析)
    print(f"\n[TOOL_CALLS_START]")
    
    # 1. 创建文档
    create_doc = {
        "tool": "feishu_doc",
        "action": "create",
        "params": {
            "title": f"🚀 Hunter 每日商机报告 - {today}"
        }
    }
    print(f"CREATE_DOC:{json.dumps(create_doc)}")
    
    # 2. 写入内容 (需要等创建成功后，使用返回的 doc_token)
    # 这个由主会话处理
    
    # 3. 发送消息
    message = {
        "tool": "message",
        "action": "send",
        "params": {
            "target": "user:ou_4192609eb71f18ae82f9163f02bef144",
            "message": f"✅ Hunter 报告已生成\n📄 https://feishu.cn/docx/{{doc_id}}\n📌 推荐：公众号内容矩阵管家 (¥199/mo)"
        }
    }
    print(f"SEND_MESSAGE:{json.dumps(message)}")
    
    print(f"[TOOL_CALLS_END]")
    
    print(f"\n" + "=" * 60)
    print("✅ Hunter v4 报告内容生成完成！")
    print("⚠️ 需要 OpenClaw 工具支持创建飞书文档")
    print("=" * 60)

if __name__ == "__main__":
    main()
