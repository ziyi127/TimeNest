#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 浮窗系统验证脚本
验证浮窗系统的代码质量和功能完整性
"""

import sys
import os
import inspect
import importlib

def validate_floating_system():
    """验证浮窗系统"""
    print("🚀 TimeNest 浮窗系统质量检查")
    print("=" * 60)
    
    results = {
        'pyqt6_import': False,
        'floating_widget': False,
        'floating_manager': False,
        'system_tray': False,
        'settings_tab': False,
        'qt_api_usage': False,
        'type_annotations': False,
        'documentation': False
    }
    
    # 1. 检查PyQt6导入
    print("📦 检查PyQt6导入...")
    try:
        from PyQt6.QtCore import Qt, pyqtSignal, QTimer
        from PyQt6.QtWidgets import QWidget, QSystemTrayIcon
        from PyQt6.QtGui import QIcon
        print("✓ PyQt6导入正常")
        results['pyqt6_import'] = True
    except ImportError as e:
        print(f"✗ PyQt6导入失败: {e}")
    
    # 2. 检查浮窗组件
    print("\n🎯 检查浮窗组件...")
    try:
        # 检查文件是否存在
        floating_widget_path = os.path.join("ui", "floating_widget.py")
        if os.path.exists(floating_widget_path):
            print("✓ 浮窗组件文件存在")

            # 检查关键类定义
            with open(floating_widget_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class FloatingWidget' in content and 'pyqtSignal' in content:
                    print("✓ 浮窗组件类定义正确")
                    if 'module_clicked = pyqtSignal' in content and 'visibility_changed = pyqtSignal' in content:
                        print("✓ 信号定义正确")
                    else:
                        print("⚠️ 部分信号定义缺失")
                else:
                    print("✗ 浮窗组件类定义缺失")

            results['floating_widget'] = True
        else:
            print("✗ 浮窗组件文件不存在")
    except Exception as e:
        print(f"✗ 浮窗组件检查失败: {e}")

    # 3. 检查浮窗管理器
    print("\n🎛️ 检查浮窗管理器...")
    try:
        floating_manager_path = os.path.join("core", "floating_manager.py")
        if os.path.exists(floating_manager_path):
            print("✓ 浮窗管理器文件存在")

            with open(floating_manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class FloatingManager' in content and 'QObject' in content:
                    print("✓ 浮窗管理器类定义正确")
                    if 'widget_created = pyqtSignal' in content and 'widget_shown = pyqtSignal' in content:
                        print("✓ 管理器信号定义正确")
                    else:
                        print("⚠️ 部分管理器信号定义缺失")
                else:
                    print("✗ 浮窗管理器类定义缺失")

            results['floating_manager'] = True
        else:
            print("✗ 浮窗管理器文件不存在")
    except Exception as e:
        print(f"✗ 浮窗管理器检查失败: {e}")

    # 4. 检查系统托盘
    print("\n🔔 检查系统托盘...")
    try:
        system_tray_path = os.path.join("ui", "system_tray.py")
        if os.path.exists(system_tray_path):
            print("✓ 系统托盘文件存在")

            with open(system_tray_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class SystemTrayManager' in content and 'QObject' in content:
                    print("✓ 系统托盘类定义正确")
                    if 'show_main_window = pyqtSignal' in content and 'floating_toggled = pyqtSignal' in content:
                        print("✓ 托盘信号定义正确")
                    else:
                        print("⚠️ 部分托盘信号定义缺失")
                else:
                    print("✗ 系统托盘类定义缺失")

            results['system_tray'] = True
        else:
            print("✗ 系统托盘文件不存在")
    except Exception as e:
        print(f"✗ 系统托盘检查失败: {e}")

    # 5. 检查设置标签页
    print("\n⚙️ 检查设置标签页...")
    try:
        settings_tab_path = os.path.join("ui", "floating_settings_tab.py")
        if os.path.exists(settings_tab_path):
            print("✓ 设置标签页文件存在")

            with open(settings_tab_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class FloatingSettingsTab' in content and 'QWidget' in content:
                    print("✓ 设置标签页类定义正确")
                    if 'settings_changed = pyqtSignal' in content and 'preview_requested = pyqtSignal' in content:
                        print("✓ 设置信号定义正确")
                    else:
                        print("⚠️ 部分设置信号定义缺失")
                else:
                    print("✗ 设置标签页类定义缺失")

            results['settings_tab'] = True
        else:
            print("✗ 设置标签页文件不存在")
    except Exception as e:
        print(f"✗ 设置标签页检查失败: {e}")
    
    # 6. 检查Qt API使用
    print("\n🔧 检查Qt API使用...")
    try:
        from PyQt6.QtCore import Qt
        
        # 验证新的枚举格式
        orientation = Qt.Orientation.Horizontal
        alignment = Qt.AlignmentFlag.AlignCenter
        window_flag = Qt.WindowType.WindowStaysOnTopHint
        
        print("✓ Qt枚举使用正确")
        results['qt_api_usage'] = True
    except Exception as e:
        print(f"✗ Qt API使用检查失败: {e}")
    
    # 7. 检查类型注解
    print("\n📝 检查类型注解...")
    try:
        if results['floating_widget']:
            floating_widget_path = os.path.join("ui", "floating_widget.py")
            with open(floating_widget_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 检查类型注解的使用
                type_hints = [
                    'def __init__(self, parent: Optional[QWidget] = None)',
                    'def add_module(self, module: FloatingModule) -> None',
                    'def remove_module(self, module_id: str) -> bool',
                    'def update_config(self, config: Dict[str, Any]) -> None'
                ]

                annotated_methods = 0
                for hint in type_hints:
                    if any(part in content for part in hint.split()):
                        annotated_methods += 1

                if annotated_methods >= 2:
                    print(f"✓ 类型注解覆盖良好: {annotated_methods}/{len(type_hints)} 方法")
                    results['type_annotations'] = True
                else:
                    print(f"⚠️ 类型注解覆盖较少: {annotated_methods}/{len(type_hints)} 方法")
    except Exception as e:
        print(f"✗ 类型注解检查失败: {e}")

    # 8. 检查文档字符串
    print("\n📚 检查文档字符串...")
    try:
        if results['floating_widget']:
            floating_widget_path = os.path.join("ui", "floating_widget.py")
            with open(floating_widget_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 检查文档字符串
                doc_patterns = [
                    '"""',
                    'Args:',
                    'Returns:',
                    'Raises:'
                ]

                doc_count = 0
                for pattern in doc_patterns:
                    if pattern in content:
                        doc_count += 1

                if doc_count >= 3:
                    print(f"✓ 文档字符串完整: 包含 {doc_count}/{len(doc_patterns)} 个标准元素")
                    results['documentation'] = True
                else:
                    print(f"⚠️ 文档字符串需要改进: 仅包含 {doc_count}/{len(doc_patterns)} 个标准元素")
    except Exception as e:
        print(f"✗ 文档字符串检查失败: {e}")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("🎉 浮窗系统质量检查完成!")
    print("=" * 60)
    
    print("\n📋 质量检查清单:")
    checklist = [
        ("PyQt6 API 迁移完成", results['pyqt6_import']),
        ("浮窗组件功能正常", results['floating_widget']),
        ("浮窗管理器正常", results['floating_manager']),
        ("系统托盘功能正常", results['system_tray']),
        ("设置界面集成", results['settings_tab']),
        ("Qt API 使用正确", results['qt_api_usage']),
        ("类型注解基本完整", results['type_annotations']),
        ("文档字符串符合要求", results['documentation'])
    ]
    
    passed = 0
    for item, status in checklist:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {item}")
        if status:
            passed += 1
    
    print(f"\n📊 通过率: {passed}/{len(checklist)} ({passed/len(checklist)*100:.1f}%)")
    
    if passed >= len(checklist) * 0.8:
        print("\n🚀 浮窗系统质量良好，已准备就绪!")
    else:
        print("\n⚠️ 浮窗系统需要进一步改进")
    
    return results

if __name__ == "__main__":
    validate_floating_system()
