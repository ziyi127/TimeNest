#!/usr/bin/env python3
"""
运行所有静态分析工具的脚本
"""

import os
import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str], description: str) -> bool:
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行 {description}")
    print(f"命令: {' '.join(command)}")
    print("=" * 60)

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"返回码: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"运行命令时出错: {e}")
        return False


def main() -> int:
    # 确保在虚拟环境中运行
    if not os.environ.get("VIRTUAL_ENV"):
        print("警告: 未检测到虚拟环境，正在激活...")
        # 注意: 在子进程中激活虚拟环境不会影响父进程
        # 这里我们假设脚本已在虚拟环境中运行

    # 定义要运行的分析工具命令
    commands: List[Tuple[List[str], str]] = [
        (["flake8", "."], "Flake8 代码风格检查"),
        (["pylint", "--recursive=y", "."], "Pylint 代码质量检查"),
        (["mypy", "--package", "core", "--package", "models", "--package", "ui"], "Mypy 类型检查"),
        (["bandit", "-r", "."], "Bandit 安全漏洞扫描"),
        (["black", "--check", "."], "Black 代码格式检查"),
        (["isort", "--check-only", "."], "ISort 导入排序检查"),
    ]

    # 运行所有分析工具
    results: List[Tuple[str, bool]] = []
    for command, description in commands:
        # 在虚拟环境中运行命令
        # 注意：在subprocess中激活虚拟环境比较复杂，这里我们假设脚本已在正确的环境中运行
        success = run_command(command, description)
        results.append((description, success))

    # 输出总结
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

    all_passed = True
    for description, success in results:
        status = "通过" if success else "失败"
        print(f"{description}: {status}")
        if not success:
            all_passed = False

    if all_passed:
        print("\n所有检查都通过了!")
        return 0
    
    print("\n一些检查失败了，请查看上面的输出以了解详细信息。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
