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
TimeNest 容器组件
用于管理和布局其他组件
"""

import logging
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QScrollArea, QSplitter, QTabWidget, QStackedWidget,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QFont

from .base_component import BaseComponent

class ContainerComponent(BaseComponent):
    """容器组件"""
    
    # 信号定义
    child_component_added = pyqtSignal(str)  # 子组件ID
    child_component_removed = pyqtSignal(str)  # 子组件ID
    layout_changed = pyqtSignal(str)  # 布局类型
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        # 子组件列表
        self.child_components: List[BaseComponent] = []
        
        # 容器布局
        self.container_widget: Optional[QWidget] = None
        self.container_layout: Optional[QVBoxLayout] = None
        
        # 布局类型相关组件
        self.scroll_area: Optional[QScrollArea] = None
        self.splitter: Optional[QSplitter] = None
        self.tab_widget: Optional[QTabWidget] = None
        self.stacked_widget: Optional[QStackedWidget] = None
        
        super().__init__(component_id, config)
    
    def initialize_component(self):
        """初始化容器组件"""
        try:
            if not self.widget or not self.layout:
                return
            
            # 创建标题
            title_label = self.create_title_label(self.config.get('name', '容器'))
            self.layout.addWidget(title_label)
            
            # 创建容器区域
            self._create_container_area()
            
            # 初始化内容
            self.update_content()
            
        except Exception as e:
            self.logger.error(f"初始化容器组件失败: {e}")
            self.show_error(str(e))
    
    def _create_container_area(self):
        """创建容器区域"""
        try:
            settings = self.config.get('settings', {})
            layout_type = settings.get('layout_type', 'vertical')  # vertical, horizontal, grid, tabs, stack, scroll
            
            # 根据布局类型创建不同的容器
            if layout_type == 'scroll':
                self._create_scroll_container()
            elif layout_type == 'tabs':
                self._create_tab_container()
            elif layout_type == 'stack':
                self._create_stack_container()
            elif layout_type == 'splitter_vertical':
                self._create_splitter_container(Qt.Orientation.Vertical)
            elif layout_type == 'splitter_horizontal':
                self._create_splitter_container(Qt.Orientation.Horizontal)
            else:
                self._create_basic_container(layout_type)
            
        except Exception as e:
            self.logger.error(f"创建容器区域失败: {e}")
    
    def _create_basic_container(self, layout_type: str):
        """创建基本容器"""
        try:
            self.container_widget = QWidget()
            
            
            if layout_type == 'horizontal':
                self.container_layout = QHBoxLayout(self.container_widget)
            
                self.container_layout = QHBoxLayout(self.container_widget)
            elif layout_type == 'grid':
                self.container_layout = QGridLayout(self.container_widget)
            else:  # vertical
                self.container_layout = QVBoxLayout(self.container_widget)
            
            self.container_layout.setContentsMargins(5, 5, 5, 5)
            self.container_layout.setSpacing(5)
            
            # 设置容器样式
            self.container_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                }
            """)
            
            self.layout.addWidget(self.container_widget)
            
        except Exception as e:
            self.logger.error(f"创建基本容器失败: {e}")
    
    def _create_scroll_container(self):
        """创建滚动容器"""
        try:
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            self.container_widget = QWidget()
            self.container_layout = QVBoxLayout(self.container_widget)
            self.container_layout.setContentsMargins(5, 5, 5, 5)
            self.container_layout.setSpacing(5)
            
            self.scroll_area.setWidget(self.container_widget)
            
            # 设置样式
            self.scroll_area.setStyleSheet("""
                QScrollArea {
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    background-color: #ffffff;
                }
                QScrollBar:vertical {
                    background-color: #f8f9fa;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar:handle:vertical {
                    background-color: #6c757d;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar:handle:vertical:hover {
                    background-color: #5a6268;
                }
            """)
            
            self.layout.addWidget(self.scroll_area)
            
        except Exception as e:
            self.logger.error(f"创建滚动容器失败: {e}")
    
    def _create_tab_container(self):
        """创建标签页容器"""
        try:
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
            self.tab_widget.setMovable(True)
            
            # 设置样式
            self.tab_widget.setStyleSheet("""
                QTabWidget:pane {
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    background-color: #ffffff;
                }
                QTabBar:tab {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-bottom: none;
                    border-radius: 6px 6px 0 0;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar:tab:selected {
                    background-color: #ffffff;
                    border-bottom: 1px solid #ffffff;
                }
                QTabBar:tab:hover {
                    background-color: #e9ecef;
                }
            """)
            
            self.layout.addWidget(self.tab_widget)
            
        except Exception as e:
            self.logger.error(f"创建标签页容器失败: {e}")
    
    def _create_stack_container(self):
        """创建堆叠容器"""
        try:
            self.stacked_widget = QStackedWidget()
            
            # 设置样式
            self.stacked_widget.setStyleSheet("""
                QStackedWidget {
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    background-color: #ffffff;
                }
            """)
            
            self.layout.addWidget(self.stacked_widget)
            
        except Exception as e:
            self.logger.error(f"创建堆叠容器失败: {e}")
    
    def _create_splitter_container(self, orientation: Qt.Orientation):
        """创建分割器容器"""
        try:
            self.splitter = QSplitter(orientation)
            self.splitter.setChildrenCollapsible(False)
            
            # 设置样式
            self.splitter.setStyleSheet("""
                QSplitter {
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    background-color: #ffffff;
                }
                QSplitter:handle {
                    background-color: #dee2e6;
                }
                QSplitter:handle:horizontal {
                    width: 3px;
                }
                QSplitter:handle:vertical {
                    height: 3px;
                }
                QSplitter:handle:hover {
                    background-color: #6c757d;
                }
            """)
            
            self.layout.addWidget(self.splitter)
            
        except Exception as e:
            self.logger.error(f"创建分割器容器失败: {e}")
    
    def update_content(self):
        """更新容器内容"""
        try:
            if not self.child_components:
                self._show_empty_message()
                return
            
            # 根据布局类型更新内容
            settings = self.config.get('settings', {})
            layout_type = settings.get('layout_type', 'vertical')
            
            
            if layout_type == 'tabs' and self.tab_widget:
                self._update_tab_content()
            
                self._update_tab_content()
            elif layout_type == 'stack' and self.stacked_widget:
                self._update_stack_content()
            elif layout_type.startswith('splitter') and self.splitter:
                self._update_splitter_content()
            elif layout_type == 'grid' and self.container_layout:
                self._update_grid_content()
            else:
                self._update_basic_content()
            
        except Exception as e:
            self.logger.error(f"更新容器内容失败: {e}")
    
    def _update_basic_content(self):
        """更新基本布局内容"""
        try:
            if not self.container_layout:
                return
            
            # 清除现有内容
            self._clear_layout(self.container_layout)
            
            # 添加子组件
            for component in self.child_components:
                if component.is_enabled() and component.widget:
                    self.container_layout.addWidget(component.widget)
            
            # 添加弹性空间
            self.container_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"更新基本布局内容失败: {e}")
    
    def _update_grid_content(self):
        """更新网格布局内容"""
        try:
            if not self.container_layout:
                return
            
            # 清除现有内容
            self._clear_layout(self.container_layout)
            
            settings = self.config.get('settings', {})
            columns = settings.get('grid_columns', 2)
            
            # 按网格排列子组件
            for i, component in enumerate(self.child_components):
                if component.is_enabled() and component.widget:
                    row = i // columns
                    col = i % columns
                    self.container_layout.addWidget(component.widget, row, col)
            
        except Exception as e:
            self.logger.error(f"更新网格布局内容失败: {e}")
    
    def _update_tab_content(self):
        """更新标签页内容"""
        try:
            if not self.tab_widget:
                return
            
            # 清除现有标签页
            self.tab_widget.clear()
            
            # 添加子组件作为标签页
            for component in self.child_components:
                if component.is_enabled() and component.widget:
                    tab_name = component.config.get('name', f'组件 {component.component_id}')
                    self.tab_widget.addTab(component.widget, tab_name)
            
        except Exception as e:
            self.logger.error(f"更新标签页内容失败: {e}")
    
    def _update_stack_content(self):
        """更新堆叠内容"""
        try:
            if not self.stacked_widget:
                return
            
            # 清除现有页面
            while self.stacked_widget.count() > 0:
                widget = self.stacked_widget.widget(0)
                self.stacked_widget.removeWidget(widget)
            
            # 添加子组件作为页面
            for component in self.child_components:
                if component.is_enabled() and component.widget:
                    self.stacked_widget.addWidget(component.widget)
            
            # 显示第一个页面
            if self.stacked_widget.count() > 0:
                self.stacked_widget.setCurrentIndex(0)
            
        except Exception as e:
            self.logger.error(f"更新堆叠内容失败: {e}")
    
    def _update_splitter_content(self):
        """更新分割器内容"""
        try:
            if not self.splitter:
                return
            
            # 清除现有组件
            while self.splitter.count() > 0:
                widget = self.splitter.widget(0)
                widget.setParent(None)
            
            # 添加子组件
            for component in self.child_components:
                if component.is_enabled() and component.widget:
                    self.splitter.addWidget(component.widget)
            
            # 设置均匀分割
            if self.splitter.count() > 0:
                sizes = [100] * self.splitter.count()
                self.splitter.setSizes(sizes)
            
        except Exception as e:
            self.logger.error(f"更新分割器内容失败: {e}")
    
    def _clear_layout(self, layout):
        """清除布局中的所有组件"""
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            
        except Exception as e:
            self.logger.error(f"清除布局失败: {e}")
    
    def _show_empty_message(self):
        """显示空消息"""
        try:
            # 创建空消息标签
            empty_label = QLabel("📦 容器为空\n\n请添加子组件")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 14px;
                    font-style: italic;
                    padding: 40px;
                    border: 2px dashed #dee2e6;
                    border-radius: 8px;
                    background-color: #f8f9fa;
                }
            """)
            
            # 根据容器类型添加到合适的位置
            if self.tab_widget:
                self.tab_widget.addTab(empty_label, "空")
            elif self.stacked_widget:
                self.stacked_widget.addWidget(empty_label)
            elif self.splitter:
                self.splitter.addWidget(empty_label)
            elif self.container_layout:
                self.container_layout.addWidget(empty_label)
            
        except Exception as e:
            self.logger.error(f"显示空消息失败: {e}")
    
    def add_child_component(self, component: BaseComponent) -> bool:
        """添加子组件"""
        try:
            if component and component not in self.child_components:
                self.child_components.append(component)
                
                # 更新显示
                self.update_content()
                
                # 发送信号
                self.child_component_added.emit(component.component_id)
                
                self.logger.info(f"添加子组件: {component.component_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"添加子组件失败: {e}")
            return False
    
    def remove_child_component(self, component_id: str) -> bool:
        """移除子组件"""
        try:
            for i, component in enumerate(self.child_components):
                if component.component_id == component_id:
                    # 从列表中移除:
                    # 从列表中移除
                    removed_component = self.child_components.pop(i)
                    
                    # 清理组件
                    if hasattr(removed_component, 'cleanup_component'):
                        removed_component.cleanup_component()
                    
                    # 更新显示
                    self.update_content()
                    
                    # 发送信号
                    self.child_component_removed.emit(component_id)
                    
                    self.logger.info(f"移除子组件: {component_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"移除子组件失败: {e}")
            return False
    
    def get_child_component(self, component_id: str) -> Optional[BaseComponent]:
        """获取子组件"""
        try:
            for component in self.child_components:
                if component.component_id == component_id:
                    return component
            return None
            
        except Exception as e:
            self.logger.error(f"获取子组件失败: {e}")
            return None
    
    def get_child_components(self) -> List[BaseComponent]:
        """获取所有子组件"""
        return self.child_components.copy()
    
    def set_current_child(self, component_id: str) -> bool:
        """设置当前显示的子组件（用于标签页和堆叠布局）"""
        try:
            for i, component in enumerate(self.child_components):
                if component.component_id == component_id:
                    if self.tab_widget:
                        self.tab_widget.setCurrentIndex(i)
                        return True
                    elif self.stacked_widget:
                        self.stacked_widget.setCurrentIndex(i)
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"设置当前子组件失败: {e}")
            return False
    
    def get_update_interval(self) -> int:
        """容器组件不需要定时更新"""
        return 0
    
    def on_config_updated(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置更新回调"""
        try:
            # 检查布局类型是否改变
            old_layout = (old_config.get('settings', {}) or {}).get('layout_type', 'vertical')
            new_layout = (new_config.get('settings', {}) or {}).get('layout_type', 'vertical')
            
            
            if old_layout != new_layout:
                # 布局类型改变，需要重新初始化:
            
                # 布局类型改变，需要重新初始化
                self.initialize_component()
                self.layout_changed.emit(new_layout)
            else:
                # 只是配置改变，更新内容
                self.update_content()
            
        except Exception as e:
            self.logger.error(f"处理容器配置更新失败: {e}")
    
    def cleanup_component(self):
        """清理组件资源"""
        try:
            # 清理所有子组件
            for component in self.child_components:
                if hasattr(component, 'cleanup_component'):
                    component.cleanup_component()
            
            self.child_components.clear()
            
        except Exception as e:
            self.logger.error(f"清理容器组件失败: {e}")