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
    for stream in [sys.stdout, sys.stderr]:
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')

    print("Starting TimeNest build (fallback mode)...")

    project_root = Path(__file__).parent
    main_py = project_root / "main.py"

    if not main_py.exists():
        print("ERROR: main.py not found")
        sys.exit(1)
    
    cmd = [
        "pyinstaller", "--onefile", "--windowed", "--name", "TimeNest",
        "--clean", "--noconfirm", str(main_py)
    ]
    
    print("Executing command:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, cwd=project_root, check=True)

        exe_path = project_root / "dist" / "TimeNest.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Build successful! Size: {size_mb:.1f}MB")
            print(f"Output: {exe_path}")
            sys.exit(0)

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
