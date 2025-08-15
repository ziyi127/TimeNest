import logging
from datetime import datetime
from typing import Any, Optional

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QCursor,
    QEnterEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from core.models.component_settings.floating_window_settings import (
    FloatingWindowSettings,
)
from core.models.component_settings.lesson_control_settings import LessonControlSettings


class FloatingWindow(QMainWindow):
    """浮动窗口组件 - 采用类似Apple Dynamic Island的设计风格，固定在屏幕顶部"""

    # 插件接口信号
    plugin_content_added = Signal(str, object)  # 内容标识, 控件
    plugin_content_removed = Signal(str)  # 内容标识

    def __init__(
        self,
        lesson_settings: Optional[LessonControlSettings] = None,
        floating_settings: Optional[FloatingWindowSettings] = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # 设置组件
        self.lesson_settings = lesson_settings or LessonControlSettings()
        self.floating_settings = floating_settings or FloatingWindowSettings()

        # 窗口状态变量
        self.is_pinned = False

        # Dynamic Island相关变量
        self.default_width = 400
        self.default_height = 60
        self.animation_duration = 300

        # 透明度效果相关变量
        self.normal_opacity = 0.95
        self.hover_opacity = self.lesson_settings.floating_window_hover_transparency
        self.touch_opacity = self.lesson_settings.floating_window_touch_transparency
        self.current_opacity = self.normal_opacity

        # 内容组件
        self.content_widget = None
        self.time_label = None
        self.date_label = None
        self.lesson_label = None
        self.countdown_label = None
        self.schedule_label = None
        self.plugin_content = {}  # 存储插件内容 {identifier: widget}

        # 初始化窗口
        self.init_window()

        # 初始化UI
        self.init_ui()

        # 初始化动画
        self.init_animations()

        # 初始化定时器
        self.init_timers()

        # 连接设置变更信号
        self.lesson_settings.setting_changed.connect(self.on_lesson_setting_changed)
        self.floating_settings.setting_changed.connect(self.on_floating_setting_changed)

    def init_window(self):
        """初始化窗口属性"""
        # 设置窗口标志 - 固定在屏幕顶部，无边框
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

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

        # 创建内容标签
        # 时间标签
        self.time_label = QLabel()
        self.time_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white;"
        )

        # 日期标签
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 14px; color: #CCCCCC;")

        # 课程状态标签
        self.lesson_label = QLabel()
        self.lesson_label.setStyleSheet("font-size: 16px; color: white;")

        # 倒计时标签
        self.countdown_label = QLabel()
        self.countdown_label.setStyleSheet("font-size: 14px; color: #FFD700;")

        # 课程表标签
        self.schedule_label = QLabel()
        self.schedule_label.setStyleSheet("font-size: 12px; color: #CCCCCC;")

        # 添加到布局
        self.content_layout.addWidget(self.time_label)
        self.content_layout.addWidget(self.date_label)
        self.content_layout.addStretch()
        self.content_layout.addWidget(self.lesson_label)
        self.content_layout.addWidget(self.countdown_label)
        self.content_layout.addWidget(self.schedule_label)

        main_layout.addWidget(self.content_area)

        # 更新显示内容
        self.update_content()

        # 连接插件接口信号
        self.plugin_content_added.connect(self._add_plugin_content)
        self.plugin_content_removed.connect(self._remove_plugin_content)

    def init_animations(self):
        """初始化动画"""
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(200)  # 200ms的透明度过渡
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def init_timers(self):
        """初始化定时器"""
        # 每秒更新一次内容
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_content)
        self.update_timer.start(1000)

    def center_window_top(self):
        """将窗口居中显示在屏幕顶部"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.move(
                screen_geometry.center().x() - self.width() // 2,
                screen_geometry.top() + 10,  # 距离顶部10像素
            )

    def enterEvent(self, event: QEnterEvent):
        """鼠标进入窗口事件"""
        if self.lesson_settings.enable_floating_window_hover_effect:
            self.set_opacity_with_animation(self.hover_opacity)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """鼠标离开窗口事件"""
        if self.lesson_settings.enable_floating_window_hover_effect:
            self.set_opacity_with_animation(self.normal_opacity)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 实现透明度效果"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 触控透明效果
            if self.lesson_settings.enable_floating_window_touch_effect:
                self.set_opacity_with_animation(self.touch_opacity)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键按下时也应用触控透明效果
            if self.lesson_settings.enable_floating_window_touch_effect:
                self.set_opacity_with_animation(self.touch_opacity)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 恢复正常透明度
            if self.lesson_settings.enable_floating_window_touch_effect:
                # 如果鼠标仍在窗口内，恢复悬停透明度；否则恢复正常透明度
                if self.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    if self.lesson_settings.enable_floating_window_hover_effect:
                        self.set_opacity_with_animation(self.hover_opacity)
                    else:
                        self.set_opacity_with_animation(self.normal_opacity)
                else:
                    self.set_opacity_with_animation(self.normal_opacity)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键释放时恢复透明度
            if self.lesson_settings.enable_floating_window_touch_effect:
                # 如果鼠标仍在窗口内，恢复悬停透明度；否则恢复正常透明度
                if self.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    if self.lesson_settings.enable_floating_window_hover_effect:
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
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()

    def set_pinned(self, pinned: bool):
        """设置固定状态"""
        self.is_pinned = pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
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
            x = max(
                screen_geometry.left(), min(x, screen_geometry.right() - self.width())
            )
            y = screen_geometry.top() + 10  # 始终距离顶部10像素
            self.move(x, y)

    def get_position(self):
        """获取窗口位置"""
        return self.pos()

    def set_opacity_with_animation(self, target_opacity: float):
        """使用动画设置窗口透明度"""
        # 如果目标透明度与当前透明度相同，则不执行动画
        if abs(self.windowOpacity() - target_opacity) < 0.01:
            return

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
            if not value and not self.geometry().contains(
                self.mapFromGlobal(QCursor.pos())
            ):
                self.set_opacity_with_animation(self.normal_opacity)
        elif key == "enable_floating_window_touch_effect":
            # 触控效果开关变更，无需特殊处理
            pass

    def update_content(self):
        """更新显示内容"""
        # 更新倒计时
        if self.floating_settings.show_countdown:
            self.update_countdown()
            self.countdown_label.show()
        else:
            self.countdown_label.hide()

        # 更新实时时间
        if self.floating_settings.show_real_time:
            self.update_time()
            self.time_label.show()
            self.date_label.show()
        else:
            self.time_label.hide()
            self.date_label.hide()

        # 更新课程信息
        if (
            self.floating_settings.show_current_lesson
            or self.floating_settings.show_full_schedule
        ):
            self.update_lesson()
            if self.floating_settings.show_current_lesson:
                self.lesson_label.show()
            else:
                self.lesson_label.hide()

            if self.floating_settings.show_full_schedule:
                self.schedule_label.show()
            else:
                self.schedule_label.hide()
        else:
            self.lesson_label.hide()
            self.schedule_label.hide()

    def update_countdown(self):
        """更新倒计时显示"""
        try:
            # 获取倒计时目标日期
            target_date_str = self.floating_settings.countdown_target_date
            if target_date_str:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
                current_date = datetime.now()

                # 计算剩余天数
                delta = target_date - current_date
                days_left = delta.days

                # 显示倒计时
                label_text = f"{self.floating_settings.countdown_label}: {days_left}天"
                self.countdown_label.setText(label_text)
            else:
                self.countdown_label.setText("")
        except Exception as e:
            self.logger.error(f"更新倒计时显示时出错: {e}")
            self.countdown_label.setText("倒计时: 错误")

    def update_time(self):
        """更新时间显示"""
        try:
            current_time = datetime.now()

            # 根据设置格式化时间
            time_format = self.floating_settings.time_format
            date_format = self.floating_settings.date_format

            time_str = current_time.strftime(time_format)
            date_str = current_time.strftime(date_format)

            self.time_label.setText(time_str)
            self.date_label.setText(date_str)
        except Exception as e:
            self.logger.error(f"更新时间显示时出错: {e}")
            self.time_label.setText("时间: 错误")
            self.date_label.setText("日期: 错误")

    def update_lesson(self):
        """更新课程信息显示"""
        # 这里需要根据实际的课程服务来实现
        # 暂时使用示例数据
        try:
            if self.floating_settings.show_current_lesson:
                # 示例当前课程
                self.lesson_label.setText("课程: 数学")

            if self.floating_settings.show_full_schedule:
                # 示例全天课程表
                schedule_text = "课表: 数学, 语文, 英语, 物理"
                self.schedule_label.setText(schedule_text)
        except Exception as e:
            self.logger.error(f"更新课程信息显示时出错: {e}")
            self.lesson_label.setText("课程: 错误")
            self.schedule_label.setText("课表: 错误")

    def on_lesson_setting_changed(self, key: str, value: Any):
        """处理课程设置变更"""
        if key == "floating_window_hover_transparency":
            self.hover_opacity = value
        elif key == "floating_window_touch_transparency":
            self.touch_opacity = value
        elif key == "enable_floating_window_hover_effect":
            # 如果禁用了悬停效果且当前处于悬停状态，恢复正常透明度
            if not value and not self.geometry().contains(
                self.mapFromGlobal(QCursor.pos())
            ):
                self.set_opacity_with_animation(self.normal_opacity)
        elif key == "enable_floating_window_touch_effect":
            # 触控效果开关变更，无需特殊处理
            pass

    def on_floating_setting_changed(self, key: str, value: Any):
        """处理浮动窗口设置变更"""
        self.logger.info(f"浮动窗口设置变更: {key} = {value}")
        # 立即更新显示内容
        self.update_content()

    def _add_plugin_content(self, identifier: str, widget):
        """添加插件内容"""
        # 检查是否已存在同名内容
        if identifier in self.plugin_content:
            self.logger.warning(f"插件内容 '{identifier}' 已存在，将被替换")
            # 移除旧的内容
            old_widget = self.plugin_content[identifier]
            self.content_layout.removeWidget(old_widget)
            old_widget.deleteLater()

        # 添加新的内容
        self.plugin_content[identifier] = widget
        self.content_layout.addWidget(widget)
        widget.show()
        self.logger.info(f"已添加插件内容: {identifier}")

    def _remove_plugin_content(self, identifier: str):
        """移除插件内容"""
        if identifier in self.plugin_content:
            widget = self.plugin_content[identifier]
            self.content_layout.removeWidget(widget)
            widget.deleteLater()
            del self.plugin_content[identifier]
            self.logger.info(f"已移除插件内容: {identifier}")
        else:
            self.logger.warning(f"插件内容 '{identifier}' 不存在")

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
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius - 1, radius - 1)


# 测试代码
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建浮动窗口
    floating_window = FloatingWindow()
    floating_window.show()

    sys.exit(app.exec())
