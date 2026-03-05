#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 自动重试和自愈系统 v2.8.5

目标：减少人工干预，提高成功率
1. GitHub 推送自动重试（指数退避）
2. 任务执行自愈机制（重试 + 降级）
3. 主动错误提醒（重复错误预警）
"""

import asyncio
import time
import os
import subprocess
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

# ==================== 配置 ====================

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0  # 秒
    max_delay: float = 60.0  # 秒
    exponential_base: float = 2.0  # 指数退避基数
    jitter: bool = True  # 是否添加随机抖动

# ==================== 工具函数 ====================

def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """计算重试延迟（指数退避 + 抖动）"""
    import random
    
    # 指数退避
    delay = config.base_delay * (config.exponential_base ** attempt)
    
    # 限制最大延迟
    delay = min(delay, config.max_delay)
    
    # 添加抖动（±25%）
    if config.jitter:
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)

# ==================== Git 推送重试 ====================

class GitPushManager:
    """Git 推送管理器（带自动重试）"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.config = RetryConfig(
            max_retries=3,
            base_delay=2.0,
            max_delay=30.0
        )
        self.push_history = []
    
    async def push(self, branch: str = "main", tags: bool = False) -> Dict[str, Any]:
        """推送到 GitHub（自动重试，带 5 分钟超时）"""
        result = {
            "success": False,
            "attempts": 0,
            "error": None,
            "message": ""
        }
        
        # 5 分钟超时配置
        PUSH_TIMEOUT = 300.0  # 5 分钟 = 300 秒
        
        for attempt in range(self.config.max_retries):
            result["attempts"] = attempt + 1
            
            try:
                # 构建命令
                cmd = ["git", "push", "origin", branch]
                if tags:
                    cmd.append("--tags")
                
                # 执行推送
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.repo_path
                )
                
                try:
                    # 带超时的等待（5 分钟）
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=PUSH_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    # 超时后 kill 进程
                    print(f"⏰ Git 推送超时 ({PUSH_TIMEOUT}秒)，终止进程...")
                    try:
                        process.kill()
                        await process.wait()
                    except:
                        pass
                    result["error"] = f"推送超时 ({PUSH_TIMEOUT}秒)"
                    
                    # 准备重试
                    if attempt < self.config.max_retries - 1:
                        delay = calculate_delay(attempt, self.config)
                        print(f"⏳ {delay:.1f}秒后重试...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        break
                
                if process.returncode == 0:
                    result["success"] = True
                    result["message"] = stdout.decode('utf-8', errors='ignore').strip()
                    result["error"] = None
                    
                    print(f"✅ Git 推送成功 (尝试 {attempt + 1} 次)")
                    self._record_push(result)
                    return result
                else:
                    error_msg = stderr.decode('utf-8', errors='ignore').strip()
                    result["error"] = error_msg
                    
                    # 检查是否可重试的错误
                    if not self._is_retryable_error(error_msg):
                        print(f"❌ Git 推送失败（不可重试）: {error_msg}")
                        break
                    
                    # 准备重试
                    if attempt < self.config.max_retries - 1:
                        delay = calculate_delay(attempt, self.config)
                        print(f"⏳ Git 推送失败，{delay:.1f}秒后重试 ({attempt + 1}/{self.config.max_retries})...")
                        await asyncio.sleep(delay)
                    else:
                        print(f"❌ Git 推送失败（已达最大重试次数）: {error_msg}")
            
            except Exception as e:
                result["error"] = str(e)
                print(f"❌ Git 推送异常：{e}")
                break
        
        # 记录失败
        self._record_push(result)
        
        # 发送失败通知
        if not result["success"]:
            await self._send_push_failure_alert(result)
        
        return result
    
    def _is_retryable_error(self, error_msg: str) -> bool:
        """判断是否是可重试的错误"""
        retryable_keywords = [
            "timeout", "timed out",
            "connection reset",
            "connection refused",
            "network is unreachable",
            "couldn't connect to server",
            "transient",
            "temporary"
        ]
        
        error_lower = error_msg.lower()
        return any(kw in error_lower for kw in retryable_keywords)
    
    def _record_push(self, result: Dict):
        """记录推送历史"""
        self.push_history.append({
            "timestamp": datetime.now().isoformat(),
            "success": result["success"],
            "attempts": result["attempts"],
            "error": result["error"]
        })
        
        # 限制历史记录数量
        if len(self.push_history) > 100:
            self.push_history = self.push_history[-100:]
    
    async def _send_push_failure_alert(self, result: Dict):
        """发送推送失败警报"""
        # 这里可以集成 QQ/微信/邮件通知
        # 暂时打印日志
        print(f"\n🚨 Git 推送失败警报")
        print(f"   错误：{result['error']}")
        print(f"   尝试次数：{result['attempts']}")
        print(f"   建议：检查网络连接或稍后手动重试\n")
    
    def get_statistics(self) -> Dict:
        """获取推送统计"""
        if not self.push_history:
            return {"total": 0}
        
        total = len(self.push_history)
        success = sum(1 for p in self.push_history if p["success"])
        
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": f"{success/total*100:.1f}%",
            "avg_attempts": sum(p["attempts"] for p in self.push_history) / total
        }

# ==================== 任务自愈执行器 ====================

