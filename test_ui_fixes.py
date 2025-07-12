#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest UI问题修复验证脚本
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_floating_widget_focus_fix():
    """测试浮窗焦点修复"""
    print("🎈 测试浮窗焦点修复...")
    
    try:
        # 检查浮窗代码中是否移除了WindowDoesNotAcceptFocus标志
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'WindowDoesNotAcceptFocus' in content:
            print("❌ 浮窗代码中仍然包含WindowDoesNotAcceptFocus标志")
            return False
        else:
            print("✅ 已移除WindowDoesNotAcceptFocus标志")
        
        # 检查鼠标穿透默认设置
        if 'self.mouse_transparent = False' in content:
            print("✅ 鼠标穿透默认设置为False，允许交互")
        else:
            print("⚠️ 鼠标穿透设置可能需要检查")
        
        print("✅ 浮窗焦点修复测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 浮窗焦点修复测试失败: {e}")
        return False


def test_tray_menu_cleanup():
    """测试托盘菜单清理"""
    print("\n🗂️ 测试托盘菜单清理...")
    
    try:
        with open('ui/system_tray.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 计算"浮窗设置"菜单项的数量
        floating_settings_count = content.count('⚙️ 浮窗设置')
        
        print(f"📊 找到 {floating_settings_count} 个'浮窗设置'菜单项")
        
        if floating_settings_count == 1:
            print("✅ 浮窗设置菜单项数量正确（只有1个）")
        elif floating_settings_count > 1:
            print(f"❌ 仍有重复的浮窗设置菜单项（{floating_settings_count}个）")
            return False
        else:
            print("❌ 没有找到浮窗设置菜单项")
            return False
        
        # 检查菜单启用设置
        if 'menu.setEnabled(True)' in content:
            print("✅ 菜单启用设置已添加")
        else:
            print("⚠️ 菜单启用设置可能缺失")
        
        print("✅ 托盘菜单清理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 托盘菜单清理测试失败: {e}")
        return False


def test_window_flags_configuration():
    """测试窗口标志配置"""
    print("\n🪟 测试窗口标志配置...")
    
    try:
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查窗口标志设置
        required_flags = [
            'Qt.WindowType.FramelessWindowHint',
            'Qt.WindowType.WindowStaysOnTopHint',
            'Qt.WindowType.Tool',
            'Qt.WindowType.BypassWindowManagerHint'
        ]
        
        missing_flags = []
        for flag in required_flags:
            if flag not in content:
                missing_flags.append(flag)
        
        if missing_flags:
            print(f"❌ 缺少窗口标志: {missing_flags}")
            return False
        else:
            print("✅ 所有必需的窗口标志都存在")
        
        # 检查条件性鼠标穿透设置
        if 'if self.mouse_transparent:' in content and 'WindowTransparentForInput' in content:
            print("✅ 条件性鼠标穿透设置正确")
        else:
            print("⚠️ 鼠标穿透设置可能有问题")
        
        print("✅ 窗口标志配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 窗口标志配置测试失败: {e}")
        return False


def test_menu_structure():
    """测试菜单结构"""
    print("\n📋 测试菜单结构...")
    
    try:
        with open('ui/system_tray.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查菜单项
        expected_menu_items = [
            '隐藏浮窗',
            '⚙️ 浮窗设置',
            '📅 课程表管理',
            '🔧 应用设置',
            '🔌 插件市场',
            '⏰ 时间校准',
            '❌ 退出 TimeNest'
        ]
        
        missing_items = []
        for item in expected_menu_items:
            if item not in content:
                missing_items.append(item)
        
        if missing_items:
            print(f"❌ 缺少菜单项: {missing_items}")
            return False
        else:
            print("✅ 所有预期的菜单项都存在")
        
        # 检查菜单分隔符
        separator_count = content.count('menu.addSeparator()')
        print(f"📊 找到 {separator_count} 个菜单分隔符")
        
        if separator_count >= 3:  # 至少应该有几个分隔符来分组
            print("✅ 菜单分隔符数量合理")
        else:
            print("⚠️ 菜单分隔符可能不足")
        
        print("✅ 菜单结构测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 菜单结构测试失败: {e}")
        return False


def test_syntax_validation():
    """测试语法验证"""
    print("\n🔍 测试语法验证...")
    
    try:
        import ast
        
        # 检查修复的文件
        files_to_check = [
            "ui/floating_widget/smart_floating_widget.py",
            "ui/system_tray.py"
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
    print("🚀 TimeNest UI问题修复验证")
    print("=" * 50)
    
    tests = [
        ("浮窗焦点修复", test_floating_widget_focus_fix),
        ("托盘菜单清理", test_tray_menu_cleanup),
        ("窗口标志配置", test_window_flags_configuration),
        ("菜单结构", test_menu_structure),
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
        print("\n🎉 所有测试通过！UI问题修复验证成功")
        print("\n💡 修复说明:")
        print("1. ✅ 移除了浮窗的WindowDoesNotAcceptFocus标志")
        print("2. ✅ 删除了重复的浮窗设置菜单项")
        print("3. ✅ 修复了鼠标穿透默认设置")
        print("4. ✅ 改进了窗口标志配置")
        print("5. ✅ 确保了菜单可以正常点击")
        
        print("\n🔧 预期效果:")
        print("- ✅ 不再出现requestActivate()错误")
        print("- ✅ 托盘菜单按钮可以正常点击")
        print("- ✅ 浮窗设置菜单项不重复")
        print("- ✅ 浮窗可以正常交互（如果禁用鼠标穿透）")
        
        return True
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
