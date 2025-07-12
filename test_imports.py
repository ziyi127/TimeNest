#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入是否正常
"""

import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """测试所有关键导入"""
    print("测试导入...")
    
    try:
        print("1. 测试核心模块...")
        from core.app_manager import AppManager
        print("   ✅ AppManager")
        
        from core.config_manager import ConfigManager
        print("   ✅ ConfigManager")
        
        from core.theme_system import ThemeManager
        print("   ✅ ThemeManager")
        
        from core.floating_manager import FloatingManager
        print("   ✅ FloatingManager")
        
        from core.notification_manager import NotificationManager
        print("   ✅ NotificationManager")
        
        print("2. 测试托盘模块...")
        from ui.system_tray import SystemTray, SystemTrayManager
        print("   ✅ SystemTray, SystemTrayManager")
        
        from ui.tray_features import TrayFeatureManager
        print("   ✅ TrayFeatureManager")
        
        from ui.tray_status_monitor import TrayStatusManager
        print("   ✅ TrayStatusManager")
        
        print("3. 测试UI模块...")
        from ui.notification_window import NotificationWindow
        print("   ✅ NotificationWindow")
        
        from ui.floating_widget import FloatingWidget
        print("   ✅ FloatingWidget")
        
        print("4. 测试PyQt6...")
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
        from PyQt6.QtCore import QObject, pyqtSignal
        from PyQt6.QtGui import QIcon
        print("   ✅ PyQt6 基础组件")
        
        # 测试系统托盘可用性
        if QSystemTrayIcon.isSystemTrayAvailable():
            print("   ✅ 系统托盘可用")
        else:
            print("   ⚠️ 系统托盘不可用")
        
        print("\n🎉 所有导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 其他错误: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        # 创建基本组件
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        print("   ✅ ConfigManager 创建成功")
        
        from core.theme_system import ThemeManager
        theme_manager = ThemeManager(config_manager)
        print("   ✅ ThemeManager 创建成功")
        
        from ui.tray_features import TrayFeatureManager
        feature_manager = TrayFeatureManager()
        print("   ✅ TrayFeatureManager 创建成功")
        
        print("\n🎉 基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("TimeNest 导入测试")
    print("=" * 50)
    
    import_success = test_imports()
    
    if import_success:
        func_success = test_basic_functionality()
        
        if func_success:
            print("\n" + "=" * 50)
            print("✅ 所有测试通过！可以运行 main.py")
            sys.exit(0)
    
    print("\n" + "=" * 50)
    print("❌ 测试失败，请检查依赖和代码")
    sys.exit(1)
