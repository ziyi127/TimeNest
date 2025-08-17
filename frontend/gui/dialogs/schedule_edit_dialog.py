#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
课程表编辑对话框
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit,
    QHBoxLayout, QPushButton
)
from PySide6.QtCore import QDate


class ScheduleEditDialog(QDialog):
    def __init__(self, app: 'TimeNestFrontendApp', schedule: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.app = app
        self.schedule = schedule
        self.setWindowTitle("编辑课程表项" if schedule else "添加课程表项")
        self.initUI()

    def get_schedule_data(self) -> dict[str, Any]:
        """获取课程表数据"""
        return {
            'id': self.id_edit.text().strip(),
            'day_of_week': self.day_of_week_combo.currentIndex(),
            'week_parity': ["both", "odd", "even"][self.week_parity_combo.currentIndex()],
            'course_id': self.course_combo.currentData(),
            'valid_from': self.valid_from_edit.date().toString("yyyy-MM-dd"),
            'valid_to': self.valid_to_edit.date().toString("yyyy-MM-dd")
        }

    def initUI(self):
        # 创建表单布局
        layout = QFormLayout(self)

        # 课程表项ID
        self.id_edit = QLineEdit()
        if self.schedule:
            self.id_edit.setText(self.schedule['id'])
            self.id_edit.setEnabled(False)  # 编辑时ID不可修改
        else:
            # 自动生成ID
            self.id_edit.setText(f"schedule{len(self.app.schedules) + 1}")
        layout.addRow("课程表项ID:", self.id_edit)

        # 星期
        self.day_of_week_combo = QComboBox()
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        self.day_of_week_combo.addItems(weekdays)
        if self.schedule:
            self.day_of_week_combo.setCurrentIndex(self.schedule['day_of_week'])
        layout.addRow("星期:", self.day_of_week_combo)

        # 周次
        self.week_parity_combo = QComboBox()
        self.week_parity_combo.addItems(["每周", "奇数周", "偶数周"])
        if self.schedule:
            week_parity_map = {
                "both": 0,
                "odd": 1,
                "even": 2
            }
            current_index = week_parity_map.get(self.schedule['week_parity'], 0)
            self.week_parity_combo.setCurrentIndex(current_index)
        layout.addRow("周次:", self.week_parity_combo)

        # 课程
        self.course_combo = QComboBox()
        self.update_course_list()
        if self.schedule:
            # 查找课程索引
            for i in range(self.course_combo.count()):
                if self.course_combo.itemData(i) == self.schedule['course_id']:
                    self.course_combo.setCurrentIndex(i)
                    break
        layout.addRow("课程:", self.course_combo)

        # 有效期从
        self.valid_from_edit = QDateEdit()
        self.valid_from_edit.setDisplayFormat("yyyy-MM-dd")
        if self.schedule:
            valid_from = QDate.fromString(self.schedule['valid_from'], "yyyy-MM-dd")
            self.valid_from_edit.setDate(valid_from)
        else:
            # 默认为今天
            self.valid_from_edit.setDate(QDate.currentDate())
        layout.addRow("有效期从:", self.valid_from_edit)

        # 有效期至
        self.valid_to_edit = QDateEdit()
        self.valid_to_edit.setDisplayFormat("yyyy-MM-dd")
        if self.schedule:
            valid_to = QDate.fromString(self.schedule['valid_to'], "yyyy-MM-dd")
            self.valid_to_edit.setDate(valid_to)
        else:
            # 默认为今天+30天
            self.valid_to_edit.setDate(QDate.currentDate().addDays(30))
        layout.addRow("有效期至:", self.valid_to_edit)

        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def update_course_list(self):
        """更新课程列表"""
        self.course_combo.clear()
        for course in self.app.courses:
            self._add_course_to_combo(course)

    def _add_course_to_combo(self, course: dict):
        """
        添加课程到下拉列表
        
        Args:
            course: 课程数据
        """
        self.course_combo.addItem(f"{course['name']} - {course['teacher']}", course['id'])

    def accept(self):
        # 获取并验证输入的数据
        schedule_data = self._get_and_validate_schedule_data()
        if not schedule_data:
            return  # 验证失败，不关闭对话框
        
        # 保存课程表数据
        self._save_schedule_data(schedule_data)
        
        # 保存数据到文件
        self.app.save_data()
        super().accept()
    
    def _get_and_validate_schedule_data(self) -> Optional[Dict[str, Any]]:
        """
        获取并验证课程表数据
        
        Returns:
            验证通过的课程表数据，验证失败则返回None
        """
        # 获取输入的数据
        id = self.id_edit.text().strip()
        day_of_week = self.day_of_week_combo.currentIndex()
        week_parity_map = {
            0: "both",
            1: "odd",
            2: "even"
        }
        week_parity = week_parity_map[self.week_parity_combo.currentIndex()]
        course_id = self.course_combo.currentData()
        valid_from = self.valid_from_edit.date().toString("yyyy-MM-dd")
        valid_to = self.valid_to_edit.date().toString("yyyy-MM-dd")

        # 验证数据
        if not id or not course_id:
            QMessageBox.warning(self, "警告", "请填写所有必填字段")
            return None

        # 验证日期
        if self.valid_from_edit.date() > self.valid_to_edit.date():
            QMessageBox.warning(self, "警告", "有效期开始日期不能晚于结束日期")
            return None
        
        return {
            'id': id,
            'day_of_week': day_of_week,
            'week_parity': week_parity,
            'course_id': course_id,
            'valid_from': valid_from,
            'valid_to': valid_to
        }
    
    def _save_schedule_data(self, schedule_data: Dict[str, Any]):
        """
        保存课程表数据
        
        Args:
            schedule_data: 课程表数据
        """
        # 如果是编辑现有课程表项
        if self.schedule:
            # 更新现有课程表项
            for i, s in enumerate(self.app.schedules):
                if s['id'] == self.schedule['id']:
                    self.app.schedules[i] = schedule_data
                    break
        else:
            # 添加新课程表项
            self.app.schedules.append(schedule_data)
    
    def _get_and_validate_schedule_data(self) -> Optional[Dict[str, Any]]:
        """
        获取并验证课程表数据
        
        Returns:
            验证通过的课程表数据，验证失败则返回None
        """
        # 获取输入的数据
        id = self.id_edit.text().strip()
        day_of_week = self.day_of_week_combo.currentIndex()
        week_parity_map = {
            0: "both",
            1: "odd",
            2: "even"
        }
        week_parity = week_parity_map[self.week_parity_combo.currentIndex()]
        course_id = self.course_combo.currentData()
        valid_from = self.valid_from_edit.date().toString("yyyy-MM-dd")
        valid_to = self.valid_to_edit.date().toString("yyyy-MM-dd")

        # 验证数据
        if not id or not course_id:
            QMessageBox.warning(self, "警告", "请填写所有必填字段")
            return None

        # 验证日期
        if self.valid_from_edit.date() > self.valid_to_edit.date():
            QMessageBox.warning(self, "警告", "有效期开始日期不能晚于结束日期")
            return None
        
        return {
            'id': id,
            'day_of_week': day_of_week,
            'week_parity': week_parity,
            'course_id': course_id,
            'valid_from': valid_from,
            'valid_to': valid_to
        }
    
    def _save_schedule_data(self, schedule_data: Dict[str, Any]):
        """
        保存课程表数据
        
        Args:
            schedule_data: 课程表数据
        """
        # 如果是编辑现有课程表项
        if self.schedule:
            # 更新现有课程表项
            for i, s in enumerate(self.app.schedules):
                if s['id'] == self.schedule['id']:
                    self.app.schedules[i] = schedule_data
                    break
        else:
            # 添加新课程表项
            self.app.schedules.append(schedule_data)