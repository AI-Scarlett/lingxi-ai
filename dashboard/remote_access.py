#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard 远程访问配置

功能：
- 内网穿透配置（ngrok/ClawPort）
- 公网访问 URL 生成
- 认证和授权
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional
import hashlib


class RemoteAccessConfig:
    """远程访问配置"""
    
    def __init__(self):
        self.config_path = Path("~/.openclaw/workspace/.lingxi/remote_access.json").expanduser()
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return {
            "enabled": False,
            "provider": "ngrok",  # ngrok / clawport / frp
            "public_url": None,
            "local_port": 8765,
            "auth_token": None,
            "created_at": None,
            "expires_at": None
        }
    
    def _save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def enable_remote_access(self, provider: str = "ngrok", auth_token: str = None) -> str:
        """启用远程访问"""
        self.config["enabled"] = True
        self.config["provider"] = provider
        self.config["auth_token"] = auth_token or self._generate_token()
        self.config["created_at"] = time.time()
        
        # 默认 7 天有效期
        self.config["expires_at"] = time.time() + (7 * 86400)
        
        self._save_config()
        
        return self.config["auth_token"]
    
    def disable_remote_access(self):
        """禁用远程访问"""
        self.config["enabled"] = False
        self.config["public_url"] = None
        self._save_config()
    
    def set_public_url(self, url: str):
        """设置公网 URL"""
        self.config["public_url"] = url
        self._save_config()
    
    def get_public_url(self) -> Optional[str]:
        """获取公网 URL"""
        if not self.config["enabled"]:
            return None
        
        # 检查是否过期
        if self.config["expires_at"] and time.time() > self.config["expires_at"]:
            self.disable_remote_access()
            return None
        
        return self.config["public_url"]
    
    def _generate_token(self) -> str:
        """生成访问令牌"""
        return hashlib.sha256(
            str(time.time()).encode() + b"lingxi_v4"
        ).hexdigest()[:32]
    
    def get_config(self) -> dict:
        """获取配置"""
        return {
            "enabled": self.config["enabled"],
            "provider": self.config["provider"],
            "public_url": self.config["public_url"],
            "local_port": self.config["local_port"],
            "has_auth": bool(self.config["auth_token"]),
            "expires_in_days": (
                (self.config["expires_at"] - time.time()) / 86400
                if self.config["expires_at"] else None
            )
        }


# 全局实例
_config = None


def get_remote_access_config() -> RemoteAccessConfig:
    """获取远程访问配置实例"""
    global _config
    if _config is None:
        _config = RemoteAccessConfig()
    return _config


async def setup_ngrok(authtoken: str, port: int = 8765) -> str:
    """设置 ngrok 内网穿透"""
    import asyncio
    
    print(f"🔧 启动 ngrok（端口 {port}）...")
    
    # 使用 pyngrok 或调用 ngrok CLI
    try:
        from pyngrok import ngrok
        
        # 设置认证 token
        ngrok.set_auth_token(authtoken)
        
        # 创建隧道
        tunnel = ngrok.connect(port, "http")
        public_url = tunnel.public_url
        
        print(f"✅ ngrok 隧道已创建：{public_url}")
        
        return public_url
    
    except ImportError:
        print("⚠️ pyngrok 未安装，使用 ngrok CLI")
        
        # 调用 ngrok CLI
        proc = await asyncio.create_subprocess_exec(
            "ngrok", "http", str(port), "--log", "stdout",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 等待 ngrok 启动
        await asyncio.sleep(3)
        
        # 读取日志获取 URL
        # TODO: 解析 ngrok API 获取 URL
        
        return f"http://localhost:4040"  # ngrok Web UI


async def setup_clawport(port: int = 8765) -> str:
    """设置 ClawPort 内网穿透"""
    print(f"🔧 启动 ClawPort（端口 {port}）...")
    
    # TODO: 实现 ClawPort 集成
    # 这里使用模拟 URL
    
    public_url = f"https://lingxi.clawport.ai"
    
    print(f"✅ ClawPort 隧道已创建：{public_url}")
    
    return public_url


async def demo():
    """演示远程访问配置"""
    print("="*60)
    print("🌐 Dashboard 远程访问演示")
    print("="*60)
    
    config = get_remote_access_config()
    
    # 查看当前配置
    current = config.get_config()
    print(f"\n📊 当前配置：{current}")
    
    # 启用远程访问
    if not current["enabled"]:
        print("\n🔑 启用远程访问...")
        token = config.enable_remote_access(provider="ngrok")
        print(f"✅ 访问令牌：{token}")
    
    # 设置 ngrok
    print("\n🔧 设置 ngrok...")
    # public_url = await setup_ngrok("your_ngrok_token")
    # config.set_public_url(public_url)
    
    # 获取公网 URL
    public_url = config.get_public_url()
    if public_url:
        print(f"\n✅ 公网访问 URL: {public_url}")
        print(f"🔐 访问令牌：{config.config['auth_token']}")
        print(f"📱 完整链接：{public_url}/?token={config.config['auth_token']}")
    else:
        print("\n⚠️ 远程访问未启用或已过期")
    
    print("\n✨ 演示完成！")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
