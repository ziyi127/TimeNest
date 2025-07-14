#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
课程表设置对话框
用于配置开学日期、学期周数等课程表相关设置
"""

import logging
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QDateEdit, QSpinBox,
    QGroupBox, QMessageBox, QDialogButtonBox
)
from PyQt6.QtGui import QFont

if TYPE_CHECKING:
    from core.app_manager import AppManager


class ScheduleSettingsDialog(QDialog):
    """课程表设置对话框"""
    
    # 信号定义
    settings_saved = pyqtSignal(dict)  # 设置保存信号
    
    def __init__(self, app_manager: Optional['AppManager'] = None, parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.ScheduleSettingsDialog')
        
        self.setup_ui()
        self.load_settings()
        
        self.logger.info("课程表设置对话框初始化完成")
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("课程表设置")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 学期设置组
        semester_group = QGroupBox("学期设置")
        semester_layout = QFormLayout(semester_group)
        
        # 开学日期
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(date.today())
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        semester_layout.addRow("开学日期:", self.start_date_edit)
        
        # 学期总周数
        self.semester_weeks_spin = QSpinBox()
        self.semester_weeks_spin.setRange(10, 30)
        self.semester_weeks_spin.setValue(20)
        self.semester_weeks_spin.setSuffix(" 周")
        semester_layout.addRow("学期总周数:", self.semester_weeks_spin)
        
        # 当前周次
        self.current_week_spin = QSpinBox()
        self.current_week_spin.setRange(1, 30)
        self.current_week_spin.setValue(1)
        self.current_week_spin.setSuffix(" 周")
        semester_layout.addRow("当前周次:", self.current_week_spin)
        
        layout.addWidget(semester_group)
        
        # 周次计算说明
        info_group = QGroupBox("说明")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
• 开学日期：用于计算当前是第几周
• 学期总周数：整个学期的总周数
• 当前周次：手动设置当前周次（会覆盖自动计算）

多周循环功能：
• 全部周次：每周都有课
• 单周：只在单数周（1,3,5...）有课
• 双周：只在双数周（2,4,6...）有课
        """.strip())
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #666; font-size: 11px;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # 自动计算按钮
        calc_layout = QHBoxLayout()
        self.calc_week_button = QPushButton("根据开学日期计算当前周次")
        self.calc_week_button.clicked.connect(self.calculate_current_week)
        calc_layout.addWidget(self.calc_week_button)
        layout.addLayout(calc_layout)
        
        # 按钮组
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_settings(self):
        """加载设置"""
        try:
            if not self.app_manager:
                return
            
            config_manager = self.app_manager.config_manager
            
            # 加载开学日期
            start_date_str = config_manager.get_config('schedule.start_date', '', 'user')
            if start_date_str:
                try:
                    start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    self.start_date_edit.setDate(start_date_obj)
                except ValueError:
                    self.logger.warning(f"无效的开学日期格式: {start_date_str}")
            
            # 加载学期周数
            semester_weeks = config_manager.get_config('schedule.semester_weeks', 20, 'user')
            self.semester_weeks_spin.setValue(semester_weeks)
            
            # 加载当前周次
            current_week = config_manager.get_config('schedule.current_week', 1, 'user')
            self.current_week_spin.setValue(current_week)
            
            self.logger.info("课程表设置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            if not self.app_manager:
                QMessageBox.warning(self, "警告", "无法保存设置：应用管理器不可用")
                return
            
            config_manager = self.app_manager.config_manager
            
            # 保存开学日期
            start_date = self.start_date_edit.date().toPython()
            config_manager.set_config('schedule.start_date', start_date.strftime('%Y-%m-%d'), 'user')
            
            # 保存学期周数
            semester_weeks = self.semester_weeks_spin.value()
            config_manager.set_config('schedule.semester_weeks', semester_weeks, 'user')
            
            # 保存当前周次
            current_week = self.current_week_spin.value()
            config_manager.set_config('schedule.current_week', current_week, 'user')
            
            # 保存配置文件
            config_manager.save_user_config()
            
            # 发出设置保存信号
            settings_data = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'semester_weeks': semester_weeks,
                'current_week': current_week
            }
            self.settings_saved.emit(settings_data)
            
            QMessageBox.information(self, "成功", "设置保存成功")
            self.accept()
            
            self.logger.info("课程表设置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")
    
    def calculate_current_week(self):
        """根据开学日期计算当前周次"""
        try:
            start_date = self.start_date_edit.date().toPython()
            today = date.today()
            
            # 计算天数差
            days_diff = (today - start_date).days
            
            if days_diff < 0:
                QMessageBox.warning(self, "警告", "开学日期不能晚于今天")
                return
            
            # 计算周次（从第1周开始）
            current_week = (days_diff // 7) + 1
            
            # 限制在合理范围内
            max_weeks = self.semester_weeks_spin.value()
            if current_week > max_weeks:
                current_week = max_weeks
                QMessageBox.information(
                    self, "提示", 
                    f"计算出的周次({current_week})超过学期总周数，已设置为第{max_weeks}周"
                )
            
            self.current_week_spin.setValue(current_week)
            
            QMessageBox.information(
                self, "计算完成", 
                f"根据开学日期 {start_date.strftime('%Y-%m-%d')}，\n当前是第 {current_week} 周"
            )
            
        except Exception as e:
            self.logger.error(f"计算当前周次失败: {e}")
            QMessageBox.critical(self, "错误", f"计算失败: {e}")
    
    def get_current_week_from_date(self, start_date_str: str) -> int:
        """根据开学日期字符串计算当前周次"""
        try:
            if not start_date_str:
                return 1
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            today = date.today()
            
            days_diff = (today - start_date).days
            if days_diff < 0:
                return 1
            
            return (days_diff // 7) + 1
            
        except Exception as e:
            self.logger.error(f"计算当前周次失败: {e}")
            return 1
