#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest Release Creator
自动创建 Git 标签和触发 GitHub Release 的脚本
"""

import subprocess
import sys
import json
import re
from pathlib import Path

def get_current_version():
    """从 app_info.json 获取当前版本"""
    try:
        app_info_path = Path(__file__).parent.parent / "app_info.json"
        with open(app_info_path, 'r', encoding='utf-8') as f:
            app_info = json.load(f)
        return app_info['version']['number']
    except Exception as e:
        print(f"无法读取版本信息: {e}")
        return None

def validate_version(version):
    """验证版本号格式"""
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$'
    return re.match(pattern, version) is not None

def check_git_status():
    """检查 Git 状态"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("警告: 工作目录有未提交的更改")
            print("请先提交所有更改后再创建发布")
            return False
        return True
    except subprocess.CalledProcessError:
        print("错误: 无法检查 Git 状态")
        return False

def create_tag(version):
    """创建 Git 标签"""
    tag_name = f"v{version}"
    
    try:
        # 检查标签是否已存在
        result = subprocess.run(['git', 'tag', '-l', tag_name], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(f"标签 {tag_name} 已存在")
            return False
        
        # 创建标签
        subprocess.run(['git', 'tag', '-a', tag_name, '-m', f'Release {version}'], 
                      check=True)
        print(f"已创建标签: {tag_name}")
        
        # 推送标签
        subprocess.run(['git', 'push', 'origin', tag_name], check=True)
        print(f"已推送标签到远程仓库: {tag_name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"创建标签失败: {e}")
        return False

def main():
    """主函数"""
    print("TimeNest Release Creator")
    print("=" * 40)
    
    # 检查 Git 状态
    if not check_git_status():
        sys.exit(1)
    
    # 获取当前版本
    current_version = get_current_version()
    if current_version:
        print(f"当前版本: {current_version}")
        use_current = input(f"使用当前版本 {current_version} 创建发布? (y/n): ").lower()
        if use_current == 'y':
            version = current_version
        else:
            version = input("请输入新版本号 (例如: 2.1.0): ").strip()
    else:
        version = input("请输入版本号 (例如: 2.1.0): ").strip()
    
    # 验证版本号
    if not validate_version(version):
        print("错误: 版本号格式无效")
        print("正确格式: x.y.z 或 x.y.z-suffix (例如: 2.1.0 或 2.1.0-Preview)")
        sys.exit(1)
    
    # 确认创建
    print(f"\n即将创建发布:")
    print(f"版本: {version}")
    print(f"标签: v{version}")
    
    confirm = input("\n确认创建? (y/n): ").lower()
    if confirm != 'y':
        print("已取消")
        sys.exit(0)
    
    # 创建标签
    if create_tag(version):
        print(f"\n✅ 发布创建成功!")
        print(f"GitHub Actions 将自动构建并发布 TimeNest {version}")
        print(f"请访问 GitHub 仓库查看构建进度")
    else:
        print("\n❌ 发布创建失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
