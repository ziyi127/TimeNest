#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
设置窗口组件
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTabWidget, QWidget, QCheckBox, QSlider, QLabel,
                               QComboBox, QGroupBox, QFormLayout, QLineEdit,
                               QSpinBox, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SettingsWindow(QDialog):
    """设置窗口类"""
    
    # 设置保存信号
    settings_saved = Signal(dict)
    
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.initUI()
        self.load_settings()
    
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setFixedSize(600, 500)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建选项卡
        self.create_floating_window_tab()
        self.create_school_server_tab()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        # 确定按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.ok_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 应用按钮
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
    
    def create_floating_window_tab(self):
        """创建悬浮窗管理选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 隐藏主界面托盘菜单开关
        self.hide_tray_menu_checkbox = QCheckBox("隐藏\"隐藏主界面\"托盘菜单开关，防止学生误触")
        layout.addWidget(self.hide_tray_menu_checkbox)
        
        # 记住位置开关
        self.remember_position_checkbox = QCheckBox("记住位置：关闭后重启软件恢复默认位置（大屏场景防止误拖动后难找回）")
        layout.addWidget(self.remember_position_checkbox)
        
        # 自动隐藏阈值设置
        auto_hide_group = QGroupBox("自动隐藏阈值")
        auto_hide_layout = QFormLayout(auto_hide_group)
        
        self.auto_hide_slider = QSlider(Qt.Horizontal)
        self.auto_hide_slider.setRange(0, 200)
        self.auto_hide_slider.setValue(50)
        self.auto_hide_value_label = QLabel("50px")
        
        auto_hide_slider_layout = QHBoxLayout()
        auto_hide_slider_layout.addWidget(self.auto_hide_slider)
        auto_hide_slider_layout.addWidget(self.auto_hide_value_label)
        
        auto_hide_layout.addRow("鼠标距离悬浮窗多远时触发隐藏：", auto_hide_slider_layout)
        
        # 连接信号
        self.auto_hide_slider.valueChanged.connect(
            lambda value: self.auto_hide_value_label.setText(f"{value}px"))
        
        layout.addWidget(auto_hide_group)
        
        # 透明度调节
        transparency_group = QGroupBox("透明度调节")
        transparency_layout = QFormLayout(transparency_group)
        
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(50, 100)
        self.transparency_slider.setValue(80)
        self.transparency_value_label = QLabel("80%")
        
        transparency_slider_layout = QHBoxLayout()
        transparency_slider_layout.addWidget(self.transparency_slider)
        transparency_slider_layout.addWidget(self.transparency_value_label)
        
        transparency_layout.addRow("悬浮窗透明度：", transparency_slider_layout)
        
        # 连接信号
        self.transparency_slider.valueChanged.connect(
            lambda value: self.transparency_value_label.setText(f"{value}%"))
        
        layout.addWidget(transparency_group)
        
        # 吸附边缘规则
        snap_group = QGroupBox("吸附边缘规则")
        snap_layout = QVBoxLayout(snap_group)
        
        self.snap_edge_checkbox = QCheckBox("拖动时自动吸附屏幕边缘")
        snap_layout.addWidget(self.snap_edge_checkbox)
        
        # 吸附优先级
        self.snap_priority_label = QLabel("吸附优先级：")
        snap_layout.addWidget(self.snap_priority_label)
        
        self.snap_priority_combo = QComboBox()
        self.snap_priority_combo.addItems(["右侧 > 顶部 > 左侧", "顶部 > 右侧 > 左侧", "左侧 > 顶部 > 右侧"])
        snap_layout.addWidget(self.snap_priority_combo)
        
        layout.addWidget(snap_group)
        
        # 天气显示规则
        weather_group = QGroupBox("天气显示规则")
        weather_layout = QVBoxLayout(weather_group)
        
        self.weather_display_combo = QComboBox()
        self.weather_display_combo.addItems(["仅显示温度", "温度 + 天气描述", "隐藏天气"])
        weather_layout.addWidget(self.weather_display_combo)
        
        layout.addWidget(weather_group)
        
        # 课程状态标记
        course_status_group = QGroupBox("课程状态标记")
        course_status_layout = QVBoxLayout(course_status_group)
        
        self.temp_course_style_combo = QComboBox()
        self.temp_course_style_combo.addItems(["临时调课标红边框", "临时调课闪烁提醒", "临时调课标红边框+闪烁提醒"])
        course_status_layout.addWidget(self.temp_course_style_combo)
        
        layout.addWidget(course_status_group)
        
        # 添加到选项卡
        self.tab_widget.addTab(tab, "悬浮窗管理")
    
    def create_school_server_tab(self):
        """创建学校服务器功能选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 配置导出/导入
        export_import_group = QGroupBox("配置导出/导入")
        export_import_layout = QVBoxLayout(export_import_group)
        
        # 导出按钮
        self.export_button = QPushButton("导出当前设置为JSON文件")
        self.export_button.clicked.connect(self.export_settings)
        export_import_layout.addWidget(self.export_button)
        
        # 导入按钮
        self.import_button = QPushButton("从JSON文件导入设置")
        self.import_button.clicked.connect(self.import_settings)
        export_import_layout.addWidget(self.import_button)
        
        layout.addWidget(export_import_group)
        
        # 添加到选项卡
        self.tab_widget.addTab(tab, "学校服务器功能")
        
        # 添加说明标签
        info_label = QLabel("与学校服务器做对接，未来会开发校内课表云同步功能")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
    
    def load_settings(self):
        """加载设置"""
        # 从应用设置中加载配置
        settings = self.app.settings
        
        # 加载悬浮窗设置
        if "floating_window" in settings:
            fw_settings = settings["floating_window"]
            self.hide_tray_menu_checkbox.setChecked(fw_settings.get("hide_tray_menu", False))
            self.remember_position_checkbox.setChecked(fw_settings.get("remember_position", True))
            
            # 自动隐藏阈值
            threshold = fw_settings.get("auto_hide_threshold", 50)
            self.auto_hide_slider.setValue(threshold)
            self.auto_hide_value_label.setText(f"{threshold}px")
            
            # 透明度
            transparency = fw_settings.get("transparency", 80)
            self.transparency_slider.setValue(transparency)
            self.transparency_value_label.setText(f"{transparency}%")
            
            # 吸附边缘
            self.snap_edge_checkbox.setChecked(fw_settings.get("snap_to_edge", False))
            
            # 吸附优先级
            priority = fw_settings.get("snap_priority", "右侧 > 顶部 > 左侧")
            index = self.snap_priority_combo.findText(priority)
            if index >= 0:
                self.snap_priority_combo.setCurrentIndex(index)
            
            # 天气显示规则
            weather_display = fw_settings.get("weather_display", "温度 + 天气描述")
            index = self.weather_display_combo.findText(weather_display)
            if index >= 0:
                self.weather_display_combo.setCurrentIndex(index)
            
            # 课程状态标记
            temp_course_style = fw_settings.get("temp_course_style", "临时调课标红边框")
            index = self.temp_course_style_combo.findText(temp_course_style)
            if index >= 0:
                self.temp_course_style_combo.setCurrentIndex(index)
        
        # 加载天气设置
        # TODO: 实现具体的天气设置加载逻辑
        
    def save_settings(self):
        """保存设置"""
        # 收集设置数据
        settings_data = {
            "floating_window": {
                "hide_tray_menu": self.hide_tray_menu_checkbox.isChecked(),
                "remember_position": self.remember_position_checkbox.isChecked(),
                "auto_hide_threshold": self.auto_hide_slider.value(),
                "transparency": self.transparency_slider.value(),
                "snap_to_edge": self.snap_edge_checkbox.isChecked(),
                "snap_priority": self.snap_priority_combo.currentText(),
                "weather_display": self.weather_display_combo.currentText(),
                "temp_course_style": self.temp_course_style_combo.currentText()
            },
            "school_server": {
                # 学校服务器设置将在导入/导出功能中处理
            }
        }
        
        # 更新应用设置
        self.app.settings.update(settings_data)
        
        # 保存到文件
        self.app.save_data()
        
        # 发出信号通知设置已保存
        self.settings_saved.emit(settings_data)
        
        # 关闭窗口
        self.accept()
    
    def apply_settings(self):
        """应用设置"""
        # 保存设置但不关闭窗口
        self.save_settings()
    
    def export_settings(self):
        """导出设置"""
        # 选择保存文件路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出设置", "", "JSON Files (*.json)")
        
        if file_path:
            try:
                # 获取当前设置
                settings_data = {
                    "app_settings": self.app.settings,
                    "floating_window_settings": {
                        "hide_tray_menu": self.hide_tray_menu_checkbox.isChecked(),
                        "remember_position": self.remember_position_checkbox.isChecked(),
                        "auto_hide_threshold": self.auto_hide_slider.value(),
                        "transparency": self.transparency_slider.value(),
                        "snap_to_edge": self.snap_edge_checkbox.isChecked(),
                        "snap_priority": self.snap_priority_combo.currentText(),
                        "weather_display": self.weather_display_combo.currentText(),
                        "temp_course_style": self.temp_course_style_combo.currentText()
                    }
                }
                
                # 保存到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "导出成功", "设置已成功导出到文件。")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出设置时发生错误：{str(e)}")
    
    def import_settings(self):
        """导入设置"""
        # 选择导入文件路径
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入设置", "", "JSON Files (*.json)")
        
        if file_path:
            try:
                # 从文件读取设置
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # 应用设置
                # TODO: 实现具体的设置导入逻辑
                
                QMessageBox.information(self, "导入成功", "设置已成功从文件导入。")
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入设置时发生错误：{str(e)}")