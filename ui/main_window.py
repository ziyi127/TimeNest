import sys
import logging
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QRect, QPoint, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QScreen, QColor, QPalette, QFont

from ui.components.schedule_component import ScheduleComponent
from core.components.clock_component import ClockComponent
from core.components.date_component import DateComponent
from core.components.user_preferences import user_preferences

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类 - 仿ClassIsland悬浮窗样式"""
    
    # 窗口状态改变信号
    windowStateChanged = Signal(bool)  # visible
    
    def __init__(self, lessons_service=None, exact_time_service=None, profile_service=None):
        super().__init__()
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.profile_service = profile_service
        
        # 组件列表
        self.components = []
        
        # 窗口状态
        self.is_visible = True
        self.is_floating = True
        self.is_minimized_state = False
        
        # 动画
        self.opacity_animation = None
        self.position_animation = None
        
        self.init_ui()
        self.init_window_properties()
        self.init_components()
        self.init_timers()
        self.init_animations()
        
    def init_ui(self):
        """初始化UI - 仿ClassIsland布局"""
        # 创建中央部件
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWindowRoot")
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局 - 仿ClassIsland的水平布局
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(12, 0, 12, 0)  # 仿ClassIsland边距
        self.main_layout.setSpacing(20)  # 组件间距
        
        # 左侧组件区域（时钟和日期）
        self.left_container = QWidget()
        self.left_container.setObjectName("LeftContainer")
        self.left_layout = QHBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)
        self.left_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 右侧组件区域（课程表）
        self.right_container = QWidget()
        self.right_container.setObjectName("RightContainer")
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # 添加容器到主布局
        self.main_layout.addWidget(self.left_container)
        self.main_layout.addStretch()  # 弹性空间
        self.main_layout.addWidget(self.right_container)
        
        # 应用样式表 - 仿ClassIsland样式
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
                font-family: "Microsoft YaHei", "SimHei", "sans-serif";
            }
            #MainWindowRoot {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
            #LeftContainer, #RightContainer {
                background: transparent;
            }
        """)
        
    def init_window_properties(self):
        """初始化窗口属性 - 仿ClassIsland窗口特性"""
        # 设置窗口标题
        self.setWindowTitle("TimeNest")
        
        # 设置窗口标志，实现悬浮窗效果 - 优化设置以避免焦点冲突
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # 无边框
            Qt.WindowType.WindowStaysOnTopHint |     # 置顶
            Qt.WindowType.Tool |                     # 工具窗口
            Qt.WindowType.WindowTransparentForInput | # 点击穿透
            Qt.WindowType.SubWindow                   # 子窗口（避免与配置窗口冲突）
        )
        
        # 设置窗口透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 设置窗口大小和位置 - 仿ClassIsland尺寸
        self.resize(600, 40)  # 更宽的窗口以容纳更多组件
        self.move_to_top_center()
        
        # 设置窗口透明度
        self.setWindowOpacity(0.95)
        
    def init_animations(self):
        """初始化动画效果"""
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 位置动画（用于最小化/恢复）
        self.position_animation = QPropertyAnimation(self, b"pos")
        self.position_animation.setDuration(300)
        self.position_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def move_to_top_center(self):
        """将窗口移动到屏幕顶部中央 - 仿ClassIsland停靠机制"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            # 停靠在屏幕顶部中央
            x = screen_geometry.center().x() - self.width() // 2
            y = screen_geometry.top() + 30  # 距离顶部30像素，避免与系统栏冲突
            self.move(x, y)
            
    def init_components(self):
        """初始化组件 - 优化组件加载流程"""
        logger.info("正在初始化主窗口组件")
        
        try:
            # 创建组件实例
            clock_component = ClockComponent(
                lessons_service=self.lessons_service,
                exact_time_service=self.exact_time_service
            )
            
            date_component = DateComponent(
                lessons_service=self.lessons_service,
                exact_time_service=self.exact_time_service
            )
            
            schedule_component = ScheduleComponent(
                lessons_service=self.lessons_service,
                exact_time_service=self.exact_time_service,
                profile_service=self.profile_service
            )
            
            # 先添加左侧组件
            self.left_layout.addWidget(clock_component)
            self.left_layout.addWidget(date_component)
            
            # 再添加右侧组件
            self.right_layout.addWidget(schedule_component)
            
            # 保存组件引用
            self.components = [clock_component, date_component, schedule_component]
            
            logger.info(f"已初始化 {len(self.components)} 个组件")
            
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
        
    def update_components(self):
        """更新所有组件 - 严格按照ClassIsland的更新逻辑"""
        try:
            for component in self.components:
                if hasattr(component, 'update_content'):
                    component.update_content()
        except Exception as e:
            logger.error(f"更新组件时发生错误: {e}")
            
    def on_screen_changed(self):
        """屏幕变化处理"""
        # 当屏幕分辨率或配置发生变化时，重新调整窗口位置
        self.move_to_top_center()
            
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 保持窗口在屏幕顶部中央
        self.move_to_top_center()
        logger.debug(f"窗口大小改变: {self.width()}x{self.height()}")
        
    def moveEvent(self, event):
        """窗口移动事件"""
        super().moveEvent(event)
        # 仅在用户手动移动窗口时更新位置
        if self.is_floating:
            logger.debug(f"窗口位置改变: ({self.x()}, {self.y()})")
        
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        self.is_visible = True
        self.windowStateChanged.emit(True)
        logger.info("主窗口已显示")
        
    def hideEvent(self, event):
        """窗口隐藏事件"""
        super().hideEvent(event)
        self.is_visible = False
        self.windowStateChanged.emit(False)
        logger.info("主窗口已隐藏")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("主窗口正在关闭")
        # 停止定时器
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        if hasattr(self, 'screen_timer'):
            self.screen_timer.stop()
        super().closeEvent(event)
        
    def setVisible(self, visible: bool):
        """设置窗口可见性（带动画效果）"""
        if visible and not self.isVisible():
            # 显示窗口带动画
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(user_preferences.get('window_opacity', 0.95))
            self.opacity_animation.start()
            super().setVisible(True)
        elif not visible and self.isVisible():
            # 隐藏窗口带动画
            self.opacity_animation.setStartValue(self.windowOpacity())
            self.opacity_animation.setEndValue(0.0)
            self.opacity_animation.finished.connect(lambda: super().setVisible(False))
            self.opacity_animation.start()
        else:
            super().setVisible(visible)
            
        self.is_visible = visible
        self.windowStateChanged.emit(visible)
        
    def minimize(self):
        """最小化窗口（滑动到屏幕边缘）"""
        if not self.is_minimized_state:
            screen = self.screen()
            if screen:
                screen_geometry = screen.geometry()
                start_pos = self.pos()
                end_pos = QPoint(start_pos.x(), -self.height() + 10)  # 隐藏到屏幕顶部边缘
                
                self.position_animation.setStartValue(start_pos)
                self.position_animation.setEndValue(end_pos)
                self.position_animation.start()
                
                self.is_minimized_state = True
                
    def restore(self):
        """恢复窗口"""
        if self.is_minimized_state:
            self.move_to_top_center()
            self.is_minimized_state = False
            
    def toggle_minimize(self):
        """切换最小化状态"""
        if self.is_minimized_state:
            self.restore()
        else:
            self.minimize()
        
    def get_is_visible(self):
        """获取窗口可见性状态"""
        return self.is_visible
        
    def get_is_floating(self):
        """获取窗口悬浮状态"""
        return self.is_floating