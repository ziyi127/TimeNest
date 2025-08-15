import logging
from datetime import datetime
from typing import List, Optional

from config import DISABLE_ANIMATIONS
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from core.models.component_settings.date_component_settings import DateComponentSettings
from core.services.lessons_service import LessonsService
from core.services.time_service import TimeService

# 为了消除Pylance类型识别问题，添加类型注解
# from core.models.component_settings.date_component_settings import DateComponentSettings as DateComponentSettingsType


class DateComponent(QWidget):
    """日期组件 - 显示当前日期和星期，基于ClassIsland的DateComponent实现"""

    def __init__(
        self,
        lessons_service: Optional[LessonsService] = None,
        exact_time_service: Optional[TimeService] = None,
        settings_service: Optional[object] = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_date = datetime.now()

        # 服务依赖
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.settings_service = settings_service

        # 设置组件
        self.settings = DateComponentSettings()

        # 动画相关
        self.fade_animation: Optional[QPropertyAnimation] = None
        self.animations: List[QPropertyAnimation] = []  # 保存动画引用防止被垃圾回收

        # 初始化UI
        self.init_ui()

        # 连接事件 - 严格按照ClassIsland逻辑
        if self.lessons_service is not None:
            try:
                self.lessons_service.post_main_timer_ticked.connect(self.update_date)
            except AttributeError:
                # 如果没有post_main_timer_ticked信号，使用自己的定时器
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update_date)
                self.timer.start(60000)  # 1分钟检查一次
        else:
            # 如果没有课程服务，使用自己的定时器
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_date)
            self.timer.start(60000)  # 1分钟检查一次

        # 初始化内容
        self.update_date()

    def init_ui(self):
        """初始化UI - 严格按照ClassIsland的XAML结构实现"""
        # 设置布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # 日期显示 - 使用ClassIsland的格式化方式
        self.date_display = QLabel()
        self.date_display.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self.date_display.setObjectName("dateDisplay")

        # 设置字体样式 - 更接近ClassIsland风格
        font = QFont("Microsoft YaHei", 15)
        self.date_display.setFont(font)

        # 直接设置样式表确保颜色生效
        self.date_display.setStyleSheet(
            """
            QLabel#dateDisplay {
                color: white !important;
                background: transparent;
                font-family: "Microsoft YaHei";
                font-weight: normal;
                qproperty-alignment: AlignVCenter | AlignLeft;
            }
            """
        )
        # 额外直接设置调色板以确保颜色生效
        palette = self.date_display.palette()
        palette.setColor(self.date_display.foregroundRole(), Qt.GlobalColor.white)
        self.date_display.setPalette(palette)

        layout.addWidget(self.date_display)
        self.setLayout(layout)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedHeight(40)  # 设置固定高度

        # 启用鼠标穿透，允许点击穿透到下方
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def update_date(self):
        """更新日期显示内容 - 严格按照ClassIsland逻辑实现"""
        try:
            # 获取当前日期 - 根据设置决定使用实时时间还是精确时间
            # 明确类型注解
            show_real_time: bool = bool(self.settings.show_real_time)
            if show_real_time:
                self.current_date = datetime.now()
            elif self.exact_time_service:
                self.current_date = self.exact_time_service.get_current_local_datetime()
            else:
                self.current_date = datetime.now()

            # 格式化日期显示 - 严格按照ClassIsland的格式: "ddd MM/dd"
            # 注意：ClassIsland使用的是英文星期缩写，需要对应转换
            weekday_names = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
            weekday = weekday_names[self.current_date.weekday()]
            formatted_date = f"{weekday} {self.current_date.strftime('%m/%d')}"

            # 更新显示
            self.date_display.setText(formatted_date)

            # 添加淡入效果
            self.animate_fade_in()

        except Exception as e:
            self.logger.error(f"更新日期组件内容时出错: {e}")
            # 出错时显示错误信息
            self.date_display.setText("日期错误")

    def animate_fade_in(self):
        """淡入动画效果 - 根据全局配置决定是否使用动画"""
        if DISABLE_ANIMATIONS:
            self.logger.debug("全局禁用动画，直接设置日期组件透明度为1.0")
            self.date_display.setWindowOpacity(1.0)
            return
        
        self.logger.debug("直接设置日期组件透明度为1.0")
        self.date_display.setWindowOpacity(1.0)
        return

    def _remove_animation(self, animation: Optional[QPropertyAnimation]) -> None:
        """从动画列表中移除已完成的动画"""
        try:
            if animation and animation in self.animations:
                self.animations.remove(animation)
        except ValueError:
            # 动画可能已经被移除了
            pass

    def get_current_date(self) -> datetime:
        """获取当前日期"""
        return self.current_date


# 测试代码
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建日期组件 - 修正测试代码，传递正确的参数
    date_component = DateComponent()
    date_component.show()

    sys.exit(app.exec())
