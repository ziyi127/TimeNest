import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QTimer
import ntplib
import threading

logger = logging.getLogger(__name__)

class TimeService(QObject):
    """时间服务 - 提供精确时间同步功能，基于ClassIsland的ExactTimeService实现"""
    
    # 时间同步状态变化信号
    sync_status_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # 时间同步相关属性
        self._sync_status_message = "时间尚未同步。"
        self.prev_datetime = datetime.min
        self.need_waiting = False
        self.ntp_client: Optional[ntplib.NTPClient] = None
        self.last_time = datetime.now()
        self.waiting_for_system_time_changed = False
        self.last_system_time = datetime.now()
        self.time_get_stopwatch = time.time()
        self.time_offset_seconds = 0.0
        self.debug_time_offset_seconds = 0.0
        self.is_exact_time_enabled = True
        self.exact_time_server = "ntp.aliyun.com"  # 默认NTP服务器
        self.backup_servers = ["ntp1.aliyun.com", "ntp2.aliyun.com", "ntp3.aliyun.com"]  # 备用服务器
        self.max_retry_attempts = 3  # 最大重试次数
        
        # 初始化NTP客户端
        try:
            self.ntp_client = ntplib.NTPClient()
        except Exception as e:
            self.logger.error(f"初始化NTP客户端失败: {e}")
            self._sync_status_message = str(e)
            
        # 初始化定时器，每10分钟同步一次时间
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(10 * 60 * 1000)  # 10分钟
        self.update_timer.timeout.connect(self.sync)
        
        # 立即执行一次同步
        self.sync()
        
    @property
    def sync_status_message(self) -> str:
        """获取同步状态消息"""
        return self._sync_status_message
    
    @sync_status_message.setter
    def sync_status_message(self, value: str):
        """设置同步状态消息"""
        if value != self._sync_status_message:
            self._sync_status_message = value
            self.sync_status_changed.emit(value)
            
    def sync(self):
        """同步时间"""
        if not self.is_exact_time_enabled or not self.ntp_client:
            self.waiting_for_system_time_changed = False
            return
            
        self.logger.info(f"正在从 {self.exact_time_server} 同步时间")
        self.sync_status_message = "正在同步时间……"
        self.sync_status_changed.emit(self.sync_status_message)
        
        prev = datetime.now()
        
        # 尝试同步时间，包括重试机制
        servers_to_try = [self.exact_time_server] + self.backup_servers
        last_exception = None
        
        for attempt in range(self.max_retry_attempts):
            for server in servers_to_try:
                try:
                    # 使用NTP获取时间
                    response = self.ntp_client.request(server)
                    ntp_time = datetime.fromtimestamp(response.tx_time)
                    
                    # 检查时间差异
                    if abs((ntp_time - prev).total_seconds()) < 30 and ntp_time < prev:
                        self.need_waiting = True
                        self.prev_datetime = prev
                        
                    self.logger.info(f"成功地同步了时间，现在是 {ntp_time}")
                    self.sync_status_message = f"成功地在{ntp_time}同步了时间"
                    self.sync_status_changed.emit(self.sync_status_message)
                    return  # 成功同步，退出函数
                    
                except Exception as e:
                    last_exception = e
                    self.logger.warning(f"从服务器 {server} 同步时间失败 (尝试 {attempt + 1}/{self.max_retry_attempts}): {e}")
                    continue  # 尝试下一个服务器
            
            # 如果所有服务器都尝试失败，等待一段时间后重试
            if attempt < self.max_retry_attempts - 1:
                self.logger.info(f"所有服务器同步失败，等待5秒后进行第 {attempt + 2} 次重试")
                time.sleep(5)
        
        # 所有重试都失败
        self.logger.error(f"同步时间失败，已尝试所有服务器和重试次数: {last_exception}")
        self.sync_status_message = f"同步时间失败：{last_exception}"
        self.sync_status_changed.emit(self.sync_status_message)
            
    def get_current_local_datetime(self) -> datetime:
        """获取当前精确当地时间"""
        system_time = datetime.now()
        
        if self.is_exact_time_enabled and self.ntp_client:
            if self.waiting_for_system_time_changed:
                return self.last_time
                
            # 使用NTP时间
            try:
                response = self.ntp_client.request(self.exact_time_server)
                ntp_time = datetime.fromtimestamp(response.tx_time)
                base_time = ntp_time
            except Exception:
                # 如果NTP同步失败，回退到系统时间
                base_time = system_time
        else:
            # 使用系统时间
            base_time = system_time
            
        # 处理时间回退情况
        base_time = base_time if base_time > self.prev_datetime or not self.need_waiting else self.prev_datetime
        
        if self.need_waiting and base_time > self.prev_datetime:
            self.need_waiting = False
            
        # 应用时间偏移
        final_time = base_time + timedelta(seconds=self.time_offset_seconds + self.debug_time_offset_seconds)
        self.last_time = final_time
        return final_time
            
    def get_current_local_datetime(self) -> datetime:
        """获取当前精确当地时间"""
        system_time = datetime.now()
        
        if self.is_exact_time_enabled and self.ntp_client:
            if self.waiting_for_system_time_changed:
                return self.last_time
                
            # 使用NTP时间
            try:
                response = self.ntp_client.request(self.exact_time_server)
                ntp_time = datetime.fromtimestamp(response.tx_time)
                base_time = ntp_time
            except Exception:
                # 如果NTP同步失败，回退到系统时间
                base_time = system_time
        else:
            # 使用系统时间
            base_time = system_time
            
        # 处理时间回退情况
        base_time = base_time if base_time > self.prev_datetime or not self.need_waiting else self.prev_datetime
        
        if self.need_waiting and base_time > self.prev_datetime:
            self.need_waiting = False
            
        # 应用时间偏移
        final_time = base_time + timedelta(seconds=self.time_offset_seconds + self.debug_time_offset_seconds)
        self.last_time = final_time
        return final_time
        
    def set_time_offset(self, offset_seconds: float):
        """设置时间偏移（秒）"""
        self.time_offset_seconds = offset_seconds
        
    def set_debug_time_offset(self, offset_seconds: float):
        """设置调试时间偏移（秒）"""
        self.debug_time_offset_seconds = offset_seconds
        
    def enable_exact_time(self, enabled: bool):
        """启用或禁用精确时间"""
        self.is_exact_time_enabled = enabled
        if enabled:
            self.update_timer.start()
        else:
            self.update_timer.stop()
            
    def set_exact_time_server(self, server: str):
        """设置精确时间服务器"""
        self.exact_time_server = server
        try:
            # 重新初始化NTP客户端
            self.ntp_client = ntplib.NTPClient()
        except Exception as e:
            self.logger.error(f"初始化NTP客户端失败: {e}")
            self._sync_status_message = str(e)
            self.sync_status_changed.emit(self._sync_status_message)
            
    def get_current_time_str(self) -> str:
        """获取当前时间字符串"""
        current_time = self.get_current_local_datetime()
        return current_time.strftime("%H:%M:%S")
        
    def get_time_info(self) -> Dict[str, Any]:
        """获取时间信息"""
        current_time = self.get_current_local_datetime()
        return {
            "current_time": current_time,
            "time_str": current_time.strftime("%H:%M:%S"),
            "date_str": current_time.strftime("%Y-%m-%d"),
            "weekday": current_time.weekday()
        }

# 全局时间服务实例
time_service_instance: Optional[TimeService] = None

def get_time_service() -> TimeService:
    """
    获取时间服务实例（单例模式）
    
    Returns:
        TimeService: 时间服务实例
    """
    global time_service_instance
    
    if time_service_instance is None:
        time_service_instance = TimeService()
    
    return time_service_instance
