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
时间校准对话框
提供时间校准功能的用户界面
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QProgressBar, QTextEdit, QCheckBox, QSpinBox,
    QFormLayout, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont


class TimeCalibrationDialog(QDialog):
    """时间校准对话框"""
    
    def __init__(self, app_manager, parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.calibration_service = None
        self.logger = logging.getLogger(f'{__name__}.TimeCalibrationDialog')
        
        self.setWindowTitle("时间校准")
        self.setFixedSize(600, 500)
        
        self.setup_ui()
        self.connect_signals()
        self.load_settings()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 当前时间显示
        current_time_group = QGroupBox("当前时间状态")
        current_time_layout = QFormLayout(current_time_group)
        
        self.local_time_label = QLabel("--:--:--")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.local_time_label.setFont(font)
        current_time_layout.addRow("本地时间:", self.local_time_label)
        
        self.calibrated_time_label = QLabel("--:--:--")
        self.calibrated_time_label.setFont(font)
        current_time_layout.addRow("校准时间:", self.calibrated_time_label)
        
        self.offset_label = QLabel("未校准")
        current_time_layout.addRow("时间偏差:", self.offset_label)
        
        self.sync_status_label = QLabel("未同步")
        current_time_layout.addRow("同步状态:", self.sync_status_label)
        
        layout.addWidget(current_time_group)
        
        # 校准设置
        settings_group = QGroupBox("校准设置")
        settings_layout = QFormLayout(settings_group)
        
        self.auto_calibration_checkbox = QCheckBox("启用自动校准")
        settings_layout.addRow("自动校准:", self.auto_calibration_checkbox)
        
        self.calibration_interval_spinbox = QSpinBox()
        self.calibration_interval_spinbox.setRange(1, 24)
        self.calibration_interval_spinbox.setValue(1)
        self.calibration_interval_spinbox.setSuffix(" 小时")
        settings_layout.addRow("校准间隔:", self.calibration_interval_spinbox)
        
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 60)
        self.timeout_spinbox.setValue(10)
        self.timeout_spinbox.setSuffix(" 秒")
        settings_layout.addRow("超时时间:", self.timeout_spinbox)
        
        layout.addWidget(settings_group)
        
        # 校准进度
        progress_group = QGroupBox("校准进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("准备就绪")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # 校准日志
        log_group = QGroupBox("校准日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.calibrate_button = QPushButton("开始校准")
        self.calibrate_button.clicked.connect(self.start_calibration)
        button_layout.addWidget(self.calibrate_button)
        
        self.stop_button = QPushButton("停止校准")
        self.stop_button.clicked.connect(self.stop_calibration)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 时间更新定时器
        self.time_update_timer = QTimer()
        self.time_update_timer.timeout.connect(self.update_time_display)
        self.time_update_timer.start(1000)  # 每秒更新
    
    def connect_signals(self):
        """连接信号"""
        try:
            # 获取时间校准服务
            if hasattr(self.app_manager, 'time_calibration_service') and self.app_manager.time_calibration_service:
                self.calibration_service = self.app_manager.time_calibration_service

                # 连接信号
                if hasattr(self.calibration_service, 'calibration_started'):
                    self.calibration_service.calibration_started.connect(self.on_calibration_started)
                if hasattr(self.calibration_service, 'calibration_progress'):
                    self.calibration_service.calibration_progress.connect(self.on_calibration_progress)
                if hasattr(self.calibration_service, 'calibration_completed'):
                    self.calibration_service.calibration_completed.connect(self.on_calibration_completed)
                if hasattr(self.calibration_service, 'time_sync_status_changed'):
                    self.calibration_service.time_sync_status_changed.connect(self.on_sync_status_changed)

                self.logger.info("时间校准服务信号连接成功")
            else:
                self.logger.warning("时间校准服务不可用，使用模拟模式")
                self.calibration_service = None

        except Exception as e:
            self.logger.error(f"连接信号失败: {e}")
            self.calibration_service = None
    
    def load_settings(self):
        """加载设置"""
        try:
            if self.calibration_service:
                # 加载当前设置
                self.auto_calibration_checkbox.setChecked(
                    self.calibration_service.auto_calibration_enabled
                )
                self.calibration_interval_spinbox.setValue(
                    self.calibration_service.auto_calibration_interval // 3600
                )
                self.timeout_spinbox.setValue(
                    self.calibration_service.calibration_timeout
                )
                
                # 更新状态显示
                self.update_sync_status()
                
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            if self.calibration_service:
                # 保存设置
                self.calibration_service.auto_calibration_enabled = self.auto_calibration_checkbox.isChecked()
                self.calibration_service.auto_calibration_interval = self.calibration_interval_spinbox.value() * 3600
                self.calibration_service.calibration_timeout = self.timeout_spinbox.value()
                
                # 重启自动校准
                if self.calibration_service.auto_calibration_enabled:
                    self.calibration_service.start_auto_calibration()
                else:
                    self.calibration_service.stop_auto_calibration()
                
                QMessageBox.information(self, "成功", "设置已保存")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")
    
    def start_calibration(self):
        """开始校准"""
        try:
            if self.calibration_service and hasattr(self.calibration_service, 'start_calibration'):
                if self.calibration_service.start_calibration():
                    self.add_log("开始时间校准...")
                else:
                    QMessageBox.warning(self, "警告", "校准已在进行中")
            else:
                # 模拟校准过程
                self.add_log("开始模拟时间校准...")
                self.on_calibration_started()

                # 模拟校准进度
                from PyQt6.QtCore import QTimer
                self.simulation_timer = QTimer()
                self.simulation_progress = 0
                self.simulation_timer.timeout.connect(self._simulate_calibration_progress)
                self.simulation_timer.start(100)  # 每100ms更新一次

        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动校准失败: {e}")

    def _simulate_calibration_progress(self):
        """模拟校准进度"""
        try:
            self.simulation_progress += 2
            self.on_calibration_progress(self.simulation_progress)

            if self.simulation_progress >= 100:
                self.simulation_timer.stop()
                # 模拟成功完成
                import random
                simulated_offset = random.uniform(-50, 50)  # 模拟偏移量
                self.on_calibration_completed(True, simulated_offset, "模拟校准完成")

        except Exception as e:
            self.logger.error(f"模拟校准进度失败: {e}")
    
    def stop_calibration(self):
        """停止校准"""
        try:
            # 这里可以添加停止校准的逻辑
            self.add_log("校准已停止")
            self.on_calibration_completed(False, 0.0, "用户取消")
        except Exception as e:
            self.logger.error(f"停止校准失败: {e}")
    
    def update_time_display(self):
        """更新时间显示"""
        try:
            from datetime import datetime
            
            # 更新本地时间
            local_time = datetime.now()
            self.local_time_label.setText(local_time.strftime("%H:%M:%S"))
            
            # 更新校准时间
            if self.calibration_service:
                calibrated_time = self.calibration_service.get_calibrated_time()
                self.calibrated_time_label.setText(calibrated_time.strftime("%H:%M:%S"))
                
                # 更新偏差显示
                offset = self.calibration_service.get_time_offset()
                if abs(offset) < 1:
                    self.offset_label.setText("< 1ms")
                    self.offset_label.setStyleSheet("color: green;")
                elif abs(offset) < 100:
                    self.offset_label.setText(f"{offset:.0f}ms")
                    self.offset_label.setStyleSheet("color: orange;")
                else:
                    self.offset_label.setText(f"{offset:.0f}ms")
                    self.offset_label.setStyleSheet("color: red;")
            else:
                self.calibrated_time_label.setText(local_time.strftime("%H:%M:%S"))
                self.offset_label.setText("服务不可用")
                self.offset_label.setStyleSheet("color: gray;")
                
        except Exception as e:
            self.logger.error(f"更新时间显示失败: {e}")
    
    def update_sync_status(self):
        """更新同步状态"""
        try:
            if self.calibration_service:
                is_synced = self.calibration_service.is_synchronized()
                if is_synced:
                    self.sync_status_label.setText("已同步")
                    self.sync_status_label.setStyleSheet("color: green;")
                else:
                    self.sync_status_label.setText("未同步")
                    self.sync_status_label.setStyleSheet("color: red;")
            else:
                self.sync_status_label.setText("服务不可用")
                self.sync_status_label.setStyleSheet("color: gray;")
                
        except Exception as e:
            self.logger.error(f"更新同步状态失败: {e}")
    
    def add_log(self, message: str):
        """添加日志"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            self.log_text.append(log_entry)
        except Exception as e:
            self.logger.error(f"添加日志失败: {e}")
    
    @pyqtSlot()
    def on_calibration_started(self):
        """校准开始"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在校准...")
        self.calibrate_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.add_log("时间校准已开始")
    
    @pyqtSlot(int, str)
    def on_calibration_progress(self, progress: int, status: str):
        """校准进度更新"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        self.add_log(f"进度 {progress}%: {status}")
    
    @pyqtSlot(bool, float, str)
    def on_calibration_completed(self, success: bool, offset: float, message: str):
        """校准完成"""
        self.progress_bar.setVisible(False)
        self.calibrate_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        
        if success:
            self.status_label.setText("校准完成")
            self.add_log(f"校准成功: {message}")
        else:
            self.status_label.setText("校准失败")
            self.add_log(f"校准失败: {message}")
        
        self.update_sync_status()
    
    @pyqtSlot(bool)
    def on_sync_status_changed(self, is_synced: bool):
        """同步状态变更"""
        self.update_sync_status()
        status = "已同步" if is_synced else "未同步"
        self.add_log(f"同步状态变更: {status}")
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            self.time_update_timer.stop()
            event.accept()
        except Exception as e:
            self.logger.error(f"关闭处理失败: {e}")
            event.accept()
