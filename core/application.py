import sys
import logging
from typing import List, Tuple, Type, Optional, Any
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow
from ui.profile_window import ProfileWindow
from ui.swap_window import SwapWindow
from ui.temp_class_plan_window import TempClassPlanWindow
from core.services.component_registry import component_registry
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

logger = logging.getLogger(__name__)


class TimeNestApplication:
    """TimeNest应用程序主类 - 仿ClassIsland架构"""
    
    def __init__(self, argv: Optional[List[str]] = None):
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
        
        # 初始化应用程序
        self.init_application(argv or sys.argv)
        
    def init_application(self, argv: List[str]) -> None:
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
        
        logger.info("TimeNest应用程序初始化完成")
        
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
            
    def init_component_registry(self):
        """初始化组件注册服务 - 仿ClassIsland组件注册机制"""
        logger.info("正在注册组件")
        
        # 注册内置组件 - 使用ClassIsland兼容的GUID
        component_mappings: List[Tuple[str, str, Type]] = [
            ("9E1AF71D-8F77-4B21-A342-448787104DD9", "时钟组件", ClockComponent),
            ("DF3F8295-21F6-482E-BADA-FA0E5F14BB66", "日期组件", DateComponent),
            ("1DB2017D-E374-4BC6-9D57-0B4ADF03A6B8", "课程表组件", ScheduleComponent),
            ("EE8F66BD-C423-4E7C-AB46-AA9976B00E08", "文本组件", TextComponent),
            ("A1B2C3D4-E5F6-7890-ABCD-EF1234567890", "天气组件", WeatherComponent),
            ("F0E1D2C3-B4A5-6789-0123-456789ABCDEF", "倒计时组件", CountDownComponent),
            ("12345678-90AB-CDEF-1234-567890ABCDEF", "滚动组件", RollingComponent),
            ("ABCDEF12-3456-7890-ABCD-EF1234567890", "分组组件", GroupComponent),
            ("SLIDE123-4567-8901-2345-678901234567", "幻灯片组件", SlideComponent),
            ("SEP12345-6789-0123-4567-890123456789", "分割线组件", SeparatorComponent),
        ]
        
        registered_count = 0
        for guid, name, component_class in component_mappings:
            # 为循环变量添加类型注解
            guid: str
            name: str
            component_class: Type
            try:
                component_info = self.component_registry.get_component_info(guid)
                if component_info:
                    component_info.component_type = component_class
                    component_info.name = name
                    logger.info(f"已注册组件: {name} ({guid})")
                    registered_count += 1
                else:
                    logger.warning(f"无法获取组件信息: {name} ({guid})")
            except Exception as e:
                logger.error(f"注册组件 {name} 时发生错误: {e}")
        
        # 确保所有组件类型都已正确设置
        # 使用公共方法注册组件，如果没有公共方法则保持原样
        # 使用类型: ignore注释忽略私有方法使用警告
        self.component_registry._register_builtin_components()  # type: ignore
        logger.info(f"组件注册完成，共注册 {registered_count} 个组件，总组件数: {len(self.component_registry.registered_components)}")
        
        # 为组件注册设置信号连接
        # 为信号连接添加类型注解
        self.component_registry.component_added.connect(self.on_component_added)  # type: ignore
        self.component_registry.component_removed.connect(self.on_component_removed)  # type: ignore
            
    def init_main_window(self):
        """初始化主窗口"""
        logger.info("正在初始化主窗口")
        self.main_window = MainWindow(
            lessons_service=self.lessons_service,
            exact_time_service=self.time_service,
        )
        
        # 连接主窗口信号
        if self.main_window:
            self.main_window.windowStateChanged.connect(self.on_main_window_state_changed)
            
        logger.info("主窗口初始化完成")
        
    def init_tray_icon(self):
        """初始化系统托盘图标"""
        logger.info("正在初始化系统托盘图标")
        try:
            # 传递None作为parent，因为create_tray_icon需要QWidget类型
            self.tray_icon = create_tray_icon(None)
            
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
        """显示主窗口"""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            # 不再激活窗口，避免干扰用户当前操作
            # self.main_window.activateWindow()
            
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
        """打开设置窗口"""
        logger.info("打开应用设置")
        # 创建或显示设置窗口
        if self.tray_icon:
            self.tray_icon.show_message("应用设置", "正在打开设置窗口...")
            
        try:
            if self.settings_window is None:
                self.settings_window = SettingsWindow(self.main_window)
                
            self.settings_window.show()
            self.settings_window.raise_()
            # 不再激活窗口，避免干扰用户当前操作
            # self.settings_window.activateWindow()
        except Exception as e:
            logger.error(f"打开设置窗口时出错: {e}")
            
    def open_profiles(self):
        """打开档案编辑窗口"""
        logger.info("打开档案编辑")
        # 创建或显示档案编辑窗口
        if self.tray_icon:
            self.tray_icon.show_message("编辑档案", "正在打开档案编辑窗口...")
            
        try:
            if self.profile_window is None:
                self.profile_window = ProfileWindow(self.main_window)
                
            self.profile_window.show()
            self.profile_window.raise_()
            # 不再激活窗口，避免干扰用户当前操作
            # self.profile_window.activateWindow()
        except Exception as e:
            logger.error(f"打开档案编辑窗口时出错: {e}")
            
    def restart_application(self):
        """重启应用程序"""
        logger.info("用户请求重启应用程序")
        try:
            # 仿ClassIsland方式重启应用
            if self.tray_icon:
                self.tray_icon.show_message("重启应用", "正在重启TimeNest...")
            # 先关闭当前应用
            self.shutdown()
            # 重新启动应用程序
            import subprocess
            import sys
            # 使用跨平台方式启动进程
            if sys.platform == "win32":
                # Windows平台 - 使用CREATE_NO_WINDOW标志实现静默运行
                subprocess.Popen([sys.executable] + sys.argv, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Unix/Linux/macOS平台
                subprocess.Popen([sys.executable] + sys.argv)
            if self.app:
                self.app.quit()
        except Exception as e:
            logger.error(f"重启应用程序时出错: {e}")
            
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
        """加载临时课表"""
        logger.info("加载临时课表")
        # 创建或显示临时课表窗口
        if self.tray_icon:
            self.tray_icon.show_message("临时课表", "正在打开临时课表窗口...")
            
        try:
            if self.temp_class_plan_window is None:
                self.temp_class_plan_window = TempClassPlanWindow(self.main_window)
                
            self.temp_class_plan_window.show()
            self.temp_class_plan_window.raise_()
            # 不再激活窗口，避免干扰用户当前操作
            # self.temp_class_plan_window.activateWindow()
        except Exception as e:
            logger.error(f"打开临时课表窗口时出错: {e}")
            
    def swap_classes(self):
        """换课功能"""
        logger.info("换课功能")
        # 创建或显示换课窗口
        if self.tray_icon:
            self.tray_icon.show_message("换课", "正在打开换课窗口...")
            
        try:
            if self.swap_window is None:
                self.swap_window = SwapWindow(self.main_window)
                
            self.swap_window.show()
            self.swap_window.raise_()
            # 不再激活窗口，避免干扰用户当前操作
            # self.swap_window.activateWindow()
        except Exception as e:
            logger.error(f"打开换课窗口时出错: {e}")
            
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
        if self.main_window:
            logger.info("显示主窗口")
            self.main_window.show()
            
        # 运行应用程序事件循环
        if self.app:
            logger.info("启动应用程序事件循环")
            return self.app.exec()
            
    def shutdown(self):
        """关闭应用程序"""
        logger.info("正在关闭应用程序")
        try:
            # 清理所有窗口
            if self.settings_window:
                self.settings_window.close()
                self.settings_window = None
                
            if self.profile_window:
                self.profile_window.close()
                self.profile_window = None
                
            if self.swap_window:
                self.swap_window.close()
                self.swap_window = None
                
            if self.temp_class_plan_window:
                self.temp_class_plan_window.close()
                self.temp_class_plan_window = None
                
            # 隐藏主窗口
            if self.main_window:
                self.main_window.hide()
                
            # 隐藏托盘图标
            if self.tray_icon:
                self.tray_icon.hide()
                
        except Exception as e:
            logger.error(f"关闭应用程序时出错: {e}")
            
        logger.info("应用程序已关闭")
        
    def on_component_added(self, component_info: Any) -> None:
        """处理组件添加事件"""
        logger.info(f"组件已添加: {component_info.name}")
        # 可以在这里添加组件添加后的逻辑，比如更新UI等
        
    def on_component_removed(self, component_info: Any) -> None:
        """处理组件移除事件"""
        logger.info(f"组件已移除: {component_info.name}")
        # 可以在这里添加组件移除后的逻辑


def main(argv: Optional[List[str]] = None):
    """应用程序入口点"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 创建并运行应用程序
        app = TimeNestApplication(argv)
        exit_code = app.run()
        app.shutdown()
        return exit_code
    except Exception as e:
        logger.error(f"运行应用程序时出错: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main(sys.argv)
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"应用程序启动时出错: {e}")
        sys.exit(1)