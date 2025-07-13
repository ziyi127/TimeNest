#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 课程表编辑器
提供可视化的课程表编辑功能
"""

import logging
from typing import Optional, Dict, List, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
    QTimeEdit, QColorDialog, QTableWidget, QTableWidgetItem,
    QTabWidget, QWidget, QTextEdit, QCheckBox, QGroupBox,
    QScrollArea, QMessageBox, QFileDialog, QSplitter,
    QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QTime, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon

from ..models.schedule import Schedule, Subject, TimeSlot, ClassItem


class ScheduleEditor(QDialog):
    """
    课程表编辑器
    
    提供完整的课程表编辑功能，包括：
    - 课程表基本信息编辑
    - 科目管理
    - 时间段管理
    - 课程安排
    - 预览和导出
    """
    
    # 信号定义
    schedule_saved = pyqtSignal(object)  # 课程表保存完成
    schedule_changed = pyqtSignal()      # 课程表发生变化
    
    def __init__(self, schedule: Optional[Schedule] = None, parent=None):
        """
        初始化课程表编辑器
        
        Args:
            schedule: 要编辑的课程表，如果为None则创建新课程表
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.ScheduleEditor')
        
        # 课程表数据
        self.schedule = schedule or Schedule()
        self.original_schedule = self.schedule.copy() if schedule else None
        
        # 编辑状态
        self.is_modified = False
        self.current_subject = None
        self.current_time_slot = None
        
        # 初始化UI
        self.init_ui()
        
        # 加载数据
        self.load_schedule_data()
        
        # 连接信号
        self.connect_signals()
        
        self.logger.info("课程表编辑器初始化完成")
    
    def init_ui(self):
        """
        初始化用户界面
        """
        self.setWindowTitle("课程表编辑器")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("新建")
        self.open_btn = QPushButton("打开")
        self.save_btn = QPushButton("保存")
        self.save_as_btn = QPushButton("另存为")
        self.preview_btn = QPushButton("预览")
        self.export_btn = QPushButton("导出")
        
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addWidget(self.open_btn)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.save_as_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.preview_btn)
        toolbar_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 700])
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.apply_btn = QPushButton("应用")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_left_panel(self) -> QWidget:
        """
        创建左侧面板
        
        Returns:
            左侧面板widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 课程表信息
        info_group = QGroupBox("课程表信息")
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel("名称:"), 0, 0)
        self.name_edit = QLineEdit()
        info_layout.addWidget(self.name_edit, 0, 1)
        
        info_layout.addWidget(QLabel("学期:"), 1, 0)
        self.semester_edit = QLineEdit()
        info_layout.addWidget(self.semester_edit, 1, 1)
        
        info_layout.addWidget(QLabel("描述:"), 2, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        info_layout.addWidget(self.description_edit, 2, 1)
        
        layout.addWidget(info_group)
        
        # 科目管理
        subject_group = QGroupBox("科目管理")
        subject_layout = QVBoxLayout(subject_group)
        
        subject_btn_layout = QHBoxLayout()
        self.add_subject_btn = QPushButton("添加科目")
        self.edit_subject_btn = QPushButton("编辑科目")
        self.delete_subject_btn = QPushButton("删除科目")
        
        subject_btn_layout.addWidget(self.add_subject_btn)
        subject_btn_layout.addWidget(self.edit_subject_btn)
        subject_btn_layout.addWidget(self.delete_subject_btn)
        subject_layout.addLayout(subject_btn_layout)
        
        self.subject_list = QListWidget()
        subject_layout.addWidget(self.subject_list)
        
        layout.addWidget(subject_group)
        
        # 时间段管理
        timeslot_group = QGroupBox("时间段管理")
        timeslot_layout = QVBoxLayout(timeslot_group)
        
        timeslot_btn_layout = QHBoxLayout()
        self.add_timeslot_btn = QPushButton("添加时间段")
        self.edit_timeslot_btn = QPushButton("编辑时间段")
        self.delete_timeslot_btn = QPushButton("删除时间段")
        
        timeslot_btn_layout.addWidget(self.add_timeslot_btn)
        timeslot_btn_layout.addWidget(self.edit_timeslot_btn)
        timeslot_btn_layout.addWidget(self.delete_timeslot_btn)
        timeslot_layout.addLayout(timeslot_btn_layout)
        
        self.timeslot_list = QListWidget()
        timeslot_layout.addWidget(self.timeslot_list)
        
        layout.addWidget(timeslot_group)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """
        创建右侧面板
        
        Returns:
            右侧面板widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 课程表视图
        self.schedule_tab = self.create_schedule_tab()
        self.tab_widget.addTab(self.schedule_tab, "课程表")
        
        # 课程编辑
        self.class_tab = self.create_class_tab()
        self.tab_widget.addTab(self.class_tab, "课程编辑")
        
        # 预览
        self.preview_tab = self.create_preview_tab()
        self.tab_widget.addTab(self.preview_tab, "预览")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def create_schedule_tab(self) -> QWidget:
        """
        创建课程表标签页
        
        Returns:
            课程表标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 课程表表格
        self.schedule_table = QTableWidget()
        self.schedule_table.setRowCount(12)  # 12个时间段
        self.schedule_table.setColumnCount(7)  # 7天
        
        # 设置表头
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.schedule_table.setHorizontalHeaderLabels(weekdays)
        
        # 设置行标签（时间段）
        self.update_schedule_table_headers()
        
        # 设置表格属性
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.schedule_table)
        
        return tab
    
    def create_class_tab(self) -> QWidget:
        """
        创建课程编辑标签页
        
        Returns:
            课程编辑标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 课程编辑表单
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("科目:"), 0, 0)
        self.class_subject_combo = QComboBox()
        form_layout.addWidget(self.class_subject_combo, 0, 1)
        
        form_layout.addWidget(QLabel("时间段:"), 1, 0)
        self.class_timeslot_combo = QComboBox()
        form_layout.addWidget(self.class_timeslot_combo, 1, 1)
        
        form_layout.addWidget(QLabel("星期:"), 2, 0)
        self.class_weekday_combo = QComboBox()
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.class_weekday_combo.addItems(weekdays)
        form_layout.addWidget(self.class_weekday_combo, 2, 1)
        
        form_layout.addWidget(QLabel("周次:"), 3, 0)
        self.class_weeks_edit = QLineEdit()
        self.class_weeks_edit.setPlaceholderText("例如: 1-16 或 1,3,5-8")
        form_layout.addWidget(self.class_weeks_edit, 3, 1)
        
        layout.addLayout(form_layout)
        
        # 课程操作按钮
        class_btn_layout = QHBoxLayout()
        self.add_class_btn = QPushButton("添加课程")
        self.update_class_btn = QPushButton("更新课程")
        self.delete_class_btn = QPushButton("删除课程")
        
        class_btn_layout.addWidget(self.add_class_btn)
        class_btn_layout.addWidget(self.update_class_btn)
        class_btn_layout.addWidget(self.delete_class_btn)
        class_btn_layout.addStretch()
        
        layout.addLayout(class_btn_layout)
        
        # 课程列表
        self.class_list = QListWidget()
        layout.addWidget(self.class_list)
        
        return tab
    
    def create_preview_tab(self) -> QWidget:
        """
        创建预览标签页
        
        Returns:
            预览标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 预览控制
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("预览周次:"))
        self.preview_week_spin = QSpinBox()
        self.preview_week_spin.setRange(1, 20)
        self.preview_week_spin.setValue(1)
        control_layout.addWidget(self.preview_week_spin)
        
        self.refresh_preview_btn = QPushButton("刷新预览")
        control_layout.addWidget(self.refresh_preview_btn)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 预览表格
        self.preview_table = QTableWidget()
        self.preview_table.setRowCount(12)
        self.preview_table.setColumnCount(7)
        
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.preview_table.setHorizontalHeaderLabels(weekdays)
        
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.preview_table)
        
        return tab
    
    def connect_signals(self):
        """
        连接信号和槽
        """
        # 工具栏按钮
        self.new_btn.clicked.connect(self.new_schedule)
        self.open_btn.clicked.connect(self.open_schedule)
        self.save_btn.clicked.connect(self.save_schedule)
        self.save_as_btn.clicked.connect(self.save_schedule_as)
        self.preview_btn.clicked.connect(self.preview_schedule)
        self.export_btn.clicked.connect(self.export_schedule)
        
        # 科目管理
        self.add_subject_btn.clicked.connect(self.add_subject)
        self.edit_subject_btn.clicked.connect(self.edit_subject)
        self.delete_subject_btn.clicked.connect(self.delete_subject)
        self.subject_list.currentItemChanged.connect(self.on_subject_selected)
        
        # 时间段管理
        self.add_timeslot_btn.clicked.connect(self.add_timeslot)
        self.edit_timeslot_btn.clicked.connect(self.edit_timeslot)
        self.delete_timeslot_btn.clicked.connect(self.delete_timeslot)
        self.timeslot_list.currentItemChanged.connect(self.on_timeslot_selected)
        
        # 课程管理
        self.add_class_btn.clicked.connect(self.add_class)
        self.update_class_btn.clicked.connect(self.update_class)
        self.delete_class_btn.clicked.connect(self.delete_class)
        self.class_list.currentItemChanged.connect(self.on_class_selected)
        
        # 预览
        self.refresh_preview_btn.clicked.connect(self.refresh_preview)
        self.preview_week_spin.valueChanged.connect(self.refresh_preview)
        
        # 底部按钮
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self.apply_changes)
        
        # 数据变化
        self.name_edit.textChanged.connect(self.mark_modified)
        self.semester_edit.textChanged.connect(self.mark_modified)
        self.description_edit.textChanged.connect(self.mark_modified)
    
    def load_schedule_data(self):
        """
        加载课程表数据到界面
        """
        try:
            # 基本信息
            self.name_edit.setText(self.schedule.name)
            self.semester_edit.setText(self.schedule.semester)
            self.description_edit.setPlainText(self.schedule.description or "")
            
            # 科目列表
            self.update_subject_list()
            
            # 时间段列表
            self.update_timeslot_list()
            
            # 课程列表
            self.update_class_list()
            
            # 更新课程表
            self.update_schedule_table()
            
            # 更新预览
            self.refresh_preview()
            
            self.logger.info("课程表数据加载完成")
            
        except Exception as e:
            self.logger.error(f"加载课程表数据失败: {e}", exc_info=True)
            QMessageBox.warning(self, "警告", f"加载数据失败: {str(e)}")
    
    def update_subject_list(self):
        """
        更新科目列表
        """
        self.subject_list.clear()
        self.class_subject_combo.clear()
        
        for subject in self.schedule.subjects:
            item = QListWidgetItem(f"{subject.name} ({subject.teacher})")
            item.setData(Qt.ItemDataRole.UserRole, subject.id)
            self.subject_list.addItem(item)
            
            self.class_subject_combo.addItem(subject.name, subject.id)
    
    def update_timeslot_list(self):
        """
        更新时间段列表
        """
        self.timeslot_list.clear()
        self.class_timeslot_combo.clear()
        
        for timeslot in self.schedule.time_slots:
            item = QListWidgetItem(f"{timeslot.name} ({timeslot.start_time}-{timeslot.end_time})")
            item.setData(Qt.ItemDataRole.UserRole, timeslot.id)
            self.timeslot_list.addItem(item)
            
            self.class_timeslot_combo.addItem(
                f"{timeslot.name} ({timeslot.start_time}-{timeslot.end_time})",
                timeslot.id
            )
        
        # 更新课程表表头
        self.update_schedule_table_headers()
    
    def update_class_list(self):
        """
        更新课程列表
        """
        self.class_list.clear()
        
        for class_item in self.schedule.classes:
            subject = self.schedule.get_subject(class_item.subject_id)
            timeslot = self.schedule.get_time_slot(class_item.time_slot_id)
            
            
            if subject and timeslot:
                weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            
                weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                weekday_name = weekday_names[class_item.day_of_week - 1]
                
                weeks_str = ','.join(map(str, class_item.weeks))
                
                item_text = f"{subject.name} - {timeslot.name} - {weekday_name} - 周次:{weeks_str}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, class_item)
                self.class_list.addItem(item)
    
    def update_schedule_table(self):
        """
        更新课程表表格
        """
        # 清空表格
        for row in range(self.schedule_table.rowCount()):
            for col in range(self.schedule_table.columnCount()):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        # 填充课程数据
        for class_item in self.schedule.classes:
            subject = self.schedule.get_subject(class_item.subject_id)
            timeslot = self.schedule.get_time_slot(class_item.time_slot_id)
            
            
            if subject and timeslot:
                # 找到时间段在表格中的行:
            
                # 找到时间段在表格中的行
                row = -1
                for i, ts in enumerate(self.schedule.time_slots):
                    if ts.id == timeslot.id:
                        row = i
                        break
                
                
                if row >= 0 and row < self.schedule_table.rowCount():
                    col = class_item.day_of_week - 1
                
                    col = class_item.day_of_week - 1
                    if col >= 0 and col < self.schedule_table.columnCount():
                        item = QTableWidgetItem(subject.name)
                        item.setBackground(QColor(subject.color))
                        item.setData(Qt.ItemDataRole.UserRole, class_item)
                        self.schedule_table.setItem(row, col, item)
    
    def update_schedule_table_headers(self):
        """
        更新课程表表格的行标签
        """
        headers = []
        for i, timeslot in enumerate(self.schedule.time_slots):
            if i < self.schedule_table.rowCount():
                headers.append(f"{timeslot.name}\n{timeslot.start_time}-{timeslot.end_time}")
        
        # 补充空标签
        while len(headers) < self.schedule_table.rowCount():
            headers.append("")
        
        self.schedule_table.setVerticalHeaderLabels(headers)
    
    def refresh_preview(self):
        """
        刷新预览
        """
        try:
            week = self.preview_week_spin.value()
            
            # 清空预览表格
            for row in range(self.preview_table.rowCount()):
                for col in range(self.preview_table.columnCount()):
                    self.preview_table.setItem(row, col, QTableWidgetItem(""))
            
            # 设置行标签
            headers = []
            for i, timeslot in enumerate(self.schedule.time_slots):
                if i < self.preview_table.rowCount():
                    headers.append(f"{timeslot.name}\n{timeslot.start_time}-{timeslot.end_time}")
            
            while len(headers) < self.preview_table.rowCount():
                headers.append("")
            
            self.preview_table.setVerticalHeaderLabels(headers)
            
            # 填充指定周次的课程
            for class_item in self.schedule.classes:
                if week in class_item.weeks:
                    subject = self.schedule.get_subject(class_item.subject_id)
                    timeslot = self.schedule.get_time_slot(class_item.time_slot_id)
                    
                    
                    if subject and timeslot:
                        row = -1
                    
                        row = -1
                        for i, ts in enumerate(self.schedule.time_slots):
                            if ts.id == timeslot.id:
                                row = i
                                break
                        
                        
                        if row >= 0 and row < self.preview_table.rowCount():
                            col = class_item.day_of_week - 1
                        
                            col = class_item.day_of_week - 1
                            if col >= 0 and col < self.preview_table.columnCount():
                                item_text = f"{subject.name}\n{subject.teacher}\n{subject.location}"
                                item = QTableWidgetItem(item_text)
                                item.setBackground(QColor(subject.color))
                                self.preview_table.setItem(row, col, item)
            
        except Exception as e:
            self.logger.error(f"刷新预览失败: {e}", exc_info=True)
    
    def mark_modified(self):
        """
        标记为已修改
        """
        if not self.is_modified:
            self.is_modified = True
            self.setWindowTitle(self.windowTitle() + " *")
            self.schedule_changed.emit()
    
    def new_schedule(self):
        """
        新建课程表
        """
        if self.is_modified:
            reply = QMessageBox.question(
                self, "确认", "当前课程表已修改，是否保存？",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_schedule():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.schedule = Schedule()
        self.original_schedule = None
        self.is_modified = False
        self.setWindowTitle("课程表编辑器")
        
        self.load_schedule_data()
    
    def open_schedule(self):
        """
        打开课程表文件
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开课程表", "",
            "JSON文件 (*.json);;YAML文件 (*.yaml *.yml);;所有文件 (*)"
        )
        
        
        if file_path:
            try:
                self.schedule = Schedule.load_from_file(file_path)
                self.original_schedule = self.schedule.copy()
                self.is_modified = False
                self.setWindowTitle(f"课程表编辑器 - {file_path}")
                
                self.load_schedule_data()
                
            except Exception as e:
                self.logger.error(f"打开课程表失败: {e}", exc_info=True)
                QMessageBox.critical(self, "错误", f"打开文件失败: {str(e)}")
    
    def save_schedule(self) -> bool:
        """
        保存课程表
        
        Returns:
            是否保存成功
        """
        if not hasattr(self, '_save_path') or not self._save_path:
            return self.save_schedule_as()
        
        try:
            self.apply_form_data()
            self.schedule.save_to_file(self._save_path)
            
            self.is_modified = False
            self.setWindowTitle(f"课程表编辑器 - {self._save_path}")
            
            self.schedule_saved.emit(self.schedule)
            
            QMessageBox.information(self, "成功", "课程表保存成功")
            return True
            
        except Exception as e:
            self.logger.error(f"保存课程表失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
            return False
    
    def save_schedule_as(self) -> bool:
        """
        另存为课程表
        
        Returns:
            是否保存成功
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存课程表", "",
            "JSON文件 (*.json);;YAML文件 (*.yaml);;所有文件 (*)"
        )
        
        
        if file_path:
            try:
                self.apply_form_data()
                self.schedule.save_to_file(file_path)
                
                self._save_path = file_path
                self.is_modified = False
                self.setWindowTitle(f"课程表编辑器 - {file_path}")
                
                self.schedule_saved.emit(self.schedule)
                
                QMessageBox.information(self, "成功", "课程表保存成功")
                return True
                
            except Exception as e:
                self.logger.error(f"保存课程表失败: {e}", exc_info=True)
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
                return False
        
        return False
    
    def apply_form_data(self):
        """
        应用表单数据到课程表对象
        """
        self.schedule.name = self.name_edit.text()
        self.schedule.semester = self.semester_edit.text()
        self.schedule.description = self.description_edit.toPlainText()
    
    def apply_changes(self):
        """
        应用更改
        """
        try:
            self.apply_form_data()
            self.schedule_saved.emit(self.schedule)
            self.is_modified = False
            
            QMessageBox.information(self, "成功", "更改已应用")
            
        except Exception as e:
            self.logger.error(f"应用更改失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"应用更改失败: {str(e)}")
    
    def preview_schedule(self):
        """
        预览课程表
        """
        self.tab_widget.setCurrentWidget(self.preview_tab)
        self.refresh_preview()
    
    def export_schedule(self):
        """
        导出课程表
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出课程表", "",
            "Excel文件 (*.xlsx);;PDF文件 (*.pdf);;图片文件 (*.png);;所有文件 (*)"
        )
        
        
        if file_path:
            try:
                self.apply_form_data()
                
                if file_path.endswith('.xlsx'):
                    self.schedule.export_to_excel(file_path)
                elif file_path.endswith('.pdf'):
                    self.export_to_pdf(file_path)
                elif file_path.endswith('.png'):
                    self.export_to_image(file_path)
                
                QMessageBox.information(self, "成功", "课程表导出成功")
                
            except Exception as e:
                self.logger.error(f"导出课程表失败: {e}", exc_info=True)
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def export_to_pdf(self, file_path: str):
        """导出为PDF"""
        try:
            from PyQt6.QtPrintSupport import QPrinter
            from PyQt6.QtGui import QPainter, QTextDocument
            from PyQt6.QtCore import QSizeF
            
            # 创建HTML内容
            html_content = self.generate_schedule_html()
            
            # 创建文档
            document = QTextDocument()
            document.setHtml(html_content)
            
            # 创建打印机
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPrinter.PageSize.A4)
            
            # 打印到PDF
            document.print(printer)
            
        except Exception as e:
            self.logger.error(f"PDF导出失败: {e}", exc_info=True)
            raise e
    
    def export_to_image(self, file_path: str):
        """导出为图片"""
        try:
            from PyQt6.QtGui import QPainter, QPixmap
            from PyQt6.QtCore import QSize
            
            # 创建课程表的截图
            widget = self.schedule_table
            size = QSize(widget.width(), widget.height())
            
            # 创建像素图
            pixmap = QPixmap(size)
            pixmap.fill()
            
            # 绘制widget到像素图
            painter = QPainter(pixmap)
            widget.render(painter)
            painter.end()
            
            # 保存图片
            pixmap.save(file_path, "PNG")
            
        except Exception as e:
            self.logger.error(f"图片导出失败: {e}", exc_info=True)
            raise e
    
    def generate_schedule_html(self) -> str:
        """生成课程表的HTML内容"""
        try:
            html = """<!DOCTYPE html>
            <html>
            <head>
                <meta charset='utf-8'>
                <title>课程表</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                    th { background-color: #f2f2f2; }
                    .class-cell { background-color: #e3f2fd; }
                </style>
            </head>
            <body>
                <h1>课程表</h1>
                <table>
                    <tr>
                        <th>时间</th>
                        <th>周一</th>
                        <th>周二</th>
                        <th>周三</th>
                        <th>周四</th>
                        <th>周五</th>
                        <th>周六</th>
                        <th>周日</th>
                    </tr>
            """
            
            # 获取时间段
            time_slots = self.schedule.get_time_slots()
            
            for time_slot in time_slots:
                html += f"<tr><td>{time_slot.name}<br>{time_slot.start_time}-{time_slot.end_time}</td>"
                
                # 遍历一周的每一天
                for weekday in range(1, 8):
                    classes = self.schedule.get_classes_by_time_and_day(time_slot.id, weekday)
                    if classes:
                        class_info = classes[0]  # 取第一个课程
                        subject = self.schedule.get_subject(class_info.subject_id)
                        html += f"<td class='class-cell'>{subject.name}<br>{subject.teacher}<br>{subject.location}</td>"
                    else:
                        html += "<td></td>"
                
                html += "</tr>"
            
            html += """</table>
            </body>
            </html>"""
            
            return html
            
        except Exception as e:
            self.logger.error(f"生成HTML失败: {e}", exc_info=True)
            return "<html><body><h1>生成课程表失败</h1></body></html>"
    
    # 科目管理方法
    def add_subject(self):
        """
        添加科目
        """
        dialog = SubjectDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            subject = dialog.get_subject()
            self.schedule.add_subject(subject)
            self.update_subject_list()
            self.mark_modified()
    
    def edit_subject(self):
        """
        编辑科目
        """
        current_item = self.subject_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要编辑的科目")
            return
        
        subject_id = current_item.data(Qt.ItemDataRole.UserRole)
        subject = self.schedule.get_subject(subject_id)
        
        
        if subject:
            dialog = SubjectDialog(subject, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_subject = dialog.get_subject()
                self.schedule.update_subject(subject_id, updated_subject)
                self.update_subject_list()
                self.update_schedule_table()
                self.mark_modified()
    
    def delete_subject(self):
        """
        删除科目
        """
        current_item = self.subject_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的科目")
            return
        
        subject_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除选中的科目吗？这将同时删除相关的课程。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        
        if reply == QMessageBox.StandardButton.Yes:
            self.schedule.remove_subject(subject_id)
            self.update_subject_list()
            self.update_class_list()
            self.update_schedule_table()
            self.mark_modified()
    
    def on_subject_selected(self, current, previous):
        """
        科目选择变化
        """
        if current:
            self.current_subject = current.data(Qt.ItemDataRole.UserRole)
    
    # 时间段管理方法
    def add_timeslot(self):
        """
        添加时间段
        """
        dialog = TimeSlotDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            timeslot = dialog.get_timeslot()
            self.schedule.add_time_slot(timeslot)
            self.update_timeslot_list()
            self.mark_modified()
    
    def edit_timeslot(self):
        """
        编辑时间段
        """
        current_item = self.timeslot_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要编辑的时间段")
            return
        
        timeslot_id = current_item.data(Qt.ItemDataRole.UserRole)
        timeslot = self.schedule.get_time_slot(timeslot_id)
        
        
        if timeslot:
            dialog = TimeSlotDialog(timeslot, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_timeslot = dialog.get_timeslot()
                self.schedule.update_time_slot(timeslot_id, updated_timeslot)
                self.update_timeslot_list()
                self.update_schedule_table()
                self.mark_modified()
    
    def delete_timeslot(self):
        """
        删除时间段
        """
        current_item = self.timeslot_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的时间段")
            return
        
        timeslot_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除选中的时间段吗？这将同时删除相关的课程。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        
        if reply == QMessageBox.StandardButton.Yes:
            self.schedule.remove_time_slot(timeslot_id)
            self.update_timeslot_list()
            self.update_class_list()
            self.update_schedule_table()
            self.mark_modified()
    
    def on_timeslot_selected(self, current, previous):
        """
        时间段选择变化
        """
        if current:
            self.current_time_slot = current.data(Qt.ItemDataRole.UserRole)
    
    # 课程管理方法
    def add_class(self):
        """
        添加课程
        """
        try:
            subject_id = self.class_subject_combo.currentData()
            timeslot_id = self.class_timeslot_combo.currentData()
            weekday = self.class_weekday_combo.currentIndex() + 1
            weeks_text = self.class_weeks_edit.text().strip()
            
            
            if not subject_id or not timeslot_id:
                QMessageBox.warning(self, "警告", "请选择科目和时间段")
                return
            
            if not weeks_text:
                QMessageBox.warning(self, "警告", "请输入周次")
                return
            
            # 解析周次
            weeks = self.parse_weeks(weeks_text)
            if not weeks:
                QMessageBox.warning(self, "警告", "周次格式错误")
                return
            
            # 创建课程
            class_item = ClassItem(
                subject_id=subject_id,
                time_slot_id=timeslot_id,
                day_of_week=weekday,
                weeks=weeks
            )
            
            self.schedule.add_class(class_item)
            self.update_class_list()
            self.update_schedule_table()
            self.mark_modified()
            
            # 清空表单
            self.class_weeks_edit.clear()
            
        except Exception as e:
            self.logger.error(f"添加课程失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"添加课程失败: {str(e)}")
    
    def update_class(self):
        """
        更新课程
        """
        current_item = self.class_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要更新的课程")
            return
        
        try:
            class_item = current_item.data(Qt.ItemDataRole.UserRole)
            
            subject_id = self.class_subject_combo.currentData()
            timeslot_id = self.class_timeslot_combo.currentData()
            weekday = self.class_weekday_combo.currentIndex() + 1
            weeks_text = self.class_weeks_edit.text().strip()
            
            
            if not subject_id or not timeslot_id:
                QMessageBox.warning(self, "警告", "请选择科目和时间段")
            
                QMessageBox.warning(self, "警告", "请选择科目和时间段")
                return
            
            
            if not weeks_text:
                QMessageBox.warning(self, "警告", "请输入周次")
            
                QMessageBox.warning(self, "警告", "请输入周次")
                return
            
            # 解析周次
            weeks = self.parse_weeks(weeks_text)
            if not weeks:
                QMessageBox.warning(self, "警告", "周次格式错误")
                return
            
            # 更新课程
            class_item.subject_id = subject_id
            class_item.time_slot_id = timeslot_id
            class_item.day_of_week = weekday
            class_item.weeks = weeks
            
            self.update_class_list()
            self.update_schedule_table()
            self.mark_modified()
            
        except Exception as e:
            self.logger.error(f"更新课程失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"更新课程失败: {str(e)}")
    
    def delete_class(self):
        """
        删除课程
        """
        current_item = self.class_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的课程")
            return
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除选中的课程吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        
        if reply == QMessageBox.StandardButton.Yes:
            class_item = current_item.data(Qt.ItemDataRole.UserRole)
        
            class_item = current_item.data(Qt.ItemDataRole.UserRole)
            self.schedule.remove_class(class_item)
            self.update_class_list()
            self.update_schedule_table()
            self.mark_modified()
    
    def on_class_selected(self, current, previous):
        """
        课程选择变化
        """
        if current:
            class_item = current.data(Qt.ItemDataRole.UserRole)
            
            # 更新表单
            for i in range(self.class_subject_combo.count()):
                if self.class_subject_combo.itemData(i) == class_item.subject_id:
                    self.class_subject_combo.setCurrentIndex(i)
                    break
            
            for i in range(self.class_timeslot_combo.count()):
                if self.class_timeslot_combo.itemData(i) == class_item.time_slot_id:
                    self.class_timeslot_combo.setCurrentIndex(i)
                    break
            
            self.class_weekday_combo.setCurrentIndex(class_item.day_of_week - 1)
            
            weeks_text = ','.join(map(str, sorted(class_item.weeks)))
            self.class_weeks_edit.setText(weeks_text)
    
    def parse_weeks(self, weeks_text: str) -> List[int]:
        """
        解析周次字符串
        
        Args:
            weeks_text: 周次字符串，如 "1-16" 或 "1,3,5-8"
            
        Returns:
            周次列表
        """
        try:
            weeks = set()
            
            for part in weeks_text.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    weeks.update(range(start, end + 1))
                else:
                    weeks.add(int(part))
            
            return sorted(list(weeks))
            
        except ValueError:
            return []
    
    def closeEvent(self, event):
        """
        关闭事件处理
        """
        if self.is_modified:
            reply = QMessageBox.question(
                self, "确认", "当前课程表已修改，是否保存？",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_schedule():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        event.accept()


class SubjectDialog(QDialog):
    """
    科目编辑对话框
    """
    
    def __init__(self, subject: Optional[Subject] = None, parent=None):
        super().__init__(parent)
        
        self.subject = subject
        self.init_ui()
        
        
        if subject:
            self.load_subject_data()
    
    def init_ui(self):
        """
        初始化UI
        """
        self.setWindowTitle("科目编辑")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 表单
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("科目名称:"), 0, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 0, 1)
        
        form_layout.addWidget(QLabel("教师:"), 1, 0)
        self.teacher_edit = QLineEdit()
        form_layout.addWidget(self.teacher_edit, 1, 1)
        
        form_layout.addWidget(QLabel("教室:"), 2, 0)
        self.location_edit = QLineEdit()
        form_layout.addWidget(self.location_edit, 2, 1)
        
        form_layout.addWidget(QLabel("颜色:"), 3, 0)
        color_layout = QHBoxLayout()
        self.color_edit = QLineEdit()
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_edit)
        color_layout.addWidget(self.color_btn)
        form_layout.addLayout(color_layout, 3, 1)
        
        form_layout.addWidget(QLabel("学分:"), 4, 0)
        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(0, 10)
        form_layout.addWidget(self.credits_spin, 4, 1)
        
        form_layout.addWidget(QLabel("描述:"), 5, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form_layout.addWidget(self.description_edit, 5, 1)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_subject_data(self):
        """
        加载科目数据
        """
        if self.subject:
            self.name_edit.setText(self.subject.name)
            self.teacher_edit.setText(self.subject.teacher or "")
            self.location_edit.setText(self.subject.location or "")
            self.color_edit.setText(self.subject.color or "#3498db")
            self.credits_spin.setValue(self.subject.credits or 0)
            self.description_edit.setPlainText(self.subject.description or "")
    
    def choose_color(self):
        """
        选择颜色
        """
        current_color = QColor(self.color_edit.text() or "#3498db")
        color = QColorDialog.getColor(current_color, self, "选择科目颜色")
        
        
        if color.isValid():
            self.color_edit.setText(color.name())
    
    def get_subject(self) -> Subject:
        """
        获取科目对象
        
        Returns:
            科目对象
        """
        subject_id = self.subject.id if self.subject else None
        
        return Subject(
            id=subject_id,
            name=self.name_edit.text(),
            teacher=self.teacher_edit.text(),
            location=self.location_edit.text(),
            color=self.color_edit.text(),
            credits=self.credits_spin.value(),
            description=self.description_edit.toPlainText()
        )


class TimeSlotDialog(QDialog):
    """
    时间段编辑对话框
    """
    
    def __init__(self, timeslot: Optional[TimeSlot] = None, parent=None):
        super().__init__(parent)
        
        self.timeslot = timeslot
        self.init_ui()
        
        
        if timeslot:
            self.load_timeslot_data()
    
    def init_ui(self):
        """
        初始化UI
        """
        self.setWindowTitle("时间段编辑")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        # 表单
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("时间段名称:"), 0, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 0, 1)
        
        form_layout.addWidget(QLabel("开始时间:"), 1, 0)
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        form_layout.addWidget(self.start_time_edit, 1, 1)
        
        form_layout.addWidget(QLabel("结束时间:"), 2, 0)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        form_layout.addWidget(self.end_time_edit, 2, 1)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_timeslot_data(self):
        """
        加载时间段数据
        """
        if self.timeslot:
            self.name_edit.setText(self.timeslot.name)
            
            start_time = QTime.fromString(self.timeslot.start_time, "HH:mm")
            self.start_time_edit.setTime(start_time)
            
            end_time = QTime.fromString(self.timeslot.end_time, "HH:mm")
            self.end_time_edit.setTime(end_time)
    
    def get_timeslot(self) -> TimeSlot:
        """
        获取时间段对象
        
        Returns:
            时间段对象
        """
        timeslot_id = self.timeslot.id if self.timeslot else None
        
        return TimeSlot(
            id=timeslot_id,
            name=self.name_edit.text(),
            start_time=self.start_time_edit.time().toString("HH:mm"),
            end_time=self.end_time_edit.time().toString("HH:mm")
        )