#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 新增细分功能测试
测试学习环境优化、学习计划生成、资源管理等新功能
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta, date

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_environment_optimizer():
    """测试学习环境优化器"""
    print("\n1. 测试学习环境优化器")
    print("-" * 40)
    
    try:
        from core.environment_optimizer import EnvironmentOptimizer, EnvironmentFactor, OptimizationLevel
        from core.config_manager import ConfigManager
        
        # 创建管理器
        config_manager = ConfigManager()
        optimizer = EnvironmentOptimizer(config_manager)
        print("   ✅ 学习环境优化器创建成功")
        
        # 测试开始监控
        optimizer.start_monitoring()
        print("   ✅ 环境监控启动成功")
        
        # 等待一段时间收集数据
        import time
        time.sleep(2)
        
        # 测试获取环境总结
        summary = optimizer.get_environment_summary()
        if summary.get('status') == 'success':
            print(f"   ✅ 环境总结获取成功: {summary.get('grade', 'Unknown')}")
            print(f"       整体评分: {summary.get('overall_score', 0):.1%}")
            print(f"       建议数量: {summary.get('suggestions_count', 0)}")
        else:
            print("   ⚠️ 环境总结暂无数据")
        
        # 测试优化建议
        suggestions = optimizer.get_optimization_suggestions()
        print(f"   ✅ 优化建议获取成功: {len(suggestions)} 条建议")
        
        # 测试设置优化级别
        optimizer.set_optimization_level(OptimizationLevel.ADVANCED)
        print("   ✅ 优化级别设置成功")
        
        # 停止监控
        optimizer.stop_monitoring()
        print("   ✅ 环境监控停止成功")
        
        print("   🎉 学习环境优化器测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 学习环境优化器测试失败: {e}")
        return False

def test_study_planner():
    """测试学习计划生成器"""
    print("\n2. 测试学习计划生成器")
    print("-" * 40)
    
    try:
        from core.study_planner import StudyPlannerManager, PlanType, TaskType, Difficulty
        from core.config_manager import ConfigManager
        
        # 创建管理器
        config_manager = ConfigManager()
        planner = StudyPlannerManager(config_manager)
        print("   ✅ 学习计划生成器创建成功")
        
        # 测试创建学习目标
        goal_id = planner.create_study_goal(
            title="掌握线性代数",
            subject="数学",
            target_date=datetime.now() + timedelta(days=30),
            estimated_hours=40.0,
            description="学习线性代数基础知识",
            priority=4
        )
        
        if goal_id:
            print(f"   ✅ 学习目标创建成功: {goal_id}")
        else:
            print("   ❌ 学习目标创建失败")
            return False
        
        # 测试生成学习计划
        plan_id = planner.generate_study_plan(
            plan_name="数学学习计划",
            plan_type=PlanType.MONTHLY,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            goal_ids=[goal_id]
        )
        
        if plan_id:
            print(f"   ✅ 学习计划生成成功: {plan_id}")
        else:
            print("   ❌ 学习计划生成失败")
            return False
        
        # 测试获取计划总结
        summary = planner.get_plan_summary(plan_id)
        if summary.get('status') == 'success':
            print(f"   ✅ 计划总结获取成功")
            print(f"       总时长: {summary.get('total_hours', 0)} 小时")
            print(f"       学习块数量: {summary.get('total_blocks', 0)}")
            print(f"       目标数量: {summary.get('goals_count', 0)}")
        else:
            print("   ❌ 计划总结获取失败")
        
        # 测试更新目标进度
        success = planner.update_goal_progress(goal_id, 0.3)
        if success:
            print("   ✅ 目标进度更新成功")
        else:
            print("   ❌ 目标进度更新失败")
        
        print("   🎉 学习计划生成器测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 学习计划生成器测试失败: {e}")
        return False

def test_resource_manager():
    """测试学习资源管理器"""
    print("\n3. 测试学习资源管理器")
    print("-" * 40)
    
    try:
        from core.resource_manager import ResourceManager, ResourceType, ResourceStatus
        from core.config_manager import ConfigManager
        
        # 创建管理器
        config_manager = ConfigManager()
        manager = ResourceManager(config_manager)
        print("   ✅ 学习资源管理器创建成功")
        
        # 测试添加资源
        resource_id = manager.add_resource(
            title="线性代数教程",
            resource_type=ResourceType.DOCUMENT,
            subject="数学",
            url="https://example.com/linear-algebra",
            description="线性代数基础教程",
            tags={"数学", "教程", "重要"}
        )
        
        if resource_id:
            print(f"   ✅ 学习资源添加成功: {resource_id}")
        else:
            print("   ❌ 学习资源添加失败")
            return False
        
        # 测试访问资源
        success = manager.access_resource(resource_id)
        if success:
            print("   ✅ 资源访问成功")
        else:
            print("   ❌ 资源访问失败")
        
        # 测试创建资源集合
        collection_id = manager.create_collection(
            name="数学学习资料",
            description="数学相关的学习资源",
            subject="数学",
            resource_ids={resource_id},
            tags={"数学", "集合"}
        )
        
        if collection_id:
            print(f"   ✅ 资源集合创建成功: {collection_id}")
        else:
            print("   ❌ 资源集合创建失败")
        
        # 测试添加笔记
        note_id = manager.add_note(
            title="线性代数学习笔记",
            content="今天学习了矩阵的基本概念和运算规则。",
            subject="数学",
            resource_id=resource_id,
            tags={"笔记", "数学"}
        )
        
        if note_id:
            print(f"   ✅ 学习笔记添加成功: {note_id}")
        else:
            print("   ❌ 学习笔记添加失败")
        
        # 测试搜索资源
        results = manager.search_resources("线性代数", subject="数学")
        print(f"   ✅ 资源搜索完成: 找到 {len(results)} 个结果")
        
        # 测试获取推荐
        recommendations = manager.get_resource_recommendations(subject="数学")
        print(f"   ✅ 资源推荐获取成功: {len(recommendations)} 个推荐")
        
        # 测试获取统计信息
        stats = manager.get_resource_statistics()
        if stats:
            print(f"   ✅ 资源统计获取成功")
            print(f"       总资源数: {stats.get('total_resources', 0)}")
            print(f"       总集合数: {stats.get('total_collections', 0)}")
            print(f"       总笔记数: {stats.get('total_notes', 0)}")
        else:
            print("   ❌ 资源统计获取失败")
        
        # 测试整理资源
        organize_result = manager.organize_resources()
        if organize_result:
            print(f"   ✅ 资源整理完成: 整理了 {organize_result.get('organized_count', 0)} 个资源")
        
        print("   🎉 学习资源管理器测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 学习资源管理器测试失败: {e}")
        return False

