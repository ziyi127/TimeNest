"""
循环课程表模型类
对应架构设计文档中的CycleSchedule模型
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ScheduleItem:
    """课程表项"""
    day_of_week: int  # 0-6, 0表示星期日
    course_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'day_of_week': self.day_of_week,
            'course_id': self.course_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduleItem':
        """从字典创建ScheduleItem实例"""
        return cls(
            day_of_week=data['day_of_week'],
            course_id=data['course_id']
        )


@dataclass
class CycleScheduleItem:
    """循环课程表项"""
    week_index: int
    schedule_items: List[ScheduleItem]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'week_index': self.week_index,
            'schedule_items': [item.to_dict() for item in self.schedule_items]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CycleScheduleItem':
        """从字典创建CycleScheduleItem实例"""
        schedule_items = [ScheduleItem.from_dict(item) for item in data['schedule_items']]
        return cls(
            week_index=data['week_index'],
            schedule_items=schedule_items
        )


@dataclass
class CycleSchedule:
    """循环课程表模型类"""
    id: str
    name: str
    cycle_length: int
    schedules: List[CycleScheduleItem]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'cycle_length': self.cycle_length,
            'schedules': [schedule.to_dict() for schedule in self.schedules]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CycleSchedule':
        """从字典创建CycleSchedule实例"""
        schedules = [CycleScheduleItem.from_dict(schedule) for schedule in data['schedules']]
        return cls(
            id=data['id'],
            name=data['name'],
            cycle_length=data['cycle_length'],
            schedules=schedules
        )