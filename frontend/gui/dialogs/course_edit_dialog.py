#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
课程编辑对话框
"""

import sys
from datetime import datetime
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
    QLineEdit, QTimeEdit,
    QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt


class CourseEditDialog(QDialog):
    def __init__(self, app: 'TimeNestFrontendApp', course: Optional[Dict[str, Any]] = None):
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

        # 地点
        self.location_edit = QLineEdit()
        if self.course:
            self.location_edit.setText(self.course['location'])
        layout.addRow("地点:", self.location_edit)

        # 开始时间
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        if self.course:
            start_time = datetime.strptime(self.course['start_time'], "%H:%M").time()
            self.start_time_edit.setTime(start_time)
        layout.addRow("开始时间:", self.start_time_edit)

        # 结束时间
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        if self.course:
            end_time = datetime.strptime(self.course['end_time'], "%H:%M").time()
            self.end_time_edit.setTime(end_time)
        layout.addRow("结束时间:", self.end_time_edit)

        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def accept(self):
        # 获取并验证输入的数据
        course_data = self._get_and_validate_course_data()
        if not course_data:
            return  # 验证失败，不关闭对话框
        
        # 保存课程数据
        self._save_course_data(course_data)
        
        # 保存数据到文件
        self.app.save_data()
        super().accept()
    
    def _get_and_validate_course_data(self) -> Optional[Dict[str, Any]]:
        """
        获取并验证课程数据
        
        Returns:
            验证通过的课程数据，验证失败则返回None
        """
        # 获取输入的数据
        id = self.id_edit.text().strip()
        name = self.name_edit.text().strip()
        teacher = self.teacher_edit.text().strip()
        location = self.location_edit.text().strip()
        start_time = self.start_time_edit.time().toString("HH:mm")
        end_time = self.end_time_edit.time().toString("HH:mm")

        # 验证数据
        if not id or not name or not teacher or not location:
            QMessageBox.warning(self, "警告", "请填写所有必填字段")
            return None

        # 验证时间格式
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M")
            end_time_obj = datetime.strptime(end_time, "%H:%M")
            if start_time_obj >= end_time_obj:
                QMessageBox.warning(self, "警告", "开始时间必须早于结束时间")
                return None
        except ValueError:
            QMessageBox.warning(self, "警告", "时间格式不正确")
            return None
        
        return {
            'id': id,
            'name': name,
            'teacher': teacher,
            'location': location,
            'start_time': start_time,
            'end_time': end_time
        }
    
    def _save_course_data(self, course_data: Dict[str, Any]):
        """
        保存课程数据
        
        Args:
            course_data: 课程数据
        """
        # 如果是编辑现有课程
        if self.course:
            # 更新现有课程
            for i, c in enumerate(self.app.courses):
                if c['id'] == self.course['id']:
                    self.app.courses[i] = course_data
                    break
        else:
            # 添加新课程
            self.app.courses.append(course_data)