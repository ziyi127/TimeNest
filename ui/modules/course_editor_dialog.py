#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 课程编辑对话框
用于添加和编辑课程信息
"""

import logging
from typing import Dict, Optional, Any
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
    QTextEdit, QCheckBox, QTimeEdit, QMessageBox, QGroupBox
)
from PyQt6.QtCore import QTime


class CourseEditorDialog(QDialog):
    """课程编辑对话框"""
    
    # 信号定义
    course_saved = pyqtSignal(dict)  # 课程保存信号
    
    def __init__(self, course_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.course_data = course_data or {}
        self.is_edit_mode = bool(course_data)
        self.logger = logging.getLogger(f'{__name__}.CourseEditorDialog')
        
        self.setup_ui()
        self.load_course_data()
        
        self.logger.info(f"课程编辑对话框初始化完成 - {'编辑' if self.is_edit_mode else '添加'}模式")
    
    def setup_ui(self):
        """设置界面"""
        title = "编辑课程" if self.is_edit_mode else "添加课程"
        self.setWindowTitle(title)
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.course_name_edit = QLineEdit()
        self.course_name_edit.setPlaceholderText("请输入课程名称")
        basic_layout.addRow("课程名称*:", self.course_name_edit)
        
        self.teacher_edit = QLineEdit()
        self.teacher_edit.setPlaceholderText("请输入授课教师")
        basic_layout.addRow("授课教师:", self.teacher_edit)
        
        self.classroom_edit = QLineEdit()
        self.classroom_edit.setPlaceholderText("请输入上课地点")
        basic_layout.addRow("上课地点:", self.classroom_edit)
        
        layout.addWidget(basic_group)
        
        # 时间安排组
        time_group = QGroupBox("时间安排")
        time_layout = QFormLayout(time_group)
        
        self.day_combo = QComboBox()
        self.day_combo.addItems(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        time_layout.addRow("星期:", self.day_combo)
        
        # 开始时间
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(8, 0))
        self.start_time_edit.setDisplayFormat("HH:mm")
        time_layout.addRow("开始时间:", self.start_time_edit)
        
        # 结束时间
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(9, 40))
        self.end_time_edit.setDisplayFormat("HH:mm")
        time_layout.addRow("结束时间:", self.end_time_edit)
        
        layout.addWidget(time_group)
        
        # 周次设置组
        weeks_group = QGroupBox("周次设置")
        weeks_layout = QFormLayout(weeks_group)
        
        self.start_week_spin = QSpinBox()
        self.start_week_spin.setRange(1, 30)
        self.start_week_spin.setValue(1)
        weeks_layout.addRow("开始周次:", self.start_week_spin)
        
        self.end_week_spin = QSpinBox()
        self.end_week_spin.setRange(1, 30)
        self.end_week_spin.setValue(16)
        weeks_layout.addRow("结束周次:", self.end_week_spin)
        
        # 单双周设置
        week_type_layout = QHBoxLayout()
        self.all_weeks_radio = QCheckBox("全部周次")
        self.all_weeks_radio.setChecked(True)
        self.odd_weeks_radio = QCheckBox("单周")
        self.even_weeks_radio = QCheckBox("双周")
        
        week_type_layout.addWidget(self.all_weeks_radio)
        week_type_layout.addWidget(self.odd_weeks_radio)
        week_type_layout.addWidget(self.even_weeks_radio)
        weeks_layout.addRow("周次类型:", week_type_layout)
        
        layout.addWidget(weeks_group)
        
        # 课程属性组
        properties_group = QGroupBox("课程属性")
        properties_layout = QFormLayout(properties_group)
        
        self.course_type_combo = QComboBox()
        self.course_type_combo.addItems(["必修课", "选修课", "实验课", "实习课", "其他"])
        properties_layout.addRow("课程类型:", self.course_type_combo)
        
        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(0, 10)
        self.credits_spin.setValue(2)
        self.credits_spin.setSuffix(" 学分")
        properties_layout.addRow("学分:", self.credits_spin)
        
        layout.addWidget(properties_group)
        
        # 备注信息
        notes_group = QGroupBox("备注信息")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("请输入课程备注信息...")
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_course)
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.all_weeks_radio.toggled.connect(self.on_week_type_changed)
        self.odd_weeks_radio.toggled.connect(self.on_week_type_changed)
        self.even_weeks_radio.toggled.connect(self.on_week_type_changed)
    
    def load_course_data(self):
        """加载课程数据"""
        if not self.course_data:
            return
        
        try:
            self.course_name_edit.setText(self.course_data.get('name', ''))
            self.teacher_edit.setText(self.course_data.get('teacher', ''))
            self.classroom_edit.setText(self.course_data.get('classroom', ''))
            
            # 设置星期
            day = self.course_data.get('day', 0)
            if 0 <= day < 7:
                self.day_combo.setCurrentIndex(day)
            
            # 设置时间
            start_time = self.course_data.get('start_time', '08:00')
            end_time = self.course_data.get('end_time', '09:40')
            
            self.start_time_edit.setTime(QTime.fromString(start_time, "HH:mm"))
            self.end_time_edit.setTime(QTime.fromString(end_time, "HH:mm"))
            
            # 设置周次
            self.start_week_spin.setValue(self.course_data.get('start_week', 1))
            self.end_week_spin.setValue(self.course_data.get('end_week', 16))
            
            # 设置课程属性
            course_type = self.course_data.get('course_type', '必修课')
            index = self.course_type_combo.findText(course_type)
            if index >= 0:
                self.course_type_combo.setCurrentIndex(index)
            
            self.credits_spin.setValue(self.course_data.get('credits', 2))
            self.notes_edit.setText(self.course_data.get('notes', ''))
            
        except Exception as e:
            self.logger.error(f"加载课程数据失败: {e}")
    
    def on_week_type_changed(self):
        """周次类型变化处理"""
        sender = self.sender()
        if sender.isChecked():
            # 取消其他选项
            if sender == self.all_weeks_radio:
                self.odd_weeks_radio.setChecked(False)
                self.even_weeks_radio.setChecked(False)
            elif sender == self.odd_weeks_radio:
                self.all_weeks_radio.setChecked(False)
                self.even_weeks_radio.setChecked(False)
            elif sender == self.even_weeks_radio:
                self.all_weeks_radio.setChecked(False)
                self.odd_weeks_radio.setChecked(False)
    
    def validate_input(self) -> bool:
        """验证输入"""
        if not self.course_name_edit.text().strip():
            QMessageBox.warning(self, "输入错误", "请输入课程名称")
            self.course_name_edit.setFocus()
            return False
        
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        
        if start_time >= end_time:
            QMessageBox.warning(self, "时间错误", "结束时间必须晚于开始时间")
            self.end_time_edit.setFocus()
            return False
        
        start_week = self.start_week_spin.value()
        end_week = self.end_week_spin.value()
        
        if start_week > end_week:
            QMessageBox.warning(self, "周次错误", "结束周次必须大于等于开始周次")
            self.end_week_spin.setFocus()
            return False
        
        return True
    
    def save_course(self):
        """保存课程"""
        try:
            if not self.validate_input():
                return
            
            # 确定周次类型
            week_type = "all"
            if self.odd_weeks_radio.isChecked():
                week_type = "odd"
            elif self.even_weeks_radio.isChecked():
                week_type = "even"
            
            course_data = {
                'id': self.course_data.get('id', None),  # 编辑模式时保留ID
                'name': self.course_name_edit.text().strip(),
                'teacher': self.teacher_edit.text().strip(),
                'classroom': self.classroom_edit.text().strip(),
                'day': self.day_combo.currentIndex(),
                'start_time': self.start_time_edit.time().toString("HH:mm"),
                'end_time': self.end_time_edit.time().toString("HH:mm"),
                'start_week': self.start_week_spin.value(),
                'end_week': self.end_week_spin.value(),
                'week_type': week_type,
                'course_type': self.course_type_combo.currentText(),
                'credits': self.credits_spin.value(),
                'notes': self.notes_edit.toPlainText().strip()
            }
            
            # 发出保存信号
            self.course_saved.emit(course_data)
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            self.logger.error(f"保存课程失败: {e}")
            QMessageBox.critical(self, "保存失败", f"保存课程时发生错误: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        event.accept()  # 只关闭对话框，不退出程序
