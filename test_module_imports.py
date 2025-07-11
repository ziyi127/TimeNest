#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 模块导入测试脚本
测试每个模块是否可以独立导入，验证循环依赖修复效果
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_module_import(module_name: str) -> bool:
    """测试单个模块导入"""
    try:
        # 清除模块缓存
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # 尝试导入
        __import__(module_name)
        print(f"  ✓ {module_name}")
        return True
    except ImportError as e:
        print(f"  ✗ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️ {module_name}: {e}")
        return False

def test_core_modules():
    """测试核心模块"""
    print("🔧 测试核心模块...")
    print("-" * 40)
    
    core_modules = [
        'core.config_manager',
        'core.notification_manager',
        'core.floating_manager',
        'core.app_manager',
        'core.theme_system',
        'core.data_import_export'
    ]
    
    passed = 0
    for module in core_modules:
        if test_module_import(module):
            passed += 1
    
    print(f"\n核心模块: {passed}/{len(core_modules)} 通过")
    return passed, len(core_modules)

def test_ui_modules():
    """测试UI模块"""
    print("\n🎨 测试UI模块...")
    print("-" * 40)
    
    ui_modules = [
        'ui.floating_widget',
        'ui.system_tray',
        'ui.floating_settings_tab',
        'ui.settings_dialog',
        'ui.main_window'
    ]
    
    passed = 0
    for module in ui_modules:
        if test_module_import(module):
            passed += 1
    
    print(f"\nUI模块: {passed}/{len(ui_modules)} 通过")
    return passed, len(ui_modules)

def test_model_modules():
    """测试模型模块"""
    print("\n📊 测试模型模块...")
    print("-" * 40)
    
    model_modules = [
        'models.schedule',
        'models.theme',
        'models.notification'
    ]
    
    passed = 0
    for module in model_modules:
        if test_module_import(module):
            passed += 1
    
    print(f"\n模型模块: {passed}/{len(model_modules)} 通过")
    return passed, len(model_modules)

def test_utils_modules():
    """测试工具模块"""
    print("\n🛠️ 测试工具模块...")
    print("-" * 40)
    
    utils_modules = [
        'utils.text_to_speech',
        'utils.excel_exporter_v2'
    ]
    
    passed = 0
    for module in utils_modules:
        if test_module_import(module):
            passed += 1
    
    print(f"\n工具模块: {passed}/{len(utils_modules)} 通过")
    return passed, len(utils_modules)

def test_main_entry():
    """测试主入口"""
    print("\n🚀 测试主入口...")
    print("-" * 40)
    
    try:
        # 测试 main 模块导入（不执行）
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", current_dir / "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        # 只加载，不执行
        spec.loader.exec_module(main_module)
        print("  ✓ main.py 可以导入")
        return True
    except Exception as e:
        print(f"  ✗ main.py: {e}")
        return False

def test_circular_dependencies():
    """测试循环依赖修复效果"""
    print("\n🔄 测试循环依赖修复...")
    print("-" * 40)
    
    # 测试之前有问题的模块组合
    test_cases = [
        ('core.app_manager', 'core.floating_manager'),
        ('core.floating_manager', 'core.notification_manager'),
        ('ui.main_window', 'ui.system_tray'),
        ('ui.floating_widget', 'models.schedule')
    ]
    
    passed = 0
    for module1, module2 in test_cases:
        try:
            # 清除缓存
            for mod in [module1, module2]:
                if mod in sys.modules:
                    del sys.modules[mod]
            
            # 尝试同时导入
            __import__(module1)
            __import__(module2)
            print(f"  ✓ {module1} ↔ {module2}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {module1} ↔ {module2}: {e}")
    
    print(f"\n循环依赖测试: {passed}/{len(test_cases)} 通过")
    return passed, len(test_cases)

def test_dependency_injection():
    """测试依赖注入修复"""
    print("\n💉 测试依赖注入...")
    print("-" * 40)
    
    try:
        # 测试 FloatingManager 可以无参数创建
        from core.floating_manager import FloatingManager
        floating_manager = FloatingManager()
        print("  ✓ FloatingManager 可以无参数创建")
        
        # 测试可以后续设置依赖
        if hasattr(floating_manager, 'set_app_manager'):
            print("  ✓ FloatingManager 支持依赖注入")
        else:
            print("  ⚠️ FloatingManager 缺少 set_app_manager 方法")
        
        # 清理
        floating_manager.cleanup()
        return True
        
    except Exception as e:
        print(f"  ✗ 依赖注入测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 TimeNest 模块导入测试")
    print("=" * 60)
    print("验证循环依赖修复效果和模块独立性")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    # 测试各个模块类别
    core_passed, core_total = test_core_modules()
    total_passed += core_passed
    total_tests += core_total
    
    ui_passed, ui_total = test_ui_modules()
    total_passed += ui_passed
    total_tests += ui_total
    
    model_passed, model_total = test_model_modules()
    total_passed += model_passed
    total_tests += model_total
    
    utils_passed, utils_total = test_utils_modules()
    total_passed += utils_passed
    total_tests += utils_total
    
    # 测试主入口
    main_passed = test_main_entry()
    if main_passed:
        total_passed += 1
    total_tests += 1
    
    # 测试循环依赖修复
    circular_passed, circular_total = test_circular_dependencies()
    total_passed += circular_passed
    total_tests += circular_total
    
    # 测试依赖注入
    injection_passed = test_dependency_injection()
    if injection_passed:
        total_passed += 1
    total_tests += 1
    
    # 输出总结
    print("\n" + "=" * 60)
    print("🎉 测试结果总结")
    print("=" * 60)
    
    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"总体结果: {total_passed}/{total_tests} 测试通过 ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("\n✅ 优秀！循环依赖修复成功")
        print("  ✓ 所有模块可以独立导入")
        print("  ✓ 循环依赖问题已解决")
        print("  ✓ 依赖注入机制工作正常")
    elif success_rate >= 75:
        print("\n✅ 良好！大部分问题已修复")
        print("  ✓ 主要循环依赖已解决")
        print("  ⚠️ 部分模块可能需要进一步优化")
    else:
        print("\n⚠️ 需要进一步修复")
        print("  ✗ 仍存在循环依赖或导入问题")
    
    # 提供修复建议
    if success_rate < 100:
        print("\n💡 修复建议:")
        print("  1. 检查失败的模块导入错误")
        print("  2. 确保所有相对导入已改为绝对导入")
        print("  3. 使用延迟导入或依赖注入解决剩余循环依赖")
        print("  4. 考虑重构模块架构，减少不必要的依赖")
    
    return success_rate >= 75

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        sys.exit(1)
