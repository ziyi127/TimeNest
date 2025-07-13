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
TimeNest 应用设置模块
集成浮窗设置、通知设置、主题设置、时间校准、系统集成等功能
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from functools import lru_cache
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QSlider, QColorDialog, QFontDialog,
    QMessageBox, QProgressBar, QTextEdit, QLineEdit, QFrame,
    QListWidget, QListWidgetItem, QSplitter, QScrollArea
)
from PyQt6.QtGui import QFont, QColor, QPalette


if TYPE_CHECKING:
    from core.app_manager import AppManager
else:
    from core.app_manager import AppManager


class AppSettingsDialog(QDialog):
    """应用设置主对话框"""
    
    # 信号定义
    settings_changed = pyqtSignal(str, dict)  # 设置类型, 设置数据
    theme_changed = pyqtSignal(str)  # 主题名称
    
    def __init__(self, app_manager: 'AppManager', parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.AppSettingsDialog')
        
        # 设置数据
        self.settings_data = {}
        self.temp_settings = {}  # 临时设置，用于预览
        
        self.setup_ui()
        self.load_settings()
        self.connect_signals()
        
        self.logger.info("应用设置模块初始化完成")
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("应用设置")
        self.setFixedSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 1. 浮窗设置选项卡
        self.floating_tab = self.create_floating_settings_tab()
        self.tab_widget.addTab(self.floating_tab, "🎈 浮窗设置")
        
        # 2. 通知设置选项卡
        self.notification_tab = self.create_notification_settings_tab()
        self.tab_widget.addTab(self.notification_tab, "🔔 通知设置")
        
        # 3. 主题设置选项卡
        self.theme_tab = self.create_theme_settings_tab()
        self.tab_widget.addTab(self.theme_tab, "🎨 主题设置")
        
        # 4. 时间校准选项卡
        self.time_tab = self.create_time_calibration_tab()
        self.tab_widget.addTab(self.time_tab, "⏰ 时间校准")
        
        # 5. 系统集成选项卡
        self.system_tab = self.create_system_integration_tab()
        self.tab_widget.addTab(self.system_tab, "⚙️ 系统集成")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览效果")
        self.preview_button.clicked.connect(self.preview_settings)
        button_layout.addWidget(self.preview_button)
        
        self.reset_button = QPushButton("重置默认")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept_settings)
        self.ok_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_floating_settings_tab(self) -> QWidget:
        """创建浮窗设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 外观设置
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QFormLayout(appearance_group)
        
        # 透明度
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(90)
        self.opacity_label = QLabel("90%")
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        appearance_layout.addRow("透明度:", opacity_layout)
        
        # 尺寸设置
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 800)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" px")
        size_layout.addWidget(QLabel("宽度:"))
        size_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(40, 200)
        self.height_spin.setValue(60)
        self.height_spin.setSuffix(" px")
        size_layout.addWidget(QLabel("高度:"))
        size_layout.addWidget(self.height_spin)
        appearance_layout.addRow("尺寸:", size_layout)
        
        # 圆角
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 50)
        self.border_radius_spin.setValue(30)
        self.border_radius_spin.setSuffix(" px")
        appearance_layout.addRow("圆角:", self.border_radius_spin)
        
        layout.addWidget(appearance_group)
        
        # 位置设置
        position_group = QGroupBox("位置设置")
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
        
        # 模块管理
        modules_group = QGroupBox("模块管理")
        modules_layout = QVBoxLayout(modules_group)
        
        self.modules_list = QListWidget()
        self.modules_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        
        # 添加模块项
        modules = [
            ("time", "时间显示", True),
            ("schedule", "课程表", True),
            ("weather", "天气信息", False),
            ("calendar", "日历", False),
            ("tasks", "任务提醒", False)
        ]
        
        for module_id, module_name, enabled in modules:
            item = QListWidgetItem(module_name)
            item.setData(Qt.ItemDataRole.UserRole, module_id)
            item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            self.modules_list.addItem(item)
        
        modules_layout.addWidget(QLabel("拖拽调整显示顺序，勾选启用模块:"))
        modules_layout.addWidget(self.modules_list)
        
        layout.addWidget(modules_group)
        
        # 交互设置
        interaction_group = QGroupBox("交互设置")
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
        
        return tab
    
    def create_notification_settings_tab(self) -> QWidget:
        """创建通知设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 通知方式
        method_group = QGroupBox("通知方式")
        method_layout = QFormLayout(method_group)
        
        self.desktop_notification_check = QCheckBox("桌面通知")
        self.desktop_notification_check.setChecked(True)
        method_layout.addRow(self.desktop_notification_check)
        
        self.sound_notification_check = QCheckBox("声音提醒")
        self.sound_notification_check.setChecked(True)
        method_layout.addRow(self.sound_notification_check)
        
        self.floating_notification_check = QCheckBox("浮窗提醒")
        self.floating_notification_check.setChecked(True)
        method_layout.addRow(self.floating_notification_check)
        
        self.email_notification_check = QCheckBox("邮件通知")
        method_layout.addRow(self.email_notification_check)
        
        layout.addWidget(method_group)
        
        # 声音设置
        sound_group = QGroupBox("声音设置")
        sound_layout = QFormLayout(sound_group)
        
        self.sound_scheme_combo = QComboBox()
        self.sound_scheme_combo.addItems(["默认", "轻柔", "清脆", "自定义"])
        sound_layout.addRow("声音方案:", self.sound_scheme_combo)
        
        self.sound_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.sound_volume_slider.setRange(0, 100)
        self.sound_volume_slider.setValue(70)
        self.sound_volume_label = QLabel("70%")
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.sound_volume_slider)
        volume_layout.addWidget(self.sound_volume_label)
        self.sound_volume_slider.valueChanged.connect(lambda v: self.sound_volume_label.setText(f"{v}%"))
        sound_layout.addRow("音量:", volume_layout)
        
        layout.addWidget(sound_group)
        
        # 提醒频率
        frequency_group = QGroupBox("提醒频率")
        frequency_layout = QFormLayout(frequency_group)
        
        self.reminder_advance_spin = QSpinBox()
        self.reminder_advance_spin.setRange(1, 60)
        self.reminder_advance_spin.setValue(10)
        self.reminder_advance_spin.setSuffix(" 分钟")
        frequency_layout.addRow("提前提醒:", self.reminder_advance_spin)
        
        self.repeat_reminder_check = QCheckBox("重复提醒")
        frequency_layout.addRow(self.repeat_reminder_check)
        
        self.repeat_interval_spin = QSpinBox()
        self.repeat_interval_spin.setRange(1, 30)
        self.repeat_interval_spin.setValue(5)
        self.repeat_interval_spin.setSuffix(" 分钟")
        self.repeat_interval_spin.setEnabled(False)
        frequency_layout.addRow("重复间隔:", self.repeat_interval_spin)
        
        self.repeat_reminder_check.toggled.connect(self.repeat_interval_spin.setEnabled)
        
        layout.addWidget(frequency_group)
        
        # 免打扰设置
        dnd_group = QGroupBox("免打扰设置")
        dnd_layout = QFormLayout(dnd_group)
        
        self.dnd_enabled_check = QCheckBox("启用免打扰模式")
        dnd_layout.addRow(self.dnd_enabled_check)
        
        self.dnd_schedule_check = QCheckBox("按时间段免打扰")
        dnd_layout.addRow(self.dnd_schedule_check)
        
        # 免打扰时间段
        dnd_time_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QTimeEdit
        from PyQt6.QtCore import QTime
        
        self.dnd_start_time = QTimeEdit()
        self.dnd_start_time.setTime(QTime(22, 0))
        dnd_time_layout.addWidget(QLabel("从:"))
        dnd_time_layout.addWidget(self.dnd_start_time)
        
        self.dnd_end_time = QTimeEdit()
        self.dnd_end_time.setTime(QTime(8, 0))
        dnd_time_layout.addWidget(QLabel("到:"))
        dnd_time_layout.addWidget(self.dnd_end_time)
        
        dnd_layout.addRow("时间段:", dnd_time_layout)
        
        layout.addWidget(dnd_group)
        
        return tab
    
    def create_theme_settings_tab(self) -> QWidget:
        """创建主题设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 主题选择
        theme_group = QGroupBox("主题选择")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["跟随系统", "浅色主题", "深色主题", "自定义"])
        theme_layout.addRow("主题:", self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # 颜色设置
        color_group = QGroupBox("颜色设置")
        color_layout = QFormLayout(color_group)
        
        # 背景色
        self.bg_color_button = QPushButton("选择背景色")
        self.bg_color_button.clicked.connect(self.choose_background_color)
        self.bg_color_button.setStyleSheet("background-color: #f0f0f0;")
        color_layout.addRow("背景色:", self.bg_color_button)
        
        # 文字色
        self.text_color_button = QPushButton("选择文字色")
        self.text_color_button.clicked.connect(self.choose_text_color)
        self.text_color_button.setStyleSheet("background-color: #333333; color: white;")
        color_layout.addRow("文字色:", self.text_color_button)
        
        # 强调色
        self.accent_color_button = QPushButton("选择强调色")
        self.accent_color_button.clicked.connect(self.choose_accent_color)
        self.accent_color_button.setStyleSheet("background-color: #2196F3; color: white;")
        color_layout.addRow("强调色:", self.accent_color_button)
        
        layout.addWidget(color_group)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout(font_group)
        
        self.font_button = QPushButton("选择字体")
        self.font_button.clicked.connect(self.choose_font)
        font_layout.addRow("字体:", self.font_button)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(12)
        font_layout.addRow("字体大小:", self.font_size_spin)
        
        layout.addWidget(font_group)
        
        # 主题预览
        preview_group = QGroupBox("主题预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.theme_preview_label = QLabel("这是主题预览文本\nTimeNest 智能浮窗")
        self.theme_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.theme_preview_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                color: #333333;
                padding: 20px;
                border-radius: 10px;
                font-size: 14px;
            }
        """)
        preview_layout.addWidget(self.theme_preview_label)
        
        layout.addWidget(preview_group)
        
        return tab

    def create_time_calibration_tab(self) -> QWidget:
        """创建时间校准选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 自动校准设置
        auto_group = QGroupBox("自动校准设置")
        auto_layout = QFormLayout(auto_group)

        self.auto_calibration_check = QCheckBox("启用自动校准")
        auto_layout.addRow(self.auto_calibration_check)

        self.calibration_interval_spin = QSpinBox()
        self.calibration_interval_spin.setRange(1, 24)
        self.calibration_interval_spin.setValue(6)
        self.calibration_interval_spin.setSuffix(" 小时")
        auto_layout.addRow("校准间隔:", self.calibration_interval_spin)

        layout.addWidget(auto_group)

        # 手动校准
        manual_group = QGroupBox("手动校准")
        manual_layout = QVBoxLayout(manual_group)

        self.calibrate_button = QPushButton("立即校准")
        self.calibrate_button.clicked.connect(self.start_manual_calibration)
        manual_layout.addWidget(self.calibrate_button)

        self.calibration_progress = QProgressBar()
        self.calibration_progress.setVisible(False)
        manual_layout.addWidget(self.calibration_progress)

        self.calibration_status = QLabel("点击上方按钮开始校准")
        manual_layout.addWidget(self.calibration_status)

        layout.addWidget(manual_group)

        return tab

    def create_system_integration_tab(self) -> QWidget:
        """创建系统集成选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QFormLayout(startup_group)

        self.auto_start_check = QCheckBox("开机自动启动")
        startup_layout.addRow(self.auto_start_check)

        self.start_minimized_check = QCheckBox("启动时最小化到托盘")
        self.start_minimized_check.setChecked(True)
        startup_layout.addRow(self.start_minimized_check)

        layout.addWidget(startup_group)

        # 托盘设置
        tray_group = QGroupBox("系统托盘")
        tray_layout = QFormLayout(tray_group)

        self.show_tray_icon_check = QCheckBox("显示托盘图标")
        self.show_tray_icon_check.setChecked(True)
        tray_layout.addRow(self.show_tray_icon_check)

        self.minimize_to_tray_check = QCheckBox("最小化到托盘")
        self.minimize_to_tray_check.setChecked(True)
        tray_layout.addRow(self.minimize_to_tray_check)

        layout.addWidget(tray_group)

        return tab

    def load_settings(self):
        """加载设置"""
        try:
            if self.app_manager and self.app_manager.config_manager:
                # 加载各种设置:
                # 加载各种设置
                floating_settings = self.app_manager.config_manager.get_config('floating_widget', {}, 'component')

                # 应用到界面
                if floating_settings:
                    self.opacity_slider.setValue(int(floating_settings.get('opacity', 0.9) * 100))
                    self.width_spin.setValue(floating_settings.get('width', 400))
                    self.height_spin.setValue(floating_settings.get('height', 60))

        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")

    def connect_signals(self):
        """连接信号"""
        try:
            # 主题变化
            self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

        except Exception as e:
            self.logger.error(f"连接信号失败: {e}")

    def on_theme_changed(self, theme_name):
        """主题变化处理"""
        try:
            # 更新预览
            if theme_name == "深色主题":
                self.theme_preview_label.setStyleSheet("""
                    QLabel {
                        background-color: #2b2b2b;
                        color: #ffffff;
                        padding: 20px;
                        border-radius: 10px;
                        font-size: 14px;
                    }
                """)
            elif theme_name == "浅色主题":
                self.theme_preview_label.setStyleSheet("""
                    QLabel {
                        background-color: #f0f0f0;
                        color: #333333;
                        padding: 20px;
                        border-radius: 10px;
                        font-size: 14px;
                    }
                """)

        except Exception as e:
            self.logger.error(f"处理主题变化失败: {e}")

    # 颜色选择方法
    def choose_background_color(self):
        """选择背景色"""
        color = QColorDialog.getColor(QColor("#f0f0f0"), self, "选择背景色")
        if color.isValid():
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()};")
            self.bg_color_button.setText(color.name())
            self.update_theme_preview()

    def choose_text_color(self):
        """选择文字色"""
        color = QColorDialog.getColor(QColor("#333333"), self, "选择文字色")
        if color.isValid():
            self.text_color_button.setStyleSheet(f"background-color: {color.name()}; color: white;")
            self.text_color_button.setText(color.name())
            self.update_theme_preview()

    def choose_accent_color(self):
        """选择强调色"""
        color = QColorDialog.getColor(QColor("#2196F3"), self, "选择强调色")
        if color.isValid():
            self.accent_color_button.setStyleSheet(f"background-color: {color.name()}; color: white;")
            self.accent_color_button.setText(color.name())
            self.update_theme_preview()

    def choose_font(self):
        """选择字体"""
        font, ok = QFontDialog.getFont(QFont("Arial", 12), self, "选择字体")
        if ok:
            self.font_button.setText(f"{font.family()} {font.pointSize()}pt")
            self.font_size_spin.setValue(font.pointSize())
            self.update_theme_preview()

    def update_theme_preview(self):
        """更新主题预览"""
        try:
            # 获取当前颜色设置
            bg_color = self.bg_color_button.text() if hasattr(self.bg_color_button, 'text') and self.bg_color_button.text().startswith('#') else "#f0f0f0"
            text_color = self.text_color_button.text() if hasattr(self.text_color_button, 'text') and self.text_color_button.text().startswith('#') else "#333333"
            accent_color = self.accent_color_button.text() if hasattr(self.accent_color_button, 'text') and self.accent_color_button.text().startswith('#') else "#2196F3"

            # 获取字体设置
            font_size = self.font_size_spin.value()

            # 应用到预览标签
            preview_style = f"""
                QLabel {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 2px solid {accent_color};
                    padding: 20px;
                    border-radius: 10px;
                    font-size: {font_size}px;
                }}
            """

            self.theme_preview_label.setStyleSheet(preview_style)

        except Exception as e:
            self.logger.error(f"更新主题预览失败: {e}")

    def start_manual_calibration(self):
        """开始手动校准"""
        try:
            if not self.app_manager or not self.app_manager.time_calibration_service:
                QMessageBox.warning(self, "警告", "时间校准服务不可用")
                return

            # 显示进度条和状态
            self.calibration_progress.setVisible(True)
            self.calibration_progress.setValue(0)
            self.calibration_status.setText("正在校准...")
            self.calibrate_button.setEnabled(False)

            # 连接校准服务信号
            calibration_service = self.app_manager.time_calibration_service

            # 断开之前的连接（避免重复连接）
            try:
                calibration_service.calibration_progress.disconnect()
                calibration_service.calibration_completed.disconnect()
            except:
                pass

            # 连接新的信号
            calibration_service.calibration_progress.connect(self.on_calibration_progress)
            calibration_service.calibration_completed.connect(self.on_calibration_completed)

            # 开始校准
            calibration_service.start_calibration()

        except Exception as e:
            self.logger.error(f"开始校准失败: {e}")
            QMessageBox.critical(self, "错误", f"校准失败: {e}")
            self.calibrate_button.setEnabled(True)
            self.calibration_progress.setVisible(False)

    def on_calibration_progress(self, value, status):
        """校准进度更新"""
        try:
            self.calibration_progress.setValue(value)
            self.calibration_status.setText(status)
        except Exception as e:
            self.logger.error(f"更新校准进度失败: {e}")

    def on_calibration_completed(self, success, offset, message):
        """校准完成"""
        try:
            self.calibration_progress.setVisible(False)
            self.calibrate_button.setEnabled(True)


            if success:
                self.calibration_status.setText(f"校准成功: {message}")

                # 添加到历史记录
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_item = f"{timestamp} - 偏移: {offset:+.3f}秒"

                # 插入到历史列表顶部
                if hasattr(self, 'calibration_history'):
                    self.calibration_history.insertItem(0, history_item)

                    # 限制历史记录数量
                    while self.calibration_history.count() > 10:
                        self.calibration_history.takeItem(self.calibration_history.count() - 1)

                QMessageBox.information(self, "校准成功", message)
            else:
                self.calibration_status.setText(f"校准失败: {message}")
                QMessageBox.warning(self, "校准失败", message)

        except Exception as e:
            self.logger.error(f"处理校准完成失败: {e}")

    def apply_settings(self):
        """应用设置"""
        try:
            # 收集所有设置
            settings = self._collect_all_settings()

            # 保存设置到配置管理器
            if self.app_manager and self.app_manager.config_manager:
                self._save_settings_to_config(settings)

                # 立即应用设置到相关组件
                self._apply_settings_to_components(settings)

                QMessageBox.information(self, "成功", "设置已应用并生效")
                self.logger.info("设置已成功应用")

        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用设置失败: {e}")

    def _collect_all_settings(self) -> Dict[str, Any]:
        """收集所有设置"""
        try:
            # 获取已启用模块
            enabled_modules = []
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    module_id = item.data(Qt.ItemDataRole.UserRole)
                    if module_id:
                        enabled_modules.append(module_id)

            settings = {
                # 浮窗设置
                'floating_widget': {
                    'enabled': True,
                    'width': self.width_spin.value(),
                    'height': self.height_spin.value(),
                    'opacity': self.opacity_slider.value() / 100.0,
                    'border_radius': getattr(self, 'radius_slider', None).value() if hasattr(self, 'radius_slider') else 30,
                    'mouse_transparent': self.mouse_transparent_check.isChecked(),
                    'always_on_top': self.always_on_top_check.isChecked(),
                    'auto_hide': self.auto_hide_check.isChecked(),
                    'enabled_modules': enabled_modules,
                    'position': self._get_position_setting()
                },
                # 通知设置
                'notification': {
                    'enabled': getattr(self, 'notification_enabled_check', None).isChecked() if hasattr(self, 'notification_enabled_check') else True,
                    'sound_enabled': getattr(self, 'sound_enabled_check', None).isChecked() if hasattr(self, 'sound_enabled_check') else True,
                    'voice_enabled': getattr(self, 'voice_enabled_check', None).isChecked() if hasattr(self, 'voice_enabled_check') else False,
                    'popup_enabled': getattr(self, 'popup_enabled_check', None).isChecked() if hasattr(self, 'popup_enabled_check') else True,
                    'advance_minutes': getattr(self, 'advance_minutes_spin', None).value() if hasattr(self, 'advance_minutes_spin') else 5
                },
                # 主题设置
                'theme': {
                    'name': getattr(self, 'theme_combo', None).currentText() if hasattr(self, 'theme_combo') else 'default',
                    'auto_switch': getattr(self, 'auto_theme_check', None).isChecked() if hasattr(self, 'auto_theme_check') else False
                },
                # 时间校准设置
                'time': {
                    'offset_enabled': getattr(self, 'time_offset_check', None).isChecked() if hasattr(self, 'time_offset_check') else False,
                    'offset_minutes': getattr(self, 'time_offset_spin', None).value() if hasattr(self, 'time_offset_spin') else 0,
                    'speed_factor': getattr(self, 'time_speed_spin', None).value() if hasattr(self, 'time_speed_spin') else 1.0
                },
                # 系统集成设置
                'system': {
                    'auto_start': getattr(self, 'auto_start_check', None).isChecked() if hasattr(self, 'auto_start_check') else False,
                    'minimize_to_tray': getattr(self, 'minimize_tray_check', None).isChecked() if hasattr(self, 'minimize_tray_check') else True,
                    'check_updates': getattr(self, 'check_updates_check', None).isChecked() if hasattr(self, 'check_updates_check') else True
                }
            }

            return settings

        except Exception as e:
            self.logger.error(f"收集设置失败: {e}")
            return {}

    def _get_position_setting(self) -> str:
        """获取位置设置"""
        try:
            if hasattr(self, 'position_group'):
                checked_id = self.position_group.checkedId()
                position_map = {0: 'top_center', 1: 'top_left', 2: 'top_right', 3: 'custom'}
                return position_map.get(checked_id, 'top_center')
            return 'top_center'
        except Exception:
            return 'top_center'

    def _save_settings_to_config(self, settings: Dict[str, Any]):
        """保存设置到配置文件"""
        try:
            config_manager = self.app_manager.config_manager

            # 保存到主配置
            for category, data in settings.items():
                config_manager.set_config(category, data, 'main', save=False)

            # 一次性保存所有配置
            config_manager.save_all_configs()
            self.logger.info("设置已保存到配置文件")

        except Exception as e:
            self.logger.error(f"保存设置到配置文件失败: {e}")
            raise

    def _apply_settings_to_components(self, settings: Dict[str, Any]):
        """立即应用设置到相关组件"""
        try:
            # 应用浮窗设置
            if 'floating_widget' in settings and self.app_manager.floating_manager:
                floating_config = settings['floating_widget']
                self.app_manager.floating_manager.apply_config(floating_config)

            # 应用通知设置
            if 'notification' in settings and self.app_manager.notification_manager:
                notification_config = settings['notification']
                self.app_manager.notification_manager.apply_config(notification_config)

            # 应用主题设置
            if 'theme' in settings and self.app_manager.theme_manager:
                theme_config = settings['theme']
                if 'name' in theme_config:
                    self.app_manager.theme_manager.set_theme(theme_config['name'])

            # 应用时间校准设置
            if 'time' in settings and hasattr(self.app_manager, 'time_manager'):
                time_config = settings['time']
                if hasattr(self.app_manager.time_manager, 'apply_config'):
                    self.app_manager.time_manager.apply_config(time_config)

            self.logger.info("设置已应用到相关组件")

        except Exception as e:
            self.logger.error(f"应用设置到组件失败: {e}")
            # 不抛出异常，因为保存已经成功

    def preview_settings(self):
        """预览设置"""
        try:
            # 收集当前设置
            settings = self._collect_all_settings()

            # 创建预览浮窗
            if hasattr(self, 'preview_widget') and self.preview_widget:
                self.preview_widget.close()
                self.preview_widget = None

            # 临时应用设置进行预览
            if self.app_manager.floating_manager:
                # 保存当前配置
                self.original_config = self.app_manager.floating_manager.get_current_config()

                # 应用预览配置
                floating_config = settings.get('floating_widget', {})
                self.app_manager.floating_manager.apply_config(floating_config)

                # 显示预览提示
                QMessageBox.information(
                    self,
                    "预览模式",
                    "预览效果已应用到浮窗。\n点击'应用'保存设置，或点击'取消'恢复原设置。"
                )

                self.logger.info("设置预览已应用")
            else:
                QMessageBox.warning(self, "预览失败", "浮窗管理器不可用，无法预览设置")

        except Exception as e:
            self.logger.error(f"预览设置失败: {e}")
            QMessageBox.critical(self, "预览失败", f"预览设置时发生错误: {e}")

    def reset_to_defaults(self):
        """重置为默认设置"""
        try:
            reply = QMessageBox.question(
                self, "确认重置",
                "确定要重置所有设置为默认值吗？\n这将清除您的所有自定义设置。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 获取默认配置
                default_config = self._get_default_settings()

                # 重置界面控件
                self._reset_ui_to_defaults(default_config)

                # 保存默认配置
                if self.app_manager and self.app_manager.config_manager:
                    self._save_settings_to_config(default_config)
                    self._apply_settings_to_components(default_config)

                QMessageBox.information(self, "重置完成", "所有设置已重置为默认值")
                self.logger.info("设置已重置为默认值")

        except Exception as e:
            self.logger.error(f"重置设置失败: {e}")
            QMessageBox.critical(self, "重置失败", f"重置设置时发生错误: {e}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            'floating_widget': {
                'enabled': True,
                'width': 400,
                'height': 60,
                'opacity': 0.9,
                'border_radius': 30,
                'mouse_transparent': False,
                'always_on_top': True,
                'auto_hide': False,
                'enabled_modules': ['time', 'schedule'],
                'position': 'top_center'
            },
            'notification': {
                'enabled': True,
                'sound_enabled': True,
                'voice_enabled': False,
                'popup_enabled': True,
                'advance_minutes': 5
            },
            'theme': {
                'name': 'default',
                'auto_switch': False
            },
            'time': {
                'offset_enabled': False,
                'offset_minutes': 0,
                'speed_factor': 1.0
            },
            'system': {
                'auto_start': False,
                'minimize_to_tray': True,
                'check_updates': True
            }
        }

    def _reset_ui_to_defaults(self, default_config: Dict[str, Any]):
        """重置界面控件为默认值"""
        try:
            # 重置浮窗设置
            floating_config = default_config.get('floating_widget', {})
            self.width_spin.setValue(floating_config.get('width', 400))
            self.height_spin.setValue(floating_config.get('height', 60))
            self.opacity_slider.setValue(int(floating_config.get('opacity', 0.9) * 100))
            self.mouse_transparent_check.setChecked(floating_config.get('mouse_transparent', False))
            self.always_on_top_check.setChecked(floating_config.get('always_on_top', True))
            self.auto_hide_check.setChecked(floating_config.get('auto_hide', False))

            # 重置模块列表
            enabled_modules = floating_config.get('enabled_modules', ['time', 'schedule'])
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                module_id = item.data(Qt.ItemDataRole.UserRole)
                item.setCheckState(
                    Qt.CheckState.Checked if module_id in enabled_modules else Qt.CheckState.Unchecked
                )

            # 重置其他设置控件
            if hasattr(self, 'notification_enabled_check'):
                notification_config = default_config.get('notification', {})
                self.notification_enabled_check.setChecked(notification_config.get('enabled', True))

            if hasattr(self, 'auto_start_check'):
                system_config = default_config.get('system', {})
                self.auto_start_check.setChecked(system_config.get('auto_start', False))

            self.logger.info("界面控件已重置为默认值")

        except Exception as e:
            self.logger.error(f"重置界面控件失败: {e}")

    def accept_settings(self):
        """确定并应用设置"""
        try:
            self.apply_settings()
            self.accept()
        except Exception as e:
            self.logger.error(f"确定设置失败: {e}")

    def reject(self):
        """取消设置"""
        try:
            # 如果有预览配置，恢复原始配置
            if hasattr(self, 'original_config') and self.original_config:
                if self.app_manager.floating_manager:
                    self.app_manager.floating_manager.apply_config(self.original_config)
                    self.logger.info("已恢复原始配置")

            super().reject()
        except Exception as e:
            self.logger.error(f"取消设置失败: {e}")
            super().reject()

    def closeEvent(self, event):
        """关闭事件处理"""
        try:
            # 如果有预览配置，恢复原始配置
            if hasattr(self, 'original_config') and self.original_config:
                if self.app_manager.floating_manager:
                    self.app_manager.floating_manager.apply_config(self.original_config)
                    self.logger.info("关闭时已恢复原始配置")

            super().closeEvent(event)
        except Exception as e:
            self.logger.error(f"关闭事件处理失败: {e}")
            super().closeEvent(event)

    def accept_settings(self):
        """确定并关闭"""
        self.apply_settings()
        self.accept()

    def closeEvent(self, event):
        """关闭事件 - 只关闭窗口，不退出程序"""
        try:
            # 询问是否保存设置
            reply = QMessageBox.question(
                self, "确认关闭", "是否保存设置后关闭？",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )


            if reply == QMessageBox.StandardButton.Save:
                self.apply_settings()

                self.apply_settings()
                event.accept()  # 只关闭窗口，不退出程序
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()  # 只关闭窗口，不退出程序
            else:
                event.ignore()

        except Exception as e:
            self.logger.error(f"关闭处理失败: {e}")
            event.accept()  # 只关闭窗口，不退出程序
