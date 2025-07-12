#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 系统修复脚本
清理问题文件，恢复稳定状态
"""

import os
import sys
import shutil
from pathlib import Path

def clean_problematic_files():
    """清理可能导致问题的文件"""
    print("🧹 清理问题文件...")
    
    # 要删除的问题文件列表
    problematic_files = [
        "core/environment_optimizer.py",
        "core/study_planner.py", 
        "core/resource_manager.py",
        "core/schedule_enhancements.py",
        "core/notification_enhancements.py",
        "core/study_assistant.py",
        "test_additional_enhancements.py",
        "test_new_enhancements.py",
        "test_tray_fixes.py"
    ]
    
    removed_count = 0
    
    for file_path in problematic_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   ✅ 已删除: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ 删除失败 {file_path}: {e}")
        else:
            print(f"   ℹ️ 文件不存在: {file_path}")
    
    print(f"\n📊 清理完成，删除了 {removed_count} 个问题文件")

def clean_cache_files():
    """清理缓存文件"""
    print("\n🗑️ 清理缓存文件...")
    
    cache_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache"
    ]
    
    removed_count = 0
    
    # 递归删除 __pycache__ 目录
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:  # 使用切片复制避免修改正在迭代的列表
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   ✅ 已删除缓存目录: {cache_path}")
                    dirs.remove(dir_name)  # 从迭代中移除
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ 删除缓存失败 {cache_path}: {e}")
    
    # 删除 .pyc 文件
    for root, dirs, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                    print(f"   ✅ 已删除缓存文件: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ 删除缓存文件失败 {file_path}: {e}")
    
    print(f"\n📊 缓存清理完成，删除了 {removed_count} 个缓存文件")

def check_core_files():
    """检查核心文件完整性"""
    print("\n🔍 检查核心文件...")
    
    core_files = [
        "main.py",
        "core/app_manager.py",
        "core/config_manager.py", 
        "core/theme_system.py",
        "core/floating_manager.py",
        "core/notification_manager.py",
        "ui/system_tray.py",
        "ui/tray_features.py",
        "ui/floating_widget.py"
    ]
    
    missing_files = []
    
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ 缺失: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ 发现 {len(missing_files)} 个缺失的核心文件")
        print("建议从备份或Git历史恢复这些文件")
        return False
    else:
        print("\n✅ 所有核心文件完整")
        return True

def reset_config():
    """重置配置文件"""
    print("\n⚙️ 重置配置...")
    
    config_files = [
        "config.yaml",
        "user_config.yaml",
        ".timenest_config"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            backup_name = f"{config_file}.backup"
            try:
                shutil.copy2(config_file, backup_name)
                print(f"   ✅ 已备份配置: {config_file} -> {backup_name}")
            except Exception as e:
                print(f"   ⚠️ 备份配置失败 {config_file}: {e}")

def create_minimal_main():
    """创建最小化的main.py备份"""
    print("\n📝 创建安全启动备份...")
    
    minimal_main = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 最小化启动脚本
紧急恢复版本
"""

import sys
import logging
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """最小化主函数"""
    try:
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox
        from PyQt6.QtCore import Qt
        
        app = QApplication(sys.argv)
        
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "错误", "系统托盘不可用")
            return 1
        
        # 创建简单托盘图标
        tray = QSystemTrayIcon()
        tray.setIcon(app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon))
        tray.setToolTip("TimeNest - 紧急模式")
        tray.show()
        
        tray.showMessage("TimeNest", "紧急模式启动成功", QSystemTrayIcon.MessageIcon.Information)
        
        return app.exec()
        
    except Exception as e:
        print(f"启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    try:
        with open("main_emergency.py", "w", encoding="utf-8") as f:
            f.write(minimal_main)
        print("   ✅ 已创建紧急启动脚本: main_emergency.py")
    except Exception as e:
        print(f"   ❌ 创建紧急脚本失败: {e}")

def main():
    """主修复函数"""
    print("🆘 TimeNest 系统修复工具")
    print("=" * 50)
    
    # 1. 清理问题文件
    clean_problematic_files()
    
    # 2. 清理缓存
    clean_cache_files()
    
    # 3. 检查核心文件
    core_ok = check_core_files()
    
    # 4. 重置配置
    reset_config()
    
    # 5. 创建紧急启动脚本
    create_minimal_main()
    
    print("\n" + "=" * 50)
    print("🔧 修复完成！")
    
    print("\n📋 下一步操作:")
    if core_ok:
        print("   1. 尝试运行: python safe_start.py")
        print("   2. 如果失败，运行: python main_emergency.py")
        print("   3. 重新安装依赖: pip install -r requirements.txt")
    else:
        print("   1. 从Git恢复缺失文件: git checkout HEAD -- <missing_file>")
        print("   2. 或者重新克隆项目")
    
    print("   4. 重启系统清理内存")
    print("   5. 避免使用复杂功能，只用基本课程表")

if __name__ == "__main__":
    main()
