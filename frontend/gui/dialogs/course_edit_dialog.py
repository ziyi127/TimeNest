#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
课程编辑对话框
"""

import sys
import os
from datetime import datetime
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


# 课程编辑对话框
class CourseEditDialog(QDialog):
    def __init__(self, app, course=None):
        super().__init__()
        self.app = app
        self.course = course
        self.setWindowTitle("编辑课程" if course else "添加课程")
        self.initUI()

    def initUI(self):
        # 创建表单布局
        layout = QFormLayout(self)

        # 课程ID
        self.id_edit = QLineEdit()
        if self.course:
            self.id_edit.setText(self.course['id'])
            self.id_edit.setEnabled(False)  # 编辑时ID不可修改
        else:
            # 自动生成ID
            self.id_edit.setText(f"course{len(self.app.courses) + 1}")
        layout.addRow("课程ID:", self.id_edit)

        # 课程名称
        self.name_edit = QLineEdit()
        if self.course:
            self.name_edit.setText(self.course['name'])
        layout.addRow("课程名称:", self.name_edit)

        # 教师
        self.teacher_edit = QLineEdit()
        if self.course:
            self.teacher_edit.setText(self.course['teacher'])
        layout.addRow("教师:", self.teacher_edit)

        # 教室
        self.location_edit = QLineEdit()
        if self.course:
            self.location_edit.setText(self.course['location'])
        layout.addRow("教室:", self.location_edit)

        # 开始时间
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        if self.course:
            start_time = datetime.strptime(self.course['duration']['start_time'], "%H:%M").time()
            self.start_time_edit.setTime(start_time)
        layout.addRow("开始时间:", self.start_time_edit)

        # 结束时间
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        if self.course:
            end_time = datetime.strptime(self.course['duration']['end_time'], "%H:%M").time()
            self.end_time_edit.setTime(end_time)
        layout.addRow("结束时间:", self.end_time_edit)

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
        # 验证输入
        id = self.id_edit.text().strip()
        name = self.name_edit.text().strip()
        teacher = self.teacher_edit.text().strip()
        location = self.location_edit.text().strip()
        start_time = self.start_time_edit.time().toString("HH:mm")
        end_time = self.end_time_edit.time().toString("HH:mm")

        if not id or not name or not teacher or not location:
            QMessageBox.warning(self, "警告", "所有字段都不能为空")
            return

        # 检查时间顺序
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        if start >= end:
            QMessageBox.warning(self, "警告", "开始时间必须早于结束时间")
            return

        # 检查ID是否已存在（添加时）
        if not self.course:
            for course in self.app.courses:
                if course['id'] == id:
                    QMessageBox.warning(self, "警告", f"课程ID '{id}' 已存在")
                    return

        # 创建或更新课程
        course_data = {
            "id": id,
            "name": name,
            "teacher": teacher,
            "location": location,
            "duration": {
                "start_time": start_time,
                "end_time": end_time
            }
        }

        if self.course:
            # 更新课程
            index = -1
            for i, c in enumerate(self.app.courses):
                if c['id'] == id:
                    index = i
                    break
            if index != -1:
                self.app.courses[index] = course_data
        else:
            # 添加新课程
            self.app.courses.append(course_data)

        # 保存数据
        self.app.save_data()
        super().accept()