class SelfHealingExecutor:
    """自愈执行器"""
    
    def __init__(self):
        self.config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=10.0
        )
        self.execution_history = []
    
    async def execute(
        self,
        task_id: str,
        task_func: Callable,
        fallback_func: Callable = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """执行任务（带自愈机制）"""
        result = {
            "task_id": task_id,
            "success": False,
            "attempts": 0,
            "error": None,
            "recovered": False,
            "recovery_method": None,
            "result": None
        }
        
        last_error = None
        
        # 主执行尝试
        for attempt in range(self.config.max_retries):
            result["attempts"] = attempt + 1
            
            try:
                print(f"🚀 执行任务 {task_id} (尝试 {attempt + 1}/{self.config.max_retries})...")
                
                # 执行任务
                task_result = await task_func()
                
                result["success"] = True
                result["result"] = task_result
                result["error"] = None
                
                print(f"✅ 任务 {task_id} 执行成功")
                self._record_execution(result)
                return result
            
            except Exception as e:
                last_error = str(e)
                result["error"] = last_error
                
                print(f"⚠️  任务 {task_id} 执行失败：{e}")
                
                # 检查是否可重试
                if not self._is_retryable_error(e):
                    print(f"❌ 错误不可重试，跳过重试")
                    break
                
                # 准备重试
                if attempt < self.config.max_retries - 1:
                    delay = calculate_delay(attempt, self.config)
                    print(f"⏳ {delay:.1f}秒后重试...")
                    await asyncio.sleep(delay)
        
        # 所有重试失败，尝试降级方案
        if fallback_func and callable(fallback_func):
            print(f"⚙️  尝试降级方案...")
            try:
                fallback_result = await fallback_func()
                result["recovered"] = True
                result["recovery_method"] = "fallback"
                result["result"] = fallback_result
                result["success"] = True
                
                print(f"✅ 任务 {task_id} 通过降级方案恢复")
                self._record_execution(result)
                return result
            
            except Exception as fallback_error:
                print(f"❌ 降级方案也失败：{fallback_error}")
                result["error"] = f"{last_error}; 降级失败：{fallback_error}"
        
        # 彻底失败
        print(f"❌ 任务 {task_id} 彻底失败")
        self._record_execution(result)
        
        # 发送失败警报
        await self._send_failure_alert(result, context)
        
        return result
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """判断是否是可重试的错误"""
        retryable_types = [
            "TimeoutError",
            "ConnectionError",
            "ConnectionRefusedError",
            "ConnectionResetError",
            "OSError"
        ]
        
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # 类型判断
        if error_type in retryable_types:
            return True
        
        # 关键词判断
        retryable_keywords = [
            "timeout", "timed out",
            "connection",
            "network",
            "temporary",
            "transient"
        ]
        
        return any(kw in error_msg for kw in retryable_keywords)
    
    def _record_execution(self, result: Dict):
        """记录执行历史"""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            **result
        })
        
        # 限制历史记录数量
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    async def _send_failure_alert(self, result: Dict, context: Dict = None):
        """发送失败警报"""
        print(f"\n🚨 任务失败警报")
        print(f"   任务 ID: {result['task_id']}")
        print(f"   错误：{result['error']}")
        print(f"   尝试次数：{result['attempts']}")
        if context:
            print(f"   上下文：{json.dumps(context, ensure_ascii=False, indent=2)}")
        print(f"   建议：检查任务配置或联系管理员\n")
    
    def get_statistics(self) -> Dict:
        """获取执行统计"""
        if not self.execution_history:
            return {"total": 0}
        
        total = len(self.execution_history)
        success = sum(1 for e in self.execution_history if e["success"])
        recovered = sum(1 for e in self.execution_history if e.get("recovered"))
        
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "recovered": recovered,
            "success_rate": f"{success/total*100:.1f}%",
            "recovery_rate": f"{recovered/total*100:.1f}%" if total > 0 else "0%"
        }

# ==================== 全局实例 ====================

_git_push_manager: Optional[GitPushManager] = None
_self_healing_executor: Optional[SelfHealingExecutor] = None

def get_git_push_manager(repo_path: str = None) -> GitPushManager:
    """获取 Git 推送管理器实例"""
    global _git_push_manager
    if _git_push_manager is None:
        _git_push_manager = GitPushManager(repo_path)
    return _git_push_manager

def get_self_healing_executor() -> SelfHealingExecutor:
    """获取自愈执行器实例"""
    global _self_healing_executor
    if _self_healing_executor is None:
        _self_healing_executor = SelfHealingExecutor()
    return _self_healing_executor

# ==================== 测试入口 ====================

async def main():
    """测试入口"""
    print("=" * 60)
    print("🤖 灵犀自动重试和自愈系统测试")
    print("=" * 60)
    
    # 测试 Git 推送
    print("\n1️⃣ 测试 Git 推送（模拟）")
    git_manager = get_git_push_manager()
    
    # 模拟推送（实际应该调用真实的 git push）
    async def mock_git_push():
        # 这里模拟成功
        return {"success": True, "message": "推送成功"}
    
    # 测试自愈执行
    print("\n2️⃣ 测试自愈执行器")
    executor = get_self_healing_executor()
    
    # 成功任务
    async def success_task():
        return "任务完成"
    
    result = await executor.execute(
        task_id="test_success",
        task_func=success_task
    )
    print(f"   结果：{result}")
    
    # 失败任务（有降级方案）
    fail_count = [0]
    async def fail_task():
        fail_count[0] += 1
        if fail_count[0] < 3:
            raise ConnectionError("连接失败")
        return "终于成功了"
    
    async def fallback_task():
        return "降级方案执行"
    
    result = await executor.execute(
        task_id="test_fail_with_fallback",
        task_func=fail_task,
        fallback_func=fallback_task
    )
    print(f"   结果：{result}")
    
    # 显示统计
    print("\n3️⃣ 统计信息")
    print(f"   Git 推送：{json.dumps(git_manager.get_statistics(), indent=2, ensure_ascii=False)}")
    print(f"   任务执行：{json.dumps(executor.get_statistics(), indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
