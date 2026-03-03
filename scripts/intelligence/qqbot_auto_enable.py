#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Bot 自动启用优化 - QQ Bot Auto-Enable
解决 QQ Bot 默认不启用的问题 💋

功能：
- 自动检测 QQ Bot 安装
- 自动启用 QQ Bot 集成
- 检查依赖项
- 一键修复配置
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class EnableResult:
    """启用结果"""
    success: bool
    qqbot_detected: bool
    qqbot_enabled: bool
    config_updated: bool
    issues: List[str]
    fixes: List[str]


class QQBotAutoEnable:
    """QQ Bot 自动启用器"""
    
    def __init__(self, 
                 workspace_path: str = "~/.openclaw/workspace/",
                 skills_path: str = "~/.openclaw/skills/"):
        self.workspace_path = Path(workspace_path).expanduser()
        self.skills_path = Path(skills_path).expanduser()
        self.lingxi_path = self.skills_path / "lingxi"
        self.config_path = self.workspace_path / "lingxi-config.json"
        self.qqbot_bridge = self.lingxi_path / "scripts" / "qqbot_bridge.py"
    
    def detect_qqbot(self) -> bool:
        """检测 QQ Bot 是否安装"""
        # 检查 QQ Bot 技能目录
        qqbot_paths = [
            self.skills_path / "qqbot",
            self.skills_path / "lingxi" / "qqbot",
        ]
        
        for path in qqbot_paths:
            if path.exists():
                return True
        
        # 检查 QQ Bot 桥接脚本
        if self.qqbot_bridge.exists():
            return True
        
        return False
    
    def check_qqbot_integration(self) -> Dict[str, Any]:
        """检查 QQ Bot 集成状态"""
        status = {
            "qqbot_installed": self.detect_qqbot(),
            "bridge_exists": self.qqbot_bridge.exists(),
            "config_exists": self.config_path.exists(),
            "qqbot_enabled": False,
            "issues": []
        }
        
        # 检查配置
        if status["config_exists"]:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "qqbot" in config:
                    status["qqbot_enabled"] = config["qqbot"].get("enabled", False)
        
        # 检查问题
        if not status["qqbot_installed"]:
            status["issues"].append("QQ Bot 未安装")
        
        if not status["bridge_exists"]:
            status["issues"].append("QQ Bot 桥接脚本不存在")
        
        if status["config_exists"] and not status["qqbot_enabled"]:
            status["issues"].append("QQ Bot 在配置中未启用")
        
        return status
    
    def enable_qqbot(self) -> EnableResult:
        """
        启用 QQ Bot 集成
        
        Returns:
            启用结果
        """
        issues = []
        fixes = []
        
        # 1. 检测 QQ Bot
        qqbot_detected = self.detect_qqbot()
        
        if not qqbot_detected:
            issues.append("QQ Bot 未安装，请先安装 QQ Bot 技能")
            return EnableResult(
                success=False,
                qqbot_detected=False,
                qqbot_enabled=False,
                config_updated=False,
                issues=issues,
                fixes=fixes
            )
        
        # 2. 检查桥接脚本
        if not self.qqbot_bridge.exists():
            issues.append("QQ Bot 桥接脚本不存在")
            fixes.append("创建 QQ Bot 桥接脚本")
            self._create_qqbot_bridge()
        
        # 3. 更新配置
        config_updated = self._update_qqbot_config()
        
        if config_updated:
            fixes.append("已更新配置文件，启用 QQ Bot 集成")
        
        # 4. 检查结果
        qqbot_enabled = config_updated
        
        return EnableResult(
            success=qqbot_enabled,
            qqbot_detected=qqbot_detected,
            qqbot_enabled=qqbot_enabled,
            config_updated=config_updated,
            issues=issues,
            fixes=fixes
        )
    
    def _update_qqbot_config(self) -> bool:
        """更新 QQ Bot 配置"""
        # 加载或创建配置
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {"_version": "v2.3.0"}
        
        # 确保 QQ Bot 配置存在并启用
        if "qqbot" not in config:
            config["qqbot"] = {}
        
        config["qqbot"]["enabled"] = True
        config["qqbot"]["auto_enable"] = True
        config["qqbot"]["integration_check"] = True
        config["qqbot"]["auto_detect_tasks"] = True
        config["qqbot"]["instant_keywords"] = [
            "天气", "搜索", "翻译", "几点了", "时间", "查询"
        ]
        config["qqbot"]["background_keywords"] = [
            "发布", "生成", "创作", "写", "做图", "开发"
        ]
        
        # 保存配置
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    
    def _create_qqbot_bridge(self):
        """创建 QQ Bot 桥接脚本（如果不存在）"""
        bridge_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Bot 桥接器 - 自动生成的桥接脚本
