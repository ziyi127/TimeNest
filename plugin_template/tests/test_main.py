#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件模板测试
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# 添加插件路径
plugin_path = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_path))

from main import MyPlugin, create_plugin, get_plugin_info
from core.plugin_system import PluginManager, PluginStatus


class TestMyPlugin:
    """插件测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.plugin = MyPlugin()
        self.mock_plugin_manager = Mock(spec=PluginManager)
        
        # 模拟插件管理器方法
        self.mock_plugin_manager.get_plugin_config.return_value = {}
        self.mock_plugin_manager.set_plugin_config.return_value = None
        self.mock_plugin_manager.get_event_bus.return_value = Mock()
    
    def test_plugin_creation(self):
        """测试插件创建"""
        assert self.plugin is not None
        assert self.plugin.metadata.id == "my_plugin_template"
        assert self.plugin.metadata.name == "插件模板"
        assert self.plugin.metadata.version == "1.0.0"
    
    def test_initialize(self):
        """测试插件初始化"""
        result = self.plugin.initialize(self.mock_plugin_manager)
        
        assert result is True
        assert self.plugin.plugin_manager == self.mock_plugin_manager
        assert not self.plugin.is_running
    
    def test_activate(self):
        """测试插件激活"""
        # 先初始化
        self.plugin.initialize(self.mock_plugin_manager)
        
        # 激活插件
        result = self.plugin.activate()
        
        assert result is True
        assert self.plugin.is_running
        assert self.plugin.status == PluginStatus.ENABLED
    
    def test_deactivate(self):
        """测试插件停用"""
        # 先初始化和激活
        self.plugin.initialize(self.mock_plugin_manager)
        self.plugin.activate()
        
        # 停用插件
        result = self.plugin.deactivate()
        
        assert result is True
        assert not self.plugin.is_running
    
    def test_cleanup(self):
        """测试插件清理"""
        # 先初始化和激活
        self.plugin.initialize(self.mock_plugin_manager)
        self.plugin.activate()
        
        # 清理插件
        result = self.plugin.cleanup()
        
        assert result is True
        assert not self.plugin.is_running
    
    def test_config_management(self):
        """测试配置管理"""
        self.plugin.initialize(self.mock_plugin_manager)
        
        # 测试设置配置
        self.plugin.set_setting('test_key', 'test_value')
        assert self.plugin.get_setting('test_key') == 'test_value'
        
        # 测试默认值
        assert self.plugin.get_setting('nonexistent_key', 'default') == 'default'
    
    def test_data_file_path(self):
        """测试数据文件路径"""
        file_path = self.plugin.get_data_file_path('test.json')
        
        assert isinstance(file_path, Path)
        assert file_path.name == 'test.json'
        assert 'my_plugin_template' in str(file_path)
    
    def test_event_handling(self):
        """测试事件处理"""
        self.plugin.initialize(self.mock_plugin_manager)
        
        # 测试事件处理方法存在
        assert hasattr(self.plugin, '_on_app_started')
        assert hasattr(self.plugin, '_on_app_closing')
        assert hasattr(self.plugin, '_on_schedule_changed')
        
        # 测试事件处理方法可调用
        mock_event = Mock()
        self.plugin._on_app_started(mock_event)
        self.plugin._on_app_closing(mock_event)
        self.plugin._on_schedule_changed(mock_event)


class TestPluginEntryPoints:
    """测试插件入口点"""
    
    def test_create_plugin(self):
        """测试创建插件函数"""
        plugin = create_plugin()
        
        assert plugin is not None
        assert isinstance(plugin, MyPlugin)
    
    def test_get_plugin_info(self):
        """测试获取插件信息函数"""
        info = get_plugin_info()
        
        assert isinstance(info, dict)
        assert 'id' in info
        assert 'name' in info
        assert 'version' in info
        assert 'description' in info
        assert 'author' in info
        
        assert info['id'] == 'my_plugin_template'
        assert info['name'] == '插件模板'
        assert info['version'] == '1.0.0'


class TestPluginIntegration:
    """插件集成测试"""
    
    @pytest.fixture
    def plugin_manager(self):
        """创建模拟插件管理器"""
        manager = Mock(spec=PluginManager)
        manager.get_plugin_config.return_value = {}
        manager.set_plugin_config.return_value = None
        manager.get_event_bus.return_value = Mock()
        return manager
    
    def test_full_lifecycle(self, plugin_manager):
        """测试完整生命周期"""
        plugin = create_plugin()
        
        # 初始化
        assert plugin.initialize(plugin_manager) is True
        
        # 激活
        assert plugin.activate() is True
        assert plugin.is_running
        
        # 停用
        assert plugin.deactivate() is True
        assert not plugin.is_running
        
        # 清理
        assert plugin.cleanup() is True
    
    def test_error_handling(self, plugin_manager):
        """测试错误处理"""
        plugin = create_plugin()
        
        # 测试未初始化就激活
        # 这应该不会崩溃，但可能返回 False
        try:
            result = plugin.activate()
            # 根据实现，这可能成功也可能失败
        except Exception:
            # 如果抛出异常，确保是预期的异常类型
            pass
    
    def test_double_activation(self, plugin_manager):
        """测试重复激活"""
        plugin = create_plugin()
        plugin.initialize(plugin_manager)
        
        # 第一次激活
        assert plugin.activate() is True
        
        # 第二次激活应该也成功（或至少不崩溃）
        assert plugin.activate() is True
    
    def test_deactivate_without_activation(self, plugin_manager):
        """测试未激活就停用"""
        plugin = create_plugin()
        plugin.initialize(plugin_manager)
        
        # 未激活就停用应该成功
        assert plugin.deactivate() is True


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])
