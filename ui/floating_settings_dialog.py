#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 独立浮窗设置对话框
以浮窗形式显示的浮窗设置界面
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QSlider, QSpinBox, QComboBox, QCheckBox,
    QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

from core.base_manager import BaseManager


class FloatingSettingsDialog(QWidget):
    """独立的浮窗设置对话框"""
    
    # 信号定义
    settings_changed = pyqtSignal(str, object)  # 设置名, 值
    settings_applied = pyqtSignal()
    dialog_closed = pyqtSignal()
    
    def __init__(self, config_manager: Optional[object] = None, theme_manager: Optional[object] = None, floating_manager: Optional[object] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.floating_manager = floating_manager
        
        self.logger = logging.getLogger(f'{__name__}.FloatingSettingsDialog')
        
        # 设置窗口属性
        self.setWindowTitle("🎈 浮窗设置")
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小和位置
        self.setFixedSize(420, 600)
        self.move_to_center()
        
        # 初始化UI
        self.init_ui()
        
        # 加载当前设置
        self.load_current_settings()
        
        # 连接信号
        self.connect_signals()
        
        # 应用样式
        self.apply_floating_style()
        
        self.logger.info("浮窗设置对话框初始化完成")
    
    def init_ui(self) -> None:
        """初始化用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 标题栏
        self.create_title_bar(main_layout)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # 创建设置组
        self.create_appearance_group(content_layout)
        self.create_position_group(content_layout)
        self.create_modules_group(content_layout)
        self.create_interaction_group(content_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部按钮
        self.create_bottom_buttons(main_layout)
    
    def create_title_bar(self, layout):
        """创建标题栏"""
        title_frame = QFrame()
        title_frame.setFixedHeight(40)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # 标题
        title_label = QLabel("🎈 浮窗设置")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.close_dialog)
        title_layout.addWidget(self.close_button)
        
        layout.addWidget(title_frame)
    
    def create_appearance_group(self, layout):
        """创建外观设置组"""
        appearance_group = QGroupBox("🎨 外观设置")
        appearance_layout = QFormLayout(appearance_group)
        
        # 透明度
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(90)
        self.opacity_label = QLabel("90%")
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        appearance_layout.addRow("透明度:", opacity_layout)
        
        # 尺寸设置
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 800)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" px")
        size_layout.addWidget(QLabel("宽:"))
        size_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(40, 200)
        self.height_spin.setValue(60)
        self.height_spin.setSuffix(" px")
        size_layout.addWidget(QLabel("高:"))
        size_layout.addWidget(self.height_spin)
        appearance_layout.addRow("尺寸:", size_layout)
        
        # 圆角
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 50)
        self.border_radius_spin.setValue(30)
        self.border_radius_spin.setSuffix(" px")
        appearance_layout.addRow("圆角:", self.border_radius_spin)
        
        layout.addWidget(appearance_group)
    
    def create_position_group(self, layout):
        """创建位置设置组"""
        position_group = QGroupBox("📍 位置设置")
        position_layout = QFormLayout(position_group)
        
        self.position_preset_combo = QComboBox()
        self.position_preset_combo.addItems([
            "屏幕顶部居中", "屏幕顶部左侧", "屏幕顶部右侧",
            "屏幕底部居中", "自定义位置"
        ])
        position_layout.addRow("位置预设:", self.position_preset_combo)
        
        # 自定义坐标
        coord_layout = QHBoxLayout()
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setValue(100)
        coord_layout.addWidget(QLabel("X:"))
        coord_layout.addWidget(self.x_spin)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setValue(10)
        coord_layout.addWidget(QLabel("Y:"))
        coord_layout.addWidget(self.y_spin)
        position_layout.addRow("自定义坐标:", coord_layout)
        
        layout.addWidget(position_group)
    
    def create_modules_group(self, layout):
        """创建模块管理组"""
        modules_group = QGroupBox("🧩 模块管理")
        modules_layout = QVBoxLayout(modules_group)
        
        modules_layout.addWidget(QLabel("拖拽调整显示顺序，勾选启用模块:"))
        
        self.modules_list = QListWidget()
        self.modules_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.modules_list.setMaximumHeight(120)
        
        # 添加模块项
        modules = [
            ("time", "⏰ 时间显示", True),
            ("schedule", "📅 课程表", True),
            ("weather", "🌤️ 天气信息", False),
            ("calendar", "📆 日历", False),
            ("tasks", "📋 任务提醒", False)
        ]
        
        for module_id, module_name, enabled in modules:
            item = QListWidgetItem(module_name)
            item.setData(Qt.ItemDataRole.UserRole, module_id)
            item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            self.modules_list.addItem(item)
        
        modules_layout.addWidget(self.modules_list)
        layout.addWidget(modules_group)
    
    def create_interaction_group(self, layout):
        """创建交互设置组"""
        interaction_group = QGroupBox("🖱️ 交互设置")
        interaction_layout = QFormLayout(interaction_group)
        
        self.mouse_transparent_check = QCheckBox("鼠标穿透")
        self.mouse_transparent_check.setChecked(True)
        interaction_layout.addRow(self.mouse_transparent_check)
        
        self.auto_hide_check = QCheckBox("自动隐藏")
        interaction_layout.addRow(self.auto_hide_check)
        
        self.always_on_top_check = QCheckBox("总是置顶")
        self.always_on_top_check.setChecked(True)
        interaction_layout.addRow(self.always_on_top_check)
        
        layout.addWidget(interaction_group)
    
    def create_bottom_buttons(self, layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        
        # 应用按钮
        self.apply_button = QPushButton("✅ 应用")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        # 重置按钮
        self.reset_button = QPushButton("🔄 重置")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        # 关闭按钮
        self.close_btn = QPushButton("❌ 关闭")
        self.close_btn.clicked.connect(self.close_dialog)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def move_to_center(self):
        """移动到屏幕中央"""
        try:
            from PyQt6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except Exception as e:
            self.logger.error(f"移动到屏幕中央失败: {e}")
    
    def apply_floating_style(self):
        """应用浮窗样式"""
        try:
            style = """
            QWidget {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 15px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid rgba(200, 200, 200, 150);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(248, 248, 248, 200);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #333;
            }
            
            QPushButton {
                background-color: rgba(70, 130, 180, 200);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 255);
            }
            
            QPushButton:pressed {
                background-color: rgba(50, 110, 160, 255);
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #4682b4;
                border: 1px solid #5c5c5c;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QComboBox, QSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
            
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            self.logger.error(f"应用浮窗样式失败: {e}")
    
    def connect_signals(self):
        """连接信号"""
        try:
            # 连接设置变化信号
            self.width_spin.valueChanged.connect(lambda v: self.settings_changed.emit("width", v))
            self.height_spin.valueChanged.connect(lambda v: self.settings_changed.emit("height", v))
            self.border_radius_spin.valueChanged.connect(lambda v: self.settings_changed.emit("border_radius", v))
            self.position_preset_combo.currentTextChanged.connect(lambda v: self.settings_changed.emit("position_preset", v))
            self.x_spin.valueChanged.connect(lambda v: self.settings_changed.emit("x", v))
            self.y_spin.valueChanged.connect(lambda v: self.settings_changed.emit("y", v))
            self.mouse_transparent_check.toggled.connect(lambda v: self.settings_changed.emit("mouse_transparent", v))
            self.auto_hide_check.toggled.connect(lambda v: self.settings_changed.emit("auto_hide", v))
            self.always_on_top_check.toggled.connect(lambda v: self.settings_changed.emit("always_on_top", v))
            
        except Exception as e:
            self.logger.error(f"连接信号失败: {e}")
    
    def on_opacity_changed(self, value):
        """透明度变化处理"""
        self.opacity_label.setText(f"{value}%")
        self.settings_changed.emit("opacity", value / 100.0)
    
    def load_current_settings(self):
        """加载当前设置"""
        try:
            if not self.config_manager:
                return
            
            # 从配置管理器加载设置
            floating_config = self.config_manager.get_config("floating_widget", {})
            
            # 应用设置到控件
            self.opacity_slider.setValue(int(floating_config.get("opacity", 0.9) * 100))
            self.width_spin.setValue(floating_config.get("width", 400))
            self.height_spin.setValue(floating_config.get("height", 60))
            self.border_radius_spin.setValue(floating_config.get("border_radius", 30))
            
            position_preset = floating_config.get("position_preset", "屏幕顶部居中")
            index = self.position_preset_combo.findText(position_preset)
            if index >= 0:
                self.position_preset_combo.setCurrentIndex(index)
            
            self.x_spin.setValue(floating_config.get("x", 100))
            self.y_spin.setValue(floating_config.get("y", 10))
            
            self.mouse_transparent_check.setChecked(floating_config.get("mouse_transparent", True))
            self.auto_hide_check.setChecked(floating_config.get("auto_hide", False))
            self.always_on_top_check.setChecked(floating_config.get("always_on_top", True))
            
            self.logger.info("当前设置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载当前设置失败: {e}")
    
    def apply_settings(self):
        """应用设置"""
        try:
            if not self.config_manager:
                return
            
            # 收集设置
            settings = {
                "opacity": self.opacity_slider.value() / 100.0,
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
                "border_radius": self.border_radius_spin.value(),
                "position_preset": self.position_preset_combo.currentText(),
                "x": self.x_spin.value(),
                "y": self.y_spin.value(),
                "mouse_transparent": self.mouse_transparent_check.isChecked(),
                "auto_hide": self.auto_hide_check.isChecked(),
                "always_on_top": self.always_on_top_check.isChecked()
            }
            
            # 收集模块设置
            modules = {}
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                module_id = item.data(Qt.ItemDataRole.UserRole)
                enabled = item.checkState() == Qt.CheckState.Checked
                modules[module_id] = {"enabled": enabled, "order": i}
            
            settings["modules"] = modules
            
            # 保存到配置
            self.config_manager.set_config("floating_widget", settings)
            
            # 应用到浮窗管理器
            if self.floating_manager:
                self.floating_manager.apply_settings(settings)
            
            self.settings_applied.emit()
            self.logger.info("设置已应用")
            
        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
    
    def reset_settings(self):
        """重置设置"""
        try:
            # 重置为默认值
            self.opacity_slider.setValue(90)
            self.width_spin.setValue(400)
            self.height_spin.setValue(60)
            self.border_radius_spin.setValue(30)
            self.position_preset_combo.setCurrentIndex(0)
            self.x_spin.setValue(100)
            self.y_spin.setValue(10)
            self.mouse_transparent_check.setChecked(True)
            self.auto_hide_check.setChecked(False)
            self.always_on_top_check.setChecked(True)
            
            # 重置模块列表
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                module_id = item.data(Qt.ItemDataRole.UserRole)
                # 默认启用时间和课程表
                enabled = module_id in ["time", "schedule"]
                item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            
            self.logger.info("设置已重置")
            
        except Exception as e:
            self.logger.error(f"重置设置失败: {e}")
    
    def close_dialog(self):
        """关闭对话框"""
        try:
            self.dialog_closed.emit()
            self.hide()
            self.logger.info("浮窗设置对话框已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭对话框失败: {e}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于拖拽"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
