#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知窗口
弹窗通知的UI实现
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen


class NotificationWindow(QWidget):
    """
    通知窗口类
    
    显示弹窗通知的UI组件
    """
    
    # 信号定义
    closed = pyqtSignal()  # 窗口关闭信号
    clicked = pyqtSignal()  # 窗口点击信号
    
    def __init__(self, title: str = "", message: str = "", duration: int = 5000, **kwargs):
        """
        初始化通知窗口
        
        Args:
            title: 通知标题
            message: 通知消息
            duration: 显示时长（毫秒）
            **kwargs: 其他参数
        """
        super().__init__()
        
        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.NotificationWindow')
        
        # 参数
        self.title = title
        self.message = message
        self.duration = duration
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 初始化UI
        self._init_ui()
        
        # 自动关闭定时器
        if duration > 0:
            QTimer.singleShot(duration, self.close)
    
    def _init_ui(self):
        """初始化UI"""
        # 设置固定大小
        self.setFixedSize(300, 100)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题标签
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #333; margin-bottom: 5px;")
            layout.addWidget(title_label)
        
        # 消息标签
        if self.message:
            message_label = QLabel(self.message)
            message_label.setFont(QFont("Arial", 10))
            message_label.setStyleSheet("color: #666;")
            message_label.setWordWrap(True)
            layout.addWidget(message_label)
        
        # 关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        close_button.clicked.connect(self.close)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            rect = self.rect()
            painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawRoundedRect(rect, 10, 10)
        finally:
            painter.end()
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def closeEvent(self, event):
        """关闭事件"""
        self.closed.emit()
        super().closeEvent(event)
    
    def apply_theme(self, theme_colors: Dict[str, Any]):
        """应用主题"""
        # 简单的主题应用实现
        pass
    
    def show_at_position(self, x: int, y: int):
        """在指定位置显示"""
        self.move(x, y)
        self.show()
    
    def show_at_corner(self, corner: str = "top-right"):
        """在屏幕角落显示"""
        from PyQt6.QtWidgets import QApplication
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            
            if corner == "top-right":
                x = screen_rect.width() - self.width() - 20
                y = 20
            elif corner == "top-left":
                x = 20
                y = 20
            elif corner == "bottom-right":
                x = screen_rect.width() - self.width() - 20
                y = screen_rect.height() - self.height() - 20
            elif corner == "bottom-left":
                x = 20
                y = screen_rect.height() - self.height() - 20
            else:
                x = screen_rect.width() - self.width() - 20
                y = 20
            
            self.show_at_position(x, y)
        else:
            self.show()


# 测试函数
def test_notification_window():
    """测试通知窗口"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建通知窗口
    notification = NotificationWindow(
        title="测试通知",
        message="这是一个测试通知消息",
        duration=3000
    )
    
    # 显示在右上角
    notification.show_at_corner("top-right")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_notification_window()
