#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 v1.3.0 性能基准测试
测试企业架构系统的响应速度、路由准确率、并发能力 💋
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict
import sys
sys.path.insert(0, '/app/working/active_skills/smart-orchestrator/scripts')

from org_structure import AIEnterprise, create_sample_company, TaskPriority

class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self):
        self.results = []
        self.enterprise = create_sample_company()
    
    def test_task_routing_speed(self, iterations: int = 100) -> Dict:
        """测试任务路由速度"""
        print(f"\n🚀 测试 1: 任务路由速度 ({iterations} 次)")
        print("="*60)
        
        test_tasks = [
            ("帮我写个小红书美妆推广文案", TaskPriority.P2),
            ("制定明年 Q1 的市场战略", TaskPriority.P1),
            ("修复支付系统的 bug", TaskPriority.P0),
            ("优化官网 SEO 排名", TaskPriority.P3),
            ("分析上个月销售数据", TaskPriority.P2),
            ("招聘 3 个前端工程师", TaskPriority.P1),
            ("设计新 logo", TaskPriority.P3),
            ("客户投诉处理", TaskPriority.P0),
        ]
        
        times = []
        
        for i in range(iterations):
            task_desc, priority = test_tasks[i % len(test_tasks)]
            
            start = time.perf_counter()
            task = self.enterprise.route_task(task_desc, priority)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            
            times.append(elapsed)
        
        # 统计
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        result = {
            "test_name": "任务路由速度",
            "iterations": iterations,
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "p95_ms": p95_time,
            "tasks_per_second": 1000 / avg_time if avg_time > 0 else 0
        }
        
        self.results.append(result)
        
        # 输出报告
        print(f"  ⏱️  平均耗时：{avg_time:.2f}ms")
        print(f"  📊 最快：{min_time:.2f}ms")
        print(f"  📊 最慢：{max_time:.2f}ms")
        print(f"  📊 P95: {p95_time:.2f}ms")
        print(f"  🚀 吞吐量：{result['tasks_per_second']:.1f} 任务/秒")
        
        return result
    
    def test_routing_accuracy(self) -> Dict:
        """测试路由准确率"""
        print(f"\n🎯 测试 2: 路由准确率")
        print("="*60)
        
        # 预期路由结果（允许路由到部门总监或具体专员）
        test_cases = [
            ("帮我写个小红书美妆推广文案", TaskPriority.P2, ["marketing_director", "copywriter_senior", "social_manager"]),
            ("制定明年 Q1 的市场战略", TaskPriority.P1, ["ceo_ai", "marketing_director"]),
            ("修复支付系统的 bug", TaskPriority.P0, ["ceo_ai", "tech_cto"]),
            ("优化官网 SEO 排名", TaskPriority.P3, ["seo_specialist", "marketing_director"]),  # P3 可能到部门或直接到专员
            ("开发新功能模块", TaskPriority.P2, ["tech_cto", "senior_developer"]),
            ("写产品说明书", TaskPriority.P3, ["copywriter_senior", "marketing_director"]),  # P3 可能到部门或直接到专员
        ]
        
        correct = 0
        total = len(test_cases)
        
        for task_desc, priority, expected_roles in test_cases:
            task = self.enterprise.route_task(task_desc, priority)
            assigned = task.assigned_to
            
            is_correct = assigned in expected_roles
            if is_correct:
                correct += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"  {status} '{task_desc[:25]}...' → {assigned}")
            if not is_correct:
                print(f"      预期：{expected_roles}")
        
        accuracy = correct / total * 100
        
        result = {
            "test_name": "路由准确率",
            "total_cases": total,
            "correct": correct,
            "accuracy": accuracy
        }
        
        self.results.append(result)
        
        print(f"\n  📊 准确率：{accuracy:.1f}% ({correct}/{total})")
        
        return result
    
    async def test_concurrent_tasks(self, concurrent_count: int = 50) -> Dict:
        """测试并发任务处理"""
        print(f"\n🔥 测试 3: 并发任务处理 ({concurrent_count} 个并发)")
        print("="*60)
        
        async def process_task(task_id: int):
            task_desc = f"处理任务 {task_id}"
            start = time.perf_counter()
            task = self.enterprise.route_task(task_desc, TaskPriority.P3)
            elapsed = (time.perf_counter() - start) * 1000
            return elapsed
        
        start_time = time.perf_counter()
        
        # 创建并发任务
        tasks = [process_task(i) for i in range(concurrent_count)]
        results = await asyncio.gather(*tasks)
        
        total_time = (time.perf_counter() - start_time) * 1000
        avg_time = sum(results) / len(results)
        
        result = {
            "test_name": "并发任务处理",
            "concurrent_count": concurrent_count,
            "total_time_ms": total_time,
            "avg_time_ms": avg_time,
            "tasks_per_second": concurrent_count / (total_time / 1000)
        }
        
        self.results.append(result)
        
        print(f"  ⏱️  总耗时：{total_time:.2f}ms")
        print(f"  📊 平均每个任务：{avg_time:.2f}ms")
        print(f"  🚀 吞吐量：{result['tasks_per_second']:.1f} 任务/秒")
        
        return result
    
    def test_budget_tracking(self) -> Dict:
        """测试预算跟踪"""
        print(f"\n💰 测试 4: 预算跟踪")
        print("="*60)
        
        # 模拟完成任务并记录成本
        test_scenarios = [
            ("写文案", "copywriter_senior", 0.5),
            ("做 SEO 分析", "seo_specialist", 0.3),
            ("发社交媒体", "social_manager", 0.8),
            ("开发功能", "senior_developer", 1.2),
            ("CEO 决策", "ceo_ai", 2.5),
        ]
        
        total_cost = 0
        
        for desc, role_name, cost in test_scenarios:
            role = self.enterprise.roles.get(role_name)
            if role:
                # 模拟完成任务
                task = self.enterprise.route_task(desc, TaskPriority.P3)
                self.enterprise.complete_task(task, score=9.0, cost=cost)
                total_cost += cost
                print(f"  ✅ {desc}: ¥{cost:.2f} (角色：{role_name})")
        
        # 生成报告
        report = self.enterprise.get_performance_report()
        
        result = {
            "test_name": "预算跟踪",
            "total_cost": total_cost,
            "tasks_completed": self.enterprise.stats["completed_tasks"],
            "budget_remaining": self.enterprise.company.annual_budget - total_cost
        }
        
        self.results.append(result)
        
        print(f"\n  💰 总花费：¥{total_cost:.2f}")
        print(f"  📊 完成任务：{result['tasks_completed']} 个")
        print(f"  📊 预算剩余：¥{result['budget_remaining']:.2f}")
        
        return result
    
    def test_escalation_flow(self) -> Dict:
        """测试升级流程"""
        print(f"\n⚠️  测试 5: 任务升级流程")
        print("="*60)
        
        # 创建任务并模拟升级
        task = self.enterprise.route_task("复杂战略规划", TaskPriority.P2)
        print(f"  📋 初始分配：{task.assigned_to}")
        
        # 模拟无法处理，触发升级
        self.enterprise.escalate_task(task, "超出能力范围")
        print(f"  ⚠️  第一次升级：{task.assigned_to}")
        
        # 再次升级
        role = self.enterprise.roles.get(task.assigned_to)
        if role and role.escalation_to:
            self.enterprise.escalate_task(task, "需要更高级决策")
            print(f"  ⚠️  第二次升级：{task.assigned_to}")
        
        result = {
            "test_name": "升级流程",
            "final_assignee": task.assigned_to,
            "escalation_count": task.status.count("escalated") + 1 if "escalated" in task.status else 0
        }
        
        self.results.append(result)
        
        print(f"  📊 最终处理人：{task.assigned_to}")
        print(f"  📊 升级次数：{result['escalation_count']}")
        
        return result
    
    def generate_summary_report(self) -> str:
        """生成总结报告"""
        print("\n" + "="*60)
        print("📊 性能测试总结报告")
        print("="*60)
        
        lines = [
            f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"测试项目：{len(self.results)} 个",
            ""
        ]
        
        for result in self.results:
            test_name = result.get("test_name", "未知测试")
            lines.append(f"✅ {test_name}:")
            
            if "avg_ms" in result:
                lines.append(f"   ├─ 平均耗时：{result['avg_ms']:.2f}ms")
                lines.append(f"   └─ 吞吐量：{result.get('tasks_per_second', 0):.1f} 任务/秒")
            
            if "accuracy" in result:
                lines.append(f"   └─ 准确率：{result['accuracy']:.1f}%")
            
            if "total_cost" in result:
                lines.append(f"   ├─ 总花费：¥{result['total_cost']:.2f}")
                lines.append(f"   └─ 完成任务：{result['tasks_completed']} 个")
            
            lines.append("")
        
        # 性能评级
        lines.append("🏆 性能评级:")
        
        # 根据路由速度评级
        routing_test = next((r for r in self.results if r["test_name"] == "任务路由速度"), None)
        if routing_test:
            avg_ms = routing_test["avg_ms"]
            if avg_ms < 1:
                rating = "🌟🌟🌟🌟🌟 卓越 (<1ms)"
            elif avg_ms < 5:
                rating = "🌟🌟🌟🌟 优秀 (<5ms)"
            elif avg_ms < 10:
                rating = "🌟🌟🌟 良好 (<10ms)"
            else:
                rating = "🌟🌟 需改进 (>10ms)"
            
            lines.append(f"   路由速度：{rating}")
        
        # 根据准确率评级
        accuracy_test = next((r for r in self.results if r["test_name"] == "路由准确率"), None)
        if accuracy_test:
            acc = accuracy_test["accuracy"]
            if acc >= 95:
                rating = "🌟🌟🌟🌟🌟 卓越 (≥95%)"
            elif acc >= 85:
                rating = "🌟🌟🌟🌟 优秀 (≥85%)"
            elif acc >= 75:
                rating = "🌟🌟🌟 良好 (≥75%)"
            else:
                rating = "🌟🌟 需改进 (<75%)"
            
            lines.append(f"   路由准确率：{rating}")
        
        lines.append("")
        lines.append("="*60)
        
        report = "\n".join(lines)
        print(report)
        
        return report


async def run_full_benchmark():
    """运行完整基准测试"""
    print("="*60)
    print("🚀 灵犀 v1.3.0 企业架构性能测试")
    print("="*60)
    print(f"测试开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    benchmark = PerformanceBenchmark()
    
    # 运行所有测试
    benchmark.test_task_routing_speed(iterations=100)
    benchmark.test_routing_accuracy()
    await benchmark.test_concurrent_tasks(concurrent_count=50)
    benchmark.test_budget_tracking()
    benchmark.test_escalation_flow()
    
    # 生成总结
    benchmark.generate_summary_report()
    
    return benchmark.results


if __name__ == "__main__":
    asyncio.run(run_full_benchmark())
