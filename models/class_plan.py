"""
<<<<<<< HEAD
课程计划数据模型
定义课程计划相关的核心数据结构
=======
课程表模型类
对应架构设计文档中的Schedule模型
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ClassPlan:
    """课程表模型类"""
    id: str
    day_of_week: int  # 0-6, 0表示星期日
    week_parity: str  # "odd"表示奇数周, "even"表示偶数周, "both"表示每周
    course_id: str
    valid_from: str  # 日期格式: YYYY-MM-DD
    valid_to: str    # 日期格式: YYYY-MM-DD
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassPlan':
        """从字典创建ClassPlan实例"""
        return cls(
            id=data['id'],
            day_of_week=data['day_of_week'],
            week_parity=data['week_parity'],
            course_id=data['course_id'],
            valid_from=data['valid_from'],
            valid_to=data['valid_to']
        )
