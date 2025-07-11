#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 系统托盘管理
"""

import logging
import os
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


class SystemTray(QObject):
    """
    系统托盘管理类。

    Signals:
        show_window_requested: 请求显示主窗口。
        toggle_floating_widget_requested: 请求切换浮窗显示状态。
        settings_requested: 请求打开设置。
        quit_requested: 请求退出应用。
    """
    # 窗口控制信号
    show_window_requested = pyqtSignal()

    # 浮窗控制信号
    toggle_floating_widget_requested = pyqtSignal()
    floating_settings_requested = pyqtSignal()

    # 核心模块信号
    schedule_module_requested = pyqtSignal()
    settings_module_requested = pyqtSignal()
    plugins_module_requested = pyqtSignal()

    # 快捷功能信号
    time_calibration_requested = pyqtSignal()

    # 应用控制信号
    quit_requested = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.SystemTray')
        self.tray_icon: Optional[QSystemTrayIcon] = None

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._init_tray()
        else:
            self.logger.warning("系统托盘不可用。")

    def _init_tray(self):
        """初始化托盘图标和菜单"""
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))

        self.tray_icon.setToolTip("TimeNest")

        # 创建菜单
        menu = QMenu()

        # 浮窗控制区域
        self.toggle_floater_action = QAction("隐藏浮窗", self)
        self.toggle_floater_action.setCheckable(True)
        self.toggle_floater_action.setChecked(True)  # 默认显示
        self.toggle_floater_action.triggered.connect(self.toggle_floating_widget_requested)
        menu.addAction(self.toggle_floater_action)

        floating_settings_action = QAction("⚙️ 浮窗设置", self)
        floating_settings_action.triggered.connect(self.floating_settings_requested)
        menu.addAction(floating_settings_action)

        menu.addSeparator()

        # 核心功能模块区域
        module_label = QAction("📋 核心功能", self)
        module_label.setEnabled(False)  # 作为标题，不可点击
        menu.addAction(module_label)

        schedule_action = QAction("📅 课程表管理", self)
        schedule_action.triggered.connect(self.schedule_module_requested)
        menu.addAction(schedule_action)

        settings_action = QAction("🔧 应用设置", self)
        settings_action.triggered.connect(self.settings_module_requested)
        menu.addAction(settings_action)

        plugins_action = QAction("🔌 插件市场", self)
        plugins_action.triggered.connect(self.plugins_module_requested)
        menu.addAction(plugins_action)

        menu.addSeparator()

        # 快捷工具区域
        tools_label = QAction("🛠️ 快捷工具", self)
        tools_label.setEnabled(False)  # 作为标题，不可点击
        menu.addAction(tools_label)

        calibration_action = QAction("⏰ 时间校准", self)
        calibration_action.triggered.connect(self.time_calibration_requested)
        menu.addAction(calibration_action)

        menu.addSeparator()

        # 应用控制区域
        quit_action = QAction("❌ 退出 TimeNest", self)
        quit_action.triggered.connect(self.quit_requested)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_activated)
        self.tray_icon.show()
        self.logger.info("系统托盘初始化完成。")

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()

    def update_floating_widget_action(self, is_visible: bool):
        """更新浮窗菜单项的状态"""
        if self.tray_icon:
            self.toggle_floater_action.setChecked(is_visible)
            self.toggle_floater_action.setText("隐藏浮窗" if is_visible else "显示浮窗")