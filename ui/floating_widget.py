#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 智能浮窗组件
"""

import logging
from typing import Optional
from functools import lru_cache

from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QScreen
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication

from ..core.app_manager import AppManager
from ..core.config_manager import ConfigManager
from ..core.theme_system import ThemeManager, Theme


class FloatingModule(QWidget):
    """
    浮窗信息模块基类。

    Args:
        app_manager (AppManager): 主应用管理器实例。
        parent (QWidget, optional): 父组件. Defaults to None.
    """

    def __init__(self, app_manager: AppManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def update_content(self):
        """子类需要实现此方法来更新显示内容"""
        raise NotImplementedError

    def apply_theme(self, theme: Theme, config: dict):
        """子类需要实现此方法来应用主题和配置"""
        font = self.font()
        font.setPointSize(config.get('font_size', 12))
        self.setFont(font)
        self.setStyleSheet(f"color: {theme.colors.text_primary}; background-color: transparent;")


class TimeModule(FloatingModule):
    """时间模块"""

    def __init__(self, app_manager: AppManager, parent: Optional[QWidget] = None):
        super().__init__(app_manager, parent)
        self.label = QLabel("00:00", self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_content)
        self.timer.start(1000)
        self.update_content()

    def update_content(self):
        """更新时间显示"""
        current_time = self.app_manager.time_manager.get_current_time()
        self.label.setText(current_time.strftime("%H:%M"))

    def apply_theme(self, theme: Theme, config: dict):
        """应用主题"""
        super().apply_theme(theme, config)
        self.label.setFont(self.font())
        self.label.setStyleSheet(f"color: {theme.colors.text_primary}; background-color: transparent;")


class FloatingWidget(QWidget):
    """主浮窗类"""

    def __init__(self, app_manager: AppManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.FloatingWidget')
        self.app_manager = app_manager
        self.config_manager = app_manager.config_manager
        self.theme_manager = app_manager.theme_manager

        self.drag_position: Optional[QPoint] = None
        self.modules: dict[str, FloatingModule] = {}

        self._init_ui()
        self.update_from_config()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

    def update_from_config(self):
        """从配置更新浮窗"""
        config = self.config_manager.get_config('floating_widget', {})
        self.setFixedSize(config.get('width', 400), config.get('height', 60))
        self.setWindowOpacity(1.0)  # Opacity is handled in paintEvent for the background

        mouse_through = config.get('mouse_through', False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, mouse_through)

        self.reposition()
        self.apply_theme()
        self.update_modules(config.get('modules', ['time']))
        self.update()

    def update_modules(self, module_names: list[str]):
        """更新显示的模块"""
        # A simple implementation that clears and re-adds modules
        # A more advanced version could reuse existing modules
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.modules.clear()

        module_map = {
            'time': TimeModule,
            # 'schedule': ScheduleModule, # Example for future
            # 'weather': WeatherModule,   # Example for future
        }

        for name in module_names:
            if name in module_map:
                try:
                    module_class = module_map[name]
                    module_instance = module_class(self.app_manager, self)
                    self.main_layout.addWidget(module_instance)
                    self.modules[name] = module_instance
                except Exception as e:
                    self.logger.error(f"创建模块 '{name}' 失败: {e}", exc_info=True)

        self.apply_theme()

    def apply_theme(self):
        """应用当前主题"""
        theme = self.theme_manager.get_current_theme()
        config = self.config_manager.get_config('floating_widget', {})
        if not theme:
            return

        for module in self.modules.values():
            module.apply_theme(theme, config)

        self.update()  # Trigger repaint

    def reposition(self):
        """重新定位窗口到屏幕顶部中央"""
        try:
            screen = QApplication.primaryScreen()
            if not screen:
                return
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = 10  # top: 10px
            self.move(screen_geometry.x() + x, screen_geometry.y() + y)
        except Exception as e:
            self.logger.error(f"浮窗定位失败: {e}", exc_info=True)

    def show_animated(self):
        """带动画显示"""
        self.setWindowOpacity(0.0)
        self.show()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def hide_animated(self):
        """带动画隐藏"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.windowOpacity())
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self.hide)
        self.animation.start()

    @lru_cache(maxsize=8)
    def _get_cached_paint_data(self, theme_id: str, opacity: float, border_radius: int):
        """缓存绘制数据"""
        theme = self.theme_manager.get_current_theme()
        if not theme:
            return None
        bg_color = QColor(theme.colors.surface)
        bg_color.setAlphaF(opacity)
        return bg_color, border_radius

    def paintEvent(self, event):
        """绘制事件，用于绘制圆角背景和阴影（优化版本）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        config = self.config_manager.get_config('floating_widget', {})
        theme = self.theme_manager.get_current_theme()
        if not theme:
            return

        opacity = config.get('opacity', 0.85)
        border_radius = config.get('border_radius', 30)

        # 使用缓存的绘制数据
        paint_data = self._get_cached_paint_data(theme.metadata.id, opacity, border_radius)
        if not paint_data:
            return

        bg_color, cached_radius = paint_data

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(self.rect(), cached_radius, cached_radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def load_config(self):
        """重新加载配置"""
        try:
            self.update_from_config()
            self.logger.info("浮窗配置已重新加载")
        except Exception as e:
            self.logger.error(f"重新加载浮窗配置失败: {e}")

    def apply_config(self):
        """应用配置更改"""
        try:
            config = self.config_manager.get_config('floating_widget', {})

            # 应用尺寸
            width = config.get('width', 400)
            height = config.get('height', 60)
            self.setFixedSize(width, height)

            # 应用透明度
            opacity = config.get('opacity', 0.85)
            self.setWindowOpacity(1.0)  # 透明度在paintEvent中处理

            # 应用位置
            self.reposition()

            # 应用鼠标穿透
            mouse_through = config.get('mouse_through', False)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, mouse_through)

            # 应用置顶设置
            always_on_top = config.get('always_on_top', True)
            self.set_always_on_top(always_on_top)

            # 更新模块
            modules = config.get('modules', ['time'])
            self.update_modules(modules)

            # 应用主题
            self.apply_theme()

            # 强制重绘
            self.update()

            self.logger.info("浮窗配置已应用")

        except Exception as e:
            self.logger.error(f"应用浮窗配置失败: {e}")

    def set_always_on_top(self, always_on_top: bool):
        """设置是否总是置顶"""
        try:
            flags = self.windowFlags()
            if always_on_top:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowType.WindowStaysOnTopHint

            # 保存当前状态
            was_visible = self.isVisible()

            # 应用新的窗口标志
            self.setWindowFlags(flags)

            # 恢复可见状态
            if was_visible:
                self.show()

        except Exception as e:
            self.logger.error(f"设置置顶状态失败: {e}")

    def contextMenuEvent(self, event):
        """右键菜单事件"""
        try:
            from PyQt6.QtWidgets import QMenu

            menu = QMenu(self)

            # 添加设置选项
            settings_action = menu.addAction("🎈 浮窗设置")
            settings_action.triggered.connect(self.show_settings)

            menu.addSeparator()

            # 添加隐藏选项
            hide_action = menu.addAction("🙈 隐藏浮窗")
            hide_action.triggered.connect(self.hide_animated)

            # 显示菜单
            menu.exec(event.globalPos())

        except Exception as e:
            self.logger.error(f"显示右键菜单失败: {e}")

    def show_settings(self):
        """显示设置对话框"""
        try:
            # 通过应用管理器获取浮窗管理器并显示设置
            if hasattr(self.app_manager, 'floating_manager') and self.app_manager.floating_manager:
                self.app_manager.floating_manager.show_settings_dialog()
            else:
                self.logger.warning("浮窗管理器不可用")

        except Exception as e:
            self.logger.error(f"显示浮窗设置失败: {e}")