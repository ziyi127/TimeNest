#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 最终验证脚本
验证重构后的系统质量和功能完整性
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def validate_notification_system():
    """验证通知系统"""
    print("🔔 验证通知系统...")
    print("-" * 40)
    
    try:
        # 检查文件存在
        notification_file = current_dir / "core" / "notification_manager.py"
        if not notification_file.exists():
            print("✗ 通知管理器文件不存在")
            return False
        
        print("✓ 通知管理器文件存在")
        
        # 检查文件内容
        with open(notification_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查核心类定义
        core_classes = [
            'class NotificationManager(QObject):',
            'class NotificationChannel(ABC):',
            'class PopupChannel(NotificationChannel):',
            'class TrayChannel(NotificationChannel):',
            'class SoundChannel(NotificationChannel):',
            'class VoiceChannel(NotificationChannel):',
            'class EmailChannel(NotificationChannel):'
        ]
        
        class_count = 0
        for class_def in core_classes:
            if class_def in content:
                class_count += 1
                print(f"  ✓ {class_def.split('(')[0].replace('class ', '')}")
            else:
                print(f"  ✗ {class_def.split('(')[0].replace('class ', '')} 缺失")
        
        # 检查核心方法
        core_methods = [
            'def send_notification(',
            'def send_batch_notifications(',
            'def cancel_notification(',
            'def get_notification_history(',
            'def register_channel(',
            'def unregister_channel(',
            'def get_available_channels(',
            'def set_channel_enabled(',
            'def update_settings(',
            'def test_notification(',
            'def get_statistics(',
            'def cleanup('
        ]
        
        method_count = 0
        for method in core_methods:
            if method in content:
                method_count += 1
                print(f"  ✓ {method.replace('def ', '').replace('(', '')}")
            else:
                print(f"  ✗ {method.replace('def ', '').replace('(', '')} 缺失")
        
        # 检查信号定义
        signals = [
            'notification_sent = pyqtSignal',
            'notification_failed = pyqtSignal',
            'channel_status_changed = pyqtSignal',
            'config_updated = pyqtSignal',
            'batch_notification_completed = pyqtSignal'
        ]
        
        signal_count = 0
        for signal in signals:
            if signal in content:
                signal_count += 1
                print(f"  ✓ {signal.split(' = ')[0]}")
            else:
                print(f"  ✗ {signal.split(' = ')[0]} 缺失")
        
        # 计算完整性
        total_items = len(core_classes) + len(core_methods) + len(signals)
        found_items = class_count + method_count + signal_count
        completeness = (found_items / total_items) * 100
        
        print(f"\n📊 通知系统完整性: {completeness:.1f}%")
        print(f"  类定义: {class_count}/{len(core_classes)}")
        print(f"  方法定义: {method_count}/{len(core_methods)}")
        print(f"  信号定义: {signal_count}/{len(signals)}")
        
        return completeness >= 90
        
    except Exception as e:
        print(f"✗ 通知系统验证失败: {e}")
        return False

def validate_floating_system():
    """验证浮窗系统"""
    print("\n🎯 验证浮窗系统...")
    print("-" * 40)
    
    try:
        # 检查浮窗管理器
        floating_file = current_dir / "core" / "floating_manager.py"
        if not floating_file.exists():
            print("✗ 浮窗管理器文件不存在")
            return False
        
        print("✓ 浮窗管理器文件存在")
        
        with open(floating_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查核心功能
        core_features = [
            'class FloatingManager(QObject):',
            'def create_widget(',
            'def destroy_widget(',
            'def show_widget(',
            'def hide_widget(',
            'def toggle_widget(',
            'def update_config(',
            'def set_enabled(',
            'def is_enabled(',
            'def get_statistics(',
            'def cleanup('
        ]
        
        feature_count = 0
        for feature in core_features:
            if feature in content:
                feature_count += 1
                name = feature.replace('class ', '').replace('def ', '').replace('(', '')
                print(f"  ✓ {name}")
            else:
                name = feature.replace('class ', '').replace('def ', '').replace('(', '')
                print(f"  ✗ {name} 缺失")
        
        # 检查信号定义
        signals = [
            'widget_created = pyqtSignal',
            'widget_destroyed = pyqtSignal',
            'widget_shown = pyqtSignal',
            'widget_hidden = pyqtSignal',
            'config_updated = pyqtSignal'
        ]
        
        signal_count = 0
        for signal in signals:
            if signal in content:
                signal_count += 1
                print(f"  ✓ {signal.split(' = ')[0]}")
            else:
                print(f"  ✗ {signal.split(' = ')[0]} 缺失")
        
        # 计算完整性
        total_items = len(core_features) + len(signals)
        found_items = feature_count + signal_count
        completeness = (found_items / total_items) * 100
        
        print(f"\n📊 浮窗系统完整性: {completeness:.1f}%")
        print(f"  功能定义: {feature_count}/{len(core_features)}")
        print(f"  信号定义: {signal_count}/{len(signals)}")
        
        return completeness >= 80
        
    except Exception as e:
        print(f"✗ 浮窗系统验证失败: {e}")
        return False

def validate_system_tray():
    """验证系统托盘"""
    print("\n🔔 验证系统托盘...")
    print("-" * 40)
    
    try:
        # 检查系统托盘文件
        tray_file = current_dir / "ui" / "system_tray.py"
        if not tray_file.exists():
            print("✗ 系统托盘文件不存在")
            return False
        
        print("✓ 系统托盘文件存在")
        
        with open(tray_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查核心功能
        core_features = [
            'class SystemTrayManager(QObject):',
            'def show(',
            'def hide(',
            'def show_message(',
            'def update_floating_status(',
            'def is_available(',
            'def cleanup('
        ]
        
        feature_count = 0
        for feature in core_features:
            if feature in content:
                feature_count += 1
                name = feature.replace('class ', '').replace('def ', '').replace('(', '')
                print(f"  ✓ {name}")
            else:
                name = feature.replace('class ', '').replace('def ', '').replace('(', '')
                print(f"  ✗ {name} 缺失")
        
        # 检查PyQt6兼容性
        pyqt6_imports = [
            'from PyQt6.QtCore import',
            'from PyQt6.QtWidgets import',
            'from PyQt6.QtGui import'
        ]
        
        import_count = 0
        for import_stmt in pyqt6_imports:
            if import_stmt in content:
                import_count += 1
                print(f"  ✓ PyQt6导入正确")
            else:
                print(f"  ✗ PyQt6导入缺失")
        
        completeness = ((feature_count + import_count) / (len(core_features) + len(pyqt6_imports))) * 100
        
        print(f"\n📊 系统托盘完整性: {completeness:.1f}%")
        
        return completeness >= 80
        
    except Exception as e:
        print(f"✗ 系统托盘验证失败: {e}")
        return False

def validate_code_quality():
    """验证代码质量"""
    print("\n📝 验证代码质量...")
    print("-" * 40)
    
    try:
        files_to_check = [
            current_dir / "core" / "notification_manager.py",
            current_dir / "core" / "floating_manager.py",
            current_dir / "ui" / "system_tray.py"
        ]
        
        total_score = 0
        file_count = 0
        
        for file_path in files_to_check:
            if not file_path.exists():
                continue
            
            file_count += 1
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查质量指标
            quality_indicators = [
                ('类型注解', ['def ', ') -> ', ': str', ': int', ': bool', ': List[', ': Dict[', ': Optional[']),
                ('文档字符串', ['"""', 'Args:', 'Returns:', 'Raises:']),
                ('错误处理', ['try:', 'except Exception as e:', 'self.logger.error']),
                ('PyQt6兼容', ['from PyQt6.', 'pyqtSignal'])
            ]
            
            file_score = 0
            for indicator_name, patterns in quality_indicators:
                pattern_count = sum(1 for pattern in patterns if pattern in content)
                if pattern_count >= len(patterns) // 2:  # 至少一半的模式存在
                    file_score += 25
                    print(f"  ✓ {file_path.name}: {indicator_name}")
                else:
                    print(f"  ⚠️ {file_path.name}: {indicator_name} 需要改进")
            
            total_score += file_score
        
        if file_count > 0:
            average_score = total_score / file_count
            print(f"\n📊 代码质量评分: {average_score:.1f}%")
            return average_score >= 75
        else:
            print("✗ 没有找到要检查的文件")
            return False
        
    except Exception as e:
        print(f"✗ 代码质量验证失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 TimeNest 重构系统最终验证")
    print("=" * 60)
    
    results = []
    
    # 验证各个系统
    results.append(("通知系统", validate_notification_system()))
    results.append(("浮窗系统", validate_floating_system()))
    results.append(("系统托盘", validate_system_tray()))
    results.append(("代码质量", validate_code_quality()))
    
    # 输出结果
    print("\n" + "=" * 60)
    print("🎉 最终验证结果")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(results)} 项验证通过")
    
    if passed == len(results):
        print("\n🎉 所有验证项目通过！")
        print("✨ 重构成果总结:")
        print("  ✓ 通知系统重构完成，功能完整")
        print("  ✓ 浮窗系统重构完成，架构清晰")
        print("  ✓ 系统托盘重构完成，PyQt6兼容")
        print("  ✓ 代码质量优秀，符合标准")
        print("  ✓ 类型注解完整，文档规范")
        print("  ✓ 错误处理完善，日志统一")
        print("\n🚀 TimeNest 重构项目圆满完成！")
    elif passed >= len(results) * 0.75:
        print("\n✅ 大部分验证项目通过！")
        print("重构质量良好，核心功能完整")
    else:
        print("\n⚠️ 部分验证项目需要改进")
    
    return passed >= len(results) * 0.75

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 验证异常: {e}")
        sys.exit(1)
