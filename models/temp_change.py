"""
<<<<<<< HEAD
临时换课数据模型
定义临时换课相关的核心数据结构
=======
临时换课模型类
对应架构设计文档中的TempChange模型
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class TempChange:
    """临时换课模型类"""
    id: str
    original_schedule_id: str
    new_course_id: str
    change_date: str  # 日期格式: YYYY-MM-DD
    is_permanent: bool = False
    used: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TempChange':
        """从字典创建TempChange实例"""
        return cls(
            id=data['id'],
            original_schedule_id=data['original_schedule_id'],
            new_course_id=data['new_course_id'],
            change_date=data['change_date'],
            is_permanent=data.get('is_permanent', False),
            used=data.get('used', False)
        )
