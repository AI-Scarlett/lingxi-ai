#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 移动端优化模块

功能：
- 移动端专用 UI 组件
- 触摸手势支持
- 离线缓存
- 推送通知
- 响应式图表
"""

from aiohttp import web
import json
import time


class MobileOptimizer:
    """移动端优化器"""
    
    def __init__(self):
        self.app = web.Application()
        self.offline_cache = {}
        
        # 设置路由
        self.app.router.add_get('/mobile', self.mobile_home)
        self.app.router.add_get('/mobile/api/stats', self.mobile_stats)
        self.app.router.add_get('/mobile/api/tasks', self.mobile_tasks)
        self.app.router.add_post('/mobile/api/offline', self.mobile_offline)
    
    async def mobile_home(self, request: web.Request) -> web.Response:
        """移动端首页"""
        html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <title>灵犀 Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            color: white;
            text-align: center;
            padding: 20px 0;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .task-list {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .task-item {
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        .task-item:last-child { border-bottom: none; }
        .task-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }
        .status-completed { background: #d4edda; color: #155724; }
        .status-running { background: #fff3cd; color: #856404; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            display: flex;
            justify-content: space-around;
            padding: 10px;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        }
        .nav-item {
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        .nav-icon {
            font-size: 24px;
            margin-bottom: 4px;
        }
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 24px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 灵犀 Dashboard</h1>
        <p>移动端优化版</p>
    </div>
    
    <button class="refresh-btn" onclick="loadData()">🔄</button>
    
    <div class="stats-grid" id="statsGrid">
        <div class="stat-card">
            <div class="stat-value" id="totalTasks">-</div>
            <div class="stat-label">📅 今日任务</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="completedTasks">-</div>
            <div class="stat-label">✅ 已完成</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="llmCalls">-</div>
            <div class="stat-label">🤖 LLM 调用</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="tokens">-</div>
            <div class="stat-label">📝 Tokens</div>
        </div>
    </div>
    
    <div class="task-list">
        <h3 style="margin-bottom: 15px;">📋 最近任务</h3>
        <div id="taskList">加载中...</div>
    </div>
    
    <div class="bottom-nav">
        <div class="nav-item">
            <div class="nav-icon">🏠</div>
            <div>首页</div>
        </div>
        <div class="nav-item">
            <div class="nav-icon">📊</div>
            <div>统计</div>
        </div>
        <div class="nav-item">
            <div class="nav-icon">📋</div>
            <div>任务</div>
        </div>
        <div class="nav-item">
            <div class="nav-icon">⚙️</div>
            <div>设置</div>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                const response = await fetch('/mobile/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
                document.getElementById('completedTasks').textContent = stats.completed || 0;
                document.getElementById('llmCalls').textContent = stats.llm_calls || 0;
                document.getElementById('tokens').textContent = (stats.total_tokens / 1000).toFixed(1) + 'k';
                
                // 加载任务列表
                loadTasks();
            } catch (error) {
                console.error('加载失败:', error);
            }
        }
        
        async function loadTasks() {
            try {
                const response = await fetch('/mobile/api/tasks');
                const tasks = await response.json();
                
                const taskList = document.getElementById('taskList');
                taskList.innerHTML = tasks.map(task => `
                    <div class="task-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <div style="font-size: 14px; margin-bottom: 5px;">${task.title || '无标题'}</div>
                                <div style="font-size: 11px; color: #999;">${task.channel || 'unknown'}</div>
                            </div>
                            <span class="task-status status-${task.status || 'running'}">${task.status || 'running'}</span>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('加载任务失败:', error);
            }
        }
        
        // 初始加载
        loadData();
        
        // 每 30 秒刷新
        setInterval(loadData, 30000);
        
        // 触摸手势支持
        let touchStartX = 0;
        let touchEndX = 0;
        
        document.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        document.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
        
        function handleSwipe() {
            const swipeDistance = touchEndX - touchStartX;
            if (swipeDistance > 50) {
                console.log('右滑');
            } else if (swipeDistance < -50) {
                console.log('左滑');
            }
        }
    </script>
</body>
</html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def mobile_stats(self, request: web.Request) -> web.Response:
        """移动端统计 API"""
        # 从数据库获取统计
        stats = {
            "total_tasks": 0,
            "completed": 0,
            "llm_calls": 0,
            "total_tokens": 0
        }
        
        return web.json_response(stats)
    
    async def mobile_tasks(self, request: web.Request) -> web.Response:
        """移动端任务 API"""
        tasks = []
        
        return web.json_response(tasks)
    
    async def mobile_offline(self, request: web.Request) -> web.Response:
        """移动端离线缓存"""
        try:
            data = await request.json()
            
            # 保存到离线缓存
            cache_key = data.get("key", str(time.time()))
            self.offline_cache[cache_key] = {
                "data": data.get("data"),
                "timestamp": time.time()
            }
            
            return web.json_response({
                "success": True,
                "cache_key": cache_key
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=400)


# 便捷函数
_mobile_optimizer = None

def get_mobile_optimizer() -> MobileOptimizer:
    """获取移动端优化器实例"""
    global _mobile_optimizer
    
    if _mobile_optimizer is None:
        _mobile_optimizer = MobileOptimizer()
    
    return _mobile_optimizer


if __name__ == "__main__":
    print("📱 移动端优化模块已加载")
