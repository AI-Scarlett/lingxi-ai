#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多机器人系统 - Multi-Agent System
让每个部门拥有独立的 AI 机器人，实现精准触达！

三种模式：
1. 部门专属机器人
2. 多身份账号系统  
3. 直接 @单个 AI 角色
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ContactMode(Enum):
    """联系方式模式"""
    DEPARTMENT_ROBOT = "dept_robot"      # 部门专属机器人
    MULTI_IDENTITY = "multi_identity"      # 多身份账号
    DIRECT_MENTION = "direct_mention"      # 直接 @AI

@dataclass
class RobotConfig:
    """机器人配置"""
    robot_id: str
    name: str                  # 机器人名称，如 "运营小助手"
    avatar: str                # 头像 URL
    description: str           # 功能描述
    department: str            # 所属部门
    roles: List[str]           # 有权限调用的角色
    platform: str              # 平台：wechat/qq/telegram/discord
    
    # 消息处理
    welcome_msg: str = ""
    keywords: List[str] = field(default_factory=list)  # 触发关键词
    
    # 权限
    max_concurrent: int = 3
    can_escalate: bool = True
    
    # 统计
    total_handled: int = 0
    avg_response_time: float = 0.0


class MultiAgentSystem:
    """多机器人系统 💋"""
    
    def __init__(self, org_system):
        self.org = org_system
        self.robots: Dict[str, RobotConfig] = {}
        self.identity_map: Dict[str, str] = {}  # user_id -> robot_id
        self.direct_mention_prefix = "@"
    
    def register_department_robot(self, dept_id: str, 
                                   robot_name: str,
                                   platform: str = "wechat") -> RobotConfig:
        """
        注册部门专属机器人
        
        Args:
            dept_id: 部门 ID（如 "marketing_dept"）
            robot_name: 机器人名称（如 "市场运营小助手"）
            platform: 平台类型
        
        Returns:
            RobotConfig 实例
        """
        dept = self.org.departments.get(dept_id)
        if not dept:
            raise ValueError(f"部门不存在：{dept_id}")
        
        # 获取部门下所有角色
        dept_roles = []
        for team_id in dept.teams:
            team = self.org.teams.get(team_id)
            if team:
                dept_roles.extend(team.roles)
        
        robot_id = f"robot_{dept_id}"
        
        robot = RobotConfig(
            robot_id=robot_id,
            name=robot_name,
            avatar=f"https://example.com/avatars/{robot_id}.png",
            description=f"🎯 {dept.name}专属助手，负责 {dept.mission}",
            department=dept_id,
            roles=dept_roles,
            platform=platform,
            welcome_msg=f"你好！我是{robot_name}，专门帮你处理{dept.name}的所有事务~"
        )
        
        self.robots[robot_id] = robot
        return robot
    
    def register_multi_identity(self, user_id: str, 
                                  robot_id: str,
                                  identity_name: str = None) -> str:
        """
        注册多身份账号
        同一用户可以切换不同身份来触达不同部门
        
        Args:
            user_id: 用户在平台上的唯一 ID
            robot_id: 要绑定的机器人 ID
            identity_name: 自定义身份名称
        
        Returns:
            身份令牌
        """
        identity = f"{user_id}_{robot_id}"
        self.identity_map[identity] = robot_id
        
        # 记录用户的身份
        if not hasattr(self, '_user_identities'):
            self._user_identities = {}
        
        self._user_identities[user_id] = {
            'robot_id': robot_id,
            'identity_name': identity_name or robot_id,
            'bound_at': datetime.now()
        }
        
        return identity
    
    def handle_message(self, message: str, 
                       sender_id: str = None,
                       contact_mode: ContactMode = ContactMode.DIRECT_MENTION,
                       platform: str = "wechat") -> Dict:
        """
        处理消息的核心方法
        
        Args:
            message: 用户消息内容
            sender_id: 发送者 ID
            contact_mode: 联系方式模式
            platform: 平台类型
        
        Returns:
            处理结果字典
        """
        result = {
            "status": "success",
            "response": "",
            "handled_by": None,
            "escalated": False,
            "metadata": {}
        }
        
        # 解析消息
        if contact_mode == ContactMode.DIRECT_MENTION:
            # 模式 3：直接 @某个 AI 角色
            result = self._handle_direct_mention(message, sender_id)
            
        elif contact_mode == ContactMode.DEPARTMENT_ROBOT:
            # 模式 1：部门专属机器人
            result = self._handle_dept_robot(message, sender_id, platform)
            
        elif contact_mode == ContactMode.MULTI_IDENTITY:
            # 模式 2：多身份账号
            result = self._handle_multi_identity(message, sender_id)
        
        return result
    
    def _handle_direct_mention(self, message: str, sender_id: str) -> Dict:
        """直接 @单个 AI 角色"""
        # 解析 @提及的角色名
        mentioned_role = self._parse_mention(message)
        
        if not mentioned_role:
            return {
                "status": "error",
                "response": "没有检测到 @的目标角色，请使用 @角色名 的格式~",
                "handled_by": None
            }
        
        # 查找角色
        role = self.org.roles.get(mentioned_role)
        if not role:
            # 模糊匹配
            matched = self._fuzzy_match_role(mentioned_role)
            if matched:
                role = self.org.roles.get(matched)
            else:
                return {
                    "status": "error",
                    "response": f"找不到角色：{mentioned_role}，可以用 @运营部 试试~",
                    "handled_by": None
                }
        
        # 执行任务
        task = self.org.route_task(message, priority="P3")
        task.assigned_to = role.name
        
        return {
            "status": "success",
            "response": f"✅ 已将任务交给 {role.job_title} ({role.name}) 处理！",
            "handled_by": role.name,
            "role": {
                "name": role.name,
                "job_title": role.job_title,
                "model": role.model_name
            }
        }
    
    def _handle_dept_robot(self, message: str, sender_id: str, 
                           platform: str) -> Dict:
        """部门专属机器人处理"""
        # 查找对应的机器人
        robot = self._find_robot_by_platform(platform)
        
        if not robot:
            return {
                "status": "error",
                "response": "当前平台没有配置部门机器人~"
            }
        
        # 根据消息关键词智能分配
        target_role = self._smart_assign(robot.roles, message)
        
        return {
            "status": "success",
            "response": f"📋 已将任务转交给 {target_role.job_title}...",
            "handled_by": target_role.name,
            "robot": robot.name,
            "suggested_role": target_role.name
        }
    
    def _handle_multi_identity(self, message: str, sender_id: str) -> Dict:
        """多身份账号处理"""
        identity_key = f"{sender_id}_current"  # 当前身份
        
        # 获取用户当前绑定的身份
        user_info = self._user_identities.get(sender_id, {})
        robot_id = user_info.get('robot_id')
        
        if not robot_id or robot_id not in self.robots:
            return {
                "status": "error",
                "response": "你还没有绑定身份，请先绑定一个部门助手~",
                "action": "show_bind_menu"
            }
        
        robot = self.robots[robot_id]
        
        # 智能分配任务
        target_role = self._smart_assign(robot.roles, message)
        
        return {
            "status": "success",
            "response": f"🎯 [{user_info.get('identity_name')}] 已接单：{target_role.job_title}",
            "handled_by": target_role.name,
            "identity": user_info.get('identity_name')
        }
    
    def _parse_mention(self, message: str) -> Optional[str]:
        """解析 @提及"""
        if self.direct_mention_prefix in message:
            # 提取 @后面的内容
            parts = message.split(self.direct_mention_prefix)
            if len(parts) > 1:
                mentioned = parts[1].split()[0]  # 取第一个词
                return mentioned
        return None
    
    def _fuzzy_match_role(self, keyword: str) -> Optional[str]:
        """模糊匹配角色名"""
        keyword_lower = keyword.lower()
        
        for role_name, role in self.org.roles.items():
            # 检查角色名、职位、标签
            if (keyword_lower in role_name.lower() or 
                keyword_lower in role.job_title.lower() or
                any(keyword_lower in tag.lower() for tag in role.skills)):
                return role_name
        
        return None
    
    def _find_robot_by_platform(self, platform: str) -> Optional[RobotConfig]:
        """根据平台找到对应的机器人"""
        for robot in self.robots.values():
            if robot.platform == platform:
                return robot
        return None
    
    def _smart_assign(self, available_roles: List[str], 
                      message: str) -> 'RoleConfig':
        """智能分配任务到最合适的角色"""
        # 计算每个角色的匹配度
        best_role = None
        best_score = 0
        
        for role_name in available_roles:
            role = self.org.roles.get(role_name)
            if not role:
                continue
            
            score = 0
            # 技能匹配
            for skill in role.skills:
                if skill in message:
                    score += 3
            # 职位关键词匹配
            if any(kw in message for kw in role.job_title):
                score += 5
            
            if score > best_score:
                best_score = score
                best_role = role
        
        # 兜底：返回第一个可用角色
        if not best_role and available_roles:
            role_name = available_roles[0]
            best_role = self.org.roles.get(role_name)
        
        return best_role
    
    def get_robot_info(self, platform: str = "wechat") -> List[Dict]:
        """获取所有机器人的详细信息"""
        robots = []
        
        for robot in self.robots.values():
            if platform and robot.platform != platform:
                continue
            
            robots.append({
                "id": robot.robot_id,
                "name": robot.name,
                "description": robot.description,
                "department": robot.department,
                "welcome_msg": robot.welcome_msg,
                "keywords": robot.keywords,
                "stats": {
                    "total_handled": robot.total_handled,
                    "avg_response_time": robot.avg_response_time
                }
            })
        
        return robots
    
    def create_bind_keyboard(self, platform: str = "wechat") -> str:
        """生成绑定键盘（按钮）"""
        buttons = []
        
        for robot in self.robots.values():
            if platform and robot.platform != platform:
                continue
            
            buttons.append({
                "text": f"绑定 {robot.name}",
                "command": f"/bind {robot.robot_id}"
            })
        
        return buttons


