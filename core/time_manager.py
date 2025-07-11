# -*- coding: utf-8 -*-
"""
TimeNest 时间管理器
负责时间获取、时间偏移、时间校准等功能
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from core.config_manager import ConfigManager

class TimeManager(QObject):
    """时间管理器"""
    
    # 信号定义
    time_offset_changed = pyqtSignal(timedelta)  # 时间偏移变化
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # 时间偏移量（用于调试和测试）
        self._time_offset = timedelta()

        # 时间流速（用于调试，1.0为正常速度）
        self._time_speed = 1.0

        # 是否启用时间偏移（合并重复变量）
        self._offset_enabled = False
        
        # 加载设置
        self._load_settings()
        
        self.logger.info("时间管理器初始化完成")
    
    def _load_settings(self):
        """加载时间设置"""
        try:
            time_settings = self.config_manager.get('time', {})
            
            # 在非调试模式下，不加载时间偏移设置
            debug_mode = self.config_manager.get('debug.enabled', False)
            if debug_mode:
                offset_seconds = time_settings.get('offset_seconds', 0)
                self._time_offset = timedelta(seconds=offset_seconds)
                self._time_speed = time_settings.get('speed', 1.0)
                self._offset_enabled = time_settings.get('offset_enabled', False)
            
        except Exception as e:
            self.logger.error(f"加载时间设置失败: {e}")
    
    def get_current_time(self) -> datetime:
        """获取当前时间（考虑偏移）"""
        current_time = datetime.now()
        
        if self._offset_enabled and self._time_offset:
            current_time += self._time_offset
        
        return current_time
    
    def get_real_time(self) -> datetime:
        """获取真实时间（不考虑偏移）"""
        return datetime.now()
    
    def set_time_offset(self, offset: timedelta, save_to_config: bool = True):
        """设置时间偏移"""
        try:
            old_offset = self._time_offset
            self._time_offset = offset
            
            if save_to_config:
                self.config_manager.set('time.offset_seconds', int(offset.total_seconds()))
            
            self.time_offset_changed.emit(offset)
            self.logger.info(f"时间偏移已更改: {old_offset} -> {offset}")
            
        except Exception as e:
            self.logger.error(f"设置时间偏移失败: {e}")
    
    def get_time_offset(self) -> timedelta:
        """获取当前时间偏移"""
        return self._time_offset
    
    def set_time_speed(self, speed: float, save_to_config: bool = True):
        """设置时间流速（调试用）"""
        try:
            if speed <= 0:
                raise ValueError("时间流速必须大于0")
            
            old_speed = self._time_speed
            self._time_speed = speed
            
            if save_to_config:
                self.config_manager.set('time.speed', speed)
            
            self.logger.info(f"时间流速已更改: {old_speed} -> {speed}")
            
        except Exception as e:
            self.logger.error(f"设置时间流速失败: {e}")
    
    def get_time_speed(self) -> float:
        """获取当前时间流速"""
        return self._time_speed
    
    def enable_time_offset(self, enabled: bool, save_to_config: bool = True):
        """启用/禁用时间偏移"""
        try:
            old_enabled = self._offset_enabled
            self._offset_enabled = enabled
            
            if save_to_config:
                self.config_manager.set('time.offset_enabled', enabled)
            
            self.logger.info(f"时间偏移状态已更改: {old_enabled} -> {enabled}")
            
        except Exception as e:
            self.logger.error(f"设置时间偏移状态失败: {e}")
    
    def is_time_offset_enabled(self) -> bool:
        """检查时间偏移是否启用"""
        return self._offset_enabled
    
    def reset_time_offset(self, save_to_config: bool = True):
        """重置时间偏移"""
        self.set_time_offset(timedelta(), save_to_config)
        self.enable_time_offset(False, save_to_config)
    
    def add_time_offset(self, delta: timedelta, save_to_config: bool = True):
        """增加时间偏移"""
        new_offset = self._time_offset + delta
        self.set_time_offset(new_offset, save_to_config)
    
    def set_time_to(self, target_time: datetime, save_to_config: bool = True):
        """设置时间到指定时间"""
        current_real_time = self.get_real_time()
        offset = target_time - current_real_time
        self.set_time_offset(offset, save_to_config)
        self.enable_time_offset(True, save_to_config)
    
    def format_time(self, time_obj: datetime, format_str: str = "%H:%M:%S") -> str:
        """格式化时间显示"""
        try:
            return time_obj.strftime(format_str)
        except Exception as e:
            self.logger.error(f"格式化时间失败: {e}")
            return str(time_obj)
    
    def format_date(self, date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
        """格式化日期显示"""
        try:
            return date_obj.strftime(format_str)
        except Exception as e:
            self.logger.error(f"格式化日期失败: {e}")
            return str(date_obj)
    
    def format_datetime(self, datetime_obj: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化日期时间显示"""
        try:
            return datetime_obj.strftime(format_str)
        except Exception as e:
            self.logger.error(f"格式化日期时间失败: {e}")
            return str(datetime_obj)
    
    def get_time_until(self, target_time: datetime) -> timedelta:
        """获取到目标时间的时间差"""
        current_time = self.get_current_time()
        return target_time - current_time
    
    def is_time_in_range(self, check_time: datetime, start_time: datetime, end_time: datetime) -> bool:
        """检查时间是否在指定范围内"""
        return start_time <= check_time <= end_time
    
    def get_next_occurrence(self, target_time: datetime) -> datetime:
        """获取下一次出现的时间（如果已过今天，则返回明天的时间）"""
        current_time = self.get_current_time()
        
        if target_time <= current_time:
            # 如果目标时间已过，返回明天的同一时间
            next_day = current_time.date() + timedelta(days=1)
            return datetime.combine(next_day, target_time.time())
        else:
            return target_time
    
    def sync_system_time(self) -> bool:
        """同步系统时间（需要管理员权限）"""
        try:
            # 这里可以实现NTP时间同步
            # 由于需要系统权限，暂时只是重置偏移
            self.reset_time_offset()
            self.logger.info("时间已同步")
            return True
            
        except Exception as e:
            self.logger.error(f"同步系统时间失败: {e}")
            return False
    
    def get_debug_info(self) -> dict:
        """获取调试信息"""
        return {
            'real_time': self.get_real_time().isoformat(),
            'current_time': self.get_current_time().isoformat(),
            'time_offset': str(self._time_offset),
            'time_speed': self._time_speed,
            'offset_enabled': self._offset_enabled
        }