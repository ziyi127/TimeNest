"""
开机启动配置数据模型
定义开机启动配置相关的核心数据结构
"""

from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class StartupItem:
    """开机启动项模型类"""
    id: str
    name: str
    executable_path: str
    enabled: bool = True
    arguments: str = ""
    working_directory: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StartupItem':
        """从字典创建StartupItem实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            executable_path=data['executable_path'],
            enabled=data.get('enabled', True),
            arguments=data.get('arguments', ''),
            working_directory=data.get('working_directory', ''),
            description=data.get('description', '')
        )


@dataclass
class StartupSettings:
    """开机启动设置模型类"""
    enabled: bool = True
    allow_user_config: bool = True
    max_startup_items: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StartupSettings':
        """从字典创建StartupSettings实例"""
        return cls(
            enabled=data.get('enabled', True),
            allow_user_config=data.get('allow_user_config', True),
            max_startup_items=data.get('max_startup_items', 10)
        )