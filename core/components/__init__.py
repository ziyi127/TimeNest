"""
TimeNest 组件包
包含所有核心组件的导入和初始化
"""

# 导入所有组件
from .base_component import BaseComponent, ComponentSettings
from .clock_component import ClockComponent
from .date_component import DateComponent
from .schedule_component import ScheduleComponent
from .text_component import TextComponent
from .weather_component import WeatherComponent
from .countdown_component import CountDownComponent
from .rolling_component import RollingComponent
from .group_component import GroupComponent
from .slide_component import SlideComponent
from .separator_component import SeparatorComponent
from .floating_window import FloatingWindow
from .theme_manager import ThemeManager, get_theme_manager
from .tray_icon import TrayIcon, create_tray_icon, get_tray_icon
from .notifier import Notifier, get_notifier

# 组件列表
COMPONENTS = [
    ClockComponent,
    DateComponent,
    ScheduleComponent,
    TextComponent,
    WeatherComponent,
    CountDownComponent,
    RollingComponent,
    GroupComponent,
    SlideComponent,
    SeparatorComponent,
]

# 组件名称映射
COMPONENT_NAMES = {
    "时钟": ClockComponent,
    "日期": DateComponent,
    "课程表": ScheduleComponent,
    "文本": TextComponent,
    "天气": WeatherComponent,
    "倒计时": CountDownComponent,
    "滚动": RollingComponent,
    "分组": GroupComponent,
    "轮播": SlideComponent,
    "分割线": SeparatorComponent,
}

# 导出所有组件
__all__ = [
    'BaseComponent',
    'ComponentSettings',
    'ClockComponent',
    'DateComponent',
    'ScheduleComponent',
    'TextComponent',
    'WeatherComponent',
    'CountDownComponent',
    'RollingComponent',
    'GroupComponent',
    'SlideComponent',
    'SeparatorComponent',
    'FloatingWindow',
    'ThemeManager',
    'get_theme_manager',
    'TrayIcon',
    'create_tray_icon',
    'get_tray_icon',
    'Notifier',
    'get_notifier',
    'COMPONENTS',
    'COMPONENT_NAMES',
]
