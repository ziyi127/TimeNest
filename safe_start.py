#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 安全启动脚本
最小化功能，确保基本可用性
"""

import sys
import os
import logging
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_minimal_logging():
    """设置最小化日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def check_dependencies():
    """检查关键依赖"""
    print("🔍 检查依赖...")
    
    missing_deps = []
    
    try:
        import PyQt6
        print("   ✅ PyQt6 可用")
    except ImportError:
        missing_deps.append("PyQt6")
        print("   ❌ PyQt6 缺失")
    
    try:
        import yaml
        print("   ✅ PyYAML 可用")
    except ImportError:
        missing_deps.append("PyYAML")
        print("   ❌ PyYAML 缺失")
    
    if missing_deps:
        print(f"\n⚠️ 缺失依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def safe_main():
    """安全的主函数"""
    print("🆘 TimeNest 安全启动模式")
    print("=" * 50)
    
    setup_minimal_logging()
    logger = logging.getLogger(__name__)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    try:
        # 导入必要模块
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon
        
        print("✅ 基础模块导入成功")
        
        # 创建应用
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        print("✅ 应用创建成功")
        
        # 检查系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "错误", "系统托盘不可用！")
            return False
        
        print("✅ 系统托盘可用")
        
        # 尝试导入核心模块
        try:
            from core.config_manager import ConfigManager
            config_manager = ConfigManager()
            print("✅ 配置管理器创建成功")
        except Exception as e:
            print(f"⚠️ 配置管理器创建失败: {e}")
            config_manager = None
        
        # 尝试创建简单的托盘图标
        try:
            tray_icon = QSystemTrayIcon()
            
            # 设置图标（使用系统默认图标）
            tray_icon.setIcon(app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon))
            tray_icon.setToolTip("TimeNest - 安全模式")
            
            # 显示托盘图标
            tray_icon.show()
            
            print("✅ 托盘图标创建成功")
            
            # 显示成功消息
            tray_icon.showMessage(
                "TimeNest 安全模式",
                "应用已在安全模式下启动。基本功能可用。",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            
            print("\n" + "=" * 50)
            print("🎉 TimeNest 安全启动成功！")
            print("\n📋 当前状态:")
            print("   - 运行在安全模式")
            print("   - 托盘图标已显示")
            print("   - 基本功能可用")
            print("\n⚠️ 注意:")
            print("   - 增强功能已禁用")
            print("   - 如需完整功能，请修复依赖问题")
            print("   - 按 Ctrl+C 退出")
            
            # 运行应用
            return app.exec()
            
        except Exception as e:
            print(f"❌ 托盘图标创建失败: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("\n🔧 修复建议:")
        print("   1. 安装依赖: pip install PyQt6")
        print("   2. 检查Python版本")
        print("   3. 重启终端")
        return False
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = safe_main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，安全退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 严重错误: {e}")
        sys.exit(1)
