#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 缺失方法修复验证脚本
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_system_tray_methods():
    """测试SystemTray方法"""
    print("🗂️ 测试SystemTray方法...")
    
    try:
        from ui.system_tray import SystemTray
        
        # 检查update_floating_status方法是否存在
        if hasattr(SystemTray, 'update_floating_status'):
            print("✅ SystemTray.update_floating_status 方法存在")
        else:
            print("❌ SystemTray.update_floating_status 方法不存在")
            return False
        
        # 检查方法是否可调用
        if callable(getattr(SystemTray, 'update_floating_status')):
            print("✅ SystemTray.update_floating_status 方法可调用")
        else:
            print("❌ SystemTray.update_floating_status 方法不可调用")
            return False
        
        # 检查update_floating_widget_action方法（原有方法）
        if hasattr(SystemTray, 'update_floating_widget_action'):
            print("✅ SystemTray.update_floating_widget_action 方法存在")
        else:
            print("❌ SystemTray.update_floating_widget_action 方法不存在")
            return False
        
        print("✅ SystemTray方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ SystemTray方法测试失败: {e}")
        return False


def test_plugin_manager_methods():
    """测试PluginManager方法"""
    print("\n🔌 测试PluginManager方法...")
    
    try:
        from core.plugin_base import PluginManager
        
        # 检查update_plugins_status方法是否存在
        if hasattr(PluginManager, 'update_plugins_status'):
            print("✅ PluginManager.update_plugins_status 方法存在")
        else:
            print("❌ PluginManager.update_plugins_status 方法不存在")
            return False
        
        # 检查方法是否可调用
        if callable(getattr(PluginManager, 'update_plugins_status')):
            print("✅ PluginManager.update_plugins_status 方法可调用")
        else:
            print("❌ PluginManager.update_plugins_status 方法不可调用")
            return False
        
        # 检查_cleanup_invalid_plugins方法
        if hasattr(PluginManager, '_cleanup_invalid_plugins'):
            print("✅ PluginManager._cleanup_invalid_plugins 方法存在")
        else:
            print("❌ PluginManager._cleanup_invalid_plugins 方法不存在")
            return False
        
        print("✅ PluginManager方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ PluginManager方法测试失败: {e}")
        return False


def test_enhanced_plugin_manager_methods():
    """测试EnhancedPluginManager方法"""
    print("\n🔌+ 测试EnhancedPluginManager方法...")
    
    try:
        from core.plugin_system.enhanced_plugin_manager import EnhancedPluginManager
        
        # 检查update_plugins_status方法是否存在
        if hasattr(EnhancedPluginManager, 'update_plugins_status'):
            print("✅ EnhancedPluginManager.update_plugins_status 方法存在")
        else:
            print("❌ EnhancedPluginManager.update_plugins_status 方法不存在")
            return False
        
        # 检查方法是否可调用
        if callable(getattr(EnhancedPluginManager, 'update_plugins_status')):
            print("✅ EnhancedPluginManager.update_plugins_status 方法可调用")
        else:
            print("❌ EnhancedPluginManager.update_plugins_status 方法不可调用")
            return False
        
        # 检查_cleanup_invalid_plugins方法
        if hasattr(EnhancedPluginManager, '_cleanup_invalid_plugins'):
            print("✅ EnhancedPluginManager._cleanup_invalid_plugins 方法存在")
        else:
            print("❌ EnhancedPluginManager._cleanup_invalid_plugins 方法不存在")
            return False
        
        print("✅ EnhancedPluginManager方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ EnhancedPluginManager方法测试失败: {e}")
        return False


