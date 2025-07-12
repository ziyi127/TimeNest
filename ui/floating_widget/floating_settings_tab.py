#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 浮窗设置标签页扩展
提供更多高级设置功能
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QSlider, QCheckBox, QSpinBox, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QColorDialog, QMessageBox,
    QTabWidget, QScrollArea, QFrame, QSplitter
)
from PyQt6.QtGui import QFont, QColor, QPalette

if TYPE_CHECKING:
    from core.app_manager import AppManager
    from .smart_floating_widget import SmartFloatingWidget


class FloatingSettingsTabWidget(QWidget):
    """浮窗设置标签页扩展组件"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, app_manager: 'AppManager', floating_widget: 'SmartFloatingWidget', parent=None):
        super().__init__(parent)
        
        self.app_manager = app_manager
        self.floating_widget = floating_widget
        self.logger = logging.getLogger(f'{__name__}.FloatingSettingsTabWidget')
        
        self.init_ui()
        
    def init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 主内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 动画效果设置
        self.create_animation_settings(content_layout)
        
        # 交互行为设置
        self.create_interaction_settings(content_layout)
        
        # 显示效果设置
        self.create_display_effects_settings(content_layout)
        
        # 性能优化设置
        self.create_performance_settings(content_layout)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
    def create_animation_settings(self, layout: QVBoxLayout) -> None:
        """创建动画效果设置"""
        group = QGroupBox("🎬 动画效果")
        group_layout = QFormLayout(group)
        
        # 启用动画
        self.animation_enabled = QCheckBox("启用动画效果")
        self.animation_enabled.setChecked(True)
        self.animation_enabled.toggled.connect(self.on_animation_toggled)
        
        # 动画速度
        self.animation_speed = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed.setRange(1, 10)
        self.animation_speed.setValue(5)
        self.animation_speed.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.animation_speed_label = QLabel("中等")
        self.animation_speed.valueChanged.connect(self.update_animation_speed_label)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.animation_speed)
        speed_layout.addWidget(self.animation_speed_label)
        
        # 动画类型
        self.animation_type = QComboBox()
        self.animation_type.addItems([
            "淡入淡出", "滑动", "缩放", "弹性", "自定义"
        ])
        
        # 进入动画
        self.enter_animation = QComboBox()
        self.enter_animation.addItems([
            "从上滑入", "从下滑入", "从左滑入", "从右滑入", 
            "淡入", "缩放进入", "旋转进入"
        ])
        
        # 退出动画
        self.exit_animation = QComboBox()
        self.exit_animation.addItems([
            "向上滑出", "向下滑出", "向左滑出", "向右滑出",
            "淡出", "缩放退出", "旋转退出"
        ])
        
        group_layout.addRow("启用动画:", self.animation_enabled)
        group_layout.addRow("动画速度:", speed_layout)
        group_layout.addRow("动画类型:", self.animation_type)
        group_layout.addRow("进入动画:", self.enter_animation)
        group_layout.addRow("退出动画:", self.exit_animation)
        
        layout.addWidget(group)
        
    def create_interaction_settings(self, layout: QVBoxLayout) -> None:
        """创建交互行为设置"""
        group = QGroupBox("🖱️ 交互行为")
        group_layout = QFormLayout(group)
        
        # 鼠标悬停效果
        self.hover_effects = QCheckBox("鼠标悬停高亮")
        self.hover_effects.setChecked(True)
        
        # 点击行为
        self.click_behavior = QComboBox()
        self.click_behavior.addItems([
            "无操作", "显示详细信息", "打开设置", "切换模块", "自定义操作"
        ])
        
        # 双击行为
        self.double_click_behavior = QComboBox()
        self.double_click_behavior.addItems([
            "无操作", "隐藏浮窗", "打开设置", "全屏显示", "最小化"
        ])
        
        # 右键菜单
        self.context_menu_enabled = QCheckBox("启用右键菜单")
        self.context_menu_enabled.setChecked(True)
        
        # 拖拽行为
        self.drag_enabled = QCheckBox("允许拖拽移动")
        self.drag_enabled.setChecked(False)
        
        # 键盘快捷键
        self.keyboard_shortcuts = QCheckBox("启用键盘快捷键")
        self.keyboard_shortcuts.setChecked(True)
        
        group_layout.addRow("悬停效果:", self.hover_effects)
        group_layout.addRow("单击行为:", self.click_behavior)
        group_layout.addRow("双击行为:", self.double_click_behavior)
        group_layout.addRow("右键菜单:", self.context_menu_enabled)
        group_layout.addRow("拖拽移动:", self.drag_enabled)
        group_layout.addRow("快捷键:", self.keyboard_shortcuts)
        
        layout.addWidget(group)
        
    def create_display_effects_settings(self, layout: QVBoxLayout) -> None:
        """创建显示效果设置"""
        group = QGroupBox("✨ 显示效果")
        group_layout = QFormLayout(group)
        
        # 阴影效果
        self.shadow_enabled = QCheckBox("启用阴影效果")
        self.shadow_enabled.setChecked(True)
        
        # 阴影强度
        self.shadow_intensity = QSlider(Qt.Orientation.Horizontal)
        self.shadow_intensity.setRange(0, 100)
        self.shadow_intensity.setValue(50)
        
        # 边框效果
        self.border_enabled = QCheckBox("启用边框")
        self.border_enabled.setChecked(False)
        
        # 边框颜色
        self.border_color_btn = QPushButton("选择边框颜色")
        self.border_color_btn.clicked.connect(self.choose_border_color)
        
        # 渐变背景
        self.gradient_background = QCheckBox("渐变背景")
        self.gradient_background.setChecked(False)
        
        # 模糊效果
        self.blur_background = QCheckBox("背景模糊")
        self.blur_background.setChecked(False)
        
        # 发光效果
        self.glow_effect = QCheckBox("发光效果")
        self.glow_effect.setChecked(False)
        
        group_layout.addRow("阴影效果:", self.shadow_enabled)
        group_layout.addRow("阴影强度:", self.shadow_intensity)
        group_layout.addRow("边框效果:", self.border_enabled)
        group_layout.addRow("边框颜色:", self.border_color_btn)
        group_layout.addRow("渐变背景:", self.gradient_background)
        group_layout.addRow("背景模糊:", self.blur_background)
        group_layout.addRow("发光效果:", self.glow_effect)
        
        layout.addWidget(group)
        
    def create_performance_settings(self, layout: QVBoxLayout) -> None:
        """创建性能优化设置"""
        group = QGroupBox("⚡ 性能优化")
        group_layout = QFormLayout(group)
        
        # 低功耗模式
        self.low_power_mode = QCheckBox("低功耗模式")
        self.low_power_mode.setChecked(False)
        
        # 更新频率
        self.update_frequency = QSpinBox()
        self.update_frequency.setRange(100, 5000)
        self.update_frequency.setValue(1000)
        self.update_frequency.setSuffix(" ms")
        
        # GPU加速
        self.gpu_acceleration = QCheckBox("GPU加速渲染")
        self.gpu_acceleration.setChecked(True)
        
        # 内存优化
        self.memory_optimization = QCheckBox("内存优化")
        self.memory_optimization.setChecked(True)
        
        # 后台运行优化
        self.background_optimization = QCheckBox("后台运行优化")
        self.background_optimization.setChecked(True)
        
        group_layout.addRow("低功耗模式:", self.low_power_mode)
        group_layout.addRow("更新频率:", self.update_frequency)
        group_layout.addRow("GPU加速:", self.gpu_acceleration)
        group_layout.addRow("内存优化:", self.memory_optimization)
        group_layout.addRow("后台优化:", self.background_optimization)
        
        layout.addWidget(group)
        
    def on_animation_toggled(self, enabled: bool) -> None:
        """动画开关切换"""
        self.animation_speed.setEnabled(enabled)
        self.animation_type.setEnabled(enabled)
        self.enter_animation.setEnabled(enabled)
        self.exit_animation.setEnabled(enabled)
        
    def update_animation_speed_label(self, value: int) -> None:
        """更新动画速度标签"""
        speed_labels = {
            1: "很慢", 2: "慢", 3: "较慢", 4: "稍慢", 5: "中等",
            6: "稍快", 7: "较快", 8: "快", 9: "很快", 10: "极快"
        }
        self.animation_speed_label.setText(speed_labels.get(value, "中等"))
        
    def choose_border_color(self) -> None:
        """选择边框颜色"""
        color = QColorDialog.getColor(Qt.GlobalColor.black, self)
        if color.isValid():
            self.border_color_btn.setStyleSheet(f"background-color: {color.name()}")
            
    def get_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        return {
            'animation': {
                'enabled': self.animation_enabled.isChecked(),
                'speed': self.animation_speed.value(),
                'type': self.animation_type.currentText(),
                'enter': self.enter_animation.currentText(),
                'exit': self.exit_animation.currentText()
            },
            'interaction': {
                'hover_effects': self.hover_effects.isChecked(),
                'click_behavior': self.click_behavior.currentText(),
                'double_click_behavior': self.double_click_behavior.currentText(),
                'context_menu': self.context_menu_enabled.isChecked(),
                'drag_enabled': self.drag_enabled.isChecked(),
                'keyboard_shortcuts': self.keyboard_shortcuts.isChecked()
            },
            'display_effects': {
                'shadow_enabled': self.shadow_enabled.isChecked(),
                'shadow_intensity': self.shadow_intensity.value(),
                'border_enabled': self.border_enabled.isChecked(),
                'gradient_background': self.gradient_background.isChecked(),
                'blur_background': self.blur_background.isChecked(),
                'glow_effect': self.glow_effect.isChecked()
            },
            'performance': {
                'low_power_mode': self.low_power_mode.isChecked(),
                'update_frequency': self.update_frequency.value(),
                'gpu_acceleration': self.gpu_acceleration.isChecked(),
                'memory_optimization': self.memory_optimization.isChecked(),
                'background_optimization': self.background_optimization.isChecked()
            }
        }
        
    def load_settings(self, settings: Dict[str, Any]) -> None:
        """加载设置"""
        try:
            # 加载动画设置
            if 'animation' in settings:
                anim = settings['animation']
                self.animation_enabled.setChecked(anim.get('enabled', True))
                self.animation_speed.setValue(anim.get('speed', 5))
                
            # 加载交互设置
            if 'interaction' in settings:
                inter = settings['interaction']
                self.hover_effects.setChecked(inter.get('hover_effects', True))
                self.context_menu_enabled.setChecked(inter.get('context_menu', True))
                
            # 加载显示效果设置
            if 'display_effects' in settings:
                display = settings['display_effects']
                self.shadow_enabled.setChecked(display.get('shadow_enabled', True))
                self.shadow_intensity.setValue(display.get('shadow_intensity', 50))
                
            # 加载性能设置
            if 'performance' in settings:
                perf = settings['performance']
                self.low_power_mode.setChecked(perf.get('low_power_mode', False))
                self.update_frequency.setValue(perf.get('update_frequency', 1000))
                
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
