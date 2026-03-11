#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 快速访问工具

功能：
- 自动检测网络环境
- 一键生成内网访问地址（IP+ 端口）
- 一键生成外网访问地址（官方域名+token）
- 零配置，小白用户友好
- 显示二维码，手机扫码访问
"""

import socket
import secrets
import time
import json
from pathlib import Path
from datetime import datetime, timedelta


class QuickAccessGenerator:
    """快速访问地址生成器"""
    
    def __init__(self, local_port: int = 8765):
        self.local_port = local_port
        self.token_file = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "access_tokens.json"
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有 tokens
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> dict:
        """加载现有 tokens"""
        if self.token_file.exists():
            try:
                return json.loads(self.token_file.read_text())
            except:
                return {}
        return {}
    
    def _save_tokens(self):
        """保存 tokens"""
        self.token_file.write_text(json.dumps(self.tokens, indent=2))
    
    def get_local_ip(self) -> str:
        """获取本机内网 IP"""
        try:
            # 创建一个临时 socket 来获取本机 IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def generate_access_token(self, user_id: str = None, expires_days: int = 30) -> str:
        """
        生成访问 token
        
        Args:
            user_id: 用户 ID（可选）
            expires_days: 有效期（天）
        
        Returns:
            token 字符串
        """
        token = secrets.token_urlsafe(32)
        
        self.tokens[token] = {
            "user_id": user_id or f"user_{int(time.time())}",
            "created_at": time.time(),
            "expires_at": time.time() + (expires_days * 86400),
            "access_count": 0,
            "last_accessed": None
        }
        
        self._save_tokens()
        
        return token
    
    def get_inner_url(self) -> str:
        """
        获取内网访问地址
        
        Returns:
            内网访问 URL
        """
        local_ip = self.get_local_ip()
        return f"http://{local_ip}:{self.local_port}"
    
    def get_public_ip(self) -> str:
        """获取公网 IP"""
        try:
            import urllib.request
            response = urllib.request.urlopen("https://api.ipify.org", timeout=5)
            return response.read().decode().strip()
        except:
            # 备用方案
            try:
                response = urllib.request.urlopen("https://ifconfig.me", timeout=5)
                return response.read().decode().strip()
            except:
                return self.get_local_ip()  # 降级到内网 IP
    
    def get_outer_url(self, token: str = None) -> str:
        """
        获取外网访问地址（公网 IP+token）
        
        Args:
            token: 访问 token（可选，没有则自动生成）
        
        Returns:
            外网访问 URL
        """
        if not token:
            token = self.generate_access_token()
        
        # 获取公网 IP
        public_ip = self.get_public_ip()
        
        # 外网访问地址（公网 IP+ 端口+token）
        return f"http://{public_ip}:8766?token={token}"
    
    def get_mobile_url(self, token: str = None) -> str:
        """
        获取移动端访问地址（公网 IP+token）
        
        Args:
            token: 访问 token（可选）
        
        Returns:
            移动端访问 URL
        """
        if not token:
            token = self.generate_access_token()
        
        # 获取公网 IP
        public_ip = self.get_public_ip()
        
        # 移动端访问地址
        return f"http://{public_ip}:8766/mobile?token={token}"
    
    def validate_token(self, token: str) -> dict:
        """
        验证 token 是否有效
        
        Args:
            token: 要验证的 token
        
        Returns:
            验证结果
        """
        if token not in self.tokens:
            return {"valid": False, "error": "Token 不存在"}
        
        token_data = self.tokens[token]
        
        # 检查是否过期
        if time.time() > token_data["expires_at"]:
            return {"valid": False, "error": "Token 已过期"}
        
        # 更新访问记录
        token_data["access_count"] += 1
        token_data["last_accessed"] = time.time()
        self._save_tokens()
        
        return {
            "valid": True,
            "user_id": token_data["user_id"],
            "access_count": token_data["access_count"]
        }
    
    def list_tokens(self) -> list:
        """列出所有有效 tokens"""
        now = time.time()
        valid_tokens = []
        
        for token, data in self.tokens.items():
            if data["expires_at"] > now:
                valid_tokens.append({
                    "token": token,
                    "user_id": data["user_id"],
                    "created_at": datetime.fromtimestamp(data["created_at"]).strftime("%Y-%m-%d %H:%M"),
                    "expires_at": datetime.fromtimestamp(data["expires_at"]).strftime("%Y-%m-%d %H:%M"),
                    "access_count": data["access_count"]
                })
        
        return valid_tokens
    
    def revoke_token(self, token: str) -> bool:
        """撤销 token"""
        if token in self.tokens:
            del self.tokens[token]
            self._save_tokens()
            return True
        return False
    
    def generate_qr_code(self, url: str) -> str:
        """
        生成二维码（文本形式）
        
        Args:
            url: 要生成二维码的 URL
        
        Returns:
            ASCII 二维码（简化版）
        """
        # 简化版：显示 URL 和提示
        return f"""
