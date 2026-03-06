#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置迁移器 - Config Migrator
版本升级时保留用户配置 💋

功能：
- 检测旧版本配置
- 自动迁移到新版本
- 备份旧配置
- 兼容性检查
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MigrationResult:
    """迁移结果"""
    success: bool
    old_version: str
    new_version: str
    migrated_items: List[str]
    skipped_items: List[str]
    warnings: List[str]
    backup_path: Optional[str]


class ConfigMigrator:
    """配置迁移器"""
    
    # 版本映射
    VERSION_MAP = {
        "v1.0.0": 10000,
        "v1.1.0": 10100,
        "v1.2.0": 10200,
        "v1.3.0": 10300,
        "v2.0.0": 20000,
        "v2.1.0": 20100,
        "v2.2.0": 20200,
        "v2.3.0": 20300,
    }
    
    def __init__(self, workspace_path: str = "~/.openclaw/workspace/"):
        self.workspace_path = Path(workspace_path).expanduser()
        self.config_path = self.workspace_path / "lingxi-config.json"
        self.backup_path = self.workspace_path / "config-backups"
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def _get_version_number(self, version: str) -> int:
        """获取版本号数字"""
        return self.VERSION_MAP.get(version, 0)
    
    def _detect_current_version(self) -> str:
        """检测当前配置版本"""
        if not self.config_path.exists():
            return "v1.0.0"  # 默认初始版本
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("_version", "v1.0.0")
    
    def _backup_config(self, version: str) -> str:
        """备份当前配置"""
        if not self.config_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"config_{version}_{timestamp}.json"
        shutil.copy2(self.config_path, backup_file)
        
        return str(backup_file)
    
    def migrate(self, target_version: str = "v2.9.3") -> MigrationResult:
        """
        迁移配置到目标版本
        
        Args:
            target_version: 目标版本号
            
        Returns:
            迁移结果
        """
        current_version = self._detect_current_version()
        current_num = self._get_version_number(current_version)
        target_num = self._get_version_number(target_version)
        
        # 不需要迁移
        if current_num >= target_num:
            return MigrationResult(
                success=True,
                old_version=current_version,
                new_version=target_version,
                migrated_items=[],
                skipped_items=["已是最新版本"],
                warnings=[],
                backup_path=None
            )
        
        # 备份旧配置
        backup_path = self._backup_config(current_version)
        
        # 加载当前配置
        config = self._load_config()
        
        # 执行迁移
        migrated_items = []
        skipped_items = []
        warnings = []
        
        # v1.x → v2.x 迁移
        if current_num < 20000:
            items, skips, warns = self._migrate_to_v2(config)
            migrated_items.extend(items)
            skipped_items.extend(skips)
            warnings.extend(warns)
        
        # v2.0 → v2.1 迁移
        if current_num < 20100:
            items, skips, warns = self._migrate_to_v2_1(config)
            migrated_items.extend(items)
            skipped_items.extend(skips)
            warnings.extend(warns)
        
        # v2.1 → v2.2 迁移
        if current_num < 20200:
            items, skips, warns = self._migrate_to_v2_2(config)
            migrated_items.extend(items)
            skipped_items.extend(skips)
            warnings.extend(warns)
        
        # v2.2 → v2.3 迁移
        if current_num < 20300:
            items, skips, warns = self._migrate_to_v2_3(config)
            migrated_items.extend(items)
            skipped_items.extend(skips)
            warnings.extend(warns)
        
        # 更新版本号
        config["_version"] = target_version
        config["_migrated_at"] = datetime.now().isoformat()
        config["_migrated_from"] = current_version
        
        # 保存新配置
        self._save_config(config)
        
        return MigrationResult(
            success=True,
            old_version=current_version,
            new_version=target_version,
            migrated_items=migrated_items,
            skipped_items=skipped_items,
            warnings=warnings,
            backup_path=backup_path
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _migrate_to_v2(self, config: Dict) -> tuple:
        """迁移到 v2.0.0（异步任务系统）"""
        migrated = []
        skipped = []
        warnings = []
        
        # 保留角色配置
        if "roles" in config:
            config["roles_v2"] = config["roles"]
            migrated.append("角色配置 → roles_v2")
        
        # 保留模型偏好
        if "preferred_model" in config:
            config["model_preferences"] = {
                "default": config["preferred_model"]
            }
            migrated.append("模型偏好 → model_preferences")
        
        # 添加异步任务配置（新增）
        if "async_tasks" not in config:
            config["async_tasks"] = {
                "enabled": True,
                "max_concurrent": 5,
                "timeout_seconds": 300
            }
            migrated.append("新增异步任务配置")
        
        # 保留任务模板
        if "templates" in config:
            config["task_templates"] = config["templates"]
            migrated.append("任务模板 → task_templates")
        
        return migrated, skipped, warnings
    
    def _migrate_to_v2_1(self, config: Dict) -> tuple:
        """迁移到 v2.1.0（复杂任务方法论 + QQ Bot）"""
        migrated = []
        skipped = []
        warnings = []
        
        # 保留异步配置
        if "async_tasks" in config:
            config["async_config"] = config["async_tasks"]
            migrated.append("异步配置 → async_config")
        
        # 添加 QQ Bot 配置（新增）
        if "qqbot" not in config:
            config["qqbot"] = {
                "enabled": True,  # 默认启用
                "auto_detect_tasks": True,
                "instant_keywords": ["天气", "搜索", "翻译", "几点了"],
                "background_keywords": ["发布", "生成", "创作", "写"]
            }
            migrated.append("新增 QQ Bot 配置（默认启用）")
        
        # 添加复杂任务配置
        if "complex_tasks" not in config:
            config["complex_tasks"] = {
                "enabled": True,
                "methodology": "three_layer",  # three_layer 或 s0_s3
                "max_retries": 3
            }
            migrated.append("新增复杂任务配置")
        
        return migrated, skipped, warnings
    
    def _migrate_to_v2_2(self, config: Dict) -> tuple:
        """迁移到 v2.2.0（S0→S3 过滤）"""
        migrated = []
        skipped = []
        warnings = []
        
        # 保留复杂任务配置
        if "complex_tasks" in config:
            config["complex_tasks"]["methodology"] = "s0_s3"
            migrated.append("复杂任务方法升级为 S0→S3")
        
        # 添加 S0→S3 配置
        if "s0_s3" not in config:
            config["s0_s3"] = {
                "enabled": True,
                "whitelist": ["天气", "时间", "翻译", "搜索"],
                "blacklist": ["开发", "系统", "架构"],
                "threshold_score": 8
            }
            migrated.append("新增 S0→S3 过滤配置")
        
        # 保留成本优化配置
        if "cost_optimization" not in config:
            config["cost_optimization"] = {
                "enabled": True,
                "max_token_per_task": 5000,
                "prefer_cache": True
            }
            migrated.append("新增成本优化配置")
        
        return migrated, skipped, warnings
    
    def _migrate_to_v2_3(self, config: Dict) -> tuple:
        """迁移到 v2.3.0（智能学习系统）"""
        migrated = []
        skipped = []
        warnings = []
        
        # 保留所有旧配置
        if "model_preferences" in config:
            config["intelligence"] = {
                "enabled": True,
                "inherit_preferences": True,
                "legacy_model_prefs": config["model_preferences"]
            }
            migrated.append("模型偏好 → intelligence.legacy")
        else:
            config["intelligence"] = {
                "enabled": True,
                "inherit_preferences": False
            }
            migrated.append("新增智能学习配置")
        
        # 保留 QQ Bot 配置并增强
        if "qqbot" in config:
            config["qqbot"]["auto_enable"] = True  # 强制自动启用
            config["qqbot"]["integration_check"] = True
            migrated.append("QQ Bot 配置增强（自动启用）")
        
        # 添加任务日志配置
        if "task_logging" not in config:
            config["task_logging"] = {
                "enabled": True,
                "log_path": "~/.openclaw/workspace/task-logs/",
                "retention_days": 30,
                "auto_migrate": True  # 自动迁移旧数据
            }
            migrated.append("新增任务日志配置")
        
        # 添加模式学习配置
        if "pattern_learning" not in config:
            config["pattern_learning"] = {
                "enabled": True,
                "analyze_days": 7,
                "auto_optimize": True
            }
            migrated.append("新增模式学习配置")
        
        # 添加预测调度配置
        if "prediction" not in config:
            config["prediction"] = {
                "enabled": True,
                "advance_minutes": 30,
                "auto_remind": False  # 默认不自动提醒，避免打扰
            }
            migrated.append("新增预测调度配置")
        
        return migrated, skipped, warnings
    
    def get_migration_report(self) -> str:
        """获取迁移报告"""
        current_version = self._detect_current_version()
        
        report = []
        report.append("📦 灵犀配置迁移报告\n")
        report.append("=" * 50 + "\n")
        report.append(f"当前版本：{current_version}\n")
        report.append(f"配置文件：{self.config_path}\n")
        
        if self.config_path.exists():
            report.append(f"配置文件状态：✅ 存在\n")
            
            # 显示保留的配置
            config = self._load_config()
            report.append(f"\n保留的配置项:\n")
            
            # 关键配置
            key_configs = [
                "roles_v2",
                "model_preferences",
                "async_config",
                "qqbot",
                "complex_tasks",
                "s0_s3",
                "intelligence",
                "task_logging"
            ]
            
            for key in key_configs:
                if key in config:
                    report.append(f"   ✅ {key}\n")
                else:
                    report.append(f"   ❌ {key}\n")
        else:
            report.append(f"配置文件状态：❌ 不存在（首次安装）\n")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)


# 全局单例
_migrator = None

def get_migrator() -> ConfigMigrator:
    """获取全局配置迁移器实例"""
    global _migrator
    if _migrator is None:
        _migrator = ConfigMigrator()
    return _migrator


# 使用示例
if __name__ == "__main__":
    migrator = ConfigMigrator()
    
    # 获取迁移报告
    report = migrator.get_migration_report()
    print(report)
    
    # 执行迁移
    print("\n🔄 执行迁移到 v2.3.0...")
    result = migrator.migrate(target_version="v2.9.3")
    
    print(f"\n✅ 迁移完成:")
    print(f"   旧版本：{result.old_version}")
    print(f"   新版本：{result.new_version}")
    print(f"   迁移项：{len(result.migrated_items)}")
    print(f"   跳过项：{len(result.skipped_items)}")
    print(f"   警告：{len(result.warnings)}")
    
    if result.backup_path:
        print(f"   备份：{result.backup_path}")
    
    if result.migrated_items:
        print(f"\n📋 迁移详情:")
        for item in result.migrated_items[:10]:
            print(f"   • {item}")
