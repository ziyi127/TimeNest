#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
系统托盘图标类（前端专用）
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

# 导入GUI组件
from frontend.gui.management_window import ManagementWindow
from frontend.gui.temp_change_window import TempChangeWindow
from frontend.gui.settings_window import SettingsWindow


class FrontendSystemTrayIcon(QSystemTrayIcon):
    """前端应用系统托盘图标类"""
    
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__(app)
        self.app = app
        # 添加编辑模式标志
        self.edit_mode = False
        self.initUI()

    def initUI(self):
        # 设置托盘图标
        self.setIcon(QIcon.fromTheme("computer", QApplication.style().standardIcon(QStyle.SP_ComputerIcon)))
        
        # 创建右键菜单
        self.context_menu = QMenu()
        
        # 课表管理菜单项
        self.management_action = QAction("课表管理", self.app)
        self.management_action.triggered.connect(self.show_management_window)
        self.context_menu.addAction(self.management_action)
        
        # 临时调课菜单项
        self.temp_change_action = QAction("临时调课", self.app)
        self.temp_change_action.triggered.connect(self.show_temp_change_window)
        self.context_menu.addAction(self.temp_change_action)
        
        # 设置菜单项
        self.settings_action = QAction("设置", self.app)
        self.settings_action.triggered.connect(self.show_settings_window)
        self.context_menu.addAction(self.settings_action)
        
        # 编辑模式菜单项
        self.edit_mode_action = QAction("编辑模式", self.app)
        self.edit_mode_action.setCheckable(True)
        self.edit_mode_action.setChecked(self.edit_mode)
        self.edit_mode_action.triggered.connect(self.toggle_edit_mode)
        self.context_menu.addAction(self.edit_mode_action)
        
        # 分隔线
        self.context_menu.addSeparator()
        
        # 显示/隐藏菜单项
        self.show_action = QAction("显示悬浮窗", self.app)
        self.show_action.triggered.connect(self.show_floating_window)
        self.context_menu.addAction(self.show_action)
        
        self.hide_action = QAction("隐藏悬浮窗", self.app)
        self.hide_action.triggered.connect(self.hide_floating_window)
        self.context_menu.addAction(self.hide_action)
        
        # 分隔线
        self.context_menu.addSeparator()
        
        # 退出菜单项
        self.quit_action = QAction("退出", self.app)
        self.quit_action.triggered.connect(self.app.quit)
        self.context_menu.addAction(self.quit_action)
        
        # 设置上下文菜单
        self.setContextMenu(self.context_menu)
        
        # 连接激活信号
        self.activated.connect(self.on_activated)
        
        # 显示托盘图标
        self.show()

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 左键单击切换悬浮窗显示/隐藏
            if self.app.floating_window.isVisible():
                self.app.floating_window.hide()
            else:
                self.app.floating_window.show()
                self.app.floating_window.raise_()

    def show_management_window(self):
        """显示课表管理窗口"""
        if not hasattr(self, 'management_window'):
            self.management_window = ManagementWindow(self.app)
        self.management_window.show()
        self.management_window.raise_()
        self.management_window.activateWindow()

    def show_temp_change_window(self):
        """显示临时调课窗口"""
        if not hasattr(self, 'temp_change_window'):
            self.temp_change_window = TempChangeWindow(self.app)
        self.temp_change_window.show()
        self.temp_change_window.raise_()
        self.temp_change_window.activateWindow()
        # 更新原课程显示
        self.temp_change_window.update_original_course()

    def show_settings_window(self):
        """显示设置窗口"""
        if not hasattr(self, 'settings_window'):
            self.settings_window = SettingsWindow(self.app)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def toggle_edit_mode(self):
        """切换编辑模式"""
        self.edit_mode = not self.edit_mode
        self.edit_mode_action.setChecked(self.edit_mode)
        self.app.floating_window.set_edit_mode(self.edit_mode)
        
        # 根据编辑模式状态更新悬浮窗行为
        if self.edit_mode:
            # 编辑模式：显示悬浮窗并停止自动隐藏
            self.app.floating_window.show()
            self.app.floating_window.stop_fade_out()
        else:
            # 非编辑模式：恢复自动隐藏
            self.app.floating_window.hide_timer.start(self.app.settings.get("auto_hide_timeout", 5000))

    def show_floating_window(self):
        """显示悬浮窗"""
        self.app.floating_window.show()
        self.app.floating_window.raise_()

    def hide_floating_window(self):
        """隐藏悬浮窗"""
        self.app.floating_window.hide()