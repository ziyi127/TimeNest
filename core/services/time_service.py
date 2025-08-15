import logging
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import platform
from PySide6.QtCore import QObject, Signal


class TimeService(QObject):
    """时间服务 - 提供精确时间同步功能，基于ClassIsland的ExactTimeService实现"""

    # 时间同步状态变化信号
    sync_status_changed = Signal(str)
    # 时间同步完成信号
    time_synced = Signal(datetime)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # 时间相关属性
        self._sync_status_message = "使用系统时间"
        self.prev_datetime = datetime.min
        self.last_time = datetime.now()
        self.time_get_stopwatch = time.time()
        self.time_offset_seconds = 0.0
        self.debug_time_offset_seconds = 0.0

        # 检测操作系统
        self.os_type = platform.system()
        self.logger.info(f"当前操作系统: {self.os_type}")

        # 初始化状态
        self.sync_status_message = "时间服务已初始化，使用系统时间"
        # 发送系统时间作为同步时间
        system_time = datetime.now()
        self.time_synced.emit(system_time)

    @property
    def sync_status_message(self) -> str:
        """获取同步状态消息"""
        return self._sync_status_message

    @sync_status_message.setter
    def sync_status_message(self, value: str) -> None:
        """设置同步状态消息"""
        if value != self._sync_status_message:
            self._sync_status_message = value
            self.sync_status_changed.emit(value)

    def get_current_local_datetime(self) -> datetime:
        """获取当前系统时间"""
        # 根据操作系统获取系统时间
        system_time = datetime.now()

        # 处理时间回退情况
        if system_time < self.prev_datetime:
            self.logger.warning(f"检测到时间回退: {system_time} < {self.prev_datetime}")
            system_time = self.prev_datetime
        else:
            self.prev_datetime = system_time

        # 应用时间偏移
        final_time = system_time + timedelta(
            seconds=self.time_offset_seconds + self.debug_time_offset_seconds
        )
        self.last_time = final_time
        return final_time

    def set_time_offset(self, offset_seconds: float) -> None:
        """设置时间偏移（秒）"""
        self.time_offset_seconds = offset_seconds

    def set_debug_time_offset(self, offset_seconds: float) -> None:
        """设置调试时间偏移（秒）"""
        self.debug_time_offset_seconds = offset_seconds

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
            "weekday": current_time.weekday(),
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
