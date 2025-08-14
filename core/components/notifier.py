import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class NotificationDialog(QDialog):
    """通知对话框 - 用于显示通知消息"""
    
    def __init__(self, title: str, message: str, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 创建标题标签
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建消息标签
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        
        self.setLayout(layout)
        
        # 设置大小
        self.resize(300, 150)
        
    def show_notification(self):
        """显示通知"""
        self.show()
        # 3秒后自动隐藏
        QTimer.singleShot(3000, self.close)


class Notifier:
    """通知器组件 - 管理应用通知，基于ClassIsland的NotificationHostService实现"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notifications = []
        self.is_enabled = True
        
    def enable_notifications(self, enabled: bool):
        """启用/禁用通知"""
        self.is_enabled = enabled
        self.logger.debug(f"通知功能 {'已启用' if enabled else '已禁用'}")
        
    def is_notification_enabled(self):
        """检查通知是否启用"""
        return self.is_enabled
        
    def show_notification(self, title: str, message: str, duration: int = 5000,
                         notification_type: str = "info", callback: Optional[Callable[[], None]] = None) -> None:
        """显示通知"""
        if not self.is_enabled:
            return
            
        # 创建通知
        notification: Dict[str, Any] = {
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now(),
            "duration": duration
        }
        
        self.notifications.append(notification)
        self.logger.info(f"显示通知: {title} - {message}")
        
        # 在主线程中显示通知
        self._show_notification_dialog(title, message, notification_type, callback)
        
    def _show_notification_dialog(self, title: str, message: str, notification_type: str, callback: Optional[Callable[[], None]]) -> None:
        """在主线程中显示通知对话框"""
        # 这里应该使用Qt的主线程机制来显示对话框
        # 简化实现，使用消息框
        try:
            # 创建通知对话框
            dialog = NotificationDialog(title, message)
            dialog.show_notification()
            
            # 如果有回调函数，执行回调
            if callback:
                callback()
                
        except Exception as e:
            self.logger.error(f"显示通知失败: {e}")
            
    def show_info_notification(self, title: str, message: str, duration: int = 5000):
        """显示信息通知"""
        self.show_notification(title, message, duration, "info")
        
    def show_warning_notification(self, title: str, message: str, duration: int = 5000):
        """显示警告通知"""
        self.show_notification(title, message, duration, "warning")
        
    def show_error_notification(self, title: str, message: str, duration: int = 5000):
        """显示错误通知"""
        self.show_notification(title, message, duration, "error")
        
    def cancel_all_notifications(self):
        """取消所有通知"""
        self.notifications.clear()
        self.logger.info("所有通知已取消")
        
    def get_notification_count(self):
        """获取通知数量"""
        return len(self.notifications)
        
    def get_latest_notification(self) -> Optional[Dict[str, Any]]:
        """获取最新通知"""
        if self.notifications:
            return self.notifications[-1]
        return None
        
    def set_notification_sound_enabled(self, enabled: bool):
        """设置通知声音是否启用"""
        self.logger.debug(f"通知声音 {'已启用' if enabled else '已禁用'}")


# 全局通知器实例
notifier = Notifier()

def get_notifier():
    """获取通知器实例"""
    return notifier


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建通知器
    notifier = Notifier()
    
    # 测试通知显示
    notifier.show_info_notification("测试通知", "这是一个测试通知消息")
    notifier.show_warning_notification("警告通知", "这是一个警告通知消息")
    notifier.show_error_notification("错误通知", "这是一个错误通知消息")
    
    print("通知器已创建并测试")
    
    sys.exit(app.exec())
