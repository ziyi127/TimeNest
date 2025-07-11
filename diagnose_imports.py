#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断 TimeNest 导入问题
"""

import sys
import traceback
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_import(module_name, description=""):
    """测试单个模块导入"""
    print(f"🔍 测试导入: {module_name} {description}")
    try:
        module = __import__(module_name, fromlist=[''])
        print(f"   ✅ 成功导入 {module_name}")
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        if "circular import" in str(e).lower():
            print(f"   🔄 检测到循环导入!")
        traceback.print_exc()
        return False

def test_specific_imports():
    """测试具体的导入"""
    print("🔧 诊断 TimeNest 导入问题")
    print("=" * 50)
    
    # 测试基础模块
    tests = [
        ("core.config_manager", "配置管理器"),
        ("core.plugin_system", "插件系统"),
        ("core.plugin_system.interface_registry", "接口注册表"),
        ("core.plugin_system.dependency_validator", "依赖验证器"),
        ("core.plugin_system.message_bus", "消息总线"),
        ("core.plugin_system.communication_bus", "通信总线"),
        ("core.plugin_system.enhanced_plugin_manager", "增强插件管理器"),
        ("core.base_manager", "基础管理器"),
        ("core.time_calibration_service", "时间校准服务"),
        ("core.plugin_development_tools", "插件开发工具"),
        ("core.app_manager", "应用管理器"),
    ]
    
    results = []
    for module_name, description in tests:
        result = test_import(module_name, description)
        results.append((module_name, result))
        print()
    
    print("=" * 50)
    print("📊 导入测试结果:")
    
    success_count = 0
    for module_name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"   {module_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 模块导入成功")
    
    if success_count == len(results):
        print("🎉 所有模块导入成功!")
        return True
    else:
        print("⚠️ 部分模块导入失败")
        return False

def test_specific_classes():
    """测试具体类的导入"""
    print("\n🔍 测试具体类导入:")
    print("-" * 30)
    
    class_tests = [
        ("core.plugin_system", "IPlugin"),
        ("core.plugin_system", "PluginMetadata"),
        ("core.plugin_system", "PluginStatus"),
        ("core.plugin_system", "PluginType"),
        ("core.plugin_system", "IServiceProvider"),
        ("core.plugin_system", "ServiceType"),
        ("core.plugin_system", "ServiceMethod"),
        ("core.base_manager", "BaseManager"),
        ("core.base_manager", "QObjectABCMeta"),
    ]
    
    success_count = 0
    for module_name, class_name in class_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name}.{class_name}: {e}")
    
    print(f"\n类导入结果: {success_count}/{len(class_tests)} 成功")
    return success_count == len(class_tests)

def test_plugin_system_imports():
    """测试插件系统的具体导入"""
    print("\n🔌 测试插件系统导入:")
    print("-" * 30)
    
    try:
        # 测试从 core.plugin_system 导入
        print("测试从 core.plugin_system 导入...")
        from core.plugin_system import IPlugin, PluginMetadata, PluginStatus
        print("   ✅ 基础插件类导入成功")
        
        # 测试从 core.plugin_system 包导入
        print("测试从 core.plugin_system 包导入...")
        from core.plugin_system import EnhancedPluginManager
        print("   ✅ 增强插件管理器导入成功")
        
        # 测试创建实例
        print("测试创建插件管理器实例...")
        manager = EnhancedPluginManager(None)
        print("   ✅ 插件管理器实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 插件系统导入失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始诊断 TimeNest 导入问题...")
    
    # 测试基础导入
    basic_success = test_specific_imports()
    
    # 测试类导入
    class_success = test_specific_classes()
    
    # 测试插件系统
    plugin_success = test_plugin_system_imports()
    
    print("\n" + "=" * 50)
    print("🎯 诊断总结:")
    print(f"   基础模块导入: {'✅ 成功' if basic_success else '❌ 失败'}")
    print(f"   类导入测试: {'✅ 成功' if class_success else '❌ 失败'}")
    print(f"   插件系统测试: {'✅ 成功' if plugin_success else '❌ 失败'}")
    
    if basic_success and class_success and plugin_success:
        print("\n🎉 所有导入测试通过! 可以尝试运行 main.py")
        return True
    else:
        print("\n❌ 存在导入问题，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
