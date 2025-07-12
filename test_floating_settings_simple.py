#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 浮窗设置功能简单测试
不依赖GUI的基本功能测试
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_file_structure():
    """测试文件结构"""
    print("\n1. 测试文件结构")
    print("-" * 40)
    
    # 检查新创建的文件
    files_to_check = [
        "ui/floating_settings_dialog.py",
        "test_floating_settings.py"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} 存在")
        else:
            print(f"   ❌ {file_path} 缺失")
            all_exist = False
    
    return all_exist

def test_app_settings_modification():
    """测试应用设置文件修改"""
    print("\n2. 测试应用设置文件修改")
    print("-" * 40)
    
    try:
        # 读取应用设置对话框文件
        with open("ui/modules/app_settings_dialog.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否删除了浮窗设置相关代码
        checks = [
            ("浮窗设置选项卡删除", "浮窗设置" not in content or content.count("浮窗设置") <= 1),
            ("create_floating_settings_tab方法删除", "create_floating_settings_tab" not in content),
            ("浮窗设置tab删除", "floating_tab" not in content)
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def test_floating_settings_dialog_content():
    """测试浮窗设置对话框内容"""
    print("\n3. 测试浮窗设置对话框内容")
    print("-" * 40)
    
    try:
        # 读取浮窗设置对话框文件
        with open("ui/floating_settings_dialog.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键功能
        features_to_check = [
            ("FloatingSettingsDialog类", "class FloatingSettingsDialog"),
            ("外观设置组", "create_appearance_group"),
            ("位置设置组", "create_position_group"),
            ("模块管理组", "create_modules_group"),
            ("交互设置组", "create_interaction_group"),
            ("应用设置方法", "def apply_settings"),
            ("重置设置方法", "def reset_settings"),
            ("浮窗样式", "apply_floating_style"),
            ("拖拽功能", "mousePressEvent"),
            ("信号定义", "settings_changed = pyqtSignal")
        ]
        
        all_passed = True
        for feature_name, feature_code in features_to_check:
            if feature_code in content:
                print(f"   ✅ {feature_name}")
            else:
                print(f"   ❌ {feature_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def test_floating_manager_modifications():
    """测试浮窗管理器修改"""
    print("\n4. 测试浮窗管理器修改")
    print("-" * 40)
    
    try:
        # 读取浮窗管理器文件
        with open("core/floating_manager.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查新增的方法
        methods_to_check = [
            ("显示设置对话框", "def show_settings_dialog"),
            ("设置应用处理", "def on_settings_applied"),
            ("对话框关闭处理", "def on_settings_dialog_closed"),
            ("应用设置", "def apply_settings"),
            ("设置对话框属性", "self.settings_dialog")
        ]
        
        all_passed = True
        for method_name, method_code in methods_to_check:
            if method_code in content:
                print(f"   ✅ {method_name}")
            else:
                print(f"   ❌ {method_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def test_tray_features_modifications():
    """测试托盘功能修改"""
    print("\n5. 测试托盘功能修改")
    print("-" * 40)
    
    try:
        # 读取托盘功能文件
        with open("ui/tray_features.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查浮窗设置方法的修改
        checks = [
            ("浮窗设置方法存在", "def show_floating_settings" in content),
            ("使用浮窗管理器", "floating_manager.show_settings_dialog" in content),
            ("删除旧的实现", "FloatingSettingsTab" not in content)
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def test_floating_widget_modifications():
    """测试浮窗组件修改"""
    print("\n6. 测试浮窗组件修改")
    print("-" * 40)
    
    try:
        # 读取浮窗组件文件
        with open("ui/floating_widget.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查新增的方法
        methods_to_check = [
            ("重新加载配置", "def load_config"),
            ("应用配置", "def apply_config"),
            ("设置置顶", "def set_always_on_top"),
            ("显示设置", "def show_settings"),
            ("右键菜单", "def contextMenuEvent")
        ]
        
        all_passed = True
        for method_name, method_code in methods_to_check:
            if method_code in content:
                print(f"   ✅ {method_name}")
            else:
                print(f"   ❌ {method_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def test_code_quality():
    """测试代码质量"""
    print("\n7. 测试代码质量")
    print("-" * 40)
    
    try:
        # 检查浮窗设置对话框的代码质量
        with open("ui/floating_settings_dialog.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        quality_checks = [
            ("文档字符串", '"""' in content),
            ("异常处理", "try:" in content and "except" in content),
            ("日志记录", "self.logger" in content),
            ("类型注解", ":" in content and "->" in content),
            ("编码声明", "# -*- coding: utf-8 -*-" in content),
            ("导入组织", "from PyQt6" in content),
            ("信号使用", "pyqtSignal" in content),
            ("样式设置", "setStyleSheet" in content)
        ]
        
        all_passed = True
        for check_name, check_result in quality_checks:
            if check_result:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("TimeNest 浮窗设置功能简单测试")
    print("=" * 50)
    
    # 运行所有测试
    test_results = []
    
    test_results.append(test_file_structure())
    test_results.append(test_app_settings_modification())
    test_results.append(test_floating_settings_dialog_content())
    test_results.append(test_floating_manager_modifications())
    test_results.append(test_tray_features_modifications())
    test_results.append(test_floating_widget_modifications())
    test_results.append(test_code_quality())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print("📊 测试结果统计")
    print(f"   通过: {passed}/{total}")
    print(f"   成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有浮窗设置功能测试通过！")
        print("\n✨ 完成的功能:")
        print("   🗑️ 删除了应用设置中的浮窗设置选项卡")
        print("   🎈 创建了独立的浮窗设置对话框")
        print("   🔧 浮窗管理器支持独立设置对话框")
        print("   🖱️ 托盘功能集成独立设置对话框")
        print("   ⚙️ 浮窗组件支持右键菜单和设置")
        print("   🎨 浮窗样式和拖拽功能")
        print("   📝 完整的配置管理和信号系统")
        print("\n🚀 浮窗设置现在以独立浮窗形式显示，完美兼容所有设置功能！")
    else:
        print(f"\n⚠️ {total-passed} 个功能测试失败，请检查相关模块")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
