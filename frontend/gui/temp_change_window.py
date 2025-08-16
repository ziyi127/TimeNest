#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
临时调课窗口组件
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton,
    QMessageBox, QComboBox, QDateEdit
)
from PySide6.QtCore import QDate


class TempChangeWindow(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.setWindowTitle("TimeNest 临时调课")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        # 创建主布局
        layout = QVBoxLayout(self)

        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("调课日期:")
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(datetime.now().date())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)

        # 原课程显示
        original_layout = QHBoxLayout()
        original_label = QLabel("原课程:")
        self.original_course_label = QLabel("无")
        original_layout.addWidget(original_label)
        original_layout.addWidget(self.original_course_label)
        layout.addLayout(original_layout)

        # 新课程选择
        new_layout = QHBoxLayout()
        new_label = QLabel("新课程:")
        self.new_course_combo = QComboBox()
        new_layout.addWidget(new_label)
        new_layout.addWidget(self.new_course_combo)
        layout.addLayout(new_layout)

        # 按钮
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(self.confirm_change)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # 更新课程列表
        self.update_course_list()

        # 更新原课程显示
        self.update_original_course()

    def update_course_list(self):
        """更新课程列表"""
        self.new_course_combo.clear()
        for course in self.app.courses:
            self.new_course_combo.addItem(f"{course['name']} - {course['teacher']}", course['id'])

    def update_original_course(self):
        """更新原课程显示"""
        schedule = self.app.get_today_schedule()
        if schedule["type"] == "none":
            self.original_course_label.setText("今日无课程")
        elif schedule["type"] in ["regular", "temp"]:
            course = schedule["course"]
            self.original_course_label.setText(f"{course['name']} ({course['teacher']}) {course['location']}")

    def confirm_change(self):
        """确认调课"""
        # 获取选择的日期
        change_date = self.date_edit.date().toString("yyyy-MM-dd")

        # 获取原课程
        schedule = self.app.get_today_schedule()
        if schedule["type"] == "none":
            QMessageBox.warning(self, "警告", "今日无课程，无法调课")
            return

        # 获取新课程
        new_course_index = self.new_course_combo.currentIndex()
        if new_course_index == -1:
            QMessageBox.warning(self, "警告", "请选择新课程")
            return

        new_course_id = self.new_course_combo.currentData()

        # 创建临时换课记录
        temp_change = {
            "id": f"temp{len(self.app.temp_changes) + 1}",
            "change_date": change_date,
            "original_schedule_id": schedule.get("schedule_id", ""),
            "new_course_id": new_course_id,
            "used": False
        }

        # 添加到临时换课列表
        self.app.temp_changes.append(temp_change)

        # 保存数据
        self.app.save_data()

        # 显示成功消息
        QMessageBox.information(self, "成功", "临时调课设置成功")

        # 关闭窗口
        self.close()