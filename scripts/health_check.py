#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 健康检查脚本
定期检查 Dashboard 和系统状态，发送告警
"""

import requests
import time
import sys
from pathlib import Path
from datetime import datetime

# 配置
DASHBOARD_URL = "http://localhost:8765/api/health"
TIMEOUT = 5  # 超时时间（秒）
LOG_FILE = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "health_check.log"

# 告警配置（可选）
ENABLE_ALERT = False
ALERT_EMAIL = ""
ALERT_WEBHOOK = ""


def log_message(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    # 写入日志文件
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception as e:
        print(f"写入日志失败：{e}")


def check_dashboard_health() -> bool:
    """检查 Dashboard 健康状态"""
    try:
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            version = data.get("version", "unknown")
            
            if status == "healthy":
                log_message(f"✅ Dashboard 健康检查通过 (版本：{version})")
                return True
            else:
                log_message(f"⚠️  Dashboard 状态异常：{status}")
                send_alert(f"Dashboard 状态异常：{status}")
                return False
        else:
            log_message(f"❌ Dashboard HTTP 状态异常：{response.status_code}")
            send_alert(f"Dashboard HTTP 状态异常：{response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        log_message(f"❌ Dashboard 健康检查超时（{TIMEOUT}秒）")
        send_alert("Dashboard 健康检查超时")
        return False
    except requests.exceptions.ConnectionError:
        log_message("❌ Dashboard 无法连接")
        send_alert("Dashboard 无法连接")
        return False
    except Exception as e:
        log_message(f"❌ Dashboard 健康检查失败：{str(e)}")
        send_alert(f"Dashboard 健康检查失败：{str(e)}")
        return False


def check_process_status() -> bool:
    """检查 Dashboard 进程状态"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["pgrep", "-f", "python3.*backend/main.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            log_message(f"✅ Dashboard 进程运行中 (PID: {', '.join(pids)})")
            return True
        else:
            log_message("❌ Dashboard 进程未运行")
            send_alert("Dashboard 进程未运行")
            return False
    except Exception as e:
        log_message(f"❌ 检查进程状态失败：{e}")
        return False


def check_disk_space() -> bool:
    """检查磁盘空间"""
    import shutil
    
    try:
        workspace = Path.home() / ".openclaw" / "workspace"
        total, used, free = shutil.disk_usage(workspace)
        free_gb = free / (1024 ** 3)
        usage_percent = (used / total) * 100
        
        if usage_percent > 90:
            log_message(f"❌ 磁盘空间严重不足 (剩余：{free_gb:.2f}GB, 使用：{usage_percent:.1f}%)")
            send_alert(f"磁盘空间严重不足：{usage_percent:.1f}%")
            return False
        elif usage_percent > 80:
            log_message(f"⚠️  磁盘空间紧张 (剩余：{free_gb:.2f}GB, 使用：{usage_percent:.1f}%)")
            return True
        else:
            log_message(f"✅ 磁盘空间正常 (剩余：{free_gb:.2f}GB, 使用：{usage_percent:.1f}%)")
            return True
    except Exception as e:
        log_message(f"❌ 检查磁盘空间失败：{e}")
        return True  # 不阻止健康检查


def send_alert(message: str):
    """发送告警（邮件/短信/飞书）"""
    if not ENABLE_ALERT:
        return
    
    log_message(f"🚨 发送告警：{message}")
    
    # TODO: 实现邮件/短信/飞书告警
    # 示例：飞书 webhook
    if ALERT_WEBHOOK:
        try:
            requests.post(
                ALERT_WEBHOOK,
                json={
                    "msg_type": "text",
                    "content": {
                        "text": f"🚨 灵犀告警\n{message}"
                    }
                },
                timeout=5
            )
        except:
            pass


def run_health_check():
    """执行完整健康检查"""
    log_message("=" * 50)
    log_message("开始健康检查...")
    
    results = {
        "dashboard_http": check_dashboard_health(),
        "dashboard_process": check_process_status(),
        "disk_space": check_disk_space()
    }
    
    # 统计结果
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    log_message("=" * 50)
    log_message(f"健康检查完成：{passed}/{total} 通过")
    
    if passed == total:
        log_message("✅ 所有检查项通过")
        return 0
    else:
        log_message("❌ 部分检查项失败")
        return 1


if __name__ == "__main__":
    exit_code = run_health_check()
    sys.exit(exit_code)
