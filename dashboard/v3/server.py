#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 服务器 - v3.3.3
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json
import re
from datetime import datetime

app = FastAPI(title="灵犀 Dashboard v3.3.3")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
DASHBOARD_DIR = Path(__file__).parent


def verify_token(token: str) -> bool:
    """验证访问令牌"""
    # 从文件读取 token
    token_file = Path("/root/.openclaw/workspace/.lingxi/dashboard_token.txt")
    
    if not token_file.exists():
        return True  # 没有 token 文件时允许访问
    
    saved_token = token_file.read_text().strip()
    return token == saved_token


@app.get("/")
async def root(token: str = ""):
    """根路径"""
    index_file = DASHBOARD_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "Dashboard 页面不存在"}


@app.get("/api/tasks")
async def get_tasks(limit: int = 50, token: str = ""):
    """获取任务列表 - 从 HEARTBEAT.md 读取"""
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token 无效")
    
    heartbeat_file = Path("/root/.openclaw/workspace/HEARTBEAT.md")
    
    if not heartbeat_file.exists():
        return {"tasks": [], "error": "HEARTBEAT.md 不存在"}
    
    try:
        content = heartbeat_file.read_text(encoding='utf-8')
        tasks = []
        
        # 解析最近完成任务
        lines = content.split('\n')
        in_completed_section = False
        
        for line in lines:
            # 检查是否进入完成任务部分
            if '### ✅ 最近完成' in line or '## 2️⃣ 最近完成任务' in line:
                in_completed_section = True
                continue
            
            if in_completed_section:
                # 检查是否到了下一个部分
                if line.startswith('## ') or (line.startswith('### ') and '最近完成' not in line and '定时任务' not in line):
                    break
                
                # 解析任务行（支持多种格式）
                if '- ✅' in line:
                    # 提取任务名称（支持 **粗体** 格式）
                    name_match = re.search(r'\*\*(.+?)\*\*', line)
                    if name_match:
                        name = name_match.group(1)
                    else:
                        # 没有粗体，提取 - ✅ 后面的内容
                        name = line.replace('- ✅', '').replace('📘', '').strip()
                        if ':' in name:
                            name = name.split(':')[0]
                    
                    # 提取完成时间（支持多种格式）
                    completed_at = None
                    time_match = re.search(r'完成时间：(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                    if time_match:
                        completed_at = time_match.group(1)
                    
                    # 提取备注
                    note_match = re.search(r'备注：(.+)', line)
                    note = note_match.group(1) if note_match else ""
                    
                    tasks.append({
                        "id": f"task_{len(tasks)+1}",
                        "title": name[:80],
                        "status": "已完成",
                        "completed_at": completed_at,
                        "note": note
                    })
                    
                    if len(tasks) >= limit:
                        break
        
        return {"tasks": tasks, "total": len(tasks)}
    
    except Exception as e:
        return {"tasks": [], "error": str(e)}


@app.get("/api/scheduled-tasks")
async def get_scheduled_tasks(token: str = ""):
    """获取定时任务列表 - 从 HEARTBEAT.md 读取"""
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token 无效")
    
    heartbeat_file = Path("/root/.openclaw/workspace/HEARTBEAT.md")
    
    if not heartbeat_file.exists():
        return {"tasks": []}
    
    try:
        content = heartbeat_file.read_text(encoding='utf-8')
        tasks = []
        
        # 解析定时任务
        in_scheduled_section = False
        for line in content.split('\n'):
            if '## ⏰ 定时任务' in line or '定时任务状态' in line:
                in_scheduled_section = True
                continue
            
            if in_scheduled_section and line.startswith('- ⏰ **'):
                # 提取任务名称
                name_match = re.search(r'\*\*(.+?)\*\*', line)
                name = name_match.group(1) if name_match else "未知任务"
                
                # 提取周期
                period_match = re.search(r'周期：(.+)', line)
                period = period_match.group(1) if period_match else "未知"
                
                tasks.append({
                    "id": f"scheduled_{len(tasks)+1}",
                    "name": name,
                    "period": period,
                    "status": "运行中"
                })
        
        return {"tasks": tasks, "total": len(tasks)}
    
    except Exception as e:
        return {"tasks": [], "error": str(e)}


@app.get("/api/stats")
async def get_stats(token: str = ""):
    """获取统计数据"""
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token 无效")
    
    try:
        # 统计任务数
        sessions_dir = Path("/root/.openclaw/agents/main/sessions")
        total_tasks = 0
        
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.jsonl"):
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            msg = json.loads(line)
                            if msg.get('role') == 'user':
                                total_tasks += 1
                        except:
                            continue
        
        return {
            "total_tasks": total_tasks,
            "total_memories": 0,
            "total_skills": 18,
            "api_calls_today": 0
        }
    
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
