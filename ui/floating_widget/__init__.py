#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 智能浮窗系统
仿苹果灵动岛的动态信息显示功能
"""

from .smart_floating_widget import SmartFloatingWidget
from .floating_modules import (
    FloatingModule,
    TimeModule,
    ScheduleModule,
    CountdownModule,
    WeatherModule,
    SystemStatusModule
)
from .floating_settings import FloatingSettingsDialog
from .animations import FloatingAnimations

# 为了向后兼容，将 SmartFloatingWidget 别名为 FloatingWidget
FloatingWidget = SmartFloatingWidget

__all__ = [
    'SmartFloatingWidget',
    'FloatingWidget',  # 向后兼容
    'FloatingModule',
    'TimeModule',
    'ScheduleModule',
    'CountdownModule',
    'WeatherModule',
    'SystemStatusModule',
    'FloatingSettingsDialog',
    'FloatingAnimations'
]
