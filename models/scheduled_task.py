"""
计划任务数据模型
定义计划任务相关的核心数据结构
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class OSType(Enum):
    """操作系统类型枚举"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class TaskType(Enum):
    """任务类型枚举"""
    APPLICATION = "application"
    FILE_OPERATION = "file_operation"
    SYSTEM_COMMAND = "system_command"
    CUSTOM_SCRIPT = "custom_script"


@dataclass
class ScheduledTask:
    """计划任务模型类"""
    id: str
    name: str
    command: str
    task_type: TaskType
    os_type: OSType
    schedule: str  # cron表达式或特定格式
    enabled: bool = True
    description: str = ""
    working_directory: str = ""
    custom_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.task_type, str):
            self.task_type = TaskType(self.task_type)
        if isinstance(self.os_type, str):
            self.os_type = OSType(self.os_type)
        if self.custom_config is None:
            self.custom_config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['os_type'] = self.os_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledTask':
        """从字典创建ScheduledTask实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            command=data['command'],
            task_type=data['task_type'],
            os_type=data['os_type'],
            schedule=data['schedule'],
            enabled=data.get('enabled', True),
            description=data.get('description', ''),
            working_directory=data.get('working_directory', ''),
            custom_config=data.get('custom_config', {})
        )


@dataclass
class TaskSettings:
    """任务设置模型类"""
    enabled: bool = True
    max_concurrent_tasks: int = 5
    log_level: str = "INFO"
    default_working_directory: str = "./tasks"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskSettings':
        """从字典创建TaskSettings实例"""
        return cls(
            enabled=data.get('enabled', True),
            max_concurrent_tasks=data.get('max_concurrent_tasks', 5),
            log_level=data.get('log_level', 'INFO'),
            default_working_directory=data.get('default_working_directory', './tasks')
        )