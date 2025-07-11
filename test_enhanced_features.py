#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 增强功能测试脚本
测试所有新实现的功能特性
"""

import sys
import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_remind_api_v2():
    """测试Remind API v2功能"""
    print("\n=== 测试 Remind API v2 ===")
    
    try:
        from core.remind_api_v2 import (
            RemindAPIv2, ChainedReminder, ReminderAction, 
            ReminderCondition, ReminderChannel, ReminderPriority
        )
        
        # 创建模拟应用管理器
        class MockAppManager:
            def __init__(self):
                self.notification_manager = None
                self.floating_manager = None
        
        app_manager = MockAppManager()
        remind_api = RemindAPIv2(app_manager)
        
        # 创建测试提醒
        condition = ReminderCondition(
            type="time",
            value=(datetime.now() + timedelta(seconds=5)).isoformat(),
            operator="<="
        )
        
        action = ReminderAction(
            channel=ReminderChannel.POPUP,
            title="测试提醒",
            message="这是一个测试提醒消息"
        )
        
        reminder = ChainedReminder(
            id="test_reminder_1",
            name="测试提醒",
            description="用于测试的提醒",
            conditions=[condition],
            actions=[action],
            priority=ReminderPriority.NORMAL
        )
        
        # 添加提醒
        success = remind_api.add_reminder(reminder)
        print(f"✓ 添加提醒: {'成功' if success else '失败'}")
        
        # 获取提醒列表
        reminders = remind_api.get_reminders()
        print(f"✓ 提醒数量: {len(reminders)}")
        
        # 清理
        remind_api.cleanup()
        print("✓ Remind API v2 测试完成")
        
    except Exception as e:
        print(f"✗ Remind API v2 测试失败: {e}")


def test_excel_export_enhanced():
    """测试Excel导出增强功能"""
    print("\n=== 测试 Excel导出增强 ===")
    
    try:
        from core.excel_export_enhanced import (
            ExcelExportEnhanced, ExportOptions, ExportTemplate, ExportFormat
        )
        
        exporter = ExcelExportEnhanced()
        
        # 测试数据
        schedule_data = {
            'courses': [
                {
                    'id': 'course_1',
                    'name': '高等数学',
                    'teacher': '张教授',
                    'classroom': 'A101',
                    'day': 0,
                    'start_time': '08:00',
                    'end_time': '09:40',
                    'credits': 3,
                    'course_type': '必修课'
                },
                {
                    'id': 'course_2',
                    'name': '大学英语',
                    'teacher': '李老师',
                    'classroom': 'B203',
                    'day': 1,
                    'start_time': '10:00',
                    'end_time': '11:40',
                    'credits': 2,
                    'course_type': '必修课'
                }
            ]
        }
        
        # 测试不同格式导出
        formats = [
            (ExportFormat.CSV, "test_schedule.csv"),
            (ExportFormat.HTML, "test_schedule.html")
        ]
        
        for export_format, filename in formats:
            options = ExportOptions(
                template=ExportTemplate.DETAILED,
                format=export_format,
                include_statistics=True,
                custom_title="测试课程表"
            )
            
            success = exporter.export_schedule(schedule_data, filename, options)
            print(f"✓ {export_format.value.upper()}导出: {'成功' if success else '失败'}")
        
        # 测试模板获取
        templates = exporter.get_available_templates()
        print(f"✓ 可用模板数量: {len(templates)}")
        
        print("✓ Excel导出增强测试完成")
        
    except Exception as e:
        print(f"✗ Excel导出增强测试失败: {e}")


def test_plugin_interaction_enhanced():
    """测试插件交互增强功能"""
    print("\n=== 测试 插件交互增强 ===")
    
    try:
        from core.plugin_interaction_enhanced import (
            PluginInteractionManager, PluginInterface, PluginMetadata,
            PluginDependency, PluginDependencyType
        )
        
        manager = PluginInteractionManager()
        
        # 创建测试接口
        def test_method(message: str) -> str:
            return f"处理消息: {message}"
        
        interface = PluginInterface(
            name="test_interface",
            version="1.0.0",
            description="测试接口"
        )
        interface.add_method("process_message", test_method)
        interface.add_event("message_processed")
        
        # 注册接口
        success = manager.register_plugin_interface("test_plugin", interface)
        print(f"✓ 注册接口: {'成功' if success else '失败'}")
        
        # 调用接口方法
        try:
            result = manager.call_plugin_method("test_interface", "process_message", "Hello World")
            print(f"✓ 方法调用结果: {result}")
        except Exception as e:
            print(f"✗ 方法调用失败: {e}")
        
        # 测试事件系统
        def event_handler(data):
            print(f"✓ 收到事件: {data}")
        
        manager.subscribe_event("test_event", event_handler)
        manager.publish_event("test_event", {"message": "测试事件数据"})
        
        # 获取接口信息
        interfaces = manager.get_available_interfaces()
        print(f"✓ 可用接口数量: {len(interfaces)}")
        
        # 获取统计信息
        stats = manager.get_call_statistics()
        print(f"✓ 调用统计: {stats}")
        
        # 清理
        manager.cleanup()
        print("✓ 插件交互增强测试完成")
        
    except Exception as e:
        print(f"✗ 插件交互增强测试失败: {e}")


def test_enhanced_floating_modules():
    """测试增强浮窗模块"""
    print("\n=== 测试 增强浮窗模块 ===")
    
    try:
        from ui.floating_widget.enhanced_modules import (
            EnhancedFloatingModules, ScrollingTextWidget, WeatherWidget,
            CarouselWidget, AnimatedProgressBar, NotificationBanner
        )
        
        # 创建应用实例（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        modules = EnhancedFloatingModules()
        
        # 测试滚动文本
        scrolling_text = modules.create_scrolling_text("这是一个测试滚动文本")
        print("✓ 滚动文本组件创建成功")
        
        # 测试天气组件
        weather_widget = modules.create_weather_widget()
        print("✓ 天气组件创建成功")
        
        # 测试轮播组件
        carousel = modules.create_carousel()
        print("✓ 轮播组件创建成功")
        
        # 测试进度条
        progress_bar = modules.create_progress_bar()
        progress_bar.set_progress(75)
        print("✓ 动画进度条创建成功")
        
        # 测试通知横幅
        notification_banner = modules.create_notification_banner("测试通知")
        print("✓ 通知横幅创建成功")
        
        # 获取模块
        module = modules.get_module('weather')
        print(f"✓ 获取模块: {'成功' if module else '失败'}")
        
        # 清理
        modules.cleanup()
        print("✓ 增强浮窗模块测试完成")
        
    except Exception as e:
        print(f"✗ 增强浮窗模块测试失败: {e}")


def test_app_manager_integration():
    """测试应用管理器集成"""
    print("\n=== 测试 应用管理器集成 ===")
    
    try:
        from core.app_manager import AppManager
        
        # 创建应用实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建应用管理器
        app_manager = AppManager()
        
        # 检查增强功能是否正确初始化
        features = [
            ('plugin_interaction_manager', '插件交互管理器'),
            ('remind_api_v2', 'Remind API v2'),
            ('excel_exporter', 'Excel导出增强'),
            ('theme_marketplace', '主题市场'),
            ('time_calibration_service', '时间校准服务')
        ]
        
        for attr_name, feature_name in features:
            if hasattr(app_manager, attr_name):
                feature = getattr(app_manager, attr_name)
                status = "已初始化" if feature is not None else "未初始化"
                print(f"✓ {feature_name}: {status}")
            else:
                print(f"✗ {feature_name}: 不存在")
        
        # 测试清理
        app_manager.cleanup()
        print("✓ 应用管理器集成测试完成")
        
    except Exception as e:
        print(f"✗ 应用管理器集成测试失败: {e}")


def main():
    """主测试函数"""
    print("TimeNest 增强功能测试开始")
    print("=" * 50)
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    
    # 运行所有测试
    test_remind_api_v2()
    test_excel_export_enhanced()
    test_plugin_interaction_enhanced()
    test_enhanced_floating_modules()
    test_app_manager_integration()
    
    print("\n" + "=" * 50)
    print("所有测试完成！")
    
    # 显示完成消息
    QMessageBox.information(None, "测试完成", "TimeNest 增强功能测试已完成！\n请查看控制台输出了解详细结果。")


if __name__ == "__main__":
    main()
