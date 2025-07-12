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
TimeNest 通知组件UI
显示和管理通知的用户界面组件
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSizePolicy, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor

from core.notification_service import NotificationHostService, NotificationRequest, NotificationType, NotificationPriority

class NotificationItem(QWidget):
    """
    单个通知项组件
    """
    
    # 信号定义
    dismiss_requested = pyqtSignal(str)  # 请求关闭通知
    action_clicked = pyqtSignal(str, str)  # 通知动作被点击
    
    def __init__(self, notification: NotificationRequest, parent=None):
        """
        初始化通知项
        
        Args:
            notification: 通知请求对象
            parent: 父组件
        """
        super().__init__(parent)
        
        self.notification = notification
        self.logger = logging.getLogger(f'{__name__}.NotificationItem')
        
        # UI组件
        self.main_layout: Optional[QHBoxLayout] = None
        self.content_layout: Optional[QVBoxLayout] = None
        self.action_layout: Optional[QHBoxLayout] = None
        
        self.icon_label: Optional[QLabel] = None
        self.title_label: Optional[QLabel] = None
        self.message_label: Optional[QLabel] = None
        self.time_label: Optional[QLabel] = None
        self.dismiss_button: Optional[QPushButton] = None
        
        # 初始化UI
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        try:
            # 设置组件属性
            self.setFixedHeight(80)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            # 主布局
            self.main_layout = QHBoxLayout(self)
            self.main_layout.setContentsMargins(10, 8, 10, 8)
            self.main_layout.setSpacing(10)
            
            # 图标
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(32, 32)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.update_icon()
            self.main_layout.addWidget(self.icon_label)
            
            # 内容区域
            self.content_layout = QVBoxLayout()
            self.content_layout.setSpacing(2)
            
            # 标题
            self.title_label = QLabel(self.notification.title)
            self.title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
            self.title_label.setWordWrap(True)
            self.content_layout.addWidget(self.title_label)
            
            # 消息内容
            if self.notification.message:
                self.message_label = QLabel(self.notification.message)
                self.message_label.setFont(QFont("Microsoft YaHei", 9))
                self.message_label.setWordWrap(True)
                self.message_label.setStyleSheet("color: #666;")
                self.content_layout.addWidget(self.message_label)
            
            # 时间
            self.time_label = QLabel(self.format_time())
            self.time_label.setFont(QFont("Microsoft YaHei", 8))
            self.time_label.setStyleSheet("color: #999;")
            self.content_layout.addWidget(self.time_label)
            
            self.main_layout.addLayout(self.content_layout)
            
            # 动作按钮区域
            self.action_layout = QVBoxLayout()
            self.action_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # 关闭按钮
            self.dismiss_button = QPushButton("×")
            self.dismiss_button.setFixedSize(20, 20)
            self.dismiss_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #999;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    color: #666;
                }
            """)
            self.dismiss_button.clicked.connect(self.dismiss_notification)
            self.action_layout.addWidget(self.dismiss_button)
            
            # 添加自定义动作按钮
            if self.notification.actions:
                for action_id, action_text in self.notification.actions.items():
                    action_button = QPushButton(action_text)
                    action_button.setFixedHeight(25)
                    action_button.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            padding: 2px 8px;
                            font-size: 9px;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """)
                    action_button.clicked.connect(
                        lambda checked, aid=action_id: self.action_clicked.emit(self.notification.id, aid)
                    )
                    self.action_layout.addWidget(action_button)
            
            self.main_layout.addLayout(self.action_layout)
            
        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")
    
    def update_icon(self):
        """
        更新图标
        """
        try:
            # 根据通知类型设置图标
            icon_text = "ℹ️"  # 默认信息图标
            
            
            if self.notification.type == NotificationType.SUCCESS:
                icon_text = "✅"
            elif self.notification.type == NotificationType.WARNING:
                icon_text = "⚠️"
            elif self.notification.type == NotificationType.ERROR:
                icon_text = "❌"
            elif self.notification.type == NotificationType.REMINDER:
                icon_text = "⏰"
            elif self.notification.type == NotificationType.CLASS_START:
                icon_text = "📚"
            elif self.notification.type == NotificationType.CLASS_END:
                icon_text = "🎓"
            elif self.notification.type == NotificationType.BREAK_START:
                icon_text = "☕"
            
            self.icon_label.setText(icon_text)
            self.icon_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    border: 1px solid #ddd;
                    border-radius: 16px;
                    background-color: #f8f9fa;
                }
            """)
            
        except Exception as e:
            self.logger.error(f"更新图标失败: {e}")
    
    def apply_styles(self):
        """
        应用样式
        """
        try:
            # 根据优先级设置边框颜色
            border_color = "#e0e0e0"
            
            
            if self.notification.priority == NotificationPriority.HIGH:
                border_color = "#e74c3c"
            
                border_color = "#e74c3c"
            elif self.notification.priority == NotificationPriority.MEDIUM:
                border_color = "#f39c12"
            
            self.setStyleSheet(f"""
                NotificationItem {
                    background-color: #ffffff;
                    border: 2px solid {border_color};
                    border-radius: 6px;
                    margin: 2px;
                }
                NotificationItem:hover {
                    background-color: #f8f9fa;
                }
            """)
            
        except Exception as e:
            self.logger.error(f"应用样式失败: {e}")
    
    def format_time(self) -> str:
        """
        格式化时间显示
        
        Returns:
            格式化的时间字符串
        """
        try:
            if self.notification.timestamp:
                now = datetime.now()
                diff = now - self.notification.timestamp
                
                
                if diff.total_seconds() < 60:
                    return "刚刚"
                
                    return "刚刚"
                elif diff.total_seconds() < 3600:
                    minutes = int(diff.total_seconds() / 60)
                    return f"{minutes}分钟前"
                elif diff.total_seconds() < 86400:
                    hours = int(diff.total_seconds() / 3600)
                    return f"{hours}小时前"
                else:
                    return self.notification.timestamp.strftime("%m-%d %H:%M")
            
            return "未知时间"
            
        except Exception as e:
            self.logger.error(f"格式化时间失败: {e}")
            return "--"
    
    def dismiss_notification(self):
        """
        关闭通知
        """
        try:
            self.dismiss_requested.emit(self.notification.id)
            
        except Exception as e:
            self.logger.error(f"关闭通知失败: {e}")

class NotificationWidget(QWidget):
    """
    通知显示组件
    
    显示和管理所有通知
    """
    
    # 信号定义
    notification_dismissed = pyqtSignal(str)  # 通知被关闭
    notification_action_clicked = pyqtSignal(str, str)  # 通知动作被点击
    clear_all_requested = pyqtSignal()  # 请求清除所有通知
    
    def __init__(self, notification_service: NotificationHostService, parent=None):
        """
        初始化通知组件
        
        Args:
            notification_service: 通知服务实例
            parent: 父组件
        """
        super().__init__(parent)
        
        self.notification_service = notification_service
        self.logger = logging.getLogger(f'{__name__}.NotificationWidget')
        
        # 通知项管理
        self.notification_items: Dict[str, NotificationItem] = {}
        
        # UI组件
        self.main_layout: Optional[QVBoxLayout] = None
        self.header_layout: Optional[QHBoxLayout] = None
        self.content_layout: Optional[QVBoxLayout] = None
        
        self.title_label: Optional[QLabel] = None
        self.count_label: Optional[QLabel] = None
        self.clear_button: Optional[QPushButton] = None
        self.scroll_area: Optional[QScrollArea] = None
        self.notification_list: Optional[QWidget] = None
        self.notification_list_layout: Optional[QVBoxLayout] = None
        self.empty_label: Optional[QLabel] = None
        
        # 初始化UI
        self.init_ui()
        self.init_connections()
        
        # 设置样式
        self.apply_styles()
        
        # 加载初始数据
        self.load_notifications()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        try:
            # 设置组件属性
            self.setFixedSize(320, 400)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            
            # 主布局
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(10, 10, 10, 10)
            self.main_layout.setSpacing(8)
            
            # 标题栏
            self.header_layout = QHBoxLayout()
            
            self.title_label = QLabel("通知")
            self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
            self.header_layout.addWidget(self.title_label)
            
            self.count_label = QLabel("(0)")
            self.count_label.setFont(QFont("Microsoft YaHei", 10))
            self.count_label.setStyleSheet("color: #666;")
            self.header_layout.addWidget(self.count_label)
            
            self.header_layout.addStretch()
            
            self.clear_button = QPushButton("清空")
            self.clear_button.setFixedSize(50, 25)
            self.clear_button.clicked.connect(self.clear_all_notifications)
            self.header_layout.addWidget(self.clear_button)
            
            self.main_layout.addLayout(self.header_layout)
            
            # 分隔线
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            self.main_layout.addWidget(separator)
            
            # 滚动区域
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarNever)
            
            # 通知列表
            self.notification_list = QWidget()
            self.notification_list_layout = QVBoxLayout(self.notification_list)
            self.notification_list_layout.setContentsMargins(0, 0, 0, 0)
            self.notification_list_layout.setSpacing(5)
            self.notification_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # 空状态标签
            self.empty_label = QLabel("暂无通知")
            self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.empty_label.setStyleSheet("""
                QLabel {
                    color: #999;
                    font-size: 14px;
                    padding: 40px;
                }
            """)
            self.notification_list_layout.addWidget(self.empty_label)
            
            self.scroll_area.setWidget(self.notification_list)
            self.main_layout.addWidget(self.scroll_area)
            
        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")
    
    def init_connections(self):
        """
        初始化信号连接
        """
        try:
            # 连接通知服务信号
            if self.notification_service:
                self.notification_service.notification_sent.connect(self.on_notification_sent)
                self.notification_service.notification_cancelled.connect(self.on_notification_cancelled)
            
        except Exception as e:
            self.logger.error(f"初始化信号连接失败: {e}")
    
    def apply_styles(self):
        """
        应用样式
        """
        try:
            self.setStyleSheet("""
                NotificationWidget {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #f0f0f0;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar:handle:vertical {
                    background-color: #c0c0c0;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar:handle:vertical:hover {
                    background-color: #a0a0a0;
                }
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """)
            
        except Exception as e:
            self.logger.error(f"应用样式失败: {e}")
    
    def load_notifications(self):
        """
        加载通知数据
        """
        try:
            # 这里可以从通知服务获取历史通知
            # 目前先显示空状态
            self.update_display()
            
        except Exception as e:
            self.logger.error(f"加载通知数据失败: {e}")
    
    def on_notification_sent(self, notification_id: str):
        """
        新通知发送处理
        
        Args:
            notification_id: 通知ID
        """
        try:
            # 从通知服务获取通知详情
            # 这里需要通知服务提供获取通知详情的方法
            # 暂时跳过具体实现
            self.update_display()
            
        except Exception as e:
            self.logger.error(f"处理新通知失败: {e}")
    
    def on_notification_cancelled(self, notification_id: str):
        """
        通知取消处理
        
        Args:
            notification_id: 通知ID
        """
        try:
            if notification_id in self.notification_items:
                item = self.notification_items[notification_id]
                self.notification_list_layout.removeWidget(item)
                item.deleteLater()
                del self.notification_items[notification_id]
                
                self.update_display()
            
        except Exception as e:
            self.logger.error(f"处理通知取消失败: {e}")
    
    def add_notification(self, notification: NotificationRequest):
        """
        添加通知
        
        Args:
            notification: 通知请求对象
        """
        try:
            # 创建通知项
            item = NotificationItem(notification)
            item.dismiss_requested.connect(self.dismiss_notification)
            item.action_clicked.connect(self.notification_action_clicked.emit)
            
            # 添加到列表
            self.notification_items[notification.id] = item
            
            # 根据优先级插入到合适位置
            insert_index = 0
            for i in range(self.notification_list_layout.count()):
                widget = self.notification_list_layout.itemAt(i).widget()
                if isinstance(widget, NotificationItem):
                    if widget.notification.priority.value <= notification.priority.value:
                        insert_index = i
                        break
                    insert_index = i + 1
            
            self.notification_list_layout.insertWidget(insert_index, item)
            
            self.update_display()
            
        except Exception as e:
            self.logger.error(f"添加通知失败: {e}")
    
    def dismiss_notification(self, notification_id: str):
        """
        关闭通知
        
        Args:
            notification_id: 通知ID
        """
        try:
            if notification_id in self.notification_items:
                item = self.notification_items[notification_id]
                self.notification_list_layout.removeWidget(item)
                item.deleteLater()
                del self.notification_items[notification_id]
                
                self.notification_dismissed.emit(notification_id)
                self.update_display()
            
        except Exception as e:
            self.logger.error(f"关闭通知失败: {e}")
    
    def clear_all_notifications(self):
        """
        清除所有通知
        """
        try:
            # 移除所有通知项
            for item in self.notification_items.values():
                self.notification_list_layout.removeWidget(item)
                item.deleteLater()
            
            self.notification_items.clear()
            self.clear_all_requested.emit()
            self.update_display()
            
        except Exception as e:
            self.logger.error(f"清除所有通知失败: {e}")
    
    def update_display(self):
        """
        更新显示
        """
        try:
            count = len(self.notification_items)
            
            # 更新计数
            self.count_label.setText(f"({count})")
            
            # 更新清空按钮状态
            self.clear_button.setEnabled(count > 0)
            
            # 显示/隐藏空状态
            self.empty_label.setVisible(count == 0)
            
        except Exception as e:
            self.logger.error(f"更新显示失败: {e}")
    
    def get_notification_count(self) -> int:
        """
        获取通知数量
        
        Returns:
            通知数量
        """
        return len(self.notification_items)
    
    def has_high_priority_notifications(self) -> bool:
        """
        检查是否有高优先级通知
        
        Returns:
            是否有高优先级通知
        """
        try:
            for item in self.notification_items.values():
                if item.notification.priority == NotificationPriority.HIGH:
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"检查高优先级通知失败: {e}")
            return False
    
    def cleanup(self):
        """
        清理资源
        """
        try:
            # 断开通知服务信号连接
            if self.notification_service:
                self.notification_service.notification_sent.disconnect()
                self.notification_service.notification_cancelled.disconnect()
            
            # 清理所有通知项
            self.clear_all_notifications()
            
            self.logger.debug("通知组件清理完成")
            
        except Exception as e:
            self.logger.error(f"清理通知组件失败: {e}")