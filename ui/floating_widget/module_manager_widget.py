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
TimeNest 浮窗模块管理器
提供可视化的模块管理界面
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QSplitter,
    QTextEdit, QTabWidget, QScrollArea, QFrame, QSlider
)
from PyQt6.QtGui import QFont, QColor, QPalette, QDrag, QPixmap, QPainter


if TYPE_CHECKING:
    from core.app_manager import AppManager:

    from core.app_manager import AppManager
    from .smart_floating_widget import SmartFloatingWidget


class ModuleItem(QListWidgetItem):
    """模块列表项"""
    
    def __init__(self, module_id: str, name: str, description: str, icon: str = "🧩"):
        super().__init__()
        
        self.module_id = module_id
        self.module_name = name
        self.module_description = description
        self.module_icon = icon
        
        # 设置显示文本
        self.setText(f"{icon} {name}")
        self.setToolTip(f"{name}\n{description}")
        
        # 设置数据
        self.setData(Qt.ItemDataRole.UserRole, module_id)
        self.setData(Qt.ItemDataRole.UserRole + 1, {
            'name': name,
            'description': description,
            'icon': icon
        })
        
        # 设置为可选中和可拖拽
        self.setFlags(
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled
        )
        
        # 默认选中
        self.setCheckState(Qt.CheckState.Checked)


