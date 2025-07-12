#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 智能浮窗组件
"""

import logging
from typing import Optional
from functools import lru_cache

from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QScreen
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QApplication

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
        
        # 创建时间和日期标签
        self.time_label = QLabel("00:00", self)
        self.date_label = QLabel("", self)
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(2)
        
        # 时间标签设置
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)

        # 定时器设置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_content)
        self.timer.start(1000)
        self.update_content()

    def update_content(self):
        """更新时间显示"""
        current_time = self.app_manager.time_manager.get_current_time()
        
        # 获取配置
        config = self.app_manager.config_manager.get_config('floating_widget', {})
        time_format = config.get('time_format', '24h')
        show_seconds = config.get('show_seconds', False)
        show_date = config.get('show_date', True)
        
        # 格式化时间
        if time_format == '12h':
            time_str = current_time.strftime("%I:%M")
            if show_seconds:
                time_str = current_time.strftime("%I:%M:%S")
            time_str += current_time.strftime(" %p")
        else:
            time_str = current_time.strftime("%H:%M")
            if show_seconds:
                time_str = current_time.strftime("%H:%M:%S")
        
        self.time_label.setText(time_str)
        
        # 更新日期
        if show_date:
            date_str = current_time.strftime("%Y年%m月%d日 %A")
            self.date_label.setText(date_str)
            self.date_label.show()
        else:
            self.date_label.hide()

    def apply_theme(self, theme: Theme, config: dict):
        """应用主题"""
        super().apply_theme(theme, config)
        
        # 设置字体
        time_font = self.font()
        time_font.setPointSize(16)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        
        date_font = self.font()
        date_font.setPointSize(10)
        self.date_label.setFont(date_font)
        
        # 设置样式
        time_style = f"color: {theme.colors.text_primary}; background-color: transparent;"
        date_style = f"color: {theme.colors.text_secondary}; background-color: transparent;"
        
        self.time_label.setStyleSheet(time_style)
        self.date_label.setStyleSheet(date_style)


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
        self.auto_hide = False
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self._auto_hide)
        self.is_mouse_over = False

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
        config = self.config_manager.get_config('floating_widget', {
            'width': 450,
            'height': 70,
            'opacity': 0.9,
            'border_radius': 35,
            'modules': ['time'],
            'mouse_through': False,
            'auto_hide': False,
            'animation_duration': 300
        })
        
        # 设置窗口大小和透明度
        self.setFixedSize(config.get('width', 450), config.get('height', 70))
        self.setWindowOpacity(1.0)  # 透明度在paintEvent中处理

        # 鼠标穿透设置
        mouse_through = config.get('mouse_through', False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, mouse_through)

        # 自动隐藏功能
        self.auto_hide = config.get('auto_hide', False)
        if self.auto_hide:
            self._setup_auto_hide()

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
        config = self.config_manager.get_config('floating_widget', {})
        duration = config.get('animation_duration', 300)
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.windowOpacity())
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self.hide)
        self.animation.start()

    def _setup_auto_hide(self):
        """设置自动隐藏功能"""
        self.setMouseTracking(True)
        for module in self.modules.values():
            module.setMouseTracking(True)

    def _auto_hide(self):
        """自动隐藏浮窗"""
        if not self.is_mouse_over:
            self.hide_animated()

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_mouse_over = True
        if self.auto_hide:
            self.auto_hide_timer.stop()
            if not self.isVisible():
                self.show_animated()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_mouse_over = False
        if self.auto_hide:
            self.auto_hide_timer.start(2000)  # 2秒后自动隐藏
        super().leaveEvent(event)

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
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        config = self.config_manager.get_config('floating_widget', {})
        theme = self.theme_manager.get_current_theme()
        if not theme:
            return

        opacity = config.get('opacity', 0.9)
        border_radius = config.get('border_radius', 35)
        shadow_enabled = config.get('shadow_enabled', True)
        
        rect = self.rect()
        
        # 绘制阴影
        if shadow_enabled:
            shadow_offset = 3
            shadow_blur = 8
            shadow_color = QColor(0, 0, 0, 60)
            
            shadow_rect = rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(shadow_rect, border_radius, border_radius)

        # 使用缓存的绘制数据
        paint_data = self._get_cached_paint_data(theme.metadata.id, opacity, border_radius)
        if not paint_data:
            return

        bg_color, cached_radius = paint_data

        # 绘制主背景
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, cached_radius, cached_radius)
        
        # 绘制边框（可选）
        border_enabled = config.get('border_enabled', False)
        if border_enabled:
            border_color = QColor(theme.colors.text_primary)
            border_color.setAlphaF(0.3)
            painter.setPen(QPen(border_color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), cached_radius-1, cached_radius-1)

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