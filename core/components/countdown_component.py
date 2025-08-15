import logging
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from core.models.component_settings.countdown_component_settings import (
    CountDownComponentSettings,
)


class CountDownComponent(QWidget):
    """倒计时组件 - 显示倒计时信息，基于ClassIsland的CountDownComponent实现"""

    def __init__(self, settings: Optional[CountDownComponentSettings] = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # 直接创建设置实例
        self.settings = settings or CountDownComponentSettings()

        # 倒计时相关变量
        self.countdown_target_time = datetime.now()
        self.is_countdown_active = False
        self.remaining_seconds = 0

        # 初始化UI
        self.init_ui()

        # 初始化内容
        self.update_content()

        # 连接设置变更信号
        if hasattr(self.settings, "changed"):
            self.settings.changed.connect(self.update_content)

        # 定时器更新倒计时
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # 每秒更新一次

    def init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 倒计时显示标签
        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setObjectName("countdownLabel")

        layout.addWidget(self.countdown_label)
        self.setLayout(layout)

    def update_content(self):
        """更新倒计时显示内容"""
        # 根据设置更新显示
        # 使用正确的属性名
        if self.settings.count_down_name:
            title = self.settings.count_down_name
            self.countdown_label.setText(title)
        else:
            self.countdown_label.setText("")

        # 更新倒计时状态
        self.update_countdown()

    def update_countdown(self):
        """更新倒计时显示"""
        if not self.is_countdown_active:
            # 如果没有激活倒计时，显示默认文本
            if self.settings.count_down_name:
                self.countdown_label.setText(self.settings.count_down_name)
            else:
                self.countdown_label.setText("倒计时")
            return

        # 计算剩余时间
        now = datetime.now()
        if now <= self.countdown_target_time:
            remaining = self.countdown_target_time - now
            self.remaining_seconds = int(remaining.total_seconds())

            # 格式化显示
            hours, remainder = divmod(self.remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                display_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                display_text = f"{minutes:02d}:{seconds:02d}"

            self.countdown_label.setText(display_text)
        else:
            # 倒计时结束
            self.countdown_label.setText("00:00")
            self.is_countdown_active = False

    def start_countdown(self, target_time: datetime):
        """开始倒计时"""
        self.countdown_target_time = target_time
        self.is_countdown_active = True
        self.update_countdown()

    def stop_countdown(self):
        """停止倒计时"""
        self.is_countdown_active = False
        self.countdown_label.setText("00:00")

    def set_target_time(self, target_time: datetime):
        """设置目标时间"""
        self.countdown_target_time = target_time
        if not self.is_countdown_active:
            self.is_countdown_active = True
        self.update_countdown()

    def get_remaining_seconds(self):
        """获取剩余秒数"""
        return self.remaining_seconds

    def is_active(self):
        """检查倒计时是否激活"""
        return self.is_countdown_active
