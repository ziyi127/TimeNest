#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
前端应用入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

# 导入GUI组件
from frontend.gui.floating_window import FloatingWindow
from frontend.gui.system_tray import SystemTrayIcon

# 设置中文字体支持
font = QFont()
font.setFamily("SimHei")


class TimeNestFrontendApp(QApplication):
    def __init__(self, args: list[str]):
        super().__init__(args)
        self.setApplicationName("TimeNest")
        self.setApplicationVersion("1.0.0")
        self.setStyle("Fusion")

        # 创建悬浮窗
        self.floating_window = FloatingWindow(self)
        self.floating_window.show()

        # 创建系统托盘图标
        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()


def main():
    """前端应用程序主入口点"""
    app = TimeNestFrontendApp(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()