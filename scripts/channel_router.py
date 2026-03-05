#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 渠道智能路由器 (Channel Router)

功能:
1. 根据渠道自动选择最优配置
2. 支持关键词识别
3. 支持时间段路由
4. 支持用户等级路由
5. Orchestrator 实例缓存

使用方式:
    from channel_router import get_channel_orchestrator
    
    orch = get_channel_orchestrator(
        channel="qqbot",
        user_id="user_123",
        user_input="写个 Python 函数"
    )
    
    reply = await orch.execute(user_input, user_id)
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# 延迟导入，避免循环依赖
_orchestrator_cache = {}
_config = None
_config_path = None

def load_channel_config(config_path: str = None) -> Dict:
    """加载渠道配置"""
    global _config, _config_path
    
    # 使用缓存
    if _config and _config_path == config_path:
        return _config
    
    # 默认路径
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "workspace" / ".learnings" / "channel_config.json"
    else:
        config_path = Path(config_path)
    
    # 加载配置
    try:
        if config_path.exists():
            _config = json.loads(config_path.read_text(encoding='utf-8'))
            _config_path = config_path
            print(f"✅ 渠道配置已加载：{config_path}")
        else:
            _config = get_default_config()
            print(f"⚠️  配置文件不存在，使用默认配置")
    except Exception as e:
        print(f"❌ 加载配置失败：{e}，使用默认配置")
        _config = get_default_config()
    
    return _config

def get_default_config() -> Dict:
    """默认配置"""
    return {
        "channels": {
            "default": {
                "description": "默认通道",
                "default": True,
                "config": {
                    "max_concurrent": 3,
                    "enable_review": False,
                    "enable_audit": False,
                    "enable_learning": True,
                    "fast_response": True,
                    "enable_auto_retry": True
                }
            }
        },
        "fallback": {
            "max_concurrent": 3,
            "enable_review": False,
            "enable_audit": False,
            "enable_learning": True,
            "fast_response": True,
            "enable_auto_retry": True
        }
    }

def identify_channel_type(channel: str, user_id: str, user_input: str) -> str:
    """
    识别渠道类型
    
    Args:
        channel: 渠道名 (qqbot/feishu/wechat 等)
        user_id: 用户 ID
        user_input: 用户输入
    
    Returns:
        渠道类型名称
    """
    config = load_channel_config()
    
    # 1. 检查渠道 + 关键词匹配
    for name, cfg in config.get("channels", {}).items():
        # 检查渠道名前缀
        if not channel.lower().startswith(name.split("_")[0]):
            continue
        
        # 检查用户 ID 匹配
        if "user_ids" in cfg and user_id not in cfg["user_ids"]:
            continue
        
        # 检查关键词匹配
        if "keywords" in cfg:
            if any(kw.lower() in user_input.lower() for kw in cfg["keywords"]):
                print(f"🎯 匹配渠道类型：{name} (关键词)")
                return name
        
        # 检查默认通道
        if cfg.get("default"):
            print(f"🎯 匹配渠道类型：{name} (默认)")
            return name
    
    # 2. 仅检查渠道名
    for name, cfg in config.get("channels", {}).items():
        if channel.lower() == name.split("_")[0] or channel.lower().startswith(name.split("_")[0]):
            if cfg.get("default"):
                print(f"🎯 匹配渠道类型：{name} (渠道名)")
                return name
    
    # 3. 返回默认
    print(f"⚠️  未匹配到渠道类型，使用默认配置")
    return "default"

def get_orchestrator_config(channel_type: str) -> Dict:
    """获取渠道配置"""
    config = load_channel_config()
    
    channels = config.get("channels", {})
    if channel_type in channels:
        return channels[channel_type].get("config", config.get("fallback", {}))
    
    return config.get("fallback", {})

