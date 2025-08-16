#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
系统托盘图标类（前端专用）
"""

import os
from pathlib import Path

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

# 导入GUI组件
from frontend.gui.management_window import ManagementWindow
from frontend.gui.temp_change_window import TempChangeWindow


class FrontendSystemTrayIcon(QSystemTrayIcon):
    """前端应用系统托盘图标类"""
    
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__(app)
        self.app = app
        # 添加编辑模式标志
        self.edit_mode = False

        # 设置图标
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.resolve()
        icon_path = os.path.join(project_root, "res", "logo.ico")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # 使用默认图标
            self.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))

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

        # 编辑模式切换动作
        self.edit_mode_action = QAction("启用编辑模式", self)
        self.edit_mode_action.triggered.connect(self.toggle_edit_mode)

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
        menu.addAction(self.edit_mode_action)
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

    def toggle_edit_mode(self):
        """切换编辑模式"""
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.edit_mode_action.setText("禁用编辑模式")
            # 启用悬浮窗的拖动功能
            self.app.floating_window.set_edit_mode(True)
        else:
            self.edit_mode_action.setText("启用编辑模式")
            # 禁用悬浮窗的拖动功能
            self.app.floating_window.set_edit_mode(False)