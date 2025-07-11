#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有导入问题的脚本
"""

import sys
import traceback
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_import_without_pyqt():
    """在没有PyQt6的情况下测试导入"""
    print("🔧 修复 TimeNest 所有导入问题")
    print("=" * 50)
    
    # 创建模拟的PyQt6模块
    import types
    
    # 模拟 PyQt6.QtCore
    mock_qtcore = types.ModuleType('PyQt6.QtCore')

    class MockQObjectMeta(type):
        pass

    class MockQObject(metaclass=MockQObjectMeta):
        def __init__(self):
            pass

    class MockSignal:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, slot):
            pass

        def disconnect(self, slot=None):
            pass

        def emit(self, *args):
            pass

    def mock_signal(*args, **kwargs):
        return MockSignal(*args, **kwargs)

    class MockQTimer:
        def __init__(self):
            self.timeout = MockSignal()

        def start(self, interval=None):
            pass

        def stop(self):
            pass

    class MockQThread:
        def __init__(self):
            pass

    class MockQEasingCurve:
        def __init__(self):
            pass

    mock_qtcore.QObject = MockQObject
    mock_qtcore.pyqtSignal = mock_signal
    mock_qtcore.QTimer = MockQTimer
    mock_qtcore.QThread = MockQThread
    mock_qtcore.QEasingCurve = MockQEasingCurve
    mock_qtcore.QUrl = type('QUrl', (), {})
    mock_qtcore.QPoint = type('QPoint', (), {})
    mock_qtcore.QTranslator = type('QTranslator', (), {})
    mock_qtcore.QLocale = type('QLocale', (), {})
    mock_qtcore.QPropertyAnimation = type('QPropertyAnimation', (), {})
    mock_qtcore.QRect = type('QRect', (), {})
    mock_qtcore.QSize = type('QSize', (), {})
    mock_qtcore.Qt = types.ModuleType('Qt')
    
    # 模拟 PyQt6.QtWidgets
    mock_qtwidgets = types.ModuleType('PyQt6.QtWidgets')
    mock_qtwidgets.QApplication = type('QApplication', (), {})
    mock_qtwidgets.QFrame = type('QFrame', (), {})
    mock_qtwidgets.QWidget = type('QWidget', (), {})
    mock_qtwidgets.QLabel = type('QLabel', (), {})
    
    # 模拟 PyQt6.QtGui
    mock_qtgui = types.ModuleType('PyQt6.QtGui')
    mock_qtgui.QIcon = type('QIcon', (), {})
    mock_qtgui.QBrush = type('QBrush', (), {})
    mock_qtgui.QColor = type('QColor', (), {})
    mock_qtgui.QPalette = type('QPalette', (), {})
    mock_qtgui.QFont = type('QFont', (), {})
    mock_qtgui.QPixmap = type('QPixmap', (), {})
    mock_qtgui.QPainter = type('QPainter', (), {})
    mock_qtgui.QPen = type('QPen', (), {})

    # 模拟 PyQt6.QtNetwork
    mock_qtnetwork = types.ModuleType('PyQt6.QtNetwork')
    mock_qtnetwork.QNetworkAccessManager = type('QNetworkAccessManager', (), {})
    mock_qtnetwork.QNetworkRequest = type('QNetworkRequest', (), {})
    mock_qtnetwork.QNetworkReply = type('QNetworkReply', (), {})

    # 模拟 PyQt6
    mock_pyqt6 = types.ModuleType('PyQt6')
    mock_pyqt6.QtCore = mock_qtcore
    mock_pyqt6.QtWidgets = mock_qtwidgets
    mock_pyqt6.QtGui = mock_qtgui
    mock_pyqt6.QtNetwork = mock_qtnetwork

    # 安装模拟模块
    sys.modules['PyQt6'] = mock_pyqt6
    sys.modules['PyQt6.QtCore'] = mock_qtcore
    sys.modules['PyQt6.QtWidgets'] = mock_qtwidgets
    sys.modules['PyQt6.QtGui'] = mock_qtgui
    sys.modules['PyQt6.QtNetwork'] = mock_qtnetwork
    
    print("✅ PyQt6 模拟模块已安装")

def test_core_imports():
    """测试核心模块导入"""
    print("\n🔍 测试核心模块导入:")
    print("-" * 30)
    
    core_modules = [
        "core.plugin_base",
        "core.plugin_system",
        "core.base_manager", 
        "core.config_manager",
        "core.time_calibration_service",
        "core.plugin_development_tools",
        "core.app_manager",
    ]
    
    success_count = 0
    for module_name in core_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"   ✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
            if "circular import" in str(e).lower():
                print(f"      🔄 循环导入检测!")
    
    print(f"\n核心模块导入结果: {success_count}/{len(core_modules)} 成功")
    return success_count == len(core_modules)

def test_plugin_system_imports():
    """测试插件系统导入"""
    print("\n🔌 测试插件系统导入:")
    print("-" * 30)
    
    try:
        # 测试基础插件类
        print("测试基础插件类...")
        from core.plugin_base import IPlugin, PluginMetadata, PluginStatus, PluginType
        print("   ✅ 基础插件类导入成功")
        
        # 测试服务相关类
        print("测试服务相关类...")
        from core.plugin_base import IServiceProvider, ServiceType, ServiceMethod, ServiceInterface
        print("   ✅ 服务相关类导入成功")
        
        # 测试增强插件系统
        print("测试增强插件系统...")
        from core.plugin_system import EnhancedPluginManager
        print("   ✅ 增强插件系统导入成功")
        
        # 测试从插件系统包导入基础类
        print("测试从插件系统包导入基础类...")
        from core.plugin_system import IPlugin as IPlugin2
        print("   ✅ 从插件系统包导入基础类成功")
        
        # 验证类是同一个
        if IPlugin is IPlugin2:
            print("   ✅ 导入的类是同一个对象")
        else:
            print("   ⚠️ 导入的类不是同一个对象")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 插件系统导入失败: {e}")
        traceback.print_exc()
        return False

def test_metaclass_fix():
    """测试元类修复"""
    print("\n🔧 测试元类修复:")
    print("-" * 30)
    
    try:
        from core.base_manager import BaseManager, QObjectABCMeta
        print("   ✅ BaseManager 和 QObjectABCMeta 导入成功")
        
        # 测试元类
        print(f"   ✅ QObjectABCMeta 类型: {QObjectABCMeta}")
        print(f"   ✅ BaseManager 元类: {type(BaseManager)}")
        
        # 测试抽象类
        try:
            manager = BaseManager(None, "test")
            print("   ❌ BaseManager 应该是抽象类，不能直接实例化")
            return False
        except TypeError as e:
            if "abstract" in str(e).lower():
                print("   ✅ BaseManager 正确地阻止了直接实例化")
            else:
                print(f"   ⚠️ 意外错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 元类测试失败: {e}")
        traceback.print_exc()
        return False

def test_concrete_implementations():
    """测试具体实现"""
    print("\n🏗️ 测试具体实现:")
    print("-" * 30)
    
    try:
        # 测试时间校准服务
        print("测试时间校准服务...")
        from core.time_calibration_service import TimeCalibrationService
        service = TimeCalibrationService(None)
        print("   ✅ TimeCalibrationService 实例化成功")
        
        # 测试插件开发工具
        print("测试插件开发工具...")
        from core.plugin_development_tools import PluginDevelopmentTools
        tools = PluginDevelopmentTools(None)
        print("   ✅ PluginDevelopmentTools 实例化成功")
        
        # 测试增强插件管理器
        print("测试增强插件管理器...")
        from core.plugin_system import EnhancedPluginManager
        manager = EnhancedPluginManager(None)
        print("   ✅ EnhancedPluginManager 实例化成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 具体实现测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始修复和测试 TimeNest 导入问题...")
    
    # 安装PyQt6模拟
    test_import_without_pyqt()
    
    # 测试核心导入
    core_success = test_core_imports()
    
    # 测试插件系统
    plugin_success = test_plugin_system_imports()
    
    # 测试元类修复
    metaclass_success = test_metaclass_fix()
    
    # 测试具体实现
    concrete_success = test_concrete_implementations()
    
    print("\n" + "=" * 50)
    print("🎯 修复和测试总结:")
    print(f"   核心模块导入: {'✅ 成功' if core_success else '❌ 失败'}")
    print(f"   插件系统导入: {'✅ 成功' if plugin_success else '❌ 失败'}")
    print(f"   元类修复测试: {'✅ 成功' if metaclass_success else '❌ 失败'}")
    print(f"   具体实现测试: {'✅ 成功' if concrete_success else '❌ 失败'}")
    
    all_success = core_success and plugin_success and metaclass_success and concrete_success
    
    if all_success:
        print("\n🎉 所有测试通过! TimeNest 导入问题已修复!")
        print("\n📋 修复总结:")
        print("   • 解决了循环导入问题 (plugin_system.py -> plugin_base.py)")
        print("   • 修复了元类冲突 (QObjectABCMeta)")
        print("   • 更新了所有相关导入")
        print("   • 添加了缺失的类定义")
        print("\n🚀 现在可以尝试运行:")
        print("   python main.py")
        return True
    else:
        print("\n❌ 仍有问题需要解决")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
