from datetime import datetime

from PySide6.QtCore import QObject, Signal


class FloatingWindowSettings(QObject):
    """悬浮窗设置，用于控制悬浮窗中显示的内容"""

    # 定义设置更改时发出的信号
    setting_changed = Signal(str, object)

    def __init__(self):
        super().__init__()
        # 悬浮窗显示内容控制
        self._show_countdown: bool = True  # 是否显示倒计时
        self._show_real_time: bool = True  # 是否显示实时时间
        self._show_current_lesson: bool = True  # 是否显示当前课程
        self._show_full_schedule: bool = False  # 是否显示全天课程表

        # 倒计时设置
        self._countdown_target_date: str = ""  # 倒计时目标日期 (YYYY-MM-DD格式)
        self._countdown_label: str = "倒计时"  # 倒计时标签

        # 实时时间设置
        self._time_format: str = "HH:mm:ss"  # 时间显示格式
        self._date_format: str = "yyyy-MM-dd"  # 日期显示格式

        # 课程表设置
        self._schedule_display_mode: int = 0  # 0=当前课程, 1=全天课程

    @property
    def show_countdown(self) -> bool:
        """是否显示倒计时"""
        return self._show_countdown

    @show_countdown.setter
    def show_countdown(self, value: bool) -> None:
        if self._show_countdown != value:
            self._show_countdown = value
            self.setting_changed.emit("show_countdown", value)

    @property
    def show_real_time(self) -> bool:
        """是否显示实时时间"""
        return self._show_real_time

    @show_real_time.setter
    def show_real_time(self, value: bool) -> None:
        if self._show_real_time != value:
            self._show_real_time = value
            self.setting_changed.emit("show_real_time", value)

    @property
    def show_current_lesson(self) -> bool:
        """是否显示当前课程"""
        return self._show_current_lesson

    @show_current_lesson.setter
    def show_current_lesson(self, value: bool) -> None:
        if self._show_current_lesson != value:
            self._show_current_lesson = value
            self.setting_changed.emit("show_current_lesson", value)

    @property
    def show_full_schedule(self) -> bool:
        """是否显示全天课程表"""
        return self._show_full_schedule

    @show_full_schedule.setter
    def show_full_schedule(self, value: bool) -> None:
        if self._show_full_schedule != value:
            self._show_full_schedule = value
            self.setting_changed.emit("show_full_schedule", value)

    @property
    def countdown_target_date(self) -> str:
        """倒计时目标日期 (YYYY-MM-DD格式)"""
        return self._countdown_target_date

    @countdown_target_date.setter
    def countdown_target_date(self, value: str) -> None:
        if self._countdown_target_date != value:
            self._countdown_target_date = value
            self.setting_changed.emit("countdown_target_date", value)

    @property
    def countdown_label(self) -> str:
        """倒计时标签"""
        return self._countdown_label

    @countdown_label.setter
    def countdown_label(self, value: str) -> None:
        if self._countdown_label != value:
            self._countdown_label = value
            self.setting_changed.emit("countdown_label", value)

    @property
    def time_format(self) -> str:
        """时间显示格式"""
        return self._time_format

    @time_format.setter
    def time_format(self, value: str) -> None:
        if self._time_format != value:
            self._time_format = value
            self.setting_changed.emit("time_format", value)

    @property
    def date_format(self) -> str:
        """日期显示格式"""
        return self._date_format

    @date_format.setter
    def date_format(self, value: str) -> None:
        if self._date_format != value:
            self._date_format = value
            self.setting_changed.emit("date_format", value)

    @property
    def schedule_display_mode(self) -> int:
        """课程表显示模式 (0=当前课程, 1=全天课程)"""
        return self._schedule_display_mode

    @schedule_display_mode.setter
    def schedule_display_mode(self, value: int) -> None:
        if self._schedule_display_mode != value:
            self._schedule_display_mode = value
            self.setting_changed.emit("schedule_display_mode", value)
