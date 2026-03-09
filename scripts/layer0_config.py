#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - Layer 0 自定义规则系统

✅ 开箱即用：支持用户自定义 Layer 0 规则
📁 配置文件：~/.openclaw/workspace/layer0_custom_rules.json
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime


# 配置文件路径
CONFIG_PATH = Path.home() / ".openclaw" / "workspace" / "layer0_custom_rules.json"


def load_custom_rules() -> List[Dict]:
    """
    加载用户自定义规则
    
    Returns:
        List[Dict]: 自定义规则列表
    """
    if not CONFIG_PATH.exists():
        # 创建默认配置文件
        _create_default_config()
        return []
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("rules", [])
    except Exception as e:
        print(f"⚠️ 加载自定义规则失败：{e}")
        return []


def _create_default_config():
    """创建默认配置文件"""
    default_config = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "description": "灵犀 Layer 0 自定义规则配置",
        "rules": [
            {
                "patterns": ["老板好", "老板早"],
                "response": "老板好呀～💋 今天也要加油哦！",
                "priority": 10,
                "enabled": True
            },
            {
                "patterns": ["退下", "去吧"],
                "response": "好的老板～ 有事随时叫我！😊",
                "priority": 5,
                "enabled": True
            }
        ],
        "usage": {
            "how_to_add": "在 rules 数组中添加新规则，每个规则包含 patterns、response、priority、enabled 字段",
            "pattern_format": "patterns 是字符串数组，匹配任一模式即触发",
            "priority_range": "priority 范围 1-10，数字越大优先级越高",
            "example": {
                "patterns": ["你好", "您好"],
                "response": "您好老板～ 有什么吩咐？",
                "priority": 8,
                "enabled": True
            }
        }
    }
    
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已创建 Layer 0 自定义规则配置文件：{CONFIG_PATH}")


def match_custom_rules(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    匹配自定义规则
    
    Args:
        user_input: 用户输入
    
    Returns:
        Tuple[bool, Optional[str]]: (是否匹配，响应内容)
    """
    rules = load_custom_rules()
    
    if not rules:
        return False, None
    
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        
        patterns = rule.get("patterns", [])
        response = rule.get("response", "")
        
        if not patterns or not response:
            continue
        
        # 检查是否匹配任一模式
        for pattern in patterns:
            if pattern in user_input:
                return True, response
    
    return False, None


def add_custom_rule(patterns: List[str], response: str, priority: int = 5, enabled: bool = True) -> bool:
    """
    添加自定义规则
    
    Args:
        patterns: 模式列表
        response: 响应内容
        priority: 优先级 (1-10)
        enabled: 是否启用
    
    Returns:
        bool: 是否成功添加
    """
    try:
        config = {
            "version": "1.0",
            "rules": []
        }
        
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        new_rule = {
            "patterns": patterns,
            "response": response,
            "priority": priority,
            "enabled": enabled,
            "created_at": datetime.now().isoformat()
        }
        
        config["rules"].append(new_rule)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已添加自定义规则：{patterns[0]} → {response[:30]}...")
        return True
        
    except Exception as e:
        print(f"❌ 添加规则失败：{e}")
        return False


def list_custom_rules() -> List[Dict]:
    """列出所有自定义规则"""
    return load_custom_rules()


def remove_custom_rule(index: int) -> bool:
    """
    删除自定义规则
    
    Args:
        index: 规则索引（从 0 开始）
    
    Returns:
        bool: 是否成功删除
    """
    try:
        if not CONFIG_PATH.exists():
            return False
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        rules = config.get("rules", [])
        if index < 0 or index >= len(rules):
            print(f"❌ 索引超出范围：{index}")
            return False
        
        removed = rules.pop(index)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已删除规则：{removed.get('patterns', ['?'])[0]}")
        return True
        
    except Exception as e:
        print(f"❌ 删除规则失败：{e}")
        return False


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Layer 0 自定义规则管理")
    parser.add_argument("action", choices=["list", "add", "remove", "init"], help="操作类型")
    parser.add_argument("--patterns", "-p", nargs="+", help="模式列表（添加时用）")
    parser.add_argument("--response", "-r", type=str, help="响应内容（添加时用）")
    parser.add_argument("--priority", type=int, default=5, help="优先级 1-10（添加时用）")
    parser.add_argument("--index", "-i", type=int, help="规则索引（删除时用）")
    
    args = parser.parse_args()
    
    if args.action == "list":
        rules = list_custom_rules()
        print(f"📋 自定义规则 ({len(rules)} 条):\n")
        for i, rule in enumerate(rules):
            status = "✅" if rule.get("enabled", True) else "❌"
            print(f"{i}. {status} 模式：{rule.get('patterns', [])}")
            print(f"   响应：{rule.get('response', '')}")
            print(f"   优先级：{rule.get('priority', 5)}\n")
    
    elif args.action == "add":
        if not args.patterns or not args.response:
            print("❌ 添加规则需要 --patterns 和 --response 参数")
            exit(1)
        add_custom_rule(args.patterns, args.response, args.priority)
    
    elif args.action == "remove":
        if args.index is None:
            print("❌ 删除规则需要 --index 参数")
            exit(1)
        remove_custom_rule(args.index)
    
    elif args.action == "init":
        _create_default_config()
        print("✅ 配置文件已初始化")
