#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
课程表编辑对话框
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout,
                               QHBoxLayout, QPushButton, QMenu,
                               QSystemTrayIcon, QMessageBox, QDialog, QFormLayout,
                               QLineEdit, QComboBox, QDateEdit, QTimeEdit,
                               QListWidget, QListWidgetItem, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFrame, QCheckBox)
from PySide6.QtCore import QDate, QEvent, Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QAction, QMouseEvent, QGuiApplication


# 课程表编辑对话框
class ScheduleEditDialog(QDialog):
    def __init__(self, app, schedule=None):
        super().__init__()
        self.app = app
        self.schedule = schedule
        self.setWindowTitle("编辑课程表项" if schedule else "添加课程表项")
        self.initUI()

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
        self.weekday_combo = QComboBox()
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        self.weekday_combo.addItems(weekdays)
        if self.schedule:
            self.weekday_combo.setCurrentIndex(self.schedule['day_of_week'])
        layout.addRow("星期:", self.weekday_combo)

        # 周次
        self.week_parity_combo = QComboBox()
        self.week_parity_combo.addItems(["每周", "奇数周", "偶数周"])
        if self.schedule:
            week_parity_map = {
                "both": 0,
                "odd": 1,
                "even": 2
            }
            self.week_parity_combo.setCurrentIndex(week_parity_map.get(self.schedule['week_parity'], 0))
        layout.addRow("周次:", self.week_parity_combo)

        # 课程
        self.course_combo = QComboBox()
        self.course_ids = []
        for course in self.app.courses:
            self.course_combo.addItem(f"{course['name']} - {course['teacher']}")
            self.course_ids.append(course['id'])
        if self.schedule and self.schedule['course_id'] in self.course_ids:
            self.course_combo.setCurrentIndex(self.course_ids.index(self.schedule['course_id']))
        layout.addRow("课程:", self.course_combo)

        # 有效期从
        self.valid_from_edit = QDateEdit()
        self.valid_from_edit.setDisplayFormat("yyyy-MM-dd")
        if self.schedule:
            valid_from = datetime.strptime(self.schedule['valid_from'], "%Y-%m-%d").date()
            self.valid_from_edit.setDate(valid_from)
        else:
            self.valid_from_edit.setDate(datetime.now().date())
        layout.addRow("有效期从:", self.valid_from_edit)

        # 有效期至
        self.valid_to_edit = QDateEdit()
        self.valid_to_edit.setDisplayFormat("yyyy-MM-dd")
        if self.schedule:
            valid_to = datetime.strptime(self.schedule['valid_to'], "%Y-%m-%d").date()
            self.valid_to_edit.setDate(valid_to)
        else:
            next_month = datetime.now().date().replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            self.valid_to_edit.setDate(next_month)
        layout.addRow("有效期至:", self.valid_to_edit)

        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def accept(self):
        """确认按钮事件"""
        # 获取输入
        id = self.id_edit.text().strip()
        day_of_week = self.weekday_combo.currentIndex()
        week_parity_index = self.week_parity_combo.currentIndex()
        week_parity_map = ["both", "odd", "even"]
        week_parity = week_parity_map[week_parity_index]
        course_index = self.course_combo.currentIndex()
        course_id = self.course_ids[course_index]
        valid_from = self.valid_from_edit.date().toString("yyyy-MM-dd")
        valid_to = self.valid_to_edit.date().toString("yyyy-MM-dd")

        # 验证日期
        from_date = datetime.strptime(valid_from, "%Y-%m-%d").date()
        to_date = datetime.strptime(valid_to, "%Y-%m-%d").date()
        if from_date > to_date:
            QMessageBox.warning(self, "警告", "有效期从必须早于有效期至")
            return

        # 检查ID是否已存在（添加时）
        if not self.schedule:
            for schedule in self.app.schedules:
                if schedule['id'] == id:
                    QMessageBox.warning(self, "警告", f"课程表项ID '{id}' 已存在")
                    return

        # 创建或更新课程表项
        schedule_data = {
            "id": id,
            "day_of_week": day_of_week,
            "week_parity": week_parity,
            "course_id": course_id,
            "valid_from": valid_from,
            "valid_to": valid_to
        }

        if self.schedule:
            # 更新课程表项
            index = -1
            for i, s in enumerate(self.app.schedules):
                if s['id'] == id:
                    index = i
                    break
            if index != -1:
                self.app.schedules[index] = schedule_data
        else:
            # 添加新课程表项
            self.app.schedules.append(schedule_data)

        # 保存数据
        self.app.save_data()
        super().accept()