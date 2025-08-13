#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的构建脚本，用于测试PyInstaller是否能正常工作
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """构建可执行文件"""
    print("开始构建TimeNest可执行文件...")
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "TimeNest",
        str(project_root / "main.py")
    ]
    
    # 如果有图标文件，添加图标参数
    icon_path = project_root / "assets" / "logo.svg"
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行构建
        subprocess.check_call(cmd)
        print("构建成功完成！")
        print("可执行文件位于 dist/ 目录中")
        
        # 显示生成的文件信息
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            print("\n生成的文件:")
            for file in dist_dir.iterdir():
                if file.is_file():
                    size = file.stat().st_size
                    print(f"  {file.name}: {size} bytes")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()