# ==================== 使用示例 ====================

def demo():
    """演示多机器人系统"""
    
    # 假设已经有 org 系统
    from org_structure import create_sample_company
    
    org = create_sample_company()
    multi_agent = MultiAgentSystem(org)
    
    print("=" * 60)
    print("🎭 多机器人系统演示")
    print("=" * 60)
    
    # 注册部门专属机器人
    robot1 = multi_agent.register_department_robot(
        dept_id="marketing_dept",
        robot_name="市场运营小助手",
        platform="wechat"
    )
    print(f"\n✅ 注册机器人：{robot1.name}")
    print(f"   所属部门：{robot1.department}")
    print(f"   可用角色：{', '.join(robot1.roles)}")
    
    robot2 = multi_agent.register_department_robot(
        dept_id="tech_dept",
        robot_name="技术大牛助手",
        platform="wechat"
    )
    print(f"\n✅ 注册机器人：{robot2.name}")
    
    # 演示：直接 @某个角色
    print("\n" + "=" * 60)
    print("🎯 模式 1: 直接 @单个 AI 角色")
    print("=" * 60)
    
    result = multi_agent.handle_message(
        "@copywriter 帮我写个小红书文案",
        sender_id="user_001",
        contact_mode=ContactMode.DIRECT_MENTION
    )
    print(f"输入：@copywriter 帮我写个小红书文案")
    print(f"输出：{result['response']}")
    print(f"处理者：{result['handled_by']}")
    
    # 演示：多身份账号
    print("\n" + "=" * 60)
    print("🎭 模式 2: 多身份账号系统")
    print("=" * 60)
    
    # 用户绑定身份
    identity = multi_agent.register_multi_identity(
        user_id="wechat_user_888",
        robot_id="robot_marketing_dept",
        identity_name="市场部小王"
    )
    print(f"用户绑定身份：{identity}")
    
    # 用户发送消息
    result = multi_agent.handle_message(
        "帮我分析上个月的销售数据",
        sender_id="wechat_user_888",
        contact_mode=ContactMode.MULTI_IDENTITY
    )
    print(f"输入：帮我分析上个月的销售数据")
    print(f"输出：{result['response']}")
    print(f"身份：{result.get('identity')}")
    
    # 演示：获取机器人列表
    print("\n" + "=" * 60)
    print("📋 可用机器人列表")
    print("=" * 60)
    
    robots = multi_agent.get_robot_info(platform="wechat")
    for r in robots:
        print(f"\n🤖 {r['name']}")
        print(f"   描述：{r['description']}")
        print(f"   欢迎语：{r['welcome_msg']}")
        print(f"   已处理任务：{r['stats']['total_handled']}")


if __name__ == "__main__":
    demo()