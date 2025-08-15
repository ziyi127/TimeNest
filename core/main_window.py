# TimeNest 主窗口
# 完整重构自Classisland的MainWindow类

import logging
from datetime import datetime
from typing import Any, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QHideEvent, QIcon, QKeySequence, QShowEvent
from PySide6.QtWidgets import QMainWindow, QStatusBar, QToolBar, QVBoxLayout, QWidget

from core.components.base_component import (
    BaseComponent,
    TimeNestClockComponent,
    TimeNestDateComponent,
    TimeNestScheduleComponent,
)
from core.services.time_service import get_time_service
from core.settings import TimeNestSettings

logger = logging.getLogger(__name__)


class TimeNestMainWindow(QMainWindow):
    """TimeNest主窗口类"""

    # 窗口状态信号
    window_visibility_changed = Signal(bool)

    def __init__(self, settings: TimeNestSettings):
        """
        初始化主窗口

        Args:
            settings: 应用设置实例
        """
        super().__init__()

        self.settings = settings
        self.time_service = get_time_service()

        # 初始化组件列表
        self.components: List[BaseComponent] = []

        # 设置窗口属性
        self._setup_window()

        # 创建界面
        self._create_ui()

        # 初始化组件
        self._initialize_components()

        # 连接信号
        self._connect_signals()

        logger.info("TimeNest主窗口已初始化")

    def _setup_window(self):
        """设置窗口属性"""
        # 窗口标题
        self.setWindowTitle("TimeNest")
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))  # 后续实现图标

        # 窗口大小
        self.resize(800, 600)
        self.setMinimumSize(600, 400)

        # 设置窗口标志
        self.setWindowFlags(Qt.WindowType.Window)

        # 设置窗口位置和大小
        self._restore_window_state()

    def _create_ui(self):
        """创建用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建工具栏
        self._create_toolbar()

        # 创建菜单栏
        self._create_menubar()

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 创建主内容区域（后续实现）
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # 添加一些占位内容
        from PySide6.QtWidgets import QLabel

        placeholder_label = QLabel("TimeNest 主界面内容区域")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(placeholder_label)

        main_layout.addWidget(content_widget)

        logger.debug("主窗口UI已创建")

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setObjectName("main_toolbar")

        # 添加工具栏动作
        # 这里可以添加各种工具栏按钮

        self.addToolBar(toolbar)
        logger.debug("工具栏已创建")

    def _create_menubar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("&文件")

        # 新建动作
        new_action = QAction("&新建", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("新建档案")
        file_menu.addAction(new_action)

        # 打开动作
        open_action = QAction("&打开", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("打开档案")
        file_menu.addAction(open_action)

        # 保存动作
        save_action = QAction("&保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("保存档案")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # 退出动作
        exit_action = QAction("&退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("退出应用")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("&编辑")

        # 设置动作
        settings_action = QAction("&设置", self)
        settings_action.setStatusTip("应用设置")
        edit_menu.addAction(settings_action)

        # 视图菜单
        view_menu = menubar.addMenu("&视图")

        # 窗口可见性动作
        toggle_visibility_action = QAction("&切换窗口可见性", self)
        toggle_visibility_action.setStatusTip("切换主窗口可见性")
        view_menu.addAction(toggle_visibility_action)

        # 帮助菜单
        help_menu = menubar.addMenu("&帮助")

        # 关于动作
        about_action = QAction("&关于", self)
        about_action.setStatusTip("关于TimeNest")
        help_menu.addAction(about_action)

        logger.debug("菜单栏已创建")

    def _initialize_components(self):
        """初始化组件"""
        # 创建默认组件
        clock_component = TimeNestClockComponent()
        date_component = TimeNestDateComponent()
        schedule_component = TimeNestScheduleComponent()

        self.components.extend([clock_component, date_component, schedule_component])

        logger.info(f"已初始化 {len(self.components)} 个组件")

    def _connect_signals(self):
        """连接信号"""
        # 连接时间服务信号
        self.time_service.time_synced.connect(self._on_time_synced)
        self.time_service.sync_status_changed.connect(self._on_sync_status_changed)

        # 连接设置变更信号
        self.settings.settings_changed.connect(self._on_settings_changed)

        logger.debug("信号已连接")

    def _restore_window_state(self):
        """恢复窗口状态"""
        # 恢复窗口位置和大小
        if self.settings.is_main_window_visible:
            self.show()
        else:
            self.hide()

    def _on_time_synced(self, new_time: datetime):
        """时间同步回调"""
        logger.debug(f"时间已同步: {new_time}")
        # 更新显示的时间
        self._update_display_time()

    def _on_sync_status_changed(self, status: str):
        """同步状态变更回调"""
        logger.debug(f"同步状态变更: {status}")
        # 更新状态栏
        self.status_bar.showMessage(status)

    def _on_settings_changed(self, setting_key: str):
        """设置变更回调"""
        logger.debug(f"设置已变更: {setting_key}")
        # 根据设置变更更新界面
        if setting_key == "is_main_window_visible":
            if self.settings.is_main_window_visible:
                self.show()
                self.window_visibility_changed.emit(True)
            else:
                self.hide()
                self.window_visibility_changed.emit(False)

    def _update_display_time(self):
        """更新显示时间"""
        # 这里可以更新时间显示
        current_time = self.time_service.get_current_time_str()
        logger.debug(f"当前时间显示: {current_time}")

    def show_event(self, event: QShowEvent) -> None:
        """窗口显示事件"""
        logger.debug("主窗口已显示")
        self.window_visibility_changed.emit(True)
        super().showEvent(event)

    def hide_event(self, event: QHideEvent) -> None:
        """窗口隐藏事件"""
        logger.debug("主窗口已隐藏")
        self.window_visibility_changed.emit(False)
        super().hideEvent(event)

    def closeEvent(self, event: Any) -> None:
        """窗口关闭事件"""
        logger.info("主窗口正在关闭")

        # 保存窗口状态
        self.settings.set_setting("is_main_window_visible", self.isVisible())

        # 保存设置
        self.settings.save_settings()

        # 保存窗口位置和大小
        # self._save_window_state()

        event.accept()
        logger.info("主窗口已关闭")

    def _save_window_state(self):
        """保存窗口状态"""
        # 保存窗口位置和大小到设置
        pass

    def get_components(self) -> List[BaseComponent]:
        """获取所有组件"""
        return self.components.copy()

    def add_component(self, component: BaseComponent) -> None:
        """添加组件"""
        if component not in self.components:
            self.components.append(component)
            logger.debug(f"组件已添加: {component.name}")

    def remove_component(self, component: BaseComponent) -> None:
        """移除组件"""
        if component in self.components:
            self.components.remove(component)
            logger.debug(f"组件已移除: {component.name}")

    def update_components(self):
        """更新所有组件"""
        for component in self.components:
            component.update_content()
        logger.debug("所有组件已更新")

    def get_time_service(self):
        """获取时间服务实例"""
        return self.time_service

    def get_settings(self):
        """获取设置实例"""
        return self.settings


# 为方便测试添加一个简单的创建函数
def create_main_window(settings: TimeNestSettings) -> TimeNestMainWindow:
    """
    创建主窗口的便捷函数

    Args:
        settings: 应用设置实例

    Returns:
        TimeNestMainWindow: 主窗口实例
    """
    return TimeNestMainWindow(settings)
