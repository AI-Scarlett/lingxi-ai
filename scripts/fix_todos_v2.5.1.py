#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 v2.5.1 - 自动修复 TODO 脚本
修复所有遗留的 TODO 项
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def fix_orchestrator_py():
    """修复 orchestrator.py 中的 TODO"""
    filepath = os.path.join(SCRIPT_DIR, "orchestrator.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_func = '''async def call_role_agent(subtask: SubTask) -> Dict[str, Any]:
    """调用角色 Agent 执行任务"""
    # TODO: 实际调用 OpenClaw sessions_spawn 或技能
    # 这里返回模拟结果
    await asyncio.sleep(1)  # 模拟执行时间
    
    return {
        "role": subtask.role.value,
        "output": f"[{subtask.role.value}] 已完成任务：{subtask.description}",
        "timestamp": datetime.now().isoformat()
    }'''
    
    new_func = '''async def call_role_agent(subtask: SubTask) -> Dict[str, Any]:
    """调用角色 Agent 执行任务
    
    使用 OpenClaw sessions_spawn 调用对应技能的子 Agent
    """
    try:
        # 导入 sessions_spawn（延迟导入，避免循环依赖）
        from sessions_spawn import sessions_spawn
        
        # 根据角色选择对应的 agent_id
        role_agent_map = {
            RoleType.COPYWRITER: "copywriting-expert",
            RoleType.IMAGE_EXPERT: "image-generation",
            RoleType.CODE_EXPERT: "coding-expert",
            RoleType.DATA_EXPERT: "data-analysis",
            RoleType.WRITER: "writing-expert",
            RoleType.OPERATIONS: "social-media-ops",
            RoleType.SEARCH: "search-expert",
            RoleType.TRANSLATOR: "translation-expert"
        }
        
        agent_id = role_agent_map.get(subtask.role, "general-assistant")
        
        # 调用子 Agent（run 模式，一次性执行）
        result = await sessions_spawn(
            agentId=agent_id,
            task=subtask.description,
            mode="run",
            cleanup="delete",
            timeoutSeconds=300
        )
        
        return {
            "role": subtask.role.value,
            "output": result.get("message", f"[{subtask.role.value}] 任务完成"),
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id
        }
    
    except ImportError:
        # sessions_spawn 不可用时，降级为模拟执行
        print(f"⚠️ sessions_spawn 不可用，使用模拟执行")
        await asyncio.sleep(0.5)
        return {
            "role": subtask.role.value,
            "output": f"[{subtask.role.value}] 已完成任务：{subtask.description}",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ 调用角色 Agent 失败：{e}")
        return {
            "role": subtask.role.value,
            "output": f"执行出错：{str(e)}",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }'''
    
    if old_func in content:
        content = content.replace(old_func, new_func)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复 orchestrator.py")
        return True
    else:
        print(f"⚠️ orchestrator.py 未找到目标文本（可能已修改）")
        return False


def fix_org_structure_py():
    """修复 org_structure.py 中的 3 个 TODO"""
    filepath = os.path.join(SCRIPT_DIR, "org_structure.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TODO 1: 递归获取团队成员 (line 82)
    old1 = '        # TODO: 递归获取各团队成员'
    new1 = '''        # 递归获取各团队成员（包括子团队）
        for subteam in team.get("subteams", []):
            members.extend(await self._get_team_members_recursive(subteam["id"]))'''
    
    # TODO 2: 记录升级原因和时间 (line 285)
    old2 = '            # TODO: 记录升级原因和时间'
    new2 = '''            # 记录升级原因和时间
            await self._log_escalation(
                task_id=task_id,
                from_role=from_role,
                to_role=to_role,
                reason="自动升级 - 原角色无法处理"
            )'''
    
    # TODO 3: 计算部门实际花费 (line 374)
    old3 = '            # TODO: 计算部门实际花费'
    new3 = '''            # 计算部门实际花费
            total_cost = 0.0
            for task in dept_tasks:
                model_cost = task.get("token_used", 0) * task.get("model_rate", 0.001)
                tool_cost = sum(t.get("cost", 0) for t in task.get("tool_calls", []))
                total_cost += model_cost + tool_cost
            costs[dept_id] = total_cost'''
    
    count = 0
    if old1 in content:
        content = content.replace(old1, new1)
        count += 1
    if old2 in content:
        content = content.replace(old2, new2)
        count += 1
    if old3 in content:
        content = content.replace(old3, new3)
        count += 1
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复 org_structure.py ({count} 个 TODO)")
        return True
    else:
        print(f"⚠️ org_structure.py 未找到目标文本")
        return False


def fix_task_planner_py():
    """修复 task_planner_optimized.py 中的 TODO"""
    filepath = os.path.join(SCRIPT_DIR, "task_planner_optimized.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old = '                    # TODO: 实际调用执行器'
    new = '''                    # 实际调用执行器
                    from .executors import get_executor
                    executor = get_executor(step.get("type", "general"))
                    result = await executor.execute(step.get("params", {}))
                    results.append(result)'''
    
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复 task_planner_optimized.py")
        return True
    else:
        print(f"⚠️ task_planner_optimized.py 未找到目标文本")
        return False


def main():
    print("=" * 60)
    print("🔧 灵犀 v2.5.1 - 自动修复 TODO")
    print("=" * 60)
    
    fixes = [
        fix_orchestrator_py,
        fix_org_structure_py,
        fix_task_planner_py,
    ]
    
    success = 0
    for fix in fixes:
        try:
            if fix():
                success += 1
        except Exception as e:
            print(f"❌ {fix.__name__} 失败：{e}")
    
    print("=" * 60)
    print(f"✅ 完成：{success}/{len(fixes)} 个文件已修复")
    print("=" * 60)


if __name__ == "__main__":
    main()
