#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀改进审批定时任务
周期：每天 7:00/12:00/21:00 运行
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加核心模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from improvement_scheduler import ImprovementScheduler


async def main():
    """主函数"""
    workspace = str(Path.home() / ".openclaw" / "workspace")
    scheduler = ImprovementScheduler(workspace)
    
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 运行改进审批任务")
    
    # 发送审批通知
    await scheduler.send_approval_notification()
    
    # 清理旧提案（每月 1 号执行）
    if datetime.now().day == 1:
        scheduler.cleanup_old_proposals(days=30)
    
    print("✅ 改进审批任务完成")


if __name__ == "__main__":
    asyncio.run(main())
