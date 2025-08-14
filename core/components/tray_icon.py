from datetime import datetime
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox, QWidget
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, Signal
import sys
import os
import logging
from pathlib import Path

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
    
    def __init__(self, parent: QWidget | None = None):
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
        
    def get_icon_path(self):
        """
        获取图标文件路径，支持跨平台
        
        Returns:
            Path: 图标文件路径
        """
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent
        assets_dir = project_root / "assets"
        
        # 首先尝试使用新创建的时钟图标
        clock_icon_path = assets_dir / "clock_icon.png"
        if clock_icon_path.exists():
            return clock_icon_path
        
        # 尝试多种可能的图标文件名和格式
        possible_icons = [
            "logo.svg", "logo.png", "logo.ico", "logo.icns",
            "icon.svg", "icon.png", "icon.ico", "icon.icns"
        ]
        
        for icon_name in possible_icons:
            icon_path = assets_dir / icon_name
            if icon_path.exists():
                return icon_path
        
        # 如果在assets目录中没有找到，尝试在项目根目录中查找
        for icon_name in possible_icons:
            icon_path = project_root / icon_name
            if icon_path.exists():
                return icon_path
        
        return None

    def setup_icon(self):
        """设置托盘图标"""
        try:
            # 优先使用logo.svg
            project_root = Path(__file__).parent.parent.parent
            assets_dir = project_root / "assets"
            logo_path = assets_dir / "logo.svg"
            
            if logo_path.exists():
                # 使用QPixmap加载SVG文件
                pixmap = QPixmap(str(logo_path))
                if not pixmap.isNull():
                    self.setIcon(QIcon(pixmap))
                    return
                else:
                    self.logger.warning("无法加载logo.svg作为托盘图标，尝试其他图标格式")
                    
            # 如果logo.svg不存在或无法加载，尝试其他图标
            icon_path = self.get_icon_path()
            if icon_path and icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    self.setIcon(QIcon(pixmap))
                    return
                        
            # 使用系统默认图标
            self.logger.warning("无法找到自定义图标，使用系统默认图标")
            if sys.platform == "win32":
                # Windows系统默认图标
                self.setIcon(QIcon.fromTheme("application-x-executable", 
                                           QIcon.fromTheme("application")))
            elif sys.platform == "darwin":
                # macOS系统默认图标
                self.setIcon(QIcon.fromTheme("application-x-executable", 
                                           QIcon.fromTheme("application")))
            else:
                # Linux系统默认图标
                self.setIcon(QIcon.fromTheme("application-x-executable", 
                                           QIcon.fromTheme("application")))
                
        except Exception as e:
            self.logger.warning(f"设置托盘图标时出错: {e}")
            # 使用默认图标
            self.setIcon(self.getDefaultIcon())
            
    def getDefaultIcon(self):
        """
        获取默认图标
        
        Returns:
            QIcon: 默认图标
        """
        # 尝试获取系统默认图标
        icon = QIcon.fromTheme("application-x-executable")
        if icon.isNull():
            icon = QIcon.fromTheme("application")
        if icon.isNull():
            # 如果系统图标不可用，创建一个简单的文本图标
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            icon = QIcon(pixmap)
        return icon
        
    def create_context_menu(self):
        """创建上下文菜单 - 仿ClassIsland菜单结构"""
        menu = QMenu()
        
        # 应用程序标题项
        title_action = QAction("TimeNest", menu)
        title_action.setEnabled(False)  # 灰色显示，不可点击
        menu.addAction(title_action)
        
        # 帮助菜单项
        help_action = QAction("帮助…", menu)
        help_action.triggered.connect(self._show_help)
        menu.addAction(help_action)
        
        menu.addSeparator()
        
        # 显示/隐藏主界面菜单项 - 动态显示
        self.show_action = QAction("显示主界面", menu)
        self.show_action.triggered.connect(self._toggle_main_window_visibility)
        
        self.hide_action = QAction("隐藏主界面", menu)
        self.hide_action.triggered.connect(self._toggle_main_window_visibility)
        
        menu.addAction(self.show_action)
        menu.addAction(self.hide_action)
        
        # 清除全部提醒菜单项
        self.clear_notifications_action = QAction("清除全部提醒", menu)
        self.clear_notifications_action.triggered.connect(self._clear_notifications)
        menu.addAction(self.clear_notifications_action)
        
        menu.addSeparator()
        
        # 档案和设置菜单项
        profiles_action = QAction("编辑档案…", menu)
        profiles_action.triggered.connect(self._open_profiles)
        menu.addAction(profiles_action)
        
        settings_action = QAction("应用设置…", menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        
        # 临时课表和换课菜单项
        temp_class_plan_action = QAction("加载临时课表…", menu)
        temp_class_plan_action.triggered.connect(self._load_temp_class_plan)
        menu.addAction(temp_class_plan_action)
        
        swap_classes_action = QAction("换课…", menu)
        swap_classes_action.triggered.connect(self._swap_classes)
        menu.addAction(swap_classes_action)
        
        menu.addSeparator()
        
        # 重启和退出菜单项
        restart_action = QAction("重启", menu)
        restart_action.triggered.connect(self._restart_application)
        menu.addAction(restart_action)
        
        exit_action = QAction("退出", menu)
        exit_action.triggered.connect(self._exit_application)
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
        crash_test_action.triggered.connect(self._show_crash_test)
        debug_menu.addAction(crash_test_action)
        
        # 添加通知状态显示项
        self.notification_status_action = QAction("无通知", menu)
        self.notification_status_action.setEnabled(False)
        menu.addAction(self.notification_status_action)
        
        # 设置上下文菜单
        self.setContextMenu(menu)
        
        # 更新菜单项可见性
        self.update_menu_visibility()
        
        # 开发者调试菜单项（仅在调试模式下显示）
        if os.environ.get('TIMENEST_DEBUG', '').lower() == 'true':
            menu.addSeparator()
            self.debug_action = QAction("dev_Debug", menu)
            self.debug_action.triggered.connect(self._show_debug_info)
            menu.addAction(self.debug_action)
        
    def update_menu_visibility(self):
        """更新菜单项可见性"""
        # 根据当前窗口状态更新显示/隐藏菜单项
        self.show_action.setVisible(not self.is_main_window_visible)
        self.hide_action.setVisible(self.is_main_window_visible)
        
        # 默认情况下显示清除通知菜单项
        self.clear_notifications_action.setVisible(True)
        
    def _toggle_main_window_visibility(self):
        """切换主窗口可见性"""
        if self.is_main_window_visible:
            self.hide_main_window.emit()
            self.is_main_window_visible = False
            self.show_action.setVisible(True)
            self.hide_action.setVisible(False)
        else:
            self.show_main_window.emit()
            self.is_main_window_visible = True
            self.show_action.setVisible(False)
            self.hide_action.setVisible(True)
            
    def _show_debug_info(self):
        """显示调试信息"""
        debug_info = f"""TimeNest 调试信息:
        
平台: {sys.platform}
Python版本: {sys.version}
PySide6版本: 未知

当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        QMessageBox.information(None, "调试信息", debug_info)
        
    def update_notification_status(self, has_notifications: bool):
        """更新通知状态"""
        self.clear_notifications_action.setVisible(has_notifications)
        
    def on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标时切换主窗口可见性
            self._toggle_main_window_visibility()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            # 中键点击时显示设置
            self._open_settings()
            
    def _show_crash_test(self):
        """显示崩溃测试窗口"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("崩溃测试")
        msg_box.setText("这是一个模拟的崩溃窗口")
        msg_box.setInformativeText("用于测试应用程序的错误处理能力")
        msg_box.setDetailedText("详细错误信息:\n这是一个测试用的模拟错误")
        msg_box.exec()
        
    def show_message(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information, timeout: int = 3000):
        """显示托盘消息"""
        self.showMessage(title, message, icon, timeout)
        
    # 以下方法用于处理托盘菜单项的点击事件
    def _show_help(self):
        """显示帮助"""
        self.show_help.emit()
        
    def _open_settings(self):
        """打开设置"""
        self.open_settings.emit()
        
    def _open_profiles(self):
        """打开档案"""
        self.open_profiles.emit()
        
    def _load_temp_class_plan(self):
        """加载临时课表"""
        self.load_temp_class_plan.emit()
        
    def _swap_classes(self):
        """换课"""
        self.swap_classes.emit()
        
    def _clear_notifications(self):
        """清除通知"""
        self.clear_notifications.emit()
        
    def _restart_application(self):
        """重启应用"""
        # 显示确认对话框
        reply = QMessageBox.question(
            None, 
            "重启确认", 
            "确定要重启TimeNest吗？", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.restart_application.emit()
        
    def _exit_application(self):
        """退出应用"""
        # 显示确认对话框
        reply = QMessageBox.question(
            None, 
            "退出确认", 
            "确定要退出TimeNest吗？", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.exit_application.emit()


def create_tray_icon(parent: QWidget | None = None):
    """创建全局托盘图标实例"""
    global _tray_icon
    if _tray_icon is None:
        # 检查系统是否支持系统托盘
        if QSystemTrayIcon.isSystemTrayAvailable():
            _tray_icon = TrayIcon(parent)
        else:
            logging.warning("系统不支持系统托盘或系统托盘不可用")
            _tray_icon = None
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