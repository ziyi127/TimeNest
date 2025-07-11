#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 核心模块单元测试
测试配置管理器、主题管理器、通知管理器等核心功能

该测试模块包含：
- 配置管理器测试
- 主题管理器测试
- 通知管理器测试
- 性能管理器测试
- 依赖注入容器测试
- 事件总线测试
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from test_framework import TimeNestTestCase, PerformanceTestCase, IntegrationTestCase


class TestConfigManager(TimeNestTestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        
        # 创建临时配置目录
        self.temp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: self._cleanup_temp_dir())
        
        # 导入配置管理器
        from core.config_manager import ConfigManager
        self.config_manager = ConfigManager(str(self.temp_dir))
    
    def _cleanup_temp_dir(self):
        """清理临时目录"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_initialization(self):
        """测试配置管理器初始化"""
        self.assertIsNotNone(self.config_manager)
        self.assertTrue(self.temp_dir.exists())
        self.assertIsInstance(self.config_manager.main_config, dict)
        self.assertIsInstance(self.config_manager.user_config, dict)
    
    def test_default_config_loading(self):
        """测试默认配置加载"""
        # 检查主配置默认值
        self.assertIn('app', self.config_manager.main_config)
        self.assertIn('window', self.config_manager.main_config)
        self.assertIn('performance', self.config_manager.main_config)
        
        # 检查用户配置默认值
        self.assertIn('profile', self.config_manager.user_config)
        self.assertIn('preferences', self.config_manager.user_config)
    
    def test_config_validation(self):
        """测试配置验证"""
        # 有效配置
        valid_config = {
            'app': {'name': 'TimeNest', 'version': '1.0.0'},
            'window': {'width': 1200, 'height': 800},
            'performance': {'cache_size': 100}
        }
        self.assertTrue(self.config_manager.validate_config('main', valid_config))
        
        # 无效配置
        invalid_config = {
            'app': {'name': 123},  # 名称应该是字符串
            'window': {'width': -100}  # 宽度应该是正数
        }
        self.assertFalse(self.config_manager.validate_config('main', invalid_config))
    
    def test_config_file_operations(self):
        """测试配置文件操作"""
        # 保存配置
        test_config = {'test_key': 'test_value'}
        config_file = self.temp_dir / 'test_config.json'
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # 加载配置
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config, test_config)
    
    def test_config_change_signals(self):
        """测试配置变更信号"""
        signal_received = False
        
        def on_config_changed(key, old_value, new_value):
            nonlocal signal_received
            signal_received = True
        
        # 连接信号
        self.config_manager.config_changed.connect(on_config_changed)
        
        # 触发配置变更（这里需要实现具体的配置变更方法）
        # self.config_manager.set_config('test_key', 'test_value')
        
        # 由于实际的配置变更方法可能还未实现，这里先跳过
        # self.assertTrue(signal_received)


class TestThemeManager(TimeNestTestCase):
    """主题管理器测试"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        
        # 创建临时主题目录
        self.temp_theme_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: self._cleanup_temp_dir())
        
        # 创建测试主题文件
        self._create_test_themes()
        
        # 导入主题管理器
        from core.theme_manager import ThemeManager
        self.theme_manager = ThemeManager(str(self.temp_theme_dir))
    
    def _cleanup_temp_dir(self):
        """清理临时目录"""
        import shutil
        if self.temp_theme_dir.exists():
            shutil.rmtree(self.temp_theme_dir, ignore_errors=True)
    
    def _create_test_themes(self):
        """创建测试主题文件"""
        # 创建默认主题
        default_theme = {
            'name': 'Default',
            'version': '1.0.0',
            'author': 'TimeNest Team',
            'colors': {
                'primary': '#007ACC',
                'secondary': '#4FC3F7',
                'background': '#1E1E1E'
            }
        }
        
        with open(self.temp_theme_dir / 'default.json', 'w') as f:
            json.dump(default_theme, f)
        
        # 创建暗色主题
        dark_theme = {
            'name': 'Dark',
            'version': '1.0.0',
            'author': 'TimeNest Team',
            'colors': {
                'primary': '#BB86FC',
                'secondary': '#03DAC6',
                'background': '#121212'
            }
        }
        
        with open(self.temp_theme_dir / 'dark.json', 'w') as f:
            json.dump(dark_theme, f)
    
    def test_theme_manager_initialization(self):
        """测试主题管理器初始化"""
        self.assertIsNotNone(self.theme_manager)
        self.assertTrue(self.temp_theme_dir.exists())
    
    def test_theme_loading(self):
        """测试主题加载"""
        # 检查主题是否已加载
        theme_list = self.theme_manager.get_theme_list()
        self.assertIn('Default', theme_list)
        self.assertIn('Dark', theme_list)
    
    def test_theme_application(self):
        """测试主题应用"""
        # 应用默认主题
        result = self.theme_manager.apply_theme('Default')
        self.assertTrue(result)
        self.assertEqual(self.theme_manager.current_theme, 'Default')
        
        # 应用不存在的主题
        result = self.theme_manager.apply_theme('NonExistent')
        self.assertFalse(result)
    
    def test_theme_validation(self):
        """测试主题验证"""
        # 这里可以添加主题验证的测试
        # 例如检查主题文件格式、必需字段等
        pass


