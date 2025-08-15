import logging
from typing import TYPE_CHECKING, List, Optional, Union

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import (
    QCloseEvent,
    QEnterEvent,
    QHideEvent,
    QMoveEvent,
    QResizeEvent,
    QShowEvent,
)
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QWidget

if TYPE_CHECKING:
    from core.components.clock_component import ClockComponent
    from core.components.date_component import DateComponent
    from core.services.lessons_service import LessonsService
    from core.services.time_service import TimeService
    from ui.components.schedule_component import ScheduleComponent

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类 - 仿ClassIsland悬浮窗样式"""

    # 窗口状态改变信号
    windowStateChanged = Signal(bool)  # visible

    def __init__(
        self,
        lessons_service: Optional["LessonsService"] = None,
        exact_time_service: Optional["TimeService"] = None,
    ):
        super().__init__()
        self.lessons_service: Optional["LessonsService"] = lessons_service
        self.exact_time_service: Optional["TimeService"] = exact_time_service

        # 组件列表
        self.components: List[
            Union[ClockComponent, DateComponent, ScheduleComponent]
        ] = []

        # 窗口状态
        self.is_visible = True
        self.is_floating = True
        self.is_expanded = False

        # 动画相关
        self.opacity_animation = None
        self.geometry_animation = None

        # 保存动画引用防止被垃圾回收
        self.animations: List[Optional[QPropertyAnimation]] = []

        self.init_ui()
        self.init_window_properties()
        self.init_components()
        self.init_timers()

    def init_ui(self):
        """初始化UI - 优化后的布局和样式"""
        # 创建中央部件
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWindowRoot")
        self.setCentralWidget(self.central_widget)

        # 创建主布局 - 改进的水平布局
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(16, 8, 16, 8)  # 更合理的边距
        self.main_layout.setSpacing(16)  # 优化组件间距

        # 左侧组件区域（时钟和日期）
        self.left_container = QWidget()
        self.left_container.setObjectName("LeftContainer")
        self.left_layout = QHBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(12)
        self.left_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # 右侧组件区域（课程表）
        self.right_container = QWidget()
        self.right_container.setObjectName("RightContainer")
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # 添加容器到主布局
        self.main_layout.addWidget(self.left_container)
        self.main_layout.addStretch()  # 弹性空间
        self.main_layout.addWidget(self.right_container)

        # 应用样式表 - 改进的样式
        self.setStyleSheet(
            """
            QMainWindow {
                background: transparent;
                font-family: "Microsoft YaHei", "SimHei", "sans-serif";
            }
            #MainWindowRoot {
                background-color: rgba(20, 20, 20, 220);  /* 更深的背景色 */
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 30);
                box-shadow: 0 10px 32px rgba(0, 0, 0, 0.4);
            }
            #LeftContainer, #RightContainer {
                background: transparent;
            }
            QMainWindow::titlebar {
                background: transparent;
            }
        """
        )

    def init_window_properties(self):
        """初始化窗口属性 - 仿ClassIsland窗口特性"""
        # 设置窗口标题
        self.setWindowTitle("TimeNest")

        # 设置窗口标志，实现悬浮窗效果 - 优化设置以避免焦点冲突
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint  # 无边框
            | Qt.WindowType.WindowStaysOnTopHint  # 置顶
            | Qt.WindowType.Tool  # 工具窗口
            | Qt.WindowType.SubWindow  # 子窗口（避免与配置窗口冲突）
        )

        # 设置窗口透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # 设置窗口大小和位置 - 仿ClassIsland尺寸
        self.resize(600, 60)  # 更宽的窗口以容纳更多组件
        self.move_to_top_center()

        # 设置窗口透明度
        self.setWindowOpacity(0.95)

        # 启用鼠标事件
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # 连接鼠标事件
        self.setMouseTracking(True)

    def move_to_top_center(self):
        """将窗口移动到屏幕顶部中央 - 仿ClassIsland停靠机制"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            # 停靠在屏幕顶部中央
            x = screen_geometry.center().x() - self.width() // 2
            y = screen_geometry.top() + 10  # 距离顶部10像素，避免与系统栏冲突
            self.move(x, y)

    def init_components(self):
        """初始化组件 - 仿ClassIsland组件系统"""
        logger.info("正在初始化主窗口组件")

        try:
            # 导入主题管理器
            from core.components.theme_manager import theme_manager

            # 创建组件实例 - 严格按照ClassIsland的组件顺序
            clock_component = ClockComponent(
                lessons_service=self.lessons_service,
                exact_time_service=self.exact_time_service,
            )

            date_component = DateComponent(
                lessons_service=self.lessons_service,
                exact_time_service=self.exact_time_service,
            )

            schedule_component = ScheduleComponent(
                lessons_service=self.lessons_service,
                exact_time_service=self.exact_time_service,
            )

            # 应用主题到组件
            theme_manager.apply_theme_to_component(clock_component)
            theme_manager.apply_theme_to_component(date_component)
            theme_manager.apply_theme_to_component(schedule_component)

            # 添加时钟和日期组件到左侧容器
            self.left_layout.addWidget(clock_component)
            self.left_layout.addWidget(date_component)

            # 添加课程表组件到右侧容器
            self.right_layout.addWidget(schedule_component)

            # 保存组件引用
            self.components = [clock_component, date_component, schedule_component]

            logger.info(f"已初始化 {len(self.components)} 个组件，并应用主题")

        except Exception as e:
            logger.error(f"初始化组件时发生错误: {e}")

    def init_timers(self):
        """初始化定时器 - 仿ClassIsland更新机制"""
        # 组件更新定时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_components)
        self.update_timer.start(1000)  # 每秒更新一次，与ClassIsland一致

        # 屏幕变化监听器
        self.screen_timer = QTimer(self)
        self.screen_timer.timeout.connect(self.on_screen_changed)
        self.screen_timer.start(5000)  # 每5秒检查一次屏幕变化

        logger.info("组件更新定时器已启动")

    def update_components(self) -> None:
        """更新所有组件 - 严格按照ClassIsland的更新逻辑"""
        try:
            for component in self.components:
                # 根据组件类型调用相应的方法
                # 使用类型检查来避免Pylance错误
                from core.components.clock_component import ClockComponent
                from core.components.date_component import DateComponent
                from ui.components.schedule_component import ScheduleComponent

                if isinstance(
                    component, (ClockComponent, ScheduleComponent)
                ) and hasattr(component, "update_content"):
                    component.update_content()
                elif isinstance(component, DateComponent) and hasattr(
                    component, "update_date"
                ):
                    component.update_date()
        except Exception as e:
            logger.error(f"更新组件时发生错误: {e}")

    def on_screen_changed(self):
        """屏幕变化处理"""
        # 当屏幕分辨率或配置发生变化时，重新调整窗口位置
        self.move_to_top_center()

    def enterEvent(self, event: QEnterEvent) -> None:
        """鼠标进入窗口事件"""
        logger.debug("鼠标进入主窗口")
        self.animate_opacity(1.0, 200)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """鼠标离开窗口事件"""
        logger.debug("鼠标离开主窗口")
        self.animate_opacity(0.95, 200)
        super().leaveEvent(event)

    def animate_opacity(self, target_opacity: float, duration: int):
        """窗口透明度动画"""
        logger.debug(
            f"开始透明度动画: {self.windowOpacity()} -> {target_opacity}, 持续时间: {duration}ms"
        )
        # 如果目标透明度与当前透明度相同，则不执行动画
        if abs(self.windowOpacity() - target_opacity) < 0.01:
            logger.debug("目标透明度与当前透明度相同，跳过动画")
            return

        if (
            self.opacity_animation
            and self.opacity_animation.state() == QPropertyAnimation.State.Running
        ):
            logger.debug("停止正在运行的透明度动画")
            self.opacity_animation.stop()

        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(duration)
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.setEndValue(target_opacity)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 保存动画引用防止被垃圾回收
        if self.opacity_animation:
            self.animations.append(self.opacity_animation)
            self.opacity_animation.finished.connect(
                lambda: self._remove_animation(self.opacity_animation)
            )

        logger.debug("启动透明度动画")
        self.opacity_animation.start()

    def _remove_animation(self, animation: Optional[QPropertyAnimation]) -> None:
        """从动画列表中移除已完成的动画"""
        logger.debug("透明度动画完成")
        if animation in self.animations:
            self.animations.remove(animation)

    def resizeEvent(self, event: QResizeEvent):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 保持窗口在屏幕中央
        self.move_to_top_center()
        logger.debug(f"窗口大小改变: {self.width()}x{self.height()}")

    def moveEvent(self, event: QMoveEvent):
        """窗口移动事件"""
        super().moveEvent(event)
        logger.debug(f"窗口位置改变: ({self.x()}, {self.y()})")

    def showEvent(self, event: QShowEvent):
        """窗口显示事件"""
        super().showEvent(event)
        self.is_visible = True
        self.windowStateChanged.emit(True)
        logger.info("主窗口已显示")

    def hideEvent(self, event: QHideEvent):
        """窗口隐藏事件"""
        super().hideEvent(event)
        self.is_visible = False
        self.windowStateChanged.emit(False)
        logger.info("主窗口已隐藏")

    def closeEvent(self, event: QCloseEvent) -> None:
        """窗口关闭事件"""
        logger.info("主窗口正在关闭")
        # 停止定时器
        if hasattr(self, "update_timer"):
            self.update_timer.stop()
        if hasattr(self, "screen_timer"):
            self.screen_timer.stop()

        # 停止所有动画
        for animation in self.animations[:]:  # 使用切片复制避免修改列表时的问题
            if (
                animation
                and hasattr(animation, "state")
                and animation.state() == QPropertyAnimation.State.Running
            ):
                animation.stop()
        self.animations.clear()

        super().closeEvent(event)

    def setVisible(self, visible: bool):
        """设置窗口可见性"""
        super().setVisible(visible)
        self.is_visible = visible
        self.windowStateChanged.emit(visible)

    def get_is_visible(self):
        """获取窗口可见性状态"""
        return self.is_visible

    def get_is_floating(self):
        """获取窗口悬浮状态"""
        return self.is_floating
