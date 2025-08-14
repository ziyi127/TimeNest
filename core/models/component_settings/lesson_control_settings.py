from PySide6.QtCore import QObject, Signal


class LessonControlSettings(QObject):
    """课程表控制设置，基于ClassIsland的LessonControlSettings实现"""
    
    # 定义设置更改时发出的信号
    setting_changed = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self._show_extra_info_on_time_point: bool = True
        self._extra_info_type: int = 0
        self._is_countdown_enabled: bool = True
        self._countdown_seconds: int = 60
        self._extra_info4_show_seconds_seconds: int = 0
        self._schedule_spacing: float = 1.0
        self._show_current_lesson_only_on_class: bool = False
        self._hide_finished_class: bool = False
        self._show_placeholder_on_empty_class_plan: bool = True
        self._placeholder_text_no_class: str = "今天没有课程。"
        self._placeholder_text_all_class_ended: str = "今日课程已全部结束。"
        self._tomorrow_schedule_show_mode: int = 1  # 0=不显示, 1=放学后显示, 2=总是显示
        self._highlight_changed_class: bool = False
        self._is_non_exact_countdown_enabled: bool = False
        self._class_change_highlight_color: str = "#FFD700"  # 金色高亮
        self._class_change_highlight_duration: int = 3000  # 高亮持续时间，单位毫秒
        
        # 浮动窗口透明度设置
        self._floating_window_hover_transparency: float = 0.3  # 鼠标悬停时的透明度
        self._floating_window_touch_transparency: float = 0.2   # 触控点击时的透明度
        self._enable_floating_window_hover_effect: bool = True  # 是否启用悬停透明效果
        self._enable_floating_window_touch_effect: bool = True  # 是否启用触控透明效果

    @property
    def show_extra_info_on_time_point(self) -> bool:
        """是否在当前时间点上显示附加信息"""
        return self._show_extra_info_on_time_point

    @show_extra_info_on_time_point.setter
    def show_extra_info_on_time_point(self, value: bool) -> None:
        if self._show_extra_info_on_time_point != value:
            self._show_extra_info_on_time_point = value
            self.setting_changed.emit("show_extra_info_on_time_point", value)

    @property
    def extra_info_type(self) -> int:
        """时间点附加信息类型"""
        return self._extra_info_type

    @extra_info_type.setter
    def extra_info_type(self, value: int) -> None:
        if self._extra_info_type != value:
            self._extra_info_type = value
            self.setting_changed.emit("extra_info_type", value)

    @property
    def is_countdown_enabled(self) -> bool:
        """是否启用时间点结束倒计时"""
        return self._is_countdown_enabled

    @is_countdown_enabled.setter
    def is_countdown_enabled(self, value: bool) -> None:
        if self._is_countdown_enabled != value:
            self._is_countdown_enabled = value
            self.setting_changed.emit("is_countdown_enabled", value)

    @property
    def countdown_seconds(self) -> int:
        """时间点结束倒计时时长"""
        return self._countdown_seconds

    @countdown_seconds.setter
    def countdown_seconds(self, value: int) -> None:
        if self._countdown_seconds != value:
            self._countdown_seconds = value
            self.setting_changed.emit("countdown_seconds", value)

    @property
    def extra_info4_show_seconds_seconds(self) -> int:
        """时间点剩余时间精确到秒时长"""
        return self._extra_info4_show_seconds_seconds

    @extra_info4_show_seconds_seconds.setter
    def extra_info4_show_seconds_seconds(self, value: int) -> None:
        if self._extra_info4_show_seconds_seconds != value:
            self._extra_info4_show_seconds_seconds = value
            self.setting_changed.emit("extra_info4_show_seconds_seconds", value)

    @property
    def schedule_spacing(self) -> float:
        """课程表文字间距"""
        return self._schedule_spacing

    @schedule_spacing.setter
    def schedule_spacing(self, value: float) -> None:
        if self._schedule_spacing != value:
            self._schedule_spacing = value
            self.setting_changed.emit("schedule_spacing", value)

    @property
    def show_current_lesson_only_on_class(self) -> bool:
        """是否在上课时仅显示当前课程"""
        return self._show_current_lesson_only_on_class

    @show_current_lesson_only_on_class.setter
    def show_current_lesson_only_on_class(self, value: bool) -> None:
        if self._show_current_lesson_only_on_class != value:
            self._show_current_lesson_only_on_class = value
            self.setting_changed.emit("show_current_lesson_only_on_class", value)

    @property
    def is_non_exact_countdown_enabled(self) -> bool:
        """是否启用模糊倒计时"""
        return self._is_non_exact_countdown_enabled

    @is_non_exact_countdown_enabled.setter
    def is_non_exact_countdown_enabled(self, value: bool) -> None:
        if self._is_non_exact_countdown_enabled != value:
            self._is_non_exact_countdown_enabled = value
            self.setting_changed.emit("is_non_exact_countdown_enabled", value)

    @property
    def show_placeholder_on_empty_class_plan(self) -> bool:
        """是否在空课表时显示占位符"""
        return self._show_placeholder_on_empty_class_plan

    @show_placeholder_on_empty_class_plan.setter
    def show_placeholder_on_empty_class_plan(self, value: bool) -> None:
        if self._show_placeholder_on_empty_class_plan != value:
            self._show_placeholder_on_empty_class_plan = value
            self.setting_changed.emit("show_placeholder_on_empty_class_plan", value)

    @property
    def placeholder_text_no_class(self) -> str:
        """无课表时的占位符文本"""
        return self._placeholder_text_no_class

    @placeholder_text_no_class.setter
    def placeholder_text_no_class(self, value: str) -> None:
        if self._placeholder_text_no_class != value:
            self._placeholder_text_no_class = value
            self.setting_changed.emit("placeholder_text_no_class", value)

    @property
    def placeholder_text_all_class_ended(self) -> str:
        """课程结束时的占位符文本"""
        return self._placeholder_text_all_class_ended

    @placeholder_text_all_class_ended.setter
    def placeholder_text_all_class_ended(self, value: str) -> None:
        if self._placeholder_text_all_class_ended != value:
            self._placeholder_text_all_class_ended = value
            self.setting_changed.emit("placeholder_text_all_class_ended", value)

    @property
    def tomorrow_schedule_show_mode(self) -> int:
        """明天课表显示模式 (0=不显示, 1=放学后显示, 2=总是显示)"""
        return self._tomorrow_schedule_show_mode

    @tomorrow_schedule_show_mode.setter
    def tomorrow_schedule_show_mode(self, value: int) -> None:
        if self._tomorrow_schedule_show_mode != value:
            self._tomorrow_schedule_show_mode = value
            self.setting_changed.emit("tomorrow_schedule_show_mode", value)

    @property
    def highlight_changed_class(self) -> bool:
        """是否高亮变更的课程"""
        return self._highlight_changed_class

    @highlight_changed_class.setter
    def highlight_changed_class(self, value: bool) -> None:
        if self._highlight_changed_class != value:
            self._highlight_changed_class = value
            self.setting_changed.emit("highlight_changed_class", value)

    @property
    def hide_finished_class(self) -> bool:
        """是否隐藏已结束的课程"""
        return self._hide_finished_class

    @hide_finished_class.setter
    def hide_finished_class(self, value: bool) -> None:
        if self._hide_finished_class != value:
            self._hide_finished_class = value
            self.setting_changed.emit("hide_finished_class", value)

    @property
    def class_change_highlight_color(self) -> str:
        """课程变更高亮颜色"""
        return self._class_change_highlight_color

    @class_change_highlight_color.setter
    def class_change_highlight_color(self, value: str) -> None:
        if self._class_change_highlight_color != value:
            self._class_change_highlight_color = value
            self.setting_changed.emit("class_change_highlight_color", value)

    @property
    def class_change_highlight_duration(self) -> int:
        """课程变更高亮持续时间(毫秒)"""
        return self._class_change_highlight_duration

    @class_change_highlight_duration.setter
    def class_change_highlight_duration(self, value: int) -> None:
        if self._class_change_highlight_duration != value:
            self._class_change_highlight_duration = value
            self.setting_changed.emit("class_change_highlight_duration", value)
            
    # 浮动窗口透明度相关设置
    
    @property
    def floating_window_hover_transparency(self) -> float:
        """浮动窗口鼠标悬停时的透明度 (0.0-1.0)"""
        return self._floating_window_hover_transparency

    @floating_window_hover_transparency.setter
    def floating_window_hover_transparency(self, value: float) -> None:
        # 确保值在有效范围内
        value = max(0.0, min(1.0, value))
        if self._floating_window_hover_transparency != value:
            self._floating_window_hover_transparency = value
            self.setting_changed.emit("floating_window_hover_transparency", value)
            
    @property
    def floating_window_touch_transparency(self) -> float:
        """浮动窗口触控点击时的透明度 (0.0-1.0)"""
        return self._floating_window_touch_transparency

    @floating_window_touch_transparency.setter
    def floating_window_touch_transparency(self, value: float) -> None:
        # 确保值在有效范围内
        value = max(0.0, min(1.0, value))
        if self._floating_window_touch_transparency != value:
            self._floating_window_touch_transparency = value
            self.setting_changed.emit("floating_window_touch_transparency", value)
            
    @property
    def enable_floating_window_hover_effect(self) -> bool:
        """是否启用浮动窗口鼠标悬停透明效果"""
        return self._enable_floating_window_hover_effect

    @enable_floating_window_hover_effect.setter
    def enable_floating_window_hover_effect(self, value: bool) -> None:
        if self._enable_floating_window_hover_effect != value:
            self._enable_floating_window_hover_effect = value
            self.setting_changed.emit("enable_floating_window_hover_effect", value)
            
    @property
    def enable_floating_window_touch_effect(self) -> bool:
        """是否启用浮动窗口触控透明效果"""
        return self._enable_floating_window_touch_effect

    @enable_floating_window_touch_effect.setter
    def enable_floating_window_touch_effect(self, value: bool) -> None:
        if self._enable_floating_window_touch_effect != value:
            self._enable_floating_window_touch_effect = value
            self.setting_changed.emit("enable_floating_window_touch_effect", value)
