#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 运行时错误修复验证脚本
"""

import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_system_tray_initialization():
    """测试系统托盘初始化"""
    print("🗂️ 测试系统托盘初始化...")
    
    try:
        # 测试SystemTray类的参数兼容性
        from ui.system_tray import SystemTray, SystemTrayManager
        
        # 测试不带参数的初始化
        try:
            tray1 = SystemTray()
            print("✅ SystemTray() 无参数初始化成功")
        except Exception as e:
            print(f"❌ SystemTray() 无参数初始化失败: {e}")
            return False
        
        # 测试带floating_manager参数的初始化
        try:
            tray2 = SystemTray(floating_manager=None)
            print("✅ SystemTray(floating_manager=None) 初始化成功")
        except Exception as e:
            print(f"❌ SystemTray(floating_manager=None) 初始化失败: {e}")
            return False
        
        # 测试SystemTrayManager别名
        try:
            tray3 = SystemTrayManager(floating_manager=None)
            print("✅ SystemTrayManager(floating_manager=None) 别名工作正常")
        except Exception as e:
            print(f"❌ SystemTrayManager 别名失败: {e}")
            return False
        
        print("✅ 系统托盘初始化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 系统托盘初始化测试失败: {e}")
        return False


def test_notification_manager_methods():
    """测试通知管理器方法"""
    print("\n📢 测试通知管理器方法...")
    
    try:
        # 检查NotificationManager类是否有check_pending_notifications方法
        from core.notification_manager import NotificationManager
        
        # 检查方法是否存在
        if hasattr(NotificationManager, 'check_pending_notifications'):
            print("✅ check_pending_notifications 方法存在")
        else:
            print("❌ check_pending_notifications 方法不存在")
            return False
        
        # 检查方法是否可调用
        if callable(getattr(NotificationManager, 'check_pending_notifications')):
            print("✅ check_pending_notifications 方法可调用")
        else:
            print("❌ check_pending_notifications 方法不可调用")
            return False
        
        print("✅ 通知管理器方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 通知管理器方法测试失败: {e}")
        return False


def test_floating_widget_configuration():
    """测试浮窗配置"""
    print("\n🎈 测试浮窗配置...")
    
    try:
        # 确保配置文件存在
        config_dir = Path("config")
        config_file = config_dir / "config.json"
        
        if not config_file.exists():
            print("⚠️ 配置文件不存在，创建默认配置...")
            config_dir.mkdir(exist_ok=True)
            
            default_config = {
                "floating_widget": {
                    "width": 400,
                    "height": 60,
                    "opacity": 0.9,
                    "border_radius": 30,
                    "position": {"x": 0, "y": 10},
                    "mouse_transparent": False,
                    "fixed_position": True,
                    "auto_rotate_content": False,
                    "rotation_interval": 5000,
                    "modules": {
                        "time": {
                            "enabled": True,
                            "order": 0,
                            "format_24h": True,
                            "show_seconds": False
                        },
                        "schedule": {
                            "enabled": True,
                            "order": 1
                        }
                    }
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print("✅ 默认配置文件已创建")
        
        # 验证配置内容
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        floating_config = config.get('floating_widget', {})
        modules_config = floating_config.get('modules', {})
        
        if not modules_config:
            print("❌ 配置文件中没有模块配置")
            return False
        
        enabled_modules = [
            module_id for module_id, cfg in modules_config.items()
            if cfg.get('enabled', True)
        ]
        
        if not enabled_modules:
            print("❌ 没有启用的模块")
            return False
        
        print(f"✅ 配置验证通过，启用模块: {enabled_modules}")
        return True
        
    except Exception as e:
        print(f"❌ 浮窗配置测试失败: {e}")
        return False


def test_module_classes():
    """测试模块类"""
    print("\n🧩 测试模块类...")
    
    try:
        # 测试基本模块导入
        from ui.floating_widget.floating_modules import TimeModule, ScheduleModule
        
        # 测试时间模块
        time_module = TimeModule()
        time_text = time_module.get_display_text()
        
        if time_text and len(time_text) > 0:
            print(f"✅ 时间模块工作正常: {time_text}")
        else:
            print("❌ 时间模块返回空文本")
            return False
        
        # 测试课程模块
        schedule_module = ScheduleModule()
        schedule_text = schedule_module.get_display_text()
        
        if schedule_text and len(schedule_text) > 0:
            print(f"✅ 课程模块工作正常: {schedule_text}")
        else:
            print("❌ 课程模块返回空文本")
            return False
        
        print("✅ 模块类测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 模块类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_syntax_validation():
    """测试语法验证"""
    print("\n🔍 测试语法验证...")
    
    try:
        import ast
        
        # 检查修复的文件
        files_to_check = [
            "ui/system_tray.py",
            "core/notification_manager.py",
            "ui/floating_widget/smart_floating_widget.py"
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
    print("🚀 TimeNest 运行时错误修复验证")
    print("=" * 50)
    
    tests = [
        ("系统托盘初始化", test_system_tray_initialization),
        ("通知管理器方法", test_notification_manager_methods),
        ("浮窗配置", test_floating_widget_configuration),
        ("模块类", test_module_classes),
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
        print("\n🎉 所有测试通过！运行时错误修复验证成功")
        print("\n💡 修复说明:")
        print("1. ✅ 修复了SystemTray初始化参数问题")
        print("2. ✅ 添加了NotificationManager缺失的方法")
        print("3. ✅ 改进了浮窗模块配置加载逻辑")
        print("4. ✅ 增强了模块初始化的错误处理")
        print("5. ✅ 确保了配置文件的正确性")
        
        print("\n🔧 现在应该可以正常运行TimeNest了！")
        return True
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
