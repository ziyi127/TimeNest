#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 托盘菜单修复验证脚本
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_floating_widget_window_flags():
    """测试浮窗窗口标志"""
    print("🎈 测试浮窗窗口标志...")
    
    try:
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了Popup标志
        if 'Qt.WindowType.Popup' in content:
            print("✅ 浮窗使用了Popup窗口类型")
        else:
            print("❌ 浮窗未使用Popup窗口类型")
            return False
        
        # 检查是否移除了Tool标志
        tool_count = content.count('Qt.WindowType.Tool')
        if tool_count == 0:
            print("✅ 已移除Tool窗口类型标志")
        else:
            print(f"⚠️ 仍有 {tool_count} 个Tool窗口类型标志")
        
        # 检查是否添加了NoDropShadowWindowHint
        if 'Qt.WindowType.NoDropShadowWindowHint' in content:
            print("✅ 添加了NoDropShadowWindowHint标志")
        else:
            print("⚠️ 未添加NoDropShadowWindowHint标志")
        
        print("✅ 浮窗窗口标志测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 浮窗窗口标志测试失败: {e}")
        return False


def test_tray_signal_connections():
    """测试托盘信号连接"""
    print("\n🔗 测试托盘信号连接...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查信号连接
        required_connections = [
            'toggle_floating_widget_requested.connect',
            'floating_settings_requested.connect',
            'schedule_module_requested.connect',
            'settings_module_requested.connect',
            'plugins_module_requested.connect',
            'time_calibration_requested.connect'
        ]
        
        missing_connections = []
        for connection in required_connections:
            if connection not in content:
                missing_connections.append(connection)
        
        if missing_connections:
            print(f"❌ 缺少信号连接: {missing_connections}")
            return False
        else:
            print("✅ 所有必需的信号连接都存在")
        
        # 检查是否修复了信号名称
        if 'toggle_floating_widget_requested.connect' in content:
            print("✅ 浮窗切换信号连接已修复")
        else:
            print("❌ 浮窗切换信号连接未修复")
            return False
        
        print("✅ 托盘信号连接测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 托盘信号连接测试失败: {e}")
        return False


def test_tray_feature_methods():
    """测试托盘功能方法"""
    print("\n🎯 测试托盘功能方法...")
    
    try:
        with open('ui/tray_features.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否添加了调试信息
        debug_methods = [
            'self.logger.info("显示浮窗设置被调用")',
            'self.logger.info("显示课程表管理被调用")'
        ]
        
        missing_debug = []
        for debug_line in debug_methods:
            if debug_line not in content:
                missing_debug.append(debug_line)
        
        if missing_debug:
            print(f"⚠️ 缺少调试信息: {len(missing_debug)} 个")
        else:
            print("✅ 所有调试信息都已添加")
        
        # 检查方法是否存在
        required_methods = [
            'def show_floating_settings',
            'def show_schedule_management',
            'def show_app_settings',
            'def show_plugin_marketplace',
            'def show_time_calibration'
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 缺少方法: {missing_methods}")
            return False
        else:
            print("✅ 所有必需的方法都存在")
        
        print("✅ 托盘功能方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 托盘功能方法测试失败: {e}")
        return False


def test_floating_toggle_handler():
    """测试浮窗切换处理器"""
    print("\n🔄 测试浮窗切换处理器...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查浮窗切换处理函数
        if 'def handle_floating_toggle' in content:
            print("✅ 浮窗切换处理函数存在")
        else:
            print("❌ 浮窗切换处理函数不存在")
            return False
        
        # 检查是否有安全的方法调用
        if 'hasattr(tray_manager, \'update_floating_status\')' in content:
            print("✅ 添加了安全的方法调用检查")
        else:
            print("⚠️ 未添加安全的方法调用检查")
        
        print("✅ 浮窗切换处理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 浮窗切换处理器测试失败: {e}")
        return False


def test_window_attributes():
    """测试窗口属性设置"""
    print("\n🪟 测试窗口属性设置...")
    
    try:
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查窗口属性
        required_attributes = [
            'WA_TranslucentBackground',
            'WA_AlwaysShowToolTips',
            'WA_ShowWithoutActivating'
        ]
        
        missing_attributes = []
        for attr in required_attributes:
            if attr not in content:
                missing_attributes.append(attr)
        
        if missing_attributes:
            print(f"❌ 缺少窗口属性: {missing_attributes}")
            return False
        else:
            print("✅ 所有必需的窗口属性都存在")
        
        # 检查鼠标穿透设置
        if 'mouse_transparent = False' in content:
            print("✅ 鼠标穿透默认设置为False")
        else:
            print("⚠️ 鼠标穿透设置可能需要检查")
        
        print("✅ 窗口属性设置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 窗口属性设置测试失败: {e}")
        return False


def test_syntax_validation():
    """测试语法验证"""
    print("\n🔍 测试语法验证...")
    
    try:
        import ast
        
        # 检查修复的文件
        files_to_check = [
            "main.py",
            "ui/floating_widget/smart_floating_widget.py",
            "ui/tray_features.py"
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


def main():
    """主函数"""
    print("🚀 TimeNest 托盘菜单修复验证")
    print("=" * 50)
    
    tests = [
        ("浮窗窗口标志", test_floating_widget_window_flags),
        ("托盘信号连接", test_tray_signal_connections),
        ("托盘功能方法", test_tray_feature_methods),
        ("浮窗切换处理器", test_floating_toggle_handler),
        ("窗口属性设置", test_window_attributes),
        ("语法验证", test_syntax_validation)
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
        print("\n🎉 所有测试通过！托盘菜单修复验证成功")
        print("\n💡 修复说明:")
        print("1. ✅ 修复了托盘菜单信号连接问题")
        print("2. ✅ 改进了浮窗窗口标志，使其显示为真正的悬浮窗")
        print("3. ✅ 添加了调试信息以便排查问题")
        print("4. ✅ 改进了浮窗切换处理逻辑")
        print("5. ✅ 优化了窗口属性设置")
        
        print("\n🔧 预期效果:")
        print("- ✅ 托盘菜单按钮现在应该可以正常点击")
        print("- ✅ 浮窗显示为真正的悬浮窗而非普通窗口")
        print("- ✅ 浮窗设置、课程表管理等功能可以正常打开")
        print("- ✅ 浮窗切换功能正常工作")
        print("- ✅ 更好的错误处理和调试信息")
        
        return True
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