class ModuleManagerWidget(QWidget):
    """模块管理器组件"""
    
    modules_changed = pyqtSignal(list)  # 模块配置变更信号
    module_selected = pyqtSignal(str)   # 模块选择信号
    
    def __init__(self, app_manager: 'AppManager', floating_widget: 'SmartFloatingWidget', parent=None):
        super().__init__(parent)
        
        self.app_manager = app_manager
        self.floating_widget = floating_widget
        self.logger = logging.getLogger(f'{__name__}.ModuleManagerWidget')
        
        # 模块配置
        self.module_configs = {}
        self.available_modules = self.get_available_modules()
        
        self.init_ui()
        self.load_module_configs()
        
    def init_ui(self) -> None:
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：模块列表
        self.create_module_list(splitter)
        
        # 右侧：模块配置
        self.create_module_config(splitter)
        
        # 设置分割比例
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)
        
    def create_module_list(self, parent) -> None:
        """创建模块列表"""
        list_widget = QWidget()
        layout = QVBoxLayout(list_widget)
        
        # 标题
        title = QLabel("📋 可用模块")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        layout.addWidget(title)
        
        # 模块列表
        self.module_list = QListWidget()
        self.module_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.module_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.module_list.itemChanged.connect(self.on_module_item_changed)
        self.module_list.itemSelectionChanged.connect(self.on_module_selection_changed)
        
        # 设置样式
        self.module_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QListWidget:item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget:item:selected {
                background-color: #007acc;
                color: white;
            }
            QListWidget:item:hover {
                background-color: #e6f3ff;
            }
        """)
        
        # 添加模块项
        for module_id, module_info in self.available_modules.items():
            item = ModuleItem(
                module_id,
                module_info.get('name'),
                module_info.get('description'),
                module_info.get('icon', '🧩')
            )
            self.module_list.addItem(item)
        
        layout.addWidget(self.module_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ 全选")
        self.select_all_btn.clicked.connect(self.select_all_modules)
        
        self.select_none_btn = QPushButton("❌ 全不选")
        self.select_none_btn.clicked.connect(self.select_no_modules)
        
        self.reset_order_btn = QPushButton("🔄 重置顺序")
        self.reset_order_btn.clicked.connect(self.reset_module_order)
        
        # 设置按钮样式
        for btn in [self.select_all_btn, self.select_none_btn, self.reset_order_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """)
        
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.select_none_btn)
        button_layout.addWidget(self.reset_order_btn)
        
        layout.addLayout(button_layout)
        
        # 说明文字
        help_text = QLabel("💡 拖拽调整显示顺序，勾选启用模块")
        help_text.setStyleSheet("color: #666; font-style: italic; padding: 4px;")
        layout.addWidget(help_text)
        
        parent.addWidget(list_widget)
        
    def create_module_config(self, parent) -> None:
        """创建模块配置区域"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # 标题
        title = QLabel("⚙️ 模块配置")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        layout.addWidget(title)
        
        # 配置选项卡
        self.config_tabs = QTabWidget()
        
        # 通用配置
        self.create_general_config_tab()
        
        # 模块特定配置
        self.create_module_specific_config_tab()
        
        # 显示配置
        self.create_display_config_tab()
        
        layout.addWidget(self.config_tabs)
        
        parent.addWidget(config_widget)
        
    def create_general_config_tab(self) -> None:
        """创建通用配置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 轮播设置
        rotation_group = QGroupBox("🔄 内容轮播")
        rotation_layout = QFormLayout(rotation_group)
        
        self.auto_rotate = QCheckBox("启用自动轮播")
        self.auto_rotate.setChecked(True)
        self.auto_rotate.toggled.connect(self.on_auto_rotate_toggled)
        
        self.rotate_interval = QSpinBox()
        self.rotate_interval.setRange(1, 60)
        self.rotate_interval.setValue(5)
        self.rotate_interval.setSuffix(" 秒")
        
        self.rotate_on_hover = QCheckBox("鼠标悬停时暂停轮播")
        self.rotate_on_hover.setChecked(True)
        
        rotation_layout.addRow("自动轮播:", self.auto_rotate)
        rotation_layout.addRow("轮播间隔:", self.rotate_interval)
        rotation_layout.addRow("悬停暂停:", self.rotate_on_hover)
        
        layout.addWidget(rotation_group)
        
        # 更新设置
        update_group = QGroupBox("🔄 更新设置")
        update_layout = QFormLayout(update_group)
        
        self.update_interval = QSpinBox()
        self.update_interval.setRange(100, 10000)
        self.update_interval.setValue(1000)
        self.update_interval.setSuffix(" ms")
        
        self.smart_update = QCheckBox("智能更新")
        self.smart_update.setChecked(True)
        self.smart_update.setToolTip("根据内容变化智能调整更新频率")
        
        update_layout.addRow("更新间隔:", self.update_interval)
        update_layout.addRow("智能更新:", self.smart_update)
        
        layout.addWidget(update_group)
        
        layout.addStretch()
        self.config_tabs.addTab(tab, "通用设置")
        
    def create_module_specific_config_tab(self) -> None:
        """创建模块特定配置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 时间模块配置
        self.create_time_module_config(scroll_layout)
        
        # 天气模块配置
        self.create_weather_module_config(scroll_layout)
        
        # 系统状态模块配置
        self.create_system_module_config(scroll_layout)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        self.config_tabs.addTab(tab, "模块配置")
        
    def create_display_config_tab(self) -> None:
        """创建显示配置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 字体设置
        font_group = QGroupBox("🔤 字体设置")
        font_layout = QFormLayout(font_group)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        self.font_size.setSuffix(" pt")
        
        self.font_weight = QComboBox()
        self.font_weight.addItems(["正常", "粗体", "细体"])
        
        font_layout.addRow("字体大小:", self.font_size)
        font_layout.addRow("字体粗细:", self.font_weight)
        
        layout.addWidget(font_group)
        
        # 颜色设置
        color_group = QGroupBox("🎨 颜色设置")
        color_layout = QFormLayout(color_group)
        
        self.text_color_btn = QPushButton("选择文字颜色")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        
        self.bg_color_btn = QPushButton("选择背景颜色")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        
        color_layout.addRow("文字颜色:", self.text_color_btn)
        color_layout.addRow("背景颜色:", self.bg_color_btn)
        
        layout.addWidget(color_group)
        
        layout.addStretch()
        self.config_tabs.addTab(tab, "显示设置")
        
    def get_available_modules(self) -> Dict[str, Dict[str, Any]]:
        """获取可用模块列表"""
        return {
            'time': {
                'name': '时间显示',
                'description': '显示当前时间和日期',
                'icon': '🕐',
                'category': 'basic'
            },
            'schedule': {
                'name': '课程表',
                'description': '显示当前课程信息',
                'icon': '📚',
                'category': 'education'
            },
            'countdown': {
                'name': '倒计时',
                'description': '显示重要事件倒计时',
                'icon': '⏰',
                'category': 'productivity'
            },
            'weather': {
                'name': '天气信息',
                'description': '显示当前天气状况',
                'icon': '🌤️',
                'category': 'information'
            },
            'system': {
                'name': '系统状态',
                'description': '显示CPU和内存使用率',
                'icon': '💻',
                'category': 'system'
            },
            'progress': {
                'name': '学习进度',
                'description': '显示学习进度和统计',
                'icon': '📊',
                'category': 'education'
            }
        }
        
    def create_time_module_config(self, layout: QVBoxLayout) -> None:
        """创建时间模块配置"""
        group = QGroupBox("🕐 时间模块")
        group_layout = QFormLayout(group)
        
        self.time_format_24h = QCheckBox("24小时制")
        self.time_format_24h.setChecked(True)
        
        self.show_seconds = QCheckBox("显示秒数")
        self.show_seconds.setChecked(False)
        
        self.show_date = QCheckBox("显示日期")
        self.show_date.setChecked(True)
        
        self.date_format = QComboBox()
        self.date_format.addItems([
            "YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY", "中文格式"
        ])
        
        group_layout.addRow("24小时制:", self.time_format_24h)
        group_layout.addRow("显示秒数:", self.show_seconds)
        group_layout.addRow("显示日期:", self.show_date)
        group_layout.addRow("日期格式:", self.date_format)
        
        layout.addWidget(group)
        
    def create_weather_module_config(self, layout: QVBoxLayout) -> None:
        """创建天气模块配置"""
        group = QGroupBox("🌤️ 天气模块")
        group_layout = QFormLayout(group)
        
        # 这里可以添加天气模块的具体配置
        placeholder = QLabel("天气模块配置选项...")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        group_layout.addRow(placeholder)
        
        layout.addWidget(group)
        
    def create_system_module_config(self, layout: QVBoxLayout) -> None:
        """创建系统模块配置"""
        group = QGroupBox("💻 系统状态模块")
        group_layout = QFormLayout(group)
        
        # 这里可以添加系统模块的具体配置
        placeholder = QLabel("系统状态模块配置选项...")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        group_layout.addRow(placeholder)
        
        layout.addWidget(group)
        
    def on_module_item_changed(self, item: QListWidgetItem) -> None:
        """模块项状态变更"""
        self.emit_modules_changed()
        
    def on_module_selection_changed(self) -> None:
        """模块选择变更"""
        current_item = self.module_list.currentItem()
        if current_item:
            module_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.module_selected.emit(module_id)
            
    def on_auto_rotate_toggled(self, enabled: bool) -> None:
        """自动轮播开关切换"""
        self.rotate_interval.setEnabled(enabled)
        self.rotate_on_hover.setEnabled(enabled)
        
    def select_all_modules(self) -> None:
        """选择所有模块"""
        for i in range(self.module_list.count()):
            item = self.module_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
            
    def select_no_modules(self) -> None:
        """取消选择所有模块"""
        for i in range(self.module_list.count()):
            item = self.module_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
            
    def reset_module_order(self) -> None:
        """重置模块顺序"""
        # 重新排列模块到默认顺序
        pass
        
    def choose_text_color(self) -> None:
        """选择文字颜色"""
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(Qt.GlobalColor.black, self)
        if color.isValid():
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()}"):
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()}")
            
    def choose_bg_color(self) -> None:
        """选择背景颜色"""
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(Qt.GlobalColor.white, self)
        if color.isValid():
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}"):
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            
    def emit_modules_changed(self) -> None:
        """发送模块变更信号"""
        enabled_modules = []
        for i in range(self.module_list.count()):
            item = self.module_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                module_id = item.data(Qt.ItemDataRole.UserRole)
                enabled_modules.append(module_id)
        
        self.modules_changed.emit(enabled_modules)
        
    def load_module_configs(self) -> None:
        """加载模块配置"""
        try:
            # 从配置管理器加载配置
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                configs = self.app_manager.config_manager.get_config('floating_widget.modules', {})
                self.module_configs = configs
        except Exception as e:
            self.logger.error(f"加载模块配置失败: {e}")
            
    def get_module_configs(self) -> Dict[str, Any]:
        """获取所有模块配置"""
        return {
            'enabled_modules': [
                self.module_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.module_list.count()):
                if self.module_list.item(i).checkState() == Qt.CheckState.Checked:
            ],
            'rotation': {
                'auto_rotate': self.auto_rotate.isChecked(),
                'interval': self.rotate_interval.value(),
                'pause_on_hover': self.rotate_on_hover.isChecked()
            },
            'update': {
                'interval': self.update_interval.value(),
                'smart_update': self.smart_update.isChecked()
            },
            'display': {
                'font_size': self.font_size.value(),
                'font_weight': self.font_weight.currentText()
            },
            'time_module': {
                'format_24h': self.time_format_24h.isChecked(),
                'show_seconds': self.show_seconds.isChecked(),
                'show_date': self.show_date.isChecked(),
                'date_format': self.date_format.currentText()
            }
        }
