#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 时间校准服务
提供网络时间同步和时间校准功能
"""

import logging
import time
import socket
import struct
import threading
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from functools import lru_cache
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl

from core.base_manager import BaseManager


class TimeCalibrationService(BaseManager):
    """
    时间校准服务
    
    提供多种时间源的时间同步功能：
    - NTP服务器同步
    - HTTP时间服务器
    - 系统时间校准
    """
    
    # 信号
    calibration_started = pyqtSignal()
    calibration_progress = pyqtSignal(int, str)  # progress, status
    calibration_completed = pyqtSignal(bool, float, str)  # success, offset_ms, message
    time_sync_status_changed = pyqtSignal(bool)  # is_synced
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "TimeCalibrationService")
        
        # NTP服务器列表
        self.ntp_servers = [
            "pool.ntp.org",
            "time.nist.gov", 
            "time.windows.com",
            "time.apple.com",
            "cn.pool.ntp.org",
            "ntp.aliyun.com"
        ]
        
        # HTTP时间服务器
        self.http_time_servers = [
            "http://worldtimeapi.org/api/timezone/Asia/Shanghai",
            "https://timeapi.io/api/Time/current/zone?timeZone=Asia/Shanghai"
        ]
        
        # 网络管理器（延迟初始化）
        self._network_manager = None

        # 校准状态
        self.is_calibrating = False
        self.last_calibration_time = None
        self.time_offset = 0.0  # 毫秒
        self.is_time_synced = False
        
        # 自动校准定时器
        self.auto_calibration_timer = QTimer()
        self.auto_calibration_timer.timeout.connect(self._auto_calibrate)
        
        # 配置
        self.auto_calibration_enabled = True
        self.auto_calibration_interval = 3600  # 1小时
        self.calibration_timeout = 10  # 10秒超时
        
        self.logger.info("时间校准服务初始化完成")

    @property
    def network_manager(self) -> QNetworkAccessManager:
        """延迟初始化网络管理器"""
        if self._network_manager is None:
            self._network_manager = QNetworkAccessManager()
        return self._network_manager

    def initialize(self) -> bool:
        """初始化服务"""
        try:
            # 加载配置
            self._load_config()
            
            # 启动自动校准
            if self.auto_calibration_enabled:
                self.start_auto_calibration()
            
            self.logger.info("时间校准服务初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"时间校准服务初始化失败: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理服务"""
        try:
            self.stop_auto_calibration()
            self.logger.info("时间校准服务清理完成")
        except Exception as e:
            self.logger.error(f"时间校准服务清理失败: {e}")
    
    def start_calibration(self) -> bool:
        """开始时间校准"""
        try:
            if self.is_calibrating:
                self.logger.warning("时间校准已在进行中")
                return False
            
            self.is_calibrating = True
            self.calibration_started.emit()
            
            # 在后台线程执行校准
            thread = threading.Thread(target=self._perform_calibration, daemon=True)
            thread.start()
            
            return True
        except Exception as e:
            self.logger.error(f"启动时间校准失败: {e}")
            self.is_calibrating = False
            return False
    
    def start_auto_calibration(self) -> None:
        """启动自动校准"""
        try:
            if self.auto_calibration_enabled and self.auto_calibration_interval > 0:
                self.auto_calibration_timer.start(self.auto_calibration_interval * 1000)
                self.logger.info(f"自动时间校准已启动，间隔: {self.auto_calibration_interval}秒")
        except Exception as e:
            self.logger.error(f"启动自动校准失败: {e}")
    
    def stop_auto_calibration(self) -> None:
        """停止自动校准"""
        try:
            self.auto_calibration_timer.stop()
            self.logger.info("自动时间校准已停止")
        except Exception as e:
            self.logger.error(f"停止自动校准失败: {e}")
    
    def get_calibrated_time(self) -> datetime:
        """获取校准后的时间"""
        try:
            current_time = datetime.now()
            if self.is_time_synced and self.time_offset != 0:
                # 应用时间偏移
                calibrated_time = current_time + timedelta(milliseconds=self.time_offset)
                return calibrated_time
            return current_time
        except Exception as e:
            self.logger.error(f"获取校准时间失败: {e}")
            return datetime.now()
    
    def get_time_offset(self) -> float:
        """获取时间偏移量（毫秒）"""
        return self.time_offset
    
    def is_synchronized(self) -> bool:
        """检查时间是否已同步"""
        return self.is_time_synced
    
    def check_time_sync(self) -> None:
        """检查时间同步状态"""
        try:
            # 如果超过一定时间没有校准，标记为未同步
            if self.last_calibration_time:
                time_since_last = datetime.now() - self.last_calibration_time
                if time_since_last.total_seconds() > self.auto_calibration_interval * 2:
                    self._update_sync_status(False)
        except Exception as e:
            self.logger.error(f"检查时间同步状态失败: {e}")
    
    def _perform_calibration(self) -> None:
        """执行时间校准"""
        try:
            self.calibration_progress.emit(10, "开始时间校准...")
            
            # 收集多个时间源的时间
            time_samples = []
            
            # 1. 尝试NTP服务器
            self.calibration_progress.emit(30, "连接NTP服务器...")
            ntp_times = self._get_ntp_times()
            time_samples.extend(ntp_times)
            
            # 2. 尝试HTTP时间服务器
            self.calibration_progress.emit(60, "获取网络时间...")
            http_times = self._get_http_times()
            time_samples.extend(http_times)
            
            self.calibration_progress.emit(80, "计算时间偏移...")
            
            if not time_samples:
                self._finish_calibration(False, 0.0, "无法获取网络时间，请检查网络连接")
                return
            
            # 计算时间偏移
            local_time = time.time()
            offsets = [(sample - local_time) * 1000 for sample in time_samples]  # 转换为毫秒
            
            # 使用中位数减少异常值影响
            offsets.sort()
            median_offset = offsets[len(offsets) // 2]
            
            # 更新时间偏移
            self.time_offset = median_offset
            self.last_calibration_time = datetime.now()
            
            self.calibration_progress.emit(100, "校准完成")
            
            # 判断是否需要校准
            if abs(median_offset) > 1000:  # 超过1秒
                message = f"时间偏差较大: {median_offset:.0f}ms，建议手动调整系统时间"
                self._finish_calibration(True, median_offset, message)
            elif abs(median_offset) > 100:  # 超过100ms
                message = f"时间已校准，偏差: {median_offset:.0f}ms"
                self._finish_calibration(True, median_offset, message)
            else:
                message = f"时间同步良好，偏差: {median_offset:.0f}ms"
                self._finish_calibration(True, median_offset, message)
            
            self._update_sync_status(True)
            
        except Exception as e:
            self.logger.error(f"时间校准执行失败: {e}")
            self._finish_calibration(False, 0.0, f"校准失败: {e}")
    
    def _get_ntp_times(self) -> List[float]:
        """获取NTP时间（优化版本）"""
        times = []
        max_attempts = min(3, len(self.ntp_servers))

        for i in range(max_attempts):
            server = self.ntp_servers[i]
            try:
                ntp_time = self._query_ntp_server(server)
                if ntp_time:
                    times.append(ntp_time)
                    if len(times) >= 2:  # 获得2个样本就够了
                        break
            except Exception as e:
                self.logger.debug(f"NTP服务器 {server} 查询失败: {e}")
                continue

        return times
    
    def _query_ntp_server(self, server: str, timeout: int = 5) -> Optional[float]:
        """查询NTP服务器"""
        try:
            # NTP数据包格式
            ntp_packet = b'\x1b' + 47 * b'\0'
            
            # 创建UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            try:
                # 发送NTP请求
                sock.sendto(ntp_packet, (server, 123))
                
                # 接收响应
                response, _ = sock.recvfrom(1024)
                
                # 解析NTP时间戳（从1900年开始的秒数）
                ntp_time = struct.unpack('!12I', response)[10]
                ntp_time += struct.unpack('!12I', response)[11] / 2**32
                
                # 转换为Unix时间戳（从1970年开始）
                unix_time = ntp_time - 2208988800
                
                return unix_time
                
            finally:
                sock.close()
                
        except Exception as e:
            self.logger.debug(f"查询NTP服务器 {server} 失败: {e}")
            return None
    
    def _get_http_times(self) -> List[float]:
        """获取HTTP时间（同步方式）"""
        times = []
        
        # 这里简化实现，实际应该使用异步方式
        # 由于Qt的网络请求是异步的，这里使用简单的实现
        try:
            import requests
            
            for url in self.http_time_servers[:2]:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # 解析时间
                        if 'datetime' in data:
                            # worldtimeapi格式
                            time_str = data['datetime']
                            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                            times.append(dt.timestamp())
                        elif 'dateTime' in data:
                            # timeapi格式
                            time_str = data['dateTime']
                            dt = datetime.fromisoformat(time_str)
                            times.append(dt.timestamp())
                            
                except Exception as e:
                    self.logger.debug(f"HTTP时间服务器 {url} 查询失败: {e}")
                    continue
                    
        except ImportError:
            self.logger.debug("requests库不可用，跳过HTTP时间获取")
        
        return times
    
    def _finish_calibration(self, success: bool, offset: float, message: str) -> None:
        """完成校准"""
        self.is_calibrating = False
        self.calibration_completed.emit(success, offset, message)
        
        if success:
            self.logger.info(f"时间校准完成: {message}")
        else:
            self.logger.warning(f"时间校准失败: {message}")
    
    def _update_sync_status(self, is_synced: bool) -> None:
        """更新同步状态"""
        if self.is_time_synced != is_synced:
            self.is_time_synced = is_synced
            self.time_sync_status_changed.emit(is_synced)
            self.logger.info(f"时间同步状态变更: {'已同步' if is_synced else '未同步'}")
    
    def _auto_calibrate(self) -> None:
        """自动校准"""
        if not self.is_calibrating:
            self.logger.info("执行自动时间校准")
            self.start_calibration()
    
    def _load_config(self) -> None:
        """加载配置"""
        try:
            if self.config_manager:
                config = self.config_manager.get_config('time_calibration', {})
                
                self.auto_calibration_enabled = config.get('auto_enabled', True)
                self.auto_calibration_interval = config.get('auto_interval', 3600)
                self.calibration_timeout = config.get('timeout', 10)
                
                # 自定义NTP服务器
                custom_ntp = config.get('ntp_servers', [])
                if custom_ntp:
                    self.ntp_servers = custom_ntp + self.ntp_servers
                
                self.logger.debug("时间校准配置加载完成")
                
        except Exception as e:
            self.logger.error(f"加载时间校准配置失败: {e}")
    
    def get_status_info(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            'is_synced': self.is_time_synced,
            'time_offset_ms': self.time_offset,
            'last_calibration': self.last_calibration_time.isoformat() if self.last_calibration_time else None,
            'auto_calibration_enabled': self.auto_calibration_enabled,
            'is_calibrating': self.is_calibrating
        }
