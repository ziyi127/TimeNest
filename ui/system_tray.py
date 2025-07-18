#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 系统托盘管理
"""

import logging
import os
from typing import Optional
from functools import lru_cache

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

# 导入错误处理
from core.error_handler import error_handler, safe_call_method, safe_getattr
from core.safe_logger import get_cached_safe_logger


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
    show_window_requested = Signal()

    # 浮窗控制信号
    toggle_floating_widget_requested = Signal()
    floating_settings_requested = Signal()

    # 核心模块信号
    schedule_module_requested = Signal()
    settings_module_requested = Signal()
    plugins_module_requested = Signal()

    # 快捷功能信号
    time_calibration_requested = Signal()

    # 应用控制信号
    about_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent: Optional[QObject] = None, floating_manager=None):
        super().__init__(parent)
        self.logger = get_cached_safe_logger(f'{__name__}.SystemTray')
        self.tray_icon: Optional[QSystemTrayIcon] = None

        # 支持浮窗管理器参数（向后兼容）
        self.floating_manager = floating_manager


        if QSystemTrayIcon.isSystemTrayAvailable():
            self._init_tray()
        else:
            self.logger.warning("系统托盘不可用。")

    def _init_tray(self):
        """初始化托盘图标和菜单"""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            
            # 设置托盘图标 - 优先使用PNG格式
            icon_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_32x32.png'),
                os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_24x24.png'),
                os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_16x16.png'),
                os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.png'),
                os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon.png')
            ]

            icon_set = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.tray_icon.setIcon(QIcon(icon_path))
                    self.logger.debug(f"使用托盘图标: {os.path.basename(icon_path)}")
                    icon_set = True
                    break

            if not icon_set:
                self.tray_icon.setIcon(QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))
                self.logger.warning("使用系统默认托盘图标")
                self.logger.debug("使用默认托盘图标")

            self.tray_icon.setToolTip("TimeNest")
            
            # 创建简化菜单
            try:
                menu = QMenu()

                # 只保留退出按钮
                quit_action = QAction("❌ 退出 TimeNest", self)
                quit_action.triggered.connect(self.quit_requested)
                menu.addAction(quit_action)

                # 确保菜单可以正常工作
                menu.setEnabled(True)

                self.tray_icon.setContextMenu(menu)
                self.tray_icon.activated.connect(self.on_activated)
                self.tray_icon.show()
                self.logger.info("系统托盘初始化完成。")
                
            except Exception as e:
                self.logger.error(f"创建托盘菜单失败: {e}")
                # 即使菜单创建失败，也要显示基本的托盘图标
                if self.tray_icon:
                    self.tray_icon.show()
                raise
                
        except Exception as e:
            self.logger.error(f"初始化托盘失败: {e}")
            raise

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """托盘图标激活事件（优化版本）"""
        # 单击和双击都进入设置页面
        if reason in [QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick]:
            self.settings_module_requested.emit()

    def update_floating_widget_action(self, is_visible: bool):
        """更新浮窗菜单项的状态"""
        if self.tray_icon:
            self.toggle_floater_action.setChecked(is_visible)
            self.toggle_floater_action.setText("隐藏浮窗" if is_visible else "显示浮窗")

    def update_floating_status(self, is_visible: bool):
        """更新浮窗状态（兼容方法）"""
        try:
            self.update_floating_widget_action(is_visible)
            self.logger.debug(f"浮窗状态已更新: {is_visible}")
        except Exception as e:
            self.logger.error(f"更新浮窗状态失败: {e}")

    def show_message(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information, timeout: int = 5000):
        """显示系统托盘消息"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)
            self.logger.debug(f"显示托盘消息: {title} - {message}")

    def set_icon(self, icon_path: str):
        """设置托盘图标"""
        if self.tray_icon and os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
            self.logger.debug(f"设置托盘图标: {icon_path}")

    def set_tooltip(self, tooltip: str):
        """设置托盘提示文本"""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)

    def is_visible(self) -> bool:
        """检查托盘图标是否可见"""
        return self.tray_icon is not None and self.tray_icon.isVisible()

    def is_available(self) -> bool:
        """检查系统托盘是否可用"""
        return QSystemTrayIcon.isSystemTrayAvailable()

    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.logger.debug("托盘图标已隐藏")

    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            self.logger.debug("托盘图标已显示")

    def cleanup(self):
        """清理资源"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
            self.logger.info("系统托盘已清理")


# 向后兼容的别名 - 统一使用 SystemTray 类
SystemTrayManager = SystemTray


class SystemTrayManagerLegacy(QObject):
    """
    系统托盘管理器 - 完整版本

    提供完整的系统托盘功能，包括状态管理、消息通知、动态菜单等
    """

    # 浮窗控制信号
    floating_toggled = Signal(bool)  # 浮窗显示/隐藏
    floating_settings_requested = Signal()

    # 模块功能信号
    schedule_module_requested = Signal()
    settings_module_requested = Signal()
    plugins_module_requested = Signal()
    time_calibration_requested = Signal()

    # 应用控制信号
    about_requested = Signal()
    quit_requested = Signal()

    def __init__(self, floating_manager=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.SystemTrayManager')

        # 组件引用
        self.floating_manager = floating_manager

        # 状态管理
        self.floating_visible = True

        # 托盘组件
        self.tray_icon = None
        self.context_menu = None

        # 动态菜单项
        self.toggle_floating_action = None

        # 初始化
        self._init_tray_system()

    def _init_tray_system(self):
        """初始化托盘系统"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("系统托盘不可用")
            return False

        try:
            self._create_tray_icon()
            self._create_context_menu()
            self._setup_connections()

            self.tray_icon.show()
            self.logger.info("系统托盘管理器初始化完成")
            return True

        except Exception as e:
            self.logger.error(f"托盘系统初始化失败: {e}")
            return False

    def _create_tray_icon(self):
        """创建托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)

        # 设置图标
        icon_path = self._get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 使用系统默认图标
            style = QApplication.style()
            icon = style.standardIcon(style.StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)

        # 设置提示文本
        self.tray_icon.setToolTip("TimeNest - 智能时间管理助手")

    @lru_cache(maxsize=1)
    def _get_icon_path(self):
        """获取图标路径（缓存）"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_32x32.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_24x24.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_16x16.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'tray_icon.png'),
            os.path.join(os.path.dirname(__file__), '..', 'icons', 'tray_icon.png'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = QMenu()

        # 只保留退出按钮
        quit_action = QAction("❌ 退出 TimeNest", self)
        quit_action.triggered.connect(self.quit_requested)
        self.context_menu.addAction(quit_action)

        # 设置菜单
        self.tray_icon.setContextMenu(self.context_menu)

    def _setup_connections(self):
        """设置信号连接"""
        if self.tray_icon:
            self.tray_icon.activated.connect(self._on_tray_activated)
            self.tray_icon.messageClicked.connect(self._on_message_clicked)

    def _on_tray_activated(self, reason):
        """托盘图标激活事件"""
        # 单击和双击都进入设置页面
        if reason in [QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick]:
            self.settings_module_requested.emit()

    def _on_message_clicked(self):
        """托盘消息点击事件"""
        # 点击消息时切换浮窗
        self._toggle_floating()

    def _toggle_floating(self):
        """切换浮窗显示状态"""
        # 发送切换信号，不传递状态参数
        self.floating_toggled.emit(True)  # 参数不重要，只是触发切换

    def _update_floating_menu_text(self):
        """更新浮窗菜单文本"""
        if self.toggle_floating_action:
            text = "🔄 隐藏浮窗" if self.floating_visible else "🔄 显示浮窗"
            self.toggle_floating_action.setText(text)
            self.toggle_floating_action.setChecked(self.floating_visible)

    # 公共接口方法
    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            self.logger.debug("托盘图标已显示")

    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.logger.debug("托盘图标已隐藏")

    def is_available(self):
        """检查系统托盘是否可用"""
        return QSystemTrayIcon.isSystemTrayAvailable()

    def is_visible(self):
        """检查托盘图标是否可见"""
        return self.tray_icon is not None and self.tray_icon.isVisible()

    def show_message(self, title: str, message: str,
                    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                    timeout: int = 5000):
        """显示托盘消息"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)
            self.logger.debug(f"显示托盘消息: {title} - {message}")

    def update_floating_status(self, is_visible: bool):
        """更新浮窗状态"""
        self.floating_visible = is_visible
        self._update_floating_menu_text()
        self.logger.debug(f"浮窗状态更新: {is_visible}")

    def set_tooltip(self, tooltip: str):
        """设置托盘提示文本"""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)

    def set_icon(self, icon_path: str):
        """设置托盘图标"""
        if self.tray_icon and os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
            self.logger.debug(f"设置托盘图标: {icon_path}")

    def add_custom_action(self, text: str, callback, icon=None, separator_before=False):
        """添加自定义菜单项"""
        if not self.context_menu:
            return None


        if separator_before:
            self.context_menu.addSeparator()

        action = QAction(text, self)
        if icon:
            action.setIcon(icon)
        action.triggered.connect(callback)

        # 在退出按钮之前插入
        actions = self.context_menu.actions()
        if actions:
            self.context_menu.insertAction(actions[-2], action)  # -2 是分隔符，-1 是退出
        else:
            self.context_menu.addAction(action)

        return action

    def remove_custom_action(self, action):
        """移除自定义菜单项"""
        if self.context_menu and action:
            self.context_menu.removeAction(action)

    def cleanup(self):
        """清理资源"""
        try:
            if self.tray_icon:
                self.tray_icon.hide()
                self.tray_icon.deleteLater()
                self.tray_icon = None


            if self.context_menu:
                self.context_menu.deleteLater()

                self.context_menu.deleteLater()
                self.context_menu = None

            self.logger.info("系统托盘管理器已清理")

        except Exception as e:
            self.logger.error(f"托盘清理失败: {e}")


# 向后兼容的别名
SystemTrayIcon = SystemTray
SystemTrayManager = SystemTrayManagerLegacy