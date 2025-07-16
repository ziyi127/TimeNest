#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 最小化构建脚本
快速创建最小体积的可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("🚀 TimeNest 最小化构建")
    print("=" * 40)
    
    # 清理旧的构建文件
    print("🧹 清理构建目录...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✅ 已删除 {dir_name}")
    
    # 检查PyInstaller
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"📦 PyInstaller版本: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller未安装，请运行: pip install pyinstaller")
        return False
    
    # 使用最小化配置构建
    print("🔨 开始最小化构建...")
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'TimeNest_minimal.spec'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 构建完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    
    # 检查输出文件
    dist_dir = Path('dist')
    exe_files = list(dist_dir.glob('TimeNest*'))
    
    if exe_files:
        exe_file = exe_files[0]
        size_mb = exe_file.stat().st_size / 1024 / 1024
        print(f"📊 文件大小: {size_mb:.2f} MB")
        print(f"📁 输出位置: {exe_file}")
        
        # 如果有UPX，尝试进一步压缩
        try:
            subprocess.run(['upx', '--version'], check=True, capture_output=True)
            print("🗜️ 使用UPX进一步压缩...")
            subprocess.run(['upx', '--best', str(exe_file)], check=True)
            
            new_size_mb = exe_file.stat().st_size / 1024 / 1024
            compression_ratio = (1 - new_size_mb / size_mb) * 100
            print(f"✅ UPX压缩完成")
            print(f"📊 最终大小: {new_size_mb:.2f} MB (压缩率: {compression_ratio:.1f}%)")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ UPX不可用，跳过额外压缩")
        
        return True
    else:
        print("❌ 未找到输出文件")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 最小化构建完成！")
        print("💡 提示: 如果需要更小的体积，可以:")
        print("   1. 安装UPX压缩工具")
        print("   2. 移除不必要的QML文件")
        print("   3. 优化图标文件大小")
    else:
        print("\n❌ 构建失败")
    
    sys.exit(0 if success else 1)
