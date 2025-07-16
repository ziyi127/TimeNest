#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最简单的PyInstaller构建脚本
专为GitHub Actions设计，避免编码问题
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主函数 - 最简单的构建方式"""
    
    # 设置编码
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    print("Starting TimeNest build (fallback mode)...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    main_py = project_root / "main.py"
    
    if not main_py.exists():
        print("ERROR: main.py not found")
        sys.exit(1)
    
    # 最简单的PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "TimeNest",
        "--clean",
        "--noconfirm",
        str(main_py)
    ]
    
    print("Executing command:", " ".join(cmd))
    
    try:
        # 执行构建
        result = subprocess.run(cmd, cwd=project_root, check=True)
        
        # 检查输出
        exe_path = project_root / "dist" / "TimeNest.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Build successful! Size: {size_mb:.1f}MB")
            print(f"Output: {exe_path}")
            sys.exit(0)
        else:
            print("ERROR: Executable not found")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
