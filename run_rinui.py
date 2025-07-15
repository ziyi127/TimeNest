#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest RinUI版本启动脚本
"""

import sys
import os
import subprocess
from pathlib import Path

def check_rinui_installation():
    """检查RinUI是否已安装"""
    try:
        import RinUI
        print(f"✅ RinUI 已安装，版本: {RinUI.__version__}")
        return True
    except ImportError:
        print("❌ RinUI 未安装")
        return False

def install_rinui():
    """安装RinUI"""
    print("正在安装 RinUI...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "RinUI"])
        print("✅ RinUI 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ RinUI 安装失败: {e}")
        return False

def check_dependencies():
    """检查所有依赖"""
    dependencies = {
        'PySide6': 'PySide6',
        'RinUI': 'RinUI',
        'requests': 'requests',
        'psutil': 'psutil',
        'PyYAML': 'yaml'
    }
    
    missing = []
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name} 已安装")
        except ImportError:
            print(f"❌ {name} 未安装")
            missing.append(name)
    
    return missing

def install_dependencies(missing):
    """安装缺失的依赖"""
    if not missing:
        return True
    
    print(f"\n正在安装缺失的依赖: {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 TimeNest RinUI版本启动器")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    print(f"✅ Python 版本: {sys.version}")
    
    # 检查依赖
    print("\n📦 检查依赖...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  发现缺失依赖: {', '.join(missing)}")
        response = input("是否自动安装缺失的依赖? (y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            if not install_dependencies(missing):
                print("❌ 依赖安装失败，无法启动应用")
                sys.exit(1)
        else:
            print("❌ 缺少必要依赖，无法启动应用")
            print(f"请手动安装: pip install {' '.join(missing)}")
            sys.exit(1)
    
    # 检查QML文件
    qml_main = Path("qml/main.qml")
    if not qml_main.exists():
        print(f"❌ 主QML文件不存在: {qml_main}")
        print("请确保QML文件已正确创建")
        sys.exit(1)
    
    print("✅ QML文件检查通过")
    
    # 启动应用
    print("\n🎯 启动 TimeNest RinUI版本...")
    try:
        # 导入并运行主应用
        from main import main
        main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有文件都在正确位置")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
