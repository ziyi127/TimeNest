"""
TimeNest 数据模型模块
包含所有数据模型类的定义
"""

# 课程相关模型
from .class_item import ClassItem, TimeSlot
from .class_plan import ClassPlan
from .cycle_schedule import CycleSchedule, CycleScheduleItem, ScheduleItem
from .temp_change import TempChange

# 用户和权限相关模型
from .user_settings import UserSettings
from .password_config import PasswordConfig

# 通知相关模型
from .notification import Notification

# 统计分析相关模型
from .statistics import CourseStatistics, TimeStatistics, TeacherStatistics

# 数据导入导出相关模型
from .data_export import DataExportConfig, DataImportConfig, ExportFormat

# 备份恢复相关模型
from .backup import BackupInfo, BackupConfig

# 插件相关模型
from .plugin_config import PluginConfig

# 确保所有模型都被正确导出
__all__ = [
    # 课程相关模型
    'ClassItem',
    'TimeSlot',
    'ClassPlan',
    'CycleSchedule',
    'CycleScheduleItem',
    'ScheduleItem',
    'TempChange',
    
    # 用户和权限相关模型
    'UserSettings',
    'PasswordConfig',
    
    # 通知相关模型
    'Notification',
    
    # 统计分析相关模型
    'CourseStatistics',
    'TimeStatistics',
    'TeacherStatistics',
    
    # 数据导入导出相关模型
    'DataExportConfig',
    'DataImportConfig',
    'ExportFormat',
    
    # 备份恢复相关模型
    'BackupInfo',
    'BackupConfig',
    
    # 插件相关模型
    'PluginConfig',
]
