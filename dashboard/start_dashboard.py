#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 一键启动脚本

小白用户专用：
- 一键启动
- 自动显示内网/外网访问地址
- 自动生成 token
- 显示二维码
- 零配置
"""

import sys
import subprocess
import time
from pathlib import Path


def print_banner():
    """打印欢迎横幅"""
    print("""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║          🚀 灵犀 Dashboard 一键启动                   ║
║                                                      ║
║         版本：v3.3.3  |  完全体                       ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
""")


def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    try:
        import aiohttp
        print("✅ aiohttp 已安装")
    except ImportError:
        print("❌ aiohttp 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "-q"])
        print("✅ aiohttp 安装完成")
    
    print()


def start_dashboard():
    """启动 Dashboard"""
    print("🚀 启动 Dashboard 服务...")
    print()
    
    # 首次启动欢迎消息
    from first_start_welcome import show_welcome
    show_welcome()
    
    # 启动远程访问服务器
    from remote_access import RemoteAccessServer
    import asyncio
    
    server = RemoteAccessServer()
    
    # 异步启动
    async def run():
        await server.start(port=8766)
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(60)
                stats = server.get_stats()
                print(f"\r📊 运行中... 请求：{stats['total_requests']}  已认证：{stats['authenticated_requests']}", end="", flush=True)
        except KeyboardInterrupt:
            print("\n\n✅ Dashboard 已停止")
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n✅ Dashboard 已停止")


def show_access_info():
    """显示访问信息"""
    from quick_access import QuickAccessGenerator
    
    generator = QuickAccessGenerator()
    
    print()
    print("=" * 70)
    print("🎉 Dashboard 启动成功！")
    print("=" * 70)
    print()
    
    # 内网访问
    inner_url = generator.get_inner_url()
    print(f"📡 内网访问（同一 WiFi）:")
    print(f"   💻 电脑：{inner_url}")
    print(f"   📱 手机：{inner_url}/mobile")
    print()
    
    # 外网访问（公网 IP+token）
    token = generator.generate_access_token()
    outer_url = generator.get_outer_url(token)
    mobile_url = generator.get_mobile_url(token)
    
    print(f"🌐 外网访问（任何地方）:")
    print(f"   💻 电脑：{outer_url}")
    print(f"   📱 手机：{mobile_url}")
    print()
    
    # Token 信息
    print(f"🔑 访问 Token:")
    print(f"   {token}")
    print(f"   有效期：30 天")
    print()
    
    # 公网 IP 信息
    public_ip = generator.get_public_ip()
    print(f"🌍 你的公网 IP: {public_ip}")
    print(f"   外网访问：http://{public_ip}:8766?token=xxx")
    print()
    
    # 二维码
    print(generator.generate_qr_code(mobile_url))
    
    # 使用说明
    print("💡 使用说明:")
    print()
    print("   【内网访问 - 最快】")
    print("   1. 手机连接同一 WiFi")
    print("   2. 打开手机浏览器")
    print(f"   3. 访问：{inner_url}/mobile")
    print()
    print("   【外网访问 - 任何地方】")
    print("   1. 打开手机浏览器（4G/5G 或其他 WiFi）")
    print(f"   2. 访问：http://{public_ip}:8766/mobile?token=xxx")
    print("   3. 或扫描下方二维码")
    print()
    print("   ⚠️ 外网访问需要配置端口映射")
    print("   查看教程：dashboard/NAT_PORT_FORWARDING.md")
    print()
    print("   【Token 管理】")
    print("   查看：python3 quick_access.py --list-tokens")
    print("   生成：python3 quick_access.py --generate-token")
    print("   撤销：python3 quick_access.py --revoke <token>")
    print()
    print("=" * 70)
    print()
    print("✅ Dashboard 正在运行，按 Ctrl+C 停止")
    print()


def main():
    """主函数"""
    print_banner()
    check_dependencies()
    start_dashboard()


if __name__ == "__main__":
    main()
