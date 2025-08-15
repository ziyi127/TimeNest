"""
统计分析数据模型
定义课程统计、时间统计、教师统计等相关的核心数据结构
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CourseStatistics:
    """课程统计模型"""
    total_courses: int = 0
    courses_by_teacher: Optional[Dict[str, int]] = None
    courses_by_location: Optional[Dict[str, int]] = None
    courses_by_day: Optional[Dict[int, int]] = None  # 0-6, 0表示星期日
    
    def __post_init__(self):
        """初始化后处理"""
        if self.courses_by_teacher is None:
            self.courses_by_teacher = {}
        if self.courses_by_location is None:
            self.courses_by_location = {}
        if self.courses_by_day is None:
            self.courses_by_day = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_courses': self.total_courses,
            'courses_by_teacher': self.courses_by_teacher,
            'courses_by_location': self.courses_by_location,
            'courses_by_day': self.courses_by_day
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CourseStatistics':
        """从字典创建CourseStatistics实例"""
        return cls(
            total_courses=data.get('total_courses', 0),
            courses_by_teacher=data.get('courses_by_teacher', {}),
            courses_by_location=data.get('courses_by_location', {}),
            courses_by_day=data.get('courses_by_day', {})
        )


@dataclass
class TimeStatistics:
    """时间统计模型"""
    total_class_hours: float = 0.0
    class_hours_by_day: Optional[Dict[int, float]] = None  # 0-6, 0表示星期日
    class_hours_by_teacher: Optional[Dict[str, float]] = None
    peak_hours: Optional[List[str]] = None  # 最繁忙的时间段
    
    def __post_init__(self):
        """初始化后处理"""
        if self.class_hours_by_day is None:
            self.class_hours_by_day = {}
        if self.class_hours_by_teacher is None:
            self.class_hours_by_teacher = {}
        if self.peak_hours is None:
            self.peak_hours = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_class_hours': self.total_class_hours,
            'class_hours_by_day': self.class_hours_by_day,
            'class_hours_by_teacher': self.class_hours_by_teacher,
            'peak_hours': self.peak_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeStatistics':
        """从字典创建TimeStatistics实例"""
        return cls(
            total_class_hours=data.get('total_class_hours', 0.0),
            class_hours_by_day=data.get('class_hours_by_day', {}),
            class_hours_by_teacher=data.get('class_hours_by_teacher', {}),
            peak_hours=data.get('peak_hours', [])
        )


@dataclass
class TeacherStatistics:
    """教师统计模型"""
    total_teachers: int = 0
    courses_per_teacher: Optional[Dict[str, int]] = None
    hours_per_teacher: Optional[Dict[str, float]] = None
    most_busy_teachers: Optional[List[str]] = None  # 最繁忙的教师列表
    
    def __post_init__(self):
        """初始化后处理"""
        if self.courses_per_teacher is None:
            self.courses_per_teacher = {}
        if self.hours_per_teacher is None:
            self.hours_per_teacher = {}
        if self.most_busy_teachers is None:
            self.most_busy_teachers = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_teachers': self.total_teachers,
            'courses_per_teacher': self.courses_per_teacher,
            'hours_per_teacher': self.hours_per_teacher,
            'most_busy_teachers': self.most_busy_teachers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeacherStatistics':
        """从字典创建TeacherStatistics实例"""
        return cls(
            total_teachers=data.get('total_teachers', 0),
            courses_per_teacher=data.get('courses_per_teacher', {}),
            hours_per_teacher=data.get('hours_per_teacher', {}),
            most_busy_teachers=data.get('most_busy_teachers', [])
        )