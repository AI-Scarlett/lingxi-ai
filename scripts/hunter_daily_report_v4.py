#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hunter v4 - 每日商业机会侦察报告 (简化版)

每天早上 8 点自动执行，生成报告并保存，通过飞书机器人发送通知

用法:
python3 /root/.openclaw/skills/lingxi/scripts/hunter_daily_report_v4.py
"""

import os
import json
import urllib.request
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
"""

def send_feishu_message(webhook_url: str, title: str, content: str):
    """发送飞书机器人消息"""
    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [{"tag": "text", "text": content}]
                    ]
                }
            }
        }
    }
    
    data = json.dumps(message).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('StatusCode', 0) == 0
    except Exception as e:
        print(f"发送失败：{e}")
        return False

def main():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    print("=" * 60)
    print(f"🎯 Hunter v4 - 每日商业机会侦察报告")
    print(f"📅 日期：{today}")
    print("=" * 60)
    
    # 生成报告内容
    content = REPORT_CONTENT.format(date=today)
    
    # 保存本地备份
    report_dir = "/root/.openclaw/workspace/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = f"{report_dir}/hunter-{today}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 报告已保存：{report_path}")
    
    # 尝试发送飞书消息
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')
    if webhook_url:
        print(f"📤 发送飞书通知...")
        success = send_feishu_message(
            webhook_url,
            f"Hunter 报告 - {today}",
            f"✅ Hunter 报告已生成\n\n推荐：公众号内容矩阵管家 (¥199/mo)\n\n详情：{report_path}"
        )
        if success:
            print("✅ 飞书通知已发送")
        else:
            print("⚠️ 飞书通知发送失败")
    else:
        print("⚠️ 未配置 FEISHU_WEBHOOK_URL，跳过消息发送")
    
    print("=" * 60)
    print("✅ Hunter v4 报告生成完成！")

if __name__ == "__main__":
    main()
