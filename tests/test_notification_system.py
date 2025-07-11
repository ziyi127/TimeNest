#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知系统测试
验证通知系统的功能完整性和重构质量
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

from core.notification_manager import (
    NotificationManager, NotificationChannel, PopupChannel, 
    TrayChannel, SoundChannel, VoiceChannel, EmailChannel,
    NotificationChannelType
)
from core.config_manager import ConfigManager
from core.notification_service import NotificationPriority, NotificationType
from models.schedule import Schedule, Subject, TimeSlot, ClassItem


class TestNotificationSystem(unittest.TestCase):
    """通知系统测试类"""
    
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
        # 创建模拟的配置管理器
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get.return_value = {}
        self.config_manager.set.return_value = None
        
        # 创建通知管理器
        self.notification_manager = NotificationManager(self.config_manager)
    
    def tearDown(self):
        """清理测试"""
        if self.notification_manager:
            self.notification_manager.cleanup()
    
    def test_notification_manager_initialization(self):
        """测试通知管理器初始化"""
        self.assertIsNotNone(self.notification_manager)
        self.assertEqual(self.notification_manager.config_manager, self.config_manager)
        self.assertIsInstance(self.notification_manager.settings, dict)
        self.assertIsInstance(self.notification_manager.channels, dict)
        
        # 验证内置通道注册
        expected_channels = ['popup', 'tray', 'sound', 'voice', 'email']
        for channel_name in expected_channels:
            self.assertIn(channel_name, self.notification_manager.channels)
    
    def test_notification_channels(self):
        """测试通知通道"""
        # 测试弹窗通道
        popup_channel = self.notification_manager.channels['popup']
        self.assertIsInstance(popup_channel, PopupChannel)
        self.assertEqual(popup_channel.channel_id, 'popup')
        self.assertTrue(popup_channel.is_available())
        
        # 测试托盘通道
        tray_channel = self.notification_manager.channels['tray']
        self.assertIsInstance(tray_channel, TrayChannel)
        self.assertEqual(tray_channel.channel_id, 'tray')
        
        # 测试音效通道
        sound_channel = self.notification_manager.channels['sound']
        self.assertIsInstance(sound_channel, SoundChannel)
        self.assertEqual(sound_channel.channel_id, 'sound')
        self.assertTrue(sound_channel.is_available())
        
        # 测试语音通道
        voice_channel = self.notification_manager.channels['voice']
        self.assertIsInstance(voice_channel, VoiceChannel)
        self.assertEqual(voice_channel.channel_id, 'voice')
        
        # 测试邮件通道
        email_channel = self.notification_manager.channels['email']
        self.assertIsInstance(email_channel, EmailChannel)
        self.assertEqual(email_channel.channel_id, 'email')
    
    def test_send_notification(self):
        """测试发送通知"""
        # 模拟通道发送成功
        for channel in self.notification_manager.channels.values():
            channel.send = Mock(return_value=True)
            channel.is_available = Mock(return_value=True)
        
        # 发送测试通知
        notification_id = self.notification_manager.send_notification(
            title="测试通知",
            message="这是一个测试消息",
            channels=['popup', 'sound'],
            priority=2
        )
        
        self.assertIsNotNone(notification_id)
        self.assertTrue(notification_id.startswith('notification_'))
        
        # 验证通道被调用
        self.notification_manager.channels['popup'].send.assert_called_once()
        self.notification_manager.channels['sound'].send.assert_called_once()
    
    def test_batch_notifications(self):
        """测试批量通知"""
        # 模拟通道发送成功
        for channel in self.notification_manager.channels.values():
            channel.send = Mock(return_value=True)
            channel.is_available = Mock(return_value=True)
        
        # 准备批量通知
        notifications = [
            {
                'title': '通知1',
                'message': '消息1',
                'channels': ['popup']
            },
            {
                'title': '通知2',
                'message': '消息2',
                'channels': ['sound']
            }
        ]
        
        # 发送批量通知
        batch_id = self.notification_manager.send_batch_notifications(notifications)
        
        self.assertIsNotNone(batch_id)
        self.assertTrue(batch_id.startswith('batch_'))
        self.assertIn(batch_id, self.notification_manager.batch_notifications)
    
    def test_channel_management(self):
        """测试通道管理"""
        # 测试获取可用通道
        available_channels = self.notification_manager.get_available_channels()
        self.assertIsInstance(available_channels, list)
        
        # 测试设置通道状态
        success = self.notification_manager.set_channel_enabled('popup', False)
        self.assertTrue(success)
        self.assertFalse(self.notification_manager.channels['popup'].enabled)
        
        # 测试注册新通道
        class TestChannel(NotificationChannel):
            def __init__(self):
                super().__init__("test", "测试通道")
            
            def send(self, title: str, message: str, **kwargs) -> bool:
                return True
            
            def is_available(self) -> bool:
                return True
        
        test_channel = TestChannel()
        success = self.notification_manager.register_channel('test', test_channel)
        self.assertTrue(success)
        self.assertIn('test', self.notification_manager.channels)
        
        # 测试注销通道
        success = self.notification_manager.unregister_channel('test')
        self.assertTrue(success)
        self.assertNotIn('test', self.notification_manager.channels)
    
    def test_template_rendering(self):
        """测试模板渲染"""
        template_data = {
            'subject': '数学',
            'classroom': 'A101',
            'teacher': '张老师'
        }
        
        title = "上课提醒"
        message = "{subject} 即将在 {classroom} 开始，任课老师：{teacher}"
        
        rendered_title, rendered_message = self.notification_manager._render_template(
            title, message, template_data
        )
        
        self.assertEqual(rendered_title, "上课提醒")
        self.assertEqual(rendered_message, "数学 即将在 A101 开始，任课老师：张老师")
    
    def test_do_not_disturb(self):
        """测试免打扰模式"""
        # 设置免打扰时间
        self.notification_manager.settings['do_not_disturb'] = {
            'enabled': True,
            'start_time': '22:00',
            'end_time': '07:00'
        }
        
        # 测试免打扰时间检查
        test_time = datetime.now().replace(hour=23, minute=0, second=0, microsecond=0)
        is_dnd = self.notification_manager._is_do_not_disturb_time(test_time)
        self.assertTrue(is_dnd)
        
        # 测试非免打扰时间
        test_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        is_dnd = self.notification_manager._is_do_not_disturb_time(test_time)
        self.assertFalse(is_dnd)
    
    def test_notification_history(self):
        """测试通知历史"""
        # 模拟发送通知
        notification_data = {
            'id': 'test_notification',
            'title': '测试',
            'message': '测试消息',
            'channels': ['popup'],
            'priority': 1,
            'timestamp': datetime.now().isoformat()
        }
        
        self.notification_manager._record_notification_history(notification_data, True)
        
        # 获取历史记录
        history = self.notification_manager.get_notification_history()
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['id'], 'test_notification')
        self.assertTrue(history[0]['success'])
    
    def test_settings_management(self):
        """测试设置管理"""
        # 获取设置
        settings = self.notification_manager.get_settings()
        self.assertIsInstance(settings, dict)
        
        # 更新设置
        new_settings = {
            'channels': {
                'popup': {
                    'enabled': False,
                    'duration': 3000
                }
            }
        }
        
        success = self.notification_manager.update_settings(new_settings)
        self.assertTrue(success)
        
        # 验证设置已更新
        updated_settings = self.notification_manager.get_settings()
        self.assertFalse(updated_settings['channels']['popup']['enabled'])
        self.assertEqual(updated_settings['channels']['popup']['duration'], 3000)
    
    def test_statistics(self):
        """测试统计信息"""
        stats = self.notification_manager.get_statistics()
        self.assertIsInstance(stats, dict)
        
        expected_keys = [
            'total_notifications', 'successful_notifications', 'failed_notifications',
            'success_rate', 'active_timers', 'active_windows', 'channels'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
    
    def test_test_functionality(self):
        """测试测试功能"""
        # 模拟通道发送成功
        for channel in self.notification_manager.channels.values():
            channel.send = Mock(return_value=True)
            channel.is_available = Mock(return_value=True)
        
        # 测试单个通知
        notification_id = self.notification_manager.test_notification()
        self.assertIsNotNone(notification_id)
        
        # 测试所有通道
        results = self.notification_manager.test_all_channels()
        self.assertIsInstance(results, dict)
        
        for channel_name in self.notification_manager.channels.keys():
            self.assertIn(channel_name, results)


def run_notification_system_tests():
    """运行通知系统测试"""
    print("=" * 60)
    print("TimeNest 通知系统测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNotificationSystem)
    
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
    run_notification_system_tests()
