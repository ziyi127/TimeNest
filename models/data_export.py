"""
数据导出模型类
用于数据导入导出功能
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ExportFormat(Enum):
    """导出格式枚举"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


@dataclass
class DataExportConfig:
    """数据导出配置模型"""
    format: ExportFormat = ExportFormat.JSON  # 导出格式
    include_courses: bool = True              # 是否包含课程数据
    include_schedules: bool = True            # 是否包含课程表数据
    include_temp_changes: bool = True         # 是否包含临时换课数据
    include_cycle_schedules: bool = True      # 是否包含循环课程表数据
    export_date_range: Optional[Dict[str, str]] = None  # 导出日期范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'format': self.format.value,
            'include_courses': self.include_courses,
            'include_schedules': self.include_schedules,
            'include_temp_changes': self.include_temp_changes,
            'include_cycle_schedules': self.include_cycle_schedules,
            'export_date_range': self.export_date_range
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataExportConfig':
        """从字典创建DataExportConfig实例"""
        format_str = data.get('format', 'json')
        format_enum = ExportFormat(format_str) if format_str in [f.value for f in ExportFormat] else ExportFormat.JSON
        
        return cls(
            format=format_enum,
            include_courses=data.get('include_courses', True),
            include_schedules=data.get('include_schedules', True),
            include_temp_changes=data.get('include_temp_changes', True),
            include_cycle_schedules=data.get('include_cycle_schedules', True),
            export_date_range=data.get('export_date_range')
        )


@dataclass
class DataImportConfig:
    """数据导入配置模型"""
    format: ExportFormat = ExportFormat.JSON  # 导入格式
    overwrite_existing: bool = False          # 是否覆盖现有数据
    validate_data: bool = True                # 是否验证数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'format': self.format.value,
            'overwrite_existing': self.overwrite_existing,
            'validate_data': self.validate_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataImportConfig':
        """从字典创建DataImportConfig实例"""
        format_str = data.get('format', 'json')
        format_enum = ExportFormat(format_str) if format_str in [f.value for f in ExportFormat] else ExportFormat.JSON
        
        return cls(
            format=format_enum,
            overwrite_existing=data.get('overwrite_existing', False),
            validate_data=data.get('validate_data', True)
        )