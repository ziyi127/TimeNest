#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 TimeNest 核心模块导入
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试核心模块导入"""
    print("开始测试 TimeNest 核心模块导入...")
    
    try:
        # 测试核心模块
        print("导入配置管理器...")
        from TimeNest.core.config_manager import ConfigManager
        print("✓ 配置管理器导入成功")
        
        print("导入时间管理器...")
        from TimeNest.core.time_manager import TimeManager
        print("✓ 时间管理器导入成功")
        
        print("导入课程表管理器...")
        from TimeNest.core.schedule_manager import ScheduleManager
        print("✓ 课程表管理器导入成功")
        
        print("导入通知管理器...")
        from TimeNest.core.notification_manager import NotificationManager
        print("✓ 通知管理器导入成功")
        
        print("导入通知服务...")
        from TimeNest.core.notification_service import NotificationHostService
        print("✓ 通知服务导入成功")
        
        print("导入附加设置服务...")
        from TimeNest.core.attached_settings import AttachedSettingsHostService
        print("✓ 附加设置服务导入成功")
        
        print("导入天气服务...")
        from TimeNest.core.weather_service import WeatherService
        print("✓ 天气服务导入成功")
        
        print("导入组件系统...")
        from TimeNest.core.component_system import ComponentManager
        print("✓ 组件系统导入成功")
        
        print("导入应用管理器...")
        from TimeNest.core.app_manager import AppManager
        print("✓ 应用管理器导入成功")
        
        # 测试UI模块
        print("\n测试UI模块...")
        try:
            import PyQt6
            print("✓ PyQt6 可用")
            
            print("导入主窗口...")
            from TimeNest.ui.main_window import MainWindow
            print("✓ 主窗口导入成功")
            
            print("导入天气组件...")
            from TimeNest.ui.weather_widget import WeatherWidget
            print("✓ 天气组件导入成功")
            
            print("导入通知组件...")
            from TimeNest.ui.notification_widget import NotificationWidget
            print("✓ 通知组件导入成功")
            
        except ImportError as e:
            print(f"⚠ UI模块导入失败: {e}")
            print("这可能是因为缺少PyQt6或在无GUI环境中运行")
        
        print("\n✅ 所有核心模块导入测试完成!")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n开始测试基本功能...")
    
    try:
        # 测试配置管理器
        from TimeNest.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        print("✓ 配置管理器创建成功")
        
        # 测试时间管理器
        from TimeNest.core.time_manager import TimeManager
        time_manager = TimeManager()
        print("✓ 时间管理器创建成功")
        
        # 测试课程表管理器
        from TimeNest.core.schedule_manager import ScheduleManager
        schedule_manager = ScheduleManager(config_manager)
        print("✓ 课程表管理器创建成功")
        
        print("\n✅ 基本功能测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("TimeNest 模块测试")
    print("=" * 50)
    
    # 测试导入
    import_success = test_imports()
    
    if import_success:
        # 测试基本功能
        func_success = test_basic_functionality()
        
        if func_success:
            print("\n🎉 所有测试通过! TimeNest 核心功能正常.")
            sys.exit(0)
        else:
            print("\n❌ 功能测试失败.")
            sys.exit(1)
    else:
        print("\n❌ 导入测试失败.")
        sys.exit(1)