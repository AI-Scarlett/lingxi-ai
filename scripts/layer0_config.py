#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - Layer 0 自定义配置系统

功能:
1. 用户自定义快速响应规则
2. 支持 JSON 配置文件
3. 支持动态添加/删除规则
4. 规则导入导出
5. 优先级自定义

使用方式:
    from layer0_config import Layer0Config
    
    config = Layer0Config()
    
    # 添加自定义规则
    config.add_rule(patterns=["自定义问候"], response="我的自定义回复～")
    
    # 删除规则
    config.remove_rule("自定义问候")
    
    # 查看所有规则
    rules = config.get_all_rules()
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict

# ==================== 配置 ====================

CONFIG_FILE = Path.home() / ".openclaw" / "workspace" / ".learnings" / "layer0_custom_rules.json"
BACKUP_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings" / "backups"

# ==================== 数据结构 ====================

@dataclass
class CustomRule:
    """自定义规则"""
    id: str
    patterns: List[str]
    response: Any  # str or callable
    priority: int = 0
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    hit_count: int = 0
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "patterns": self.patterns,
            "response": self.response if not callable(self.response) else "<callable>",
            "priority": self.priority,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "hit_count": self.hit_count,
            "description": self.description
        }

# ==================== 配置管理器 ====================

class Layer0Config:
    """Layer 0 配置管理器"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.backup_dir = BACKUP_DIR
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.rules = self._load_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "rules": {},
            "settings": {
                "enable_custom_rules": True,
                "max_rules": 1000,
                "case_sensitive": False
            }
        }
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding='utf-8'))
                # 转换回 CustomRule 对象
                rules = {}
                for rule_id, rule_data in data.get("rules", {}).items():
                    rules[rule_id] = CustomRule(**rule_data)
                return rules
            except Exception as e:
                print(f"⚠️  加载配置失败：{e}，使用默认配置")
        return {}
    
    def _save_config(self):
        """保存配置"""
        # 备份旧配置
        if self.config_file.exists():
            backup_path = self.backup_dir / f"layer0_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path.write_text(self.config_file.read_text(encoding='utf-8'), encoding='utf-8')
        
        # 保存新配置
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
            "settings": {
                "enable_custom_rules": True,
                "max_rules": 1000,
                "case_sensitive": False
            }
        }
        
        self.config_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def add_rule(self, patterns: List[str], response: str, priority: int = 0, description: str = "") -> str:
        """添加自定义规则"""
        rule_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.rules)}"
        
        rule = CustomRule(
            id=rule_id,
            patterns=patterns,
            response=response,
            priority=priority,
            description=description
        )
        
        self.rules[rule_id] = rule
        self._save_config()
        
        print(f"✅ 规则已添加：{rule_id}")
        return rule_id
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_config()
            print(f"✅ 规则已删除：{rule_id}")
            return True
        print(f"⚠️  规则不存在：{rule_id}")
        return False
    
    def update_rule(self, rule_id: str, patterns: List[str] = None, response: str = None, priority: int = None) -> bool:
        """更新规则"""
        if rule_id not in self.rules:
            print(f"⚠️  规则不存在：{rule_id}")
            return False
        
        rule = self.rules[rule_id]
        if patterns:
            rule.patterns = patterns
        if response:
            rule.response = response
        if priority is not None:
            rule.priority = priority
        rule.updated_at = datetime.now().isoformat()
        
        self._save_config()
        print(f"✅ 规则已更新：{rule_id}")
        return True
    
    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            self.rules[rule_id].updated_at = datetime.now().isoformat()
            self._save_config()
            print(f"✅ 规则已启用：{rule_id}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            self.rules[rule_id].updated_at = datetime.now().isoformat()
            self._save_config()
            print(f"✅ 规则已禁用：{rule_id}")
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[CustomRule]:
        """获取规则"""
        return self.rules.get(rule_id)
    
    def get_all_rules(self, include_disabled: bool = True) -> List[CustomRule]:
        """获取所有规则"""
        rules = list(self.rules.values())
        if not include_disabled:
            rules = [r for r in rules if r.enabled]
        return sorted(rules, key=lambda x: x.priority, reverse=True)
    
    def export_rules(self, output_file: str) -> bool:
        """导出规则到文件"""
        try:
            data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "rules": [r.to_dict() for r in self.get_all_rules()]
            }
            
            Path(output_file).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"✅ 规则已导出：{output_file}")
            return True
        except Exception as e:
            print(f"❌ 导出失败：{e}")
            return False
    
    def import_rules(self, input_file: str, merge: bool = True) -> int:
        """从文件导入规则"""
        try:
            data = json.loads(Path(input_file).read_text(encoding='utf-8'))
            imported = 0
            
            for rule_data in data.get("rules", []):
                rule_id = rule_data.get("id", f"imported_{imported}")
                
                if merge and rule_id in self.rules:
                    # 合并模式：更新现有规则
                    self.update_rule(
                        rule_id,
                        patterns=rule_data.get("patterns"),
                        response=rule_data.get("response"),
                        priority=rule_data.get("priority")
                    )
                else:
                    # 新增模式：添加新规则
                    rule = CustomRule(**rule_data)
                    rule.id = rule_id
                    self.rules[rule_id] = rule
                
                imported += 1
            
            self._save_config()
            print(f"✅ 导入了 {imported} 条规则")
            return imported
        except Exception as e:
            print(f"❌ 导入失败：{e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        rules = list(self.rules.values())
        enabled = [r for r in rules if r.enabled]
        disabled = [r for r in rules if not r.enabled]
        total_hits = sum(r.hit_count for r in rules)
        
        return {
            "total_rules": len(rules),
            "enabled_rules": len(enabled),
            "disabled_rules": len(disabled),
            "total_hits": total_hits,
            "avg_hits_per_rule": total_hits / len(rules) if rules else 0
        }
    
    def clear_all_rules(self, confirm: bool = False) -> bool:
        """清空所有规则"""
        if not confirm:
            print("⚠️  请使用 clear_all_rules(confirm=True) 确认清空")
            return False
        
        self.rules = {}
        self._save_config()
        print("✅ 所有规则已清空")
        return True

# ==================== 集成到快速响应层 ====================

def load_custom_rules() -> List[CustomRule]:
    """加载自定义规则（供 fast_response_layer_v2.py 调用）"""
    config = Layer0Config()
    return config.get_all_rules(include_disabled=False)

def match_custom_rules(user_input: str) -> tuple:
    """匹配自定义规则（供 fast_response_layer_v2.py 调用）"""
    config = Layer0Config()
    rules = config.get_all_rules(include_disabled=False)
    
    # 按优先级排序
    sorted_rules = sorted(rules, key=lambda x: x.priority, reverse=True)
    
    for rule in sorted_rules:
        for pattern in rule.patterns:
            if pattern in user_input:
                # 命中规则，增加计数
                rule.hit_count += 1
                config._save_config()
                
                # 返回响应
                if callable(rule.response):
                    return True, rule.response()
                return True, rule.response
    
    return False, None

# ==================== 全局实例 ====================

_config: Optional[Layer0Config] = None

def get_layer0_config() -> Layer0Config:
    """获取全局实例"""
    global _config
    if _config is None:
        _config = Layer0Config()
    return _config

# ==================== 便捷函数 ====================

def add_custom_response(patterns: List[str], response: str, priority: int = 0, description: str = ""):
    """便捷添加自定义响应"""
    config = get_layer0_config()
    return config.add_rule(patterns, response, priority, description)

def remove_custom_response(rule_id: str):
    """便捷删除自定义响应"""
    config = get_layer0_config()
    return config.remove_rule(rule_id)

def list_custom_responses():
    """便捷列出所有自定义响应"""
    config = get_layer0_config()
    return config.get_all_rules()

def get_layer0_stats():
    """便捷获取统计信息"""
    config = get_layer0_config()
    return config.get_statistics()

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🎨 灵犀 Layer 0 自定义配置测试")
    print("=" * 60)
    
    config = get_layer0_config()
    
    # 测试添加规则
    print("\n1️⃣ 添加自定义规则")
    config.add_rule(
        patterns=["老板好", "老大好"],
        response="老板好呀～ 今天心情怎么样？💋",
        priority=10,
        description="自定义问候"
    )
    
    config.add_rule(
        patterns=["去休息", "去睡觉"],
        response="好的老板～ 您也早点休息哦！🌙",
        priority=5,
        description="休息回应"
    )
    
    # 测试查看所有规则
    print("\n2️⃣ 查看所有规则")
    rules = config.get_all_rules()
    for rule in rules:
        print(f"   - {rule.id}: {rule.patterns} → {rule.response[:30]}... (优先级：{rule.priority})")
    
    # 测试统计
    print("\n3️⃣ 统计信息")
    stats = config.get_statistics()
    print(f"   总规则数：{stats['total_rules']}")
    print(f"   启用规则：{stats['enabled_rules']}")
    print(f"   总命中数：{stats['total_hits']}")
    
    # 测试导出
    print("\n4️⃣ 导出规则")
    output_file = Path.home() / ".openclaw" / "workspace" / ".learnings" / "layer0_export.json"
    config.export_rules(str(output_file))
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！配置文件：~/.openclaw/workspace/.learnings/layer0_custom_rules.json")
    print("=" * 60)
