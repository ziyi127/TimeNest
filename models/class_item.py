"""
<<<<<<< HEAD
课程数据模型
定义课程相关的核心数据结构

该模块包含课程和时间段的数据模型，用于表示课程信息。
=======
课程模型类
对应架构设计文档中的Course模型
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class TimeSlot:
    """时间段模型"""
    start_time: str  # 格式: HH:MM
    end_time: str    # 格式: HH:MM

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSlot':
        """从字典创建TimeSlot实例"""
        return cls(
            start_time=data['start_time'],
            end_time=data['end_time']
        )


@dataclass
class ClassItem:
    """课程模型类"""
    id: str
    name: str
    teacher: str
    location: str
    duration: TimeSlot

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'teacher': self.teacher,
            'location': self.location,
            'duration': self.duration.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassItem':
        """从字典创建ClassItem实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            teacher=data['teacher'],
            location=data['location'],
            duration=TimeSlot.from_dict(data['duration'])
        )
