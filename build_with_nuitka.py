#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Nuitka打包TimeNest程序的脚本
"""

import os
import sys
import subprocess
import shutil


def main():
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 定义源文件和输出目录
    main_py = os.path.join(project_root, "main.py")
    output_dir = os.path.join(project_root, "dist")
    
    # 清理之前的构建
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建命令
    # 不使用onefile模式，仅包含需要的库
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",  # 独立模式，包含所有依赖
        "--remove-output",  # 构建前删除输出目录
        "--output-dir=" + output_dir,
        "--windows-disable-console",  # Windows下禁用控制台
        "--windows-icon-from-ico=" + os.path.join(project_root, "TKtimetable.ico"),
        "--include-data-file=" + os.path.join(project_root, "TKtimetable.ico") + "=TKtimetable.ico",
        "--include-data-file=" + os.path.join(project_root, "timetable_ui_settings.json") + "=timetable_ui_settings.json",
        "--include-data-dir=" + os.path.join(project_root, "ui") + "=ui",
        "--nofollow-import-to=unittest",  # 排除不需要的模块
        "--nofollow-import-to=distutils",
        "--nofollow-import-to=setuptools",
        "--nofollow-import-to=pip",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=matplotlib",
        "--enable-plugin=tk-inter",  # 启用tkinter插件
        main_py
    ]
    
    print("正在使用Nuitka打包程序...")
    print("命令:", " ".join(cmd))
    
    # 执行构建命令
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print("\n程序打包成功!")
        print("输出目录:", output_dir)
        print("\n构建的可执行文件位于 dist/main.dist/ 目录中")
        print("注意: 这不是onefile模式，而是一个包含所有必要文件的目录")
    except subprocess.CalledProcessError as e:
        print("\n程序打包失败!")
        print("错误信息:", e)
        sys.exit(1)
    except FileNotFoundError:
        print("\n未找到Nuitka，请先安装Nuitka:")
        print("pip install nuitka")
        sys.exit(1)


if __name__ == "__main__":
    main()