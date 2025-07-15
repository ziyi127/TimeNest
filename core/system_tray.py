"""
系统托盘管理器 - RinUI版本
"""

import os
import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction


class SystemTrayManager(QObject):
    """系统托盘管理器"""
    
    # 信号定义
    show_main_window = Signal()
    toggle_floating_window = Signal()
    show_settings = Signal()
    show_about = Signal()
    quit_application = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.SystemTrayManager')
        
        # 托盘组件
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.context_menu: Optional[QMenu] = None
        
        # 状态
        self.floating_window_visible = False
        
        # 初始化
        self._init_tray()
        
    def _init_tray(self):
        """初始化系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("系统托盘不可用")
            return False
            
        try:
            self._create_tray_icon()
            self._create_context_menu()
            self._setup_connections()
            
            if self.tray_icon:
                self.tray_icon.show()
                self.logger.info("系统托盘初始化完成")
                return True
                
        except Exception as e:
            self.logger.error(f"系统托盘初始化失败: {e}")
            return False
            
    def _create_tray_icon(self):
        """创建托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标
        icon_path = self._get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 使用系统默认图标
            style = QApplication.style()
            if style:
                icon = style.standardIcon(style.StandardPixmap.SP_ComputerIcon)
                self.tray_icon.setIcon(icon)
        
        # 设置提示文本
        self.tray_icon.setToolTip("TimeNest - 智能时间管理助手")
        
    def _get_icon_path(self) -> Optional[str]:
        """获取图标路径"""
        # 尝试多个可能的图标路径
        possible_paths = [
            "resources/icons/app_icon.png",
            "resources/app_icon.png", 
            "app_icon.png",
            "icon.png"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None
        
    def _create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = QMenu()
        
        # 主窗口控制
        show_action = QAction("📋 显示主窗口", self)
        show_action.triggered.connect(self.show_main_window.emit)
        self.context_menu.addAction(show_action)
        
        self.context_menu.addSeparator()
        
        # 悬浮窗控制
        self.floating_action = QAction("🔲 显示悬浮窗", self)
        self.floating_action.setCheckable(True)
        self.floating_action.triggered.connect(self._on_floating_toggle)
        self.context_menu.addAction(self.floating_action)
        
        self.context_menu.addSeparator()
        
        # 功能菜单
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.show_settings.emit)
        self.context_menu.addAction(settings_action)
        
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self.show_about.emit)
        self.context_menu.addAction(about_action)
        
        self.context_menu.addSeparator()
        
        # 退出
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(self.quit_application.emit)
        self.context_menu.addAction(quit_action)
        
        # 设置菜单
        if self.tray_icon:
            self.tray_icon.setContextMenu(self.context_menu)
            
    def _setup_connections(self):
        """设置信号连接"""
        if self.tray_icon:
            self.tray_icon.activated.connect(self._on_tray_activated)
            
    def _on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window.emit()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.toggle_floating_window.emit()
            
    def _on_floating_toggle(self):
        """悬浮窗切换"""
        self.toggle_floating_window.emit()
        
    def update_floating_status(self, visible: bool):
        """更新悬浮窗状态"""
        self.floating_window_visible = visible
        if self.floating_action:
            self.floating_action.setChecked(visible)
            self.floating_action.setText("🔲 隐藏悬浮窗" if visible else "🔲 显示悬浮窗")
            
    def show_message(self, title: str, message: str, 
                    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                    timeout: int = 5000):
        """显示托盘消息"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)
            self.logger.debug(f"显示托盘消息: {title} - {message}")
            
    def set_tooltip(self, tooltip: str):
        """设置托盘提示文本"""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
            
    def is_visible(self) -> bool:
        """检查托盘是否可见"""
        return self.tray_icon is not None and self.tray_icon.isVisible()
        
    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            
    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            
    def cleanup(self):
        """清理资源"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
        if self.context_menu:
            self.context_menu = None
        self.logger.info("系统托盘已清理")


class TrayNotificationManager(QObject):
    """托盘通知管理器"""
    
    def __init__(self, tray_manager: SystemTrayManager, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.TrayNotificationManager')
        self.tray_manager = tray_manager
        
        # 通知队列
        self.notification_queue = []
        self.current_notification = None
        
        # 定时器
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self._process_notification_queue)
        self.notification_timer.start(1000)  # 每秒检查一次
        
    def add_notification(self, title: str, message: str, 
                        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                        timeout: int = 5000):
        """添加通知到队列"""
        notification = {
            'title': title,
            'message': message,
            'icon': icon,
            'timeout': timeout
        }
        self.notification_queue.append(notification)
        self.logger.debug(f"添加通知到队列: {title}")
        
    def _process_notification_queue(self):
        """处理通知队列"""
        if not self.notification_queue or self.current_notification:
            return
            
        # 取出下一个通知
        notification = self.notification_queue.pop(0)
        self.current_notification = notification
        
        # 显示通知
        self.tray_manager.show_message(
            notification['title'],
            notification['message'],
            notification['icon'],
            notification['timeout']
        )
        
        # 设置清理定时器
        QTimer.singleShot(notification['timeout'] + 1000, self._clear_current_notification)
        
    def _clear_current_notification(self):
        """清理当前通知"""
        self.current_notification = None
        
    def clear_queue(self):
        """清空通知队列"""
        self.notification_queue.clear()
        self.current_notification = None
        self.logger.debug("通知队列已清空")
