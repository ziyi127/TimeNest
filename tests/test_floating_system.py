#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 浮窗系统测试
验证浮窗系统的功能完整性和集成正确性
"""

import sys
import os
import unittest
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 设置测试环境
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

from ui.floating_widget import (
    FloatingWidget, FloatingModule, TimeModule, ScheduleModule,
    WeatherModule, CountdownModule, SystemStatusModule
)
from core.floating_manager import FloatingManager
from ui.system_tray import SystemTrayManager
from ui.floating_settings_tab import FloatingSettingsTab
from models.schedule import Schedule, Subject, TimeSlot, ClassItem


class TestFloatingSystem(unittest.TestCase):
    """浮窗系统测试类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
        
        # 设置日志
        logging.basicConfig(level=logging.DEBUG)
    
    def setUp(self):
        """设置测试"""
        self.floating_widget = None
        self.floating_manager = None
        self.system_tray = None
        self.settings_tab = None
    
    def tearDown(self):
        """清理测试"""
        if self.floating_widget:
            self.floating_widget.close()
        if self.floating_manager:
            self.floating_manager.cleanup()
        if self.system_tray:
            self.system_tray.cleanup()
    
    def test_floating_widget_creation(self):
        """测试浮窗组件创建"""
        self.floating_widget = FloatingWidget()
        
        # 验证基本属性
        self.assertIsNotNone(self.floating_widget)
        self.assertEqual(self.floating_widget._width, 400)
        self.assertEqual(self.floating_widget._height, 60)
        self.assertEqual(self.floating_widget._opacity, 0.85)
        
        # 验证窗口标志
        flags = self.floating_widget.windowFlags()
        self.assertTrue(flags & Qt.WindowType.WindowStaysOnTopHint)
        self.assertTrue(flags & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(flags & Qt.WindowType.Tool)
    
    def test_floating_modules(self):
        """测试浮窗模块"""
        self.floating_widget = FloatingWidget()
        
        # 测试时间模块
        time_module = TimeModule()
        self.floating_widget.add_module(time_module)
        self.assertIn('time', self.floating_widget._modules)
        
        # 测试模块内容
        content = time_module.get_content()
        self.assertIsInstance(content, str)
        self.assertTrue(len(content) > 0)
        
        # 测试课程模块
        schedule = self._create_test_schedule()
        schedule_module = ScheduleModule(schedule)
        self.floating_widget.add_module(schedule_module)
        self.assertIn('schedule', self.floating_widget._modules)
        
        # 测试天气模块
        weather_module = WeatherModule()
        self.floating_widget.add_module(weather_module)
        self.assertIn('weather', self.floating_widget._modules)
        
        # 测试系统状态模块
        system_module = SystemStatusModule()
        self.floating_widget.add_module(system_module)
        self.assertIn('system', self.floating_widget._modules)
    
    def test_floating_manager(self):
        """测试浮窗管理器"""
        self.floating_manager = FloatingManager()
        
        # 测试创建浮窗
        config = {
            'width': 500,
            'height': 80,
            'opacity': 0.9,
            'enabled_modules': ['time', 'weather']
        }
        
        success = self.floating_manager.create_widget(config)
        self.assertTrue(success)
        self.assertIsNotNone(self.floating_manager.get_widget())
        
        # 测试配置更新
        new_config = {'width': 600, 'height': 70}
        self.floating_manager.update_config(new_config)
        
        # 测试启用/禁用
        self.floating_manager.set_enabled(True)
        self.assertTrue(self.floating_manager.is_enabled())
        
        self.floating_manager.set_enabled(False)
        self.assertFalse(self.floating_manager.is_enabled())
    
    def test_system_tray_manager(self):
        """测试系统托盘管理器"""
        # 创建模拟的浮窗管理器
        mock_floating_manager = Mock(spec=FloatingManager)
        mock_floating_manager.widget_shown = Mock()
        mock_floating_manager.widget_hidden = Mock()
        
        self.system_tray = SystemTrayManager(mock_floating_manager)
        
        # 验证基本属性
        self.assertIsNotNone(self.system_tray)
        self.assertEqual(self.system_tray.floating_manager, mock_floating_manager)
        
        # 测试菜单创建
        self.assertIsNotNone(self.system_tray.tray_menu)
        self.assertIn('show_main', self.system_tray.actions)
        self.assertIn('toggle_floating', self.system_tray.actions)
        self.assertIn('settings', self.system_tray.actions)
        self.assertIn('quit', self.system_tray.actions)
        
        # 测试状态更新
        self.system_tray.update_floating_status(True)
        self.assertTrue(self.system_tray.floating_visible)
        
        self.system_tray.update_floating_status(False)
        self.assertFalse(self.system_tray.floating_visible)
    
    def test_floating_settings_tab(self):
        """测试浮窗设置标签页"""
        self.settings_tab = FloatingSettingsTab()
        
        # 验证UI组件
        self.assertIsNotNone(self.settings_tab.width_spin)
        self.assertIsNotNone(self.settings_tab.height_spin)
        self.assertIsNotNone(self.settings_tab.opacity_slider)
        self.assertIsNotNone(self.settings_tab.radius_slider)
        
        # 测试配置获取
        config = self.settings_tab.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('width', config)
        self.assertIn('height', config)
        self.assertIn('opacity', config)
        self.assertIn('enabled_modules', config)
        
        # 测试配置设置
        test_config = {
            'width': 450,
            'height': 70,
            'opacity': 0.8,
            'enabled_modules': ['time', 'schedule', 'weather']
        }
        
        self.settings_tab.set_config(test_config)
        self.assertEqual(self.settings_tab.width_spin.value(), 450)
        self.assertEqual(self.settings_tab.height_spin.value(), 70)
        self.assertEqual(self.settings_tab.opacity_slider.value(), 80)
    
    def test_signal_connections(self):
        """测试信号连接"""
        # 创建组件
        self.floating_manager = FloatingManager()
        self.system_tray = SystemTrayManager(self.floating_manager)
        
        # 测试信号连接
        signal_received = []
        
        def on_widget_shown():
            signal_received.append('widget_shown')
        
        def on_floating_toggled(visible):
            signal_received.append(f'floating_toggled_{visible}')
        
        # 连接信号
        self.floating_manager.widget_shown.connect(on_widget_shown)
        self.system_tray.floating_toggled.connect(on_floating_toggled)
        
        # 触发信号
        self.floating_manager.create_widget()
        self.floating_manager.show_widget()
        
        # 验证信号
        QTest.qWait(100)  # 等待信号处理
        self.assertIn('widget_shown', signal_received)
    
    def test_configuration_integration(self):
        """测试配置集成"""
        # 测试配置路径前缀
        config_key = "floating_widget.width"
        self.assertTrue(config_key.startswith("floating_widget."))
        
        # 测试默认配置
        self.floating_manager = FloatingManager()
        default_config = self.floating_manager._get_default_config()
        
        required_keys = [
            'width', 'height', 'opacity', 'radius', 'font_size',
            'enabled_modules', 'always_on_top', 'enable_animations'
        ]
        
        for key in required_keys:
            self.assertIn(key, default_config)
    
    def test_error_handling(self):
        """测试错误处理"""
        self.floating_manager = FloatingManager()
        
        # 测试无效配置
        invalid_config = {'width': -100, 'height': -50}
        
        # 应该不会崩溃，而是使用默认值
        try:
            self.floating_manager.update_config(invalid_config)
        except Exception as e:
            self.fail(f"错误处理失败: {e}")
        
        # 测试模块添加错误
        self.floating_widget = FloatingWidget()
        
        # 添加无效模块应该被捕获
        try:
            invalid_module = Mock()
            invalid_module.module_id = "invalid"
            invalid_module.get_content.side_effect = Exception("Test error")
            self.floating_widget.add_module(invalid_module)
        except Exception as e:
            self.fail(f"模块错误处理失败: {e}")
    
    def _create_test_schedule(self) -> Schedule:
        """创建测试课程表"""
        schedule = Schedule(name="测试课程表")
        
        # 添加科目
        math = Subject(id="math", name="数学", teacher="张老师")
        schedule.add_subject(math)
        
        # 添加时间段
        slot1 = TimeSlot(id="slot1", name="第一节", 
                        start_time=time(8, 0), end_time=time(8, 45))
        schedule.add_time_slot(slot1)
        
        # 添加课程
        class1 = ClassItem(id="c1", subject_id="math", 
                          time_slot_id="slot1", weekday="monday")
        schedule.add_class(class1)
        
        return schedule


def run_floating_system_tests():
    """运行浮窗系统测试"""
    print("=" * 60)
    print("TimeNest 浮窗系统测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFloatingSystem)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n测试{'成功' if success else '失败'}!")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    run_floating_system_tests()
