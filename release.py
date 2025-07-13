#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest Release Helper
自动化版本管理和发布流程
"""

import os
import sys
import re
import subprocess
import json
from datetime import datetime

def get_current_version():
    """从version_info.txt获取当前版本"""
    try:
        with open('version_info.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找版本号
            match = re.search(r"StringStruct\(u'ProductVersion', u'([^']+)'", content)
            if match:
                return match.group(1)
            # 备用方案：从filevers获取
            match = re.search(r"filevers=\((\d+), (\d+), (\d+), (\d+)\)", content)
            if match:
                return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    except FileNotFoundError:
        pass
    return "1.0.0"

def update_version_files(new_version):
    """更新版本信息文件"""
    # 解析版本号，支持 Preview 等后缀
    version_parts = new_version.split()
    base_version = version_parts[0]
    suffix = ' '.join(version_parts[1:]) if len(version_parts) > 1 else ''
    
    try:
        major, minor, patch = base_version.split('.')
    except ValueError:
        print(f"❌ 版本号格式错误: {new_version}")
        return
    
    # 更新 version_info.txt
    with open('version_info.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构建完整版本字符串
    full_version = f"{base_version}.0"
    if suffix:
        full_version += f" {suffix}"
    
    # 替换版本号
    content = re.sub(
        r"filevers=\(\d+, \d+, \d+, \d+\)",
        f"filevers=({major}, {minor}, {patch}, 0)",
        content
    )
    content = re.sub(
        r"prodvers=\(\d+, \d+, \d+, \d+\)",
        f"prodvers=({major}, {minor}, {patch}, 0)",
        content
    )
    content = re.sub(
        r"StringStruct\(u'FileVersion', u'[^']+'",
        f"StringStruct(u'FileVersion', u'{full_version}'",
        content
    )
    content = re.sub(
        r"StringStruct\(u'ProductVersion', u'[^']+'",
        f"StringStruct(u'ProductVersion', u'{full_version}'",
        content
    )
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新版本信息到 {new_version}")

def create_git_tag(version):
    """创建Git标签"""
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  检测到未提交的更改，请先提交所有更改")
            return False
        
        # 创建标签
        tag_name = f"v{version}"
        subprocess.run(['git', 'tag', '-a', tag_name, '-m', f'Release {version}'], 
                      check=True)
        print(f"✅ 已创建Git标签: {tag_name}")
        
        # 询问是否推送
        push = input("是否推送标签到远程仓库? (y/N): ").lower().strip()
        if push == 'y':
            subprocess.run(['git', 'push', 'origin', tag_name], check=True)
            print(f"✅ 已推送标签到远程仓库")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 未找到Git命令，请确保Git已安装")
        return False

def main():
    print("🚀 TimeNest Release Helper")
    print("=" * 40)
    
    current_version = get_current_version()
    print(f"当前版本: {current_version}")
    
    # 获取新版本号
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
    else:
        new_version = input(f"请输入新版本号 (当前: {current_version}): ").strip()
    
    if not new_version:
        print("❌ 版本号不能为空")
        return
    
    # 验证版本号格式（支持后缀如 Preview, Beta, RC 等）
    if not re.match(r'^\d+\.\d+\.\d+(\s+\w+)*$', new_version):
        print("❌ 版本号格式错误，应为: x.y.z 或 x.y.z Preview")
        return
    
    # 更新版本文件
    update_version_files(new_version)
    
    # 创建Git标签
    if os.path.exists('.git'):
        create_git_tag(new_version)
    else:
        print("⚠️  未检测到Git仓库，跳过标签创建")
    
    print("\n🎉 发布准备完成!")
    print(f"📦 版本: {new_version}")
    print("📋 下一步:")
    print("   1. 运行 build_release.bat 构建可执行文件")
    print("   2. 推送代码到GitHub触发自动发布")
    print("   3. 或手动上传构建文件到GitHub Releases")

if __name__ == '__main__':
    main()