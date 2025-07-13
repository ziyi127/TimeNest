#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 设置持久化测试脚本

测试设置的保存、加载和应用功能
"""

import sys
import json
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.config_manager import ConfigManager


def test_config_persistence():
    """测试配置持久化功能"""
    print("🧪 开始测试设置持久化功能...")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 测试数据
    test_settings = {
        'floating_widget': {
            'width': 500,
            'height': 80,
            'opacity': 0.8,
            'position': 'top_left',
            'enabled_modules': ['time', 'weather', 'system']
        },
        'notification': {
            'enabled': True,
            'sound_enabled': False,
            'advance_minutes': 10
        },
        'theme': {
            'name': '深色主题',
            'auto_switch': True
        }
    }
    
    print("📝 保存测试设置...")
    
    # 保存设置
    for category, settings in test_settings.items():
        for key, value in settings.items():
            config_key = f"{category}.{key}"
            success = config_manager.set_config(config_key, value, 'main', save=False)
            if success:
                print(f"  ✅ {config_key} = {value}")
            else:
                print(f"  ❌ {config_key} = {value} (保存失败)")
    
    # 强制保存所有配置
    save_success = config_manager.force_save_all_configs()
    if save_success:
        print("💾 所有配置已保存到文件")
    else:
        print("❌ 配置保存失败")
        return False
    
    print("\n🔄 重新加载配置...")
    
    # 重新创建配置管理器（模拟应用重启）
    config_manager_new = ConfigManager()
    
    # 验证设置是否正确加载
    print("🔍 验证加载的设置...")
    verification_passed = True
    
    for category, expected_settings in test_settings.items():
        loaded_config = config_manager_new.get_merged_config(category, {})
        
        for key, expected_value in expected_settings.items():
            actual_value = loaded_config.get(key)
            
            if actual_value == expected_value:
                print(f"  ✅ {category}.{key}: {actual_value}")
            else:
                print(f"  ❌ {category}.{key}: 期望 {expected_value}, 实际 {actual_value}")
                verification_passed = False
    
    if verification_passed:
        print("\n🎉 设置持久化测试通过！")
        return True
    else:
        print("\n❌ 设置持久化测试失败！")
        return False


def test_config_backup_restore():
    """测试配置备份和恢复功能"""
    print("\n🧪 开始测试配置备份和恢复功能...")

    config_manager = ConfigManager()

    # 设置已知的初始值
    print("📝 设置初始测试值...")
    initial_width = 888
    initial_theme = '初始主题'
    config_manager.set_config('floating_widget.width', initial_width, 'main')
    config_manager.set_config('theme.name', initial_theme, 'main')

    # 验证初始值
    width_before = config_manager.get_config('floating_widget.width', 0, 'main')
    theme_before = config_manager.get_config('theme.name', '', 'main')
    print(f"  初始值: width={width_before}, theme={theme_before}")

    # 创建备份
    print("📦 创建配置备份...")
    backup_success = config_manager._create_config_backup('main')
    if backup_success:
        print("  ✅ 配置备份已创建")
    else:
        print("  ❌ 配置备份创建失败")
        return False

    # 修改配置
    print("✏️ 修改配置...")
    modified_width = 999
    modified_theme = '测试主题'
    config_manager.set_config('floating_widget.width', modified_width, 'main')
    config_manager.set_config('theme.name', modified_theme, 'main')

    # 验证修改
    width_after = config_manager.get_config('floating_widget.width', 0, 'main')
    theme_after = config_manager.get_config('theme.name', '', 'main')
    print(f"  修改后: width={width_after}, theme={theme_after}")

    if width_after != modified_width or theme_after != modified_theme:
        print("❌ 配置修改验证失败")
        return False

    # 恢复备份
    print("🔄 恢复配置备份...")
    restore_success = config_manager._restore_config_backup('main')
    if restore_success:
        print("  ✅ 配置备份已恢复")

        # 验证恢复
        width_restored = config_manager.get_config('floating_widget.width', 0, 'main')
        theme_restored = config_manager.get_config('theme.name', '', 'main')
        print(f"  恢复后: width={width_restored}, theme={theme_restored}")

        # 检查是否恢复到备份时的值
        if width_restored == initial_width and theme_restored == initial_theme:
            print("🎉 配置备份和恢复测试通过！")
            return True
        else:
            print(f"❌ 配置恢复验证失败: 期望 width={initial_width}, theme='{initial_theme}'")
            print(f"   实际 width={width_restored}, theme='{theme_restored}'")
            return False
    else:
        print("  ❌ 配置备份恢复失败")
        return False


def test_config_validation():
    """测试配置验证功能"""
    print("\n🧪 开始测试配置验证功能...")
    
    config_manager = ConfigManager()
    
    # 测试有效配置
    print("✅ 测试有效配置...")
    valid_tests = [
        ('floating_widget.opacity', 0.5),
        ('floating_widget.width', 400),
        ('notification.advance_minutes', 15),
    ]
    
    for key, value in valid_tests:
        is_valid = config_manager._validate_config_value(key, value)
        if is_valid:
            print(f"  ✅ {key} = {value} (有效)")
        else:
            print(f"  ❌ {key} = {value} (应该有效但验证失败)")
    
    # 测试无效配置
    print("❌ 测试无效配置...")
    invalid_tests = [
        ('floating_widget.opacity', 1.5),  # 超出范围
        ('floating_widget.width', 50),     # 太小
        ('notification.advance_minutes', 100),  # 超出范围
    ]
    
    for key, value in invalid_tests:
        is_valid = config_manager._validate_config_value(key, value)
        if not is_valid:
            print(f"  ✅ {key} = {value} (正确识别为无效)")
        else:
            print(f"  ❌ {key} = {value} (应该无效但验证通过)")
    
    print("🎉 配置验证测试完成！")
    return True


def main():
    """主测试函数"""
    print("🚀 TimeNest 设置持久化测试开始")
    print("=" * 50)
    
    # 创建QApplication（某些功能需要）
    app = QApplication(sys.argv)
    
    # 运行测试
    tests = [
        ("配置持久化", test_config_persistence),
        ("配置备份恢复", test_config_backup_restore),
        ("配置验证", test_config_validation),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"💥 {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！设置持久化功能正常工作。")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
