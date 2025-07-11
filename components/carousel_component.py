# -*- coding: utf-8 -*-
"""
TimeNest 轮播组件 - 增强版
支持图片轮播、内容切换，带有动画效果
"""

import logging
from typing import List, Any, Optional, Union, Dict
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                           QStackedWidget, QPushButton, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient

from .base_component import BaseComponent

class CarouselComponent(BaseComponent):
    """轮播组件"""
    
    # 信号定义
    item_clicked = pyqtSignal(str)  # 轮播项ID
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        # 轮播数据
        self.carousel_items: List[Dict[str, Any]] = []
        self.current_index: int = 0
        
        # 轮播定时器
        self.carousel_timer: Optional[QTimer] = None
        
        # UI组件
        self.content_label: Optional[QLabel] = None
        self.indicator_widget: Optional[QWidget] = None
        self.prev_button: Optional[QPushButton] = None
        self.next_button: Optional[QPushButton] = None
        
        super().__init__(component_id, config)
    
    def initialize_component(self):
        """初始化轮播组件并添加使用提示"""
        try:
            if not self.widget or not self.layout:
                return
            
            # 创建标题
            title_label = self.create_title_label(self.config.get('name', '轮播'))
            self.layout.addWidget(title_label)
            
            # 创建内容区域
            content_layout = QHBoxLayout()
            
            # 添加组件内容
            super().initialize_component()
            
            # 添加滚动组件使用提示
            self.prompt_label = QLabel("支持通过右键菜单添加/移除组件，双击组件可查看详情")
            self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.prompt_label.setStyleSheet("color: #888;")
            content_layout.addWidget(self.prompt_label)
            
            self.layout.addLayout(content_layout)
            
            # 创建控制区域
            self._create_control_area()
            
            # 创建指示器
            self._create_indicator_area()
            
            # 加载轮播数据
            self._load_carousel_items()
            
            # 设置轮播定时器
            self._setup_carousel_timer()
            
            # 初始化内容
            self.update_content()
            
        except Exception as e:
            self.logger.error(f"初始化轮播组件失败: {e}")
            self.show_error(str(e))
    
    def _create_content_area(self):
        """创建内容区域"""
        try:
            self.content_label = QLabel()
            self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_label.setWordWrap(True)
            self.content_label.setMinimumHeight(80)
            self.content_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            
            # 添加点击事件
            self.content_label.mousePressEvent = self._on_content_clicked
            
            self.layout.addWidget(self.content_label)
            
        except Exception as e:
            self.logger.error(f"创建内容区域失败: {e}")
    
    def _create_control_area(self):
        """创建控制区域"""
        try:
            settings = self.config.get('settings', {})
            if not settings.get('show_controls', True):
                return
            
            control_widget = QWidget()
            control_layout = QHBoxLayout(control_widget)
            control_layout.setContentsMargins(0, 0, 0, 0)
            control_layout.setSpacing(5)
            
            # 上一个按钮
            self.prev_button = QPushButton("‹")
            self.prev_button.setFixedSize(30, 30)
            self.prev_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
                QPushButton:pressed {
                    background-color: #495057;
                }
            """)
            self.prev_button.clicked.connect(self._on_prev_clicked)
            control_layout.addWidget(self.prev_button)
            
            control_layout.addStretch()
            
            # 下一个按钮
            self.next_button = QPushButton("›")
            self.next_button.setFixedSize(30, 30)
            self.next_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
                QPushButton:pressed {
                    background-color: #495057;
                }
            """)
            self.next_button.clicked.connect(self._on_next_clicked)
            control_layout.addWidget(self.next_button)
            
            self.layout.addWidget(control_widget)
            
        except Exception as e:
            self.logger.error(f"创建控制区域失败: {e}")
    
    def _create_indicator_area(self):
        """创建指示器区域"""
        try:
            settings = self.config.get('settings', {})
            if not settings.get('show_indicators', True):
                return
            
            self.indicator_widget = QWidget()
            indicator_layout = QHBoxLayout(self.indicator_widget)
            indicator_layout.setContentsMargins(0, 5, 0, 5)
            indicator_layout.setSpacing(5)
            indicator_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.layout.addWidget(self.indicator_widget)
            
        except Exception as e:
            self.logger.error(f"创建指示器区域失败: {e}")
    
    def _load_carousel_items(self):
        """加载轮播数据"""
        try:
            settings = self.config.get('settings', {})
            self.carousel_items = settings.get('items', [])
            
            # 如果没有配置项目，创建默认项目
            if not self.carousel_items:
                self._create_default_items()
            
            # 重置索引
            self.current_index = 0
            
        except Exception as e:
            self.logger.error(f"加载轮播数据失败: {e}")
            self.carousel_items = []
    
    def _create_default_items(self):
        """创建默认轮播项目"""
        try:
            default_items = [
                {
                    'id': 'welcome',
                    'title': '欢迎使用 TimeNest',
                    'content': '这是一个功能强大的课程表管理工具',
                    'type': 'text',
                    'enabled': True
                },
                {
                    'id': 'tip1',
                    'title': '小贴士',
                    'content': '您可以通过拖拽来调整课程时间',
                    'type': 'tip',
                    'enabled': True
                },
                {
                    'id': 'tip2',
                    'title': '提醒功能',
                    'content': '支持上下课提醒，让您不错过任何课程',
                    'type': 'tip',
                    'enabled': True
                }
            ]
            
            self.carousel_items = default_items
            
            # 保存到配置
            settings = self.config.setdefault('settings', {})
            settings['items'] = self.carousel_items
            
        except Exception as e:
            self.logger.error(f"创建默认轮播项目失败: {e}")
    
    def _setup_carousel_timer(self):
        """设置轮播定时器"""
        try:
            settings = self.config.get('settings', {})
            auto_play = settings.get('auto_play', True)
            interval = settings.get('interval', 5000)  # 默认5秒
            
            if auto_play and len(self.carousel_items) > 1:
                if not self.carousel_timer:
                    self.carousel_timer = QTimer()
                    self.carousel_timer.timeout.connect(self._on_carousel_timeout)
                
                self.carousel_timer.start(interval)
            elif self.carousel_timer:
                self.carousel_timer.stop()
            
        except Exception as e:
            self.logger.error(f"设置轮播定时器失败: {e}")
    
    def _on_carousel_timeout(self):
        """轮播定时器超时"""
        try:
            if len(self.carousel_items) > 1:
                self.next_item()
            
        except Exception as e:
            self.logger.error(f"轮播定时器处理失败: {e}")
    
    def update_content(self):
        """更新轮播内容"""
        try:
            if not self.carousel_items:
                self._show_empty_message()
                return
            
            # 确保索引有效
            if self.current_index >= len(self.carousel_items):
                self.current_index = 0
            elif self.current_index < 0:
                self.current_index = len(self.carousel_items) - 1
            
            # 获取当前项目
            current_item = self.carousel_items[self.current_index]
            
            # 更新内容显示
            self._update_content_display(current_item)
            
            # 更新指示器
            self._update_indicators()
            
            # 更新控制按钮状态
            self._update_control_buttons()
            
        except Exception as e:
            self.logger.error(f"更新轮播内容失败: {e}")
    
    def _update_content_display(self, item: Dict[str, Any]):
        """更新内容显示"""
        try:
            if not self.content_label:
                return
            
            title = item.get('title', '')
            content = item.get('content', '')
            item_type = item.get('type', 'text')
            
            # 根据类型设置样式
            if item_type == 'tip':
                style_color = '#17a2b8'  # 蓝色
                icon = '💡'
            elif item_type == 'warning':
                style_color = '#ffc107'  # 黄色
                icon = '⚠️'
            elif item_type == 'error':
                style_color = '#dc3545'  # 红色
                icon = '❌'
            else:
                style_color = '#28a745'  # 绿色
                icon = '📝'
            
            # 构建显示文本
            if title and content:
                display_text = f"{icon} {title}\n\n{content}"
            elif title:
                display_text = f"{icon} {title}"
            elif content:
                display_text = f"{icon} {content}"
            else:
                display_text = f"{icon} 空内容"
            
            self.content_label.setText(display_text)
            
            # 更新样式
            self.content_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {style_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                    font-size: 12px;
                    line-height: 1.4;
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"更新内容显示失败: {e}")
    
    def _update_indicators(self):
        """更新指示器"""
        try:
            if not self.indicator_widget:
                return
            
            layout = self.indicator_widget.layout()
            if not layout:
                return
            
            # 清除现有指示器
            for i in reversed(range(layout.count())):
                child = layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
            
            # 创建新指示器
            for i, item in enumerate(self.carousel_items):
                if not item.get('enabled', True):
                    continue
                
                indicator = QLabel("●")
                indicator.setFixedSize(12, 12)
                indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if i == self.current_index:
                    indicator.setStyleSheet("color: #007bff; font-size: 12px;")
                else:
                    indicator.setStyleSheet("color: #dee2e6; font-size: 12px;")
                
                layout.addWidget(indicator)
            
        except Exception as e:
            self.logger.error(f"更新指示器失败: {e}")
    
    def _update_control_buttons(self):
        """更新控制按钮状态"""
        try:
            if not self.prev_button or not self.next_button:
                return
            
            # 如果只有一个项目或没有项目，禁用按钮
            enabled = len(self.carousel_items) > 1
            self.prev_button.setEnabled(enabled)
            self.next_button.setEnabled(enabled)
            
        except Exception as e:
            self.logger.error(f"更新控制按钮状态失败: {e}")
    
    def _show_empty_message(self):
        """显示空消息"""
        try:
            if self.content_label:
                self.content_label.setText("📭 暂无轮播内容")
                self.content_label.setStyleSheet("""
                    QLabel {
                        background-color: #f8f9fa;
                        color: #6c757d;
                        border: 2px dashed #dee2e6;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 5px;
                        font-style: italic;
                    }
                """)
            
        except Exception as e:
            self.logger.error(f"显示空消息失败: {e}")
    
    def _on_prev_clicked(self):
        """上一个按钮点击"""
        self.prev_item()
    
    def _on_next_clicked(self):
        """下一个按钮点击"""
        self.next_item()
    
    def _on_content_clicked(self, event):
        """内容点击事件"""
        try:
            if self.carousel_items and 0 <= self.current_index < len(self.carousel_items):
                current_item = self.carousel_items[self.current_index]
                item_id = current_item.get('id', '')
                if item_id:
                    self.item_clicked.emit(item_id)
            
        except Exception as e:
            self.logger.error(f"处理内容点击失败: {e}")
    
    def prev_item(self):
        """切换到上一个项目"""
        try:
            if len(self.carousel_items) > 1:
                self.current_index = (self.current_index - 1) % len(self.carousel_items)
                self.update_content()
            
        except Exception as e:
            self.logger.error(f"切换到上一个项目失败: {e}")
    
    def next_item(self):
        """切换到下一个项目"""
        try:
            if len(self.carousel_items) > 1:
                self.current_index = (self.current_index + 1) % len(self.carousel_items)
                self.update_content()
            
        except Exception as e:
            self.logger.error(f"切换到下一个项目失败: {e}")
    
    def add_carousel_item(self, title: str, content: str, item_type: str = 'text') -> str:
        """添加轮播项目"""
        try:
            import uuid
            item_id = str(uuid.uuid4())
            
            item = {
                'id': item_id,
                'title': title,
                'content': content,
                'type': item_type,
                'enabled': True,
                'created_time': datetime.now().isoformat()
            }
            
            self.carousel_items.append(item)
            
            # 保存到配置
            settings = self.config.setdefault('settings', {})
            settings['items'] = self.carousel_items
            
            # 重新设置定时器
            self._setup_carousel_timer()
            
            # 更新显示
            self.update_content()
            
            self.logger.info(f"添加轮播项目: {title}")
            return item_id
            
        except Exception as e:
            self.logger.error(f"添加轮播项目失败: {e}")
            return ""
    
    def remove_carousel_item(self, item_id: str) -> bool:
        """移除轮播项目"""
        try:
            original_count = len(self.carousel_items)
            self.carousel_items = [item for item in self.carousel_items if item.get('id') != item_id]
            
            if len(self.carousel_items) < original_count:
                # 调整当前索引
                if self.current_index >= len(self.carousel_items):
                    self.current_index = max(0, len(self.carousel_items) - 1)
                
                # 保存到配置
                settings = self.config.setdefault('settings', {})
                settings['items'] = self.carousel_items
                
                # 重新设置定时器
                self._setup_carousel_timer()
                
                # 更新显示
                self.update_content()
                
                self.logger.info(f"移除轮播项目: {item_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"移除轮播项目失败: {e}")
            return False
    
    def get_update_interval(self) -> int:
        """轮播组件不需要定时更新"""
        return 0
    
    def on_config_updated(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置更新回调"""
        try:
            # 重新加载轮播数据
            self._load_carousel_items()
            
            # 重新设置定时器
            self._setup_carousel_timer()
            
            # 检查是否需要重新初始化UI
            old_settings = old_config.get('settings', {})
            new_settings = new_config.get('settings', {})
            
            ui_changed = (
                old_settings.get('show_controls') != new_settings.get('show_controls') or
                old_settings.get('show_indicators') != new_settings.get('show_indicators')
            )
            
            if ui_changed:
                self.initialize_component()
            else:
                self.update_content()
            
        except Exception as e:
            self.logger.error(f"处理轮播配置更新失败: {e}")
    
    def cleanup_component(self):
        """清理组件资源"""
        try:
            # 停止轮播定时器
            if self.carousel_timer and self.carousel_timer.isActive():
                self.carousel_timer.stop()
                # 断开定时器信号连接
                self.carousel_timer.timeout.disconnect()
            
            # 断开按钮信号连接
            if self.prev_button:
                self.prev_button.clicked.disconnect()
            if self.next_button:
                self.next_button.clicked.disconnect()
            
            self.carousel_items.clear()
            
        except Exception as e:
            self.logger.error(f"清理轮播组件失败: {e}")