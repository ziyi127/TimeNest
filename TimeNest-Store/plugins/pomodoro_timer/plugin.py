#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
番茄钟插件
专业的番茄工作法计时器
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QProgressBar)

# 导入插件基类
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from core.plugin_base import IPlugin, PluginStatus


class PomodoroWidget(QWidget):
    """番茄钟显示组件"""
    
    def __init__(self, plugin_instance):
        super().__init__()
        self.plugin = plugin_instance
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 状态显示
        self.status_label = QLabel("准备开始")
        self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 时间显示
        self.time_label = QLabel("25:00")
        self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.start_button.clicked.connect(self.plugin.start_timer)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("暂停")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.pause_button.clicked.connect(self.plugin.pause_timer)
        button_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.reset_button.clicked.connect(self.plugin.reset_timer)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # 周期计数
        self.cycle_label = QLabel("周期: 0/4")
        self.cycle_label.setStyleSheet("font-size: 9px; color: #666;")
        self.cycle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cycle_label)
    
    def update_display(self, status: str, time_left: int, total_time: int, cycle_count: int, max_cycles: int):
        """更新显示"""
        # 状态
        self.status_label.setText(status)
        
        # 时间
        minutes = time_left // 60
        seconds = time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        # 进度
        if total_time > 0:
            progress = int((total_time - time_left) / total_time * 100)
            self.progress_bar.setValue(progress)
        
        # 周期
        self.cycle_label.setText(f"周期: {cycle_count}/{max_cycles}")
        
        # 根据状态调整颜色
        if "工作" in status:
            self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 8px;
                }
                QProgressBar::chunk {
                    background-color: #e74c3c;
                    border-radius: 2px;
                }
            """)
        else:
            self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                    height: 8px;
                }
                QProgressBar::chunk {
                    background-color: #27ae60;
                    border-radius: 2px;
                }
            """)


class PomodoroTimerPlugin(IPlugin):
    """番茄钟插件"""
    
    # 定义信号
    timer_updated = pyqtSignal(str, int, int, int, int)  # status, time_left, total_time, cycle, max_cycles
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PomodoroTimerPlugin')
        
        # 插件状态
        self.status = PluginStatus.LOADED
        
        # 组件
        self.timer_widget = None
        self.timer = None
        self.plugin_manager = None
        
        # 计时器状态
        self.is_running = False
        self.is_work_time = True
        self.time_left = 0
        self.total_time = 0
        self.cycle_count = 0
        
        # 设置
        self.settings = {
            'work_duration': 25,
            'short_break': 5,
            'long_break': 15,
            'cycles_before_long_break': 4,
            'auto_start_breaks': False,
            'auto_start_work': False,
            'sound_enabled': True,
            'notification_enabled': True,
            'show_in_floating': True
        }
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.logger.info("番茄钟插件初始化开始")
            
            # 创建计时器组件
            self.timer_widget = PomodoroWidget(self)
            
            # 创建定时器
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_timer)
            
            # 连接信号
            self.timer_updated.connect(self.timer_widget.update_display)
            
            # 初始化计时器
            self.reset_timer()
            
            self.status = PluginStatus.INITIALIZED
            self.logger.info("番茄钟插件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            if self.status != PluginStatus.INITIALIZED:
                self.logger.error("插件未正确初始化")
                return False
            
            self.status = PluginStatus.ENABLED
            self.logger.info("番茄钟插件已激活")
            return True
            
        except Exception as e:
            self.logger.error(f"插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            # 停止计时器
            if self.timer and self.timer.isActive():
                self.timer.stop()
            
            self.is_running = False
            self.status = PluginStatus.DISABLED
            self.logger.info("番茄钟插件已停用")
            return True
            
        except Exception as e:
            self.logger.error(f"插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理插件资源"""
        try:
            # 停用插件
            self.deactivate()
            
            # 清理组件
            if self.timer_widget:
                self.timer_widget.deleteLater()
                self.timer_widget = None
            
            if self.timer:
                self.timer.deleteLater()
                self.timer = None
            
            self.status = PluginStatus.UNLOADED
            self.logger.info("番茄钟插件资源清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
            return False
    
    def start_timer(self):
        """开始计时"""
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)  # 每秒更新
            self.logger.info("番茄钟开始计时")
    
    def pause_timer(self):
        """暂停计时"""
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.logger.info("番茄钟暂停计时")
    
    def reset_timer(self):
        """重置计时器"""
        self.is_running = False
        if self.timer:
            self.timer.stop()
        
        # 重置为工作时间
        self.is_work_time = True
        self.time_left = self.settings['work_duration'] * 60
        self.total_time = self.time_left
        
        self.update_display()
        self.logger.info("番茄钟已重置")
    
    def update_timer(self):
        """更新计时器"""
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
        else:
            # 时间到了
            self.timer_finished()
    
    def timer_finished(self):
        """计时结束"""
        self.timer.stop()
        self.is_running = False
        
        if self.is_work_time:
            # 工作时间结束，开始休息
            self.cycle_count += 1
            
            # 判断是长休息还是短休息
            if self.cycle_count % self.settings['cycles_before_long_break'] == 0:
                # 长休息
                self.time_left = self.settings['long_break'] * 60
                status = "长休息时间"
            else:
                # 短休息
                self.time_left = self.settings['short_break'] * 60
                status = "短休息时间"
            
            self.is_work_time = False
            self.total_time = self.time_left
            
            # 发送通知
            self.send_notification("工作时间结束", f"开始{status}！")
            
            # 自动开始休息
            if self.settings['auto_start_breaks']:
                self.start_timer()
        else:
            # 休息时间结束，开始工作
            self.time_left = self.settings['work_duration'] * 60
            self.total_time = self.time_left
            self.is_work_time = True
            
            # 发送通知
            self.send_notification("休息时间结束", "开始新的工作周期！")
            
            # 自动开始工作
            if self.settings['auto_start_work']:
                self.start_timer()
        
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        if self.is_work_time:
            status = "工作时间" if self.is_running else "准备工作"
        else:
            if self.cycle_count % self.settings['cycles_before_long_break'] == 0:
                status = "长休息" if self.is_running else "准备长休息"
            else:
                status = "短休息" if self.is_running else "准备短休息"
        
        max_cycles = self.settings['cycles_before_long_break']
        current_cycle = self.cycle_count % max_cycles
        if current_cycle == 0 and self.cycle_count > 0:
            current_cycle = max_cycles
        
        self.timer_updated.emit(status, self.time_left, self.total_time, current_cycle, max_cycles)
    
    def send_notification(self, title: str, message: str):
        """发送通知"""
        try:
            if self.settings['notification_enabled']:
                # 这里应该调用通知管理器发送通知
                self.logger.info(f"通知: {title} - {message}")
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
    
    def get_widget(self) -> Optional[QWidget]:
        """获取插件组件"""
        return self.timer_widget
    
    def get_settings(self) -> Dict[str, Any]:
        """获取插件设置"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """更新插件设置"""
        try:
            self.settings.update(new_settings)
            
            # 如果当前不在运行，重置计时器以应用新设置
            if not self.is_running:
                self.reset_timer()
            
            self.logger.info("插件设置已更新")
            return True
            
        except Exception as e:
            self.logger.error(f"更新插件设置失败: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            'id': 'pomodoro_timer',
            'name': '番茄钟插件',
            'version': '2.1.0',
            'description': '专业的番茄工作法计时器',
            'author': 'Productivity Team',
            'status': self.status.value,
            'settings': self.settings
        }


# 插件入口点
def create_plugin():
    """创建插件实例"""
    return PomodoroTimerPlugin()
