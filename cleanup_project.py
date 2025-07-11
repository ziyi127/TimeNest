#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 项目清理脚本
彻底清理项目中的临时文件、缓存文件和开发环境残留
"""

import os
import sys
import shutil
import glob
from pathlib import Path
from typing import List, Set
import argparse
import time


class ProjectCleaner:
    """项目清理器"""
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = Path(project_root).resolve()
        self.dry_run = dry_run
        self.deleted_files = []
        self.deleted_dirs = []
        self.total_size_freed = 0
        
        # 定义要清理的模式
        self.cleanup_patterns = {
            'python_cache': [
                '__pycache__',
                '*.pyc',
                '*.pyo',
                '*.pyd',
                '.pytest_cache',
                '*.egg-info',
                'dist',
                'build',
                '.mypy_cache',
                '.tox'
            ],
            'virtual_envs': [
                'venv',
                'env',
                '.venv',
                '.env',
                'dev-env',
                'test-env',
                'virtualenv'
            ],
            'ide_files': [
                '.vscode',
                '.idea',
                '*.swp',
                '*.swo',
                '*~',
                '.spyderproject',
                '.spyproject',
                '.ropeproject'
            ],
            'logs_and_temp': [
                '*.log',
                '.DS_Store',
                'Thumbs.db',
                '*.tmp',
                '*.temp',
                '*.bak',
                '*.orig'
            ],
            'test_coverage': [
                'htmlcov',
                '.coverage',
                '.coverage.*',
                'coverage.xml',
                '.pytest_cache',
                '.cache'
            ],
            'other_cache': [
                '.cache',
                'node_modules',
                '.npm',
                '.yarn',
                '.sass-cache',
                '.parcel-cache'
            ]
        }
        
        # 要保护的重要文件和目录
        self.protected_patterns = {
            '.git',
            '.gitignore',
            '.gitattributes',
            'requirements*.txt',
            'setup.py',
            'setup.cfg',
            'pyproject.toml',
            'Pipfile',
            'Pipfile.lock',
            'poetry.lock',
            'README.md',
            'LICENSE',
            'CHANGELOG.md',
            'CONTRIBUTING.md',
            'MANIFEST.in',
            '.github',
            'docs',
            'assets',
            'resources',
            'static',
            'media'
        }
    
    def is_protected(self, path: Path) -> bool:
        """检查路径是否受保护"""
        path_str = str(path.relative_to(self.project_root))
        
        for pattern in self.protected_patterns:
            if pattern in path_str or path.name == pattern:
                return True
        
        # 检查是否是源代码文件
        if path.is_file():
            source_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini'}
            if path.suffix.lower() in source_extensions:
                # 进一步检查是否是重要文件
                important_files = {'main.py', 'app.py', '__init__.py', 'config.py'}
                if path.name in important_files:
                    return True
        
        return False
    
    def get_file_size(self, path: Path) -> int:
        """获取文件或目录大小"""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                total_size = 0
                for item in path.rglob('*'):
                    if item.is_file():
                        try:
                            total_size += item.stat().st_size
                        except (OSError, PermissionError):
                            pass
                return total_size
        except (OSError, PermissionError):
            pass
        return 0
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def scan_for_cleanup(self) -> dict:
        """扫描需要清理的文件"""
        cleanup_items = {
            'files': [],
            'directories': []
        }
        
        print(f"🔍 扫描项目目录: {self.project_root}")
        print("=" * 60)
        
        # 遍历项目目录
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # 跳过受保护的目录
            if self.is_protected(root_path):
                continue
            
            # 检查目录
            for dir_name in dirs[:]:  # 使用切片复制，避免修改迭代中的列表
                dir_path = root_path / dir_name
                
                if self.is_protected(dir_path):
                    continue
                
                # 检查是否匹配清理模式
                for category, patterns in self.cleanup_patterns.items():
                    for pattern in patterns:
                        if '*' in pattern:
                            # 通配符模式
                            if dir_path.match(pattern):
                                cleanup_items['directories'].append({
                                    'path': dir_path,
                                    'category': category,
                                    'pattern': pattern,
                                    'size': self.get_file_size(dir_path)
                                })
                                dirs.remove(dir_name)  # 不再遍历此目录
                                break
                        else:
                            # 精确匹配
                            if dir_name == pattern:
                                cleanup_items['directories'].append({
                                    'path': dir_path,
                                    'category': category,
                                    'pattern': pattern,
                                    'size': self.get_file_size(dir_path)
                                })
                                dirs.remove(dir_name)  # 不再遍历此目录
                                break
                    else:
                        continue
                    break
            
            # 检查文件
            for file_name in files:
                file_path = root_path / file_name
                
                if self.is_protected(file_path):
                    continue
                
                # 检查是否匹配清理模式
                for category, patterns in self.cleanup_patterns.items():
                    for pattern in patterns:
                        if '*' in pattern:
                            # 通配符模式
                            if file_path.match(pattern):
                                cleanup_items['files'].append({
                                    'path': file_path,
                                    'category': category,
                                    'pattern': pattern,
                                    'size': self.get_file_size(file_path)
                                })
                                break
                        else:
                            # 精确匹配
                            if file_name == pattern:
                                cleanup_items['files'].append({
                                    'path': file_path,
                                    'category': category,
                                    'pattern': pattern,
                                    'size': self.get_file_size(file_path)
                                })
                                break
                    else:
                        continue
                    break
        
        return cleanup_items
    
    def display_cleanup_summary(self, cleanup_items: dict):
        """显示清理摘要"""
        print("\n📋 清理摘要")
        print("=" * 60)
        
        # 按类别统计
        category_stats = {}
        total_files = len(cleanup_items['files'])
        total_dirs = len(cleanup_items['directories'])
        total_size = 0
        
        for item in cleanup_items['files'] + cleanup_items['directories']:
            category = item['category']
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'size': 0}
            category_stats[category]['count'] += 1
            category_stats[category]['size'] += item['size']
            total_size += item['size']
        
        # 显示统计信息
        print(f"📁 目录: {total_dirs} 个")
        print(f"📄 文件: {total_files} 个")
        print(f"💾 总大小: {self.format_size(total_size)}")
        print()
        
        # 按类别显示
        for category, stats in category_stats.items():
            print(f"🏷️  {category}: {stats['count']} 项, {self.format_size(stats['size'])}")
        
        print()
        
        # 显示详细列表
        if cleanup_items['directories']:
            print("📁 将删除的目录:")
            for item in sorted(cleanup_items['directories'], key=lambda x: str(x['path'])):
                rel_path = item['path'].relative_to(self.project_root)
                size_str = self.format_size(item['size'])
                print(f"   {rel_path} ({size_str}) [{item['category']}]")
            print()
        
        if cleanup_items['files']:
            print("📄 将删除的文件:")
            for item in sorted(cleanup_items['files'], key=lambda x: str(x['path'])):
                rel_path = item['path'].relative_to(self.project_root)
                size_str = self.format_size(item['size'])
                print(f"   {rel_path} ({size_str}) [{item['category']}]")
            print()
    
    def execute_cleanup(self, cleanup_items: dict):
        """执行清理操作"""
        if self.dry_run:
            print("🔍 DRY RUN 模式 - 不会实际删除文件")
            return
        
        print("🧹 开始清理...")
        print("=" * 60)
        
        # 删除目录
        for item in cleanup_items['directories']:
            try:
                if item['path'].exists():
                    shutil.rmtree(item['path'])
                    self.deleted_dirs.append(str(item['path'].relative_to(self.project_root)))
                    self.total_size_freed += item['size']
                    print(f"✅ 删除目录: {item['path'].relative_to(self.project_root)}")
            except Exception as e:
                print(f"❌ 删除目录失败: {item['path'].relative_to(self.project_root)} - {e}")
        
        # 删除文件
        for item in cleanup_items['files']:
            try:
                if item['path'].exists():
                    item['path'].unlink()
                    self.deleted_files.append(str(item['path'].relative_to(self.project_root)))
                    self.total_size_freed += item['size']
                    print(f"✅ 删除文件: {item['path'].relative_to(self.project_root)}")
            except Exception as e:
                print(f"❌ 删除文件失败: {item['path'].relative_to(self.project_root)} - {e}")
    
    def generate_report(self):
        """生成清理报告"""
        print("\n📊 清理报告")
        print("=" * 60)
        print(f"🗂️  删除目录: {len(self.deleted_dirs)} 个")
        print(f"📄 删除文件: {len(self.deleted_files)} 个")
        print(f"💾 释放空间: {self.format_size(self.total_size_freed)}")
        print(f"⏰ 清理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.dry_run:
            # 保存清理日志
            log_file = self.project_root / 'cleanup_log.txt'
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"TimeNest 项目清理日志\n")
                f.write(f"清理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"项目路径: {self.project_root}\n\n")
                
                f.write(f"删除的目录 ({len(self.deleted_dirs)} 个):\n")
                for dir_path in self.deleted_dirs:
                    f.write(f"  - {dir_path}\n")
                
                f.write(f"\n删除的文件 ({len(self.deleted_files)} 个):\n")
                for file_path in self.deleted_files:
                    f.write(f"  - {file_path}\n")
                
                f.write(f"\n释放空间: {self.format_size(self.total_size_freed)}\n")
            
            print(f"📝 清理日志已保存到: {log_file}")
    
    def run(self):
        """运行清理程序"""
        print("🧹 TimeNest 项目清理工具")
        print("=" * 60)
        print(f"项目路径: {self.project_root}")
        print(f"运行模式: {'DRY RUN (预览)' if self.dry_run else '实际清理'}")
        print()
        
        # 扫描需要清理的文件
        cleanup_items = self.scan_for_cleanup()
        
        if not cleanup_items['files'] and not cleanup_items['directories']:
            print("✨ 项目已经很干净了，没有找到需要清理的文件！")
            return
        
        # 显示清理摘要
        self.display_cleanup_summary(cleanup_items)
        
        # 确认清理
        if not self.dry_run:
            response = input("❓ 确认执行清理操作？(y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ 清理操作已取消")
                return
        
        # 执行清理
        self.execute_cleanup(cleanup_items)
        
        # 生成报告
        self.generate_report()
        
        print("\n🎉 清理完成！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TimeNest 项目清理工具')
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
        
        cleaner = ProjectCleaner(project_root, args.dry_run)
        cleaner.run()
        
    except KeyboardInterrupt:
        print("\n❌ 清理操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 清理过程中发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
