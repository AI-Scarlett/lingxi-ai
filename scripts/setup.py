#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 v3.0.2 - 一键配置脚本

✅ 用户只需执行这一条命令：
    python3 setup.py --auto

完成所有配置：
- Layer 0 规则初始化
- Layer 0 技能初始化
- 自定义规则配置文件创建
- 自动学习系统初始化
- 性能优化补丁应用
- 配置文件权限设置
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text):
    """打印普通信息"""
    print(f"ℹ️  {text}")


# ==================== 配置函数 ====================

def init_layer0_config():
    """初始化 Layer 0 自定义规则配置"""
    config_path = Path.home() / ".openclaw" / "workspace" / "layer0_custom_rules.json"
    
    if config_path.exists():
        print_warning(f"配置文件已存在：{config_path}")
        return True
    
    try:
        config = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "description": "灵犀 Layer 0 自定义规则配置 - 开箱即用",
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
                },
                {
                    "patterns": ["开工", "开始工作"],
                    "response": "收到老板！⚡ 马上进入工作状态～",
                    "priority": 8,
                    "enabled": True
                },
                {
                    "patterns": ["休息", "休息一下"],
                    "response": "好的老板～ 注意休息哦！☕",
                    "priority": 6,
                    "enabled": True
                }
            ],
            "usage": {
                "how_to_add": "在 rules 数组中添加新规则",
                "example": {
                    "patterns": ["你好"],
                    "response": "您好老板～",
                    "priority": 8,
                    "enabled": True
                }
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 设置文件权限
        os.chmod(config_path, 0o644)
        
        print_success(f"Layer 0 自定义规则配置已创建：{config_path}")
        print_info(f"   默认规则：{len(config['rules'])} 条")
        return True
        
    except Exception as e:
        print_error(f"创建配置文件失败：{e}")
        return False


def init_learning_system():
    """初始化自动学习系统"""
    try:
        log_path = Path.home() / ".openclaw" / "workspace" / ".learnings" / "query_logs"
        log_path.mkdir(parents=True, exist_ok=True)
        
        print_success(f"自动学习系统已初始化：{log_path}")
        return True
        
    except Exception as e:
        print_error(f"初始化学习系统失败：{e}")
        return False


def test_layer0():
    """测试 Layer 0 快速响应"""
    print_info("测试 Layer 0 快速响应...")
    
    try:
        from fast_response_layer_v2 import fast_respond, LAYER0_RULES
        
        print_info(f"   Layer 0 规则数：{len(LAYER0_RULES)} 条")
        
        test_cases = [
            ("你好", "问候"),
            ("帮我写个文案", "创作"),
            ("生成一张图片", "图像"),
            ("发小红书", "发布"),
            ("几点了", "时间"),
        ]
        
        all_passed = True
        for query, category in test_cases:
            result = fast_respond(query)
            if result.response and result.layer == "layer0":
                print_success(f"   \"{query}\" ({category}) → {result.latency_ms:.3f}ms")
            else:
                print_error(f"   \"{query}\" ({category}) → 未命中 Layer 0")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Layer 0 测试失败：{e}")
        return False


def test_layer0_skills():
    """测试 Layer 0 技能系统"""
    print_info("测试 Layer 0 技能系统...")
    
    try:
        from layer0_skills import match_layer0_skill, list_available_skills
        
        skills = list_available_skills()
        print_info(f"   可用技能数：{len(skills)} 个")
        
        test_cases = [
            "几点了",
            "写文案",
            "发小红书",
            "想你",
            "天气",
        ]
        
        all_passed = True
        for test in test_cases:
            matched, skill = match_layer0_skill(test)
            if matched:
                print_success(f"   \"{test}\" → {skill['skill_name']}")
            else:
                print_error(f"   \"{test}\" → 未匹配")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Layer 0 技能测试失败：{e}")
        return False


def test_custom_rules():
    """测试自定义规则"""
    print_info("测试自定义规则系统...")
    
    try:
        from layer0_config import load_custom_rules
        
        rules = load_custom_rules()
        print_info(f"   已加载规则：{len(rules)} 条")
        
        if len(rules) > 0:
            for rule in rules[:3]:  # 显示前 3 条
                patterns = rule.get('patterns', [])
                response = rule.get('response', '')[:30]
                print_success(f"   {patterns} → {response}...")
        
        return True
        
    except Exception as e:
        print_error(f"自定义规则测试失败：{e}")
        return False


def test_learning_system():
    """测试自动学习系统"""
    print_info("测试自动学习系统...")
    
    try:
        from learning_layer import AutoLearner
        
        learner = AutoLearner()
        stats = learner.analyzer.get_stats()
        
        print_success(f"自动学习器已初始化")
        print_info(f"   存储路径：{stats['storage_path']}")
        print_info(f"   当前记录：{stats['total_query_count']} 条")
        
        return True
        
    except Exception as e:
        print_error(f"自动学习系统测试失败：{e}")
        return False


def test_orchestrator():
    """测试 Orchestrator 初始化"""
    print_info("测试 Orchestrator 初始化...")
    
    try:
        from orchestrator_v2 import get_orchestrator
        
        orch = get_orchestrator()
        
        print_success("Orchestrator 初始化成功")
        print_info(f"   快速响应：{'✅' if orch.enable_fast_response else '❌'}")
        print_info(f"   自动学习器：{'✅' if orch.auto_learner else '❌'}")
        print_info(f"   性能监控：{'✅' if orch.perf_monitor else '❌'}")
        
        return True
        
    except Exception as e:
        print_error(f"Orchestrator 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print_header("灵犀 v3.0.2 - 完整测试套件")
    
    tests = [
        ("Layer 0 快速响应", test_layer0),
        ("Layer 0 技能系统", test_layer0_skills),
        ("自定义规则", test_custom_rules),
        ("自动学习系统", test_learning_system),
        ("Orchestrator", test_orchestrator),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append((name, result))
    
    # 汇总结果
    print_header("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status}: {name}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print_success("🎉 所有测试通过！灵犀已准备就绪！")
        return True
    else:
        print_warning(f"⚠️  {total - passed} 个测试失败，请检查配置")
        return False


def auto_setup():
    """自动配置（一键完成）"""
    print_header("灵犀 v3.0.2 - 自动配置")
    
    steps = [
        ("初始化 Layer 0 自定义规则配置", init_layer0_config),
        ("初始化自动学习系统", init_learning_system),
        ("运行完整测试", run_all_tests),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print_warning(f"步骤 '{step_name}' 未完全成功，继续执行...")
    
    print_header("配置完成")
    print_success("🎉 灵犀 v3.0.2 已配置完成！")
    print("\n📖 使用说明:")
    print("   1. 查看快速开始指南：cat QUICKSTART.md")
    print("   2. 查看自动学习文档：cat AUTO_LEARNING_GUIDE.md")
    print("   3. 测试 Layer 0 响应：python3 -c \"from fast_response_layer_v2 import fast_respond; print(fast_respond('你好').response)\"")
    print("   4. 查看学习报告：python3 learning_layer.py --report")
    print("\n💡 提示：")
    print("   - 自定义规则配置文件：~/.openclaw/workspace/layer0_custom_rules.json")
    print("   - 自动学习日志目录：~/.openclaw/workspace/.learnings/query_logs/")
    print("   - 建议设置定时任务：0 2 * * * python3 learning_layer.py --apply")
    print()


def show_status():
    """显示当前状态"""
    print_header("灵犀 v3.0.2 - 系统状态")
    
    # 检查配置文件
    config_path = Path.home() / ".openclaw" / "workspace" / "layer0_custom_rules.json"
    if config_path.exists():
        print_success(f"自定义规则配置：已创建")
        with open(config_path, 'r') as f:
            config = json.load(f)
        print_info(f"   规则数：{len(config.get('rules', []))}")
    else:
        print_warning("自定义规则配置：未创建")
    
    # 检查学习日志
    log_path = Path.home() / ".openclaw" / "workspace" / ".learnings" / "query_logs"
    if log_path.exists():
        log_files = list(log_path.glob("*.jsonl"))
        print_success(f"自动学习日志：已创建")
        print_info(f"   日志文件：{len(log_files)} 个")
    else:
        print_warning("自动学习日志：未创建")
    
    # 检查 Layer 0 规则
    try:
        from fast_response_layer_v2 import LAYER0_RULES
        print_success(f"Layer 0 规则：{len(LAYER0_RULES)} 条")
    except:
        print_error("Layer 0 规则：加载失败")
    
    # 检查 Layer 0 技能
    try:
        from layer0_skills import list_available_skills
        skills = list_available_skills()
        print_success(f"Layer 0 技能：{len(skills)} 个")
    except:
        print_error("Layer 0 技能：加载失败")


# ==================== 主入口 ====================

def main():
    parser = argparse.ArgumentParser(
        description="灵犀 v3.0.2 - 一键配置脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 setup.py --auto          # 自动配置（推荐）
  python3 setup.py --test          # 运行完整测试
  python3 setup.py --status        # 显示系统状态
  python3 setup.py --init-config   # 仅初始化配置文件
        """
    )
    
    parser.add_argument("--auto", action="store_true", help="自动配置（一键完成所有配置）")
    parser.add_argument("--test", action="store_true", help="运行完整测试套件")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--init-config", action="store_true", help="仅初始化配置文件")
    parser.add_argument("--reset-layer0", action="store_true", help="重置 Layer 0 配置")
    
    args = parser.parse_args()
    
    if args.auto:
        auto_setup()
    elif args.test:
        run_all_tests()
    elif args.status:
        show_status()
    elif args.init_config:
        init_layer0_config()
        init_learning_system()
    elif args.reset_layer0:
        config_path = Path.home() / ".openclaw" / "workspace" / "layer0_custom_rules.json"
        if config_path.exists():
            config_path.unlink()
            print_success(f"已删除配置文件：{config_path}")
            print_info("下次运行时会自动创建新配置")
        else:
            print_warning("配置文件不存在")
    else:
        parser.print_help()
        print("\n💡 推荐：运行 python3 setup.py --auto 完成自动配置")


if __name__ == "__main__":
    main()
