#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 自动时间校准服务
支持 NTP 时间同步和自动校准功能
"""

import logging
import socket
import struct
import time
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QTimer, QThread
import requests


@dataclass
class TimeServer:
    """时间服务器信息"""
    host: str
    port: int = 123
    name: str = ""
    location: str = ""
    stratum: int = 0
    delay: float = 0.0
    offset: float = 0.0
    last_sync: Optional[datetime] = None


class NTPClient:
    """NTP 客户端"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.NTPClient')
    
    def get_ntp_time(self, server: str, port: int = 123, timeout: float = 10.0) -> Optional[Tuple[datetime, float]]:
        """
        从 NTP 服务器获取时间

        Args:
            server: NTP 服务器地址
            port: 端口号
            timeout: 超时时间

        Returns:
            Tuple[datetime, float]: (服务器时间, 延迟) 或 None
        """
        sock = None
        try:
            self.logger.info(f"尝试连接 NTP 服务器: {server}:{port}")

            # 创建 NTP 请求包
            ntp_packet = bytearray(48)
            ntp_packet[0] = 0x1B  # LI=0, VN=3, Mode=3

            # 发送请求
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)

            send_time = time.time()
            sock.sendto(ntp_packet, (server, port))

            # 接收响应
            response, _ = sock.recvfrom(48)
            receive_time = time.time()

            # 解析响应
            if len(response) >= 48:
                # 提取服务器时间戳 (字节 40-47)
                server_timestamp = struct.unpack('!Q', response[40:48])[0]

                # NTP 时间戳转换为 Unix 时间戳
                # NTP 纪元: 1900-01-01, Unix 纪元: 1970-01-01
                ntp_epoch_offset = 2208988800  # 70年的秒数
                unix_timestamp = server_timestamp / (2**32) - ntp_epoch_offset

                server_time = datetime.fromtimestamp(unix_timestamp)
                delay = receive_time - send_time

                self.logger.info(f"NTP 时间获取成功: {server}, 时间: {server_time}, 延迟: {delay:.3f}s")
                return server_time, delay
            else:
                self.logger.warning(f"NTP 响应包长度不足: {len(response)} < 48")

        except socket.timeout:
            self.logger.warning(f"NTP 请求超时: {server}:{port}")
        except socket.gaierror as e:
            self.logger.warning(f"NTP 服务器地址解析失败 {server}: {e}")
        except Exception as e:
            self.logger.error(f"NTP 请求失败 {server}:{port}: {e}")
        finally:
            if sock:
                sock.close()

        return None


