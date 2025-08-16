#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
管理窗口组件
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
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

# 导入对话框
from frontend.gui.dialogs.course_edit_dialog import CourseEditDialog
from frontend.gui.dialogs.schedule_edit_dialog import ScheduleEditDialog


class ManagementWindow(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.setWindowTitle("TimeNest 课表管理")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 课程管理标签页
        self.course_tab = QWidget()
        self.tab_widget.addTab(self.course_tab, "课程管理")
        self.init_course_tab()

        # 课程表管理标签页
        self.schedule_tab = QWidget()
        self.tab_widget.addTab(self.schedule_tab, "课程表管理")
        self.init_schedule_tab()

        # 临时换课记录标签页
        self.temp_change_tab = QWidget()
        self.tab_widget.addTab(self.temp_change_tab, "临时换课记录")
        self.init_temp_change_tab()

        # 保存按钮
        save_button = QPushButton("保存数据")
        save_button.clicked.connect(self.save_data)
        main_layout.addWidget(save_button)

    def init_course_tab(self):
        """初始化课程管理标签页"""
        layout = QVBoxLayout(self.course_tab)

        # 创建课程列表
        self.course_list = QListWidget()
        layout.addWidget(self.course_list)

        # 添加按钮
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加课程")
        add_button.clicked.connect(self.add_course)
        edit_button = QPushButton("编辑课程")
        edit_button.clicked.connect(self.edit_course)
        delete_button = QPushButton("删除课程")
        delete_button.clicked.connect(self.delete_course)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        # 更新列表数据
        self.update_course_list()

    def update_course_list(self):
        """更新课程列表"""
        self.course_list.clear()
        for course in self.app.courses:
            item = QListWidgetItem(f"{course['name']} - {course['teacher']} - {course['location']}")
            item.setData(Qt.UserRole, course['id'])
            self.course_list.addItem(item)

    def add_course(self):
        """添加课程"""
        dialog = CourseEditDialog(self.app, None)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_course_list()

    def edit_course(self):
        """编辑课程"""
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要编辑的课程")
            return

        course_id = current_item.data(Qt.UserRole)
        course = self.app.get_course_by_id(course_id)
        if not course:
            QMessageBox.warning(self, "警告", "找不到选中的课程")
            return

        dialog = CourseEditDialog(self.app, course)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_course_list()

    def delete_course(self):
        """删除课程"""
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的课程")
            return

        course_id = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认", "确定要删除选中的课程吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除课程
            self.app.courses = [c for c in self.app.courses if c['id'] != course_id]
            # 删除相关的课程表项
            self.app.schedules = [s for s in self.app.schedules if s['course_id'] != course_id]
            # 删除相关的临时换课
            self.app.temp_changes = [t for t in self.app.temp_changes if t['new_course_id'] != course_id]
            self.app.save_data()
            self.update_course_list()
            self.update_schedule_table()
            self.update_temp_change_table()

    def init_schedule_tab(self):
        """初始化课程表管理标签页"""
        layout = QVBoxLayout(self.schedule_tab)

        # 创建课程表表格
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(["ID", "星期", "周次", "课程", "有效期从", "有效期至"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.schedule_table)

        # 添加按钮
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加课程表项")
        add_button.clicked.connect(self.add_schedule)
        edit_button = QPushButton("编辑课程表项")
        edit_button.clicked.connect(self.edit_schedule)
        delete_button = QPushButton("删除课程表项")
        delete_button.clicked.connect(self.delete_schedule)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        # 更新表格数据
        self.update_schedule_table()

    def update_schedule_table(self):
        """更新课程表表格"""
        self.schedule_table.setRowCount(0)
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        week_parity_map = {
            "both": "每周",
            "odd": "奇数周",
            "even": "偶数周"
        }

        for schedule in self.app.schedules:
            row = self.schedule_table.rowCount()
            self.schedule_table.insertRow(row)

            # ID
            self.schedule_table.setItem(row, 0, QTableWidgetItem(schedule['id']))

            # 星期
            weekday = weekdays[schedule['day_of_week']]
            self.schedule_table.setItem(row, 1, QTableWidgetItem(weekday))

            # 周次
            week_parity = week_parity_map.get(schedule['week_parity'], schedule['week_parity'])
            self.schedule_table.setItem(row, 2, QTableWidgetItem(week_parity))

            # 课程
            course = self.app.get_course_by_id(schedule['course_id'])
            course_name = course['name'] if course else "未知课程"
            self.schedule_table.setItem(row, 3, QTableWidgetItem(course_name))

            # 有效期从
            self.schedule_table.setItem(row, 4, QTableWidgetItem(schedule['valid_from']))

            # 有效期至
            self.schedule_table.setItem(row, 5, QTableWidgetItem(schedule['valid_to']))

    def add_schedule(self):
        """添加课程表项"""
        dialog = ScheduleEditDialog(self.app, None)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_schedule_table()

    def edit_schedule(self):
        """编辑课程表项"""
        current_row = self.schedule_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要编辑的课程表项")
            return

        schedule_id = self.schedule_table.item(current_row, 0).text()
        # 查找课程表项
        schedule = None
        for s in self.app.schedules:
            if s['id'] == schedule_id:
                schedule = s
                break

        if not schedule:
            QMessageBox.warning(self, "警告", "找不到选中的课程表项")
            return

        dialog = ScheduleEditDialog(self.app, schedule)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_schedule_table()

    def delete_schedule(self):
        """删除课程表项"""
        current_row = self.schedule_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要删除的课程表项")
            return

        schedule_id = self.schedule_table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "确认", "确定要删除选中的课程表项吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除课程表项
            self.app.schedules = [s for s in self.app.schedules if s['id'] != schedule_id]
            # 删除相关的临时换课
            self.app.temp_changes = [t for t in self.app.temp_changes if t['original_schedule_id'] != schedule_id]
            self.app.save_data()
            self.update_schedule_table()
            self.update_temp_change_table()

    def init_temp_change_tab(self):
        """初始化临时换课记录标签页"""
        layout = QVBoxLayout(self.temp_change_tab)

        # 创建临时换课表格
        self.temp_change_table = QTableWidget()
        self.temp_change_table.setColumnCount(5)
        self.temp_change_table.setHorizontalHeaderLabels(["ID", "日期", "原课程", "新课程", "状态"])
        self.temp_change_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.temp_change_table)

        # 添加按钮
        button_layout = QHBoxLayout()
        delete_button = QPushButton("删除记录")
        delete_button.clicked.connect(self.delete_temp_change)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        # 更新表格数据
        self.update_temp_change_table()

    def update_temp_change_table(self):
        """更新临时换课表格"""
        self.temp_change_table.setRowCount(0)

        for temp_change in self.app.temp_changes:
            row = self.temp_change_table.rowCount()
            self.temp_change_table.insertRow(row)

            # ID
            self.temp_change_table.setItem(row, 0, QTableWidgetItem(temp_change['id']))

            # 日期
            self.temp_change_table.setItem(row, 1, QTableWidgetItem(temp_change['change_date']))

            # 原课程（通过original_schedule_id查找）
            original_schedule = None
            for s in self.app.schedules:
                if s['id'] == temp_change['original_schedule_id']:
                    original_schedule = s
                    break

            original_course_name = "未知课程"
            if original_schedule:
                original_course = self.app.get_course_by_id(original_schedule['course_id'])
                if original_course:
                    original_course_name = original_course['name']

            self.temp_change_table.setItem(row, 2, QTableWidgetItem(original_course_name))

            # 新课程
            new_course = self.app.get_course_by_id(temp_change['new_course_id'])
            new_course_name = new_course['name'] if new_course else "未知课程"
            self.temp_change_table.setItem(row, 3, QTableWidgetItem(new_course_name))

            # 状态
            status = "已使用" if temp_change['used'] else "未使用"
            status_item = QTableWidgetItem(status)
            if temp_change['used']:
                status_item.setForeground(QColor(128, 128, 128))
            else:
                status_item.setForeground(QColor(255, 99, 71))  # 红色
            self.temp_change_table.setItem(row, 4, status_item)

    def delete_temp_change(self):
        """删除临时换课记录"""
        current_row = self.temp_change_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要删除的临时换课记录")
            return

        temp_change_id = self.temp_change_table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "确认", "确定要删除选中的临时换课记录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除临时换课记录
            self.app.temp_changes = [t for t in self.app.temp_changes if t['id'] != temp_change_id]
            self.app.save_data()
            self.update_temp_change_table()

    def save_data(self):
        """保存数据"""
        self.app.save_data()
        QMessageBox.information(self, "成功", "数据保存成功")