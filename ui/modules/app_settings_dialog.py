#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

        # 1. 通知设置选项卡
        self.notification_tab = self.create_notification_settings_tab()
        self.tab_widget.addTab(self.notification_tab, "🔔 通知设置")

        # 2. 主题设置选项卡
        self.theme_tab = self.create_theme_settings_tab()
        self.tab_widget.addTab(self.theme_tab, "🎨 主题设置")

        # 3. 时间校准选项卡
        self.time_tab = self.create_time_calibration_tab()
        self.tab_widget.addTab(self.time_tab, "⏰ 时间校准")

        # 4. 系统集成选项卡
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
            # 收集设置
            settings = {
                'floating_widget': {
                    'opacity': self.opacity_slider.value() / 100.0,
                    'width': self.width_spin.value(),
                    'height': self.height_spin.value(),
                    'mouse_transparent': self.mouse_transparent_check.isChecked(),
                    'always_on_top': self.always_on_top_check.isChecked()
                }
            }

            # 保存设置
            if self.app_manager and self.app_manager.config_manager:
                for category, data in settings.items():
                    self.app_manager.config_manager.set_config(category, data, 'component')

                self.app_manager.config_manager.save_all_configs()

                QMessageBox.information(self, "成功", "设置已应用")

        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用设置失败: {e}")

    def preview_settings(self):
        """预览设置"""
        QMessageBox.information(self, "预览", "设置预览功能正在开发中...")

    def reset_to_defaults(self):
        """重置为默认设置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "功能开发中", "重置功能正在开发中...")

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
                event.accept()  # 只关闭窗口，不退出程序
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()  # 只关闭窗口，不退出程序
            else:
                event.ignore()

        except Exception as e:
            self.logger.error(f"关闭处理失败: {e}")
            event.accept()  # 只关闭窗口，不退出程序