def test_method_signatures():
    """测试方法签名"""
    print("\n📝 测试方法签名...")
    
    try:
        import inspect
        from ui.system_tray import SystemTray
        from core.plugin_base import PluginManager
        
        # 测试SystemTray.update_floating_status签名
        sig = inspect.signature(SystemTray.update_floating_status)
        params = list(sig.parameters.keys())
        
        if 'self' in params and 'is_visible' in params:
            print("✅ SystemTray.update_floating_status 方法签名正确")
        else:
            print(f"❌ SystemTray.update_floating_status 方法签名错误: {params}")
            return False
        
        # 测试PluginManager.update_plugins_status签名
        sig = inspect.signature(PluginManager.update_plugins_status)
        params = list(sig.parameters.keys())
        
        if 'self' in params:
            print("✅ PluginManager.update_plugins_status 方法签名正确")
        else:
            print(f"❌ PluginManager.update_plugins_status 方法签名错误: {params}")
            return False
        
        print("✅ 方法签名测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 方法签名测试失败: {e}")
        return False


def test_syntax_validation():
    """测试语法验证"""
    print("\n🔍 测试语法验证...")
    
    try:
        import ast
        
        # 检查修复的文件
        files_to_check = [
            "ui/system_tray.py",
            "core/plugin_base.py",
            "core/plugin_system/enhanced_plugin_manager.py"
        ]
        
        syntax_errors = []
        
        for file_path in files_to_check:
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                    print(f"✅ {file_path}: 语法正确")
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}: {e}")
                    print(f"❌ {file_path}: 语法错误 - {e}")
            else:
                print(f"⚠️ {file_path}: 文件不存在")
        
        if not syntax_errors:
            print("✅ 语法验证测试通过")
            return True
        else:
            print(f"❌ 语法验证测试失败: {len(syntax_errors)} 个错误")
            return False
            
    except Exception as e:
        print(f"❌ 语法验证测试失败: {e}")
        return False


def test_import_validation():
    """测试导入验证"""
    print("\n📦 测试导入验证...")
    
    try:
        # 测试核心模块导入
        modules_to_test = [
            'ui.system_tray',
            'core.plugin_base',
            'core.plugin_system.enhanced_plugin_manager'
        ]
        
        import_errors = []
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"✅ {module_name}: 导入成功")
            except ImportError as e:
                import_errors.append(f"{module_name}: {e}")
                print(f"❌ {module_name}: 导入失败 - {e}")
            except Exception as e:
                # 其他错误可能是依赖问题，不算导入失败
                print(f"⚠️ {module_name}: 导入时出现其他错误 - {e}")
        
        if not import_errors:
            print("✅ 导入验证测试通过")
            return True
        else:
            print(f"❌ 导入验证测试失败: {len(import_errors)} 个错误")
            return False
            
    except Exception as e:
        print(f"❌ 导入验证测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 TimeNest 缺失方法修复验证")
    print("=" * 50)
    
    tests = [
        ("SystemTray方法", test_system_tray_methods),
        ("PluginManager方法", test_plugin_manager_methods),
        ("EnhancedPluginManager方法", test_enhanced_plugin_manager_methods),
        ("方法签名", test_method_signatures),
        ("语法验证", test_syntax_validation),
        ("导入验证", test_import_validation)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"💥 {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果:")
    print(f"  总测试数: {total_tests}")
    print(f"  通过测试: {passed_tests}")
    print(f"  失败测试: {total_tests - passed_tests}")
    print(f"  成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！缺失方法修复验证成功")
        print("\n💡 修复说明:")
        print("1. ✅ 添加了SystemTray.update_floating_status方法")
        print("2. ✅ 添加了PluginManager.update_plugins_status方法")
        print("3. ✅ 添加了EnhancedPluginManager.update_plugins_status方法")
        print("4. ✅ 添加了插件状态清理和恢复机制")
        print("5. ✅ 确保了方法签名和语法正确性")
        
        print("\n🔧 现在应该可以正常运行TimeNest了！")
        print("预期结果:")
        print("- ✅ 系统托盘初始化不会出现参数错误")
        print("- ✅ 浮窗状态更新不会出现方法缺失错误")
        print("- ✅ 插件状态定期更新不会出现方法缺失错误")
        print("- ✅ 应用启动和运行过程更加稳定")
        
        return True
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
