#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
简化版学校模式管理窗口
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QLineEdit, QSpinBox,
    QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt


class SchoolModeWindowSimple(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.setWindowTitle("TimeNest 学校模式管理")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei";
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 2px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 2px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 80px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
                color: #4CAF50;
            }
        """)
        main_layout.addWidget(self.tab_widget)

        # 中小学模式标签页
        self.middle_school_tab = QWidget()
        self.tab_widget.addTab(self.middle_school_tab, "中小学模式")
        self.init_middle_school_tab()

        # 大学模式标签页
        self.university_tab = QWidget()
        self.tab_widget.addTab(self.university_tab, "大学模式")
        self.init_university_tab()

        # 保存按钮
        save_button = QPushButton("保存课表")
        save_button.clicked.connect(self.save_schedule)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        main_layout.addWidget(save_button)

    def init_middle_school_tab(self):
        """初始化中小学模式标签页"""
        layout = QVBoxLayout(self.middle_school_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 时间设置区
        time_group = QGroupBox("时间设置")
        time_layout = QFormLayout()
        time_group.setLayout(time_layout)

        # 第一节课开始时间
        self.first_class_start_edit = QLineEdit()
        self.first_class_start_edit.setText("08:00")
        time_layout.addRow("第一节课开始时间:", self.first_class_start_edit)

        # 单节课时长
        self.class_duration_spinbox = QSpinBox()
        self.class_duration_spinbox.setRange(10, 120)
        self.class_duration_spinbox.setValue(45)
        self.class_duration_spinbox.setSuffix(" 分钟")
        time_layout.addRow("单节课时长:", self.class_duration_spinbox)

        # 课间休息时长
        self.break_duration_spinbox = QSpinBox()
        self.break_duration_spinbox.setRange(1, 30)
        self.break_duration_spinbox.setValue(10)
        self.break_duration_spinbox.setSuffix(" 分钟")
        time_layout.addRow("课间休息时长:", self.break_duration_spinbox)

        # 大课间时长
        self.large_break_duration_spinbox = QSpinBox()
        self.large_break_duration_spinbox.setRange(1, 60)
        self.large_break_duration_spinbox.setValue(30)
        self.large_break_duration_spinbox.setSuffix(" 分钟")
        time_layout.addRow("大课间时长:", self.large_break_duration_spinbox)

        # 午休时长
        self.lunch_duration_edit = QLineEdit()
        self.lunch_duration_edit.setText("1小时15分钟")
        time_layout.addRow("午休时长:", self.lunch_duration_edit)

        layout.addWidget(time_group)

        # 科目设置区
        subjects_group = QGroupBox("科目设置")
        subjects_layout = QFormLayout()
        subjects_group.setLayout(subjects_layout)

        # 科目输入
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("输入新科目名称")
        add_button = QPushButton("添加科目")
        add_button.clicked.connect(self.add_subject)
        subjects_layout.addRow("新科目:", self.subject_input)
        subjects_layout.addRow(add_button)

        layout.addWidget(subjects_group)

    def init_university_tab(self):
        """初始化大学模式标签页"""
        layout = QVBoxLayout(self.university_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 时间参数设置区
        time_group = QGroupBox("时间参数设置")
        time_layout = QFormLayout()
        time_group.setLayout(time_layout)

        # 课时类型
        self.class_type_combo = QLineEdit()
        self.class_type_combo.setText("45分钟")
        time_layout.addRow("课时类型:", self.class_type_combo)

        # 课间休息时间
        self.break_time_spinbox = QSpinBox()
        self.break_time_spinbox.setRange(1, 60)
        self.break_time_spinbox.setValue(10)
        self.break_time_spinbox.setSuffix(" 分钟")
        time_layout.addRow("课间休息时间:", self.break_time_spinbox)

        # 午休时间设置
        self.lunch_time_combo = QLineEdit()
        self.lunch_time_combo.setText("无午休")
        time_layout.addRow("午休时间:", self.lunch_time_combo)

        # 每日最大课时数
        self.max_daily_classes_spinbox = QSpinBox()
        self.max_daily_classes_spinbox.setRange(1, 20)
        self.max_daily_classes_spinbox.setValue(8)
        time_layout.addRow("每日最大课时数:", self.max_daily_classes_spinbox)

        layout.addWidget(time_group)

        # 课程信息录入区
        course_group = QGroupBox("课程信息录入")
        course_layout = QFormLayout()
        course_group.setLayout(course_layout)

        # 课程名称
        self.course_name_input = QLineEdit()
        course_layout.addRow("课程名称:", self.course_name_input)

        # 学分
        self.course_credits_spinbox = QSpinBox()
        self.course_credits_spinbox.setRange(0, 10)
        self.course_credits_spinbox.setValue(2)
        course_layout.addRow("学分:", self.course_credits_spinbox)

        # 教师姓名
        self.teacher_name_input = QLineEdit()
        course_layout.addRow("教师姓名:", self.teacher_name_input)

        # 教室
        self.classroom_input = QLineEdit()
        course_layout.addRow("教室:", self.classroom_input)

        layout.addWidget(course_group)

    def add_subject(self):
        """添加科目"""
        subject = self.subject_input.text().strip()
        if subject:
            self.subject_input.clear()
            # 这里可以实现添加科目到列表的功能
            print(f"添加科目: {subject}")

    def save_schedule(self):
        """保存课表"""
        # 这里实现保存课表的逻辑
        QMessageBox.information(self, "成功", "课表保存成功")
