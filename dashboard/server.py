#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀数据看板 - FastAPI 应用（带公网访问支持）
Lingxi Dashboard API Server with Public Access

作者：斯嘉丽 Scarlett
日期：2026-03-09

功能：
- 公网 IP 访问（0.0.0.0）
- Token 认证保护
- 自动生成访问地址
- 支持 HTTPS（可选）
"""

import asyncio
import time
import json
import secrets
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends, Security
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from database import get_database, TaskRecord, TaskStatus, TaskStage


# ==================== 安全配置 ====================

# 自动生成 Token（首次启动时）
TOKEN_FILE = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

if TOKEN_FILE.exists():
    DASHBOARD_TOKEN = TOKEN_FILE.read_text().strip()
else:
    DASHBOARD_TOKEN = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(DASHBOARD_TOKEN)
    print(f"🔑 已生成新 Token: {DASHBOARD_TOKEN}")

# 安全方案
security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """验证 Token"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="缺少认证 Token")
    
    if credentials.credentials != DASHBOARD_TOKEN:
        raise HTTPException(status_code=401, detail="Token 无效")
    
    return credentials.credentials


def get_public_ip():
    """获取公网 IP"""
    try:
        # 方法 1: 通过 socket 获取
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"


def get_local_ip():
    """获取局域网 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="灵犀数据看板",
    description="Lingxi Dashboard - 实时监控任务执行情况",
    version="1.0.0"
)

# CORS 中间件（允许所有来源，因为我们有 Token 认证）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== WebSocket 连接管理 ====================

class ConnectionManager:
    """WebSocket 连接管理器（带 Token 认证）"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, token: str):
        """连接（验证 Token）"""
        if token != DASHBOARD_TOKEN:
            await websocket.close(code=4001, reason="Token 无效")
            return False
        
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 新的看板连接，当前连接数：{len(self.active_connections)}")
        return True
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔌 看板连接断开，当前连接数：{len(self.active_connections)}")
    
    async def broadcast(self, message: Dict):
        """广播消息给所有连接"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"⚠️  发送消息失败：{e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_task(self, task_id: str, message: Dict):
        """发送任务更新（带任务 ID）"""
        message['task_id'] = task_id
        await self.broadcast(message)


manager = ConnectionManager()


# ==================== API 路由 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """看板首页（带 Token 验证）"""
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        content = html_path.read_text(encoding='utf-8')
        # 在 HTML 中注入 Token
        content = content.replace('__DASHBOARD_TOKEN__', DASHBOARD_TOKEN)
        return HTMLResponse(content=content)
    return HTMLResponse(content=f"""
    <html>
    <head><title>🚀 灵犀数据看板</title></head>
    <body style="font-family: sans-serif; padding: 40px;">
        <h1>🚀 灵犀数据看板</h1>
        <p>✅ API 服务运行中</p>
        <p>🔑 Token: <code>{DASHBOARD_TOKEN}</code></p>
        <p>📊 访问 <a href="/?token={DASHBOARD_TOKEN}">/?token={DASHBOARD_TOKEN}</a> 查看看板</p>
    </body>
    </html>
    """)


@app.get("/api/stats")
async def get_stats(token: str = Query(default=None), hours: int = Query(default=24, ge=1, le=720)):
    """获取统计数据"""
    # 支持 URL 参数 Token 和 Header Token
    if not token:
        raise HTTPException(status_code=401, detail="缺少认证 Token")
    if token != DASHBOARD_TOKEN:
        raise HTTPException(status_code=401, detail="Token 无效")
    
    db = get_database()
    await db.connect()
    stats = await db.get_stats(hours)
    return JSONResponse(content=stats)


@app.get("/api/tasks")
async def get_tasks(
    token: str = Depends(verify_token),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user_id: str = None,
    status: str = None,
    channel: str = None
):
    """获取任务列表"""
    db = get_database()
    await db.connect()
    tasks = await db.get_tasks(limit, offset, user_id, status, channel)
    return JSONResponse(content={
        "tasks": [task.to_dict() for task in tasks],
        "total": len(tasks),
        "limit": limit,
        "offset": offset
    })


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str, token: str = Depends(verify_token)):
    """获取任务详情"""
    db = get_database()
    await db.connect()
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return JSONResponse(content=task.to_dict())


@app.get("/api/errors")
async def get_errors(token: str = Depends(verify_token), limit: int = Query(default=20, ge=1, le=100)):
    """获取最近错误"""
    db = get_database()
    await db.connect()
    errors = await db.get_recent_errors(limit)
    return JSONResponse(content={"errors": errors})


@app.get("/api/health")
async def health_check():
    """健康检查（无需认证）"""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    })


@app.get("/api/token")
async def get_token_info():
    """获取 Token 信息（用于配置）"""
    return JSONResponse(content={
        "token": DASHBOARD_TOKEN,
        "message": "使用此 Token 访问受保护的 API"
    })


# ==================== WebSocket 路由 ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接（带 Token 认证）"""
    # 从 URL 获取 Token
    token = websocket.query_params.get("token", "")
    
    if await manager.connect(websocket, token):
        try:
            while True:
                # 保持连接，接收心跳
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            manager.disconnect(websocket)


