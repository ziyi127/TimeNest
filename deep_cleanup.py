#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 深度清理脚本
查找和清理可能被遗漏的隐藏文件和特殊缓存
"""

import os
import sys
import shutil
import glob
from pathlib import Path
import argparse


def find_hidden_cache_files(project_root: Path):
    """查找隐藏的缓存文件"""
    print("🔍 深度扫描隐藏文件和特殊缓存...")
    print("=" * 60)
    
    found_items = []
    
    # 定义要查找的隐藏文件和缓存模式
    hidden_patterns = [
        # Python 相关
        '**/.pytest_cache',
        '**/.mypy_cache',
        '**/.tox',
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.pyd',
        '**/.coverage',
        '**/.coverage.*',
        '**/htmlcov',
        
        # IDE 和编辑器
        '**/.vscode',
        '**/.idea',
        '**/*.swp',
        '**/*.swo',
        '**/*~',
        '**/.spyderproject',
        '**/.spyproject',
        '**/.ropeproject',
        
        # 系统文件
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/desktop.ini',
        
        # 临时文件
        '**/*.tmp',
        '**/*.temp',
        '**/*.bak',
        '**/*.orig',
        '**/*.log',
        
        # 虚拟环境
        '**/venv',
        '**/env',
        '**/.venv',
        '**/.env',
        '**/virtualenv',
        
        # Node.js (如果有前端组件)
        '**/node_modules',
        '**/.npm',
        '**/.yarn',
        '**/package-lock.json',
        '**/yarn.lock',
        
        # 其他缓存
        '**/.cache',
        '**/.sass-cache',
        '**/.parcel-cache',
        '**/dist',
        '**/build',
        '**/*.egg-info'
    ]
    
    # 要保护的文件和目录
    protected_items = {
        '.git', '.gitignore', '.gitattributes',
        'requirements.txt', 'requirements-dev.txt', 'requirements-prod.txt', 'requirements-minimal.txt',
        'setup.py', 'setup.cfg', 'pyproject.toml',
        'README.md', 'LICENSE', 'CHANGELOG.md', 'CONTRIBUTING.md',
        'PLUGIN_DEVELOPMENT_GUIDE.md', 'INSTALL.md', 'SECURITY.md',
        '.github', 'docs', 'assets', 'resources', 'static', 'media',
        'plugin_template', 'tests'
    }
    
    for pattern in hidden_patterns:
        try:
            matches = list(project_root.glob(pattern))
            for match in matches:
                # 检查是否受保护
                rel_path = match.relative_to(project_root)
                path_parts = rel_path.parts
                
                # 检查路径中是否包含受保护的目录
                is_protected = False
                for part in path_parts:
                    if part in protected_items:
                        is_protected = True
                        break
                
                # 检查是否是重要的源代码文件
                if match.is_file():
                    if match.suffix in {'.py', '.md', '.txt', '.json', '.yaml', '.yml'}:
                        if any(important in match.name for important in ['main', 'app', '__init__', 'config', 'setup']):
                            is_protected = True
                
                if not is_protected and match.exists():
                    size = 0
                    if match.is_file():
                        size = match.stat().st_size
                    elif match.is_dir():
                        size = sum(f.stat().st_size for f in match.rglob('*') if f.is_file())
                    
                    found_items.append({
                        'path': match,
                        'type': 'directory' if match.is_dir() else 'file',
                        'size': size,
                        'pattern': pattern
                    })
        except Exception as e:
            print(f"⚠️ 扫描模式 {pattern} 时出错: {e}")
    
    return found_items


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TimeNest 深度清理工具')
    parser.add_argument('--dry-run', action='store_true', 
                       help='预览模式，不实际删除文件')
    parser.add_argument('--project-root', type=str, default='.',
                       help='项目根目录路径 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    try:
        project_root = Path(args.project_root).resolve()
        if not project_root.exists():
            print(f"❌ 项目目录不存在: {project_root}")
            sys.exit(1)
        
        print("🧹 TimeNest 深度清理工具")
        print("=" * 60)
        print(f"项目路径: {project_root}")
        print(f"运行模式: {'DRY RUN (预览)' if args.dry_run else '实际清理'}")
        print()
        
        # 查找隐藏文件
        found_items = find_hidden_cache_files(project_root)
        
        if not found_items:
            print("✨ 没有发现额外的缓存文件或临时文件！")
            return
        
        # 显示发现的文件
        print(f"\n📋 发现 {len(found_items)} 个项目需要清理")
        print("=" * 60)
        
        total_size = 0
        dirs_count = 0
        files_count = 0
        
        for item in sorted(found_items, key=lambda x: str(x['path'])):
            rel_path = item['path'].relative_to(project_root)
            size_str = format_size(item['size'])
            type_icon = "📁" if item['type'] == 'directory' else "📄"
            
            print(f"{type_icon} {rel_path} ({size_str})")
            
            total_size += item['size']
            if item['type'] == 'directory':
                dirs_count += 1
            else:
                files_count += 1
        
        print()
        print(f"📊 统计: {dirs_count} 个目录, {files_count} 个文件")
        print(f"💾 总大小: {format_size(total_size)}")
        
        if args.dry_run:
            print("\n🔍 DRY RUN 模式 - 不会实际删除文件")
            return
        
        # 确认删除
        response = input("\n❓ 确认删除这些文件？(y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ 清理操作已取消")
            return
        
        # 执行删除
        print("\n🧹 开始清理...")
        deleted_count = 0
        freed_size = 0
        
        for item in found_items:
            try:
                if item['path'].exists():
                    if item['type'] == 'directory':
                        shutil.rmtree(item['path'])
                    else:
                        item['path'].unlink()
                    
                    rel_path = item['path'].relative_to(project_root)
                    print(f"✅ 删除: {rel_path}")
                    deleted_count += 1
                    freed_size += item['size']
                    
            except Exception as e:
                rel_path = item['path'].relative_to(project_root)
                print(f"❌ 删除失败: {rel_path} - {e}")
        
        print(f"\n🎉 深度清理完成！")
        print(f"📊 删除了 {deleted_count} 个项目")
        print(f"💾 释放了 {format_size(freed_size)} 空间")
        
    except KeyboardInterrupt:
        print("\n❌ 清理操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 清理过程中发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
