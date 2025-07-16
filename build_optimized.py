#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 优化构建脚本
用于创建最小化的可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✅ 已删除 {dir_name}")
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def optimize_imports():
    """优化导入，移除未使用的模块"""
    print("📦 优化导入...")
    
    # 创建最小化的requirements.txt
    minimal_requirements = [
        'PySide6>=6.5.0',
        'RinUI',
    ]
    
    with open('requirements_minimal.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(minimal_requirements))
    
    print("  ✅ 创建最小化依赖文件")

def build_with_pyinstaller():
    """使用PyInstaller构建"""
    print("🔨 开始PyInstaller构建...")
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'TimeNest.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✅ PyInstaller构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ PyInstaller构建失败: {e}")
        print(f"  错误输出: {e.stderr}")
        return False

def post_build_optimization():
    """构建后优化"""
    print("⚡ 构建后优化...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ❌ dist目录不存在")
        return False
    
    # 查找可执行文件
    exe_files = list(dist_dir.glob('TimeNest*'))
    if not exe_files:
        print("  ❌ 未找到可执行文件")
        return False
    
    exe_file = exe_files[0]
    original_size = exe_file.stat().st_size
    
    print(f"  📊 原始大小: {original_size / 1024 / 1024:.2f} MB")
    
    # 如果有UPX，尝试进一步压缩
    try:
        subprocess.run(['upx', '--version'], check=True, capture_output=True)
        print("  🗜️ 使用UPX进一步压缩...")
        subprocess.run(['upx', '--best', str(exe_file)], check=True)
        
        new_size = exe_file.stat().st_size
        compression_ratio = (1 - new_size / original_size) * 100
        print(f"  ✅ UPX压缩完成，压缩率: {compression_ratio:.1f}%")
        print(f"  📊 最终大小: {new_size / 1024 / 1024:.2f} MB")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ⚠️ UPX不可用，跳过额外压缩")
    
    return True

def create_portable_package():
    """创建便携版包"""
    print("📦 创建便携版包...")
    
    dist_dir = Path('dist')
    exe_files = list(dist_dir.glob('TimeNest*'))
    
    if not exe_files:
        print("  ❌ 未找到可执行文件")
        return False
    
    exe_file = exe_files[0]
    
    # 创建便携版目录
    portable_dir = Path('TimeNest_Portable')
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制可执行文件
    shutil.copy2(exe_file, portable_dir / 'TimeNest.exe')
    
    # 创建配置文件
    config_content = """# TimeNest 便携版配置
# 此文件确保程序以便携模式运行
portable_mode=true
"""
    
    with open(portable_dir / 'portable.ini', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # 创建说明文件
    readme_content = """# TimeNest 便携版

## 使用说明
1. 双击 TimeNest.exe 启动程序
2. 程序会在当前目录创建配置文件
3. 可以将整个文件夹复制到其他位置使用

## 系统要求
- Windows 10/11 (64位)
- 无需安装Python或其他依赖

## 版本信息
- 构建时间: {build_time}
- 文件大小: {file_size:.2f} MB
"""
    
    import datetime
    build_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_size = exe_file.stat().st_size / 1024 / 1024
    
    with open(portable_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content.format(build_time=build_time, file_size=file_size))
    
    print(f"  ✅ 便携版创建完成: {portable_dir}")
    return True

def main():
    """主函数"""
    print("🚀 TimeNest 优化构建开始")
    print("=" * 50)
    
    # 检查PyInstaller
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller未安装，请运行: pip install pyinstaller")
        return False
    
    # 构建步骤
    steps = [
        ("清理构建目录", clean_build),
        ("优化导入", optimize_imports),
        ("PyInstaller构建", build_with_pyinstaller),
        ("构建后优化", post_build_optimization),
        ("创建便携版", create_portable_package),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"❌ {step_name}失败，构建中止")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 TimeNest 优化构建完成！")
    print("\n📁 输出文件:")
    print("  - dist/TimeNest.exe (单文件版)")
    print("  - TimeNest_Portable/ (便携版)")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
