#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 依赖修复脚本
自动安装缺失的依赖包
"""

import subprocess
import sys
from pathlib import Path

def install_package(package_name):
    """安装单个包"""
    try:
        print(f"📦 正在安装 {package_name}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def check_and_install_missing_deps():
    """检查并安装缺失的依赖"""
    print("🔧 TimeNest 依赖修复工具")
    print("=" * 50)
    
    # 常见缺失的依赖
    critical_packages = [
        "packaging",
        "PyQt6",
        "PyYAML", 
        "requests",
        "pandas",
        "numpy",
        "openpyxl",
        "python-dateutil",
        "Pillow",
        "psutil"
    ]
    
    missing_packages = []
    
    # 检查哪些包缺失
    print("🔍 检查依赖状态...")
    for package in critical_packages:
        try:
            if package == "PyYAML":
                import yaml
            elif package == "Pillow":
                import PIL
            elif package == "python-dateutil":
                import dateutil
            else:
                __import__(package.lower())
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (缺失)")
            missing_packages.append(package)
    
    if not missing_packages:
        print("\n🎉 所有关键依赖都已安装！")
        return True
    
    print(f"\n📋 发现 {len(missing_packages)} 个缺失的依赖:")
    for pkg in missing_packages:
        print(f"   • {pkg}")
    
    # 安装缺失的包
    print(f"\n📦 开始安装缺失的依赖...")
    success_count = 0
    
    for package in missing_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 安装结果: {success_count}/{len(missing_packages)} 成功")
    
    if success_count == len(missing_packages):
        print("🎉 所有依赖安装完成！")
        return True
    else:
        print("⚠️ 部分依赖安装失败，请手动安装")
        return False

def install_from_requirements():
    """从 requirements.txt 安装依赖"""
    print("\n📋 从 requirements.txt 安装依赖...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        print("✅ requirements.txt 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ requirements.txt 安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主函数"""
    print("🚀 开始修复 TimeNest 依赖问题...")
    
    # 方法1: 检查并安装关键依赖
    if check_and_install_missing_deps():
        print("\n✅ 关键依赖修复完成")
    else:
        print("\n⚠️ 关键依赖修复部分失败")
    
    # 方法2: 从 requirements.txt 安装
    if install_from_requirements():
        print("✅ requirements.txt 依赖安装完成")
    else:
        print("⚠️ requirements.txt 安装失败")
    
    print("\n" + "=" * 50)
    print("🎯 修复完成！请尝试运行:")
    print("   python main.py")
    print("\n💡 如果仍有问题，请尝试:")
    print("   pip install --upgrade pip")
    print("   pip install -r requirements.txt --force-reinstall")

if __name__ == "__main__":
    main()