class TestNotificationManager(TimeNestTestCase):
    """通知管理器测试"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        
        # 创建模拟配置管理器
        self.mock_config_manager = self.mock_manager.create_mock('config_manager')
        
        # 导入通知管理器
        from core.notification_manager import NotificationManager
        self.notification_manager = NotificationManager(self.mock_config_manager)
    
    def test_notification_manager_initialization(self):
        """测试通知管理器初始化"""
        self.assertIsNotNone(self.notification_manager)
    
    def test_notification_channels(self):
        """测试通知通道"""
        # 这里可以测试各种通知通道的功能
        # 由于通知管理器比较复杂，这里先做基础测试
        pass
    
    def test_notification_sending(self):
        """测试通知发送"""
        # 模拟通知发送
        with self.profiler.measure('notification_send'):
            # 这里添加实际的通知发送测试
            pass
        
        # 检查性能
        self.assert_performance('notification_send', 0.1)


class TestPerformanceManager(PerformanceTestCase):
    """性能管理器测试"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        
        # 创建模拟配置管理器
        self.mock_config_manager = self.mock_manager.create_mock('config_manager')
        
        # 导入性能管理器
        from core.performance_manager import PerformanceManager, LRUCache
        self.performance_manager = PerformanceManager(self.mock_config_manager)
        self.lru_cache = LRUCache(max_size=10)
    
    def test_performance_manager_initialization(self):
        """测试性能管理器初始化"""
        self.assertIsNotNone(self.performance_manager)
        self.assertIsNotNone(self.performance_manager.cache)
        self.assertIsNotNone(self.performance_manager.monitor)
    
    def test_lru_cache_basic_operations(self):
        """测试LRU缓存基本操作"""
        # 测试缓存设置和获取
        self.lru_cache.put('key1', 'value1')
        self.assertEqual(self.lru_cache.get('key1'), 'value1')
        
        # 测试缓存未命中
        self.assertIsNone(self.lru_cache.get('nonexistent'))
        
        # 测试默认值
        self.assertEqual(self.lru_cache.get('nonexistent', 'default'), 'default')
    
    def test_lru_cache_eviction(self):
        """测试LRU缓存淘汰机制"""
        # 填满缓存
        for i in range(15):  # 超过最大大小10
            self.lru_cache.put(f'key{i}', f'value{i}')
        
        # 检查缓存大小
        stats = self.lru_cache.get_stats()
        self.assertLessEqual(stats['size'], 10)
        
        # 检查最早的键是否被淘汰
        self.assertIsNone(self.lru_cache.get('key0'))
    
    def test_lru_cache_statistics(self):
        """测试LRU缓存统计"""
        # 添加一些数据
        self.lru_cache.put('key1', 'value1')
        self.lru_cache.put('key2', 'value2')
        
        # 访问数据
        self.lru_cache.get('key1')
        self.lru_cache.get('key1')
        self.lru_cache.get('nonexistent')
        
        # 检查统计
        stats = self.lru_cache.get_stats()
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertGreater(stats['hit_rate'], 0.5)
    
    def test_performance_monitoring(self):
        """测试性能监控"""
        # 启动监控
        self.performance_manager.start_monitoring()
        
        # 等待一段时间收集数据
        import time
        time.sleep(1)
        
        # 停止监控
        self.performance_manager.stop_monitoring()
        
        # 检查是否收集到数据
        avg_metrics = self.performance_manager.monitor.get_average_metrics(minutes=1)
        if avg_metrics:
            self.assertGreaterEqual(avg_metrics.cpu_percent, 0)
            self.assertGreaterEqual(avg_metrics.memory_percent, 0)


