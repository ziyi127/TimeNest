#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 综合功能演示
展示项目的各个核心功能
"""

import sys
import os
import logging
from datetime import time, date, datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from TimeNest.models.schedule import Schedule, Subject, TimeSlot, ClassItem, TimeLayoutItem, TimeLayout, ClassPlan
from TimeNest.core.theme_system import ThemeManager, ThemeType
from TimeNest.core.notification_system_v2 import NotificationSystemV2, NotificationRequest, NotificationPriority
from TimeNest.core.plugin_system import PluginManager
from TimeNest.core.attached_settings import AttachedSettingsHostService, AfterSchoolNotificationAttachedSettings
from TimeNest.core.data_import_export import DataImportExportManager


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demo_schedule_system():
    """演示课程表系统"""
    print("=" * 50)
    print("课程表系统演示")
    print("=" * 50)
    
    # 创建课程表
    schedule = Schedule(name="高三(1)班课程表", description="2024年春季学期课程表")
    
    # 添加科目
    subjects = [
        Subject(id="math", name="数学", teacher="张老师", color="#FF5722"),
        Subject(id="chinese", name="语文", teacher="李老师", color="#2196F3"),
        Subject(id="english", name="英语", teacher="王老师", color="#4CAF50"),
        Subject(id="physics", name="物理", teacher="赵老师", color="#FF9800"),
        Subject(id="chemistry", name="化学", teacher="陈老师", color="#9C27B0")
    ]
    
    for subject in subjects:
        schedule.add_subject(subject)
    
    print(f"✓ 添加了 {len(subjects)} 个科目")
    
    # 添加时间段
    time_slots = [
        TimeSlot(id="slot1", name="第一节", start_time=time(8, 0), end_time=time(8, 45)),
        TimeSlot(id="slot2", name="第二节", start_time=time(8, 55), end_time=time(9, 40)),
        TimeSlot(id="slot3", name="第三节", start_time=time(10, 0), end_time=time(10, 45)),
        TimeSlot(id="slot4", name="第四节", start_time=time(10, 55), end_time=time(11, 40)),
        TimeSlot(id="slot5", name="第五节", start_time=time(14, 0), end_time=time(14, 45)),
        TimeSlot(id="slot6", name="第六节", start_time=time(14, 55), end_time=time(15, 40))
    ]
    
    for slot in time_slots:
        schedule.add_time_slot(slot)
    
    print(f"✓ 添加了 {len(time_slots)} 个时间段")
    
    # 添加课程安排
    class_arrangements = [
        # 周一
        ClassItem(id="c1", subject_id="math", time_slot_id="slot1", weekday="monday", classroom="A101"),
        ClassItem(id="c2", subject_id="chinese", time_slot_id="slot2", weekday="monday", classroom="A101"),
        ClassItem(id="c3", subject_id="english", time_slot_id="slot3", weekday="monday", classroom="A101"),
        ClassItem(id="c4", subject_id="physics", time_slot_id="slot4", weekday="monday", classroom="B201"),
        
        # 周二
        ClassItem(id="c5", subject_id="chemistry", time_slot_id="slot1", weekday="tuesday", classroom="C301"),
        ClassItem(id="c6", subject_id="math", time_slot_id="slot2", weekday="tuesday", classroom="A101"),
        ClassItem(id="c7", subject_id="chinese", time_slot_id="slot3", weekday="tuesday", classroom="A101"),
        ClassItem(id="c8", subject_id="english", time_slot_id="slot4", weekday="tuesday", classroom="A101"),
    ]
    
    for class_item in class_arrangements:
        schedule.add_class(class_item)
    
    print(f"✓ 添加了 {len(class_arrangements)} 个课程安排")
    
    # 验证课程表
    errors = schedule.validate()
    if not errors:
        print("✓ 课程表数据验证通过")
    else:
        print(f"✗ 课程表验证失败: {errors}")
    
    # 获取统计信息
    stats = schedule.get_statistics()
    print(f"✓ 课程表统计: {stats}")
    
    return schedule


def demo_theme_system():
    """演示主题系统"""
    print("\n" + "=" * 50)
    print("主题系统演示")
    print("=" * 50)
    
    try:
        # 创建主题管理器
        theme_manager = ThemeManager()
        
        # 获取可用主题
        themes = theme_manager.get_available_themes()
        print(f"✓ 可用主题数量: {len(themes)}")
        
        for theme in themes:
            print(f"  - {theme.metadata.name} ({theme.metadata.theme_type.value})")
        
        # 切换主题
        success = theme_manager.apply_theme('builtin_dark')
        print(f"✓ 切换到深色主题: {'成功' if success else '失败'}")
        
        current_theme = theme_manager.get_current_theme()
        if current_theme:
            print(f"✓ 当前主题: {current_theme.metadata.name}")
        
        return theme_manager
        
    except Exception as e:
        print(f"✗ 主题系统演示失败: {e}")
        return None


def demo_notification_system():
    """演示通知系统"""
    print("\n" + "=" * 50)
    print("通知系统v2演示")
    print("=" * 50)
    
    try:
        # 创建通知系统
        notification_system = NotificationSystemV2()
        
        # 获取可用渠道
        channels = notification_system.get_available_channels()
        print(f"✓ 可用通知渠道: {len(channels)}")
        for channel in channels:
            print(f"  - {channel.name} ({channel.channel_id})")
        
        # 发送测试通知
        request = NotificationRequest(
            title='课程提醒',
            message='数学课即将在A101教室开始',
            channels=['popup', 'sound'],
            priority=NotificationPriority.HIGH
        )
        
        success = notification_system.send_notification(request)
        print(f"✓ 发送通知: {'成功' if success else '失败'}")
        
        # 使用模板发送通知
        success = notification_system.send_notification_with_template(
            'class_start',
            {
                'subject_name': '数学',
                'classroom': 'A101'
            },
            channels=['popup']
        )
        print(f"✓ 使用模板发送通知: {'成功' if success else '失败'}")
        
        # 获取统计信息
        stats = notification_system.get_statistics()
        print(f"✓ 通知系统统计: {stats}")
        
        return notification_system
        
    except Exception as e:
        print(f"✗ 通知系统演示失败: {e}")
        return None


def demo_plugin_system():
    """演示插件系统"""
    print("\n" + "=" * 50)
    print("插件系统演示")
    print("=" * 50)
    
    try:
        # 创建插件管理器
        plugin_manager = PluginManager()
        
        # 加载插件
        success = plugin_manager.load_plugins()
        print(f"✓ 加载插件: {'成功' if success else '失败'}")
        
        # 获取统计信息
        stats = plugin_manager.get_statistics()
        print(f"✓ 插件统计: {stats}")
        
        # 获取事件总线
        event_bus = plugin_manager.get_event_bus()
        print(f"✓ 事件总线已创建")
        
        return plugin_manager
        
    except Exception as e:
        print(f"✗ 插件系统演示失败: {e}")
        return None


def demo_attached_settings():
    """演示附加设置系统"""
    print("\n" + "=" * 50)
    print("附加设置系统演示")
    print("=" * 50)
    
    try:
        # 创建附加设置服务
        settings_service = AttachedSettingsHostService()
        
        # 创建测试对象
        subject = Subject(id="math", name="数学")
        subject.attached_settings = {
            "test_id": type('MockSettings', (), {
                'is_attach_settings_enabled': True,
                'data': 'subject_data'
            })()
        }
        
        time_layout_item = TimeLayoutItem(
            id="item1", 
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45)
        )
        time_layout_item.attached_settings = {
            "test_id": type('MockSettings', (), {
                'is_attach_settings_enabled': True,
                'data': 'item_data'
            })()
        }
        
        # 测试优先级获取
        result = settings_service.get_attached_settings_by_priority(
            'test_id',
            subject=subject,
            time_layout_item=time_layout_item
        )
        
        if result and hasattr(result, 'data'):
            print(f"✓ 优先级测试通过: 获取到 {result.data}")
        else:
            print("✗ 优先级测试失败")
        
        # 测试课后通知设置
        settings = AfterSchoolNotificationAttachedSettings()
        print(f"✓ 默认通知设置: {settings.notification_message}")
        
        return settings_service
        
    except Exception as e:
        print(f"✗ 附加设置系统演示失败: {e}")
        return None


def demo_data_import_export(schedule):
    """演示数据导入导出"""
    print("\n" + "=" * 50)
    print("数据导入导出演示")
    print("=" * 50)
    
    try:
        # 创建导入导出管理器
        import_export_manager = DataImportExportManager()
        
        # 获取支持的格式
        formats = import_export_manager.get_supported_formats()
        print(f"✓ 支持的导入格式: {formats['import']}")
        print(f"✓ 支持的导出格式: {formats['export']}")
        
        # 导出为JSON
        json_file = "/tmp/test_schedule.json"
        success = import_export_manager.export_schedule(schedule, json_file)
        print(f"✓ 导出JSON: {'成功' if success else '失败'}")
        
        if success:
            # 导入JSON
            imported_schedule = import_export_manager.import_schedule(json_file)
            if imported_schedule:
                print(f"✓ 导入JSON成功: {imported_schedule.name}")
            else:
                print("✗ 导入JSON失败")
        
        return import_export_manager
        
    except Exception as e:
        print(f"✗ 数据导入导出演示失败: {e}")
        return None


def main():
    """主函数"""
    print("TimeNest 综合功能演示")
    print("=" * 60)
    
    # 设置日志
    setup_logging()
    
    # 演示各个系统
    schedule = demo_schedule_system()
    theme_manager = demo_theme_system()
    notification_system = demo_notification_system()
    plugin_manager = demo_plugin_system()
    settings_service = demo_attached_settings()
    
    if schedule:
        import_export_manager = demo_data_import_export(schedule)
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    
    # 总结
    print("\n功能总结:")
    print("✓ 课程表数据模型 - 完整的课程表管理功能")
    print("✓ 主题系统 - 支持多主题切换和自定义")
    print("✓ 通知系统v2 - 多渠道、链式提醒、模板支持")
    print("✓ 插件系统 - 插件加载、管理、事件总线")
    print("✓ 附加设置系统 - 优先级设置、组件配置")
    print("✓ 数据导入导出 - 多格式支持、数据迁移")
    print("✓ Excel导出增强 - 多种样式和格式")
    print("✓ 组件系统改进 - 滚动、轮播、天气组件")


if __name__ == "__main__":
    main()
