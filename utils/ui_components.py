#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI components and widget utilities for TimeNest
Provides safe UI component creation and management
"""

import logging
from typing import Optional, Dict, Any, List, Callable

from utils.common_imports import QObject, Signal

try:
    from PySide6.QtWidgets import (
        QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
        QFrame, QScrollArea, QTextEdit, QLineEdit, QComboBox,
        QCheckBox, QSlider, QProgressBar, QTabWidget, QSplitter
    )
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
    QT_WIDGETS_AVAILABLE = True
except ImportError:
    logging.error("PySide6 widgets not available")
    QT_WIDGETS_AVAILABLE = False
    
    class QWidget:
        def __init__(self, *args, **kwargs):
            pass
        def setLayout(self, layout):
            pass
        def show(self):
            pass
        def hide(self):
            pass
    
    QLabel = QPushButton = QFrame = QScrollArea = QWidget
    QTextEdit = QLineEdit = QComboBox = QCheckBox = QWidget
    QSlider = QProgressBar = QTabWidget = QSplitter = QWidget
    QVBoxLayout = QHBoxLayout = QWidget
    
    class Qt:
        class AlignmentFlag:
            AlignCenter = None
            AlignLeft = None
            AlignRight = None
    
    class QFont:
        def __init__(self, *args, **kwargs):
            pass
    
    class QIcon:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)

class SafeWidget:
    """Safe widget wrapper with fallback behavior"""
    
    def __init__(self, widget_class, *args, **kwargs):
        self.widget_class = widget_class
        self.widget = None
        self.available = QT_WIDGETS_AVAILABLE
        
        if self.available:
            try:
                self.widget = widget_class(*args, **kwargs)
            except Exception as e:
                logger.error(f"Failed to create widget {widget_class.__name__}: {e}")
                self.available = False
    
    def __getattr__(self, name):
        if self.available and self.widget:
            return getattr(self.widget, name)
        else:
            return lambda *args, **kwargs: None
    
    def __bool__(self):
        return self.available and self.widget is not None

class UIComponentFactory:
    """Factory for creating UI components safely"""
    
    @staticmethod
    def create_label(text: str = "", parent=None) -> SafeWidget:
        """Create a safe label widget"""
        widget = SafeWidget(QLabel, text, parent)
        return widget
    
    @staticmethod
    def create_button(text: str = "", parent=None, callback: Optional[Callable] = None) -> SafeWidget:
        """Create a safe button widget"""
        widget = SafeWidget(QPushButton, text, parent)
        if widget.available and callback:
            try:
                widget.clicked.connect(callback)
            except Exception as e:
                logger.error(f"Failed to connect button callback: {e}")
        return widget
    
    @staticmethod
    def create_layout(layout_type: str = "vertical") -> SafeWidget:
        """Create a safe layout"""
        layout_class = QVBoxLayout if layout_type == "vertical" else QHBoxLayout
        return SafeWidget(layout_class)
    
    @staticmethod
    def create_text_edit(parent=None, placeholder: str = "") -> SafeWidget:
        """Create a safe text edit widget"""
        widget = SafeWidget(QTextEdit, parent)
        if widget.available and placeholder:
            try:
                widget.setPlaceholderText(placeholder)
            except Exception as e:
                logger.debug(f"Failed to set placeholder: {e}")
        return widget
    
    @staticmethod
    def create_line_edit(parent=None, placeholder: str = "") -> SafeWidget:
        """Create a safe line edit widget"""
        widget = SafeWidget(QLineEdit, parent)
        if widget.available and placeholder:
            try:
                widget.setPlaceholderText(placeholder)
            except Exception as e:
                logger.debug(f"Failed to set placeholder: {e}")
        return widget
    
    @staticmethod
    def create_combo_box(parent=None, items: Optional[List[str]] = None) -> SafeWidget:
        """Create a safe combo box widget"""
        widget = SafeWidget(QComboBox, parent)
        if widget.available and items:
            try:
                widget.addItems(items)
            except Exception as e:
                logger.error(f"Failed to add combo box items: {e}")
        return widget
    
    @staticmethod
    def create_checkbox(text: str = "", parent=None, checked: bool = False) -> SafeWidget:
        """Create a safe checkbox widget"""
        widget = SafeWidget(QCheckBox, text, parent)
        if widget.available:
            try:
                widget.setChecked(checked)
            except Exception as e:
                logger.debug(f"Failed to set checkbox state: {e}")
        return widget
    
    @staticmethod
    def create_progress_bar(parent=None, minimum: int = 0, maximum: int = 100) -> SafeWidget:
        """Create a safe progress bar widget"""
        widget = SafeWidget(QProgressBar, parent)
        if widget.available:
            try:
                widget.setRange(minimum, maximum)
            except Exception as e:
                logger.debug(f"Failed to set progress bar range: {e}")
        return widget
    
    @staticmethod
    def create_frame(parent=None, frame_style: str = "box") -> SafeWidget:
        """Create a safe frame widget"""
        widget = SafeWidget(QFrame, parent)
        if widget.available:
            try:
                if frame_style == "box":
                    widget.setFrameStyle(QFrame.Box)
                elif frame_style == "panel":
                    widget.setFrameStyle(QFrame.Panel)
            except Exception as e:
                logger.debug(f"Failed to set frame style: {e}")
        return widget

class ThemeApplier:
    """Apply themes to UI components safely"""
    
    @staticmethod
    def apply_font(widget: SafeWidget, font_family: str = "Arial", font_size: int = 12):
        """Apply font to widget safely"""
        if not widget.available:
            return
        
        try:
            font = QFont(font_family, font_size)
            widget.setFont(font)
        except Exception as e:
            logger.debug(f"Failed to apply font: {e}")
    
    @staticmethod
    def apply_style(widget: SafeWidget, style_sheet: str):
        """Apply stylesheet to widget safely"""
        if not widget.available:
            return
        
        try:
            widget.setStyleSheet(style_sheet)
        except Exception as e:
            logger.debug(f"Failed to apply stylesheet: {e}")
    
    @staticmethod
    def apply_colors(widget: SafeWidget, background: str = None, foreground: str = None):
        """Apply colors to widget safely"""
        if not widget.available:
            return
        
        try:
            palette = widget.palette()
            if background:
                palette.setColor(QPalette.Background, QColor(background))
            if foreground:
                palette.setColor(QPalette.Foreground, QColor(foreground))
            widget.setPalette(palette)
        except Exception as e:
            logger.debug(f"Failed to apply colors: {e}")

class LayoutManager:
    """Manage layouts safely"""
    
    @staticmethod
    def add_widget_to_layout(layout: SafeWidget, widget: SafeWidget, stretch: int = 0):
        """Add widget to layout safely"""
        if not (layout.available and widget.available):
            return
        
        try:
            if stretch > 0:
                layout.addWidget(widget.widget, stretch)
            else:
                layout.addWidget(widget.widget)
        except Exception as e:
            logger.error(f"Failed to add widget to layout: {e}")
    
    @staticmethod
    def add_layout_to_layout(parent_layout: SafeWidget, child_layout: SafeWidget):
        """Add layout to layout safely"""
        if not (parent_layout.available and child_layout.available):
            return
        
        try:
            parent_layout.addLayout(child_layout.widget)
        except Exception as e:
            logger.error(f"Failed to add layout to layout: {e}")
    
    @staticmethod
    def set_layout_margins(layout: SafeWidget, left: int = 0, top: int = 0, 
                          right: int = 0, bottom: int = 0):
        """Set layout margins safely"""
        if not layout.available:
            return
        
        try:
            layout.setContentsMargins(left, top, right, bottom)
        except Exception as e:
            logger.debug(f"Failed to set layout margins: {e}")
    
    @staticmethod
    def set_layout_spacing(layout: SafeWidget, spacing: int = 6):
        """Set layout spacing safely"""
        if not layout.available:
            return
        
        try:
            layout.setSpacing(spacing)
        except Exception as e:
            logger.debug(f"Failed to set layout spacing: {e}")

def create_safe_ui_component(component_type: str, **kwargs) -> SafeWidget:
    """Create UI component safely with fallback"""
    factory = UIComponentFactory()
    
    component_map = {
        'label': factory.create_label,
        'button': factory.create_button,
        'layout': factory.create_layout,
        'text_edit': factory.create_text_edit,
        'line_edit': factory.create_line_edit,
        'combo_box': factory.create_combo_box,
        'checkbox': factory.create_checkbox,
        'progress_bar': factory.create_progress_bar,
        'frame': factory.create_frame
    }
    
    creator = component_map.get(component_type)
    if creator:
        try:
            return creator(**kwargs)
        except Exception as e:
            logger.error(f"Failed to create {component_type}: {e}")
    
    logger.warning(f"Unknown component type: {component_type}")
    return SafeWidget(QWidget)

def is_ui_available() -> bool:
    """Check if UI components are available"""
    return QT_WIDGETS_AVAILABLE
