#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置合并逻辑
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from core.config_manager import ConfigManager


def test_config_merge():
    """测试配置合并逻辑"""
    print("🧪 测试配置合并逻辑...")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    
    # 清除现有配置
    print("🧹 清除现有配置...")
    config_manager.set_config('floating_widget.width', None, 'main', save=False)
    config_manager.set_config('floating_widget.width', None, 'user', save=False)
    config_manager.set_config('floating_widget.width', None, 'component', save=False)
    
    # 设置不同配置源的值
    print("📝 设置不同配置源的值...")
    config_manager.set_config('floating_widget.width', 100, 'layout', save=False)    # 最低优先级
    config_manager.set_config('floating_widget.width', 200, 'component', save=False) # 低优先级
    config_manager.set_config('floating_widget.width', 300, 'main', save=False)      # 高优先级
    config_manager.set_config('floating_widget.width', 400, 'user', save=False)      # 最高优先级
    
    # 测试各个配置源
    layout_width = config_manager.get_config('floating_widget.width', 0, 'layout')
    component_width = config_manager.get_config('floating_widget.width', 0, 'component')
    main_width = config_manager.get_config('floating_widget.width', 0, 'main')
    user_width = config_manager.get_config('floating_widget.width', 0, 'user')
    
    print(f"  Layout配置: {layout_width}")
    print(f"  Component配置: {component_width}")
    print(f"  Main配置: {main_width}")
    print(f"  User配置: {user_width}")
    
    # 测试合并配置
    merged_width = config_manager.get_merged_config('floating_widget', {}).get('width', 0)
    print(f"  合并后配置: {merged_width}")
    
    # 验证优先级
    if merged_width == 400:  # 应该是用户配置的值
        print("✅ 配置合并优先级正确 (user > main > component > layout)")
        return True
    else:
        print(f"❌ 配置合并优先级错误，期望 400，实际 {merged_width}")
        return False


def test_config_override():
    """测试配置覆盖"""
    print("\n🧪 测试配置覆盖...")
    
    config_manager = ConfigManager()
    
    # 设置主配置
    config_manager.set_config('floating_widget.width', 888, 'main')
    
    # 检查是否正确保存和读取
    saved_width = config_manager.get_config('floating_widget.width', 0, 'main')
    merged_width = config_manager.get_merged_config('floating_widget', {}).get('width', 0)
    
    print(f"  主配置中的宽度: {saved_width}")
    print(f"  合并配置中的宽度: {merged_width}")
    
    if saved_width == 888:
        print("✅ 主配置保存正确")
        if merged_width == 888:
            print("✅ 配置合并正确")
            return True
        else:
            print(f"❌ 配置合并错误，期望 888，实际 {merged_width}")
            return False
    else:
        print(f"❌ 主配置保存错误，期望 888，实际 {saved_width}")
        return False


def main():
    """主函数"""
    print("🚀 配置合并测试开始")
    print("=" * 40)
    
    tests = [
        ("配置合并优先级", test_config_merge),
        ("配置覆盖", test_config_override),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"💥 {test_name} 异常: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
