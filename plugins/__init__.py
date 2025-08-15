"""
插件系统包初始化文件
"""

from .plugin_interface import PluginInterface
from .plugin_manager import PluginManager
from .course_plugin_interface import CoursePluginInterface
from .schedule_plugin_interface import SchedulePluginInterface
from .ui_plugin_interface import UIPluginInterface
from .data_plugin_interface import DataPluginInterface
from .course_reminder_plugin import CourseReminderPlugin

__all__ = [
    "PluginInterface",
    "PluginManager",
    "CoursePluginInterface",
    "SchedulePluginInterface",
    "UIPluginInterface",
    "DataPluginInterface",
    "CourseReminderPlugin"
]