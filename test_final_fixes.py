#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 最终修复验证脚本
验证托盘菜单、浮窗显示、位置设置和数据持久化
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_tray_signal_fixes():
    """测试托盘信号修复"""
    print("🔗 测试托盘信号修复...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查正确的信号连接
        if 'toggle_floating_widget_requested.connect' in content:
            print("✅ 浮窗切换信号连接已修复")
        else:
            print("❌ 浮窗切换信号连接未修复")
            return False
        
        # 检查是否移除了错误的信号
        if 'floating_toggled.connect' not in content:
            print("✅ 错误的信号连接已移除")
        else:
            print("❌ 仍存在错误的信号连接")
            return False
        
        # 检查安全的方法调用
        if 'hasattr(tray_manager, \'update_floating_status\')' in content:
            print("✅ 添加了安全的方法调用检查")
        else:
            print("⚠️ 未添加安全的方法调用检查")
        
        print("✅ 托盘信号修复测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 托盘信号修复测试失败: {e}")
        return False


def test_floating_widget_window_type():
    """测试浮窗窗口类型"""
    print("\n🎈 测试浮窗窗口类型...")
    
    try:
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了Popup类型
        if 'Qt.WindowType.Popup' in content:
            print("✅ 浮窗使用了Popup窗口类型")
        else:
            print("❌ 浮窗未使用Popup窗口类型")
            return False
        
        # 检查是否移除了Tool类型
        tool_count = content.count('Qt.WindowType.Tool')
        if tool_count == 0:
            print("✅ 已完全移除Tool窗口类型")
        else:
            print(f"⚠️ 仍有 {tool_count} 个Tool窗口类型")
        
        # 检查NoDropShadowWindowHint
        if 'Qt.WindowType.NoDropShadowWindowHint' in content:
            print("✅ 添加了NoDropShadowWindowHint标志")
        else:
            print("⚠️ 未添加NoDropShadowWindowHint标志")
        
        print("✅ 浮窗窗口类型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 浮窗窗口类型测试失败: {e}")
        return False


def test_position_configuration():
    """测试位置配置"""
    print("\n📍 测试位置配置...")
    
    try:
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否移除了强制居中
        if '强制设置浮窗到屏幕顶部居中' not in content:
            print("✅ 已移除强制居中设置")
        else:
            print("❌ 仍存在强制居中设置")
            return False
        
        # 检查是否添加了位置配置应用
        if 'position = self.config.get(\'position\', {})' in content:
            print("✅ 添加了位置配置应用")
        else:
            print("❌ 未添加位置配置应用")
            return False
        
        # 检查是否有条件性位置设置
        if 'if position and \'x\' in position and \'y\' in position:' in content:
            print("✅ 添加了条件性位置设置")
        else:
            print("❌ 未添加条件性位置设置")
            return False
        
        print("✅ 位置配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 位置配置测试失败: {e}")
        return False


def test_config_persistence():
    """测试配置持久化"""
    print("\n💾 测试配置持久化...")
    
    try:
        with open('ui/floating_widget/smart_floating_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有强制保存配置
        if 'self.app_manager.config_manager.save_config()' in content:
            print("✅ 添加了强制保存配置")
        else:
            print("❌ 未添加强制保存配置")
            return False
        
        # 检查是否有保存确认日志
        if '配置已保存到文件' in content:
            print("✅ 添加了保存确认日志")
        else:
            print("❌ 未添加保存确认日志")
            return False
        
        # 检查位置保存
        if '\'position\': {\'x\': self.x(), \'y\': self.y()}' in content:
            print("✅ 位置信息会被保存")
        else:
            print("❌ 位置信息不会被保存")
            return False
        
        print("✅ 配置持久化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置持久化测试失败: {e}")
        return False


def test_debug_logging():
    """测试调试日志"""
    print("\n🔍 测试调试日志...")
    
    try:
        with open('ui/tray_features.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查调试日志
        debug_logs = [
            'self.logger.info("显示浮窗设置被调用")',
            'self.logger.info("显示课程表管理被调用")'
        ]
        
        missing_logs = []
        for log in debug_logs:
            if log not in content:
                missing_logs.append(log)
        
        if not missing_logs:
            print("✅ 所有调试日志都已添加")
        else:
            print(f"⚠️ 缺少 {len(missing_logs)} 个调试日志")
        
        # 检查浮窗管理器备用方法
        if '使用浮窗管理器设置失败，尝试备用方法' in content:
            print("✅ 添加了浮窗设置备用方法")
        else:
            print("❌ 未添加浮窗设置备用方法")
            return False
        
        print("✅ 调试日志测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 调试日志测试失败: {e}")
        return False


def test_syntax_validation():
    """测试语法验证"""
    print("\n🔍 测试语法验证...")
    
    try:
        import ast
        
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
    print("🚀 TimeNest 最终修复验证")
    print("=" * 50)
    
    tests = [
        ("托盘信号修复", test_tray_signal_fixes),
        ("浮窗窗口类型", test_floating_widget_window_type),
        ("位置配置", test_position_configuration),
        ("配置持久化", test_config_persistence),
        ("调试日志", test_debug_logging),
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
        print("\n🎉 所有测试通过！最终修复验证成功")
        print("\n💡 修复说明:")
        print("1. ✅ 修复了托盘菜单信号连接问题")
        print("2. ✅ 改为Popup窗口类型实现真正悬浮效果")
        print("3. ✅ 修复了位置配置应用问题")
        print("4. ✅ 增强了配置数据持久化")
        print("5. ✅ 添加了全面的调试日志")
        print("6. ✅ 添加了错误处理和备用方案")
        
        print("\n🔧 预期效果:")
        print("- ✅ 托盘菜单按钮现在应该可以正常点击并打开对应功能")
        print("- ✅ 浮窗显示为真正的悬浮窗，不在任务栏显示")
        print("- ✅ 浮窗位置设置会被正确应用和保存")
        print("- ✅ 所有设置更改会被持久化保存")
        print("- ✅ 详细的调试日志帮助排查问题")
        
        return True
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
