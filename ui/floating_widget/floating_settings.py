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
TimeNest 浮窗设置界面
提供浮窗外观、模块管理等设置功能
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QWidget,
    QLabel, QSlider, QCheckBox, QSpinBox, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QColorDialog,
    QFontDialog, QMessageBox, QFormLayout, QDialogButtonBox, QLineEdit,
    QScrollArea
)
from PyQt6.QtGui import QFont, QColor

# 尝试导入版本管理器
try:
    from utils.version_manager import version_manager
except ImportError:
    # 如果导入失败，创建简单的备用版本
    class SimpleVersionManager:
        def get_app_name(self): return "null"
    version_manager = SimpleVersionManager()


if TYPE_CHECKING:
    from core.app_manager import AppManager
    from .smart_floating_widget import SmartFloatingWidget


class FloatingSettingsDialog(QDialog):
    """
    浮窗设置对话框
    
    提供浮窗的各种配置选项
    """
    
    # 信号定义
    settings_applied = pyqtSignal(dict)  # 设置应用信号
    
    def __init__(self, app_manager: 'AppManager', floating_widget: 'SmartFloatingWidget', parent=None):
        """
        初始化设置对话框
        
        Args:
            app_manager: 应用管理器实例
            floating_widget: 浮窗实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 依赖注入
        self.app_manager = app_manager
        self.floating_widget = floating_widget
        self.logger = logging.getLogger(f'{__name__}.FloatingSettingsDialog')
        
        # 设置数据
        self.settings = {}
        self.load_settings()
        
        # 初始化UI
        self.init_ui()
        self.load_current_settings()
        
        self.logger.debug("浮窗设置对话框初始化完成")
    
    def load_settings(self) -> None:
        """加载当前设置"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.settings = self.app_manager.config_manager.get_config('floating_widget', {}, 'component')
        except Exception as e:
            self.logger.warning(f"加载设置失败: {e}")
            self.settings = {}
    
    def save_settings(self) -> None:
        """保存设置"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.app_manager.config_manager.set_config('floating_widget', self.settings, 'component')
                self.logger.debug("设置保存成功")
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
    
    def init_ui(self) -> None:
        """初始化UI"""
        try:
            app_name = version_manager.get_app_name()
            title = f"🎨 {app_name} 浮窗设置" if app_name else "🎨 null 浮窗设置"
            self.setWindowTitle(title)
            self.setFixedSize(900, 650)  # 更大的窗口尺寸，确保内容不重叠
            self.setModal(True)

            # 设置简洁的样式
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QTabWidget:pane {
                    border: 1px solid #ddd;
                    background-color: white;
                }
                QTabBar:tab {
                    background-color: #e9e9e9;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar:tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #007acc;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #ddd;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox:title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)

            # 主布局
            layout = QVBoxLayout(self)
            layout.setSpacing(8)
            layout.setContentsMargins(10, 10, 10, 10)

            # 添加标题
            title_label = QLabel("🎨 浮窗个性化设置")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)

            # 创建选项卡
            self.tab_widget = QTabWidget()

            # 外观设置选项卡
            self.appearance_tab = self.create_appearance_tab()
            self.tab_widget.addTab(self.appearance_tab, "🎨 外观设置")

            # 模块管理选项卡
            self.modules_tab = self.create_modules_tab()
            self.tab_widget.addTab(self.modules_tab, "🧩 模块管理")

            # 高级设置选项卡
            self.advanced_tab = self.create_advanced_tab()
            self.tab_widget.addTab(self.advanced_tab, "⚙️ 高级设置")

            # 新增：预设方案选项卡
            self.presets_tab = self.create_presets_tab()
            self.tab_widget.addTab(self.presets_tab, "📋 预设方案")

            layout.addWidget(self.tab_widget)

            # 实时预览区域
            self.create_preview_area(layout)

            # 按钮组
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel |
                QDialogButtonBox.StandardButton.Apply |
                QDialogButtonBox.StandardButton.RestoreDefaults
            )

            # 美化按钮
            button_box.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e6f3ff;
                }
            """)

            button_box.accepted.connect(self.accept_settings)
            button_box.rejected.connect(self.reject)
            button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
            button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)

            layout.addWidget(button_box)

        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")

    def create_preview_area(self, layout: QVBoxLayout) -> None:
        """创建实时预览区域"""
        try:
            preview_group = QGroupBox("🔍 实时预览")
            preview_layout = QVBoxLayout(preview_group)

            # 预览说明
            preview_info = QLabel("在这里可以实时预览浮窗效果")
            preview_info.setStyleSheet("color: #666; font-style: italic;")
            preview_layout.addWidget(preview_info)

            # 预览控制按钮
            preview_controls = QHBoxLayout()

            self.preview_btn = QPushButton("🔄 刷新预览")
            self.preview_btn.clicked.connect(self.refresh_preview)
            self.preview_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)

            self.test_position_btn = QPushButton("📍 测试位置")
            self.test_position_btn.clicked.connect(self.test_position)
            self.test_position_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1e7e34;
                }
            """)

            preview_controls.addWidget(self.preview_btn)
            preview_controls.addWidget(self.test_position_btn)
            preview_controls.addStretch()

            preview_layout.addLayout(preview_controls)
            layout.addWidget(preview_group)

        except Exception as e:
            self.logger.error(f"创建预览区域失败: {e}")

    def create_presets_tab(self) -> QWidget:
        """创建预设方案选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # 设置简单的样式，确保文字为黑色
        tab.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
            QGroupBox {
                color: black;
                font-weight: bold;
                border: 1px solid gray;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)

        # 预设方案说明
        info_label = QLabel("选择预设方案快速配置浮窗样式")
        info_label.setStyleSheet("color: #666; font-style: italic; font-size: 14px;")
        layout.addWidget(info_label)

        # 预设方案网格布局
        presets_group = QGroupBox("预设方案")
        presets_layout = QGridLayout(presets_group)
        presets_layout.setSpacing(10)

        # 预设方案数据
        presets = [
            ("minimal", "🎯 极简模式", "简洁时间显示"),
            ("productivity", "💼 效率模式", "时间+课程+状态"),
            ("comprehensive", "📊 全功能模式", "显示所有模块"),
            ("gaming", "🎮 游戏模式", "低干扰显示"),
            ("presentation", "🎤 演示模式", "大字体高对比")
        ]

        # 使用网格布局排列预设按钮
        for i, (preset_id, name, description) in enumerate(presets):
            row = i // 2
            col = i % 2

            preset_btn = QPushButton(f"{name}\n{description}")
            preset_btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 10px;
                    border: 1px solid gray;
                    background-color: white;
                    color: black;
                    font-size: 11px;
                    min-height: 50px;
                    max-height: 50px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            preset_btn.clicked.connect(lambda checked, pid=preset_id: self.apply_preset(pid))
            presets_layout.addWidget(preset_btn, row, col)

        layout.addWidget(presets_group)

        # 自定义方案管理
        custom_group = QGroupBox("自定义方案")
        custom_layout = QHBoxLayout(custom_group)

        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("输入方案名称...")
        custom_layout.addWidget(QLabel("方案名称:"))
        custom_layout.addWidget(self.preset_name_edit)

        save_preset_btn = QPushButton("保存当前配置")
        save_preset_btn.clicked.connect(self.save_custom_preset)
        custom_layout.addWidget(save_preset_btn)

        layout.addWidget(custom_group)
        layout.addStretch()

        return tab

    def create_appearance_tab(self) -> QWidget:
        """创建外观设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 透明度设置
        opacity_group = QGroupBox("透明度设置")
        opacity_layout = QHBoxLayout(opacity_group)

        opacity_layout.addWidget(QLabel("透明度:"))

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(90)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        opacity_layout.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("90%")
        self.opacity_label.setStyleSheet("font-weight: bold; color: #007acc; min-width: 40px;")
        self.opacity_slider.valueChanged.connect(
            lambda v: [
                self.opacity_label.setText(f"{v}%"),
                self.on_setting_changed()
            ]
        )
        opacity_layout.addWidget(self.opacity_label)

        layout.addWidget(opacity_group)

        # 尺寸设置
        size_group = QGroupBox("尺寸设置")
        size_layout = QFormLayout(size_group)

        # 宽度设置
        width_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(250, 800)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" px")
        self.width_spin.valueChanged.connect(self.on_setting_changed)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        size_layout.addRow("宽度:", width_layout)

        # 高度设置
        height_layout = QHBoxLayout()
        self.height_spin = QSpinBox()
        self.height_spin.setRange(40, 120)
        self.height_spin.setValue(60)
        self.height_spin.setSuffix(" px")
        self.height_spin.valueChanged.connect(self.on_setting_changed)
        height_layout.addWidget(self.height_spin)
        height_layout.addStretch()
        size_layout.addRow("高度:", height_layout)

        # 圆角设置
        radius_layout = QHBoxLayout()
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 60)
        self.radius_spin.setValue(30)
        self.radius_spin.setSuffix(" px")
        self.radius_spin.valueChanged.connect(self.on_setting_changed)
        radius_layout.addWidget(self.radius_spin)
        radius_layout.addStretch()
        size_layout.addRow("圆角:", radius_layout)

        layout.addWidget(size_group)
        
        # 颜色和字体设置
        style_group = QGroupBox("样式设置")
        style_layout = QFormLayout(style_group)

        # 背景色
        bg_layout = QHBoxLayout()
        self.background_color_btn = QPushButton("选择背景色")
        self.background_color_btn.clicked.connect(self.choose_background_color)
        bg_layout.addWidget(self.background_color_btn)
        bg_layout.addStretch()
        style_layout.addRow("背景色:", bg_layout)

        # 文字色
        text_layout = QHBoxLayout()
        self.text_color_btn = QPushButton("选择文字色")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        text_layout.addWidget(self.text_color_btn)
        text_layout.addStretch()
        style_layout.addRow("文字色:", text_layout)

        # 字体
        font_layout = QHBoxLayout()
        self.font_btn = QPushButton("选择字体")
        self.font_btn.clicked.connect(self.choose_font)
        font_layout.addWidget(self.font_btn)

        self.font_label = QLabel("Arial, 12pt")
        font_layout.addWidget(self.font_label)
        font_layout.addStretch()
        style_layout.addRow("字体:", font_layout)

        layout.addWidget(style_group)
        
        layout.addStretch()
        return tab
    
    def create_modules_tab(self) -> QWidget:
        """创建模块管理选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 模块列表
        modules_group = QGroupBox("可用模块")
        modules_layout = QVBoxLayout(modules_group)
        
        self.modules_list = QListWidget()
        self.modules_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.modules_list.itemChanged.connect(self.on_module_item_changed)
        self.modules_list.itemSelectionChanged.connect(self.on_module_selection_changed)
        
        # 添加模块项
        modules = [
            ("time", "时间显示", "显示当前时间"),
            ("schedule", "课程表", "显示当前课程信息"),
            ("countdown", "倒计时", "显示重要事件倒计时"),
            ("weather", "天气信息", "显示当前天气"),
            ("system", "系统状态", "显示CPU和内存使用率")
        ]
        
        for module_id, name, description in modules:
            item = QListWidgetItem(f"{name} - {description}")
            item.setData(Qt.ItemDataRole.UserRole, module_id)
            item.setCheckState(Qt.CheckState.Checked)
            self.modules_list.addItem(item)
        
        modules_layout.addWidget(QLabel("拖拽调整显示顺序，勾选启用模块:"))
        modules_layout.addWidget(self.modules_list)
        layout.addWidget(modules_group)
        
        # 模块设置
        module_settings_group = QGroupBox("模块设置")
        module_settings_layout = QFormLayout(module_settings_group)
        
        # 时间模块设置
        self.time_24h_check = QCheckBox("24小时制")
        self.time_seconds_check = QCheckBox("显示秒数")
        
        module_settings_layout.addRow("时间格式:", self.time_24h_check)
        module_settings_layout.addRow("", self.time_seconds_check)
        
        # 天气模块设置
        self.weather_api_key_edit = QLineEdit()
        self.weather_city_edit = QLineEdit()
        self.weather_city_edit.setText("Beijing")
        
        module_settings_layout.addRow("天气API密钥:", self.weather_api_key_edit)
        module_settings_layout.addRow("城市:", self.weather_city_edit)
        
        layout.addWidget(module_settings_group)
        
        layout.addStretch()
        return tab
    
    def create_advanced_tab(self) -> QWidget:
        """创建高级设置选项卡"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 设置简单的样式，确保文字为黑色
        tab.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
                font-size: 12px;
            }
        """)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 滚动内容容器
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # 位置设置 - 使用简单的垂直布局
        layout.addWidget(QLabel("=== 位置设置 ==="))

        layout.addWidget(QLabel("预设位置:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "屏幕顶部居中", "屏幕顶部左侧", "屏幕顶部右侧",
            "屏幕底部居中", "自定义位置"
        ])
        self.position_combo.currentTextChanged.connect(self.on_position_preset_changed)
        layout.addWidget(self.position_combo)

        layout.addWidget(QLabel("X坐标:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setValue(0)
        layout.addWidget(self.x_spin)

        layout.addWidget(QLabel("Y坐标:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setValue(10)
        layout.addWidget(self.y_spin)

        # 行为设置
        layout.addWidget(QLabel("=== 行为设置 ==="))

        self.animation_enabled_check = QCheckBox("启用动画效果")
        self.animation_enabled_check.setChecked(True)
        layout.addWidget(self.animation_enabled_check)

        layout.addWidget(QLabel("动画时长:"))
        self.animation_duration_spin = QSpinBox()
        self.animation_duration_spin.setRange(100, 1000)
        self.animation_duration_spin.setValue(300)
        self.animation_duration_spin.setSuffix(" ms")
        layout.addWidget(self.animation_duration_spin)

        layout.addWidget(QLabel("更新间隔:"))
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(500, 5000)
        self.update_interval_spin.setValue(1000)
        self.update_interval_spin.setSuffix(" ms")
        layout.addWidget(self.update_interval_spin)

        self.low_cpu_mode_check = QCheckBox("低CPU使用模式")
        layout.addWidget(self.low_cpu_mode_check)

        # 交互设置
        layout.addWidget(QLabel("=== 交互设置 ==="))

        self.mouse_transparent_check = QCheckBox("启用鼠标穿透")
        self.mouse_transparent_check.setToolTip("启用后，鼠标点击将穿透浮窗到下层窗口")
        layout.addWidget(self.mouse_transparent_check)

        self.fixed_position_check = QCheckBox("固定位置")
        self.fixed_position_check.setToolTip("启用后，浮窗将固定在屏幕顶部中央，不可拖拽")
        layout.addWidget(self.fixed_position_check)

        self.auto_rotate_check = QCheckBox("自动轮播内容")
        self.auto_rotate_check.setToolTip("当有多个模块时，自动轮播显示不同内容")
        layout.addWidget(self.auto_rotate_check)

        layout.addWidget(QLabel("轮播间隔:"))
        self.rotate_interval_spin = QSpinBox()
        self.rotate_interval_spin.setRange(3, 30)
        self.rotate_interval_spin.setValue(5)
        self.rotate_interval_spin.setSuffix(" 秒")
        layout.addWidget(self.rotate_interval_spin)

        # 其他设置
        layout.addWidget(QLabel("=== 其他设置 ==="))

        self.auto_start_check = QCheckBox("开机自启动")
        layout.addWidget(self.auto_start_check)

        self.start_minimized_check = QCheckBox("启动时最小化")
        layout.addWidget(self.start_minimized_check)

        # 操作按钮
        layout.addWidget(QLabel("=== 操作 ==="))

        self.preview_button = QPushButton("预览设置")
        self.preview_button.setToolTip("预览当前设置效果")
        self.preview_button.clicked.connect(self.preview_settings)
        layout.addWidget(self.preview_button)

        self.reset_button = QPushButton("重置默认")
        self.reset_button.setToolTip("重置所有设置为默认值")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_button)

        layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return tab

    def load_current_settings(self) -> None:
        """加载当前设置到UI"""
        try:
            # 外观设置
            appearance = self.settings.get('appearance', {})
            self.opacity_slider.setValue(int(appearance.get('opacity', 0.9) * 100))
            self.width_spin.setValue(self.settings.get('width', 400))
            self.height_spin.setValue(self.settings.get('height', 60))
            self.radius_spin.setValue(self.settings.get('border_radius', 30))

            # 模块设置
            modules_config = self.settings.get('modules', {})
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                module_id = item.data(Qt.ItemDataRole.UserRole)
                module_config = modules_config.get(module_id, {})


                if module_config.get('enabled', True):
                    item.setCheckState(Qt.CheckState.Checked)

                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)

            # 时间模块设置
            time_config = modules_config.get('time', {})
            self.time_24h_check.setChecked(time_config.get('format_24h', True))
            self.time_seconds_check.setChecked(time_config.get('show_seconds', True))

            # 天气模块设置
            weather_config = modules_config.get('weather', {})
            self.weather_api_key_edit.setText(weather_config.get('api_key', ''))
            self.weather_city_edit.setText(weather_config.get('city', 'Beijing'))

            # 高级设置
            position = self.settings.get('position', {})
            self.x_spin.setValue(position.get('x', 0))
            self.y_spin.setValue(position.get('y', 10))

            self.animation_duration_spin.setValue(
                self.settings.get('animation_duration', 300)
            )

            # 交互设置
            self.mouse_transparent_check.setChecked(
                self.settings.get('mouse_transparent', True)
            )
            self.fixed_position_check.setChecked(
                self.settings.get('fixed_position', True)
            )
            self.auto_rotate_check.setChecked(
                self.settings.get('auto_rotate_content', True)
            )
            self.rotate_interval_spin.setValue(
                self.settings.get('rotation_interval', 5000) // 1000
            )

        except Exception as e:
            self.logger.error(f"加载当前设置失败: {e}")

    def choose_background_color(self) -> None:
        """选择背景颜色"""
        try:
            color = QColorDialog.getColor(QColor(50, 50, 50), self, "选择背景颜色")
            if color.isValid():
                self.background_color_btn.setStyleSheet(
                    f"background-color: {color.name()};"
                )
                # 保存颜色到临时设置
                if 'appearance' not in self.settings:
                    self.settings['appearance'] = {}
                self.settings.get('appearance')['background_color'] = color.name()

        except Exception as e:
            self.logger.error(f"选择背景颜色失败: {e}")

    def choose_text_color(self) -> None:
        """选择文字颜色"""
        try:
            color = QColorDialog.getColor(QColor(255, 255, 255), self, "选择文字颜色")
            if color.isValid():
                self.text_color_btn.setStyleSheet(
                    f"background-color: {color.name()};"
                )
                # 保存颜色到临时设置
                if 'appearance' not in self.settings:
                    self.settings['appearance'] = {}
                self.settings.get('appearance')['text_color'] = color.name()

        except Exception as e:
            self.logger.error(f"选择文字颜色失败: {e}")

    def choose_font(self) -> None:
        """选择字体"""
        try:
            current_font = QFont("Arial", 12)
            font, ok = QFontDialog.getFont(current_font, self, "选择字体")


            if ok:
                font_text = f"{font.family()}, {font.pointSize()}pt"
                if font.bold():
                    font_text += ", Bold"
                if font.italic():
                    font_text += ", Italic"

                self.font_label.setText(font_text)

                # 保存字体到临时设置
                if 'appearance' not in self.settings:
                    self.settings['appearance'] = {}
                self.settings.get('appearance')['font'] = {
                    'family': font.family(),
                    'size': font.pointSize(),
                    'bold': font.bold(),
                    'italic': font.italic()
                }

        except Exception as e:
            self.logger.error(f"选择字体失败: {e}")

    def on_theme_changed(self, theme_name: str) -> None:
        """处理主题变化"""
        try:
            # 启用/禁用自定义颜色按钮
            is_custom = theme_name == "自定义"
            self.background_color_btn.setEnabled(is_custom)
            self.text_color_btn.setEnabled(is_custom)

            # 如果不是自定义主题，应用预设颜色
            if not is_custom:
                if theme_name == "深色主题":
                    self.background_color_btn.setStyleSheet("background-color: #1e1e1e;")
                    self.text_color_btn.setStyleSheet("background-color: #ffffff;")
                elif theme_name == "浅色主题":
                    self.background_color_btn.setStyleSheet("background-color: #f0f0f0;")
                    self.text_color_btn.setStyleSheet("background-color: #333333;")
                else:  # 跟随系统
                    self.background_color_btn.setStyleSheet("")
                    self.text_color_btn.setStyleSheet("")

            # 实时预览主题变化
            if self.floating_widget and hasattr(self.floating_widget, 'apply_theme'):
                self.floating_widget.apply_theme()

        except Exception as e:
            self.logger.error(f"处理主题变化失败: {e}")

    def on_position_preset_changed(self, preset_name: str) -> None:
        """处理位置预设变化"""
        try:
            from PyQt6.QtWidgets import QApplication

            # 获取屏幕尺寸
            screen = QApplication.primaryScreen()
            if not screen:
                self.logger.warning("无法获取主屏幕信息")
                return

            screen_geometry = screen.availableGeometry()

            # 安全获取控件值
            try:
                widget_width = self.width_spin.value() if hasattr(self, 'width_spin') else 400
                widget_height = self.height_spin.value() if hasattr(self, 'height_spin') else 60
            except Exception as e:
                self.logger.warning(f"获取控件值失败: {e}")
                widget_width, widget_height = 400, 60

            # 计算预设位置
            if preset_name == "屏幕顶部居中":
                x = (screen_geometry.width() - widget_width) // 2
                y = 10
            elif preset_name == "屏幕顶部左侧":
                x = 10
                y = 10
            elif preset_name == "屏幕顶部右侧":
                x = screen_geometry.width() - widget_width - 10
                y = 10
            elif preset_name == "屏幕底部居中":
                x = (screen_geometry.width() - widget_width) // 2
                y = screen_geometry.height() - widget_height - 10
            else:  # 自定义位置
                return  # 不修改坐标

            # 安全更新坐标输入框
            try:
                if hasattr(self, 'x_spin'):
                    self.x_spin.setValue(x)
                if hasattr(self, 'y_spin'):
                    self.y_spin.setValue(y)
            except Exception as e:
                self.logger.warning(f"更新坐标输入框失败: {e}")

        except Exception as e:
            self.logger.error(f"位置预设变化处理失败: {e}")

            # 启用/禁用坐标输入框
            is_custom = preset_name == "自定义位置"
            self.x_spin.setEnabled(is_custom)
            self.y_spin.setEnabled(is_custom)

            # 实时预览位置变化
            if self.floating_widget:
                self.floating_widget.move(x, y)

        except Exception as e:
            self.logger.error(f"处理位置预设变化失败: {e}")

    def apply_settings(self) -> None:
        """应用设置"""
        try:
            # 收集设置
            new_settings = self.collect_settings()

            # 更新设置
            self.settings.update(new_settings)

            # 保存设置
            self.save_settings()

            # 发送应用信号
            self.settings_applied.emit(self.settings)

            # 应用到浮窗
            if self.floating_widget:
                self.apply_to_floating_widget()

            QMessageBox.information(self, "设置", "设置已应用")

        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用设置失败: {e}")

    def collect_settings(self) -> Dict[str, Any]:
        """收集所有设置"""
        try:
            settings = {}

            # 外观设置
            settings['width'] = self.width_spin.value()
            settings['height'] = self.height_spin.value()
            settings['border_radius'] = self.radius_spin.value()
            settings['opacity'] = self.opacity_slider.value() / 100.0
            settings['animation_duration'] = self.animation_duration_spin.value()

            # 位置设置
            settings['position'] = {
                'x': self.x_spin.value(),
                'y': self.y_spin.value()
            }

            # 交互设置
            settings['mouse_transparent'] = self.mouse_transparent_check.isChecked()
            settings['fixed_position'] = self.fixed_position_check.isChecked()
            settings['auto_rotate_content'] = self.auto_rotate_check.isChecked()
            settings['rotation_interval'] = self.rotate_interval_spin.value() * 1000

            # 模块设置
            modules_config = {}

            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                module_id = item.data(Qt.ItemDataRole.UserRole)
                enabled = item.checkState() == Qt.CheckState.Checked

                modules_config[module_id] = {
                    'enabled': enabled,
                    'order': i
                }

            # 时间模块特殊设置
            if 'time' in modules_config:
                modules_config.get('time').update({
                    'format_24h': self.time_24h_check.isChecked(),
                    'show_seconds': self.time_seconds_check.isChecked()
                })

            # 天气模块特殊设置
            if 'weather' in modules_config:
                modules_config.get('weather').update({
                    'api_key': self.weather_api_key_edit.text().strip(),
                    'city': self.weather_city_edit.text().strip()
                })

            settings['modules'] = modules_config

            # 合并外观设置
            if 'appearance' in self.settings:
                settings['appearance'] = self.settings.get('appearance')

            return settings

        except Exception as e:
            self.logger.error(f"收集设置失败: {e}")
            return {}

    def apply_to_floating_widget(self) -> None:
        """将设置应用到浮窗"""
        try:
            if not self.floating_widget:
                return

            # 应用透明度
            opacity = self.settings.get('opacity', 0.9)
            self.floating_widget.set_opacity(opacity)

            # 应用圆角半径
            radius = self.settings.get('border_radius', 30)
            self.floating_widget.set_border_radius(radius)

            # 应用大小
            width = self.settings.get('width', 400)
            height = self.settings.get('height', 60)
            self.floating_widget.setFixedSize(width, height)

            # 应用位置
            position = self.settings.get('position', {})
            if position:
                self.floating_widget.move(position.get('x', 0), position.get('y', 10))

            # 应用交互设置
            mouse_transparent = self.settings.get('mouse_transparent', True)
            self.floating_widget.set_mouse_transparent(mouse_transparent)

            fixed_position = self.settings.get('fixed_position', True)
            self.floating_widget.set_fixed_position(fixed_position)

            auto_rotate = self.settings.get('auto_rotate_content', True)
            rotation_interval = self.settings.get('rotation_interval', 5000)
            self.floating_widget.set_auto_rotate(auto_rotate, rotation_interval)

            # 强制刷新浮窗显示
            if hasattr(self.floating_widget, 'force_refresh_display'):
                self.floating_widget.force_refresh_display()
            else:
                # 兼容旧版本的方法
                # 应用模块配置
                modules_config = self.settings.get('modules', {})
                if modules_config:
                    # 更新浮窗的模块配置
                    self.floating_widget.config['modules'] = modules_config

                    # 重新初始化模块
                    if hasattr(self.floating_widget, 'reinitialize_modules'):
                        self.floating_widget.reinitialize_modules()

                # 重新加载配置
                self.floating_widget.load_config()

                # 应用主题
                self.floating_widget.apply_theme()

                # 强制更新显示
                self.floating_widget.update_display()

        except Exception as e:
            self.logger.error(f"应用设置到浮窗失败: {e}")

    def on_setting_changed(self) -> None:
        """设置变更时的回调，用于实时预览"""
        try:
            # 如果启用了实时预览，立即应用设置
            if hasattr(self, 'real_time_preview') and self.real_time_preview:
                self.apply_settings_preview()
        except Exception as e:
            self.logger.debug(f"实时预览更新失败: {e}")

    def apply_settings_preview(self) -> None:
        """应用设置预览（不保存到配置）"""
        try:
            if not self.floating_widget:
                return

            # 临时应用设置用于预览
            opacity = self.opacity_slider.value() / 100.0
            self.floating_widget.setWindowOpacity(opacity)

            width = self.width_spin.value()
            height = self.height_spin.value()
            self.floating_widget.setFixedSize(width, height)

            # 更新圆角半径（如果浮窗支持）
            if hasattr(self.floating_widget, 'set_border_radius'):
                radius = self.radius_spin.value()
                self.floating_widget.set_border_radius(radius)

        except Exception as e:
            self.logger.debug(f"预览应用失败: {e}")

    def refresh_preview(self) -> None:
        """刷新预览"""
        try:
            self.apply_settings_preview()
            QMessageBox.information(self, "预览", "预览已刷新")
        except Exception as e:
            self.logger.error(f"刷新预览失败: {e}")

    def test_position(self) -> None:
        """测试浮窗位置"""
        try:
            if not self.floating_widget:
                return

            # 临时移动到设置的位置
            x = self.x_spin.value() if hasattr(self, 'x_spin') else 0
            y = self.y_spin.value() if hasattr(self, 'y_spin') else 10

            self.floating_widget.move(x, y)
            self.floating_widget.show()

            QMessageBox.information(self, "位置测试", f"浮窗已移动到位置 ({x}, {y})")

        except Exception as e:
            self.logger.error(f"测试位置失败: {e}")

    def apply_preset(self, preset_id: str) -> None:
        """应用预设方案"""
        try:
            presets = {
                'minimal': {
                    'width': 300,
                    'height': 50,
                    'opacity': 85,
                    'border_radius': 25,
                    'modules': ['time']
                },
                'productivity': {
                    'width': 450,
                    'height': 65,
                    'opacity': 90,
                    'border_radius': 30,
                    'modules': ['time', 'schedule', 'system']
                },
                'comprehensive': {
                    'width': 600,
                    'height': 80,
                    'opacity': 95,
                    'border_radius': 35,
                    'modules': ['time', 'schedule', 'weather', 'system', 'countdown']
                },
                'gaming': {
                    'width': 250,
                    'height': 40,
                    'opacity': 70,
                    'border_radius': 20,
                    'modules': ['time']
                },
                'presentation': {
                    'width': 500,
                    'height': 90,
                    'opacity': 100,
                    'border_radius': 40,
                    'modules': ['time', 'schedule']
                }
            }


            if preset_id in presets:
                preset = presets[preset_id]

                preset = presets[preset_id]

                # 应用预设设置
                self.width_spin.setValue(preset.get('width'))
                self.height_spin.setValue(preset.get('height'))
                self.opacity_slider.setValue(preset.get('opacity'))
                self.radius_spin.setValue(preset.get('border_radius'))

                # 更新模块选择（如果模块列表存在）
                if hasattr(self, 'modules_list'):
                    for i in range(self.modules_list.count()):
                        item = self.modules_list.item(i)
                        module_id = item.data(Qt.ItemDataRole.UserRole)
                        if module_id in preset.get('modules'):
                            item.setCheckState(Qt.CheckState.Checked)
                        else:
                            item.setCheckState(Qt.CheckState.Unchecked)

                QMessageBox.information(self, "预设应用", f"已应用 {preset_id} 预设方案")

        except Exception as e:
            self.logger.error(f"应用预设失败: {e}")

    def save_custom_preset(self) -> None:
        """保存自定义预设"""
        try:
            name = self.preset_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "警告", "请输入预设方案名称")
                return

            # 收集当前设置
            current_settings = self.collect_settings()

            # 保存到配置（这里可以扩展为保存到文件或数据库）
            custom_presets = self.app_manager.config_manager.get_config('floating_widget.custom_presets', {})
            custom_presets[name] = current_settings
            self.app_manager.config_manager.set_config('floating_widget.custom_presets', custom_presets)

            QMessageBox.information(self, "保存成功", f"自定义预设 '{name}' 已保存")
            self.preset_name_edit.clear()

        except Exception as e:
            self.logger.error(f"保存自定义预设失败: {e}")

    def restore_defaults(self) -> None:
        """恢复默认设置"""
        try:
            reply = QMessageBox.question(
                self, "确认", "确定要恢复默认设置吗？这将清除所有自定义配置。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )


            if reply == QMessageBox.StandardButton.Yes:
                # 恢复默认值:

                # 恢复默认值
                self.width_spin.setValue(400)
                self.height_spin.setValue(60)
                self.opacity_slider.setValue(90)
                self.radius_spin.setValue(30)

                # 恢复其他默认设置...
                QMessageBox.information(self, "恢复完成", "已恢复默认设置")

        except Exception as e:
            self.logger.error(f"恢复默认设置失败: {e}")

    def accept_settings(self) -> None:
        """确定按钮处理"""
        try:
            self.apply_settings()
            self.accept()
        except Exception as e:
            self.logger.error(f"确定设置失败: {e}")

    def reject(self) -> None:
        """取消按钮处理"""
        try:
            # 恢复原始设置
            self.load_current_settings()
            super().reject()
        except Exception as e:
            self.logger.error(f"取消设置失败: {e}")
            super().reject()

    def on_module_item_changed(self, item: QListWidgetItem) -> None:
        """处理模块项状态变化"""
        try:
            module_id = item.data(Qt.ItemDataRole.UserRole)
            enabled = item.checkState() == Qt.CheckState.Checked

            self.logger.debug(f"模块 {module_id} 状态变化: {enabled}")

            # 实时预览功能（可选）
            if self.floating_widget and hasattr(self.floating_widget, 'modules'):
                if module_id in self.floating_widget.modules:
                    module = self.floating_widget.modules[module_id]
                    module.enabled = enabled

                    # 更新启用模块列表
                    if enabled and module_id not in self.floating_widget.enabled_modules:
                        self.floating_widget.enabled_modules.append(module_id)
                    elif not enabled and module_id in self.floating_widget.enabled_modules:
                        self.floating_widget.enabled_modules.remove(module_id)

                    # 重新排序
                    self.update_module_order()

        except Exception as e:
            self.logger.error(f"处理模块项变化失败: {e}")

    def on_module_selection_changed(self) -> None:
        """处理模块选择变化"""
        try:
            current_item = self.modules_list.currentItem()
            if current_item:
                module_id = current_item.data(Qt.ItemDataRole.UserRole)
                self.show_module_specific_settings(module_id)

        except Exception as e:
            self.logger.error(f"处理模块选择变化失败: {e}")

    def show_module_specific_settings(self, module_id: str) -> None:
        """显示特定模块的设置"""
        try:
            # 隐藏所有模块设置
            self.time_24h_check.setVisible(False)
            self.time_seconds_check.setVisible(False)
            self.weather_api_key_edit.setVisible(False)
            self.weather_city_edit.setVisible(False)

            # 显示对应模块的设置
            if module_id == 'time':
                self.time_24h_check.setVisible(True)
                self.time_seconds_check.setVisible(True)
            elif module_id == 'weather':
                self.weather_api_key_edit.setVisible(True)
                self.weather_city_edit.setVisible(True)

        except Exception as e:
            self.logger.error(f"显示模块设置失败: {e}")

    def update_module_order(self) -> None:
        """更新模块显示顺序"""
        try:
            if not self.floating_widget:
                return

            # 根据列表顺序更新模块顺序
            new_order = []
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                module_id = item.data(Qt.ItemDataRole.UserRole)
                if item.checkState() == Qt.CheckState.Checked:
                    new_order.append(module_id)

            self.floating_widget.module_order = new_order
            self.floating_widget.enabled_modules = new_order.copy()

            # 重新启动轮播定时器
            if hasattr(self.floating_widget, 'rotation_timer'):
                if self.floating_widget.auto_rotate_content and len(new_order) > 1:
                    self.floating_widget.rotation_timer.start(self.floating_widget.rotation_interval)
                else:
                    self.floating_widget.rotation_timer.stop()

            self.logger.debug(f"模块顺序已更新: {new_order}")

        except Exception as e:
            self.logger.error(f"更新模块顺序失败: {e}")

    def reset_to_defaults(self) -> None:
        """重置为默认设置"""
        try:
            reply = QMessageBox.question(
                self, "确认重置", "确定要重置所有设置为默认值吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 安全重置外观设置
                try:
                    if hasattr(self, 'opacity_slider'):
                        self.opacity_slider.setValue(90)
                    if hasattr(self, 'width_spin'):
                        self.width_spin.setValue(400)
                    if hasattr(self, 'height_spin'):
                        self.height_spin.setValue(60)
                    if hasattr(self, 'radius_spin'):
                        self.radius_spin.setValue(30)
                except Exception as e:
                    self.logger.warning(f"重置外观设置失败: {e}")

                # 安全重置模块设置
                try:
                    if hasattr(self, 'modules_list'):
                        for i in range(self.modules_list.count()):
                            item = self.modules_list.item(i)
                            if item:
                                module_id = item.data(Qt.ItemDataRole.UserRole)
                                # 默认启用时间和课程表模块
                                if module_id in ['time', 'schedule']:
                                    item.setCheckState(Qt.CheckState.Checked)
                                else:
                                    item.setCheckState(Qt.CheckState.Unchecked)
                except Exception as e:
                    self.logger.warning(f"重置模块设置失败: {e}")

                # 安全重置高级设置
                try:
                    if hasattr(self, 'animation_duration_spin'):
                        self.animation_duration_spin.setValue(300)
                    if hasattr(self, 'mouse_transparent_check'):
                        self.mouse_transparent_check.setChecked(True)
                    if hasattr(self, 'fixed_position_check'):
                        self.fixed_position_check.setChecked(True)
                    if hasattr(self, 'auto_rotate_check'):
                        self.auto_rotate_check.setChecked(True)
                    if hasattr(self, 'rotate_interval_spin'):
                        self.rotate_interval_spin.setValue(5)
                except Exception as e:
                    self.logger.warning(f"重置高级设置失败: {e}")

                QMessageBox.information(self, "重置完成", "设置已重置为默认值")

        except Exception as e:
            self.logger.error(f"重置设置失败: {e}")
            QMessageBox.critical(self, "错误", f"重置失败: {e}")

    def preview_settings(self) -> None:
        """预览设置效果"""
        try:
            if not self.floating_widget:
                QMessageBox.warning(self, "警告", "浮窗不可用，无法预览")
                return

            # 安全收集设置
            try:
                temp_settings = self.collect_settings()
            except Exception as e:
                self.logger.error(f"收集设置失败: {e}")
                QMessageBox.critical(self, "错误", f"收集设置失败: {e}")
                return

            # 安全应用透明度
            try:
                opacity = temp_settings.get('opacity', 0.9)
                if hasattr(self.floating_widget, 'set_opacity'):
                    self.floating_widget.set_opacity(opacity)
            except Exception as e:
                self.logger.warning(f"应用透明度失败: {e}")

            # 安全应用大小
            try:
                width = temp_settings.get('width', 400)
                height = temp_settings.get('height', 60)
                self.floating_widget.setFixedSize(width, height)
            except Exception as e:
                self.logger.warning(f"应用大小失败: {e}")

            # 安全应用圆角
            try:
                radius = temp_settings.get('border_radius', 30)
                if hasattr(self.floating_widget, 'set_border_radius'):
                    self.floating_widget.set_border_radius(radius)
            except Exception as e:
                self.logger.warning(f"应用圆角失败: {e}")

            # 安全应用交互设置
            try:
                mouse_transparent = temp_settings.get('mouse_transparent', False)
                if hasattr(self.floating_widget, 'set_mouse_transparent'):
                    self.floating_widget.set_mouse_transparent(mouse_transparent)
                    self.logger.info(f"应用鼠标穿透设置: {mouse_transparent}")
            except Exception as e:
                self.logger.warning(f"应用鼠标穿透设置失败: {e}")

            # 安全应用固定位置设置
            try:
                fixed_position = temp_settings.get('fixed_position', True)
                if hasattr(self.floating_widget, 'set_fixed_position'):
                    self.floating_widget.set_fixed_position(fixed_position)
                    self.logger.info(f"应用固定位置设置: {fixed_position}")
            except Exception as e:
                self.logger.warning(f"应用固定位置设置失败: {e}")

            # 安全应用自动轮播设置
            try:
                auto_rotate = temp_settings.get('auto_rotate_content', True)
                if hasattr(self.floating_widget, 'auto_rotate_content'):
                    self.floating_widget.auto_rotate_content = auto_rotate
                    self.logger.info(f"应用自动轮播设置: {auto_rotate}")
            except Exception as e:
                self.logger.warning(f"应用自动轮播设置失败: {e}")

            try:
                auto_rotate = temp_settings.get('auto_rotate_content', True)
                rotation_interval = temp_settings.get('rotation_interval', 5000)
                if hasattr(self.floating_widget, 'set_auto_rotate'):
                    self.floating_widget.set_auto_rotate(auto_rotate, rotation_interval)
            except Exception as e:
                self.logger.warning(f"应用自动轮播设置失败: {e}")

            QMessageBox.information(self, "预览", "设置预览已应用到浮窗")

        except Exception as e:
            self.logger.error(f"预览设置失败: {e}")
            QMessageBox.critical(self, "错误", f"预览失败: {e}")

    def export_settings(self) -> None:
        """导出设置"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json

            settings = self.collect_settings()

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出浮窗设置", "floating_widget_settings.json",
                "JSON文件 (*.json);;所有文件 (*)"
            )


            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)

                QMessageBox.information(self, "导出成功", f"设置已导出到: {file_path}")

        except Exception as e:
            self.logger.error(f"导出设置失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def import_settings(self) -> None:
        """导入设置"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json

            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入浮窗设置", "",
                "JSON文件 (*.json);;所有文件 (*)"
            )


            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_settings = json.load(f)

                # 验证设置格式
                if not isinstance(imported_settings, dict):
                    raise ValueError("无效的设置文件格式")

                # 应用导入的设置
                self.settings.update(imported_settings)
                self.load_current_settings()

                QMessageBox.information(self, "导入成功", "设置已导入，请点击应用生效")

        except Exception as e:
            self.logger.error(f"导入设置失败: {e}")
            QMessageBox.critical(self, "错误", f"导入失败: {e}")
