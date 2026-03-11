#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 灵犀 v3.3.3 快速启动脚本

专为养龙虾新手小白设计！
只需一个命令：python3 quick_start.py
"""

import os
import sys
import time
from pathlib import Path

# 颜色
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*60)
    print("🦞 灵犀 v3.3.3 - 养龙虾的最佳助手")
    print("="*60)
    print("\n✨ 专为新手小白设计，一键启动！\n")


def check_env():
    """检查环境变量"""
    print("📋 检查配置...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print(f"{YELLOW}⚠️  未找到 .env 文件{NC}")
        print("正在创建模板...")
        
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print(f"{GREEN}✅ 已创建 .env 文件{NC}")
            print(f"\n{YELLOW}请编辑 .env 文件，填写你的 API 密钥：{NC}")
            print("  nano .env")
            print("\n必须配置：")
            print("  - DASHSCOPE_API_KEY（图像生成）")
            print("  - QWEN_API_KEY（LLM 调用）")
            
            input("\n按回车键继续...")
        else:
            print(f"{RED}❌ 错误：未找到 .env.example{NC}")
            sys.exit(1)
    
    print(f"{GREEN}✅ 配置检查完成{NC}\n")


def start_dashboard():
    """启动 Dashboard"""
    print("🚀 启动 Dashboard...")
    
    # 导入并启动
    import subprocess
    import socket
    
    # 获取本机 IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # 尝试获取公网 IP
    try:
        import urllib.request
        public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode()
    except:
        public_ip = local_ip
    
    # 启动服务
    server_file = Path("dashboard/server.py")
    if not server_file.exists():
        print(f"{RED}❌ 错误：未找到 dashboard/server.py{NC}")
        sys.exit(1)
    
    proc = subprocess.Popen([sys.executable, str(server_file)])
    
    # 等待启动
    time.sleep(3)
    
    # 生成访问令牌
    token_file = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
    if token_file.exists():
        token = token_file.read_text().strip()
    else:
        token = f"lingxi_{int(time.time())}"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(token)
    
    # 打印访问信息
    print("\n" + "="*60)
    print(f"{GREEN}✅ Dashboard 已启动！{NC}")
    print("="*60)
    
    print("\n📊 访问方式：\n")
    
    print("   1️⃣  本地访问：")
    print(f"   http://localhost:8765/?token={token}\n")
    
    print("   2️⃣  局域网访问：")
    print(f"   http://{local_ip}:8765/?token={token}\n")
    
    if public_ip != local_ip:
        print("   3️⃣  公网访问：")
        print(f"   http://{public_ip}:8765/?token={token}\n")
    
    print("   📱 手机访问：")
    print(f"   使用浏览器扫描上方二维码，或访问：")
    print(f"   http://{local_ip}:8765/?token={token}\n")
    
    print("="*60)
    print("\n💡 提示：")
    print("   - 按 Ctrl+C 停止 Dashboard")
    print(f"   - 访问令牌已保存到：{token_file}")
    print("   - 文档：docs/ 目录")
    print("\n🦞 祝你养龙虾愉快！✨\n")
    print("="*60 + "\n")
    
    # 保持运行
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n👋 正在停止 Dashboard...")
        proc.terminate()
        print("✅ 已停止")


def main():
    """主函数"""
    print_banner()
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)
    
    # 检查配置
    check_env()
    
    # 启动 Dashboard
    start_dashboard()


if __name__ == "__main__":
    main()
