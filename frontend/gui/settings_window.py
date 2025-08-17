#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
设置窗口组件
"""

import sys
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QWidget, QCheckBox, QSlider, QLabel,
    QComboBox, QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal


class SettingsWindow(QDialog):
    """设置窗口类"""
    
    # 设置保存信号
    settings_saved = Signal()
    
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.setWindowTitle("TimeNest 设置")
        self.setGeometry(100, 100, 500, 400)
        self.initUI()

    def initUI(self):
        # 创建主布局
        layout = QVBoxLayout(self)

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 悬浮窗设置标签页
        self.floating_window_tab = QWidget()
        self.tab_widget.addTab(self.floating_window_tab, "悬浮窗设置")
        self.init_floating_window_tab()

        # 系统设置标签页
        self.system_tab = QWidget()
        self.tab_widget.addTab(self.system_tab, "系统设置")
        self.init_system_tab()

        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def init_floating_window_tab(self):
        """初始化悬浮窗设置标签页"""
        layout = QVBoxLayout(self.floating_window_tab)

        # 透明度设置
        transparency_group = QGroupBox("透明度设置")
        transparency_layout = QFormLayout(transparency_group)
        
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setMinimum(10)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(self.app.settings.get("floating_window", {}).get("transparency", 80))
        self.transparency_slider.valueChanged.connect(self.update_transparency_label)
        
        self.transparency_label = QLabel(f"{self.transparency_slider.value()}%")
        
        transparency_layout.addRow("透明度:", self.transparency_slider)
        transparency_layout.addRow("", self.transparency_label)
        
        layout.addWidget(transparency_group)

        # 自动隐藏设置
        auto_hide_group = QGroupBox("自动隐藏设置")
        auto_hide_layout = QFormLayout(auto_hide_group)
        
        self.auto_hide_checkbox = QCheckBox("启用自动隐藏")
        self.auto_hide_checkbox.setChecked(not self.app.settings.get("floating_window", {}).get("hide_tray_menu", False))
        
        self.auto_hide_threshold_slider = QSlider(Qt.Horizontal)
        self.auto_hide_threshold_slider.setMinimum(1)
        self.auto_hide_threshold_slider.setMaximum(100)
        self.auto_hide_threshold_slider.setValue(self.app.settings.get("floating_window", {}).get("auto_hide_threshold", 50))
        self.auto_hide_threshold_slider.valueChanged.connect(self.update_auto_hide_threshold_label)
        
        self.auto_hide_threshold_label = QLabel(f"{self.auto_hide_threshold_slider.value()} 秒")
        
        auto_hide_layout.addRow(self.auto_hide_checkbox)
        auto_hide_layout.addRow("自动隐藏延迟:", self.auto_hide_threshold_slider)
        auto_hide_layout.addRow("", self.auto_hide_threshold_label)
        
        layout.addWidget(auto_hide_group)

        # 位置设置
        position_group = QGroupBox("位置设置")
        position_layout = QFormLayout(position_group)
        
        self.remember_position_checkbox = QCheckBox("记住窗口位置")
        self.remember_position_checkbox.setChecked(self.app.settings.get("floating_window", {}).get("remember_position", True))
        
        self.snap_to_edge_checkbox = QCheckBox("边缘吸附")
        self.snap_to_edge_checkbox.setChecked(self.app.settings.get("floating_window", {}).get("snap_to_edge", False))
        
        self.snap_priority_combo = QComboBox()
        self.snap_priority_combo.addItems(["右侧 > 顶部 > 左侧", "顶部 > 右侧 > 左侧", "左侧 > 顶部 > 右侧"])
        snap_priority = self.app.settings.get("floating_window", {}).get("snap_priority", "右侧 > 顶部 > 左侧")
        index = self.snap_priority_combo.findText(snap_priority)
        if index >= 0:
            self.snap_priority_combo.setCurrentIndex(index)
        
        position_layout.addRow(self.remember_position_checkbox)
        position_layout.addRow(self.snap_to_edge_checkbox)
        position_layout.addRow("吸附优先级:", self.snap_priority_combo)
        
        layout.addWidget(position_group)

        # 天气显示设置
        weather_group = QGroupBox("天气显示设置")
        weather_layout = QFormLayout(weather_group)
        
        self.weather_display_combo = QComboBox()
        self.weather_display_combo.addItems(["仅显示温度", "温度 + 天气描述", "隐藏天气"])
        weather_display = self.app.settings.get("floating_window", {}).get("weather_display", "温度 + 天气描述")
        index = self.weather_display_combo.findText(weather_display)
        if index >= 0:
            self.weather_display_combo.setCurrentIndex(index)
        
        weather_layout.addRow("天气显示方式:", self.weather_display_combo)
        
        layout.addWidget(weather_group)

        # 临时课程样式设置
        temp_course_group = QGroupBox("临时课程样式设置")
        temp_course_layout = QFormLayout(temp_course_group)
        
        self.temp_course_style_combo = QComboBox()
        self.temp_course_style_combo.addItems(["临时调课标红边框", "临时调课闪烁提醒", "临时调课标红边框+闪烁提醒"])
        temp_course_style = self.app.settings.get("floating_window", {}).get("temp_course_style", "临时调课标红边框")
        index = self.temp_course_style_combo.findText(temp_course_style)
        if index >= 0:
            self.temp_course_style_combo.setCurrentIndex(index)
        
        temp_course_layout.addRow("临时课程样式:", self.temp_course_style_combo)
        
        layout.addWidget(temp_course_group)

        layout.addStretch()

    def init_system_tab(self):
        """初始化系统设置标签页"""
        layout = QVBoxLayout(self.system_tab)

        # 数据设置
        data_group = QGroupBox("数据设置")
        data_layout = QFormLayout(data_group)
        
        self.data_dir_label = QLabel(self.app.data_dir)
        data_layout.addRow("数据目录:", self.data_dir_label)
        
        layout.addWidget(data_group)

        # 更新间隔设置
        update_group = QGroupBox("更新设置")
        update_layout = QFormLayout(update_group)
        
        self.update_interval_slider = QSlider(Qt.Horizontal)
        self.update_interval_slider.setMinimum(100)
        self.update_interval_slider.setMaximum(10000)
        self.update_interval_slider.setValue(self.app.settings.get("update_interval", 1000))
        self.update_interval_slider.valueChanged.connect(self.update_update_interval_label)
        
        self.update_interval_label = QLabel(f"{self.update_interval_slider.value()} 毫秒")
        
        update_layout.addRow("数据更新间隔:", self.update_interval_slider)
        update_layout.addRow("", self.update_interval_label)
        
        layout.addWidget(update_group)

        layout.addStretch()

    def update_transparency_label(self, value):
        """更新透明度标签"""
        self.transparency_label.setText(f"{value}%")

    def update_auto_hide_threshold_label(self, value):
        """更新自动隐藏阈值标签"""
        self.auto_hide_threshold_label.setText(f"{value} 秒")

    def update_update_interval_label(self, value):
        """更新更新间隔标签"""
        self.update_interval_label.setText(f"{value} 毫秒")

    def save_settings(self):
        """保存设置"""
        try:
            # 收集变更的设置
            changed_settings = {}
            
            # 检查悬浮窗设置是否有变更
            current_floating_settings = self.app.settings.get("floating_window", {})
            new_floating_settings = {
                "transparency": self.transparency_slider.value(),
                "hide_tray_menu": not self.auto_hide_checkbox.isChecked(),
                "auto_hide_threshold": self.auto_hide_threshold_slider.value(),
                "remember_position": self.remember_position_checkbox.isChecked(),
                "snap_to_edge": self.snap_to_edge_checkbox.isChecked(),
                "snap_priority": self.snap_priority_combo.currentText(),
                "weather_display": self.weather_display_combo.currentText(),
                "temp_course_style": self.temp_course_style_combo.currentText()
            }
            
            # 只有当设置发生变化时才添加到变更字典中
            if new_floating_settings != current_floating_settings:
                changed_settings["floating_window"] = new_floating_settings
            
            # 检查更新间隔是否有变更
            new_update_interval = self.update_interval_slider.value()
            if new_update_interval != self.app.settings.get("update_interval", 1000):
                changed_settings["update_interval"] = new_update_interval
            
            # 如果有变更的设置，则保存
            if changed_settings:
                # 更新应用设置
                for key, value in changed_settings.items():
                    self.app.settings[key] = value
                
                # 保存设置
                self.app.save_data()
                
                # 发出设置保存完成信号
                self.settings_saved.emit()
                
                # 显示成功消息
                QMessageBox.information(self, "成功", "设置已保存")
            else:
                # 没有变更，直接显示消息
                QMessageBox.information(self, "提示", "没有检测到设置变更")
            
            # 关闭窗口
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时出错: {str(e)}")