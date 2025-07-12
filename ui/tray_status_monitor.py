#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 托盘状态监控
监控系统状态并提供实时信息
"""

import logging
import platform
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTextEdit

# 尝试导入psutil，如果失败则使用简化版本
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemStatusMonitor(QThread):
    """系统状态监控线程"""
    
    status_updated = pyqtSignal(dict)  # 状态更新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.SystemStatusMonitor')
        self.running = False
        self.update_interval = 5  # 5秒更新一次
    
    def start_monitoring(self):
        """开始监控"""
        self.running = True
        self.start()
        self.logger.info("系统状态监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        self.wait()
        self.logger.info("系统状态监控已停止")
    
    def run(self):
        """监控主循环"""
        while self.running:
            try:
                status = self._collect_system_status()
                self.status_updated.emit(status)
                self.msleep(self.update_interval * 1000)
            except Exception as e:
                self.logger.error(f"系统状态监控错误: {e}")
                self.msleep(5000)  # 错误时等待5秒
    
    def _collect_system_status(self) -> Dict[str, Any]:
        """收集系统状态信息"""
        try:
            if PSUTIL_AVAILABLE:
                return self._collect_with_psutil()
            else:
                return self._collect_basic_info()

        except Exception as e:
            self.logger.error(f"收集系统状态失败: {e}")
            return {'error': str(e)}

    def _collect_with_psutil(self) -> Dict[str, Any]:
        """使用psutil收集详细系统信息"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024**3)  # GB
        memory_total = memory.total / (1024**3)  # GB

        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_used = disk.used / (1024**3)  # GB
        disk_total = disk.total / (1024**3)  # GB

        # 网络状态
        network = psutil.net_io_counters()

        # 系统信息
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        return {
            'timestamp': datetime.now(),
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'percent': memory_percent,
                'used_gb': round(memory_used, 2),
                'total_gb': round(memory_total, 2)
            },
            'disk': {
                'percent': round(disk_percent, 1),
                'used_gb': round(disk_used, 2),
                'total_gb': round(disk_total, 2)
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            'system': {
                'platform': platform.system(),
                'uptime': str(uptime).split('.')[0],  # 去掉微秒
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    def _collect_basic_info(self) -> Dict[str, Any]:
        """收集基本系统信息（不依赖psutil）"""
        import os

        return {
            'timestamp': datetime.now(),
            'cpu': {
                'percent': 0.0,  # 无法获取
                'count': os.cpu_count() or 1
            },
            'memory': {
                'percent': 0.0,  # 无法获取
                'used_gb': 0.0,
                'total_gb': 0.0
            },
            'disk': {
                'percent': 0.0,  # 无法获取
                'used_gb': 0.0,
                'total_gb': 0.0
            },
            'network': {
                'bytes_sent': 0,
                'bytes_recv': 0
            },
            'system': {
                'platform': platform.system(),
                'uptime': 'Unknown',
                'boot_time': 'Unknown'
            }
        }


class TrayStatusManager(QObject):
    """托盘状态管理器"""
    
    status_changed = pyqtSignal(str, dict)  # 状态类型, 状态数据
    alert_triggered = pyqtSignal(str, str)  # 警告类型, 警告消息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.TrayStatusManager')
        
        # 状态监控
        self.system_monitor = SystemStatusMonitor()
        self.system_monitor.status_updated.connect(self._on_system_status_updated)
        
        # 当前状态
        self.current_status = {}
        
        # 警告阈值
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        }
        
        # 警告状态
        self.alert_states = {
            'cpu_high': False,
            'memory_high': False,
            'disk_high': False
        }
        
        self.logger.info("托盘状态管理器初始化完成")
    
    def start_monitoring(self):
        """开始状态监控"""
        self.system_monitor.start_monitoring()
    
    def stop_monitoring(self):
        """停止状态监控"""
        self.system_monitor.stop_monitoring()
    
    def _on_system_status_updated(self, status: Dict[str, Any]):
        """处理系统状态更新"""
        if 'error' in status:
            self.logger.error(f"系统状态错误: {status['error']}")
            return
        
        self.current_status = status
        self.status_changed.emit('system', status)
        
        # 检查警告条件
        self._check_alerts(status)
    
    def _check_alerts(self, status: Dict[str, Any]):
        """检查警告条件"""
        try:
            # CPU警告
            cpu_percent = status.get('cpu', {}).get('percent', 0)
            if cpu_percent > self.alert_thresholds['cpu_percent']:
                if not self.alert_states['cpu_high']:
                    self.alert_states['cpu_high'] = True
                    self.alert_triggered.emit(
                        'cpu_high',
                        f"CPU使用率过高: {cpu_percent:.1f}%"
                    )
            else:
                self.alert_states['cpu_high'] = False
            
            # 内存警告
            memory_percent = status.get('memory', {}).get('percent', 0)
            if memory_percent > self.alert_thresholds['memory_percent']:
                if not self.alert_states['memory_high']:
                    self.alert_states['memory_high'] = True
                    self.alert_triggered.emit(
                        'memory_high',
                        f"内存使用率过高: {memory_percent:.1f}%"
                    )
            else:
                self.alert_states['memory_high'] = False
            
            # 磁盘警告
            disk_percent = status.get('disk', {}).get('percent', 0)
            if disk_percent > self.alert_thresholds['disk_percent']:
                if not self.alert_states['disk_high']:
                    self.alert_states['disk_high'] = True
                    self.alert_triggered.emit(
                        'disk_high',
                        f"磁盘使用率过高: {disk_percent:.1f}%"
                    )
            else:
                self.alert_states['disk_high'] = False
                
        except Exception as e:
            self.logger.error(f"检查警告失败: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self.current_status.copy()
    
    def get_status_summary(self) -> str:
        """获取状态摘要"""
        if not self.current_status:
            return "状态信息不可用"
        
        try:
            cpu = self.current_status.get('cpu', {}).get('percent', 0)
            memory = self.current_status.get('memory', {}).get('percent', 0)
            disk = self.current_status.get('disk', {}).get('percent', 0)
            
            return f"CPU: {cpu:.1f}% | 内存: {memory:.1f}% | 磁盘: {disk:.1f}%"
            
        except Exception as e:
            self.logger.error(f"生成状态摘要失败: {e}")
            return "状态摘要生成失败"
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """设置警告阈值"""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            self.logger.info(f"设置 {metric} 警告阈值为 {threshold}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.stop_monitoring()
            self.logger.info("托盘状态管理器已清理")
        except Exception as e:
            self.logger.error(f"托盘状态管理器清理失败: {e}")


class SystemStatusDialog(QDialog):
    """系统状态对话框"""
    
    def __init__(self, status_manager: TrayStatusManager, parent=None):
        super().__init__(parent)
        self.status_manager = status_manager
        self.setWindowTitle("系统状态监控")
        self.setFixedSize(500, 400)
        
        self._init_ui()
        self._setup_connections()
        self._update_display()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # CPU状态
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU使用率:"))
        self.cpu_progress = QProgressBar()
        self.cpu_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_progress)
        cpu_layout.addWidget(self.cpu_label)
        layout.addLayout(cpu_layout)
        
        # 内存状态
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("内存使用率:"))
        self.memory_progress = QProgressBar()
        self.memory_label = QLabel("0%")
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addWidget(self.memory_label)
        layout.addLayout(memory_layout)
        
        # 磁盘状态
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("磁盘使用率:"))
        self.disk_progress = QProgressBar()
        self.disk_label = QLabel("0%")
        disk_layout.addWidget(self.disk_progress)
        disk_layout.addWidget(self.disk_label)
        layout.addLayout(disk_layout)
        
        # 详细信息
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)
    
    def _setup_connections(self):
        """设置信号连接"""
        self.status_manager.status_changed.connect(self._on_status_changed)
    
    def _on_status_changed(self, status_type: str, status_data: Dict[str, Any]):
        """处理状态变化"""
        if status_type == 'system':
            self._update_display(status_data)
    
    def _update_display(self, status: Optional[Dict[str, Any]] = None):
        """更新显示"""
        if status is None:
            status = self.status_manager.get_current_status()
        
        if not status:
            return
        
        try:
            # 更新进度条
            cpu_percent = status.get('cpu', {}).get('percent', 0)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            
            memory_percent = status.get('memory', {}).get('percent', 0)
            self.memory_progress.setValue(int(memory_percent))
            self.memory_label.setText(f"{memory_percent:.1f}%")
            
            disk_percent = status.get('disk', {}).get('percent', 0)
            self.disk_progress.setValue(int(disk_percent))
            self.disk_label.setText(f"{disk_percent:.1f}%")
            
            # 更新详细信息
            self._update_detail_text(status)
            
        except Exception as e:
            self.detail_text.setText(f"显示更新错误: {e}")
    
    def _update_detail_text(self, status: Dict[str, Any]):
        """更新详细信息文本"""
        try:
            text_lines = []
            
            # 系统信息
            system = status.get('system', {})
            text_lines.append(f"系统平台: {system.get('platform', 'Unknown')}")
            text_lines.append(f"启动时间: {system.get('boot_time', 'Unknown')}")
            text_lines.append(f"运行时间: {system.get('uptime', 'Unknown')}")
            text_lines.append("")
            
            # CPU信息
            cpu = status.get('cpu', {})
            text_lines.append(f"CPU核心数: {cpu.get('count', 'Unknown')}")
            text_lines.append(f"CPU使用率: {cpu.get('percent', 0):.1f}%")
            text_lines.append("")
            
            # 内存信息
            memory = status.get('memory', {})
            text_lines.append(f"内存总量: {memory.get('total_gb', 0):.2f} GB")
            text_lines.append(f"内存使用: {memory.get('used_gb', 0):.2f} GB")
            text_lines.append(f"内存使用率: {memory.get('percent', 0):.1f}%")
            text_lines.append("")
            
            # 磁盘信息
            disk = status.get('disk', {})
            text_lines.append(f"磁盘总量: {disk.get('total_gb', 0):.2f} GB")
            text_lines.append(f"磁盘使用: {disk.get('used_gb', 0):.2f} GB")
            text_lines.append(f"磁盘使用率: {disk.get('percent', 0):.1f}%")
            
            self.detail_text.setText("\n".join(text_lines))
            
        except Exception as e:
            self.detail_text.setText(f"详细信息生成错误: {e}")
