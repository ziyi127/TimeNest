from PySide6.QtCore import QObject, Signal


class ScheduleComponentSettings(QObject):
    """课程表组件设置，基于ClassIsland的LessonControlSettings实现"""
    
    # 定义设置更改时发出的信号
    setting_changed = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self._show_extra_info_on_time_point = True
        self._extra_info_type = 0
        self._is_countdown_enabled = True
        self._countdown_seconds = 60
        self._extra_info4_show_seconds_seconds = 0
        self._schedule_spacing = 1.0
        self._show_current_lesson_only_on_class = False
        self._hide_finished_class = False
        self._show_placeholder_on_empty_class_plan = True
        self._placeholder_text_no_class = "今天没有课程。"
        self._placeholder_text_all_class_ended = "今日课程已全部结束。"
        self._tomorrow_schedule_show_mode = 1  # 0=不显示, 1=放学后显示, 2=总是显示
        self._highlight_changed_class = False
        self._is_non_exact_countdown_enabled = False
        self._class_change_highlight_color = "#FFD700"  # 金色高亮
        self._class_change_highlight_duration = 3000  # 高亮持续时间，单位毫秒

    @property
    def show_extra_info_on_time_point(self):
        """是否在当前时间点上显示附加信息"""
        return self._show_extra_info_on_time_point

    @show_extra_info_on_time_point.setter
    def show_extra_info_on_time_point(self, value):
        if self._show_extra_info_on_time_point != value:
            self._show_extra_info_on_time_point = value
            self.setting_changed.emit("show_extra_info_on_time_point", value)

    @property
    def extra_info_type(self):
        """时间点附加信息类型"""
        return self._extra_info_type

    @extra_info_type.setter
    def extra_info_type(self, value):
        if self._extra_info_type != value:
            self._extra_info_type = value
            self.setting_changed.emit("extra_info_type", value)

    @property
    def is_countdown_enabled(self):
        """是否启用时间点结束倒计时"""
        return self._is_countdown_enabled

    @is_countdown_enabled.setter
    def is_countdown_enabled(self, value):
        if self._is_countdown_enabled != value:
            self._is_countdown_enabled = value
            self.setting_changed.emit("is_countdown_enabled", value)

    @property
    def countdown_seconds(self):
        """时间点结束倒计时时长"""
        return self._countdown_seconds

    @countdown_seconds.setter
    def countdown_seconds(self, value):
        if self._countdown_seconds != value:
            self._countdown_seconds = value
            self.setting_changed.emit("countdown_seconds", value)

    @property
    def extra_info4_show_seconds_seconds(self):
        """时间点剩余时间精确到秒时长"""
        return self._extra_info4_show_seconds_seconds

    @extra_info4_show_seconds_seconds.setter
    def extra_info4_show_seconds_seconds(self, value):
        if self._extra_info4_show_seconds_seconds != value:
            self._extra_info4_show_seconds_seconds = value
            self.setting_changed.emit("extra_info4_show_seconds_seconds", value)

    @property
    def schedule_spacing(self):
        """课程表文字间距"""
        return self._schedule_spacing

    @schedule_spacing.setter
    def schedule_spacing(self, value):
        if self._schedule_spacing != value:
            self._schedule_spacing = value
            self.setting_changed.emit("schedule_spacing", value)

    @property
    def show_current_lesson_only_on_class(self):
        """是否在上课时仅显示当前课程"""
        return self._show_current_lesson_only_on_class

    @show_current_lesson_only_on_class.setter
    def show_current_lesson_only_on_class(self, value):
        if self._show_current_lesson_only_on_class != value:
            self._show_current_lesson_only_on_class = value
            self.setting_changed.emit("show_current_lesson_only_on_class", value)

    @property
    def is_non_exact_countdown_enabled(self):
        """是否启用模糊倒计时"""
        return self._is_non_exact_countdown_enabled

    @is_non_exact_countdown_enabled.setter
    def is_non_exact_countdown_enabled(self, value):
        if self._is_non_exact_countdown_enabled != value:
            self._is_non_exact_countdown_enabled = value
            self.setting_changed.emit("is_non_exact_countdown_enabled", value)

    @property
    def show_placeholder_on_empty_class_plan(self):
        """是否在空课表时显示占位符"""
        return self._show_placeholder_on_empty_class_plan

    @show_placeholder_on_empty_class_plan.setter
    def show_placeholder_on_empty_class_plan(self, value):
        if self._show_placeholder_on_empty_class_plan != value:
            self._show_placeholder_on_empty_class_plan = value
            self.setting_changed.emit("show_placeholder_on_empty_class_plan", value)

    @property
    def placeholder_text_no_class(self):
        """无课表时的占位符文本"""
        return self._placeholder_text_no_class

    @placeholder_text_no_class.setter
    def placeholder_text_no_class(self, value):
        if self._placeholder_text_no_class != value:
            self._placeholder_text_no_class = value
            self.setting_changed.emit("placeholder_text_no_class", value)

    @property
    def placeholder_text_all_class_ended(self):
        """课程结束时的占位符文本"""
        return self._placeholder_text_all_class_ended

    @placeholder_text_all_class_ended.setter
    def placeholder_text_all_class_ended(self, value):
        if self._placeholder_text_all_class_ended != value:
            self._placeholder_text_all_class_ended = value
            self.setting_changed.emit("placeholder_text_all_class_ended", value)

    @property
    def tomorrow_schedule_show_mode(self):
        """明天课表显示模式 (0=不显示, 1=放学后显示, 2=总是显示)"""
        return self._tomorrow_schedule_show_mode

    @tomorrow_schedule_show_mode.setter
    def tomorrow_schedule_show_mode(self, value):
        if self._tomorrow_schedule_show_mode != value:
            self._tomorrow_schedule_show_mode = value
            self.setting_changed.emit("tomorrow_schedule_show_mode", value)

    @property
    def highlight_changed_class(self):
        """是否高亮变更的课程"""
        return self._highlight_changed_class

    @highlight_changed_class.setter
    def highlight_changed_class(self, value):
        if self._highlight_changed_class != value:
            self._highlight_changed_class = value
            self.setting_changed.emit("highlight_changed_class", value)

    @property
    def hide_finished_class(self):
        """是否隐藏已结束的课程"""
        return self._hide_finished_class

    @hide_finished_class.setter
    def hide_finished_class(self, value):
        if self._hide_finished_class != value:
            self._hide_finished_class = value
            self.setting_changed.emit("hide_finished_class", value)

    @property
    def class_change_highlight_color(self):
        """课程变更高亮颜色"""
        return self._class_change_highlight_color

    @class_change_highlight_color.setter
    def class_change_highlight_color(self, value):
        if self._class_change_highlight_color != value:
            self._class_change_highlight_color = value
            self.setting_changed.emit("class_change_highlight_color", value)

    @property
    def class_change_highlight_duration(self):
        """课程变更高亮持续时间(毫秒)"""
        return self._class_change_highlight_duration

    @class_change_highlight_duration.setter
    def class_change_highlight_duration(self, value):
        if self._class_change_highlight_duration != value:
            self._class_change_highlight_duration = value
            self.setting_changed.emit("class_change_highlight_duration", value)