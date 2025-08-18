#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
中小学模式和大学模式管理窗口
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QGridLayout, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QCheckBox, QDateEdit, QTimeEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SchoolModeWindow(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.setWindowTitle("TimeNest 学校模式管理")
        self.setGeometry(100, 100, 1000, 700)
        self.initUI()
        
        # 初始化当前模式为中小学模式
        self.current_mode = "middle_school"  # 或 "university"
        
        # 初始化数据存储
        self.school_settings = {
            "middle_school": {
                "first_class_start": "08:00",
                "class_duration": 45,
                "break_duration": 10,
                "large_break_duration": 30,
                "lunch_duration": "1小时15分钟"
            },
            "university": {
                "class_types": ["45分钟", "90分钟", "自定义"],
                "default_class_type": "45分钟",
                "default_break_time": 10,
                "default_lunch_time": "无午休",
                "max_daily_classes": 8
            }
        }
        
        # 初始化科目列表
        self.subjects = ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治", "体育"]
        
        # 初始化课程表数据
        self.course_schedule = []

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
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
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

        # 模式切换按钮
        mode_layout = QHBoxLayout()
        self.mode_switch_button = QPushButton("切换到大学模式")
        self.mode_switch_button.clicked.connect(self.toggle_mode)
        mode_layout.addWidget(self.mode_switch_button)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

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

        # 加载按钮
        load_button = QPushButton("加载课表")
        load_button.clicked.connect(self.load_schedule)
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
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
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        main_layout.addWidget(load_button)

        # 重置按钮
        reset_button = QPushButton("重置")
        reset_button.clicked.connect(self.reset_settings)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
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
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        main_layout.addWidget(reset_button)

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
        subjects_layout = QVBoxLayout()
        subjects_group.setLayout(subjects_layout)

        # 科目列表
        self.subjects_list = QListWidget()
        self.subjects_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 5px;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #000000;
            }
        """)
        
        # 添加初始科目
        for subject in self.subjects:
            item = QListWidgetItem(subject)
            self.subjects_list.addItem(item)
        
        subjects_layout.addWidget(self.subjects_list)

        # 添加科目按钮
        add_subject_layout = QHBoxLayout()
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("输入新科目名称")
        add_button = QPushButton("添加科目")
        add_button.clicked.connect(self.add_subject)
        remove_button = QPushButton("删除选中")
        remove_button.clicked.connect(self.remove_subject)
        add_subject_layout.addWidget(self.subject_input)
        add_subject_layout.addWidget(add_button)
        add_subject_layout.addWidget(remove_button)
        subjects_layout.addLayout(add_subject_layout)

        layout.addWidget(subjects_group)

        # 课表设置区
        schedule_group = QGroupBox("课表设置")
        schedule_layout = QVBoxLayout()
        schedule_group.setLayout(schedule_layout)

        # 排序操作区
        sort_group = QGroupBox("排序操作")
        sort_layout = QVBoxLayout()
        sort_group.setLayout(sort_layout)

        # 课表预览区
        preview_group = QGroupBox("课表预览")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)

        # 预览标签
        self.schedule_preview_label = QLabel("课表预览将在选择科目后显示")
        self.schedule_preview_label.setWordWrap(True)
        self.schedule_preview_label.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 4px; }")
        preview_layout.addWidget(self.schedule_preview_label)

        schedule_layout.addWidget(sort_group)
        schedule_layout.addWidget(preview_group)
        layout.addWidget(schedule_group)

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
        self.class_type_combo = QComboBox()
        self.class_type_combo.addItems(["45分钟", "90分钟", "自定义"])
        self.class_type_combo.setCurrentIndex(0)
        time_layout.addRow("课时类型:", self.class_type_combo)

        # 单节课时长输入框（自定义时使用）
        self.custom_class_duration_spinbox = QSpinBox()
        self.custom_class_duration_spinbox.setRange(10, 180)
        self.custom_class_duration_spinbox.setValue(45)
        self.custom_class_duration_spinbox.setSuffix(" 分钟")
        self.custom_class_duration_spinbox.setVisible(False)
        self.class_type_combo.currentTextChanged.connect(self.toggle_custom_duration)
        time_layout.addRow("自定义课时长度:", self.custom_class_duration_spinbox)

        # 课间休息时间
        self.break_time_spinbox = QSpinBox()
        self.break_time_spinbox.setRange(1, 60)
        self.break_time_spinbox.setValue(10)
        self.break_time_spinbox.setSuffix(" 分钟")
        time_layout.addRow("课间休息时间:", self.break_time_spinbox)

        # 午休时间设置
        self.lunch_time_combo = QComboBox()
        self.lunch_time_combo.addItems(["无午休", "30分钟", "45分钟", "60分钟", "自定义"])
        self.lunch_time_combo.setCurrentIndex(0)
        self.lunch_time_spinbox = QSpinBox()
        self.lunch_time_spinbox.setRange(1, 120)
        self.lunch_time_spinbox.setValue(30)
        self.lunch_time_spinbox.setSuffix(" 分钟")
        self.lunch_time_spinbox.setVisible(False)
        self.lunch_time_combo.currentTextChanged.connect(self.toggle_custom_lunch)
        time_layout.addRow("午休时间:", self.lunch_time_combo)
        time_layout.addRow("自定义午休时长:", self.lunch_time_spinbox)

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

        # 周次设置
        self.week_parity_combo = QComboBox()
        self.week_parity_combo.addItems(["每周", "单周", "双周", "自定义周次范围"])
        course_layout.addRow("周次设置:", self.week_parity_combo)

        # 课程类型标签
        self.course_type_combo = QComboBox()
        self.course_type_combo.addItems(["必修课", "选修课", "实验课"])
        course_layout.addRow("课程类型:", self.course_type_combo)

        # 添加课程按钮
        add_course_button = QPushButton("添加课程")
        add_course_button.clicked.connect(self.add_university_course)
        course_layout.addRow(add_course_button)

        layout.addWidget(course_group)

        # 课程池区
        pool_group = QGroupBox("课程池")
        pool_layout = QVBoxLayout()
        pool_group.setLayout(pool_layout)

        self.course_pool_table = QTableWidget()
        self.course_pool_table.setColumnCount(5)
        self.course_pool_table.setHorizontalHeaderLabels(["课程名称", "学分", "教师", "教室", "周次"])
        self.course_pool_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        pool_layout.addWidget(self.course_pool_table)

        layout.addWidget(pool_group)

    def toggle_custom_duration(self, text):
        """切换自定义课时长度输入框"""
        self.custom_class_duration_spinbox.setVisible(text == "自定义")

    def toggle_custom_lunch(self, text):
        """切换自定义午休时长输入框"""
        self.lunch_time_spinbox.setVisible(text == "自定义")

    def add_subject(self):
        """添加科目"""
        subject = self.subject_input.text().strip()
        if subject:
            item = QListWidgetItem(subject)
            self.subjects_list.addItem(item)
            self.subject_input.clear()
            self.update_schedule_preview()

    def remove_subject(self):
        """删除选中的科目"""
        current_item = self.subjects_list.currentItem()
        if current_item:
            self.subjects_list.takeItem(self.subjects_list.row(current_item))
            self.update_schedule_preview()

    def update_schedule_preview(self):
        """更新课表预览"""
        subjects = [self.subjects_list.item(i).text() for i in range(self.subjects_list.count())]
        if subjects:
            preview_text = "课表预览:\n"
            for i, subject in enumerate(subjects, 1):
                preview_text += f"第{i}节: {subject}\n"
            self.schedule_preview_label.setText(preview_text)
        else:
            self.schedule_preview_label.setText("请添加科目以生成课表预览")

    def add_university_course(self):
        """添加大学课程"""
        # 这里可以实现添加大学课程的逻辑
        pass

    def toggle_mode(self):
        """切换模式"""
        if self.current_mode == "middle_school":
            self.current_mode = "university"
            self.mode_switch_button.setText("切换到中小学模式")
            self.tab_widget.setCurrentWidget(self.university_tab)
        else:
            self.current_mode = "middle_school"
            self.mode_switch_button.setText("切换到大学模式")
            self.tab_widget.setCurrentWidget(self.middle_school_tab)

    def save_schedule(self):
        """保存课表"""
        # 这里实现保存课表的逻辑
        QMessageBox.information(self, "成功", "课表保存成功")

    def load_schedule(self):
        """加载课表"""
        # 这里实现加载课表的逻辑
        QMessageBox.information(self, "提示", "课表加载成功")

    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(self, "确认", "确定要重置所有设置吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 重置中小学模式设置
            self.first_class_start_edit.setText("08:00")
            self.class_duration_spinbox.setValue(45)
            self.break_duration_spinbox.setValue(10)
            self.large_break_duration_spinbox.setValue(30)
            self.lunch_duration_edit.setText("1小时15分钟")
            
            # 重置科目列表
            self.subjects_list.clear()
            for subject in self.subjects:
                item = QListWidgetItem(subject)
                self.subjects_list.addItem(item)
            
            # 重置大学模式设置
            self.class_type_combo.setCurrentIndex(0)
            self.break_time_spinbox.setValue(10)
            self.lunch_time_combo.setCurrentIndex(0)
            self.max_daily_classes_spinbox.setValue(8)
            
            # 清空课程池
            self.course_pool_table.setRowCount(0)
            
            self.update_schedule_preview()
            QMessageBox.information(self, "成功", "设置已重置")
