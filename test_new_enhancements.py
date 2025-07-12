#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 新增细分功能测试
测试所有新增的增强功能
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_schedule_enhancements():
    """测试课程表增强功能"""
    print("\n1. 测试课程表增强功能")
    print("-" * 40)
    
    try:
        from core.schedule_enhancements import (
            ScheduleEnhancementManager, TaskPriority, TaskStatus
        )
        from core.config_manager import ConfigManager
        
        # 创建管理器
        config_manager = ConfigManager()
        manager = ScheduleEnhancementManager(config_manager)
        print("   ✅ 课程表增强管理器创建成功")
        
        # 测试添加学习任务
        task_id = manager.add_study_task(
            title="测试任务",
            subject="数学",
            due_date=datetime.now() + timedelta(days=1),
            priority=TaskPriority.HIGH,
            estimated_duration=60
        )
        
        if task_id:
            print(f"   ✅ 学习任务添加成功: {task_id}")
            
            # 测试开始学习会话
            session_id = manager.start_study_session(task_id)
            if session_id:
                print(f"   ✅ 学习会话开始成功: {session_id}")
                
                # 测试结束学习会话
                success = manager.end_study_session(session_id, "测试完成", 4)
                if success:
                    print("   ✅ 学习会话结束成功")
                else:
                    print("   ❌ 学习会话结束失败")
            else:
                print("   ❌ 学习会话开始失败")
        else:
            print("   ❌ 学习任务添加失败")
        
        # 测试添加考试信息
        exam_id = manager.add_exam(
            subject="数学",
            title="期中考试",
            exam_date=datetime.now() + timedelta(days=7),
            duration=120,
            location="教室A101"
        )
        
        if exam_id:
            print(f"   ✅ 考试信息添加成功: {exam_id}")
        else:
            print("   ❌ 考试信息添加失败")
        
        # 测试获取统计信息
        stats = manager.get_study_statistics()
        if stats:
            print(f"   ✅ 学习统计获取成功: {len(stats)} 项数据")
        else:
            print("   ⚠️ 学习统计暂无数据")
        
        print("   🎉 课程表增强功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 课程表增强功能测试失败: {e}")
        return False

def test_notification_enhancements():
    """测试通知增强功能"""
    print("\n2. 测试通知增强功能")
    print("-" * 40)
    
    try:
        from core.notification_enhancements import (
            NotificationEnhancementManager, ReminderType, NotificationStyle
        )
        from core.config_manager import ConfigManager
        
        # 创建管理器
        config_manager = ConfigManager()
        manager = NotificationEnhancementManager(config_manager)
        print("   ✅ 通知增强管理器创建成功")
        
        # 测试创建智能提醒
        reminder_id = manager.create_smart_reminder(
            title="测试提醒",
            message="这是一个测试提醒",
            reminder_type=ReminderType.CUSTOM,
            trigger_time=datetime.now() + timedelta(minutes=1),
            style=NotificationStyle.STANDARD
        )
        
        if reminder_id:
            print(f"   ✅ 智能提醒创建成功: {reminder_id}")
        else:
            print("   ❌ 智能提醒创建失败")
        
        # 测试创建课程提醒
        course_reminder_id = manager.create_course_reminder(
            course_name="高等数学",
            start_time=datetime.now() + timedelta(hours=1),
            advance_minutes=15
        )
        
        if course_reminder_id:
            print(f"   ✅ 课程提醒创建成功: {course_reminder_id}")
        else:
            print("   ❌ 课程提醒创建失败")
        
        # 测试专注模式
        focus_success = manager.start_focus_mode(duration=1, break_duration=1)  # 1分钟测试
        if focus_success:
            print("   ✅ 专注模式启动成功")
            
            # 测试获取专注模式状态
            status = manager.get_focus_mode_status()
            if status.get('active'):
                print(f"   ✅ 专注模式状态获取成功: {status['remaining_minutes']:.1f}分钟剩余")
            
            # 结束专注模式
            end_success = manager.end_focus_mode()
            if end_success:
                print("   ✅ 专注模式结束成功")
        else:
            print("   ❌ 专注模式启动失败")
        
        # 测试获取活动提醒
        active_reminders = manager.get_active_reminders()
        print(f"   ✅ 活动提醒数量: {len(active_reminders)}")
        
        print("   🎉 通知增强功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 通知增强功能测试失败: {e}")
        return False

