[{
	"resource": "/home/archlinux/桌面/TimeNest-Dev/services/statistics_service.py",
	"owner": "pylance",
	"code": {
		"value": "reportUnusedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUnusedVariable.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 8,
	"message": "无法存取变量“courses”",
	"source": "Pylance",
	"startLineNumber": 97,
	"startColumn": 13,
	"endLineNumber": 97,
	"endColumn": 20,
	"origin": "extHost2"
},{
	"resource": "/home/archlinux/桌面/TimeNest-Dev/services/statistics_service.py",
	"owner": "pylance",
	"code": {
		"value": "reportUnknownVariableType",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUnknownVariableType.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 8,
	"message": "“stats”的类型部分未知\n  “stats”的类型为“dict[str, Unknown]”",
	"source": "Pylance",
	"startLineNumber": 258,
	"startColumn": 9,
	"endLineNumber": 258,
	"endColumn": 14,
	"origin": "extHost2"
},{
	"resource": "/home/archlinux/桌面/TimeNest-Dev/services/statistics_service.py",
	"owner": "pylance",
	"code": {
		"value": "reportUnknownVariableType",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pylance-release/blob/main/docs/diagnostics/reportUnknownVariableType.md",
			"scheme": "https",
			"authority": "github.com"
		}
	},
	"severity": 8,
	"message": "返回类型“dict[str, Unknown]”部分未知",
	"source": "Pylance",
	"startLineNumber": 265,
	"startColumn": 16,
	"endLineNumber": 265,
	"endColumn": 21,
	"origin": "extHost2"
}]#!/usr/bin/env python3
"""
模型模块初始化文件
导出所有数据模型类
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

# 天气相关模型
from .weather_data import WeatherData, WeatherSettings

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
    
    # 天气相关模型
    'WeatherData',
    'WeatherSettings',
]
