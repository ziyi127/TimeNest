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
TimeNest 组件基类
定义所有组件的通用接口和行为
"""

import logging
from abc import ABC, abstractmethod, ABCMeta
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QFont, QPalette, QColor


# 创建兼容的 metaclass
class QObjectABCMeta(type(QObject), ABCMeta):
    """兼容 QObject 和 ABC 的 metaclass"""
    pass


class BaseComponent(QObject, ABC, metaclass=QObjectABCMeta):
    """组件基类"""
    
    # 信号定义
    config_changed = Signal(str, dict)  # 组件ID, 新配置
    error_occurred = Signal(str, str)  # 组件ID, 错误信息
    status_changed = Signal(str, str)  # 组件ID, 状态信息
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        super().__init__()
        self.component_id = component_id
        self.config = config.copy()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 组件状态
        self.is_enabled = config.get('enabled', True)
        self.is_visible = True
        self.is_initialized = False
        
        # UI相关
        self.widget: Optional[QWidget] = None
        self.layout: Optional[QVBoxLayout] = None
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_timer_update)
        
        # 初始化组件
        self._initialize()
        
        self.logger.debug(f"组件初始化完成: {component_id}")
    
    def _initialize(self):
        """初始化组件"""
        try:
            # 创建主widget
            self.widget = QFrame()
            self.widget.setObjectName(f"component_{self.component_id}")
            
            # 设置基本样式
            self.widget.setFrameStyle(QFrame.Shape.Box)
            self.widget.setLineWidth(1)
            
            # 创建布局
            self.layout = QVBoxLayout(self.widget)
            self.layout.setContentsMargins(5, 5, 5, 5)
            self.layout.setSpacing(2)
            
            # 应用配置
            self._apply_config()
            
            # 子类初始化
            self.initialize_component()
            
            # 启动更新定时器（如果需要）
            update_interval = self.get_update_interval()
            if update_interval > 0:
                self.update_timer.start(update_interval)
            
            self.is_initialized = True
            
        except Exception as e:
            self.logger.error(f"初始化组件失败: {e}")
            self.error_occurred.emit(self.component_id, str(e))
    
    def _apply_config(self):
        """应用配置"""
        try:
            if not self.widget:
                return
            
            # 应用大小配置
            size_config = self.config.get('size', {})
            if 'width' in size_config and 'height' in size_config:
                self.widget.setFixedSize(size_config.get('width'), size_config.get('height'))
            elif 'width' in size_config:
                self.widget.setFixedWidth(size_config.get('width'))
            elif 'height' in size_config:
                self.widget.setFixedHeight(size_config.get('height'))
            
            # 应用可见性
            self.widget.setVisible(self.is_enabled and self.is_visible)
            
            # 应用样式
            style_config = self.config.get('style', {})
            self._apply_style(style_config)
            
        except Exception as e:
            self.logger.error(f"应用配置失败: {e}")
    
    def _apply_style(self, style_config: Dict[str, Any]):
        """应用样式配置"""
        try:
            if not self.widget:
                return
            
            style_parts = []
            
            # 背景色
            if 'background_color' in style_config:
                style_parts.append(f"background-color: {style_config.get('background_color')}")
            
            # 边框
            if 'border_color' in style_config:
                border_width = style_config.get('border_width', 1)
                style_parts.append(f"border: {border_width}px solid {style_config.get('border_color')}")
            
            # 圆角
            if 'border_radius' in style_config:
                style_parts.append(f"border-radius: {style_config.get('border_radius')}px")
            
            # 透明度
            if 'opacity' in style_config:
                opacity = max(0.0, min(1.0, style_config.get('opacity')))
                self.widget.setWindowOpacity(opacity)
            
            # 应用样式
            if style_parts:
                style_sheet = f"#{self.widget.objectName()} {{ {'; '.join(style_parts)} }}"
                self.widget.setStyleSheet(style_sheet)
            
        except Exception as e:
            self.logger.error(f"应用样式失败: {e}")
    
    @abstractmethod
    def initialize_component(self):
        """子类实现的初始化方法"""
        pass
    
    @abstractmethod
    def update_content(self):
        """更新组件内容"""
        pass
    
    def get_update_interval(self) -> int:
        """获取更新间隔（毫秒），返回0表示不需要定时更新"""
        return self.config.get('settings', {}).get('update_interval', 0)
    
    def _on_timer_update(self):
        """定时器更新回调"""
        try:
            if self.is_enabled and self.is_visible:
                self.update_content()
        except Exception as e:
            self.logger.error(f"定时更新失败: {e}")
    
    def get_widget(self) -> Optional[QWidget]:
        """获取组件的主widget"""
        return self.widget
    
    def get_config(self) -> Dict[str, Any]:
        """获取组件配置"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新组件配置"""
        try:
            old_config = self.config.copy()
            self.config.update(new_config)
            
            # 更新启用状态
            old_enabled = self.is_enabled
            self.is_enabled = self.config.get('enabled', True)
            
            # 重新应用配置
            self._apply_config()
            
            # 如果启用状态改变，更新定时器
            if old_enabled != self.is_enabled:
                if self.is_enabled and self.get_update_interval() > 0:
                    self.update_timer.start(self.get_update_interval())
                elif not self.is_enabled:
                    self.update_timer.stop()
            
            # 子类处理配置更新
            self.on_config_updated(old_config, self.config)
            
            # 发出信号
            self.config_changed.emit(self.component_id, self.config)
            
            self.logger.debug(f"配置已更新: {self.component_id}")
            
        except Exception as e:
            self.logger.error(f"更新配置失败: {e}")
            self.error_occurred.emit(self.component_id, str(e))
    
    def on_config_updated(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置更新回调，子类可重写"""
        pass
    
    def set_visible(self, visible: bool):
        """设置组件可见性"""
        try:
            self.is_visible = visible
            if self.widget:
                self.widget.setVisible(self.is_enabled and self.is_visible)
            
        except Exception as e:
            self.logger.error(f"设置可见性失败: {e}")
    
    def set_enabled(self, enabled: bool):
        """设置组件启用状态"""
        try:
            self.is_enabled = enabled
            self.config['enabled'] = enabled
            
            if self.widget:
                self.widget.setVisible(self.is_enabled and self.is_visible)
            
            # 更新定时器
            if enabled and self.get_update_interval() > 0:
                self.update_timer.start(self.get_update_interval())
            else:
                self.update_timer.stop()
            
        except Exception as e:
            self.logger.error(f"设置启用状态失败: {e}")
    
    def get_component_info(self) -> Dict[str, Any]:
        """获取组件信息"""
        return {
            'id': self.component_id,
            'type': self.config.get('type', 'unknown'),
            'name': self.config.get('name', '未命名组件'),
            'enabled': self.is_enabled,
            'visible': self.is_visible,
            'initialized': self.is_initialized,
            'update_interval': self.get_update_interval()
        }
    
    def create_title_label(self, title: str) -> QLabel:
        """创建标题标签"""
        label = QLabel(title)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label
    
    def create_content_label(self, text: str = "") -> QLabel:
        """创建内容标签"""
        label = QLabel(text)
        font = QFont()
        font.setPointSize(9)
        label.setFont(font)
        label.setWordWrap(True)
        return label
    
    def show_error(self, message: str):
        """显示错误信息"""
        try:
            if self.layout:
                # 清除现有内容
                for i in reversed(range(self.layout.count())):
                    child = self.layout.itemAt(i).widget()
                    if child:
                        child.deleteLater()
                
                # 显示错误信息
                error_label = QLabel(f"错误: {message}")
                error_label.setStyleSheet("color: red; font-weight: bold;")
                error_label.setWordWrap(True)
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.layout.addWidget(error_label)
            
            self.logger.error(f"组件错误: {message}")
            self.error_occurred.emit(self.component_id, message)
            
        except Exception as e:
            self.logger.error(f"显示错误信息失败: {e}")
    
    def show_loading(self, message: str = "加载中..."):
        """显示加载状态"""
        try:
            if self.layout:
                # 清除现有内容
                for i in reversed(range(self.layout.count())):
                    child = self.layout.itemAt(i).widget()
                    if child:
                        child.deleteLater()
                
                # 显示加载信息
                loading_label = QLabel(message)
                loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                loading_label.setStyleSheet("color: gray; font-style: italic;")
                self.layout.addWidget(loading_label)
            
        except Exception as e:
            self.logger.error(f"显示加载状态失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止定时器并断开信号连接
            if self.update_timer.isActive():
                self.update_timer.stop()
            self.update_timer.timeout.disconnect()
            
            # 子类清理
            self.cleanup_component()
            
            # 清理UI
            if self.widget:
                self.widget.deleteLater()
                self.widget = None
            
            self.logger.debug(f"组件清理完成: {self.component_id}")
            
        except Exception as e:
            self.logger.error(f"清理组件失败: {e}")
    
    def cleanup_component(self):
        """子类实现的清理方法"""
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.component_id})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.component_id}', type='{self.config.get('type', 'unknown')}')"