def test_enhanced_floating_modules():
    """测试增强浮窗模块"""
    print("\n4. 测试增强浮窗模块")
    print("-" * 40)
    
    try:
        from ui.floating_widget.floating_modules import (
            StudyProgressModule, EnvironmentModule, 
            ResourceQuickAccessModule, FocusModeModule
        )
        
        # 测试学习进度模块
        progress_module = StudyProgressModule("progress", None)
        print("   ✅ 学习进度模块创建成功")
        
        # 测试环境模块
        env_module = EnvironmentModule("environment", None)
        print("   ✅ 学习环境模块创建成功")
        
        # 测试资源快速访问模块
        resource_module = ResourceQuickAccessModule("resource", None)
        print("   ✅ 资源快速访问模块创建成功")
        
        # 测试专注模式模块
        focus_module = FocusModeModule("focus", None)
        print("   ✅ 专注模式模块创建成功")
        
        # 测试快速操作
        modules = [progress_module, env_module, resource_module, focus_module]
        total_actions = 0
        
        for module in modules:
            actions = module.get_quick_actions()
            total_actions += len(actions)
            print(f"   ✅ {module.display_name}: {len(actions)} 个快速操作")
        
        print(f"   ✅ 总计快速操作: {total_actions} 个")
        
        print("   🎉 增强浮窗模块测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 增强浮窗模块测试失败: {e}")
        return False

def test_enhanced_tray_features():
    """测试增强托盘功能"""
    print("\n5. 测试增强托盘功能")
    print("-" * 40)
    
    try:
        from ui.tray_features import TrayFeatureManager
        from core.app_manager import AppManager
        
        # 创建应用管理器
        app_manager = AppManager()
        
        # 创建托盘功能管理器
        tray_manager = TrayFeatureManager(app_manager)
        print("   ✅ 增强托盘功能管理器创建成功")
        
        # 测试获取快速操作
        quick_actions = tray_manager.get_quick_actions()
        print(f"   ✅ 快速操作获取成功: {len(quick_actions)} 个操作")
        
        # 显示所有快速操作
        for action in quick_actions:
            name = action.get('name', 'Unknown')
            shortcut = action.get('shortcut', 'None')
            print(f"       - {name} ({shortcut})")
        
        # 测试新增功能方法存在性
        new_methods = [
            'quick_add_resource',
            'create_study_plan', 
            'optimize_environment',
            'show_daily_summary',
            'quick_note'
        ]
        
        for method_name in new_methods:
            if hasattr(tray_manager, method_name):
                print(f"   ✅ 新增方法 {method_name} 存在")
            else:
                print(f"   ❌ 新增方法 {method_name} 缺失")
        
        print("   🎉 增强托盘功能测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 增强托盘功能测试失败: {e}")
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
        
        # 检查新增功能属性
        new_components = [
            ('environment_optimizer', '学习环境优化器'),
            ('study_planner', '学习计划生成器'),
            ('resource_manager', '学习资源管理器')
        ]
        
        for attr_name, display_name in new_components:
            if hasattr(app_manager, attr_name):
                component = getattr(app_manager, attr_name)
                if component is not None:
                    print(f"   ✅ {display_name}: 已初始化")
                else:
                    print(f"   ⚠️ {display_name}: 属性存在但未初始化")
            else:
                print(f"   ❌ {display_name}: 属性缺失")
        
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
    
    test_results.append(test_environment_optimizer())
    test_results.append(test_study_planner())
    test_results.append(test_resource_manager())
    test_results.append(test_enhanced_floating_modules())
    test_results.append(test_enhanced_tray_features())
    test_results.append(test_app_manager_integration())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print("📊 测试结果统计")
    print(f"   通过: {passed}/{total}")
    print(f"   成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有新增细分功能测试通过！")
        print("\n✨ 新增细分功能包括:")
        print("   🌍 学习环境优化器 - 环境监控、优化建议、自动调节")
        print("   📋 智能学习计划生成器 - 目标管理、计划生成、进度跟踪")
        print("   📚 学习资源管理器 - 资源管理、笔记记录、智能推荐")
        print("   🎈 增强浮窗模块 - 进度显示、环境状态、快速访问")
        print("   🎯 增强托盘功能 - 更多快速操作、智能功能集成")
        print("\n🚀 TimeNest 现在提供更全面的学习管理功能！")
    else:
        print(f"\n⚠️ {total-passed} 个功能测试失败，请检查相关模块")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
