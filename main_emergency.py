#!/usr/bin/env python3
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
