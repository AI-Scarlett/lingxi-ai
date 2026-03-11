#!/usr/bin/env python3
"""
Dashboard 客户端 - 灵犀任务记录

功能：
- 记录任务到 Dashboard
- 查询统计数据
- 健康检查
"""

import httpx
import time
from pathlib import Path
from typing import Optional, Dict, Any


class DashboardClient:
    """Dashboard API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url
        self.token = self._load_token()
    
    def _load_token(self) -> str:
        """加载 Dashboard Token"""
        token_file = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
        if token_file.exists():
            return token_file.read_text().strip()
        return ""
    
    def record_task(self, task_data: Dict[str, Any]) -> bool:
        """
        记录任务到 Dashboard
        
        Args:
            task_data: 任务数据
        
        Returns:
            是否成功
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"{self.base_url}/api/tasks",
                    json=task_data
                )
                return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Dashboard 记录失败: {e}")
            return False
    
    def get_stats(self, hours: int = 24) -> Dict:
        """获取统计数据"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/stats?hours={hours}")
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return {"total_tasks": 0, "llm_calls": 0}
    
    def get_tasks(self, limit: int = 50) -> list:
        """获取任务列表"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tasks?limit={limit}")
                if response.status_code == 200:
                    return response.json().get("tasks", [])
        except:
            pass
        return []
    
    def health_check(self) -> bool:
        """检查 Dashboard 是否在线"""
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{self.base_url}/api/health")
                return response.status_code == 200
        except:
            return False


# 全局实例
_dashboard_client: Optional[DashboardClient] = None


def get_dashboard_client() -> DashboardClient:
    """获取 Dashboard 客户端实例"""
    global _dashboard_client
    if _dashboard_client is None:
        _dashboard_client = DashboardClient()
    return _dashboard_client


def record_to_dashboard(
    user_input: str,
    user_id: str = "unknown",
    channel: str = "unknown",
    llm_model: str = "",
    skill_name: str = "",
    skill_agent: str = "",
    status: str = "completed",
    response_time_ms: float = 0,
    llm_tokens_in: int = 0,
    llm_tokens_out: int = 0,
    final_output: str = ""
) -> bool:
    """
    便捷函数：记录任务到 Dashboard
    """
    client = get_dashboard_client()
    
    task_data = {
        "user_id": user_id,
        "channel": channel,
        "user_input": user_input[:500],  # 限制长度
        "status": status,
        "stage": "completed",
        "llm_model": llm_model,
        "skill_name": skill_name,
        "skill_agent": skill_agent,
        "response_time_ms": response_time_ms,
        "llm_tokens_in": llm_tokens_in,
        "llm_tokens_out": llm_tokens_out,
        "final_output": final_output[:1000] if final_output else ""
    }
    
    return client.record_task(task_data)