import logging
from datetime import datetime
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, Signal
import sys
import os
from core.components.theme_manager import theme_manager

# 全局托盘图标实例
_tray_icon = None


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标类 - 仿ClassIsland样式"""
    
    # 定义信号 - 对应ClassIsland的菜单项
    show_main_window = Signal()
    hide_main_window = Signal()
    exit_application = Signal()
    open_settings = Signal()
    open_profiles = Signal()
    clear_notifications = Signal()
    restart_application = Signal()
    show_help = Signal()
    load_temp_class_plan = Signal()
    swap_classes = Signal()
    minimize_window = Signal()  # 新增最小化窗口信号
    restore_window = Signal()   # 新增恢复窗口信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.is_main_window_visible = True
        self.init_tray()
        
    def init_tray(self):
        """初始化托盘图标 - 仿ClassIsland菜单结构"""
        # 设置托盘图标
        self.setup_icon()
        
        # 创建右键菜单 - 严格按照ClassIsland的菜单结构
        self.create_context_menu()
        
        # 连接激活信号
        self.activated.connect(self.on_activated)
        
        # 显示托盘图标
        self.setVisible(True)
        
    def setup_icon(self):
        """设置托盘图标"""
        try:
            # 尝试使用应用程序图标
            if os.path.exists("assets/logo.svg"):
                pixmap = QPixmap("assets/logo.svg")
                if not pixmap.isNull():
                    self.setIcon(QIcon(pixmap))
                    return
                    
            # 尝试使用文本图标
            if os.path.exists("assets/logo.txt"):
                pixmap = QPixmap("assets/logo.txt")
                if not pixmap.isNull():
                    self.setIcon(QIcon(pixmap))
                    return
                    
            # 使用系统默认图标
            self.setIcon(QIcon.fromTheme("application-x-executable"))
            
        except Exception as e:
            self.logger.warning(f"设置托盘图标时出错: {e}")
            # 使用默认图标
            self.setIcon(QIcon.fromTheme("application-x-executable"))
        
    def create_context_menu(self):
        """创建上下文菜单 - 仿ClassIsland菜单结构"""
        menu = QMenu()
        
        # 应用程序标题项
        title_action = QAction("TimeNest", menu)
        title_action.setEnabled(False)  # 灰色显示，不可点击
        menu.addAction(title_action)
        
        # 帮助菜单项
        help_action = QAction("帮助…", menu)
        help_action.triggered.connect(self.show_help.emit)
        menu.addAction(help_action)
        
        menu.addSeparator()
        
        # 显示/隐藏主界面菜单项 - 动态显示
        self.show_action = QAction("显示主界面", menu)
        self.show_action.triggered.connect(self.toggle_main_window_visibility)
        
        self.hide_action = QAction("隐藏主界面", menu)
        self.hide_action.triggered.connect(self.toggle_main_window_visibility)
        
        menu.addAction(self.show_action)
        menu.addAction(self.hide_action)
        
        # 最小化/恢复主窗口菜单项
        self.minimize_action = QAction("最小化主窗口", menu)
        self.minimize_action.triggered.connect(self.minimize_window.emit)
        menu.addAction(self.minimize_action)
        
        self.restore_action = QAction("恢复主窗口", menu)
        self.restore_action.triggered.connect(self.restore_window.emit)
        menu.addAction(self.restore_action)
        
        # 清除全部提醒菜单项
        self.clear_notifications_action = QAction("清除全部提醒", menu)
        self.clear_notifications_action.triggered.connect(self.clear_notifications.emit)
        menu.addAction(self.clear_notifications_action)
        
        menu.addSeparator()
        
        # 档案和设置菜单项
        profiles_action = QAction("编辑档案…", menu)
        profiles_action.triggered.connect(self.open_profiles.emit)
        menu.addAction(profiles_action)
        
        settings_action = QAction("应用设置…", menu)
        settings_action.triggered.connect(self.open_settings.emit)
        menu.addAction(settings_action)
        
        # 临时课表和换课菜单项
        temp_class_plan_action = QAction("加载临时课表…", menu)
        temp_class_plan_action.triggered.connect(self.load_temp_class_plan.emit)
        menu.addAction(temp_class_plan_action)
        
        swap_classes_action = QAction("换课…", menu)
        swap_classes_action.triggered.connect(self.swap_classes.emit)
        menu.addAction(swap_classes_action)
        
        menu.addSeparator()
        
        # 重启和退出菜单项
        restart_action = QAction("重启", menu)
        restart_action.triggered.connect(self.restart_application.emit)
        menu.addAction(restart_action)
        
        exit_action = QAction("退出", menu)
        exit_action.triggered.connect(self.exit_application.emit)
        menu.addAction(exit_action)
        
        menu.addSeparator()
        
        # 调试菜单项
        debug_menu = menu.addMenu("dev_Debug")
        
        dev_tools_action = QAction("DevTools", debug_menu)
        dev_tools_action.triggered.connect(lambda: self.show_message("调试", "DevTools功能"))
        debug_menu.addAction(dev_tools_action)
        
        dev_portal_action = QAction("DevPortal", debug_menu)
        dev_portal_action.triggered.connect(lambda: self.show_message("调试", "DevPortal功能"))
        debug_menu.addAction(dev_portal_action)
        
        debug_menu.addSeparator()
        
        enable_temp_plan_action = QAction("启用课表", debug_menu)
        enable_temp_plan_action.triggered.connect(lambda: self.show_message("调试", "启用临时课表功能"))
        debug_menu.addAction(enable_temp_plan_action)
        
        crash_test_action = QAction("显示崩溃窗口", debug_menu)
        crash_test_action.triggered.connect(self.show_crash_test)
        debug_menu.addAction(crash_test_action)
        
        # 添加通知状态显示项
        self.notification_status_action = QAction("无通知", menu)
        self.notification_status_action.setEnabled(False)
        menu.addAction(self.notification_status_action)
        
        # 设置上下文菜单
        self.setContextMenu(menu)
        
        # 更新菜单项可见性
        self.update_menu_visibility()
        
        # 初始化通知状态
        self.update_notification_status(False)
        
    def toggle_main_window_visibility(self):
        """切换主窗口可见性"""
        if self.is_main_window_visible:
            self.hide_main_window.emit()
            self.is_main_window_visible = False
        else:
            self.show_main_window.emit()
            self.is_main_window_visible = True
            
        # 更新菜单项显示
        self.update_menu_visibility()
        
    def update_menu_visibility(self):
        """更新菜单项可见性"""
        # 根据主窗口状态显示相应的菜单项
        self.show_action.setVisible(not self.is_main_window_visible)
        self.hide_action.setVisible(self.is_main_window_visible)
        
        # 总是显示最小化菜单项（由窗口管理器决定是否可用）
        self.minimize_action.setVisible(True)
        self.restore_action.setVisible(True)
        
    def update_notification_status(self, has_notifications: bool):
        """更新通知状态"""
        self.clear_notifications_action.setVisible(has_notifications)
        
    def on_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标时切换主窗口可见性
            self.toggle_main_window_visibility()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            # 中键点击时最小化窗口
            self.minimize_window.emit()
            
    def show_crash_test(self):
        """显示崩溃测试窗口"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("崩溃测试")
        msg_box.setText("这是一个模拟的崩溃窗口")
        msg_box.setInformativeText("用于测试应用程序的错误处理能力")
        msg_box.setDetailedText("详细错误信息:\n这是一个测试用的模拟错误")
        msg_box.exec()
        
    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information, timeout=3000):
        """显示托盘消息"""
        self.showMessage(title, message, icon, timeout)


def create_tray_icon(parent=None):
    """创建托盘图标实例"""
    global _tray_icon
    if _tray_icon is None:
        _tray_icon = TrayIcon(parent)
    return _tray_icon


def get_tray_icon():
    """获取托盘图标实例"""
    global _tray_icon
    return _tray_icon


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建托盘图标
    tray_icon = TrayIcon()
    tray_icon.show()
    
    print("托盘图标已创建")
    
    sys.exit(app.exec())