用于灵犀和 QQ Bot 之间的通信
"""

import sys
import json
from pathlib import Path

# 添加灵犀路径
lingxi_path = Path(__file__).parent.parent
sys.path.insert(0, str(lingxi_path))

from intelligence import IntelligenceEngine

def handle_qq_message(message: dict):
    """处理 QQ 消息"""
    engine = IntelligenceEngine()
    
    user_id = message.get("user_id", "unknown")
    input_text = message.get("text", "")
    
    # 记录任务
    task_id = engine.log_task(
        task_type="chat",
        user_id=user_id,
        input_text=input_text,
        output_text="",
        model_used="qwen-plus",
        token_cost=0,
        duration_ms=0,
        success=True
    )
    
    # 获取优化建议
    optimization = engine.get_optimization("chat", input_text)
    
    return {
        "task_id": task_id,
        "optimization": optimization
    }

if __name__ == "__main__":
    # 测试
    result = handle_qq_message({
        "user_id": "test",
        "text": "你好"
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
'''
        
        with open(self.qqbot_bridge, "w", encoding="utf-8") as f:
            f.write(bridge_content)
        
        # 设置执行权限
        os.chmod(self.qqbot_bridge, 0o755)
    
    def get_status_report(self) -> str:
        """获取状态报告"""
        status = self.check_qqbot_integration()
        
        report = []
        report.append("🤖 QQ Bot 集成状态\n")
        report.append("=" * 50 + "\n")
        
        # 状态
        report.append(f"QQ Bot 安装：{'✅' if status['qqbot_installed'] else '❌'}\n")
        report.append(f"桥接脚本：{'✅' if status['bridge_exists'] else '❌'}\n")
        report.append(f"配置文件：{'✅' if status['config_exists'] else '❌'}\n")
        report.append(f"QQ Bot 启用：{'✅' if status['qqbot_enabled'] else '❌'}\n")
        
        # 问题
        if status["issues"]:
            report.append(f"\n⚠️ 问题:\n")
            for issue in status["issues"]:
                report.append(f"   • {issue}\n")
        else:
            report.append(f"\n✅ 无问题\n")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)


# 全局单例
_auto_enable = None

def get_auto_enable() -> QQBotAutoEnable:
    """获取全局 QQ Bot 自动启用器实例"""
    global _auto_enable
    if _auto_enable is None:
        _auto_enable = QQBotAutoEnable()
    return _auto_enable


# 使用示例
if __name__ == "__main__":
    auto_enable = QQBotAutoEnable()
    
    # 获取状态报告
    report = auto_enable.get_status_report()
    print(report)
    
    # 启用 QQ Bot
    print("\n🔧 启用 QQ Bot 集成...")
    result = auto_enable.enable_qqbot()
    
    print(f"\n{'✅' if result.success else '❌'} 操作完成:")
    print(f"   QQ Bot 检测：{'✅' if result.qqbot_detected else '❌'}")
    print(f"   QQ Bot 启用：{'✅' if result.qqbot_enabled else '❌'}")
    print(f"   配置更新：{'✅' if result.config_updated else '❌'}")
    
    if result.fixes:
        print(f"\n🔧 已修复:")
        for fix in result.fixes:
            print(f"   • {fix}")
    
    if result.issues:
        print(f"\n⚠️ 问题:")
        for issue in result.issues:
            print(f"   • {issue}")
