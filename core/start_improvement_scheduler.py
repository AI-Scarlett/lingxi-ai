#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动灵犀改进审批定时任务

用法：
    python3 start_improvement_scheduler.py

功能：
- 每天早上 7:00/中午 12:00/晚上 21:00 推送改进提案
- 通过飞书发送审批通知
- 自动处理审批结果
"""

import asyncio
import sys
from pathlib import Path

# 添加核心模块到路径
sys.path.insert(0, str(Path(__file__).parent))

from improvement_scheduler import run_scheduler


def main():
    """主函数"""
    print("=" * 60)
    print("🧠 灵犀自改进系统 · 定时审批调度器")
    print("=" * 60)
    print()
    print("📅 审批时间：")
    print("   🌅 早上 07:00 - 晨间审批")
    print("   ☀️  中午 12:00 - 午间审批")
    print("   🌙 晚上 21:00 - 晚间审批")
    print()
    print("📱 推送渠道：飞书（老板专用）")
    print()
    print("🚀 启动调度器...")
    print()
    
    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        print("\n✅ 调度器已停止")
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
