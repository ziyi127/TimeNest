#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 紧急测试脚本
验证基本功能是否正常
"""

import sys
import logging
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_imports():
    """测试基本导入"""
    print("🔍 测试基本导入...")
    
    try:
        # 测试PyQt6
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
        from PyQt6.QtCore import QObject
        from PyQt6.QtGui import QIcon
        print("   ✅ PyQt6 导入成功")
        
        # 测试核心模块
        from core.app_manager import AppManager
        print("   ✅ AppManager 导入成功")
        
        from core.config_manager import ConfigManager
        print("   ✅ ConfigManager 导入成功")
        
        from core.theme_system import ThemeManager
        print("   ✅ ThemeManager 导入成功")
        
        # 测试UI模块
        from ui.system_tray import SystemTray, SystemTrayManager
        print("   ✅ SystemTray 导入成功")
        
        from ui.tray_features import TrayFeatureManager
        print("   ✅ TrayFeatureManager 导入成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🔧 测试基本功能...")
    
    try:
        # 创建应用
        app = QApplication(sys.argv)
        print("   ✅ QApplication 创建成功")
        
        # 检查系统托盘
        if QSystemTrayIcon.isSystemTrayAvailable():
            print("   ✅ 系统托盘可用")
        else:
            print("   ⚠️ 系统托盘不可用")
        
        # 测试配置管理器
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        print("   ✅ ConfigManager 创建成功")
        
        # 测试应用管理器
        from core.app_manager import AppManager
        app_manager = AppManager()
        print("   ✅ AppManager 创建成功")
        
        # 测试托盘功能管理器
        from ui.tray_features import TrayFeatureManager
        tray_features = TrayFeatureManager(app_manager)
        print("   ✅ TrayFeatureManager 创建成功")
        
        # 测试托盘管理器
        from ui.system_tray import SystemTrayManager
        tray_manager = SystemTrayManager()
        print("   ✅ SystemTrayManager 创建成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safe_startup():
    """测试安全启动"""
    print("\n🚀 测试安全启动...")
    
    try:
        # 创建最小化的应用实例
        app = QApplication(sys.argv)
        
        # 只测试核心组件
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        from core.theme_system import ThemeManager
        theme_manager = ThemeManager(config_manager)
        
        print("   ✅ 核心组件启动成功")
        
        # 测试托盘图标创建（不显示）
        if QSystemTrayIcon.isSystemTrayAvailable():
            from ui.system_tray import SystemTray
            tray = SystemTray()
            print("   ✅ 托盘图标创建成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 安全启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🆘 TimeNest 紧急恢复测试")
    print("=" * 50)
    
    # 设置简单日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    import_ok = test_basic_imports()
    
    if import_ok:
        func_ok = test_basic_functionality()
        
        if func_ok:
            startup_ok = test_safe_startup()
            
            if startup_ok:
                print("\n" + "=" * 50)
                print("✅ 紧急恢复测试通过！")
                print("\n📋 建议:")
                print("   1. 现在可以尝试运行: python main.py")
                print("   2. 如果仍有问题，请重启系统")
                print("   3. 避免使用复杂的增强功能")
                print("   4. 只使用基本的课程表功能")
                return True
    
    print("\n" + "=" * 50)
    print("❌ 紧急恢复测试失败")
    print("\n🔧 修复建议:")
    print("   1. 重新安装依赖: pip install -r requirements.txt")
    print("   2. 检查Python版本是否兼容")
    print("   3. 重启系统清理内存")
    print("   4. 如果问题持续，请使用更早的稳定版本")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
