#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
系统托盘组件
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                               QHBoxLayout, QPushButton, QMenu,
                               QSystemTrayIcon, QMessageBox, QDialog, QFormLayout,
                               QLineEdit, QComboBox, QDateEdit, QTimeEdit,
                               QListWidget, QListWidgetItem, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFrame, QCheckBox)
from PySide6.QtCore import QDate, QEvent, Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QAction, QMouseEvent, QGuiApplication

# 导入GUI组件
from frontend.gui.management_window import ManagementWindow
from frontend.gui.temp_change_window import TempChangeWindow


# 系统托盘图标类
class SystemTrayIcon(QSystemTrayIcon):
    # 重写show方法以更新菜单文本
    def show(self):
        super().show()
        self.update_show_action_text()
        
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__(app)
        self.app = app

        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "logo.ico")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # 使用默认图标
            self.setIcon(self.style().standardIcon(QApplication.style().SP_ComputerIcon))

        # 设置提示文本
        self.setToolTip("TimeNest 课表软件")

        # 创建右键菜单
        self.create_menu()

        # 连接信号
        self.activated.connect(self.on_activated)

    def create_menu(self):
        """创建右键菜单"""
        menu = QMenu()

        # 显示/隐藏悬浮窗动作
        self.show_action = QAction("显示悬浮窗", self)
        self.show_action.triggered.connect(self.toggle_floating_window)
        # 更新动作文本
        self.update_show_action_text()

        # 课表管理动作
        manage_action = QAction("课表管理", self)
        manage_action.triggered.connect(self.show_management_window)

        # 临时调课动作
        temp_change_action = QAction("临时调课", self)
        temp_change_action.triggered.connect(self.show_temp_change_window)

        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.app.quit)

        # 添加动作到菜单
        menu.addAction(self.show_action)
        menu.addAction(manage_action)
        menu.addAction(temp_change_action)
        menu.addSeparator()
        menu.addAction(exit_action)

        self.setContextMenu(menu)

    def on_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.Trigger:
            # 左键点击，显示/隐藏悬浮窗
            self.toggle_floating_window()

    def toggle_floating_window(self):
        """切换悬浮窗显示/隐藏状态"""
        if self.app.floating_window.isVisible():
            self.app.floating_window.hide()
        else:
            self.app.floating_window.show()
            self.app.floating_window.raise_()
        # 更新动作文本
        self.update_show_action_text()

    def update_show_action_text(self):
        """根据悬浮窗状态更新动作文本"""
        if self.app.floating_window.isVisible():
            self.show_action.setText("关闭悬浮窗")
        else:
            self.show_action.setText("显示悬浮窗")

    def show_management_window(self):
        """显示课表管理窗口"""
        if not hasattr(self, 'management_window') or self.management_window.isHidden():
            self.management_window = ManagementWindow(self.app)
            self.management_window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
            self.management_window.setParent(None)
        self.management_window.show()
        self.management_window.raise_()

    def show_temp_change_window(self):
        """显示临时调课窗口"""
        if not hasattr(self, 'temp_change_window') or self.temp_change_window.isHidden():
            self.temp_change_window = TempChangeWindow(self.app)
            self.temp_change_window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
            self.temp_change_window.setParent(None)
        self.temp_change_window.show()
        self.temp_change_window.raise_()