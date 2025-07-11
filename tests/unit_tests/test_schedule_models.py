#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 课程表数据模型测试
"""

import unittest
from datetime import time, date
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from TimeNest.models.schedule import (
    Subject, TimeSlot, ClassItem, Schedule,
    TimeLayoutItem, TimeLayout, ClassPlan
)


class TestSubject(unittest.TestCase):
    """测试科目类"""
    
    def test_subject_creation(self):
        """测试科目创建"""
        subject = Subject(
            id="math_001",
            name="高等数学",
            color="#FF5722",
            description="数学课程",
            teacher="张教授"
        )
        
        self.assertEqual(subject.id, "math_001")
        self.assertEqual(subject.name, "高等数学")
        self.assertEqual(subject.color, "#FF5722")
        self.assertEqual(subject.description, "数学课程")
        self.assertEqual(subject.teacher, "张教授")
    
    def test_subject_auto_id(self):
        """测试自动生成ID"""
        subject = Subject(id="", name="物理")
        self.assertNotEqual(subject.id, "")
        self.assertTrue(len(subject.id) > 0)
    
    def test_subject_to_dict(self):
        """测试转换为字典"""
        subject = Subject(
            id="phys_001",
            name="物理",
            color="#2196F3",
            teacher="李老师"
        )
        
        data = subject.to_dict()
        expected = {
            'id': 'phys_001',
            'name': '物理',
            'color': '#2196F3',
            'description': '',
            'teacher': '李老师'
        }
        
        self.assertEqual(data, expected)
    
    def test_subject_from_dict(self):
        """测试从字典创建"""
        data = {
            'id': 'chem_001',
            'name': '化学',
            'color': '#4CAF50',
            'description': '化学实验课',
            'teacher': '王老师'
        }
        
        subject = Subject.from_dict(data)
        
        self.assertEqual(subject.id, 'chem_001')
        self.assertEqual(subject.name, '化学')
        self.assertEqual(subject.color, '#4CAF50')
        self.assertEqual(subject.description, '化学实验课')
        self.assertEqual(subject.teacher, '王老师')


class TestTimeSlot(unittest.TestCase):
    """测试时间段类"""
    
    def test_time_slot_creation(self):
        """测试时间段创建"""
        time_slot = TimeSlot(
            id="slot_1",
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45),
            break_duration=10
        )
        
        self.assertEqual(time_slot.id, "slot_1")
        self.assertEqual(time_slot.name, "第一节")
        self.assertEqual(time_slot.start_time, time(8, 0))
        self.assertEqual(time_slot.end_time, time(8, 45))
        self.assertEqual(time_slot.break_duration, 10)
    
    def test_duration_calculation(self):
        """测试持续时间计算"""
        time_slot = TimeSlot(
            id="slot_1",
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45)
        )
        
        self.assertEqual(time_slot.duration_minutes, 45)
    
    def test_time_slot_serialization(self):
        """测试序列化和反序列化"""
        original = TimeSlot(
            id="slot_2",
            name="第二节",
            start_time=time(9, 0),
            end_time=time(9, 45),
            break_duration=15
        )
        
        # 序列化
        data = original.to_dict()
        
        # 反序列化
        restored = TimeSlot.from_dict(data)
        
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.start_time, restored.start_time)
        self.assertEqual(original.end_time, restored.end_time)
        self.assertEqual(original.break_duration, restored.break_duration)


class TestTimeLayoutItem(unittest.TestCase):
    """测试时间布局项类"""
    
    def test_time_layout_item_creation(self):
        """测试时间布局项创建"""
        item = TimeLayoutItem(
            id="item_1",
            name="第一节课",
            start_time=time(8, 0),
            end_time=time(8, 45),
            index=0,
            break_time=10
        )
        
        self.assertEqual(item.id, "item_1")
        self.assertEqual(item.name, "第一节课")
        self.assertEqual(item.start_time, time(8, 0))
        self.assertEqual(item.end_time, time(8, 45))
        self.assertEqual(item.index, 0)
        self.assertTrue(item.is_enabled)
        self.assertEqual(item.break_time, 10)
    
    def test_time_layout_item_duration(self):
        """测试时间布局项持续时间"""
        item = TimeLayoutItem(
            id="item_1",
            name="第一节课",
            start_time=time(8, 0),
            end_time=time(9, 30)
        )
        
        self.assertEqual(item.duration_minutes, 90)


class TestTimeLayout(unittest.TestCase):
    """测试时间布局类"""
    
    def test_time_layout_creation(self):
        """测试时间布局创建"""
        layout = TimeLayout(
            id="layout_1",
            name="标准时间布局",
            description="标准的课程时间安排"
        )
        
        self.assertEqual(layout.id, "layout_1")
        self.assertEqual(layout.name, "标准时间布局")
        self.assertEqual(layout.description, "标准的课程时间安排")
        self.assertTrue(layout.is_enabled)
        self.assertEqual(len(layout.time_layout_items), 0)
    
    def test_add_time_layout_item(self):
        """测试添加时间布局项"""
        layout = TimeLayout(id="layout_1", name="测试布局")
        
        item1 = TimeLayoutItem(
            id="item_1",
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45),
            index=0
        )
        
        item2 = TimeLayoutItem(
            id="item_2",
            name="第二节",
            start_time=time(9, 0),
            end_time=time(9, 45),
            index=1
        )
        
        layout.add_time_layout_item(item1)
        layout.add_time_layout_item(item2)
        
        self.assertEqual(len(layout.time_layout_items), 2)
        self.assertEqual(layout.time_layout_items[0].index, 0)
        self.assertEqual(layout.time_layout_items[1].index, 1)
    
    def test_get_time_layout_item(self):
        """测试获取时间布局项"""
        layout = TimeLayout(id="layout_1", name="测试布局")
        
        item = TimeLayoutItem(
            id="item_1",
            name="第一节",
            start_time=time(8, 0),
            end_time=time(8, 45)
        )
        
        layout.add_time_layout_item(item)
        
        found_item = layout.get_time_layout_item("item_1")
        self.assertEqual(found_item, item)
        
        not_found = layout.get_time_layout_item("item_999")
        self.assertIsNone(not_found)


class TestClassPlan(unittest.TestCase):
    """测试课程计划类"""
    
    def test_class_plan_creation(self):
        """测试课程计划创建"""
        plan = ClassPlan(
            id="plan_1",
            name="春季学期计划",
            description="2024年春季学期课程计划",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 6, 30)
        )
        
        self.assertEqual(plan.id, "plan_1")
        self.assertEqual(plan.name, "春季学期计划")
        self.assertEqual(plan.description, "2024年春季学期课程计划")
        self.assertTrue(plan.is_enabled)
        self.assertEqual(plan.start_date, date(2024, 2, 1))
        self.assertEqual(plan.end_date, date(2024, 6, 30))
    
    def test_class_plan_with_time_layout(self):
        """测试带时间布局的课程计划"""
        time_layout = TimeLayout(id="layout_1", name="标准布局")
        
        plan = ClassPlan(
            id="plan_1",
            name="测试计划",
            time_layout=time_layout,
            time_layout_id="layout_1"
        )
        
        self.assertEqual(plan.time_layout, time_layout)
        self.assertEqual(plan.time_layout_id, "layout_1")


class TestSchedule(unittest.TestCase):
    """测试课程表类"""
    
    def setUp(self):
        """测试前准备"""
        self.schedule = Schedule(name="测试课程表")
        
        # 添加测试数据
        self.math_subject = Subject(id="math", name="数学")
        self.physics_subject = Subject(id="physics", name="物理")
        
        self.slot1 = TimeSlot(id="slot1", name="第一节", start_time=time(8, 0), end_time=time(8, 45))
        self.slot2 = TimeSlot(id="slot2", name="第二节", start_time=time(9, 0), end_time=time(9, 45))
        
        self.schedule.add_subject(self.math_subject)
        self.schedule.add_subject(self.physics_subject)
        self.schedule.add_time_slot(self.slot1)
        self.schedule.add_time_slot(self.slot2)
    
    def test_schedule_creation(self):
        """测试课程表创建"""
        schedule = Schedule(name="新课程表", description="测试描述")
        
        self.assertEqual(schedule.name, "新课程表")
        self.assertEqual(schedule.description, "测试描述")
        self.assertIsNotNone(schedule.created_date)
        self.assertIsNotNone(schedule.modified_date)
    
    def test_add_class(self):
        """测试添加课程"""
        class_item = ClassItem(
            id="class1",
            subject_id="math",
            time_slot_id="slot1",
            weekday="monday",
            classroom="A101"
        )
        
        self.schedule.add_class(class_item)
        
        self.assertEqual(len(self.schedule.classes), 1)
        self.assertEqual(self.schedule.classes[0], class_item)
    
    def test_get_classes_by_weekday(self):
        """测试按星期获取课程"""
        class1 = ClassItem(id="c1", subject_id="math", time_slot_id="slot1", weekday="monday")
        class2 = ClassItem(id="c2", subject_id="physics", time_slot_id="slot2", weekday="monday")
        class3 = ClassItem(id="c3", subject_id="math", time_slot_id="slot1", weekday="tuesday")
        
        self.schedule.add_class(class1)
        self.schedule.add_class(class2)
        self.schedule.add_class(class3)
        
        monday_classes = self.schedule.get_classes_by_weekday("monday")
        self.assertEqual(len(monday_classes), 2)
        
        tuesday_classes = self.schedule.get_classes_by_weekday("tuesday")
        self.assertEqual(len(tuesday_classes), 1)
    
    def test_schedule_validation(self):
        """测试课程表验证"""
        # 添加有效课程
        class_item = ClassItem(
            id="class1",
            subject_id="math",
            time_slot_id="slot1",
            weekday="monday"
        )
        self.schedule.add_class(class_item)
        
        errors = self.schedule.validate()
        self.assertEqual(len(errors), 0)
        
        # 添加无效课程（引用不存在的科目）
        invalid_class = ClassItem(
            id="class2",
            subject_id="invalid_subject",
            time_slot_id="slot1",
            weekday="tuesday"
        )
        self.schedule.add_class(invalid_class)
        
        errors = self.schedule.validate()
        self.assertGreater(len(errors), 0)
    
    def test_schedule_serialization(self):
        """测试课程表序列化"""
        class_item = ClassItem(
            id="class1",
            subject_id="math",
            time_slot_id="slot1",
            weekday="monday"
        )
        self.schedule.add_class(class_item)
        
        # 序列化
        data = self.schedule.to_dict()
        
        # 反序列化
        restored_schedule = Schedule.from_dict(data)
        
        self.assertEqual(self.schedule.name, restored_schedule.name)
        self.assertEqual(len(self.schedule.subjects), len(restored_schedule.subjects))
        self.assertEqual(len(self.schedule.time_slots), len(restored_schedule.time_slots))
        self.assertEqual(len(self.schedule.classes), len(restored_schedule.classes))


if __name__ == '__main__':
    unittest.main()
