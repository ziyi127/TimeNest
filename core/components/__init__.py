"""
TimeNest 组件包
包含所有核心组件的导入和初始化
"""

from typing import Dict, List

# 导入所有组件
from .base_component import BaseComponent, ComponentSettings
from .clock_component import ClockComponent
from .countdown_component import CountDownComponent
from .date_component import DateComponent
from .floating_window import FloatingWindow
from .group_component import GroupComponent
from .notifier import Notifier, get_notifier
from .rolling_component import RollingComponent
from .separator_component import SeparatorComponent
from .slide_component import SlideComponent
from .text_component import TextComponent
from .theme_manager import ThemeManager
from .tray_icon import TrayIcon, create_tray_icon, get_tray_icon
from .weather_component import WeatherComponent

# 组件列表
COMPONENTS: List[type] = [
    ClockComponent,
    DateComponent,
    TextComponent,
    WeatherComponent,
    CountDownComponent,
    RollingComponent,
    GroupComponent,
    SlideComponent,
    SeparatorComponent,
]

# 组件名称映射
COMPONENT_NAMES: Dict[str, type] = {
    "时钟": ClockComponent,
    "日期": DateComponent,
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
    "BaseComponent",
    "ComponentSettings",
    "ClockComponent",
    "DateComponent",
    "TextComponent",
    "WeatherComponent",
    "CountDownComponent",
    "RollingComponent",
    "GroupComponent",
    "SlideComponent",
    "SeparatorComponent",
    "FloatingWindow",
    "ThemeManager",
    "TrayIcon",
    "create_tray_icon",
    "get_tray_icon",
    "Notifier",
    "get_notifier",
    "COMPONENTS",
    "COMPONENT_NAMES",
]
