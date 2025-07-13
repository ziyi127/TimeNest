# -*- coding: utf-8 -*-
"""
TimeNest 课程表数据模型
定义课程表相关的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import time, date
import uuid

@dataclass
class Subject:
    """科目类"""
    id: str
    name: str
    color: str = "#2196F3"  # 默认蓝色
    description: str = ""
    teacher: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'teacher': self.teacher
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subject':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            color=data.get('color', '#2196F3'),
            description=data.get('description', ''),
            teacher=data.get('teacher', '')
        )

@dataclass
class TimeSlot:
    """时间段类"""
    id: str
    name: str
    start_time: time
    end_time: time
    break_duration: int = 10  # 课间休息时间（分钟）
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    @property
    def duration_minutes(self) -> int:
        """获取时间段持续时间（分钟）"""
        start_seconds = self.start_time.hour * 3600 + self.start_time.minute * 60 + self.start_time.second
        end_seconds = self.end_time.hour * 3600 + self.end_time.minute * 60 + self.end_time.second
        return (end_seconds - start_seconds) // 60
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.strftime('%H:%M:%S'),
            'end_time': self.end_time.strftime('%H:%M:%S'),
            'break_duration': self.break_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSlot':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            start_time=time.fromisoformat(data.get('start_time', '00:00:00')),
            end_time=time.fromisoformat(data.get('end_time', '00:00:00')),
            break_duration=data.get('break_duration', 10)
        )

@dataclass
class ClassItem:
    """课程项类"""
    id: str
    subject_id: str
    time_slot_id: str
    weekday: str  # monday, tuesday, wednesday, thursday, friday, saturday, sunday
    classroom: str = ""
    teacher: str = ""
    notes: str = ""
    is_active: bool = True
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'time_slot_id': self.time_slot_id,
            'weekday': self.weekday,
            'classroom': self.classroom,
            'teacher': self.teacher,
            'notes': self.notes,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassItem':
        return cls(
            id=data.get('id', ''),
            subject_id=data.get('subject_id', ''),
            time_slot_id=data.get('time_slot_id', ''),
            weekday=data.get('weekday', ''),
            classroom=data.get('classroom', ''),
            teacher=data.get('teacher', ''),
            notes=data.get('notes', ''),
            is_active=data.get('is_active', True)
        )

@dataclass
class Schedule:
    """课程表类"""
    name: str
    time_slots: List[TimeSlot] = field(default_factory=list)
    subjects: List[Subject] = field(default_factory=list)
    classes: List[ClassItem] = field(default_factory=list)
    description: str = ""
    created_date: Optional[date] = None
    modified_date: Optional[date] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = date.today()
        if self.modified_date is None:
            self.modified_date = date.today()
    
    def add_time_slot(self, time_slot: TimeSlot):
        """添加时间段"""
        if not any(ts.id == time_slot.id for ts in self.time_slots):
            self.time_slots.append(time_slot)
            self.modified_date = date.today()
    
    def remove_time_slot(self, time_slot_id: str):
        """移除时间段"""
        self.time_slots = [ts for ts in self.time_slots if ts.id != time_slot_id]
        # 同时移除使用该时间段的课程
        self.classes = [c for c in self.classes if c.time_slot_id != time_slot_id]
        self.modified_date = date.today()
    
    def get_time_slot(self, time_slot_id: str) -> Optional[TimeSlot]:
        """获取时间段"""
        for time_slot in self.time_slots:
            if time_slot.id == time_slot_id:
                return time_slot
        return None
    
    def add_subject(self, subject: Subject):
        """添加科目"""
        if not any(s.id == subject.id for s in self.subjects):
            self.subjects.append(subject)
            self.modified_date = date.today()
    
    def remove_subject(self, subject_id: str):
        """移除科目"""
        self.subjects = [s for s in self.subjects if s.id != subject_id]
        # 同时移除使用该科目的课程
        self.classes = [c for c in self.classes if c.subject_id != subject_id]
        self.modified_date = date.today()
    
    def get_subject(self, subject_id: str) -> Optional[Subject]:
        """获取科目"""
        for subject in self.subjects:
            if subject.id == subject_id:
                return subject
        return None
    
    def add_class(self, class_item: ClassItem):
        """添加课程"""
        # 检查是否已存在相同时间和星期的课程
        existing_class = self.get_class_by_time_and_weekday(class_item.time_slot_id, class_item.weekday)
        if existing_class:
            # 替换现有课程
            self.remove_class(existing_class.id)
        
        self.classes.append(class_item)
        self.modified_date = date.today()
    
    def remove_class(self, class_id: str):
        """移除课程"""
        self.classes = [c for c in self.classes if c.id != class_id]
        self.modified_date = date.today()
    
    def update_class(self, class_item: ClassItem):
        """更新课程"""
        for i, existing_class in enumerate(self.classes):
            if existing_class.id == class_item.id:
                self.classes[i] = class_item
                self.modified_date = date.today()
                break
    
    def get_class(self, class_id: str) -> Optional[ClassItem]:
        """获取课程"""
        for class_item in self.classes:
            if class_item.id == class_id:
                return class_item
        return None
    
    def get_class_by_time_and_weekday(self, time_slot_id: str, weekday: str) -> Optional[ClassItem]:
        """根据时间段和星期获取课程"""
        for class_item in self.classes:
            if class_item.time_slot_id == time_slot_id and class_item.weekday == weekday:
                return class_item
        return None
    
    def get_classes_by_weekday(self, weekday: str) -> List[ClassItem]:
        """获取指定星期的所有课程"""
        classes = [c for c in self.classes if c.weekday == weekday and c.is_active]
        # 按时间段排序
        time_slot_order = {ts.id: i for i, ts in enumerate(self.time_slots)}
        classes.sort(key=lambda c: time_slot_order.get(c.time_slot_id, 999))
        return classes
    
    def get_classes_by_subject(self, subject_id: str) -> List[ClassItem]:
        """获取指定科目的所有课程"""
        return [c for c in self.classes if c.subject_id == subject_id and c.is_active]
    
    def get_weekday_schedule_matrix(self) -> Dict[str, Dict[str, Optional[ClassItem]]]:
        """获取课程表矩阵（星期 -> 时间段 -> 课程）"""
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        matrix = {}
        
        for weekday in weekdays:
            matrix[weekday] = {}
            for time_slot in self.time_slots:
                matrix[weekday][time_slot.id] = self.get_class_by_time_and_weekday(time_slot.id, weekday)
        
        return matrix
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None,
            'time_slots': [ts.to_dict() for ts in self.time_slots],
            'subjects': [s.to_dict() for s in self.subjects],
            'classes': [c.to_dict() for c in self.classes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        schedule = cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            created_date=date.fromisoformat(data.get('created_date')) if data.get('created_date') else None,
            modified_date=date.fromisoformat(data.get('modified_date')) if data.get('modified_date') else None
        )
        
        # 加载时间段
        for ts_data in data.get('time_slots', []):
            schedule.time_slots.append(TimeSlot.from_dict(ts_data))
        
        # 加载科目
        for s_data in data.get('subjects', []):
            schedule.subjects.append(Subject.from_dict(s_data))
        
        # 加载课程
        for c_data in data.get('classes', []):
            schedule.classes.append(ClassItem.from_dict(c_data))
        
        return schedule

    def validate(self) -> List[str]:
        """验证课程表数据的完整性"""
        errors = []

        # 检查时间段
        if not self.time_slots:
            errors.append("课程表必须包含至少一个时间段")

        # 检查科目
        if not self.subjects:
            errors.append("课程表必须包含至少一个科目")

        # 检查课程引用的时间段和科目是否存在
        time_slot_ids = {ts.id for ts in self.time_slots}
        subject_ids = {s.id for s in self.subjects}

        for class_item in self.classes:
            if class_item.time_slot_id not in time_slot_ids:
                errors.append(f"课程 {class_item.id} 引用了不存在的时间段 {class_item.time_slot_id}")


            if class_item.subject_id not in subject_ids:
                errors.append(f"课程 {class_item.id} 引用了不存在的科目 {class_item.subject_id}")

        return errors

    def get_statistics(self) -> Dict[str, Any]:
        """获取课程表统计信息"""
        total_classes = len([c for c in self.classes if c.is_active])
        subject_count = {}
        weekday_count = {}

        for class_item in self.classes:
            if not class_item.is_active:
                continue

            # 统计科目课程数量
            subject = self.get_subject(class_item.subject_id)
            if subject:
                subject_count[subject.name] = subject_count.get(subject.name, 0) + 1

            # 统计每天课程数量
            weekday_count[class_item.weekday] = weekday_count.get(class_item.weekday, 0) + 1

        return {
            'total_classes': total_classes,
            'total_subjects': len(self.subjects),
            'total_time_slots': len(self.time_slots),
            'subject_distribution': subject_count,
            'weekday_distribution': weekday_count
        }


@dataclass
class TimeLayoutItem:
    """时间布局项类 - 对应文档中的TimeLayoutItem"""
    id: str
    name: str
    start_time: time
    end_time: time
    index: int = 0  # 在时间布局中的索引
    is_enabled: bool = True
    break_time: int = 10  # 课间休息时间（分钟）

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    @property
    def duration_minutes(self) -> int:
        """获取持续时间（分钟）"""
        start_seconds = self.start_time.hour * 3600 + self.start_time.minute * 60 + self.start_time.second
        end_seconds = self.end_time.hour * 3600 + self.end_time.minute * 60 + self.end_time.second
        return (end_seconds - start_seconds) // 60

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.strftime('%H:%M:%S'),
            'end_time': self.end_time.strftime('%H:%M:%S'),
            'index': self.index,
            'is_enabled': self.is_enabled,
            'break_time': self.break_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeLayoutItem':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            start_time=time.fromisoformat(data.get('start_time', '00:00:00')),
            end_time=time.fromisoformat(data.get('end_time', '00:00:00')),
            index=data.get('index', 0),
            is_enabled=data.get('is_enabled', True),
            break_time=data.get('break_time', 10)
        )


@dataclass
class TimeLayout:
    """时间布局类 - 对应文档中的TimeLayout"""
    id: str
    name: str
    time_layout_items: List[TimeLayoutItem] = field(default_factory=list)
    description: str = ""
    is_enabled: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def add_time_layout_item(self, item: TimeLayoutItem):
        """添加时间布局项"""
        if not any(tli.id == item.id for tli in self.time_layout_items):
            self.time_layout_items.append(item)
            # 重新排序
            self.time_layout_items.sort(key=lambda x: x.index)

    def remove_time_layout_item(self, item_id: str):
        """移除时间布局项"""
        self.time_layout_items = [tli for tli in self.time_layout_items if tli.id != item_id]

    def get_time_layout_item(self, item_id: str) -> Optional[TimeLayoutItem]:
        """获取时间布局项"""
        for item in self.time_layout_items:
            if item.id == item_id:
                return item
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'time_layout_items': [item.to_dict() for item in self.time_layout_items]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeLayout':
        layout = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_enabled=data.get('is_enabled', True)
        )

        # 加载时间布局项
        for item_data in data.get('time_layout_items', []):
            layout.time_layout_items.append(TimeLayoutItem.from_dict(item_data))

        return layout


@dataclass
class ClassPlan:
    """课程计划类 - 对应文档中的ClassPlan"""
    id: str
    name: str
    time_layout: Optional[TimeLayout] = None
    time_layout_id: str = ""
    description: str = ""
    is_enabled: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'time_layout_id': self.time_layout_id,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'time_layout': self.time_layout.to_dict() if self.time_layout else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassPlan':
        plan = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            time_layout_id=data.get('time_layout_id', ''),
            description=data.get('description', ''),
            is_enabled=data.get('is_enabled', True),
            start_date=date.fromisoformat(data.get('start_date')) if data.get('start_date') else None,
            end_date=date.fromisoformat(data.get('end_date')) if data.get('end_date') else None
        )

        # 加载时间布局
        if data.get('time_layout'):
            plan.time_layout = TimeLayout.from_dict(data.get('time_layout'))

        return plan