#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的构建脚本，用于测试PyInstaller是否能正常工作
"""


import sys
import subprocess
from pathlib import Path

def build_executable():
    """构建可执行文件"""
    print("开始构建TimeNest可执行文件...")
    

    
    # 获取项目根目录
    project_root = Path(__file__).parent.resolve()
    
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
    else:
        # 尝试其他可能的图标文件
        icon_extensions = [".png", ".ico", ".icns"]
        for ext in icon_extensions:
            alt_icon_path = project_root / "assets" / f"logo{ext}"
            if alt_icon_path.exists():
                cmd.extend(["--icon", str(alt_icon_path)])
                break
    
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
        else:
            print("警告: 未找到dist目录")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

def check_environment():
    """检查构建环境"""
    print("检查构建环境...")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    if sys.version_info < (3, 7):
        print("警告: 建议使用Python 3.7或更高版本")
    
    # 检查操作系统
    print(f"操作系统: {sys.platform}")
    
    # 检查PySide6
    try:
        import PySide6
        print(f"PySide6版本: {PySide6.__version__}")
    except ImportError:
        print("警告: 未安装PySide6")

if __name__ == "__main__":
    check_environment()
    build_executable()