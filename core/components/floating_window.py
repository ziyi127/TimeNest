import logging
from typing import Optional, Any
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QEvent
from PySide6.QtGui import QPainter, QColor, QPen, QCursor, QEnterEvent, QMouseEvent, QPaintEvent

from core.models.component_settings.lesson_control_settings import LessonControlSettings


class FloatingWindow(QMainWindow):
    """浮动窗口组件 - 采用类似Apple Dynamic Island的设计风格，固定在屏幕顶部"""
    
    def __init__(self, settings: Optional[LessonControlSettings] = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or LessonControlSettings()
        
        # 窗口状态变量
        self.is_pinned = False
        
        # Dynamic Island相关变量
        self.default_width = 400
        self.default_height = 60
        self.animation_duration = 300
        
        # 透明度效果相关变量
        self.normal_opacity = 0.95
        self.hover_opacity = self.settings.floating_window_hover_transparency
        self.touch_opacity = self.settings.floating_window_touch_transparency
        self.current_opacity = self.normal_opacity
        
        # 内容组件
        self.content_widget = None
        
        # 初始化窗口
        self.init_window()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化动画
        self.init_animations()
        
        # 连接设置变更信号
        self.settings.setting_changed.connect(self.on_setting_changed)
        
    def init_window(self):
        """初始化窗口属性"""
        # 设置窗口标志 - 固定在屏幕顶部，无边框
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(self.normal_opacity)
        
        # 设置初始大小
        self.resize(self.default_width, self.default_height)
        
        # 设置窗口位置到屏幕中心顶部
        self.center_window_top()
        
        # 启用鼠标跟踪以支持悬停效果
        self.setMouseTracking(True)
        
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        self.content_widget = QWidget()
        self.setCentralWidget(self.content_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建内容区域
        self.content_area = QWidget()
        self.content_layout = QHBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 10, 20, 10)
        self.content_layout.setSpacing(15)
        
        # 添加示例内容
        # 时间标签
        time_label = QLabel("10:30")
        time_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        
        # 日期标签
        date_label = QLabel("星期三 06/12")
        date_label.setStyleSheet("font-size: 14px; color: #CCCCCC;")
        
        # 课程状态标签
        status_label = QLabel("课程: 数学")
        status_label.setStyleSheet("font-size: 16px; color: white;")
        
        # 倒计时标签
        countdown_label = QLabel("剩余: 25:00")
        countdown_label.setStyleSheet("font-size: 14px; color: #FFD700;")
        
        # 添加到布局
        self.content_layout.addWidget(time_label)
        self.content_layout.addWidget(date_label)
        self.content_layout.addStretch()
        self.content_layout.addWidget(status_label)
        self.content_layout.addWidget(countdown_label)
        
        main_layout.addWidget(self.content_area)
        
    def init_animations(self):
        """初始化动画"""
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(200)  # 200ms的透明度过渡
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def center_window_top(self):
        """将窗口居中显示在屏幕顶部"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.move(
                screen_geometry.center().x() - self.width() // 2,
                screen_geometry.top() + 10  # 距离顶部10像素
            )
            
    def enterEvent(self, event: QEnterEvent):
        """鼠标进入窗口事件"""
        if self.settings.enable_floating_window_hover_effect:
            self.set_opacity_with_animation(self.hover_opacity)
        super().enterEvent(event)
        
    def leaveEvent(self, event: QEvent):
        """鼠标离开窗口事件"""
        if self.settings.enable_floating_window_hover_effect:
            self.set_opacity_with_animation(self.normal_opacity)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 实现透明度效果"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 触控透明效果
            if self.settings.enable_floating_window_touch_effect:
                self.set_opacity_with_animation(self.touch_opacity)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键按下时也应用触控透明效果
            if self.settings.enable_floating_window_touch_effect:
                self.set_opacity_with_animation(self.touch_opacity)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 恢复正常透明度
            if self.settings.enable_floating_window_touch_effect:
                # 如果鼠标仍在窗口内，恢复悬停透明度；否则恢复正常透明度
                if self.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    if self.settings.enable_floating_window_hover_effect:
                        self.set_opacity_with_animation(self.hover_opacity)
                    else:
                        self.set_opacity_with_animation(self.normal_opacity)
                else:
                    self.set_opacity_with_animation(self.normal_opacity)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键释放时恢复透明度
            if self.settings.enable_floating_window_touch_effect:
                # 如果鼠标仍在窗口内，恢复悬停透明度；否则恢复正常透明度
                if self.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    if self.settings.enable_floating_window_hover_effect:
                        self.set_opacity_with_animation(self.hover_opacity)
                    else:
                        self.set_opacity_with_animation(self.normal_opacity)
                else:
                    self.set_opacity_with_animation(self.normal_opacity)
            
    def toggle_pin(self):
        """切换固定/取消固定状态"""
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
    def set_pinned(self, pinned: bool):
        """设置固定状态"""
        self.is_pinned = pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
    def get_is_pinned(self):
        """获取固定状态"""
        return self.is_pinned
        
    def set_transparency(self, opacity: float):
        """设置窗口透明度"""
        self.normal_opacity = max(0.1, min(1.0, opacity))
        self.setWindowOpacity(self.normal_opacity)
        
    def set_position(self, x: int, y: int):
        """设置窗口位置"""
        # 重写此方法以保持窗口始终在顶部
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            # 保持x坐标在屏幕范围内，y坐标始终在顶部
            x = max(screen_geometry.left(), min(x, screen_geometry.right() - self.width()))
            y = screen_geometry.top() + 10  # 始终距离顶部10像素
            self.move(x, y)
        
    def get_position(self):
        """获取窗口位置"""
        return self.pos()
        
    def set_opacity_with_animation(self, target_opacity: float):
        """使用动画设置窗口透明度"""
        if self.opacity_animation.state() == QPropertyAnimation.State.Running:
            self.opacity_animation.stop()
            
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.setEndValue(target_opacity)
        self.opacity_animation.start()
        
    def on_setting_changed(self, key: str, value: Any):
        """处理设置变更"""
        if key == "floating_window_hover_transparency":
            self.hover_opacity = value
        elif key == "floating_window_touch_transparency":
            self.touch_opacity = value
        elif key == "enable_floating_window_hover_effect":
            # 如果禁用了悬停效果且当前处于悬停状态，恢复正常透明度
            if not value and not self.geometry().contains(self.mapFromGlobal(QCursor.pos())):
                self.set_opacity_with_animation(self.normal_opacity)
        elif key == "enable_floating_window_touch_effect":
            # 触控效果开关变更，无需特殊处理
            pass
            
    def paintEvent(self, event: QPaintEvent):
        """绘制窗口背景 - 创建灵动岛样式外观"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形背景，模拟Dynamic Island外观
        rect = self.rect()
        radius = 20  # 圆角半径
        
        # 绘制背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(30, 30, 30, 200))  # 深灰色半透明背景
        painter.drawRoundedRect(rect, radius, radius)
        
        # 绘制边框
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius-1, radius-1)


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建浮动窗口
    floating_window = FloatingWindow()
    floating_window.show()
    
    sys.exit(app.exec())