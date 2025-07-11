#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 附加设置系统测试
"""

import unittest
import uuid
from unittest.mock import Mock, patch
from datetime import time

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from TimeNest.core.attached_settings import (
    AttachedSettingsHostService, 
    AttachedSettingsControlHelper,
    AfterSchoolNotificationAttachedSettings,
    AfterSchoolNotificationAttachedSettingsControl
)
from TimeNest.models.schedule import Subject, TimeLayoutItem, ClassPlan, TimeLayout


class TestAttachedSettingsHostService(unittest.TestCase):
    """测试附加设置主机服务"""
    
    def setUp(self):
        """测试前准备"""
        self.service = AttachedSettingsHostService()
    
    def test_get_attached_settings_by_priority_with_subject(self):
        """测试按优先级获取附加设置 - Subject优先级最高"""
        # 创建测试对象
        subject = Subject(id="test_subject", name="数学")
        subject.attached_settings = {
            "test_id": Mock(is_attach_settings_enabled=True)
        }
        
        time_layout_item = TimeLayoutItem(
            id="test_item", 
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45)
        )
        time_layout_item.attached_settings = {
            "test_id": Mock(is_attach_settings_enabled=True)
        }
        
        # 测试Subject优先级最高
        result = self.service.get_attached_settings_by_priority(
            "test_id", 
            subject=subject, 
            time_layout_item=time_layout_item
        )
        
        self.assertEqual(result, subject.attached_settings["test_id"])
    
    def test_get_attached_settings_by_priority_fallback(self):
        """测试按优先级获取附加设置 - 回退到下一级"""
        # 创建测试对象
        subject = Subject(id="test_subject", name="数学")
        # Subject没有附加设置
        
        time_layout_item = TimeLayoutItem(
            id="test_item", 
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45)
        )
        time_layout_item.attached_settings = {
            "test_id": Mock(is_attach_settings_enabled=True)
        }
        
        # 应该回退到TimeLayoutItem
        result = self.service.get_attached_settings_by_priority(
            "test_id", 
            subject=subject, 
            time_layout_item=time_layout_item
        )
        
        self.assertEqual(result, time_layout_item.attached_settings["test_id"])
    
    def test_get_attached_settings_by_priority_disabled(self):
        """测试附加设置被禁用的情况"""
        subject = Subject(id="test_subject", name="数学")
        subject.attached_settings = {
            "test_id": Mock(is_attach_settings_enabled=False)  # 被禁用
        }
        
        time_layout_item = TimeLayoutItem(
            id="test_item", 
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45)
        )
        time_layout_item.attached_settings = {
            "test_id": Mock(is_attach_settings_enabled=True)
        }
        
        # 应该跳过被禁用的Subject，使用TimeLayoutItem
        result = self.service.get_attached_settings_by_priority(
            "test_id", 
            subject=subject, 
            time_layout_item=time_layout_item
        )
        
        self.assertEqual(result, time_layout_item.attached_settings["test_id"])
    
    def test_get_attached_settings_by_priority_not_found(self):
        """测试找不到附加设置的情况"""
        subject = Subject(id="test_subject", name="数学")
        # 没有附加设置
        
        result = self.service.get_attached_settings_by_priority(
            "test_id", 
            subject=subject
        )
        
        self.assertIsNone(result)


class TestAttachedSettingsControlHelper(unittest.TestCase):
    """测试附加设置控件助手"""
    
    def test_helper_initialization(self):
        """测试助手初始化"""
        settings_id = "8FBC3A26-6D20-44DD-B895-B9411E3DDC51"
        default_settings = AfterSchoolNotificationAttachedSettings()
        
        helper = AttachedSettingsControlHelper(settings_id, default_settings)
        
        self.assertEqual(helper.settings_id, settings_id)
        self.assertEqual(helper.attached_settings, default_settings)
    
    def test_helper_set_settings(self):
        """测试设置附加设置"""
        settings_id = "test_id"
        default_settings = AfterSchoolNotificationAttachedSettings()
        new_settings = AfterSchoolNotificationAttachedSettings(
            enable_notification=False,
            notification_message="自定义消息"
        )
        
        helper = AttachedSettingsControlHelper(settings_id, default_settings)
        helper.attached_settings = new_settings
        
        self.assertEqual(helper.attached_settings, new_settings)


class TestAfterSchoolNotificationAttachedSettings(unittest.TestCase):
    """测试课后通知附加设置"""
    
    def test_default_values(self):
        """测试默认值"""
        settings = AfterSchoolNotificationAttachedSettings()
        
        self.assertTrue(settings.is_attach_settings_enabled)
        self.assertTrue(settings.enable_notification)
        self.assertEqual(settings.notification_message, "放学了！")
        self.assertEqual(settings.delay_minutes, 0)
    
    def test_custom_values(self):
        """测试自定义值"""
        settings = AfterSchoolNotificationAttachedSettings(
            is_attach_settings_enabled=False,
            enable_notification=False,
            notification_message="自定义消息",
            delay_minutes=5
        )
        
        self.assertFalse(settings.is_attach_settings_enabled)
        self.assertFalse(settings.enable_notification)
        self.assertEqual(settings.notification_message, "自定义消息")
        self.assertEqual(settings.delay_minutes, 5)


class TestAfterSchoolNotificationAttachedSettingsControl(unittest.TestCase):
    """测试课后通知附加设置控件"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟PyQt6环境
        self.app = None
        try:
            from PyQt6.QtWidgets import QApplication
            if not QApplication.instance():
                self.app = QApplication([])
        except ImportError:
            self.skipTest("PyQt6 not available")
    
    def tearDown(self):
        """测试后清理"""
        if self.app:
            self.app.quit()
    
    def test_control_initialization(self):
        """测试控件初始化"""
        control = AfterSchoolNotificationAttachedSettingsControl()
        
        # 检查设置ID
        expected_id = "8FBC3A26-6D20-44DD-B895-B9411E3DDC51"
        self.assertEqual(control.attached_settings_control_helper.settings_id, expected_id)
        
        # 检查默认设置
        settings = control.settings
        self.assertIsInstance(settings, AfterSchoolNotificationAttachedSettings)
        self.assertTrue(settings.is_attach_settings_enabled)
    
    def test_control_load_settings(self):
        """测试加载设置到控件"""
        control = AfterSchoolNotificationAttachedSettingsControl()
        
        # 创建自定义设置
        custom_settings = AfterSchoolNotificationAttachedSettings(
            enable_notification=False,
            notification_message="测试消息",
            delay_minutes=10
        )
        
        # 加载设置
        control.load_settings(custom_settings)
        
        # 验证设置已加载
        self.assertEqual(control.settings, custom_settings)
    
    def test_control_save_settings(self):
        """测试从控件保存设置"""
        control = AfterSchoolNotificationAttachedSettingsControl()
        
        # 模拟UI更改
        control.enable_checkbox.setChecked(False)
        control.message_edit.setText("新消息")
        control.delay_spinbox.setValue(15)
        
        # 保存设置
        saved_settings = control.save_settings()
        
        # 验证保存的设置
        self.assertFalse(saved_settings.enable_notification)
        self.assertEqual(saved_settings.notification_message, "新消息")
        self.assertEqual(saved_settings.delay_minutes, 15)


if __name__ == '__main__':
    unittest.main()