# ==================== 外部调用接口 ====================

async def record_task_start(task_id: str, user_id: str, channel: str, user_input: str):
    """记录任务开始"""
    db = get_database()
    await db.connect()
    
    task = TaskRecord(
        id=task_id,
        user_id=user_id,
        channel=channel,
        user_input=user_input,
        status=TaskStatus.PROCESSING.value,
        stage=TaskStage.RECEIVED.value,
        created_at=time.time(),
        updated_at=time.time()
    )
    
    await db.insert_task(task)
    await manager.send_to_task(task_id, {
        "type": "task_started",
        "task": task.to_dict()
    })


async def record_task_stage(task_id: str, stage: str, data: Dict = None):
    """记录任务阶段"""
    db = get_database()
    await db.connect()
    
    updates = {"stage": stage}
    if data:
        updates.update(data)
    
    await db.update_task(task_id, updates)
    await manager.send_to_task(task_id, {
        "type": "stage_update",
        "stage": stage,
        "data": data
    })


async def record_task_complete(task_id: str, result: Dict):
    """记录任务完成"""
    db = get_database()
    await db.connect()
    
    updates = {
        "status": TaskStatus.COMPLETED.value,
        "stage": TaskStage.COMPLETED.value,
        "completed_at": time.time(),
        **result
    }
    
    await db.update_task(task_id, updates)
    await manager.send_to_task(task_id, {
        "type": "task_completed",
        "result": result
    })


async def record_task_error(task_id: str, error_type: str, error_message: str, traceback: str = ""):
    """记录任务错误"""
    db = get_database()
    await db.connect()
    
    updates = {
        "status": TaskStatus.FAILED.value,
        "error_type": error_type,
        "error_message": error_message,
        "error_traceback": traceback,
        "completed_at": time.time()
    }
    
    await db.update_task(task_id, updates)
    await manager.send_to_task(task_id, {
        "type": "task_error",
        "error_type": error_type,
        "error_message": error_message
    })


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """启动事件"""
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print("=" * 60)
    print("🚀 灵犀数据看板启动")
    print("=" * 60)
    print("")
    print(f"🔑 访问 Token: {DASHBOARD_TOKEN}")
    print("")
    print(f"📊 本地访问：http://localhost:8765/?token={DASHBOARD_TOKEN}")
    print(f"📡 局域网访问：http://{local_ip}:8765/?token={DASHBOARD_TOKEN}")
    print(f"🌐 公网访问：http://{public_ip}:8765/?token={DASHBOARD_TOKEN}")
    print("")
    print(f"📁 数据库：~/.openclaw/workspace/.lingxi/dashboard.db")
    print(f"📁 Token 文件：~/.openclaw/workspace/.lingxi/dashboard_token.txt")
    print("")
    print("=" * 60)
    print("⚠️  安全提示:")
    print("  - 请妥善保管 Token，不要泄露给他人")
    print("  - 如需重置 Token，删除 dashboard_token.txt 文件后重启服务")
    print("  - 生产环境建议使用 HTTPS 和防火墙")
    print("=" * 60)
    
    # 初始化数据库
    db = get_database()
    await db.connect()
    
    # 保存访问信息到文件
    info_file = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_access.txt"
    info_file.write_text(f"""# 灵犀数据看板访问信息

## 访问地址

本地访问：http://localhost:8765/?token={DASHBOARD_TOKEN}
局域网访问：http://{local_ip}:8765/?token={DASHBOARD_TOKEN}
公网访问：http://{public_ip}:8765/?token={DASHBOARD_TOKEN}

## Token
{DASHBOARD_TOKEN}

## 生成时间
{datetime.now().isoformat()}

## API 端点

- 统计数据：GET /api/stats?hours=24&token={DASHBOARD_TOKEN}
- 任务列表：GET /api/tasks?limit=50&token={DASHBOARD_TOKEN}
- 任务详情：GET /api/tasks/{{task_id}}?token={DASHBOARD_TOKEN}
- 最近错误：GET /api/errors?limit=20&token={DASHBOARD_TOKEN}
- 健康检查：GET /api/health
- WebSocket: ws://localhost:8765/ws?token={DASHBOARD_TOKEN}

## 安全提示

- 请妥善保管 Token，不要泄露给他人
- 如需重置 Token，删除 dashboard_token.txt 文件后重启服务
- 生产环境建议使用 HTTPS 和防火墙
""")
    print(f"💾 访问信息已保存：{info_file}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    db = get_database()
    await db.close()
    print("👋 灵犀数据看板已关闭")


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 灵犀数据看板")
    print("=" * 60)
    print("启动服务器...")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # 监听所有网卡（支持公网访问）
        port=8765,
        log_level="info"
    )
