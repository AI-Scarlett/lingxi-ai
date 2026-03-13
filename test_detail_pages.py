#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详情页 API 测试脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8765"

def test_api(endpoint, expected_status=200):
    """测试 API 端点"""
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        status = "✅" if resp.status_code == expected_status else "❌"
        print(f"{status} {endpoint} -> {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                print(f"   返回字段：{', '.join(data.keys())[:80]}")
            elif isinstance(data, list):
                print(f"   返回列表：{len(data)} 项")
        return resp.status_code == expected_status
    except Exception as e:
        print(f"❌ {endpoint} -> 错误：{e}")
        return False

def main():
    print("=" * 60)
    print("灵犀 Dashboard 详情页 API 测试")
    print("=" * 60)
    print()
    
    # 健康检查
    print("📊 健康检查")
    test_api("/api/health")
    print()
    
    # 任务相关
    print("📋 任务相关 API")
    test_api("/api/tasks?limit=5")
    # 如果有任务，测试详情页
    try:
        resp = requests.get(f"{BASE_URL}/api/tasks?limit=1", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('tasks'):
                task_id = data['tasks'][0]['id']
                print(f"   测试任务详情：{task_id[:8]}...")
                test_api(f"/api/tasks/{task_id}")
                test_api(f"/api/tasks/{task_id}/timeline")
                test_api(f"/api/tasks/{task_id}/subtasks")
    except Exception as e:
        print(f"   跳过任务详情测试：{e}")
    print()
    
    # 技能相关
    print("🛠️  技能相关 API")
    test_api("/api/skills/list")
    try:
        resp = requests.get(f"{BASE_URL}/api/skills/list", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('skills'):
                skill_name = data['skills'][0]['name']
                print(f"   测试技能详情：{skill_name}")
                test_api(f"/api/skills/{skill_name}")
                test_api(f"/api/skills/{skill_name}/stats")
    except Exception as e:
        print(f"   跳过技能详情测试：{e}")
    print()
    
    # Agent 相关
    print("🤖 Agent 相关 API")
    test_api("/api/agents/list")
    test_api("/api/agents/main")
    test_api("/api/agents/main/sessions")
    test_api("/api/agents/main/tasks")
    test_api("/api/agents/main/health")
    print()
    
    # 会话相关
    print("💬 会话相关 API")
    test_api("/api/sessions/list?limit=5")
    try:
        resp = requests.get(f"{BASE_URL}/api/sessions/list?limit=1", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('sessions'):
                session_id = data['sessions'][0]['id']
                print(f"   测试会话详情：{session_id[:8]}...")
                test_api(f"/api/sessions/{session_id}")
                test_api(f"/api/sessions/{session_id}/messages")
                test_api(f"/api/sessions/{session_id}/tools")
                test_api(f"/api/sessions/{session_id}/stats")
    except Exception as e:
        print(f"   跳过会话详情测试：{e}")
    print()
    
    # 记忆相关
    print("🧠 记忆相关 API")
    test_api("/api/memory/list?limit=5")
    try:
        resp = requests.get(f"{BASE_URL}/api/memory/list?limit=1&source=stm", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('memories'):
                memory_id = data['memories'][0]['id']
                print(f"   测试记忆详情：{memory_id[:8]}...")
                test_api(f"/api/memory/{memory_id}?source=stm")
                test_api(f"/api/memory/{memory_id}/accesses")
                test_api(f"/api/memory/{memory_id}/relations")
                test_api(f"/api/memory/{memory_id}/timeline")
    except Exception as e:
        print(f"   跳过记忆详情测试：{e}")
    print()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
