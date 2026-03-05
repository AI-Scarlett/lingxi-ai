#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 定时性能汇报

用法:
python3 scripts/daily_report_cron.py --daily  # 日报
python3 scripts/daily_report_cron.py --weekly # 周报
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.performance_monitor import generate_daily_report, generate_weekly_report

def main():
    if len(sys.argv) < 2:
        print("用法：python3 daily_report_cron.py [--daily|--weekly]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "--daily":
        print("📊 生成日报...")
        report = generate_daily_report()
    elif mode == "--weekly":
        print("📊 生成周报...")
        report = generate_weekly_report()
    else:
        print("未知模式，使用 --daily 或 --weekly")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

if __name__ == "__main__":
    main()
