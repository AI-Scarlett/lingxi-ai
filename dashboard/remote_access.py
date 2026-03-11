#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 远程访问模块

功能：
- 将本地 Dashboard 暴露到公网
- 支持认证和访问控制
- 移动端适配优化
- 类似 ngrok/frp 的简化实现
"""

import asyncio
import aiohttp
from aiohttp import web
from typing import Dict, Optional
import time
import hashlib
import secrets


class RemoteAccessServer:
    """远程访问服务器"""
    
    def __init__(self, local_port: int = 8765, public_host: str = None):
        self.local_port = local_port
        # 支持用户自定义域名，默认使用官方域名
        self.public_host = public_host or "lingxi.me-ai.help"
        self.app = web.Application()
        self.access_tokens: Dict[str, Dict] = {}
        
        # 设置路由
        self.app.router.add_get('/{path:.*}', self.handle_request)
        self.app.router.add_post('/api/auth', self.handle_auth)
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "authenticated_requests": 0,
            "failed_requests": 0
        }
    
    def generate_token(self, user_id: str, expires_in: int = 86400) -> str:
        """生成访问令牌"""
        token = secrets.token_urlsafe(32)
        
        self.access_tokens[token] = {
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": time.time() + expires_in,
            "access_count": 0
        }
        
        return token
    
    async def handle_auth(self, request: web.Request) -> web.Response:
        """处理认证请求"""
        try:
            data = await request.json()
            user_id = data.get("user_id")
            password = data.get("password")
            
            # 简单认证（实际应该验证数据库）
            if user_id and password:
                token = self.generate_token(user_id)
                
                return web.json_response({
                    "success": True,
                    "token": token,
                    "expires_in": 86400
                })
            
            return web.json_response({
                "success": False,
                "error": "Invalid credentials"
            }, status=401)
        
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def handle_request(self, request: web.Request) -> web.Response:
        """处理请求（代理到本地 Dashboard）"""
        self.stats["total_requests"] += 1
        
        try:
            # 检查认证（支持 URL 参数和 Header）
            token = request.query.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
            
            # 验证 token
            if token:
                from quick_access import QuickAccessGenerator
                validator = QuickAccessGenerator()
                result = validator.validate_token(token)
                
                if not result["valid"]:
                    self.stats["failed_requests"] += 1
                    return web.html("""
                        <html>
                        <head><title>认证失败</title></head>
                        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                            <h1>❌ 认证失败</h1>
                            <p>Token 无效或已过期</p>
                            <p>请重新获取访问地址</p>
                        </body>
                        </html>
                    """, status=401)
                
                self.stats["authenticated_requests"] += 1
            
            # 代理到本地 Dashboard
            path = request.match_info['path']
            local_url = f"http://localhost:{self.local_port}/{path}"
            
            if request.query_string:
                # 移除 token 参数
                query_params = request.query.copy()
                query_params.pop("token", None)
                if query_params:
                    local_url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
            
            async with aiohttp.ClientSession() as session:
                async with session.get(local_url) as resp:
                    content = await resp.text()
                    
                    return web.Response(
                        text=content,
                        status=resp.status,
                        content_type=resp.content_type
                    )
        
        except Exception as e:
            self.stats["failed_requests"] += 1
            
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    def get_public_url(self) -> str:
        """获取公网访问 URL"""
        return f"https://{self.public_host}"
    
    def get_mobile_url(self) -> str:
        """获取移动端访问 URL"""
        return f"https://{self.public_host}/mobile"
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "active_tokens": len(self.access_tokens),
            "public_url": self.get_public_url()
        }
    
    async def start(self, host: str = "0.0.0.0", port: int = 8766):
        """启动远程访问服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"🌐 远程访问服务器已启动 (v3.3.3)")
        print(f"📱 公网访问：{self.get_public_url()}")
        print(f"📱 移动端：{self.get_mobile_url()}")
        print(f"🔐 监听端口：{host}:{port}")
        
        return runner


# 便捷函数
_remote_server = None

def get_remote_access_server(local_port: int = 8765) -> RemoteAccessServer:
    """获取远程访问服务器实例"""
    global _remote_server
    
    if _remote_server is None:
        _remote_server = RemoteAccessServer(local_port)
    
    return _remote_server


if __name__ == "__main__":
    # 测试运行
    async def test():
        server = get_remote_access_server()
        
        # 启动服务器
        await server.start(port=8766)
        
        # 生成测试令牌
        token = server.generate_token("test_user")
        print(f"🔑 测试令牌：{token}")
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(60)
                stats = server.get_stats()
                print(f"📊 统计：{stats}")
        except KeyboardInterrupt:
            print("\n✅ 远程访问服务器已停止")
    
    asyncio.run(test())
