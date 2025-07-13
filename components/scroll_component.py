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
TimeNest 滚动组件
支持文本滚动、图片轮播等功能
"""

import logging
from typing import List, Any, Optional, Union, Dict
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QParallelAnimationGroup
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                           QScrollArea, QFrame, QGraphicsOpacityEffect, QTextEdit)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QTextOption

from .base_component import BaseComponent


class ScrollDirection:
    """滚动方向"""
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"
    TOP_TO_BOTTOM = "top_to_bottom"
    BOTTOM_TO_TOP = "bottom_to_top"


class ScrollMode:
    """滚动模式"""
    CONTINUOUS = "continuous"  # 连续滚动
    STEP = "step"             # 步进滚动
    FADE = "fade"             # 淡入淡出
    SLIDE = "slide"           # 滑动切换


class ScrollTrigger:
    """滚动触发器"""
    AUTO = "auto"             # 自动滚动
    HOVER = "hover"           # 鼠标悬停
    CLICK = "click"           # 点击触发
    MANUAL = "manual"         # 手动控制


class ScrollItem(QWidget):
    """滚动项"""
    
    def __init__(self, content: Union[str, QPixmap], item_type: str = "text"):
        super().__init__()
        self.content = content
        self.item_type = item_type
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        
        if self.item_type == "text":
            label = QLabel(str(self.content))
        
            label = QLabel(str(self.content))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet("""
                QLabel {
                    color: #333333;
                    font-size: 14px;
                    padding: 5px;
                    background-color: rgba(255, 255, 255, 0.8);
                    border-radius: 5px;
                }
            """)
            layout.addWidget(label)
        elif self.item_type == "image":
            label = QLabel()
            if isinstance(self.content, QPixmap):
                label.setPixmap(self.content.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)


class ScrollComponent(BaseComponent):
    """滚动组件"""
    
    # 信号定义
    item_clicked = pyqtSignal(int)  # 项目索引
    scroll_finished = pyqtSignal()  # 滚动完成
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.component_name = "滚动组件"
        
        # 滚动配置
        self.scroll_direction = ScrollDirection.LEFT_TO_RIGHT
        self.scroll_speed = 50  # 像素/秒
        self.auto_scroll = True
        self.loop_scroll = True
        self.pause_on_hover = True
        
        # 滚动项目
        self.scroll_items: List[ScrollItem] = []
        self.current_index = 0
        
        # 动画和定时器
        self.scroll_timer = QTimer()
        self.scroll_animation = None
        self.fade_animation = None
        
        # UI组件
        self.scroll_area = None
        self.content_widget = None
        self.content_layout = None
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # 设置样式
        self.setStyleSheet("""
            ScrollComponent {
                background-color: rgba(240, 240, 240, 0.9);
                border-radius: 10px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
    
    def setup_animations(self):
        """设置动画"""
        # 滚动定时器
        self.scroll_timer.timeout.connect(self._scroll_step)
        
        # 鼠标悬停事件
        if self.pause_on_hover:
            self.enterEvent = self._on_mouse_enter
            self.leaveEvent = self._on_mouse_leave
    
    def add_text_item(self, text: str):
        """添加文本项"""
        item = ScrollItem(text, "text")
        self.add_item(item)
    
    def add_image_item(self, pixmap: QPixmap):
        """添加图片项"""
        item = ScrollItem(pixmap, "image")
        self.add_item(item)
    
    def add_item(self, item: ScrollItem):
        """添加滚动项"""
        self.scroll_items.append(item)
        self.content_layout.addWidget(item)
        
        # 设置点击事件
        item.mousePressEvent = lambda event, idx=len(self.scroll_items)-1: self._on_item_clicked(idx)
    
    def remove_item(self, index: int):
        """移除滚动项"""
        if 0 <= index < len(self.scroll_items):
            item = self.scroll_items.pop(index)
            self.content_layout.removeWidget(item)
            item.deleteLater()
    
    def clear_items(self):
        """清空所有项"""
        for item in self.scroll_items:
            self.content_layout.removeWidget(item)
            item.deleteLater()
        self.scroll_items.clear()
        self.current_index = 0
    
    def start_scroll(self):
        """开始滚动"""
        if self.auto_scroll and self.scroll_items:
            interval = 1000 // self.scroll_speed  # 计算定时器间隔
            self.scroll_timer.start(max(10, interval))
    
    def stop_scroll(self):
        """停止滚动"""
        self.scroll_timer.stop()
        if self.scroll_animation:
            self.scroll_animation.stop()
    
    def pause_scroll(self):
        """暂停滚动"""
        self.scroll_timer.stop()
    
    def resume_scroll(self):
        """恢复滚动"""
        if self.auto_scroll:
            self.start_scroll()
    
    def _scroll_step(self):
        """滚动步进"""
        try:
            if not self.scroll_items:
                return
            
            
            if self.scroll_direction == ScrollDirection.LEFT_TO_RIGHT:
                self._scroll_horizontal(1)
            
                self._scroll_horizontal(1)
            elif self.scroll_direction == ScrollDirection.RIGHT_TO_LEFT:
                self._scroll_horizontal(-1)
            elif self.scroll_direction == ScrollDirection.TOP_TO_BOTTOM:
                self._scroll_vertical(1)
            elif self.scroll_direction == ScrollDirection.BOTTOM_TO_TOP:
                self._scroll_vertical(-1)
                
        except Exception as e:
            self.logger.error(f"滚动步进失败: {e}")
    
    def _scroll_horizontal(self, direction: int):
        """水平滚动"""
        try:
            scroll_bar = self.scroll_area.horizontalScrollBar()
            current_value = scroll_bar.value()
            max_value = scroll_bar.maximum()
            
            new_value = current_value + direction
            
            
            if new_value > max_value:
                if self.loop_scroll:
                    scroll_bar.setValue(0)
                else:
                    self.stop_scroll()
                    self.scroll_finished.emit()
            elif new_value < 0:
                if self.loop_scroll:
                    scroll_bar.setValue(max_value)
                else:
                    self.stop_scroll()
                    self.scroll_finished.emit()
            else:
                scroll_bar.setValue(new_value)
                
        except Exception as e:
            self.logger.error(f"水平滚动失败: {e}")
    
    def _scroll_vertical(self, direction: int):
        """垂直滚动"""
        try:
            scroll_bar = self.scroll_area.verticalScrollBar()
            current_value = scroll_bar.value()
            max_value = scroll_bar.maximum()
            
            new_value = current_value + direction
            
            
            if new_value > max_value:
                if self.loop_scroll:
                    scroll_bar.setValue(0)
                else:
                    self.stop_scroll()
                    self.scroll_finished.emit()
            elif new_value < 0:
                if self.loop_scroll:
                    scroll_bar.setValue(max_value)
                else:
                    self.stop_scroll()
                    self.scroll_finished.emit()
            else:
                scroll_bar.setValue(new_value)
                
        except Exception as e:
            self.logger.error(f"垂直滚动失败: {e}")
    
    def _on_item_clicked(self, index: int):
        """项目点击事件"""
        self.current_index = index
        self.item_clicked.emit(index)
    
    def _on_mouse_enter(self, event):
        """鼠标进入事件"""
        if self.pause_on_hover:
            self.pause_scroll()
    
    def _on_mouse_leave(self, event):
        """鼠标离开事件"""
        if self.pause_on_hover:
            self.resume_scroll()
    
    def set_scroll_direction(self, direction: str):
        """设置滚动方向"""
        self.scroll_direction = direction
        
        # 根据方向调整布局
        if direction in [ScrollDirection.LEFT_TO_RIGHT, ScrollDirection.RIGHT_TO_LEFT]:
            if isinstance(self.content_layout, QVBoxLayout):
                # 切换到水平布局
                self._switch_to_horizontal_layout()
        else:
            if isinstance(self.content_layout, QHBoxLayout):
                # 切换到垂直布局:
                # 切换到垂直布局
                self._switch_to_vertical_layout()
    
    def _switch_to_horizontal_layout(self):
        """切换到水平布局"""
        try:
            # 保存当前项目
            items = self.scroll_items.copy()
            self.clear_items()
            
            # 创建新布局
            self.content_layout = QHBoxLayout(self.content_widget)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self.content_layout.setSpacing(10)
            
            # 重新添加项目
            for item in items:
                self.add_item(item)
                
        except Exception as e:
            self.logger.error(f"切换到水平布局失败: {e}")
    
    def _switch_to_vertical_layout(self):
        """切换到垂直布局"""
        try:
            # 保存当前项目
            items = self.scroll_items.copy()
            self.clear_items()
            
            # 创建新布局
            self.content_layout = QVBoxLayout(self.content_widget)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self.content_layout.setSpacing(10)
            
            # 重新添加项目
            for item in items:
                self.add_item(item)
                
        except Exception as e:
            self.logger.error(f"切换到垂直布局失败: {e}")
    
    def set_scroll_speed(self, speed: int):
        """设置滚动速度"""
        self.scroll_speed = max(1, min(200, speed))
        if self.scroll_timer.isActive():
            self.stop_scroll()
            self.start_scroll()
    
    def set_auto_scroll(self, enabled: bool):
        """设置自动滚动"""
        self.auto_scroll = enabled
        if enabled and hasattr(self, "start_scroll"):
            self.start_scroll()
        else:
            self.stop_scroll()
    
    def set_loop_scroll(self, enabled: bool):
        """设置循环滚动"""
        self.loop_scroll = enabled
    
    def get_config(self) -> dict:
        """获取组件配置"""
        config = super().get_config()
        config.update({
            'scroll_direction': self.scroll_direction,
            'scroll_speed': self.scroll_speed,
            'auto_scroll': self.auto_scroll,
            'loop_scroll': self.loop_scroll,
            'pause_on_hover': self.pause_on_hover
        })
        return config
    
    def set_config(self, config: dict):
        """设置组件配置"""
        super().set_config(config)
        
        
        if 'scroll_direction' in config:
            self.set_scroll_direction(config.get('scroll_direction'))
        if 'scroll_speed' in config:
            self.set_scroll_speed(config.get('scroll_speed'))
        if 'auto_scroll' in config:
            self.set_auto_scroll(config.get('auto_scroll'))
        if 'loop_scroll' in config:
            self.set_loop_scroll(config.get('loop_scroll'))
        if 'pause_on_hover' in config:
            self.pause_on_hover = config.get('pause_on_hover')
