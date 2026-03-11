#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 远程访问快速启动

用法：
    python3 quick_start_remote.py

功能：
- 自动检测网络环境
- 推荐最佳外网访问方案
- 一键配置和启动
"""

import sys
import socket
import subprocess
from pathlib import Path

def check_network():
    """检测网络环境"""
    print("🔍 检测网络环境...")
    
    # 检测是否有公网 IP
    try:
        response = subprocess.run(
            ["curl", "-s", "https://api.ipify.org"],
            capture_output=True,
            text=True,
            timeout=5
        )
        public_ip = response.stdout.strip()
        print(f"✅ 公网 IP: {public_ip}")
        return True
    except:
        print("❌ 无法获取公网 IP（可能在 NAT 后）")
        return False

def check_domain():
    """检测域名配置"""
    print("\n🔍 检测域名配置...")
    
    # 检查是否有自有域名
    domain = input("请输入您的域名（可选，直接回车使用官方域名）: ").strip()
    
    if not domain:
        print("✅ 使用官方域名：lingxi.me-ai.help")
        return "lingxi.me-ai.help"
    else:
        print(f"✅ 使用自有域名：{domain}")
        return domain

def recommend_solution(has_public_ip: bool, domain: str):
    """推荐最佳方案"""
    print("\n💡 推荐方案：")
    
    if not domain or domain == "lingxi.me-ai.help":
        print("🌟 方案一：使用官方域名（推荐）")
        print("   - 零配置，开箱即用")
        print("   - 免费使用")
        print("   - 自动 HTTPS")
        print(f"   - 访问地址：https://lingxi.me-ai.help")
        return "official"
    
    elif has_public_ip:
        print("🌟 方案二：自有域名 + Nginx 反向代理（推荐）")
        print(f"   - 完全控制")
        print(f"   - 自定义域名：{domain}")
        print(f"   - 稳定可靠")
        print(f"   - 访问地址：https://{domain}")
        return "self_hosted"
    
    else:
        print("🌟 方案三：Cloudflare Tunnel（推荐）")
        print("   - 无需公网 IP")
        print("   - 免费使用")
        print("   - 自动 HTTPS")
        print(f"   - 访问地址：https://{domain}")
        return "cloudflare"

def setup_official():
    """配置官方域名方案"""
    print("\n🚀 启动官方域名方案...")
    
    from dashboard.remote_access import RemoteAccessServer
    
    server = RemoteAccessServer(public_host="lingxi.me-ai.help")
    
    print(f"\n✅ 启动成功！")
    print(f"🌐 公网访问：https://lingxi.me-ai.help")
    print(f"📱 移动端：https://lingxi.me-ai.help/mobile")
    print(f"🔐 监听端口：0.0.0.0:8766")
    
    return server

def setup_self_hosted(domain: str):
    """配置自有域名方案"""
    print(f"\n🚀 启动自有域名方案（{domain}）...")
    
    print("\n📋 配置步骤：")
    print(f"1. DNS 配置：添加 A 记录 {domain} → 你的服务器 IP")
    print(f"2. Nginx 配置：")
    print(f"""
server {{
    listen 80;
    server_name {domain};
    
    location / {{
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
""")
    print(f"3. HTTPS 配置：certbot --nginx -d {domain}")
    print(f"4. 启动服务：python3 remote_access.py --host {domain}")
    
    return None

def main():
    """主函数"""
    print("=" * 60)
    print("🌐 灵犀 Dashboard 远程访问快速启动")
    print("=" * 60)
    print()
    
    # 检测环境
    has_public_ip = check_network()
    domain = check_domain()
    
    # 推荐方案
    solution = recommend_solution(has_public_ip, domain)
    
    # 配置
    print()
    if solution == "official":
        server = setup_official()
    elif solution == "self_hosted":
        setup_self_hosted(domain)
    elif solution == "cloudflare":
        print("\n📖 请参考文档：EXTERNAL_ACCESS.md")
        print("   Cloudflare Tunnel 配置指南")
    
    print()
    print("=" * 60)
    print("💡 提示：")
    print("   - 使用官方域名：零配置，立即访问")
    print("   - 使用自有域名：完全控制，长期稳定")
    print("   - 使用 Cloudflare：无需公网 IP，免费")
    print("=" * 60)


if __name__ == "__main__":
    main()
