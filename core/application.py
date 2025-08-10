import sys
import logging
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QCoreApplication, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint
from PySide6.QtGui import QScreen

from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow
from ui.profile_window import ProfileWindow
from ui.swap_window import SwapWindow
from ui.temp_class_plan_window import TempClassPlanWindow
from core.services.component_registry import ComponentRegistryService, component_registry
from core.services.time_service import TimeService
from core.services.lessons_service import LessonsService
from core.models.profile import TimeNestProfile
from core.components.clock_component import ClockComponent
from core.components.date_component import DateComponent
from core.components.schedule_component import ScheduleComponent
from core.components.text_component import TextComponent
from core.components.weather_component import WeatherComponent
from core.components.countdown_component import CountDownComponent
from core.components.rolling_component import RollingComponent
from core.components.group_component import GroupComponent
from core.components.slide_component import SlideComponent
from core.components.separator_component import SeparatorComponent
from core.components.tray_icon import create_tray_icon
from core.components.user_preferences import user_preferences

logger = logging.getLogger(__name__)


class TimeNestApplication:
    """TimeNest应用程序主类 - 仿ClassIsland架构"""
    
    def __init__(self, argv=None):
        self.app = None
        self.main_window = None
        self.settings_window = None
        self.profile_window = None
        self.swap_window = None
        self.temp_class_plan_window = None
        self.tray_icon = None
        self.component_registry = component_registry
        self.time_service = TimeService()
        self.profile_service = None
        self.lessons_service = None
        self.window_animation = None  # 窗口动画管理器
        
        # 初始化应用程序
        self.init_application(argv or sys.argv)
        
    def init_application(self, argv):
        """初始化应用程序"""
        logger.info("正在初始化TimeNest应用程序")
        
        # 检查是否已有QApplication实例
        self.app = QApplication.instance()
        if self.app is None:
            # 创建Qt应用程序
            self.app = QApplication(argv)
            self.app.setApplicationName("TimeNest")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("TimeNest")
            self.app.setOrganizationDomain("ziyi127.github.io")
            
            # 设置应用程序属性
            self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        else:
            logger.info("使用现有的QApplication实例")
        
        # 初始化服务
        self.init_services()
        
        # 初始化组件注册服务
        self.init_component_registry()
        
        # 初始化主窗口
        self.init_main_window()
        
        # 初始化托盘图标
        self.init_tray_icon()
        
        # 连接主题变化信号
        theme_manager.theme_changed_signal.connect(self.on_theme_changed)
        
        # 初始化窗口动画
        self.init_window_animation()
        
        logger.info("TimeNest应用程序初始化完成")
        
    def init_window_animation(self):
        """初始化窗口动画效果"""
        logger.info("正在初始化窗口动画效果")
        # 创建通用窗口动画
        self.window_animation = WindowAnimationManager()
        
    def init_services(self):
        """初始化核心服务"""
        logger.info("正在初始化核心服务")
        
        try:
            # 初始化档案服务
            self.profile_service = TimeNestProfile("默认档案")
            
            # 初始化课程服务
            self.lessons_service = LessonsService(
                exact_time_service=self.time_service,
                profile_service=self.profile_service
            )
            
            logger.info("核心服务初始化完成")
        except Exception as e:
            logger.error(f"初始化核心服务时发生错误: {e}")
            # 启用基本服务作为后备
            self.profile_service = None
            self.lessons_service = None
            # 记录错误并继续运行
            logger.warning("使用基本服务模式运行应用")
        
    def init_component_registry(self):
        """初始化组件注册服务 - 仿ClassIsland组件注册机制"""
        logger.info("正在注册组件")
        
        # 定义内置组件映射 - 使用ClassIsland兼容的GUID
        component_mappings = {
            "9E1AF71D-8F77-4B21-A342-448787104DD9": {"name": "时钟组件", "type": ClockComponent},
            "DF3F8295-21F6-482E-BADA-FA0E5F14BB66": {"name": "日期组件", "type": DateComponent},
            "1DB2017D-E374-4BC6-9D57-0B4ADF03A6B8": {"name": "课程表组件", "type": ScheduleComponent},
            "EE8F66BD-C423-4E7C-AB46-AA9976B00E08": {"name": "文本组件", "type": TextComponent},
            "A1B2C3D4-E5F6-7890-ABCD-EF1234567890": {"name": "天气组件", "type": WeatherComponent},
            "F0E1D2C3-B4A5-6789-0123-456789ABCDEF": {"name": "倒计时组件", "type": CountDownComponent},
            "12345678-90AB-CDEF-1234-567890ABCDEF": {"name": "滚动组件", "type": RollingComponent},
            "ABCDEF12-3456-7890-ABCD-EF1234567890": {"name": "分组组件", "type": GroupComponent},
            "SLIDE123-4567-8901-2345-678901234567": {"name": "幻灯片组件", "type": SlideComponent},
            "SEP12345-6789-0123-4567-890123456789": {"name": "分割线组件", "type": SeparatorComponent},
        }
        
        # 注册所有组件
        registered_count = 0
        for guid, component_info in component_mappings.items():
            component = self.component_registry.get_component_info(guid)
            if component:
                component.component_type = component_info["type"]
                component.name = component_info["name"]
                logger.info(f"已注册组件: {component_info['name']} ({guid})")
                registered_count += 1
            else:
                logger.warning(f"无法找到组件: {component_info['name']} ({guid})")
        
        # 确保所有组件类型都已正确设置
        self.component_registry._register_builtin_components()
        logger.info(f"组件注册完成，共注册 {registered_count} 个组件，总组件数: {len(self.component_registry.registered_components)}")
        
        # 连接组件事件处理
        self.component_registry.component_added.connect(self.on_component_added)
        self.component_registry.component_removed.connect(self.on_component_removed)
            
    def init_main_window(self):
        """初始化主窗口"""
        logger.info("正在初始化主窗口")
        self.main_window = MainWindow(
            lessons_service=self.lessons_service,
            exact_time_service=self.time_service,
            profile_service=self.profile_service
        )
        
        # 连接主窗口信号
        if self.main_window:
            self.main_window.windowStateChanged.connect(self.on_main_window_state_changed)
            
        logger.info("主窗口初始化完成")
        
    def init_tray_icon(self):
        """初始化系统托盘图标"""
        logger.info("正在初始化系统托盘图标")
        try:
            self.tray_icon = create_tray_icon(self.app)
            
            # 连接托盘图标信号
            if self.tray_icon:
                self.tray_icon.show_main_window.connect(self.show_main_window)
                self.tray_icon.hide_main_window.connect(self.hide_main_window)
                self.tray_icon.exit_application.connect(self.exit_application)
                self.tray_icon.open_settings.connect(self.open_settings)
                self.tray_icon.open_profiles.connect(self.open_profiles)
                self.tray_icon.restart_application.connect(self.restart_application)
                self.tray_icon.show_help.connect(self.show_help)
                self.tray_icon.load_temp_class_plan.connect(self.load_temp_class_plan)
                self.tray_icon.swap_classes.connect(self.swap_classes)
                self.tray_icon.clear_notifications.connect(self.clear_notifications)
                
            logger.info("系统托盘图标初始化完成")
        except Exception as e:
            logger.error(f"初始化系统托盘图标时出错: {e}")
            
    def on_main_window_state_changed(self, visible: bool):
        """主窗口状态改变回调"""
        if self.tray_icon:
            self.tray_icon.is_main_window_visible = visible
            self.tray_icon.update_menu_visibility()
        
    def show_main_window(self):
        """显示主窗口 - 带有动画效果"""
        if self.main_window:
            self.window_animation.animate_show(self.main_window)
            
    def hide_main_window(self):
        """隐藏主窗口 - 带有动画效果"""
        if self.main_window:
            self.window_animation.animate_hide(self.main_window)
            
    def toggle_main_window_minimize(self):
        """切换主窗口最小化状态 - 带有动画效果"""
        if self.main_window:
            self.window_animation.animate_minimize(self.main_window)
            
    def center_window(self, window: QWidget):
        """将窗口居中显示"""
        if window:
            screen = self.app.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                window_geometry = window.frameGeometry()
                center_point = screen_geometry.center()
                window_geometry.moveCenter(center_point)
                window.move(window_geometry.topLeft())
                
    def animate_window_transition(self, old_window: QWidget, new_window: QWidget):
        """窗口切换动画效果"""
        if old_window and new_window:
            self.window_animation.animate_window_transition(old_window, new_window)
            
    def hide_main_window(self):
        """隐藏主窗口"""
        if self.main_window:
            self.main_window.hide()
            
    def exit_application(self):
        """退出应用程序"""
        logger.info("用户请求退出应用程序")
        self.shutdown()
        if self.app:
            self.app.quit()
            
    def open_settings(self):
        """打开设置窗口 - 带有动画和过渡效果"""
        logger.info("打开应用设置")
        # 创建或显示设置窗口
        if self.tray_icon:
            self.tray_icon.show_message("应用设置", "正在打开设置窗口...")
            
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.main_window)
            # 居中显示
            self.center_window(self.settings_window)
        else:
            # 如果已经存在，先隐藏再显示
            self.window_animation.animate_hide(self.settings_window)
            
        # 如果有其他窗口打开，执行窗口切换动画
        if self.profile_window and self.profile_window.isVisible():
            self.animate_window_transition(self.profile_window, self.settings_window)
        else:
            # 否则直接显示设置窗口
            self.window_animation.animate_show(self.settings_window)
            
        self.settings_window.raise_()
        self.settings_window.activateWindow()
            
    def open_profiles(self):
        """打开档案窗口 - 带有动画和过渡效果"""
        logger.info("打开档案管理")
        if self.tray_icon:
            self.tray_icon.show_message("档案管理", "正在打开档案管理窗口...")
            
        if self.profile_window is None:
            self.profile_window = ProfileWindow(self.main_window)
            # 居中显示
            self.center_window(self.profile_window)
        else:
            # 如果已经存在，先隐藏再显示
            self.window_animation.animate_hide(self.profile_window)
            
        # 如果有其他窗口打开，执行窗口切换动画
        if self.settings_window and self.settings_window.isVisible():
            self.animate_window_transition(self.settings_window, self.profile_window)
        else:
            # 否则直接显示档案窗口
            self.window_animation.animate_show(self.profile_window)
            
        self.profile_window.raise_()
        self.profile_window.activateWindow()
            
    def restart_application(self):
        """重启应用程序"""
        logger.info("用户请求重启应用程序")
        if self.tray_icon:
            self.tray_icon.show_message("重启应用", "正在重启TimeNest...")
            
        # 保存当前应用程序参数
        argv = sys.argv
        
        # 关闭应用程序
        self.shutdown()
        
        # 重新启动应用程序
        import subprocess
        subprocess.Popen([sys.executable] + argv)
        
        # 退出当前实例
        if self.app:
            self.app.quit()
            
    def show_help(self):
        """显示帮助"""
        logger.info("显示帮助")
        # 仿ClassIsland方式显示帮助
        import webbrowser
        try:
            webbrowser.open("https://ziyi127.github.io/TimeNest-Website")
            if self.tray_icon:
                self.tray_icon.show_message("帮助文档", "正在打开在线帮助文档...")
        except Exception as e:
            logger.error(f"打开帮助文档失败: {e}")
            if self.tray_icon:
                self.tray_icon.show_message("帮助文档", "无法打开帮助文档")
            
    def load_temp_class_plan(self):
        """加载临时课表 - 带有动画效果"""
        logger.info("加载临时课表")
        if self.tray_icon:
            self.tray_icon.show_message("临时课表", "正在加载临时课表...")
            
        if self.temp_class_plan_window is None:
            self.temp_class_plan_window = TempClassPlanWindow(self.main_window)
            # 居中显示
            self.center_window(self.temp_class_plan_window)
        else:
            # 如果已经存在，先隐藏再显示
            self.window_animation.animate_hide(self.temp_class_plan_window)
            
        # 显示窗口
        self.window_animation.animate_show(self.temp_class_plan_window)
        self.temp_class_plan_window.raise_()
        self.temp_class_plan_window.activateWindow()
            
    def swap_classes(self):
        """换课功能 - 带有动画效果"""
        logger.info("打开换课界面")
        if self.tray_icon:
            self.tray_icon.show_message("换课", "正在打开换课界面...")
            
        if self.swap_window is None:
            self.swap_window = SwapWindow(self.main_window)
            # 居中显示
            self.center_window(self.swap_window)
        else:
            # 如果已经存在，先隐藏再显示
            self.window_animation.animate_hide(self.swap_window)
            
        # 显示窗口
        self.window_animation.animate_show(self.swap_window)
        self.swap_window.raise_()
        self.swap_window.activateWindow()
            
    def clear_notifications(self):
        """清除通知"""
        logger.info("清除通知")
        # 仿ClassIsland方式清除所有通知
        if self.tray_icon:
            self.tray_icon.show_message("清除通知", "正在清除所有提醒...")
            # TODO: 实现真正的通知清除功能
            # 这里应该调用通知服务清除所有通知
            # 暂时显示主窗口作为替代
            self.show_main_window()
        
    def run(self):
        """运行应用程序"""
        logger.info("正在启动TimeNest应用程序")
        
        # 显示主窗口
        if self.main_window:
            self.main_window.show()
        
        # 运行应用程序事件循环
        if self.app:
            return self.app.exec()
        return 0
            
    def shutdown(self):
        """关闭应用程序"""
        logger.info("正在关闭TimeNest应用程序")
        # 在这里可以添加清理逻辑（如保存配置、释放资源等）
        
    def on_component_added(self, component_info):
        """处理组件添加事件"""
        logger.info(f"组件已添加: {component_info.name}")
        # 可以在这里添加组件添加后的逻辑，比如更新UI等
        
    def on_component_removed(self, component_info):
        """处理组件移除事件"""
        logger.info(f"组件已移除: {component_info.name}")
        # 可以在这里添加组件移除后的逻辑


def main(argv=None):
    """应用程序入口点"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建并运行应用程序
    app = TimeNestApplication(argv)
    exit_code = app.run()
    app.shutdown()
    return exit_code


if __name__ == "__main__":
    exit_code = main(sys.argv)
    sys.exit(exit_code)
