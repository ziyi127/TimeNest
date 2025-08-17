#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
管理窗口组件
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QListWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

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
            QTableWidget {
                gridline-color: #e0e0e0;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 6px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
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

    def init_course_tab(self):
        """初始化课程管理标签页"""
        layout = QVBoxLayout(self.course_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 创建课程列表
        self.course_list = QListWidget()
        self.course_list.setStyleSheet("""
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
        layout.addWidget(self.course_list)

        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = QPushButton("添加课程")
        add_button.clicked.connect(self.add_course)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        edit_button = QPushButton("编辑课程")
        edit_button.clicked.connect(self.edit_course)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        delete_button = QPushButton("删除课程")
        delete_button.clicked.connect(self.delete_course)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()  # 添加弹性空间
        layout.addLayout(button_layout)

        # 更新列表数据
        self.update_course_list()

    def update_course_list(self):
        """更新课程列表"""
        self.course_list.clear()
        for course in self.app.courses:
            self._add_course_to_list(course)

    def load_course_data(self):
        """加载课程数据"""
        self.update_course_list()

    def _add_course_to_list(self, course: dict[str, Any]):
        """
        添加课程到列表
        
        Args:
            course: 课程数据
        """
        item = QListWidgetItem(f"{course['name']} - {course['teacher']} - {course['location']}")
        item.setData(Qt.UserRole, course['id'])  # type: ignore
        self.course_list.addItem(item)

    def add_course(self):
        """添加课程"""
        dialog = CourseEditDialog(self.app, None)
        if dialog.exec() == QDialog.Accepted:  # type: ignore
            self.app.load_data()
            self.update_course_list()
            # 触发悬浮窗更新
            if hasattr(self.app, 'floating_window'):
                self.app.floating_window.update_status()

    def edit_course(self):
        """编辑课程"""
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要编辑的课程")
            return

        course_id = current_item.data(Qt.UserRole)  # type: ignore
        course = self.app.get_course_by_id(course_id)
        if not course:
            QMessageBox.warning(self, "警告", "找不到选中的课程")
            return

        dialog = CourseEditDialog(self.app, course)
        if dialog.exec() == QDialog.Accepted:  # type: ignore
            self.app.load_data()
            self.update_course_list()
            # 触发悬浮窗更新
            if hasattr(self.app, 'floating_window'):
                self.app.floating_window.update_status()

    def delete_course(self):
        """删除课程"""
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的课程")
            return

        course_id = current_item.data(Qt.UserRole)  # type: ignore
        reply = QMessageBox.question(self, "确认", "确定要删除选中的课程吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # type: ignore
        if reply == QMessageBox.Yes:  # type: ignore
            # 执行删除课程的步骤
            self._execute_delete_course_steps(course_id)
            QMessageBox.information(self, '成功', '课程删除成功')

    def _execute_delete_course_steps(self, course_id: str):
        """
        执行删除课程的步骤
        
        Args:
            course_id: 课程ID
        """
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
        # 触发悬浮窗更新
        if hasattr(self.app, 'floating_window'):
            self.app.floating_window.update_status()

    def init_schedule_tab(self):
        """初始化课程表管理标签页"""
        layout = QVBoxLayout(self.schedule_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 创建课程表表格
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(["ID", "星期", "周次", "课程", "有效期从", "有效期至"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 6px;
                gridline-color: #e0e0e0;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.schedule_table)

        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = QPushButton("添加课程表项")
        add_button.clicked.connect(self.add_schedule)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        edit_button = QPushButton("编辑课程表项")
        edit_button.clicked.connect(self.edit_schedule)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        delete_button = QPushButton("删除课程表项")
        delete_button.clicked.connect(self.delete_schedule)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()  # 添加弹性空间
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
            
            # 填充行数据
            self._fill_schedule_row(row, schedule, weekdays, week_parity_map)

    def load_schedule_data(self):
        """加载课程表数据"""
        self.update_schedule_table()

    def _fill_schedule_row(self, row: int, schedule: dict[str, Any], weekdays: list[str], week_parity_map: dict[str, str]):
        """
        填充课程表行数据
        
        Args:
            row: 行索引
            schedule: 课程表数据
            weekdays: 星期名称列表
            week_parity_map: 周次映射
        """
        # ID
        self.schedule_table.setItem(row, 0, QTableWidgetItem(schedule['id']))

        # 星期
        weekday = weekdays[schedule['day_of_week']]
        self.schedule_table.setItem(row, 1, QTableWidgetItem(str(weekday)))  # type: ignore

        # 周次
        week_parity = week_parity_map.get(schedule['week_parity'], schedule.get('week_parity', ''))
        self.schedule_table.setItem(row, 2, QTableWidgetItem(str(week_parity)))

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
        if dialog.exec() == QDialog.Accepted:  # type: ignore
            self.app.load_data()
            self.update_schedule_table()
            # 触发悬浮窗更新
            if hasattr(self.app, 'floating_window'):
                self.app.floating_window.update_status()

    def edit_schedule(self):
        """编辑课程表项"""
        current_row = self.schedule_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要编辑的课程表项")
            return

        schedule_id = self.schedule_table.item(current_row, 0).text() if self.schedule_table.item(current_row, 0) else ""  # type: ignore
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
        if dialog.exec() == QDialog.Accepted:  # type: ignore
            self.app.load_data()
            self.update_schedule_table()

    def delete_schedule(self):
        """删除课程表项"""
        current_row = self.schedule_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要删除的课程表项")
            return

        schedule_id = self.schedule_table.item(current_row, 0).text() if self.schedule_table.item(current_row, 0) else ""  # type: ignore
        reply = QMessageBox.question(self, "确认", "确定要删除选中的课程表项吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # type: ignore
        if reply == QMessageBox.Yes:  # type: ignore
            # 执行删除课程表项的步骤
            self._execute_delete_schedule_steps(schedule_id)
            QMessageBox.information(self, '成功', '课程表删除成功')

    def _execute_delete_schedule_steps(self, schedule_id: str):
        """
        执行删除课程表项的步骤
        
        Args:
            schedule_id: 课程表项ID
        """
        # 删除课程表项
        self.app.schedules = [s for s in self.app.schedules if s['id'] != schedule_id]
        # 删除相关的临时换课
        self.app.temp_changes = [t for t in self.app.temp_changes if t['original_schedule_id'] != schedule_id]
        self.app.save_data()
        self.update_schedule_table()
        self.update_temp_change_table()
        # 触发悬浮窗更新
        if hasattr(self.app, 'floating_window'):
            self.app.floating_window.update_status()

    def init_temp_change_tab(self):
        """初始化临时换课记录标签页"""
        layout = QVBoxLayout(self.temp_change_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 创建临时换课表格
        self.temp_change_table = QTableWidget()
        self.temp_change_table.setColumnCount(5)
        self.temp_change_table.setHorizontalHeaderLabels(["ID", "日期", "原课程", "新课程", "状态"])
        self.temp_change_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.temp_change_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 6px;
                gridline-color: #e0e0e0;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.temp_change_table)

        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        delete_button = QPushButton("删除记录")
        delete_button.clicked.connect(self.delete_temp_change)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(delete_button)
        button_layout.addStretch()  # 添加弹性空间
        layout.addLayout(button_layout)

        # 更新表格数据
        self.update_temp_change_table()

    def update_temp_change_table(self):
        """更新临时换课表格"""
        self.temp_change_table.setRowCount(0)

        for temp_change in self.app.temp_changes:
            row = self.temp_change_table.rowCount()
            self.temp_change_table.insertRow(row)
            
            # 填充行数据
            self._fill_temp_change_row(row, temp_change)

    def _fill_temp_change_row(self, row: int, temp_change: dict[str, Any]):
        """
        填充临时换课行数据
        
        Args:
            row: 行索引
            temp_change: 临时换课数据
        """
        # ID
        self.temp_change_table.setItem(row, 0, QTableWidgetItem(temp_change['id']))

        # 日期
        self.temp_change_table.setItem(row, 1, QTableWidgetItem(temp_change['change_date']))

        # 原课程（通过original_schedule_id查找）
        original_course_name = self._get_original_course_name(temp_change)
        self.temp_change_table.setItem(row, 2, QTableWidgetItem(original_course_name))

        # 新课程
        new_course_name = self._get_new_course_name(temp_change)
        self.temp_change_table.setItem(row, 3, QTableWidgetItem(new_course_name))

        # 状态
        self._set_temp_change_status(row, temp_change)
    
    def _get_original_course_name(self, temp_change: dict[str, Any]) -> str:
        """
        获取原课程名称
        
        Args:
            temp_change: 临时换课数据
            
        Returns:
            原课程名称
        """
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
        
        return original_course_name
    
    def _get_new_course_name(self, temp_change: dict[str, Any]) -> str:
        """
        获取新课程名称
        
        Args:
            temp_change: 临时换课数据
            
        Returns:
            新课程名称
        """
        new_course = self.app.get_course_by_id(temp_change['new_course_id'])
        return new_course['name'] if new_course else "未知课程"
    
    def _set_temp_change_status(self, row: int, temp_change: dict[str, Any]):
        """
        设置临时换课状态
        
        Args:
            row: 行索引
            temp_change: 临时换课数据
        """
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

        temp_change_id = self.temp_change_table.item(current_row, 0).text() if self.temp_change_table.item(current_row, 0) else ""  # type: ignore
        reply = QMessageBox.question(self, "确认", "确定要删除选中的临时换课记录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # type: ignore
        if reply == QMessageBox.Yes:  # type: ignore
            # 执行删除临时换课记录的步骤
            self._execute_delete_temp_change_steps(temp_change_id)

    def _execute_delete_temp_change_steps(self, temp_change_id: str):
        """
        执行删除临时换课记录的步骤
        
        Args:
            temp_change_id: 临时换课记录ID
        """
        # 删除临时换课记录
        self.app.temp_changes = [t for t in self.app.temp_changes if t['id'] != temp_change_id]
        self.app.save_data()
        self.update_temp_change_table()
        # 触发悬浮窗更新
        if hasattr(self.app, 'floating_window'):
            self.app.floating_window.update_status()

    def save_data(self):
        """保存数据"""
        self.app.save_data()
        QMessageBox.information(self, "成功", "数据保存成功")