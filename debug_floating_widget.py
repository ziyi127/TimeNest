#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 浮窗模块显示问题调试脚本
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_floating_widget_config():
    """调试浮窗配置"""
    print("🔍 TimeNest 浮窗模块显示问题调试")
    print("=" * 50)
    
    try:
        # 1. 检查配置管理器
        print("\n1. 检查配置管理器...")
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        # 获取浮窗配置
        floating_config = config_manager.get_config('floating_widget', 'component')
        print(f"浮窗配置: {floating_config}")
        
        if floating_config:
            modules_config = floating_config.get('modules', {})
            print(f"模块配置: {modules_config}")
            
            enabled_modules = [
                module_id for module_id, config in modules_config.items()
                if config.get('enabled', True)
            ]
            print(f"启用的模块: {enabled_modules}")
        else:
            print("❌ 未找到浮窗配置")
            
        # 2. 检查模块类是否可用
        print("\n2. 检查模块类...")
        try:
            from ui.floating_widget.floating_modules import (
                TimeModule, ScheduleModule, CountdownModule, 
                WeatherModule, SystemStatusModule
            )
            print("✅ 所有模块类导入成功")
            
            # 测试模块实例化
            time_module = TimeModule()
            print(f"✅ 时间模块实例化成功: {time_module.get_display_text()}")
            
            schedule_module = ScheduleModule()
            print(f"✅ 课程模块实例化成功: {schedule_module.get_display_text()}")
            
        except Exception as e:
            print(f"❌ 模块类导入/实例化失败: {e}")
            
        # 3. 模拟浮窗配置加载
        print("\n3. 模拟浮窗配置加载...")
        
        # 创建测试配置
        test_config = {
            'modules': {
                'time': {'enabled': True, 'order': 0},
                'schedule': {'enabled': True, 'order': 1},
                'countdown': {'enabled': False, 'order': 2},
                'weather': {'enabled': False, 'order': 3},
                'system': {'enabled': False, 'order': 4}
            }
        }
        
        # 保存测试配置
        config_manager.set_config('floating_widget', test_config, 'component')
        print("✅ 测试配置已保存")
        
        # 重新读取配置
        saved_config = config_manager.get_config('floating_widget', 'component')
        print(f"保存后的配置: {saved_config}")
        
        # 4. 测试模块加载逻辑
        print("\n4. 测试模块加载逻辑...")
        
        modules_config = saved_config.get('modules', {})
        enabled_modules = [
            module_id for module_id, config in modules_config.items()
            if config.get('enabled', True)
        ]
        
        print(f"从配置中解析的启用模块: {enabled_modules}")
        
        # 按顺序排序
        module_order = sorted(
            enabled_modules,
            key=lambda x: modules_config.get(x, {}).get('order', 0)
        )
        print(f"排序后的模块顺序: {module_order}")
        
        # 5. 检查配置文件
        print("\n5. 检查配置文件...")
        config_file = Path("config") / "config.json"
        if config_file.exists():
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            floating_config_in_file = file_config.get('floating_widget', {})
            print(f"配置文件中的浮窗配置: {floating_config_in_file}")
        else:
            print("❌ 配置文件不存在")
            
        print("\n✅ 调试完成")
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_default_config():
    """创建默认配置"""
    print("\n🔧 创建默认浮窗配置...")
    
    try:
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        default_config = {
            'width': 400,
            'height': 60,
            'border_radius': 30,
            'opacity': 0.9,
            'position': {'x': 0, 'y': 10},
            'mouse_transparent': False,
            'fixed_position': True,
            'auto_rotate_content': False,
            'rotation_interval': 5000,
            'modules': {
                'time': {
                    'enabled': True,
                    'order': 0,
                    'format_24h': True,
                    'show_seconds': False
                },
                'schedule': {
                    'enabled': True,
                    'order': 1
                },
                'countdown': {
                    'enabled': False,
                    'order': 2
                },
                'weather': {
                    'enabled': False,
                    'order': 3,
                    'api_key': '',
                    'city': ''
                },
                'system': {
                    'enabled': False,
                    'order': 4
                }
            }
        }
        
        config_manager.set_config('floating_widget', default_config, 'component')
        print("✅ 默认配置已创建")
        
        # 验证保存
        saved_config = config_manager.get_config('floating_widget', 'component')
        print(f"验证保存的配置: {saved_config}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建默认配置失败: {e}")
        return False


def test_module_display():
    """测试模块显示"""
    print("\n🧪 测试模块显示...")
    
    try:
        from ui.floating_widget.floating_modules import (
            TimeModule, ScheduleModule
        )
        
        # 创建模块实例
        time_module = TimeModule()
        schedule_module = ScheduleModule()
        
        # 测试显示文本
        time_text = time_module.get_display_text()
        schedule_text = schedule_module.get_display_text()
        
        print(f"时间模块显示: {time_text}")
        print(f"课程模块显示: {schedule_text}")
        
        # 测试工具提示
        time_tooltip = time_module.get_tooltip()
        schedule_tooltip = schedule_module.get_tooltip()
        
        print(f"时间模块提示: {time_tooltip}")
        print(f"课程模块提示: {schedule_tooltip}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始调试浮窗模块显示问题")
    
    # 1. 调试配置
    if not debug_floating_widget_config():
        print("❌ 配置调试失败")
        return False
    
    # 2. 创建默认配置
    if not create_default_config():
        print("❌ 创建默认配置失败")
        return False
    
    # 3. 测试模块显示
    if not test_module_display():
        print("❌ 模块显示测试失败")
        return False
    
    print("\n🎉 调试完成！")
    print("\n💡 建议:")
    print("1. 重启 TimeNest 应用")
    print("2. 打开浮窗设置，确认模块已启用")
    print("3. 检查浮窗是否正确显示模块内容")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
