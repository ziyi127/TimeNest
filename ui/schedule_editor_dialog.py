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
TimeNest 课程表编辑对话框
提供快速的课程表编辑功能
"""

import logging
from typing import Dict, List, Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTimeEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialogButtonBox, QGroupBox, QFormLayout, QSpinBox
)
from PyQt6.QtGui import QFont


if TYPE_CHECKING:
    from core.app_manager import AppManager:

    from core.app_manager import AppManager


class ScheduleEditorDialog(QDialog):
    """
    课程表编辑对话框
    
    提供简化的课程表编辑功能，可从系统托盘直接访问
    """
    
    # 信号定义
    schedule_updated = pyqtSignal()  # 课程表更新信号
    
    def __init__(self, app_manager: 'AppManager', parent=None):
        """
        初始化课程表编辑对话框
        
        Args:
            app_manager: 应用管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 依赖注入
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.ScheduleEditorDialog')
        
        # 课程数据
        self.schedule_data = {}
        self.weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.time_slots = [
            ('08:00', '09:40'),  # 第1-2节
            ('10:00', '11:40'),  # 第3-4节
            ('14:00', '15:40'),  # 第5-6节
            ('16:00', '17:40'),  # 第7-8节
            ('19:00', '20:40'),  # 第9-10节
        ]
        
        # 初始化UI
        self.init_ui()
        self.load_schedule_data()
        
        self.logger.debug("课程表编辑对话框初始化完成")
    
    def init_ui(self) -> None:
        """初始化UI"""
        try:
            self.setWindowTitle("课程表编辑")
            self.setFixedSize(800, 600)
            self.setModal(True)
            
            # 主布局
            layout = QVBoxLayout(self)
            
            # 标题
            title_label = QLabel("课程表编辑")
            title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            # 课程表格
            self.create_schedule_table()
            layout.addWidget(self.schedule_table)
            
            # 编辑区域
            edit_group = self.create_edit_group()
            layout.addWidget(edit_group)
            
            # 按钮组
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | 
                QDialogButtonBox.StandardButton.Cancel |
                QDialogButtonBox.StandardButton.Apply
            )
            button_box.accepted.connect(self.accept_changes)
            button_box.rejected.connect(self.reject)
            button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_changes)
            
            layout.addWidget(button_box)
            
        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")
    
    def create_schedule_table(self) -> None:
        """创建课程表格"""
        try:
            self.schedule_table = QTableWidget()
            self.schedule_table.setRowCount(len(self.time_slots))
            self.schedule_table.setColumnCount(len(self.weekdays))
            
            # 设置表头
            self.schedule_table.setHorizontalHeaderLabels(self.weekdays)
            
            # 设置时间段标签
            time_labels = []
            for i, (start, end) in enumerate(self.time_slots):
                time_labels.append(f"第{i*2+1}-{i*2+2}节\n{start}-{end}")
            self.schedule_table.setVerticalHeaderLabels(time_labels)
            
            # 设置表格属性
            self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
            self.schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            
            # 连接选择信号
            self.schedule_table.itemSelectionChanged.connect(self.on_cell_selected)
            
        except Exception as e:
            self.logger.error(f"创建课程表格失败: {e}")
    
    def create_edit_group(self) -> QGroupBox:
        """创建编辑区域"""
        try:
            group = QGroupBox("课程编辑")
            layout = QFormLayout(group)
            
            # 课程名称
            self.course_name_edit = QLineEdit()
            self.course_name_edit.setPlaceholderText("输入课程名称")
            layout.addRow("课程名称:", self.course_name_edit)
            
            # 教室
            self.classroom_edit = QLineEdit()
            self.classroom_edit.setPlaceholderText("输入教室位置")
            layout.addRow("教室:", self.classroom_edit)
            
            # 教师
            self.teacher_edit = QLineEdit()
            self.teacher_edit.setPlaceholderText("输入教师姓名")
            layout.addRow("教师:", self.teacher_edit)
            
            # 周次
            week_layout = QHBoxLayout()
            self.start_week_spin = QSpinBox()
            self.start_week_spin.setRange(1, 20)
            self.start_week_spin.setValue(1)
            
            week_layout.addWidget(QLabel("第"))
            week_layout.addWidget(self.start_week_spin)
            week_layout.addWidget(QLabel("周 至 第"))
            
            self.end_week_spin = QSpinBox()
            self.end_week_spin.setRange(1, 20)
            self.end_week_spin.setValue(16)
            week_layout.addWidget(self.end_week_spin)
            week_layout.addWidget(QLabel("周"))
            
            layout.addRow("周次:", week_layout)
            
            # 操作按钮
            button_layout = QHBoxLayout()
            
            self.add_button = QPushButton("添加课程")
            self.add_button.clicked.connect(self.add_course)
            button_layout.addWidget(self.add_button)
            
            self.update_button = QPushButton("更新课程")
            self.update_button.clicked.connect(self.update_course)
            self.update_button.setEnabled(False)
            button_layout.addWidget(self.update_button)
            
            self.delete_button = QPushButton("删除课程")
            self.delete_button.clicked.connect(self.delete_course)
            self.delete_button.setEnabled(False)
            button_layout.addWidget(self.delete_button)
            
            self.clear_button = QPushButton("清空表单")
            self.clear_button.clicked.connect(self.clear_form)
            button_layout.addWidget(self.clear_button)

            layout.addRow(button_layout)

            # 批量操作按钮
            batch_layout = QHBoxLayout()

            self.import_button = QPushButton("导入课程表")
            self.import_button.clicked.connect(self.import_schedule)
            self.import_button.setToolTip("从文件导入课程表")
            batch_layout.addWidget(self.import_button)

            self.export_button = QPushButton("导出课程表")
            self.export_button.clicked.connect(self.export_schedule)
            self.export_button.setToolTip("导出课程表到文件")
            batch_layout.addWidget(self.export_button)

            self.clear_all_button = QPushButton("清空课程表")
            self.clear_all_button.clicked.connect(self.clear_all_courses)
            self.clear_all_button.setToolTip("清空所有课程")
            batch_layout.addWidget(self.clear_all_button)

            layout.addRow("批量操作:", batch_layout)
            
            return group
            
        except Exception as e:
            self.logger.error(f"创建编辑区域失败: {e}")
            return QGroupBox()
    
    def load_schedule_data(self) -> None:
        """加载课程表数据"""
        try:
            # 从配置管理器加载数据
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.schedule_data = self.app_manager.config_manager.get_config('schedule', {}, 'user')
            
            # 更新表格显示
            self.update_table_display()
            
        except Exception as e:
            self.logger.error(f"加载课程表数据失败: {e}")
    
    def update_table_display(self) -> None:
        """更新表格显示"""
        try:
            # 清空表格
            for row in range(self.schedule_table.rowCount()):
                for col in range(self.schedule_table.columnCount()):
                    self.schedule_table.setItem(row, col, QTableWidgetItem(""))
            
            # 填充课程数据
            for day_index, day in enumerate(self.weekdays):
                day_courses = self.schedule_data.get(day, {})
                for time_index, (start_time, end_time) in enumerate(self.time_slots):
                    time_key = f"{start_time}-{end_time}"
                    if time_key in day_courses:
                        course = day_courses[time_key]
                        course_text = f"{course.get('name', '')}\n{course.get('classroom', '')}"
                        item = QTableWidgetItem(course_text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.schedule_table.setItem(time_index, day_index, item)
            
        except Exception as e:
            self.logger.error(f"更新表格显示失败: {e}")
    
    def on_cell_selected(self) -> None:
        """处理单元格选择"""
        try:
            current_item = self.schedule_table.currentItem()
            if current_item:
                row = self.schedule_table.currentRow()
                col = self.schedule_table.currentColumn()
                
                day = self.weekdays[col]
                start_time, end_time = self.time_slots[row]
                time_key = f"{start_time}-{end_time}"
                
                # 获取课程数据
                day_courses = self.schedule_data.get(day, {})
                course = day_courses.get(time_key, {})
                
                # 填充表单
                self.course_name_edit.setText(course.get('name', ''))
                self.classroom_edit.setText(course.get('classroom', ''))
                self.teacher_edit.setText(course.get('teacher', ''))
                self.start_week_spin.setValue(course.get('start_week', 1))
                self.end_week_spin.setValue(course.get('end_week', 16))
                
                # 更新按钮状态
                has_course = bool(course.get('name'))
                self.update_button.setEnabled(has_course)
                self.delete_button.setEnabled(has_course)
                
        except Exception as e:
            self.logger.error(f"处理单元格选择失败: {e}")
    
    def add_course(self) -> None:
        """添加课程"""
        try:
            if not self.validate_form():
                return:
                return
            
            current_item = self.schedule_table.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个时间段")
                return
            
            row = self.schedule_table.currentRow()
            col = self.schedule_table.currentColumn()
            
            day = self.weekdays[col]
            start_time, end_time = self.time_slots[row]
            time_key = f"{start_time}-{end_time}"
            
            # 检查是否已有课程
            if day in self.schedule_data and time_key in self.schedule_data[day]:
                reply = QMessageBox.question(
                    self, "确认", "该时间段已有课程，是否覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return:
                    return
            
            # 添加课程
            if day not in self.schedule_data:
                self.schedule_data[day] = {}:
                self.schedule_data[day] = {}
            
            self.schedule_data[day][time_key] = {
                'name': self.course_name_edit.text().strip(),
                'classroom': self.classroom_edit.text().strip(),
                'teacher': self.teacher_edit.text().strip(),
                'start_week': self.start_week_spin.value(),
                'end_week': self.end_week_spin.value()
            }
            
            # 更新显示
            self.update_table_display()
            self.clear_form()
            
            QMessageBox.information(self, "成功", "课程添加成功")
            
        except Exception as e:
            self.logger.error(f"添加课程失败: {e}")
            QMessageBox.critical(self, "错误", f"添加课程失败: {e}")
    
    def update_course(self) -> None:
        """更新课程"""
        try:
            if not self.validate_form():
                return:
                return
            
            current_item = self.schedule_table.currentItem()
            if not current_item:
                return:
                return
            
            row = self.schedule_table.currentRow()
            col = self.schedule_table.currentColumn()
            
            day = self.weekdays[col]
            start_time, end_time = self.time_slots[row]
            time_key = f"{start_time}-{end_time}"
            
            # 更新课程
            if day in self.schedule_data and time_key in self.schedule_data[day]:
                self.schedule_data[day][time_key].update({:
                self.schedule_data[day][time_key].update({
                    'name': self.course_name_edit.text().strip(),
                    'classroom': self.classroom_edit.text().strip(),
                    'teacher': self.teacher_edit.text().strip(),
                    'start_week': self.start_week_spin.value(),
                    'end_week': self.end_week_spin.value()
                })
                
                # 更新显示
                self.update_table_display()
                
                QMessageBox.information(self, "成功", "课程更新成功")
            
        except Exception as e:
            self.logger.error(f"更新课程失败: {e}")
            QMessageBox.critical(self, "错误", f"更新课程失败: {e}")
    
    def delete_course(self) -> None:
        """删除课程"""
        try:
            current_item = self.schedule_table.currentItem()
            if not current_item:
                return:
                return
            
            reply = QMessageBox.question(
                self, "确认删除", "确定要删除这门课程吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            
            if reply == QMessageBox.StandardButton.Yes:
                row = self.schedule_table.currentRow()
            
                row = self.schedule_table.currentRow()
                col = self.schedule_table.currentColumn()
                
                day = self.weekdays[col]
                start_time, end_time = self.time_slots[row]
                time_key = f"{start_time}-{end_time}"
                
                # 删除课程
                if day in self.schedule_data and time_key in self.schedule_data[day]:
                    del self.schedule_data[day][time_key]:
                    del self.schedule_data[day][time_key]
                    
                    # 如果该天没有课程了，删除整天
                    if not self.schedule_data[day]:
                        del self.schedule_data[day]:
                        del self.schedule_data[day]
                
                # 更新显示
                self.update_table_display()
                self.clear_form()
                
                QMessageBox.information(self, "成功", "课程删除成功")
            
        except Exception as e:
            self.logger.error(f"删除课程失败: {e}")
            QMessageBox.critical(self, "错误", f"删除课程失败: {e}")
    
    def clear_form(self) -> None:
        """清空表单"""
        try:
            self.course_name_edit.clear()
            self.classroom_edit.clear()
            self.teacher_edit.clear()
            self.start_week_spin.setValue(1)
            self.end_week_spin.setValue(16)
            
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            
        except Exception as e:
            self.logger.error(f"清空表单失败: {e}")
    
    def validate_form(self) -> bool:
        """验证表单"""
        try:
            if not self.course_name_edit.text().strip():
                QMessageBox.warning(self, "警告", "请输入课程名称")
                return False
            
            
            if self.start_week_spin.value() > self.end_week_spin.value():
                QMessageBox.warning(self, "警告", "开始周次不能大于结束周次")
            
                QMessageBox.warning(self, "警告", "开始周次不能大于结束周次")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证表单失败: {e}")
            return False
    
    def save_schedule_data(self) -> None:
        """保存课程表数据"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.app_manager.config_manager.set_config('schedule', self.schedule_data, 'user')
                self.logger.info("课程表数据保存成功")
            
        except Exception as e:
            self.logger.error(f"保存课程表数据失败: {e}")
    
    def apply_changes(self) -> None:
        """应用更改"""
        try:
            self.save_schedule_data()
            self.schedule_updated.emit()
            QMessageBox.information(self, "成功", "课程表保存成功")
            
        except Exception as e:
            self.logger.error(f"应用更改失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
    
    def accept_changes(self) -> None:
        """确定并关闭"""
        try:
            self.apply_changes()
            self.accept()

        except Exception as e:
            self.logger.error(f"确定更改失败: {e}")

    def import_schedule(self) -> None:
        """导入课程表"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json

            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入课程表", "",
                "JSON文件 (*.json);;CSV文件 (*.csv);;所有文件 (*)"
            )


            if file_path:
                if file_path.endswith('.json'):

                if file_path.endswith('.json'):
                    self.import_from_json(file_path)
                elif file_path.endswith('.csv'):
                    self.import_from_csv(file_path)
                else:
                    QMessageBox.warning(self, "警告", "不支持的文件格式")

        except Exception as e:
            self.logger.error(f"导入课程表失败: {e}")
            QMessageBox.critical(self, "错误", f"导入失败: {e}")

    def import_from_json(self, file_path: str) -> None:
        """从JSON文件导入"""
        try:
            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)


            if not isinstance(imported_data, dict):
                raise ValueError("无效的JSON格式")

                raise ValueError("无效的JSON格式")

            # 确认导入
            reply = QMessageBox.question(
                self, "确认导入", "导入将覆盖现有课程表，确定继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )


            if reply == QMessageBox.StandardButton.Yes:
                self.schedule_data = imported_data

                self.schedule_data = imported_data
                self.update_table_display()
                QMessageBox.information(self, "成功", "课程表导入成功")

        except Exception as e:
            raise Exception(f"JSON导入失败: {e}")

    def import_from_csv(self, file_path: str) -> None:
        """从CSV文件导入"""
        try:
            import csv

            new_schedule = {}

            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    day = (row.get('星期', '') or {}).get("strip", lambda: None)()
                    time_slot = (row.get('时间', '') or {}).get("strip", lambda: None)()
                    course_name = (row.get('课程名称', '') or {}).get("strip", lambda: None)()
                    classroom = (row.get('教室', '') or {}).get("strip", lambda: None)()
                    teacher = (row.get('教师', '') or {}).get("strip", lambda: None)()
                    start_week = int(row.get('开始周', 1))
                    end_week = int(row.get('结束周', 16))


                    if day and time_slot and course_name:
                        if day not in new_schedule:

                        if day not in new_schedule:
                            new_schedule[day] = {}

                        new_schedule[day][time_slot] = {
                            'name': course_name,
                            'classroom': classroom,
                            'teacher': teacher,
                            'start_week': start_week,
                            'end_week': end_week
                        }


            if new_schedule:
                # 确认导入:

                # 确认导入
                reply = QMessageBox.question(
                    self, "确认导入", f"将导入 {len(new_schedule)} 天的课程，确定继续吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )


                if reply == QMessageBox.StandardButton.Yes:
                    self.schedule_data = new_schedule

                    self.schedule_data = new_schedule
                    self.update_table_display()
                    QMessageBox.information(self, "成功", "课程表导入成功")
            else:
                QMessageBox.warning(self, "警告", "未找到有效的课程数据")

        except Exception as e:
            raise Exception(f"CSV导入失败: {e}")

    def export_schedule(self) -> None:
        """导出课程表"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json


            if not self.schedule_data:
                QMessageBox.warning(self, "警告", "没有课程数据可导出")

                QMessageBox.warning(self, "警告", "没有课程数据可导出")
                return

            file_path, file_filter = QFileDialog.getSaveFileName(
                self, "导出课程表", "schedule.json",
                "JSON文件 (*.json);;CSV文件 (*.csv);;所有文件 (*)"
            )


            if file_path:
                if "JSON" in file_filter or file_path.endswith('.json'):

                if "JSON" in file_filter or file_path.endswith('.json'):
                    self.export_to_json(file_path)
                elif "CSV" in file_filter or file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                else:
                    # 默认导出为JSON
                    if not file_path.endswith('.json'):
                        file_path += '.json'
                    self.export_to_json(file_path)

        except Exception as e:
            self.logger.error(f"导出课程表失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def export_to_json(self, file_path: str) -> None:
        """导出为JSON文件"""
        try:
            import json

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "成功", f"课程表已导出到: {file_path}")

        except Exception as e:
            raise Exception(f"JSON导出失败: {e}")

    def export_to_csv(self, file_path: str) -> None:
        """导出为CSV文件"""
        try:
            import csv

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow(['星期', '时间', '课程名称', '教室', '教师', '开始周', '结束周'])

                # 写入数据
                for day, day_courses in self.schedule_data.items():
                    for time_slot, course in day_courses.items():
                        writer.writerow([
                            day,
                            time_slot,
                            course.get('name', ''),
                            course.get('classroom', ''),
                            course.get('teacher', ''),
                            course.get('start_week', 1),
                            course.get('end_week', 16)
                        ])

            QMessageBox.information(self, "成功", f"课程表已导出到: {file_path}")

        except Exception as e:
            raise Exception(f"CSV导出失败: {e}")

    def clear_all_courses(self) -> None:
        """清空所有课程"""
        try:
            if not self.schedule_data:
                QMessageBox.information(self, "提示", "课程表已经是空的")
                return

            reply = QMessageBox.question(
                self, "确认清空", "确定要清空所有课程吗？此操作不可撤销！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )


            if reply == QMessageBox.StandardButton.Yes:
                self.schedule_data.clear()

                self.schedule_data.clear()
                self.update_table_display()
                self.clear_form()
                QMessageBox.information(self, "成功", "所有课程已清空")

        except Exception as e:
            self.logger.error(f"清空课程失败: {e}")
            QMessageBox.critical(self, "错误", f"清空失败: {e}")