╔══════════════════════════════════════════════════════╗
║                   扫码访问 Dashboard                   ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║   📱 请使用手机浏览器扫描下方二维码                    ║
║                                                      ║
║   [二维码区域 - 实际使用时调用 qrcode 库生成]          ║
║                                                      ║
║   或手动访问：                                        ║
║   {url[:50]}{"..." if len(url) > 50 else ""}
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""
    
    def print_access_info(self):
        """打印完整的访问信息"""
        print("\n" + "=" * 70)
        print("🚀 灵犀 Dashboard 访问信息")
        print("=" * 70)
        print()
        
        # 内网访问
        inner_url = self.get_inner_url()
        print(f"📡 内网访问（同一局域网）:")
        print(f"   {inner_url}")
        print(f"   {inner_url}/mobile (移动端)")
        print()
        
        # 外网访问
        token = self.generate_access_token()
        outer_url = self.get_outer_url(token)
        mobile_url = self.get_mobile_url(token)
        
        print(f"🌐 外网访问（任何地方）:")
        print(f"   {outer_url}")
        print(f"   {mobile_url} (移动端)")
        print()
        
        # Token 信息
        print(f"🔑 访问 Token:")
        print(f"   {token}")
        print(f"   有效期：30 天")
        print()
        
        # 二维码
        print(self.generate_qr_code(mobile_url))
        
        # 使用说明
        print("💡 使用说明:")
        print("   1. 内网访问：手机/电脑连接同一 WiFi，访问内网地址")
        print("   2. 外网访问：任何地方都可以访问外网地址")
        print("   3. Token 管理：查看/撤销 token，使用 --manage-tokens 参数")
        print()
        print("=" * 70)
        print()


def main():
    """主函数"""
    import sys
    
    generator = QuickAccessGenerator()
    
    # 命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--generate-token":
            # 生成新 token
            token = generator.generate_access_token()
            print(f"✅ 生成新 Token: {token}")
            print(f"   外网访问：{generator.get_outer_url(token)}")
        
        elif sys.argv[1] == "--list-tokens":
            # 列出所有 tokens
            tokens = generator.list_tokens()
            print(f"📋 有效 Tokens ({len(tokens)}个):")
            for t in tokens:
                print(f"   {t['token'][:20]}... - {t['user_id']} - 过期：{t['expires_at']}")
        
        elif sys.argv[1] == "--revoke":
            # 撤销 token
            if len(sys.argv) > 2:
                token = sys.argv[2]
                if generator.revoke_token(token):
                    print(f"✅ 已撤销 Token: {token[:20]}...")
                else:
                    print(f"❌ Token 不存在：{token}")
            else:
                print("❌ 请提供要撤销的 token")
        
        elif sys.argv[1] == "--validate":
            # 验证 token
            if len(sys.argv) > 2:
                token = sys.argv[2]
                result = generator.validate_token(token)
                if result["valid"]:
                    print(f"✅ Token 有效 - 用户：{result['user_id']} - 访问次数：{result['access_count']}")
                else:
                    print(f"❌ Token 无效：{result['error']}")
            else:
                print("❌ 请提供要验证的 token")
        
        elif sys.argv[1] == "--help":
            print("""
🚀 灵犀 Dashboard 快速访问工具

用法:
  python3 quick_access.py              # 显示访问信息
  python3 quick_access.py --generate-token   # 生成新 token
  python3 quick_access.py --list-tokens      # 列出所有 tokens
  python3 quick_access.py --revoke <token>   # 撤销 token
  python3 quick_access.py --validate <token> # 验证 token
  python3 quick_access.py --help             # 显示帮助
""")
        
        else:
            print(f"❌ 未知参数：{sys.argv[1]}")
            print("使用 --help 查看帮助")
    
    else:
        # 显示访问信息
        generator.print_access_info()


if __name__ == "__main__":
    main()
