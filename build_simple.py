#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的PyInstaller构建脚本
用于在GitHub Actions中构建TimeNest
"""

import os
import sys
import subprocess
from pathlib import Path

def build_timenest():
    """构建TimeNest可执行文件"""
    from utils.shared_utilities import setup_encoding
    from utils.config_constants import PYINSTALLER_HIDDEN_IMPORTS, PYINSTALLER_EXCLUDES

    setup_encoding()

    project_root = Path(__file__).parent

    print("Starting TimeNest build...")
    print(f"Project directory: {project_root}")

    main_py = project_root / "main.py"
    if not main_py.exists():
        print("ERROR: main.py file not found")
        return False
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "TimeNest",
        "--clean",
        "--noconfirm",
    ]
    
    # 添加数据文件 - 使用正确的路径分隔符
    data_dirs = ["qml", "resources", "themes", "RinUI", "config"]
    for data_dir in data_dirs:
        data_path = project_root / data_dir
        if data_path.exists():
            # Windows使用分号，Unix使用冒号
            separator = ";" if os.name == "nt" else ":"
            cmd.extend(["--add-data", f"{data_path}{separator}{data_dir}"])
            print(f"Adding data directory: {data_dir}")

    # 添加单个文件
    data_files = ["app_info.json", "schedule_template.xlsx"]
    for data_file in data_files:
        file_path = project_root / data_file
        if file_path.exists():
            separator = ";" if os.name == "nt" else ":"
            cmd.extend(["--add-data", f"{file_path}{separator}."])
            print(f"Adding data file: {data_file}")
    
    for module in PYINSTALLER_HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", module])

    for module in PYINSTALLER_EXCLUDES:
        cmd.extend(["--exclude-module", module])
    
    # 添加主文件
    cmd.append(str(main_py))
    
    print("Executing PyInstaller command:")
    print(" ".join(cmd))

    try:
        # 执行构建
        result = subprocess.run(cmd, cwd=project_root, check=True,
                              capture_output=True, text=True)

        print("Build successful!")
        print(result.stdout)

        # 检查输出文件
        exe_path = project_root / "dist" / "TimeNest.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Executable size: {size_mb:.1f}MB")
            print(f"Output path: {exe_path}")
            return True
        else:
            print("ERROR: Generated executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print("ERROR: Build failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Build process failed: {e}")
        return False

def main():
    """主函数"""
    if build_timenest():
        print("SUCCESS: TimeNest build completed!")
        sys.exit(0)
    else:
        print("FAILED: TimeNest build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
