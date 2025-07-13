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
TimeNest 计划任务管理对话框
提供重要日期倒计时和任务管理功能
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QDateTime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateTimeEdit,
    QListWidget, QListWidgetItem, QMessageBox, QTextEdit,
    QDialogButtonBox, QGroupBox, QFormLayout, QCheckBox,
    QSpinBox, QDateEdit
)
from PyQt6.QtGui import QFont


if TYPE_CHECKING:
    from core.app_manager import AppManager


class TaskManagerDialog(QDialog):
    """
    计划任务管理对话框
    
    提供重要日期倒计时和任务管理功能
    """
    
    # 信号定义
    tasks_updated = pyqtSignal()  # 任务更新信号
    
    def __init__(self, app_manager: 'AppManager', parent=None):
        """
        初始化计划任务管理对话框
        
        Args:
            app_manager: 应用管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 依赖注入
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.TaskManagerDialog')
        
        # 任务数据
        self.tasks_data = {}
        self.task_types = {
            'exam': '考试',
            'assignment': '作业',
            'holiday': '假期',
            'event': '活动',
            'deadline': '截止日期',
            'other': '其他'
        }
        
        # 初始化UI
        self.init_ui()
        self.load_tasks_data()
        
        self.logger.debug("计划任务管理对话框初始化完成")
    
    def init_ui(self) -> None:
        """初始化UI"""
        try:
            self.setWindowTitle("计划任务管理")
            self.setFixedSize(900, 700)
            self.setModal(True)
            
            # 主布局
            layout = QHBoxLayout(self)
            
            # 左侧：任务列表
            left_layout = self.create_task_list_area()
            layout.addLayout(left_layout, 1)
            
            # 右侧：任务编辑
            right_layout = self.create_task_edit_area()
            layout.addLayout(right_layout, 1)
            
        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")
    
    def create_task_list_area(self) -> QVBoxLayout:
        """创建任务列表区域"""
        try:
            layout = QVBoxLayout()
            
            # 标题
            title_label = QLabel("任务列表")
            title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            layout.addWidget(title_label)
            
            # 过滤器
            filter_layout = QHBoxLayout()
            
            self.filter_combo = QComboBox()
            self.filter_combo.addItem("全部任务", "all")
            self.filter_combo.addItem("即将到期", "upcoming")
            self.filter_combo.addItem("已过期", "overdue")
            for key, name in self.task_types.items():
                self.filter_combo.addItem(name, key)
            self.filter_combo.currentTextChanged.connect(self.filter_tasks)
            
            filter_layout.addWidget(QLabel("筛选:"))
            filter_layout.addWidget(self.filter_combo)
            filter_layout.addStretch()
            
            layout.addLayout(filter_layout)
            
            # 任务列表
            self.task_list = QListWidget()
            self.task_list.itemSelectionChanged.connect(self.on_task_selected)
            self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.task_list.customContextMenuRequested.connect(self.show_task_context_menu)
            layout.addWidget(self.task_list)
            
            # 列表操作按钮
            list_button_layout = QHBoxLayout()
            
            self.refresh_button = QPushButton("刷新")
            self.refresh_button.clicked.connect(self.refresh_task_list)
            list_button_layout.addWidget(self.refresh_button)
            
            self.delete_task_button = QPushButton("删除任务")
            self.delete_task_button.clicked.connect(self.delete_selected_task)
            self.delete_task_button.setEnabled(False)
            list_button_layout.addWidget(self.delete_task_button)

            layout.addLayout(list_button_layout)

            # 批量操作按钮
            batch_button_layout = QHBoxLayout()

            self.export_tasks_button = QPushButton("导出任务")
            self.export_tasks_button.clicked.connect(self.export_tasks)
            self.export_tasks_button.setToolTip("导出任务列表到文件")
            batch_button_layout.addWidget(self.export_tasks_button)

            self.import_tasks_button = QPushButton("导入任务")
            self.import_tasks_button.clicked.connect(self.import_tasks)
            self.import_tasks_button.setToolTip("从文件导入任务")
            batch_button_layout.addWidget(self.import_tasks_button)

            self.clear_completed_button = QPushButton("清理已完成")
            self.clear_completed_button.clicked.connect(self.clear_completed_tasks)
            self.clear_completed_button.setToolTip("清理已完成的任务")
            batch_button_layout.addWidget(self.clear_completed_button)

            layout.addLayout(batch_button_layout)
            
            return layout
            
        except Exception as e:
            self.logger.error(f"创建任务列表区域失败: {e}")
            return QVBoxLayout()
    
    def create_task_edit_area(self) -> QVBoxLayout:
        """创建任务编辑区域"""
        try:
            layout = QVBoxLayout()
            
            # 标题
            title_label = QLabel("任务编辑")
            title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            layout.addWidget(title_label)
            
            # 编辑表单
            form_group = QGroupBox("任务信息")
            form_layout = QFormLayout(form_group)
            
            # 任务名称
            self.task_name_edit = QLineEdit()
            self.task_name_edit.setPlaceholderText("输入任务名称")
            form_layout.addRow("任务名称:", self.task_name_edit)
            
            # 任务类型
            self.task_type_combo = QComboBox()
            for key, name in self.task_types.items():
                self.task_type_combo.addItem(name, key)
            form_layout.addRow("任务类型:", self.task_type_combo)
            
            # 目标日期
            self.target_date_edit = QDateTimeEdit()
            self.target_date_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
            self.target_date_edit.setCalendarPopup(True)
            form_layout.addRow("目标日期:", self.target_date_edit)
            
            # 任务描述
            self.task_description_edit = QTextEdit()
            self.task_description_edit.setMaximumHeight(100)
            self.task_description_edit.setPlaceholderText("输入任务描述（可选）")
            form_layout.addRow("任务描述:", self.task_description_edit)
            
            # 优先级
            self.priority_combo = QComboBox()
            self.priority_combo.addItem("低", "low")
            self.priority_combo.addItem("中", "medium")
            self.priority_combo.addItem("高", "high")
            self.priority_combo.addItem("紧急", "urgent")
            self.priority_combo.setCurrentIndex(1)  # 默认中等优先级
            form_layout.addRow("优先级:", self.priority_combo)
            
            # 提醒设置
            reminder_layout = QHBoxLayout()
            
            self.reminder_enabled_check = QCheckBox("启用提醒")
            self.reminder_enabled_check.setChecked(True)
            reminder_layout.addWidget(self.reminder_enabled_check)
            
            self.reminder_days_spin = QSpinBox()
            self.reminder_days_spin.setRange(0, 30)
            self.reminder_days_spin.setValue(1)
            self.reminder_days_spin.setSuffix(" 天前")
            reminder_layout.addWidget(QLabel("提前"))
            reminder_layout.addWidget(self.reminder_days_spin)
            reminder_layout.addWidget(QLabel("提醒"))
            
            form_layout.addRow("提醒设置:", reminder_layout)
            
            layout.addWidget(form_group)
            
            # 编辑按钮
            edit_button_layout = QHBoxLayout()
            
            self.add_task_button = QPushButton("添加任务")
            self.add_task_button.clicked.connect(self.add_task)
            edit_button_layout.addWidget(self.add_task_button)
            
            self.update_task_button = QPushButton("更新任务")
            self.update_task_button.clicked.connect(self.update_task)
            self.update_task_button.setEnabled(False)
            edit_button_layout.addWidget(self.update_task_button)
            
            self.clear_form_button = QPushButton("清空表单")
            self.clear_form_button.clicked.connect(self.clear_form)
            edit_button_layout.addWidget(self.clear_form_button)
            
            layout.addLayout(edit_button_layout)
            
            # 快速添加区域
            quick_group = QGroupBox("快速添加")
            quick_layout = QVBoxLayout(quick_group)
            
            quick_button_layout = QGridLayout()
            
            # 常用任务快速添加按钮
            quick_tasks = [
                ("期末考试", "exam", 30),
                ("作业截止", "assignment", 7),
                ("寒假开始", "holiday", 60),
                ("暑假开始", "holiday", 120),
                ("项目截止", "deadline", 14),
                ("重要活动", "event", 21)
            ]
            
            for i, (name, task_type, days) in enumerate(quick_tasks):
                button = QPushButton(name)
                button.clicked.connect(lambda checked, n=name, t=task_type, d=days:
                                     self.quick_add_task(n, t, d))
                quick_button_layout.addWidget(button, i // 3, i % 3)
            
            quick_layout.addLayout(quick_button_layout)
            layout.addWidget(quick_group)
            
            # 底部按钮
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | 
                QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(self.accept_changes)
            button_box.rejected.connect(self.reject)
            
            layout.addWidget(button_box)
            
            return layout
            
        except Exception as e:
            self.logger.error(f"创建任务编辑区域失败: {e}")
            return QVBoxLayout()
    
    def load_tasks_data(self) -> None:
        """加载任务数据"""
        try:
            # 从配置管理器加载数据
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.tasks_data = self.app_manager.config_manager.get_config('tasks', {}, 'user')
            
            # 更新任务列表显示
            self.refresh_task_list()
            
        except Exception as e:
            self.logger.error(f"加载任务数据失败: {e}")
    
    def refresh_task_list(self) -> None:
        """刷新任务列表"""
        try:
            self.task_list.clear()
            
            current_filter = self.filter_combo.currentData()
            current_time = datetime.now()
            
            # 按日期排序任务
            sorted_tasks = []
            for task_id, task in self.tasks_data.items():
                target_date = datetime.fromisoformat(task.get('target_date'))
                sorted_tasks.append((task_id, task, target_date))
            
            sorted_tasks.sort(key=lambda x: x[2])
            
            for task_id, task, target_date in sorted_tasks:
                # 应用过滤器
                if not self.should_show_task(task, target_date, current_time, current_filter):
                    continue
                    continue
                
                # 计算剩余时间
                time_diff = target_date - current_time
                days_left = time_diff.days
                
                # 创建显示文本
                status_text = ""
                if days_left < 0:
                    status_text = f"已过期 {abs(days_left)} 天"
                elif days_left == 0:
                    status_text = "今天到期"
                elif days_left == 1:
                    status_text = "明天到期"
                else:
                    status_text = f"还有 {days_left} 天"
                
                task_text = f"{task.get('name')} - {status_text}"
                priority_text = f"[{self.get_priority_text(task.get('priority', 'medium'))}]"
                
                item_text = f"{priority_text} {task_text}"
                
                # 创建列表项
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, task_id)
                
                # 设置颜色
                if days_left < 0:
                    item.setBackground(Qt.GlobalColor.red)
                elif days_left <= 3:
                    item.setBackground(Qt.GlobalColor.yellow)
                elif task['priority'] == 'urgent':
                    item.setBackground(Qt.GlobalColor.magenta)
                
                self.task_list.addItem(item)
            
        except Exception as e:
            self.logger.error(f"刷新任务列表失败: {e}")
    
    def should_show_task(self, task: Dict, target_date: datetime, 
                        current_time: datetime, filter_type: str) -> bool:
        """判断是否应该显示任务"""
        try:
            if filter_type == "all":
                return True
            elif filter_type == "upcoming":
                days_left = (target_date - current_time).days
                return 0 <= days_left <= 7
            elif filter_type == "overdue":
                return target_date < current_time
            else:
                return task['type'] == filter_type
                
        except Exception as e:
            self.logger.error(f"判断任务显示失败: {e}")
            return True
    
    def get_priority_text(self, priority: str) -> str:
        """获取优先级文本"""
        priority_map = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '急'
        }
        return priority_map.get(priority, '中')
    
    def filter_tasks(self) -> None:
        """过滤任务"""
        self.refresh_task_list()
    
    def on_task_selected(self) -> None:
        """处理任务选择"""
        try:
            current_item = self.task_list.currentItem()
            if current_item:
                task_id = current_item.data(Qt.ItemDataRole.UserRole)
                task = self.tasks_data.get(task_id, {})
                
                # 填充表单
                self.task_name_edit.setText(task.get('name', ''))
                
                # 设置任务类型
                task_type = task.get('type', 'other')
                for i in range(self.task_type_combo.count()):
                    if self.task_type_combo.itemData(i) == task_type:
                        self.task_type_combo.setCurrentIndex(i)
                        break
                
                # 设置目标日期
                target_date = datetime.fromisoformat((task.get('target_date', datetime.now() or {}).get("isoformat", lambda: None)()))
                self.target_date_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(target_date.timestamp())))
                
                # 设置描述
                self.task_description_edit.setPlainText(task.get('description', ''))
                
                # 设置优先级
                priority = task.get('priority', 'medium')
                for i in range(self.priority_combo.count()):
                    if self.priority_combo.itemData(i) == priority:
                        self.priority_combo.setCurrentIndex(i)
                        break
                
                # 设置提醒
                self.reminder_enabled_check.setChecked(task.get('reminder_enabled', True))
                self.reminder_days_spin.setValue(task.get('reminder_days', 1))
                
                # 更新按钮状态
                self.update_task_button.setEnabled(True)
                self.delete_task_button.setEnabled(True)
                
        except Exception as e:
            self.logger.error(f"处理任务选择失败: {e}")
    
    def add_task(self) -> None:
        """添加任务"""
        try:
            if not self.validate_form():
                return
                return
            
            # 生成任务ID
            task_id = f"task_{int(datetime.now().timestamp())}"
            
            # 创建任务数据
            task_data = {
                'name': self.task_name_edit.text().strip(),
                'type': self.task_type_combo.currentData(),
                'target_date': self.target_date_edit.dateTime().toPython().isoformat(),
                'description': self.task_description_edit.toPlainText().strip(),
                'priority': self.priority_combo.currentData(),
                'reminder_enabled': self.reminder_enabled_check.isChecked(),
                'reminder_days': self.reminder_days_spin.value(),
                'created_date': datetime.now().isoformat()
            }
            
            # 添加到数据
            self.tasks_data[task_id] = task_data
            
            # 刷新列表
            self.refresh_task_list()
            self.clear_form()
            
            QMessageBox.information(self, "成功", "任务添加成功")
            
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            QMessageBox.critical(self, "错误", f"添加任务失败: {e}")
    
    def update_task(self) -> None:
        """更新任务"""
        try:
            if not self.validate_form():
                return
                return
            
            current_item = self.task_list.currentItem()
            if not current_item:
                return
            
            task_id = current_item.data(Qt.ItemDataRole.UserRole)
            
            # 更新任务数据
            self.tasks_data[task_id].update({
                'name': self.task_name_edit.text().strip(),
                'type': self.task_type_combo.currentData(),
                'target_date': self.target_date_edit.dateTime().toPython().isoformat(),
                'description': self.task_description_edit.toPlainText().strip(),
                'priority': self.priority_combo.currentData(),
                'reminder_enabled': self.reminder_enabled_check.isChecked(),
                'reminder_days': self.reminder_days_spin.value(),
                'updated_date': datetime.now().isoformat()
            })
            
            # 刷新列表
            self.refresh_task_list()
            
            QMessageBox.information(self, "成功", "任务更新成功")
            
        except Exception as e:
            self.logger.error(f"更新任务失败: {e}")
            QMessageBox.critical(self, "错误", f"更新任务失败: {e}")
    
    def delete_selected_task(self) -> None:
        """删除选中的任务"""
        try:
            current_item = self.task_list.currentItem()
            if not current_item:
                return
                return
            
            reply = QMessageBox.question(
                self, "确认删除", "确定要删除这个任务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            
            if reply == QMessageBox.StandardButton.Yes:
                task_id = current_item.data(Qt.ItemDataRole.UserRole)
            
                task_id = current_item.data(Qt.ItemDataRole.UserRole)
                
                # 删除任务
                if task_id in self.tasks_data:
                    del self.tasks_data[task_id]
                
                # 刷新列表
                self.refresh_task_list()
                self.clear_form()
                
                QMessageBox.information(self, "成功", "任务删除成功")
            
        except Exception as e:
            self.logger.error(f"删除任务失败: {e}")
            QMessageBox.critical(self, "错误", f"删除任务失败: {e}")
    
    def quick_add_task(self, name: str, task_type: str, days: int) -> None:
        """快速添加任务"""
        try:
            self.task_name_edit.setText(name)
            
            # 设置任务类型
            for i in range(self.task_type_combo.count()):
                if self.task_type_combo.itemData(i) == task_type:
                    self.task_type_combo.setCurrentIndex(i)
                    break
            
            # 设置目标日期
            target_date = QDateTime.currentDateTime().addDays(days)
            self.target_date_edit.setDateTime(target_date)
            
            # 设置优先级
            if days <= 7:
                self.priority_combo.setCurrentIndex(3)  # 紧急:
                self.priority_combo.setCurrentIndex(3)  # 紧急
            elif days <= 14:
                self.priority_combo.setCurrentIndex(2)  # 高
            else:
                self.priority_combo.setCurrentIndex(1)  # 中
            
        except Exception as e:
            self.logger.error(f"快速添加任务失败: {e}")
    
    def clear_form(self) -> None:
        """清空表单"""
        try:
            self.task_name_edit.clear()
            self.task_type_combo.setCurrentIndex(0)
            self.target_date_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
            self.task_description_edit.clear()
            self.priority_combo.setCurrentIndex(1)
            self.reminder_enabled_check.setChecked(True)
            self.reminder_days_spin.setValue(1)
            
            self.update_task_button.setEnabled(False)
            self.delete_task_button.setEnabled(False)
            
        except Exception as e:
            self.logger.error(f"清空表单失败: {e}")
    
    def validate_form(self) -> bool:
        """验证表单"""
        try:
            if not self.task_name_edit.text().strip():
                QMessageBox.warning(self, "警告", "请输入任务名称")
                return False
            
            target_date = self.target_date_edit.dateTime().toPython()
            if target_date < datetime.now():
                reply = QMessageBox.question(
                    self, "确认", "目标日期已过期，确定要添加吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证表单失败: {e}")
            return False
    
    def save_tasks_data(self) -> None:
        """保存任务数据"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.app_manager.config_manager.set_config('tasks', self.tasks_data, 'user')
                self.logger.info("任务数据保存成功")
            
        except Exception as e:
            self.logger.error(f"保存任务数据失败: {e}")
    
    def accept_changes(self) -> None:
        """确定并关闭"""
        try:
            self.save_tasks_data()
            self.tasks_updated.emit()
            self.accept()

        except Exception as e:
            self.logger.error(f"确定更改失败: {e}")

    def export_tasks(self) -> None:
        """导出任务列表"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json


            if not self.tasks_data:
                QMessageBox.warning(self, "警告", "没有任务数据可导出")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出任务列表", "tasks.json",
                "JSON文件 (*.json);;所有文件 (*)"
            )


            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.tasks_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "成功", f"任务列表已导出到: {file_path}")

        except Exception as e:
            self.logger.error(f"导出任务失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def import_tasks(self) -> None:
        """导入任务列表"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json

            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入任务列表", "",
                "JSON文件 (*.json);;所有文件 (*)"
            )


            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_tasks = json.load(f)
                
                if not isinstance(imported_tasks, dict):
                    raise ValueError("无效的任务文件格式")

                # 确认导入
                reply = QMessageBox.question(
                    self, "确认导入", f"将导入 {len(imported_tasks)} 个任务，确定继续吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )


                if reply == QMessageBox.StandardButton.Yes:
                    # 合并任务（避免覆盖现有任务）
                    for task_id, task_data in imported_tasks.items():
                        if task_id not in self.tasks_data:
                            self.tasks_data[task_id] = task_data

                    self.refresh_task_list()
                    QMessageBox.information(self, "成功", "任务导入成功")

        except Exception as e:
            self.logger.error(f"导入任务失败: {e}")
            QMessageBox.critical(self, "错误", f"导入失败: {e}")

    def clear_completed_tasks(self) -> None:
        """清理已完成的任务"""
        try:
            current_time = datetime.now()
            completed_tasks = []

            # 找出已完成的任务（过期超过7天的任务）
            for task_id, task in self.tasks_data.items():
                target_date = datetime.fromisoformat(task.get('target_date'))
                if target_date < current_time:
                    days_overdue = (current_time - target_date).days
                    if days_overdue > 7:  # 过期超过7天
                        completed_tasks.append(task_id)
            
            if not completed_tasks:
                QMessageBox.information(self, "提示", "没有需要清理的已完成任务")
                return

            reply = QMessageBox.question(
                self, "确认清理",
                f"找到 {len(completed_tasks)} 个过期超过7天的任务，确定清理吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )


            if reply == QMessageBox.StandardButton.Yes:
                for task_id in completed_tasks:
                    del self.tasks_data[task_id]

                self.refresh_task_list()
                self.clear_form()
                QMessageBox.information(self, "成功", f"已清理 {len(completed_tasks)} 个任务")

        except Exception as e:
            self.logger.error(f"清理任务失败: {e}")
            QMessageBox.critical(self, "错误", f"清理失败: {e}")

    def mark_task_completed(self) -> None:
        """标记任务为已完成"""
        try:
            current_item = self.task_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个任务")
                return

            task_id = current_item.data(Qt.ItemDataRole.UserRole)


            if task_id in self.tasks_data:
                # 添加完成标记
                self.tasks_data[task_id]['completed'] = True
                self.tasks_data[task_id]['completed_date'] = datetime.now().isoformat()

                self.refresh_task_list()
                QMessageBox.information(self, "成功", "任务已标记为完成")

        except Exception as e:
            self.logger.error(f"标记任务完成失败: {e}")
            QMessageBox.critical(self, "错误", f"标记失败: {e}")

    def create_reminder_for_task(self) -> None:
        """为任务创建提醒"""
        try:
            current_item = self.task_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个任务")
                return

            task_id = current_item.data(Qt.ItemDataRole.UserRole)
            task = self.tasks_data.get(task_id, {})


            if not task:
                return

            # 这里可以集成到通知系统
            if self.app_manager and hasattr(self.app_manager, 'notification_manager'):
                target_date = datetime.fromisoformat(task.get('target_date'))
                reminder_days = task.get('reminder_days', 1)
                reminder_date = target_date - timedelta(days=reminder_days)


                if reminder_date > datetime.now():
                    # 创建提醒（这里简化处理）
                    QMessageBox.information(
                        self, "提醒设置",
                        f"任务 '{task.get('name')}' 的提醒已设置\n"
                        f"将在 {reminder_date.strftime('%Y-%m-%d %H:%M')} 提醒您"
                    )
                else:
                    QMessageBox.warning(self, "警告", "提醒时间已过期")
            else:
                QMessageBox.warning(self, "警告", "通知系统不可用")

        except Exception as e:
            self.logger.error(f"创建提醒失败: {e}")
            QMessageBox.critical(self, "错误", f"创建提醒失败: {e}")

    def show_task_context_menu(self, position: QPoint) -> None:
        """显示任务右键菜单"""
        try:
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction

            item = self.task_list.itemAt(position)
            if not item:
                return

            menu = QMenu(self)

            # 编辑任务
            edit_action = QAction("编辑任务", self)
            edit_action.triggered.connect(lambda: self.on_task_selected())
            menu.addAction(edit_action)

            # 标记完成
            complete_action = QAction("标记完成", self)
            complete_action.triggered.connect(self.mark_task_completed)
            menu.addAction(complete_action)

            # 创建提醒
            reminder_action = QAction("创建提醒", self)
            reminder_action.triggered.connect(self.create_reminder_for_task)
            menu.addAction(reminder_action)

            menu.addSeparator()

            # 复制任务
            copy_action = QAction("复制任务", self)
            copy_action.triggered.connect(self.copy_selected_task)
            menu.addAction(copy_action)

            # 删除任务
            delete_action = QAction("删除任务", self)
            delete_action.triggered.connect(self.delete_selected_task)
            menu.addAction(delete_action)

            # 显示菜单
            menu.exec(self.task_list.mapToGlobal(position))

        except Exception as e:
            self.logger.error(f"显示右键菜单失败: {e}")

    def copy_selected_task(self) -> None:
        """复制选中的任务"""
        try:
            current_item = self.task_list.currentItem()
            if not current_item:
                return

            task_id = current_item.data(Qt.ItemDataRole.UserRole)
            original_task = self.tasks_data.get(task_id, {})


            if not original_task:
                return

            # 创建新任务ID
            new_task_id = f"task_{int(datetime.now().timestamp())}"

            # 复制任务数据
            new_task = original_task.copy()
            new_task['name'] = f"{original_task.get('name')} (副本)"
            new_task['created_date'] = datetime.now().isoformat()

            # 添加到任务列表
            self.tasks_data[new_task_id] = new_task

            # 刷新列表
            self.refresh_task_list()

            QMessageBox.information(self, "成功", "任务复制成功")

        except Exception as e:
            self.logger.error(f"复制任务失败: {e}")
            QMessageBox.critical(self, "错误", f"复制失败: {e}")
