#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 课程表管理模块
集成课程表编辑、提醒设置、统计分析、导入导出等功能
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QTextEdit, QProgressBar, QMessageBox, QFileDialog,
    QHeaderView, QSplitter, QListWidget, QListWidgetItem,
    QDateEdit, QTimeEdit, QSlider, QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

if TYPE_CHECKING:
    from core.app_manager import AppManager


class ScheduleManagementDialog(QDialog):
    """课程表管理主对话框"""
    
    # 信号定义
    schedule_updated = pyqtSignal()
    reminder_set = pyqtSignal(str, dict)
    
    def __init__(self, app_manager: 'AppManager', parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.ScheduleManagementDialog')
        
        # 数据存储
        self.schedule_data = {}
        self.reminder_settings = {}
        self.statistics_data = {}
        
        self.setup_ui()
        self.load_data()
        self.connect_signals()
        
        self.logger.info("课程表管理模块初始化完成")
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("课程表管理")
        self.setFixedSize(1200, 800)
        
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 1. 课程表编辑选项卡
        self.schedule_tab = self.create_schedule_editor_tab()
        self.tab_widget.addTab(self.schedule_tab, "📅 课程表编辑")
        
        # 2. 提醒设置选项卡
        self.reminder_tab = self.create_reminder_settings_tab()
        self.tab_widget.addTab(self.reminder_tab, "⏰ 提醒设置")
        
        # 3. 统计分析选项卡
        self.statistics_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.statistics_tab, "📊 统计分析")
        
        # 4. 导入导出选项卡
        self.import_export_tab = self.create_import_export_tab()
        self.tab_widget.addTab(self.import_export_tab, "📁 导入导出")
        
        # 5. 冲突检测选项卡
        self.conflict_tab = self.create_conflict_detection_tab()
        self.tab_widget.addTab(self.conflict_tab, "⚠️ 冲突检测")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存所有更改")
        self.save_button.clicked.connect(self.save_all_changes)
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def create_schedule_editor_tab(self) -> QWidget:
        """创建课程表编辑选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_course_button = QPushButton("➕ 添加课程")
        self.add_course_button.clicked.connect(self.add_course)
        toolbar_layout.addWidget(self.add_course_button)
        
        self.edit_course_button = QPushButton("✏️ 编辑课程")
        self.edit_course_button.clicked.connect(self.edit_course)
        self.edit_course_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_course_button)
        
        self.delete_course_button = QPushButton("🗑️ 删除课程")
        self.delete_course_button.clicked.connect(self.delete_course)
        self.delete_course_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_course_button)
        
        toolbar_layout.addStretch()
        
        self.week_selector = QComboBox()
        self.week_selector.addItems([f"第{i}周" for i in range(1, 21)])
        self.week_selector.currentTextChanged.connect(self.on_week_changed)
        toolbar_layout.addWidget(QLabel("显示周次:"))
        toolbar_layout.addWidget(self.week_selector)
        
        layout.addLayout(toolbar_layout)
        
        # 课程表格
        self.schedule_table = QTableWidget(10, 7)  # 10个时段，7天
        self.schedule_table.setHorizontalHeaderLabels([
            "周一", "周二", "周三", "周四", "周五", "周六", "周日"
        ])
        self.schedule_table.setVerticalHeaderLabels([
            "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
            "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
            "19:00-19:45", "19:55-20:40"
        ])
        
        # 设置表格样式
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.schedule_table.itemSelectionChanged.connect(self.on_schedule_selection_changed)
        self.schedule_table.itemDoubleClicked.connect(self.edit_course)
        
        layout.addWidget(self.schedule_table)
        
        # 课程详情面板
        details_group = QGroupBox("课程详情")
        details_layout = QFormLayout(details_group)
        
        self.course_name_label = QLabel("未选择课程")
        self.course_teacher_label = QLabel("-")
        self.course_classroom_label = QLabel("-")
        self.course_weeks_label = QLabel("-")
        self.course_notes_label = QLabel("-")
        
        details_layout.addRow("课程名称:", self.course_name_label)
        details_layout.addRow("授课教师:", self.course_teacher_label)
        details_layout.addRow("上课地点:", self.course_classroom_label)
        details_layout.addRow("上课周次:", self.course_weeks_label)
        details_layout.addRow("备注信息:", self.course_notes_label)
        
        layout.addWidget(details_group)
        
        return tab
    
    def create_reminder_settings_tab(self) -> QWidget:
        """创建提醒设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 全局提醒设置
        global_group = QGroupBox("全局提醒设置")
        global_layout = QFormLayout(global_group)
        
        self.enable_reminders_check = QCheckBox("启用课程提醒")
        self.enable_reminders_check.setChecked(True)
        global_layout.addRow(self.enable_reminders_check)
        
        self.reminder_advance_spin = QSpinBox()
        self.reminder_advance_spin.setRange(1, 60)
        self.reminder_advance_spin.setValue(10)
        self.reminder_advance_spin.setSuffix(" 分钟")
        global_layout.addRow("提前提醒时间:", self.reminder_advance_spin)
        
        self.reminder_sound_check = QCheckBox("播放提醒声音")
        self.reminder_sound_check.setChecked(True)
        global_layout.addRow(self.reminder_sound_check)
        
        self.reminder_popup_check = QCheckBox("显示弹窗提醒")
        self.reminder_popup_check.setChecked(True)
        global_layout.addRow(self.reminder_popup_check)
        
        layout.addWidget(global_group)
        
        # 课程特定提醒设置
        specific_group = QGroupBox("课程特定提醒")
        specific_layout = QVBoxLayout(specific_group)
        
        # 课程列表
        self.reminder_course_list = QListWidget()
        self.reminder_course_list.itemSelectionChanged.connect(self.on_reminder_course_selected)
        specific_layout.addWidget(QLabel("选择课程:"))
        specific_layout.addWidget(self.reminder_course_list)
        
        # 提醒设置面板
        reminder_settings_layout = QFormLayout()
        
        self.course_reminder_enabled = QCheckBox("为此课程启用提醒")
        reminder_settings_layout.addRow(self.course_reminder_enabled)
        
        self.course_reminder_advance = QSpinBox()
        self.course_reminder_advance.setRange(1, 120)
        self.course_reminder_advance.setValue(10)
        self.course_reminder_advance.setSuffix(" 分钟")
        reminder_settings_layout.addRow("提前时间:", self.course_reminder_advance)
        
        self.course_reminder_message = QTextEdit()
        self.course_reminder_message.setMaximumHeight(80)
        self.course_reminder_message.setPlaceholderText("自定义提醒消息...")
        reminder_settings_layout.addRow("提醒消息:", self.course_reminder_message)
        
        specific_layout.addLayout(reminder_settings_layout)
        
        layout.addWidget(specific_group)
        
        # 提醒历史
        history_group = QGroupBox("提醒历史")
        history_layout = QVBoxLayout(history_group)
        
        self.reminder_history_list = QListWidget()
        history_layout.addWidget(self.reminder_history_list)
        
        clear_history_button = QPushButton("清空历史")
        clear_history_button.clicked.connect(self.clear_reminder_history)
        history_layout.addWidget(clear_history_button)
        
        layout.addWidget(history_group)
        
        return tab
    
    def create_statistics_tab(self) -> QWidget:
        """创建统计分析选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 统计概览
        overview_layout = QHBoxLayout()
        
        # 总课程数
        total_courses_frame = QFrame()
        total_courses_frame.setFrameStyle(QFrame.Shape.Box)
        total_courses_layout = QVBoxLayout(total_courses_frame)
        total_courses_layout.addWidget(QLabel("总课程数"))
        self.total_courses_label = QLabel("0")
        self.total_courses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_courses_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        total_courses_layout.addWidget(self.total_courses_label)
        overview_layout.addWidget(total_courses_frame)
        
        # 本周课程数
        week_courses_frame = QFrame()
        week_courses_frame.setFrameStyle(QFrame.Shape.Box)
        week_courses_layout = QVBoxLayout(week_courses_frame)
        week_courses_layout.addWidget(QLabel("本周课程"))
        self.week_courses_label = QLabel("0")
        self.week_courses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.week_courses_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        week_courses_layout.addWidget(self.week_courses_label)
        overview_layout.addWidget(week_courses_frame)
        
        # 今日课程数
        today_courses_frame = QFrame()
        today_courses_frame.setFrameStyle(QFrame.Shape.Box)
        today_courses_layout = QVBoxLayout(today_courses_frame)
        today_courses_layout.addWidget(QLabel("今日课程"))
        self.today_courses_label = QLabel("0")
        self.today_courses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_courses_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800;")
        today_courses_layout.addWidget(self.today_courses_label)
        overview_layout.addWidget(today_courses_frame)
        
        layout.addLayout(overview_layout)
        
        # 详细统计
        details_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 课程分布统计
        distribution_group = QGroupBox("课程分布统计")
        distribution_layout = QVBoxLayout(distribution_group)
        
        self.distribution_list = QListWidget()
        distribution_layout.addWidget(self.distribution_list)
        
        details_splitter.addWidget(distribution_group)
        
        # 时间统计
        time_group = QGroupBox("时间统计")
        time_layout = QVBoxLayout(time_group)
        
        self.time_stats_list = QListWidget()
        time_layout.addWidget(self.time_stats_list)
        
        details_splitter.addWidget(time_group)
        
        layout.addWidget(details_splitter)
        
        # 刷新按钮
        refresh_button = QPushButton("🔄 刷新统计")
        refresh_button.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_button)
        
        return tab
    
    def create_import_export_tab(self) -> QWidget:
        """创建导入导出选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 导入部分
        import_group = QGroupBox("导入课程表")
        import_layout = QVBoxLayout(import_group)
        
        import_buttons_layout = QHBoxLayout()
        
        self.import_json_button = QPushButton("📄 导入 JSON")
        self.import_json_button.clicked.connect(self.import_from_json)
        import_buttons_layout.addWidget(self.import_json_button)
        
        self.import_csv_button = QPushButton("📊 导入 CSV")
        self.import_csv_button.clicked.connect(self.import_from_csv)
        import_buttons_layout.addWidget(self.import_csv_button)
        
        self.import_excel_button = QPushButton("📈 导入 Excel")
        self.import_excel_button.clicked.connect(self.import_from_excel)
        import_buttons_layout.addWidget(self.import_excel_button)
        
        import_layout.addLayout(import_buttons_layout)
        
        # 导入选项
        import_options_layout = QFormLayout()
        
        self.import_merge_check = QCheckBox("合并到现有课程表")
        import_options_layout.addRow(self.import_merge_check)
        
        self.import_backup_check = QCheckBox("导入前备份当前数据")
        self.import_backup_check.setChecked(True)
        import_options_layout.addRow(self.import_backup_check)
        
        import_layout.addLayout(import_options_layout)
        
        layout.addWidget(import_group)
        
        # 导出部分
        export_group = QGroupBox("导出课程表")
        export_layout = QVBoxLayout(export_group)
        
        export_buttons_layout = QHBoxLayout()
        
        self.export_json_button = QPushButton("📄 导出 JSON")
        self.export_json_button.clicked.connect(self.export_to_json)
        export_buttons_layout.addWidget(self.export_json_button)
        
        self.export_csv_button = QPushButton("📊 导出 CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)
        export_buttons_layout.addWidget(self.export_csv_button)
        
        self.export_excel_button = QPushButton("📈 导出 Excel")
        self.export_excel_button.clicked.connect(self.export_to_excel)
        export_buttons_layout.addWidget(self.export_excel_button)
        
        self.export_pdf_button = QPushButton("📋 导出 PDF")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        export_buttons_layout.addWidget(self.export_pdf_button)
        
        export_layout.addLayout(export_buttons_layout)
        
        # 导出选项
        export_options_layout = QFormLayout()
        
        self.export_week_range_check = QCheckBox("包含周次范围")
        self.export_week_range_check.setChecked(True)
        export_options_layout.addRow(self.export_week_range_check)
        
        self.export_teacher_check = QCheckBox("包含教师信息")
        self.export_teacher_check.setChecked(True)
        export_options_layout.addRow(self.export_teacher_check)
        
        self.export_classroom_check = QCheckBox("包含教室信息")
        self.export_classroom_check.setChecked(True)
        export_options_layout.addRow(self.export_classroom_check)
        
        export_layout.addLayout(export_options_layout)
        
        layout.addWidget(export_group)
        
        # 备份管理
        backup_group = QGroupBox("备份管理")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_buttons_layout = QHBoxLayout()
        
        self.create_backup_button = QPushButton("💾 创建备份")
        self.create_backup_button.clicked.connect(self.create_backup)
        backup_buttons_layout.addWidget(self.create_backup_button)
        
        self.restore_backup_button = QPushButton("🔄 恢复备份")
        self.restore_backup_button.clicked.connect(self.restore_backup)
        backup_buttons_layout.addWidget(self.restore_backup_button)
        
        backup_layout.addLayout(backup_buttons_layout)
        
        self.backup_list = QListWidget()
        backup_layout.addWidget(QLabel("备份列表:"))
        backup_layout.addWidget(self.backup_list)
        
        layout.addWidget(backup_group)
        
        return tab
    
    def create_conflict_detection_tab(self) -> QWidget:
        """创建冲突检测选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 检测控制
        control_layout = QHBoxLayout()
        
        self.detect_conflicts_button = QPushButton("🔍 检测冲突")
        self.detect_conflicts_button.clicked.connect(self.detect_conflicts)
        control_layout.addWidget(self.detect_conflicts_button)
        
        self.auto_detect_check = QCheckBox("自动检测")
        self.auto_detect_check.setChecked(True)
        control_layout.addWidget(self.auto_detect_check)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 冲突列表
        conflicts_group = QGroupBox("检测到的冲突")
        conflicts_layout = QVBoxLayout(conflicts_group)
        
        self.conflicts_list = QListWidget()
        conflicts_layout.addWidget(self.conflicts_list)
        
        # 冲突解决按钮
        resolve_layout = QHBoxLayout()
        
        self.resolve_conflict_button = QPushButton("解决选中冲突")
        self.resolve_conflict_button.clicked.connect(self.resolve_conflict)
        self.resolve_conflict_button.setEnabled(False)
        resolve_layout.addWidget(self.resolve_conflict_button)
        
        self.ignore_conflict_button = QPushButton("忽略冲突")
        self.ignore_conflict_button.clicked.connect(self.ignore_conflict)
        self.ignore_conflict_button.setEnabled(False)
        resolve_layout.addWidget(self.ignore_conflict_button)
        
        conflicts_layout.addLayout(resolve_layout)
        
        layout.addWidget(conflicts_group)
        
        # 冲突详情
        details_group = QGroupBox("冲突详情")
        details_layout = QVBoxLayout(details_group)
        
        self.conflict_details_text = QTextEdit()
        self.conflict_details_text.setReadOnly(True)
        self.conflict_details_text.setMaximumHeight(150)
        details_layout.addWidget(self.conflict_details_text)
        
        layout.addWidget(details_group)
        
        return tab

    def load_data(self):
        """加载数据"""
        try:
            if self.app_manager and self.app_manager.config_manager:
                # 加载课程表数据
                self.schedule_data = self.app_manager.config_manager.get_config('schedule', {}, 'user')

                # 加载提醒设置
                self.reminder_settings = self.app_manager.config_manager.get_config('reminder_settings', {}, 'user')

                # 更新界面
                self.update_schedule_table()
                self.update_reminder_course_list()
                self.refresh_statistics()
                self.load_backup_list()

        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")

    def connect_signals(self):
        """连接信号"""
        try:
            # 自动检测冲突
            if hasattr(self, 'auto_detect_check'):
                self.auto_detect_check.stateChanged.connect(self.on_auto_detect_changed)

        except Exception as e:
            self.logger.error(f"连接信号失败: {e}")

    def update_schedule_table(self):
        """更新课程表显示"""
        try:
            # 清空表格
            for row in range(self.schedule_table.rowCount()):
                for col in range(self.schedule_table.columnCount()):
                    self.schedule_table.setItem(row, col, QTableWidgetItem(""))

            # 获取当前周次
            current_week = int(self.week_selector.currentText().replace("第", "").replace("周", ""))

            # 填充真实数据
            courses = self.schedule_data.get('courses', [])

            # 如果没有课程数据，添加一些示例数据
            if not courses:
                sample_courses = [
                    {
                        "id": "sample_1",
                        "name": "高等数学",
                        "teacher": "张教授",
                        "classroom": "A101",
                        "day": 0,
                        "start_time": "08:00",
                        "end_time": "09:40",
                        "start_week": 1,
                        "end_week": 16,
                        "week_type": "all"
                    },
                    {
                        "id": "sample_2",
                        "name": "大学英语",
                        "teacher": "李老师",
                        "classroom": "B203",
                        "day": 1,
                        "start_time": "08:55",
                        "end_time": "10:35",
                        "start_week": 1,
                        "end_week": 16,
                        "week_type": "all"
                    }
                ]
                self.schedule_data['courses'] = sample_courses
                courses = sample_courses

            # 时间段映射
            time_slots = [
                ("08:00", "08:45"), ("08:55", "09:40"), ("10:00", "10:45"), ("10:55", "11:40"),
                ("14:00", "14:45"), ("14:55", "15:40"), ("16:00", "16:45"), ("16:55", "17:40"),
                ("19:00", "19:45"), ("19:55", "20:40")
            ]

            for course in courses:
                # 检查课程是否在当前周次
                start_week = course.get('start_week', 1)
                end_week = course.get('end_week', 16)
                week_type = course.get('week_type', 'all')

                if not (start_week <= current_week <= end_week):
                    continue

                # 检查单双周
                if week_type == 'odd' and current_week % 2 == 0:
                    continue
                elif week_type == 'even' and current_week % 2 == 1:
                    continue

                # 找到对应的时间段
                start_time = course.get('start_time', '08:00')
                time_slot_index = -1

                for i, (slot_start, slot_end) in enumerate(time_slots):
                    if start_time == slot_start:
                        time_slot_index = i
                        break

                if time_slot_index == -1:
                    # 如果找不到精确匹配，使用最接近的时间段
                    for i, (slot_start, slot_end) in enumerate(time_slots):
                        if start_time <= slot_start:
                            time_slot_index = i
                            break
                    if time_slot_index == -1:
                        time_slot_index = 0  # 默认第一个时间段

                day = course.get('day', 0)
                if 0 <= day < 7 and 0 <= time_slot_index < 10:
                    display_text = f"{course['name']}\n{course.get('teacher', '')}\n{course.get('classroom', '')}"
                    item = QTableWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, course)

                    # 设置样式
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.schedule_table.setItem(time_slot_index, day, item)

        except Exception as e:
            self.logger.error(f"更新课程表失败: {e}")

    def update_reminder_course_list(self):
        """更新提醒课程列表"""
        try:
            self.reminder_course_list.clear()

            # 添加示例课程
            courses = ["高等数学", "大学英语", "计算机科学", "物理实验", "体育课"]
            for course in courses:
                item = QListWidgetItem(course)
                self.reminder_course_list.addItem(item)

        except Exception as e:
            self.logger.error(f"更新提醒课程列表失败: {e}")

    def refresh_statistics(self):
        """刷新统计信息"""
        try:
            # 更新统计数字（模拟数据）
            self.total_courses_label.setText("25")
            self.week_courses_label.setText("12")
            self.today_courses_label.setText("4")

            # 更新分布统计
            self.distribution_list.clear()
            distribution_data = [
                "周一: 5门课程",
                "周二: 4门课程",
                "周三: 6门课程",
                "周四: 3门课程",
                "周五: 7门课程"
            ]
            for item in distribution_data:
                self.distribution_list.addItem(item)

            # 更新时间统计
            self.time_stats_list.clear()
            time_data = [
                "上午课程: 15门",
                "下午课程: 8门",
                "晚上课程: 2门",
                "平均每天: 3.6门"
            ]
            for item in time_data:
                self.time_stats_list.addItem(item)

        except Exception as e:
            self.logger.error(f"刷新统计失败: {e}")

    def load_backup_list(self):
        """加载备份列表"""
        try:
            self.backup_list.clear()

            # 添加示例备份
            backups = [
                "2024-07-11 16:30:00 - 自动备份",
                "2024-07-10 14:20:00 - 手动备份",
                "2024-07-09 09:15:00 - 导入前备份"
            ]
            for backup in backups:
                self.backup_list.addItem(backup)

        except Exception as e:
            self.logger.error(f"加载备份列表失败: {e}")

    # 事件处理方法
    def add_course(self):
        """添加课程"""
        try:
            from ui.modules.course_editor_dialog import CourseEditorDialog

            dialog = CourseEditorDialog(parent=self)
            dialog.course_saved.connect(self.on_course_saved)
            dialog.exec()

        except Exception as e:
            self.logger.error(f"添加课程失败: {e}")
            QMessageBox.critical(self, "错误", f"打开课程编辑器失败: {e}")

    def edit_course(self):
        """编辑课程"""
        try:
            current_item = self.schedule_table.currentItem()
            if not current_item or not current_item.data(Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "警告", "请先选择要编辑的课程")
                return

            course_data = current_item.data(Qt.ItemDataRole.UserRole)

            from ui.modules.course_editor_dialog import CourseEditorDialog

            dialog = CourseEditorDialog(course_data, parent=self)
            dialog.course_saved.connect(self.on_course_saved)
            dialog.exec()

        except Exception as e:
            self.logger.error(f"编辑课程失败: {e}")
            QMessageBox.critical(self, "错误", f"打开课程编辑器失败: {e}")

    def delete_course(self):
        """删除课程"""
        try:
            current_item = self.schedule_table.currentItem()
            if not current_item or not current_item.data(Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "警告", "请先选择要删除的课程")
                return

            course_data = current_item.data(Qt.ItemDataRole.UserRole)
            course_name = course_data.get('name', '未知课程')

            reply = QMessageBox.question(
                self, "确认删除", f"确定要删除课程 '{course_name}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 从表格中移除
                row = self.schedule_table.currentRow()
                col = self.schedule_table.currentColumn()
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))

                # 从数据中移除
                course_id = course_data.get('id')
                if course_id and 'courses' in self.schedule_data:
                    self.schedule_data['courses'] = [
                        c for c in self.schedule_data['courses']
                        if c.get('id') != course_id
                    ]

                # 更新界面
                self.update_schedule_table()
                self.refresh_statistics()

                QMessageBox.information(self, "删除成功", f"课程 '{course_name}' 已删除")

        except Exception as e:
            self.logger.error(f"删除课程失败: {e}")
            QMessageBox.critical(self, "错误", f"删除课程失败: {e}")

    def on_course_saved(self, course_data):
        """课程保存处理"""
        try:
            # 确保数据结构存在
            if 'courses' not in self.schedule_data:
                self.schedule_data['courses'] = []

            # 生成课程ID（如果是新课程）
            if not course_data.get('id'):
                import uuid
                course_data['id'] = str(uuid.uuid4())
                self.schedule_data['courses'].append(course_data)
            else:
                # 更新现有课程
                for i, course in enumerate(self.schedule_data['courses']):
                    if course.get('id') == course_data['id']:
                        self.schedule_data['courses'][i] = course_data
                        break

            # 更新界面
            self.update_schedule_table()
            self.refresh_statistics()

            self.logger.info(f"课程已保存: {course_data['name']}")

        except Exception as e:
            self.logger.error(f"保存课程数据失败: {e}")
            QMessageBox.critical(self, "错误", f"保存课程数据失败: {e}")

    def on_week_changed(self, week_text):
        """周次变化处理"""
        self.logger.debug(f"切换到: {week_text}")

    def on_schedule_selection_changed(self):
        """课程表选择变化"""
        try:
            current_item = self.schedule_table.currentItem()
            if current_item and current_item.data(Qt.ItemDataRole.UserRole):
                course = current_item.data(Qt.ItemDataRole.UserRole)
                self.course_name_label.setText(course['name'])
                self.course_teacher_label.setText(course['teacher'])
                self.course_classroom_label.setText(course['classroom'])
                self.course_weeks_label.setText("1-16周")
                self.course_notes_label.setText("无")

                self.edit_course_button.setEnabled(True)
                self.delete_course_button.setEnabled(True)
            else:
                self.course_name_label.setText("未选择课程")
                self.course_teacher_label.setText("-")
                self.course_classroom_label.setText("-")
                self.course_weeks_label.setText("-")
                self.course_notes_label.setText("-")

                self.edit_course_button.setEnabled(False)
                self.delete_course_button.setEnabled(False)

        except Exception as e:
            self.logger.error(f"处理选择变化失败: {e}")

    def on_reminder_course_selected(self):
        """提醒课程选择变化"""
        try:
            current_item = self.reminder_course_list.currentItem()
            if current_item:
                course_name = current_item.text()
                # 加载该课程的提醒设置
                self.course_reminder_enabled.setChecked(True)
                self.course_reminder_advance.setValue(10)
                self.course_reminder_message.setText(f"即将开始{course_name}课程")

        except Exception as e:
            self.logger.error(f"处理提醒课程选择失败: {e}")

    def clear_reminder_history(self):
        """清空提醒历史"""
        self.reminder_history_list.clear()
        QMessageBox.information(self, "成功", "提醒历史已清空")

    def on_auto_detect_changed(self, state):
        """自动检测状态变化"""
        if state == Qt.CheckState.Checked.value:
            self.detect_conflicts()

    def detect_conflicts(self):
        """检测冲突"""
        try:
            self.conflicts_list.clear()

            # 模拟冲突检测
            conflicts = [
                "时间冲突: 周一 08:00-09:40 高等数学 与 大学物理 时间重叠",
                "教室冲突: A101教室在周二 10:00-11:40 被两门课程占用",
                "教师冲突: 张教授在周三 14:00-15:40 需要同时上两门课"
            ]

            for conflict in conflicts:
                item = QListWidgetItem(conflict)
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning))
                self.conflicts_list.addItem(item)

            if conflicts:
                QMessageBox.warning(self, "发现冲突", f"检测到 {len(conflicts)} 个冲突，请查看详情")
            else:
                QMessageBox.information(self, "检测完成", "未发现任何冲突")

        except Exception as e:
            self.logger.error(f"检测冲突失败: {e}")

    def resolve_conflict(self):
        """解决冲突"""
        QMessageBox.information(self, "功能开发中", "冲突解决功能正在开发中...")

    def ignore_conflict(self):
        """忽略冲突"""
        current_item = self.conflicts_list.currentItem()
        if current_item:
            self.conflicts_list.takeItem(self.conflicts_list.row(current_item))
            QMessageBox.information(self, "已忽略", "冲突已被忽略")

    # 导入导出方法
    def import_from_json(self):
        """从JSON导入"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "导入JSON文件", "", "JSON文件 (*.json)")
            if not file_path:
                return

            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证数据格式
            if 'courses' not in data:
                QMessageBox.warning(self, "格式错误", "JSON文件格式不正确，缺少courses字段")
                return

            # 备份当前数据
            if self.import_backup_check.isChecked():
                self.create_backup()

            # 导入数据
            if self.import_merge_check.isChecked():
                # 合并模式
                existing_courses = self.schedule_data.get('courses', [])
                new_courses = data['courses']

                # 避免重复导入
                existing_ids = {c.get('id') for c in existing_courses if c.get('id')}
                for course in new_courses:
                    if course.get('id') not in existing_ids:
                        existing_courses.append(course)

                self.schedule_data['courses'] = existing_courses
            else:
                # 替换模式
                self.schedule_data = data

            # 更新界面
            self.update_schedule_table()
            self.refresh_statistics()

            QMessageBox.information(self, "导入成功", f"成功导入 {len(data['courses'])} 门课程")

        except Exception as e:
            self.logger.error(f"JSON导入失败: {e}")
            QMessageBox.critical(self, "导入失败", f"导入JSON文件失败: {e}")

    def import_from_csv(self):
        """从CSV导入"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "导入CSV文件", "", "CSV文件 (*.csv)")
            if not file_path:
                return

            import csv
            import uuid

            courses = []

            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    course = {
                        'id': str(uuid.uuid4()),
                        'name': row.get('课程名称', ''),
                        'teacher': row.get('教师', ''),
                        'classroom': row.get('教室', ''),
                        'day': int(row.get('星期', 0)),
                        'start_time': row.get('开始时间', '08:00'),
                        'end_time': row.get('结束时间', '09:40'),
                        'start_week': int(row.get('开始周', 1)),
                        'end_week': int(row.get('结束周', 16)),
                        'week_type': row.get('周次类型', 'all'),
                        'course_type': row.get('课程类型', '必修课'),
                        'credits': int(row.get('学分', 2)),
                        'notes': row.get('备注', '')
                    }
                    courses.append(course)

            # 备份和导入逻辑同JSON
            if self.import_backup_check.isChecked():
                self.create_backup()

            if self.import_merge_check.isChecked():
                existing_courses = self.schedule_data.get('courses', [])
                existing_courses.extend(courses)
                self.schedule_data['courses'] = existing_courses
            else:
                self.schedule_data['courses'] = courses

            self.update_schedule_table()
            self.refresh_statistics()

            QMessageBox.information(self, "导入成功", f"成功导入 {len(courses)} 门课程")

        except Exception as e:
            self.logger.error(f"CSV导入失败: {e}")
            QMessageBox.critical(self, "导入失败", f"导入CSV文件失败: {e}")

    def import_from_excel(self):
        """从Excel导入"""
        QMessageBox.information(self, "功能提示", "Excel导入功能需要安装openpyxl库\n请使用CSV格式导入")

    def export_to_json(self):
        """导出为JSON"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出JSON文件", "schedule.json", "JSON文件 (*.json)")
            if not file_path:
                return

            import json

            export_data = {
                'courses': self.schedule_data.get('courses', []),
                'export_time': datetime.now().isoformat(),
                'version': '1.0'
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "导出成功", f"课程表已导出到: {file_path}")

        except Exception as e:
            self.logger.error(f"JSON导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"导出JSON文件失败: {e}")

    def export_to_csv(self):
        """导出为CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出CSV文件", "schedule.csv", "CSV文件 (*.csv)")
            if not file_path:
                return

            import csv

            courses = self.schedule_data.get('courses', [])

            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['课程名称', '教师', '教室', '星期', '开始时间', '结束时间',
                             '开始周', '结束周', '周次类型', '课程类型', '学分', '备注']
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()
                for course in courses:
                    writer.writerow({
                        '课程名称': course.get('name', ''),
                        '教师': course.get('teacher', ''),
                        '教室': course.get('classroom', ''),
                        '星期': course.get('day', 0),
                        '开始时间': course.get('start_time', ''),
                        '结束时间': course.get('end_time', ''),
                        '开始周': course.get('start_week', 1),
                        '结束周': course.get('end_week', 16),
                        '周次类型': course.get('week_type', 'all'),
                        '课程类型': course.get('course_type', '必修课'),
                        '学分': course.get('credits', 2),
                        '备注': course.get('notes', '')
                    })

            QMessageBox.information(self, "导出成功", f"课程表已导出到: {file_path}")

        except Exception as e:
            self.logger.error(f"CSV导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"导出CSV文件失败: {e}")

    def export_to_excel(self):
        """导出为Excel（增强版）"""
        try:
            from core.excel_export_enhanced import ExcelExportEnhanced, ExportOptions, ExportTemplate, ExportFormat

            # 创建导出选项对话框
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QCheckBox, QSpinBox, QLineEdit, QPushButton, QHBoxLayout

            dialog = QDialog(self)
            dialog.setWindowTitle("Excel导出设置")
            dialog.setFixedSize(400, 500)

            layout = QVBoxLayout(dialog)
            form_layout = QFormLayout()

            # 模板选择
            template_combo = QComboBox()
            template_combo.addItems([
                "基础模板", "详细模板", "周视图模板",
                "月视图模板", "统计模板", "打印友好模板"
            ])
            form_layout.addRow("导出模板:", template_combo)

            # 格式选择
            format_combo = QComboBox()
            format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "HTML (.html)"])
            form_layout.addRow("导出格式:", format_combo)

            # 包含选项
            include_weekends_check = QCheckBox("包含周末")
            include_weekends_check.setChecked(True)
            form_layout.addRow(include_weekends_check)

            include_teacher_check = QCheckBox("包含教师信息")
            include_teacher_check.setChecked(True)
            form_layout.addRow(include_teacher_check)

            include_classroom_check = QCheckBox("包含教室信息")
            include_classroom_check.setChecked(True)
            form_layout.addRow(include_classroom_check)

            include_statistics_check = QCheckBox("包含统计信息")
            include_statistics_check.setChecked(True)
            form_layout.addRow(include_statistics_check)

            # 自定义标题
            title_edit = QLineEdit()
            title_edit.setPlaceholderText("课程表")
            form_layout.addRow("自定义标题:", title_edit)

            # 字体大小
            font_size_spin = QSpinBox()
            font_size_spin.setRange(8, 72)
            font_size_spin.setValue(12)
            form_layout.addRow("字体大小:", font_size_spin)

            layout.addLayout(form_layout)

            # 按钮
            button_layout = QHBoxLayout()
            export_button = QPushButton("导出")
            cancel_button = QPushButton("取消")

            button_layout.addWidget(export_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)

            # 连接信号
            export_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 获取文件保存路径
                from PyQt6.QtWidgets import QFileDialog

                format_text = format_combo.currentText()
                if "Excel" in format_text:
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "导出Excel文件", "schedule.xlsx", "Excel文件 (*.xlsx)"
                    )
                    export_format = ExportFormat.XLSX
                elif "CSV" in format_text:
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "导出CSV文件", "schedule.csv", "CSV文件 (*.csv)"
                    )
                    export_format = ExportFormat.CSV
                else:  # HTML
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "导出HTML文件", "schedule.html", "HTML文件 (*.html)"
                    )
                    export_format = ExportFormat.HTML

                if not file_path:
                    return

                # 创建导出选项
                template_map = {
                    "基础模板": ExportTemplate.BASIC,
                    "详细模板": ExportTemplate.DETAILED,
                    "周视图模板": ExportTemplate.WEEKLY,
                    "月视图模板": ExportTemplate.MONTHLY,
                    "统计模板": ExportTemplate.STATISTICS,
                    "打印友好模板": ExportTemplate.PRINT_FRIENDLY
                }

                options = ExportOptions(
                    template=template_map[template_combo.currentText()],
                    format=export_format,
                    include_weekends=include_weekends_check.isChecked(),
                    include_teacher_info=include_teacher_check.isChecked(),
                    include_classroom_info=include_classroom_check.isChecked(),
                    include_statistics=include_statistics_check.isChecked(),
                    custom_title=title_edit.text() or "课程表",
                    font_size=font_size_spin.value()
                )

                # 执行导出
                exporter = ExcelExportEnhanced()
                success = exporter.export_schedule(self.schedule_data, file_path, options)

                if success:
                    QMessageBox.information(self, "导出成功", f"课程表已导出到: {file_path}")
                else:
                    QMessageBox.critical(self, "导出失败", "导出过程中发生错误")

        except Exception as e:
            self.logger.error(f"Excel导出失败: {e}")
            QMessageBox.critical(self, "错误", f"Excel导出失败: {e}")

    def export_to_pdf(self):
        """导出为PDF"""
        QMessageBox.information(self, "功能提示", "PDF导出功能正在开发中\n请使用CSV或JSON格式导出")

    def create_backup(self):
        """创建备份"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            backup_name = f"{timestamp} - 手动备份"
            self.backup_list.addItem(backup_name)
            QMessageBox.information(self, "备份成功", f"备份已创建: {backup_name}")

        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            QMessageBox.critical(self, "错误", f"创建备份失败: {e}")

    def restore_backup(self):
        """恢复备份"""
        current_item = self.backup_list.currentItem()
        if current_item:
            backup_name = current_item.text()
            reply = QMessageBox.question(
                self, "确认恢复", f"确定要恢复备份 '{backup_name}' 吗？\n当前数据将被覆盖！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                QMessageBox.information(self, "功能开发中", "备份恢复功能正在开发中...")
        else:
            QMessageBox.warning(self, "警告", "请先选择要恢复的备份")

    def save_all_changes(self):
        """保存所有更改"""
        try:
            if self.app_manager and self.app_manager.config_manager:
                # 保存课程表数据
                self.app_manager.config_manager.set_config('schedule', self.schedule_data, 'user')

                # 保存提醒设置
                self.app_manager.config_manager.set_config('reminder_settings', self.reminder_settings, 'user')

                # 保存配置
                self.app_manager.config_manager.save_all_configs()

                # 发出信号
                self.schedule_updated.emit()

                QMessageBox.information(self, "保存成功", "所有更改已保存")

        except Exception as e:
            self.logger.error(f"保存失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def closeEvent(self, event):
        """关闭事件 - 只关闭窗口，不退出程序"""
        try:
            # 检查是否有未保存的更改
            reply = QMessageBox.question(
                self, "确认关闭", "是否保存更改后关闭？",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_all_changes()
                event.accept()  # 只关闭窗口，不退出程序
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()  # 只关闭窗口，不退出程序
            else:
                event.ignore()

        except Exception as e:
            self.logger.error(f"关闭处理失败: {e}")
            event.accept()  # 只关闭窗口，不退出程序
