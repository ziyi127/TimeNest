#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 依赖更新脚本
自动检查和更新项目依赖
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple


def run_command(cmd: List[str]) -> Tuple[bool, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_outdated_packages() -> List[Dict[str, str]]:
    """检查过时的包"""
    print("🔍 检查过时的包...")
    
    success, output = run_command([sys.executable, "-m", "pip", "list", "--outdated", "--format=json"])
    
    if not success:
        print(f"❌ 检查失败: {output}")
        return []
    
    try:
        outdated = json.loads(output)
        return outdated
    except json.JSONDecodeError:
        print("❌ 解析输出失败")
        return []


def update_requirements_file(file_path: Path, outdated: List[Dict[str, str]]):
    """更新 requirements 文件"""
    if not file_path.exists():
        print(f"⚠️ 文件不存在: {file_path}")
        return
    
    print(f"📝 更新 {file_path.name}...")
    
    # 读取当前文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 创建过时包的映射
    outdated_map = {pkg['name'].lower(): pkg['latest_version'] for pkg in outdated}
    
    # 更新版本号
    updated_lines = []
    updated_count = 0
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        # 跳过注释和空行
        if not line or line.startswith('#') or line.startswith('-r'):
            updated_lines.append(original_line)
            continue
        
        # 解析包名和版本
        if '>=' in line:
            pkg_name, version_spec = line.split('>=', 1)
            pkg_name = pkg_name.strip()
            
            if pkg_name.lower() in outdated_map:
                new_version = outdated_map[pkg_name.lower()]
                new_line = f"{pkg_name}>={new_version}\n"
                updated_lines.append(new_line)
                updated_count += 1
                print(f"  ✓ {pkg_name}: {version_spec.strip()} -> {new_version}")
            else:
                updated_lines.append(original_line)
        else:
            updated_lines.append(original_line)
    
    # 写回文件
    if updated_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print(f"  📦 更新了 {updated_count} 个包")
    else:
        print(f"  ✅ {file_path.name} 已是最新")


def check_security_vulnerabilities():
    """检查安全漏洞"""
    print("\n🔒 检查安全漏洞...")
    
    # 尝试使用 safety
    success, output = run_command([sys.executable, "-m", "pip", "install", "safety"])
    if success:
        success, output = run_command([sys.executable, "-m", "safety", "check"])
        if success:
            print("✅ 未发现安全漏洞")
        else:
            print(f"⚠️ 发现安全问题:\n{output}")
    else:
        print("⚠️ 无法安装 safety 工具")


def main():
    """主函数"""
    print("🚀 TimeNest 依赖更新工具")
    print("=" * 50)
    
    # 检查过时的包
    outdated = check_outdated_packages()
    
    if not outdated:
        print("✅ 所有包都是最新的")
        return
    
    print(f"\n📋 发现 {len(outdated)} 个过时的包:")
    for pkg in outdated:
        print(f"  • {pkg['name']}: {pkg['version']} -> {pkg['latest_version']}")
    
    # 询问是否更新
    response = input("\n❓ 是否更新 requirements 文件? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ 取消更新")
        return
    
    # 更新各个 requirements 文件
    project_root = Path(__file__).parent
    requirements_files = [
        project_root / "requirements.txt",
        project_root / "requirements-dev.txt",
        project_root / "requirements-prod.txt",
    ]
    
    for req_file in requirements_files:
        update_requirements_file(req_file, outdated)
    
    # 检查安全漏洞
    check_security_vulnerabilities()
    
    print("\n✅ 依赖更新完成!")
    print("\n📝 建议:")
    print("1. 测试应用功能确保兼容性")
    print("2. 运行测试套件: pytest tests/")
    print("3. 更新 requirements-prod.txt 中的固定版本")
    print("4. 提交更改到版本控制")


if __name__ == "__main__":
    main()