class WebTimeClient:
    """Web 时间客户端"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.WebTimeClient')
    
    def get_web_time(self, timeout: float = 10.0) -> Optional[Tuple[datetime, float]]:
        """
        从多个 Web API 获取时间

        Args:
            timeout: 超时时间

        Returns:
            Tuple[datetime, float]: (服务器时间, 延迟) 或 None
        """
        # 多个备用时间API
        time_apis = [
            "http://worldtimeapi.org/api/timezone/Asia/Shanghai",
            "https://worldtimeapi.org/api/timezone/Asia/Shanghai",
            "http://worldtimeapi.org/api/ip",
            "https://worldtimeapi.org/api/ip"
        ]

        for url in time_apis:
            try:
                self.logger.info(f"尝试连接时间服务器: {url}")
                start_time = time.time()

                # 设置请求头，模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.get(url, timeout=timeout, headers=headers)
                end_time = time.time()

                if response.status_code == 200:
                    data = response.json()

                    # 解析时间字符串
                    datetime_str = data.get('datetime', '')
                    if datetime_str:
                        # 移除时区信息进行简单解析
                        if '+' in datetime_str:
                            datetime_str = datetime_str.split('+')[0]
                        elif 'Z' in datetime_str:
                            datetime_str = datetime_str.replace('Z', '')

                        server_time = datetime.fromisoformat(datetime_str)
                        delay = end_time - start_time

                        self.logger.info(f"Web 时间获取成功: {server_time}, 延迟: {delay:.3f}s")
                        return server_time, delay
                else:
                    self.logger.warning(f"Web API 返回错误状态码: {response.status_code}")

            except requests.exceptions.Timeout:
                self.logger.warning(f"Web 时间请求超时: {url}")
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Web 时间连接失败: {url}")
            except Exception as e:
                self.logger.error(f"Web 时间请求失败 {url}: {e}")

        self.logger.error("所有 Web 时间服务器都无法连接")
        return None

    def get_fallback_time(self) -> Optional[Tuple[datetime, float]]:
        """
        获取备用时间（本地系统时间）

        Returns:
            Tuple[datetime, float]: (系统时间, 0延迟)
        """
        try:
            current_time = datetime.now()
            self.logger.info("使用本地系统时间作为备用")
            return current_time, 0.0
        except Exception as e:
            self.logger.error(f"获取系统时间失败: {e}")
            return None


class TimeCalibrationWorker(QThread):
    """时间校准工作线程"""
    
    calibration_completed = Signal(bool, float, str)  # 成功, 偏移量, 消息
    progress_updated = Signal(int, str)  # 进度, 状态
    
    def __init__(self, servers: List[TimeServer]):
        super().__init__()
        self.servers = servers
        self.logger = logging.getLogger(f'{__name__}.TimeCalibrationWorker')
        self.ntp_client = NTPClient()
        self.web_client = WebTimeClient()
    
    def run(self):
        """执行时间校准"""
        try:
            self.progress_updated.emit(10, "开始时间校准...")

            successful_syncs = []
            total_servers = len(self.servers) + 1  # NTP服务器 + Web API

            # 尝试 NTP 服务器
            for i, server in enumerate(self.servers):
                try:
                    progress = 10 + (i * 60) // total_servers
                    self.progress_updated.emit(progress, f"同步 NTP 服务器: {server.host}")

                    # 设置较短的超时时间避免卡死
                    result = self.ntp_client.get_ntp_time(server.host, server.port, timeout=5)
                    if result:
                        server_time, delay = result
                        local_time = datetime.now()
                        offset = (server_time - local_time).total_seconds()

                        server.delay = delay
                        server.offset = offset
                        server.last_sync = datetime.now()

                        successful_syncs.append((server, offset, delay))
                        self.logger.info(f"NTP 同步成功 {server.host}: 偏移 {offset:.3f}s, 延迟 {delay:.3f}s")
                    else:
                        self.logger.warning(f"NTP 服务器 {server.host} 无响应")
                except Exception as e:
                    self.logger.error(f"NTP 服务器 {server.host} 连接失败: {e}")
                    continue
            
            # 尝试 Web API
            self.progress_updated.emit(70, "同步 Web 时间服务...")
            try:
                # 使用线程超时机制替代signal（跨平台兼容）
                import threading
                import queue

                result_queue = queue.Queue()

                def web_time_worker():
                    try:
                        result = self.web_client.get_web_time()
                        result_queue.put(('success', result))
                    except Exception as e:
                        result_queue.put(('error', e))

                # 启动工作线程
                worker_thread = threading.Thread(target=web_time_worker)
                worker_thread.daemon = True
                worker_thread.start()

                # 等待结果，最多5秒
                try:
                    status, web_result = result_queue.get(timeout=5)

                    if status == 'success' and web_result:
                        server_time, delay = web_result
                        local_time = datetime.now()
                        offset = (server_time - local_time).total_seconds()

                        # 创建虚拟服务器对象
                        web_server = TimeServer(
                            host="worldtimeapi.org",
                            name="World Time API",
                            delay=delay,
                            offset=offset,
                            last_sync=datetime.now()
                        )
                        successful_syncs.append((web_server, offset, delay))
                        self.logger.info(f"Web 时间同步成功: 偏移 {offset:.3f}s, 延迟 {delay:.3f}s")
                    else:
                        self.logger.warning("Web 时间服务不可用")

                except queue.Empty:
                    self.logger.warning("Web 时间服务超时")

            except Exception as e:
                self.logger.error(f"Web 时间同步失败: {e}")
            
            self.progress_updated.emit(90, "计算最佳时间偏移...")

            if successful_syncs:
                # 计算加权平均偏移量（延迟越小权重越大）
                total_weight = 0
                weighted_offset = 0

                for server, offset, delay in successful_syncs:
                    weight = 1.0 / (delay + 0.001)  # 避免除零
                    weighted_offset += offset * weight
                    total_weight += weight

                final_offset = weighted_offset / total_weight if total_weight > 0 else 0

                self.progress_updated.emit(100, "时间校准完成")

                message = f"成功同步 {len(successful_syncs)} 个时间源，计算偏移量: {final_offset:.3f}秒"
                self.calibration_completed.emit(True, final_offset, message)
            else:
                # 如果所有网络时间源都失败，使用本地时间作为参考
                self.progress_updated.emit(95, "使用本地时间作为参考...")
                fallback_result = self.web_client.get_fallback_time()
                if fallback_result:
                    self.progress_updated.emit(100, "时间校准完成（使用本地时间）")
                    message = "网络时间服务不可用，已使用本地系统时间。建议检查网络连接后重新校准。"
                    self.calibration_completed.emit(True, 0.0, message)
                else:
                    self.progress_updated.emit(100, "时间校准失败")
                    self.calibration_completed.emit(False, 0.0, "无法获取任何时间源，请检查系统时间设置")
            
        except Exception as e:
            self.logger.error(f"时间校准失败: {e}")
            self.calibration_completed.emit(False, 0.0, f"校准过程出错: {e}")


class TimeCalibrationService(QObject):
    """时间校准服务"""
    
    calibration_completed = Signal(bool, float, str)  # 成功, 偏移量, 消息
    calibration_progress = Signal(int, str)  # 进度, 状态
    
    def __init__(self, config_manager, time_manager):
        super().__init__()
        self.config_manager = config_manager
        self.time_manager = time_manager
        self.logger = logging.getLogger(f'{__name__}.TimeCalibrationService')
        
        # 默认 NTP 服务器列表（按可靠性排序）
        self.default_servers = [
            TimeServer("ntp.aliyun.com", name="阿里云 NTP", location="中国"),
            TimeServer("time.windows.com", name="微软 NTP", location="全球"),
            TimeServer("cn.pool.ntp.org", name="中国 NTP Pool", location="中国"),
            TimeServer("asia.pool.ntp.org", name="亚洲 NTP Pool", location="亚洲"),
            TimeServer("pool.ntp.org", name="全球 NTP Pool", location="全球"),
            TimeServer("time.cloudflare.com", name="Cloudflare NTP", location="全球"),
            TimeServer("time.google.com", name="Google NTP", location="全球")
        ]
        
        # 自动校准定时器
        self.auto_calibration_timer = QTimer()
        self.auto_calibration_timer.timeout.connect(self.auto_calibrate)
        
        # 工作线程
        self.calibration_worker: Optional[TimeCalibrationWorker] = None
        
        self._load_settings()
    
    def _load_settings(self):
        """加载设置"""
        try:
            settings = self.config_manager.get_config('time_calibration', {}, 'component')
            
            # 自动校准设置
            auto_enabled = settings.get('auto_calibration_enabled', False)
            auto_interval = settings.get('auto_calibration_interval', 3600)  # 1小时
            
            
            if auto_enabled and hasattr(self, "auto_calibration_timer"):
                self.auto_calibration_timer.start(auto_interval * 1000)
                self.logger.info(f"自动时间校准已启用，间隔: {auto_interval}秒")
            
            # 自定义服务器
            custom_servers = settings.get('custom_servers', [])
            for server_data in custom_servers:
                server = TimeServer(
                    host=server_data.get('host', ''),
                    port=server_data.get('port', 123),
                    name=server_data.get('name', ''),
                    location=server_data.get('location', '')
                )
                if server.host and server not in self.default_servers:
                    self.default_servers.append(server)
            
        except Exception as e:
            self.logger.error(f"加载时间校准设置失败: {e}")
    
    def _save_settings(self):
        """保存设置"""
        try:
            settings = {
                'auto_calibration_enabled': self.auto_calibration_timer.isActive(),
                'auto_calibration_interval': self.auto_calibration_timer.interval() // 1000,
                'custom_servers': [
                    {
                        'host': server.host,
                        'port': server.port,
                        'name': server.name,
                        'location': server.location
                    } for server in self.default_servers[5:]  # 只保存自定义服务器
                ],
                'last_calibration': datetime.now().isoformat()
            }
            
            self.config_manager.set_config('time_calibration', settings, 'component')
            self.config_manager.save_all_configs()
            
        except Exception as e:
            self.logger.error(f"保存时间校准设置失败: {e}")
    
    def start_calibration(self, servers: Optional[List[TimeServer]] = None) -> bool:
        """
        开始时间校准
        
        Args:
            servers: 要使用的服务器列表，None 使用默认列表
            
        Returns:
            bool: 是否成功启动
        """
        try:
            if self.calibration_worker and self.calibration_worker.isRunning():
                self.logger.warning("时间校准正在进行中")
                return False
            
            servers_to_use = servers or self.default_servers
            
            self.calibration_worker = TimeCalibrationWorker(servers_to_use)
            self.calibration_worker.calibration_completed.connect(self._on_calibration_completed)
            self.calibration_worker.progress_updated.connect(self.calibration_progress.emit)
            
            self.calibration_worker.start()
            self.logger.info("开始时间校准")
            return True
            
        except Exception as e:
            self.logger.error(f"启动时间校准失败: {e}")
            return False
    
    def _on_calibration_completed(self, success: bool, offset: float, message: str):
        """校准完成处理"""
        try:
            if success:
                # 应用时间偏移:
                # 应用时间偏移
                if hasattr(self.time_manager, 'set_time_offset'):
                    self.time_manager.set_time_offset(timedelta(seconds=offset))
                    self.logger.info(f"时间偏移已应用: {offset:.3f}秒")
                
                # 保存校准结果
                self._save_calibration_result(offset)
            
            # 清理工作线程
            if self.calibration_worker:
                self.calibration_worker.deleteLater()
                self.calibration_worker = None
            
            # 发出完成信号
            self.calibration_completed.emit(success, offset, message)
            
        except Exception as e:
            self.logger.error(f"处理校准结果失败: {e}")
    
    def _save_calibration_result(self, offset: float):
        """保存校准结果"""
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'offset': offset,
                'servers_used': len(self.default_servers)
            }
            
            # 保存到历史记录
            history = self.config_manager.get_config('calibration_history', [], 'component')
            history.append(result)
            
            # 只保留最近 50 次记录
            if len(history) > 50:
                history = history[-50:]
            
            self.config_manager.set_config('calibration_history', history, 'component')
            self.config_manager.save_all_configs()
            
        except Exception as e:
            self.logger.error(f"保存校准结果失败: {e}")
    
    def auto_calibrate(self):
        """自动校准"""
        self.logger.info("执行自动时间校准")
        self.start_calibration()
    
    def set_auto_calibration(self, enabled: bool, interval_seconds: int = 3600):
        """设置自动校准"""
        try:
            if enabled and hasattr(self, "auto_calibration_timer"):
                self.auto_calibration_timer.start(interval_seconds * 1000)
                self.logger.info(f"自动时间校准已启用，间隔: {interval_seconds}秒")
            else:
                self.auto_calibration_timer.stop()
                self.logger.info("自动时间校准已禁用")
            
            self._save_settings()
            
        except Exception as e:
            self.logger.error(f"设置自动校准失败: {e}")
    
    def get_calibration_history(self) -> List[Dict]:
        """获取校准历史"""
        return self.config_manager.get_config('calibration_history', [], 'component')
    
    def add_custom_server(self, server: TimeServer):
        """添加自定义服务器"""
        if server not in self.default_servers:
            self.default_servers.append(server)
            self._save_settings()
            self.logger.info(f"添加自定义时间服务器: {server.host}")
    
    def remove_custom_server(self, host: str):
        """移除自定义服务器"""
        self.default_servers = [s for s in self.default_servers if s.host != host]
        self._save_settings()
        self.logger.info(f"移除自定义时间服务器: {host}")
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.auto_calibration_timer.isActive():
                self.auto_calibration_timer.stop()
            
            
            if self.calibration_worker and self.calibration_worker.isRunning():
                self.calibration_worker.terminate()
            
                self.calibration_worker.terminate()
                self.calibration_worker.wait()
                self.calibration_worker.deleteLater()
            
            self.logger.info("时间校准服务清理完成")
            
        except Exception as e:
            self.logger.error(f"清理时间校准服务失败: {e}")
