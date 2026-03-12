#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 编排器单元测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFastResponseLayer:
    """快速响应层测试"""
    
    def test_import_fast_response(self):
        """测试快速响应层导入"""
        try:
            from scripts.fast_response_layer_v2 import fast_respond, ResponseResult
            assert fast_respond is not None
        except ImportError as e:
            pytest.skip(f"快速响应层未安装：{e}")
    
    def test_fast_respond_time(self):
        """测试快速响应时间"""
        import time
        from scripts.fast_response_layer_v2 import fast_respond
        
        test_inputs = [
            "现在几点了",
            "今天日期",
            "你好",
            "在吗"
        ]
        
        for user_input in test_inputs:
            start = time.time()
            result = fast_respond(user_input)
            elapsed = (time.time() - start) * 1000  # 转换为毫秒
            
            if result and result.matched:
                assert elapsed < 10, f"响应时间超过 10ms: {elapsed}ms"


class TestLayer0Skills:
    """Layer 0 技能测试"""
    
    def test_import_layer0(self):
        """测试 Layer 0 导入"""
        try:
            from scripts.layer0_skills import match_layer0_skill, execute_layer0_skill
            assert match_layer0_skill is not None
        except ImportError as e:
            pytest.skip(f"Layer 0 技能未安装：{e}")
    
    def test_time_skill(self):
        """测试时间查询技能"""
        from scripts.layer0_skills import match_layer0_skill
        
        matched, skill_info = match_layer0_skill("现在几点了")
        assert matched is True
        assert skill_info["skill_name"] == "time"
    
    def test_date_skill(self):
        """测试日期查询技能"""
        from scripts.layer0_skills import match_layer0_skill
        
        matched, skill_info = match_layer0_skill("今天几号")
        assert matched is True
        assert skill_info["skill_name"] == "date"
    
    def test_weather_skill(self):
        """测试天气查询技能"""
        from scripts.layer0_skills import match_layer0_skill
        
        matched, skill_info = match_layer0_skill("北京天气")
        assert matched is True
        assert skill_info["skill_name"] == "weather"


class TestConfigManager:
    """配置管理器测试"""
    
    def test_import_config(self):
        """测试配置管理器导入"""
        try:
            from core.config_manager import get_settings, Settings
            assert get_settings is not None
        except ImportError as e:
            pytest.skip(f"配置管理器未安装：{e}")
    
    def test_get_settings(self):
        """测试获取配置"""
        from core.config_manager import get_settings
        
        settings = get_settings()
        assert settings.VERSION == "v3.3.6"
        assert settings.DASHBOARD_PORT == 8765
        assert settings.MAX_CONCURRENT_TASKS == 100
    
    def test_get_dashboard_url(self):
        """测试获取 Dashboard URL"""
        from core.config_manager import get_dashboard_url
        
        url = get_dashboard_url()
        assert "8765" in url


class TestHealthCheck:
    """健康检查测试"""
    
    def test_import_health_check(self):
        """测试健康检查导入"""
        try:
            from scripts.health_check import check_dashboard_health, log_message
            assert check_dashboard_health is not None
        except ImportError as e:
            pytest.skip(f"健康检查模块未安装：{e}")


class TestEnhancedLogging:
    """增强日志测试"""
    
    def test_import_logging(self):
        """测试日志模块导入"""
        try:
            from scripts.enhanced_logging import lingxi_logger, log_execution
            assert lingxi_logger is not None
        except ImportError as e:
            pytest.skip(f"日志模块未安装：{e}")
    
    def test_log_execution(self):
        """测试日志执行装饰器"""
        from scripts.enhanced_logging import log_execution
        
        @log_execution
        def test_function():
            return "test"
        
        result = test_function()
        assert result == "test"


# 性能基准测试
class TestPerformance:
    """性能基准测试"""
    
    @pytest.mark.slow
    def test_orchestrator_init_time(self):
        """测试编排器初始化时间"""
        import time
        
        start = time.time()
        try:
            from scripts.orchestrator_v2 import SmartOrchestrator
            orch = SmartOrchestrator()
            elapsed = (time.time() - start) * 1000
            assert elapsed < 5000, f"初始化时间超过 5 秒：{elapsed}ms"
        except ImportError:
            pytest.skip("编排器未安装")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
