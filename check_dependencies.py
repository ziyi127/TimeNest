#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 依赖检查脚本
检查所有依赖是否正确安装并可用
"""

import sys
import importlib
from pathlib import Path
from typing import List, Tuple, Dict


def check_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """检查模块是否可以导入"""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {e}"


def check_core_dependencies() -> List[Tuple[bool, str]]:
    """检查核心依赖"""
    dependencies = [
        ("PyQt6.QtCore", "PyQt6"),
        ("PyQt6.QtWidgets", "PyQt6"),
        ("PyQt6.QtGui", "PyQt6"),
        ("yaml", "PyYAML"),
        ("requests", "requests"),
        ("plyer", "plyer"),
        ("jsonschema", "jsonschema"),
    ]
    
    results = []
    for module, package in dependencies:
        results.append(check_import(module, package))
    
    return results


def check_optional_dependencies() -> List[Tuple[bool, str]]:
    """检查可选依赖"""
    dependencies = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("openpyxl", "openpyxl"),
        ("xlsxwriter", "xlsxwriter"),
        ("PIL", "Pillow"),
        ("coloredlogs", "coloredlogs"),
        ("cryptography", "cryptography"),
        ("psutil", "psutil"),
        ("sentry_sdk", "sentry-sdk"),
    ]
    
    results = []
    for module, package in dependencies:
        results.append(check_import(module, package))
    
    return results


def check_dev_dependencies() -> List[Tuple[bool, str]]:
    """检查开发依赖"""
    dependencies = [
        ("pytest", "pytest"),
        ("black", "black"),
        ("flake8", "flake8"),
        ("mypy", "mypy"),
        ("isort", "isort"),
        ("bandit", "bandit"),
        ("safety", "safety"),
    ]
    
    results = []
    for module, package in dependencies:
        results.append(check_import(module, package))
    
    return results


def check_project_modules() -> List[Tuple[bool, str]]:
    """检查项目内部模块"""
    modules = [
        "core.app_manager",
        "core.config_manager",
        "core.notification_manager",
        "core.floating_manager",
        "ui.system_tray",
        "models.schedule",
        "utils.text_to_speech",
    ]
    
    results = []
    for module in modules:
        results.append(check_import(module))
    
    return results


def get_python_info() -> Dict[str, str]:
    """获取Python环境信息"""
    return {
        "Python版本": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "Python路径": sys.executable,
        "平台": sys.platform,
        "架构": sys.maxsize > 2**32 and "64位" or "32位",
    }


def main():
    """主函数"""
    print("🔍 TimeNest 依赖检查工具")
    print("=" * 60)
    
    # Python环境信息
    print("\n📋 Python环境信息:")
    python_info = get_python_info()
    for key, value in python_info.items():
        print(f"  {key}: {value}")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("\n❌ Python版本过低，需要3.8或更高版本")
        return False
    
    # 检查核心依赖
    print("\n🔧 核心依赖检查:")
    core_results = check_core_dependencies()
    core_success = 0
    for success, message in core_results:
        print(f"  {message}")
        if success:
            core_success += 1
    
    # 检查可选依赖
    print("\n📦 可选依赖检查:")
    optional_results = check_optional_dependencies()
    optional_success = 0
    for success, message in optional_results:
        print(f"  {message}")
        if success:
            optional_success += 1
    
    # 检查开发依赖
    print("\n🛠️ 开发依赖检查:")
    dev_results = check_dev_dependencies()
    dev_success = 0
    for success, message in dev_results:
        print(f"  {message}")
        if success:
            dev_success += 1
    
    # 检查项目模块
    print("\n🏗️ 项目模块检查:")
    project_results = check_project_modules()
    project_success = 0
    for success, message in project_results:
        print(f"  {message}")
        if success:
            project_success += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 检查结果总结:")
    print(f"  核心依赖: {core_success}/{len(core_results)} ✅")
    print(f"  可选依赖: {optional_success}/{len(optional_results)} ✅")
    print(f"  开发依赖: {dev_success}/{len(dev_results)} ✅")
    print(f"  项目模块: {project_success}/{len(project_results)} ✅")
    
    # 建议
    print("\n💡 建议:")
    if core_success < len(core_results):
        print("  ⚠️ 核心依赖缺失，请运行: pip install -r requirements.txt")
    
    if optional_success < len(optional_results):
        missing_optional = len(optional_results) - optional_success
        print(f"  ℹ️ {missing_optional}个可选依赖缺失，某些功能可能不可用")
    
    if dev_success < len(dev_results):
        print("  🔧 开发依赖缺失，请运行: pip install -r requirements-dev.txt")
    
    if project_success < len(project_results):
        print("  🏗️ 项目模块导入失败，请检查代码完整性")
    
    # 返回是否可以运行
    can_run = core_success >= len(core_results) * 0.8 and project_success >= len(project_results) * 0.8
    
    if can_run:
        print("\n✅ TimeNest 可以正常运行!")
    else:
        print("\n❌ TimeNest 可能无法正常运行，请解决上述问题")
    
    return can_run


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