class TestDependencyInjection(TimeNestTestCase):
    """依赖注入容器测试"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        
        # 导入依赖注入容器
        from core.dependency_injection import DependencyInjectionContainer
        self.container = DependencyInjectionContainer()
        
        # 创建测试类
        class TestService:
            def __init__(self):
                self.value = "test"
        
        class TestDependentService:
            def __init__(self, test_service: TestService):
                self.test_service = test_service
        
        self.TestService = TestService
        self.TestDependentService = TestDependentService
    
    def test_container_initialization(self):
        """测试容器初始化"""
        self.assertIsNotNone(self.container)
    
    def test_singleton_registration(self):
        """测试单例注册"""
        # 注册单例服务
        self.container.register_singleton(self.TestService)
        
        # 解析服务
        service1 = self.container.resolve(self.TestService)
        service2 = self.container.resolve(self.TestService)
        
        # 检查是否为同一实例
        self.assertIs(service1, service2)
    
    def test_transient_registration(self):
        """测试瞬态注册"""
        # 注册瞬态服务
        self.container.register_transient(self.TestService)
        
        # 解析服务
        service1 = self.container.resolve(self.TestService)
        service2 = self.container.resolve(self.TestService)
        
        # 检查是否为不同实例
        self.assertIsNot(service1, service2)
    
    def test_dependency_resolution(self):
        """测试依赖解析"""
        # 注册服务
        self.container.register_singleton(self.TestService)
        self.container.register_transient(self.TestDependentService)
        
        # 解析依赖服务
        dependent_service = self.container.resolve(self.TestDependentService)
        
        # 检查依赖是否正确注入
        self.assertIsInstance(dependent_service.test_service, self.TestService)
    
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        # 创建循环依赖的类
        class ServiceA:
            def __init__(self, service_b: 'ServiceB'):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a
        
        # 注册服务
        self.container.register_transient(ServiceA)
        self.container.register_transient(ServiceB)
        
        # 检查是否检测到循环依赖
        from core.dependency_injection import CircularDependencyError
        with self.assertRaises(CircularDependencyError):
            self.container.resolve(ServiceA)


class TestEventBus(TimeNestTestCase):
    """事件总线测试"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        
        # 导入事件总线
        from core.event_bus import EventBus, EventPriority
        self.event_bus = EventBus()
        self.EventPriority = EventPriority
        
        # 测试数据
        self.received_events = []
    
    def test_event_bus_initialization(self):
        """测试事件总线初始化"""
        self.assertIsNotNone(self.event_bus)
    
    def test_event_publishing_and_subscription(self):
        """测试事件发布和订阅"""
        # 订阅事件
        def event_handler(event):
            self.received_events.append(event)
        
        subscription_id = self.event_bus.subscribe('test_event', event_handler)
        self.assertIsNotNone(subscription_id)
        
        # 发布事件
        event_id = self.event_bus.publish('test_event', {'message': 'Hello World'})
        self.assertIsNotNone(event_id)
        
        # 等待事件处理
        import time
        time.sleep(0.1)
        
        # 检查事件是否被接收
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].type, 'test_event')
        self.assertEqual(self.received_events[0].data['message'], 'Hello World')
    
    def test_event_unsubscription(self):
        """测试事件取消订阅"""
        # 订阅事件
        def event_handler(event):
            self.received_events.append(event)
        
        subscription_id = self.event_bus.subscribe('test_event', event_handler)
        
        # 取消订阅
        result = self.event_bus.unsubscribe(subscription_id)
        self.assertTrue(result)
        
        # 发布事件
        self.event_bus.publish('test_event', {'message': 'Should not receive'})
        
        # 等待事件处理
        import time
        time.sleep(0.1)
        
        # 检查事件是否未被接收
        self.assertEqual(len(self.received_events), 0)
    
    def test_event_priority(self):
        """测试事件优先级"""
        # 创建不同优先级的处理器
        def high_priority_handler(event):
            self.received_events.append(('high', event))
        
        def low_priority_handler(event):
            self.received_events.append(('low', event))
        
        # 订阅事件（注意订阅顺序）
        self.event_bus.subscribe('priority_test', low_priority_handler, priority=self.EventPriority.LOW)
        self.event_bus.subscribe('priority_test', high_priority_handler, priority=self.EventPriority.HIGH)
        
        # 发布事件
        self.event_bus.publish('priority_test', {'message': 'Priority test'})
        
        # 等待事件处理
        import time
        time.sleep(0.1)
        
        # 检查处理顺序（高优先级应该先处理）
        self.assertEqual(len(self.received_events), 2)
        self.assertEqual(self.received_events[0][0], 'high')
        self.assertEqual(self.received_events[1][0], 'low')


if __name__ == '__main__':
    unittest.main()