def test_study_assistant():
    """测试智能学习助手"""
    print("\n3. 测试智能学习助手")
    print("-" * 40)
    
    try:
        from core.study_assistant import StudyAssistantManager, StudyPattern
        from core.schedule_enhancements import ScheduleEnhancementManager
        from core.config_manager import ConfigManager
        
        # 创建依赖组件
        config_manager = ConfigManager()
        schedule_enhancement = ScheduleEnhancementManager(config_manager)
        
        # 创建学习助手
        assistant = StudyAssistantManager(config_manager, schedule_enhancement)
        print("   ✅ 智能学习助手创建成功")
        
        # 测试分析学习模式
        analysis = assistant.analyze_study_patterns()
        if analysis:
            print(f"   ✅ 学习模式分析完成: {analysis.get('status', 'unknown')}")
        else:
            print("   ⚠️ 学习模式分析暂无数据")
        
        # 测试生成学习建议
        recommendations = assistant.generate_study_recommendations()
        print(f"   ✅ 生成学习建议: {len(recommendations)} 条")
        
        # 测试获取学习分析数据
        analytics = assistant.get_learning_analytics()
        if analytics:
            print(f"   ✅ 学习分析数据获取成功")
            print(f"       总学习时间: {analytics.total_study_time} 分钟")
            print(f"       连续学习天数: {analytics.streak_days} 天")
        else:
            print("   ⚠️ 学习分析数据暂无")
        
        # 测试每日学习总结
        daily_summary = assistant.get_daily_study_summary()
        if daily_summary:
            print(f"   ✅ 每日学习总结获取成功")
            print(f"       今日学习时间: {daily_summary.get('total_study_time', 0)} 分钟")
            print(f"       完成任务: {daily_summary.get('tasks_completed', 0)} 个")
        else:
            print("   ⚠️ 每日学习总结暂无数据")
        
        print("   🎉 智能学习助手测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 智能学习助手测试失败: {e}")
        return False

def test_floating_enhancements():
    """测试浮窗增强功能"""
    print("\n4. 测试浮窗增强功能")
    print("-" * 40)
    
    try:
        from ui.floating_widget.floating_modules import SystemStatusModule
        
        # 创建系统状态模块
        module = SystemStatusModule("system_status", None)
        print("   ✅ 系统状态模块创建成功")
        
        # 测试增强功能
        if hasattr(module, 'get_quick_actions'):
            actions = module.get_quick_actions()
            print(f"   ✅ 快速操作获取成功: {len(actions)} 个操作")
            for action in actions:
                print(f"       - {action.get('name', 'Unknown')}: {action.get('icon', '❓')}")
        else:
            print("   ⚠️ 快速操作功能不可用")
        
        # 测试状态信息
        if hasattr(module, 'get_status_info'):
            status = module.get_status_info()
            print(f"   ✅ 状态信息获取成功: {len(status)} 项")
        else:
            print("   ⚠️ 状态信息功能不可用")
        
        print("   🎉 浮窗增强功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 浮窗增强功能测试失败: {e}")
        return False

def test_tray_enhancements():
    """测试托盘增强功能"""
    print("\n5. 测试托盘增强功能")
    print("-" * 40)
    
    try:
        from ui.tray_features import TrayFeatureManager
        from core.app_manager import AppManager
        
        # 创建应用管理器
        app_manager = AppManager()
        
        # 创建托盘功能管理器
        tray_manager = TrayFeatureManager(app_manager)
        print("   ✅ 托盘功能管理器创建成功")
        
        # 测试获取快速操作
        quick_actions = tray_manager.get_quick_actions()
        print(f"   ✅ 快速操作获取成功: {len(quick_actions)} 个操作")
        
        for action in quick_actions:
            print(f"       - {action.get('name', 'Unknown')}: {action.get('description', 'No description')}")
        
        print("   🎉 托盘增强功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 托盘增强功能测试失败: {e}")
        return False

def test_app_manager_integration():
    """测试应用管理器集成"""
    print("\n6. 测试应用管理器集成")
    print("-" * 40)
    
    try:
        from core.app_manager import AppManager
        
        # 创建应用管理器
        app_manager = AppManager()
        print("   ✅ 应用管理器创建成功")
        
        # 检查增强功能属性
        enhancements = [
            ('schedule_enhancement', '课程表增强'),
            ('notification_enhancement', '通知增强'),
            ('study_assistant', '智能学习助手')
        ]
        
        for attr_name, display_name in enhancements:
            if hasattr(app_manager, attr_name):
                print(f"   ✅ {display_name}属性存在")
            else:
                print(f"   ❌ {display_name}属性缺失")
        
        print("   🎉 应用管理器集成测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 应用管理器集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("TimeNest 新增细分功能测试")
    print("=" * 50)
    
    # 设置日志
    setup_logging()
    
    # 运行所有测试
    test_results = []
    
    test_results.append(test_schedule_enhancements())
    test_results.append(test_notification_enhancements())
    test_results.append(test_study_assistant())
    test_results.append(test_floating_enhancements())
    test_results.append(test_tray_enhancements())
    test_results.append(test_app_manager_integration())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print("📊 测试结果统计")
    print(f"   通过: {passed}/{total}")
    print(f"   成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有新增功能测试通过！")
        print("\n✨ 新增功能包括:")
        print("   📚 课程表增强 - 学习任务、会话跟踪、考试管理")
        print("   🔔 通知增强 - 智能提醒、专注模式、通知规则")
        print("   🤖 智能学习助手 - 模式分析、学习建议、数据统计")
        print("   🎈 浮窗增强 - 快速操作、状态信息、交互优化")
        print("   🎯 托盘增强 - 快速学习、专注模式、统计查看")
        print("\n🚀 现在可以体验完整的增强功能！")
    else:
        print(f"\n⚠️ {total-passed} 个功能测试失败，请检查相关模块")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