def create_orchestrator(config: Dict):
    """创建 Orchestrator 实例"""
    from scripts.orchestrator_v2 import SmartOrchestrator
    
    return SmartOrchestrator(
        max_concurrent=config.get("max_concurrent", 3),
        enable_review=config.get("enable_review", False),
        enable_audit=config.get("enable_audit", False),
        enable_learning=config.get("enable_learning", True),
        enable_fast_response=config.get("fast_response", True),
        enable_auto_retry=config.get("enable_auto_retry", True)
    )

def get_channel_orchestrator(channel: str, user_id: str, 
                              user_input: str = None,
                              force_new: bool = False):
    """
    根据渠道获取最优配置的 Orchestrator
    
    Args:
        channel: 渠道名 (qqbot/feishu/wechat 等)
        user_id: 用户 ID
        user_input: 用户输入 (用于关键词匹配)
        force_new: 是否强制创建新实例
    
    Returns:
        SmartOrchestrator 实例
    """
    # 1. 识别渠道类型
    channel_type = identify_channel_type(channel, user_id, user_input or "")
    
    # 2. 获取配置
    config = get_orchestrator_config(channel_type)
    
    # 3. 生成缓存 key
    cache_key = f"{channel_type}_{hash(str(sorted(config.items())))}"
    
    # 4. 返回缓存的实例
    if not force_new and cache_key in _orchestrator_cache:
        print(f"♻️  使用缓存的 Orchestrator: {channel_type}")
        return _orchestrator_cache[cache_key]
    
    # 5. 创建新实例
    print(f"🆕 创建新的 Orchestrator: {channel_type}")
    orch = create_orchestrator(config)
    
    # 6. 缓存
    _orchestrator_cache[cache_key] = orch
    
    # 7. 返回
    print(f"✅ 渠道路由完成：{channel} → {channel_type}")
    print(f"   配置：max_concurrent={config.get('max_concurrent')}, " +
          f"review={config.get('enable_review')}, " +
          f"audit={config.get('enable_audit')}, " +
          f"fast={config.get('fast_response')}")
    
    return orch

def clear_cache():
    """清除缓存"""
    global _orchestrator_cache
    _orchestrator_cache = {}
    print("🗑️  Orchestrator 缓存已清除")

def reload_config(config_path: str = None):
    """重新加载配置"""
    global _config, _config_path
    _config = None
    load_channel_config(config_path)
    clear_cache()
    print("🔄 配置已重新加载")

def get_stats() -> Dict:
    """获取统计信息"""
    return {
        "cache_size": len(_orchestrator_cache),
        "cached_channels": list(_orchestrator_cache.keys())
    }

# ==================== 便捷函数 ====================

async def execute_with_channel_routing(channel: str, user_id: str, 
                                        user_input: str,
                                        is_background: bool = False):
    """
    便捷函数：使用渠道路由执行任务
    
    Args:
        channel: 渠道名
        user_id: 用户 ID
        user_input: 用户输入
        is_background: 是否后台任务
    
    Returns:
        TaskResult
    """
    orch = get_channel_orchestrator(channel, user_id, user_input)
    return await orch.execute(user_input, user_id, is_background=is_background)

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("📡 灵犀渠道智能路由器测试")
    print("=" * 60)
    
    test_cases = [
        ("qqbot", "DE5BA2C531B102AD9989F5E04935BCA6", "你好呀"),
        ("qqbot", "DE5BA2C531B102AD9989F5E04935BCA6", "写个 Python 函数"),
        ("qqbot", "DE5BA2C531B102AD9989F5E04935BCA6", "在吗？"),
        ("feishu", "user_456", "周报怎么写"),
        ("wechat", "user_789", "公众号文章"),
    ]
    
    print("\n📋 测试渠道路由:\n")
    
    for channel, user_id, input_text in test_cases:
        print(f"\n测试：{channel} | {user_id} | '{input_text}'")
        channel_type = identify_channel_type(channel, user_id, input_text)
        config = get_orchestrator_config(channel_type)
        print(f"  → 渠道类型：{channel_type}")
        print(f"  → 配置：{json.dumps(config, indent=2)}")
    
    print("\n📊 缓存统计:")
    stats = get_stats()
    print(f"  缓存大小：{stats['cache_size']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
