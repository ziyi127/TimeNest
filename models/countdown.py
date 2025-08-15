"""
倒计时数据模型
定义倒计时相关的核心数据结构
"""

from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CountdownItem:
    """倒计时项目模型类"""
    id: str
    name: str
    target_date: str  # YYYY-MM-DD
    description: str = ""
    is_important: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CountdownItem':
        """从字典创建CountdownItem实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            target_date=data['target_date'],
            description=data.get('description', ''),
            is_important=data.get('is_important', False)
        )


@dataclass
class CountdownSettings:
    """倒计时设置模型类"""
    enabled: bool = True
    show_in_dashboard: bool = True
    notification_enabled: bool = True
    notification_time: str = "09:00"  # HH:MM
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CountdownSettings':
        """从字典创建CountdownSettings实例"""
        return cls(
            enabled=data.get('enabled', True),
            show_in_dashboard=data.get('show_in_dashboard', True),
            notification_enabled=data.get('notification_enabled', True),
            notification_time=data.get('notification_time', '09:00')
        )