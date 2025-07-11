#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 浮窗模块实现
定义浮窗模块的基类和具体实现
"""

import logging
import psutil
import requests
from abc import ABC, abstractmethod, ABCMeta
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, TYPE_CHECKING
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

if TYPE_CHECKING:
    from core.app_manager import AppManager


# 创建兼容的 metaclass
class QObjectABCMeta(type(QObject), ABCMeta):
    """兼容 QObject 和 ABC 的 metaclass"""
    pass


class FloatingModule(QObject, ABC, metaclass=QObjectABCMeta):
    """
    浮窗模块抽象基类
    
    定义所有浮窗模块的通用接口和行为
    """
    
    # 信号定义
    content_updated = pyqtSignal(str)  # 内容更新信号
    error_occurred = pyqtSignal(str)   # 错误发生信号
    
    def __init__(self, module_id: str, app_manager: Optional['AppManager'] = None):
        """
        初始化浮窗模块
        
        Args:
            module_id: 模块唯一标识符
            app_manager: 应用管理器实例（依赖注入）
        """
        super().__init__()
        
        self.module_id = module_id
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        
        # 模块状态
        self.enabled = True
        self.visible = True
        self.order = 0
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_content)
        
        # 配置
        self.config = {}
        self.load_config()
        
        self.logger.debug(f"模块 {module_id} 初始化完成")
    
    @abstractmethod
    def get_display_text(self) -> str:
        """
        获取显示文本
        
        Returns:
            str: 要显示的文本内容
        """
        pass
    
    @abstractmethod
    def get_tooltip_text(self) -> str:
        """
        获取工具提示文本
        
        Returns:
            str: 工具提示内容
        """
        pass
    
    @abstractmethod
    def update_content(self) -> None:
        """更新模块内容"""
        pass
    
    def load_config(self) -> None:
        """加载模块配置"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                config_key = f'floating_widget.modules.{self.module_id}'
                self.config = self.app_manager.config_manager.get(config_key, {})
                self.enabled = self.config.get('enabled', True)
                self.order = self.config.get('order', 0)
        except Exception as e:
            self.logger.warning(f"加载配置失败: {e}")
    
    def save_config(self) -> None:
        """保存模块配置"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                config_key = f'floating_widget.modules.{self.module_id}'
                self.config.update({
                    'enabled': self.enabled,
                    'order': self.order
                })
                self.app_manager.config_manager.set(config_key, self.config)
        except Exception as e:
            self.logger.warning(f"保存配置失败: {e}")
    
    def start_updates(self, interval_ms: int = 1000) -> None:
        """
        开始定期更新

        Args:
            interval_ms: 更新间隔（毫秒）
        """
        if self.enabled:
            self.update_timer.start(interval_ms)
            # 立即更新一次内容
            self.update_content()
            self.logger.debug(f"模块 {self.module_id} 开始更新，间隔 {interval_ms}ms")
    
    def stop_updates(self) -> None:
        """停止定期更新"""
        self.update_timer.stop()
        self.logger.debug(f"模块 {self.module_id} 停止更新")
    
    def set_enabled(self, enabled: bool) -> None:
        """
        设置模块启用状态
        
        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
        if enabled:
            self.start_updates()
        else:
            self.stop_updates()
        self.save_config()
    
    def cleanup(self) -> None:
        """清理资源"""
        self.stop_updates()
        self.logger.debug(f"模块 {self.module_id} 清理完成")


class TimeModule(FloatingModule):
    """时间显示模块"""
    
    def __init__(self, app_manager: Optional['AppManager'] = None):
        super().__init__('time', app_manager)
        self.format_24h = True
        self.show_seconds = True
        self.timezone_offset = 0
        
        # 从配置加载设置
        self.format_24h = self.config.get('format_24h', True)
        self.show_seconds = self.config.get('show_seconds', True)
        self.timezone_offset = self.config.get('timezone_offset', 0)
    
    def get_display_text(self) -> str:
        """获取时间显示文本"""
        try:
            now = datetime.now()
            if self.timezone_offset != 0:
                now += timedelta(hours=self.timezone_offset)
            
            if self.format_24h:
                if self.show_seconds:
                    return now.strftime("%H:%M:%S")
                else:
                    return now.strftime("%H:%M")
            else:
                if self.show_seconds:
                    return now.strftime("%I:%M:%S %p")
                else:
                    return now.strftime("%I:%M %p")
        except Exception as e:
            self.logger.error(f"获取时间失败: {e}")
            return "时间错误"
    
    def get_tooltip_text(self) -> str:
        """获取时间工具提示"""
        try:
            now = datetime.now()
            return f"当前时间: {now.strftime('%Y年%m月%d日 %A')}"
        except Exception as e:
            return "时间信息不可用"
    
    def update_content(self) -> None:
        """更新时间内容"""
        text = self.get_display_text()
        self.content_updated.emit(text)


class ScheduleModule(FloatingModule):
    """课程表模块"""
    
    def __init__(self, app_manager: Optional['AppManager'] = None):
        super().__init__('schedule', app_manager)
        self.current_class = None
        self.next_class = None
    
    def get_display_text(self) -> str:
        """获取课程显示文本"""
        try:
            # 获取当前课程信息
            current_info = self.get_current_class_info()
            
            if current_info['status'] == 'in_class':
                return f"📚 {current_info['name']} | {current_info['room']}"
            elif current_info['status'] == 'break':
                return f"⏰ 课间 | 下节: {current_info['next_name']}"
            else:
                return "📖 今日课程已结束"
                
        except Exception as e:
            self.logger.error(f"获取课程信息失败: {e}")
            return "课程信息不可用"
    
    def get_tooltip_text(self) -> str:
        """获取课程工具提示"""
        try:
            current_info = self.get_current_class_info()
            if current_info['status'] == 'in_class':
                return f"当前课程: {current_info['name']}\n教室: {current_info['room']}\n剩余时间: {current_info['remaining']}"
            elif current_info['status'] == 'break':
                return f"课间休息\n下节课程: {current_info['next_name']}\n开始时间: {current_info['next_time']}"
            else:
                return "今日课程已全部结束"
        except Exception as e:
            return "课程信息不可用"
    
    def get_current_class_info(self) -> Dict[str, Any]:
        """获取当前课程信息"""
        try:
            # 这里应该从 schedule_manager 获取实际数据
            # 暂时返回模拟数据
            now = datetime.now()
            hour = now.hour
            
            if 8 <= hour < 12:
                return {
                    'status': 'in_class',
                    'name': '数学',
                    'room': 'A101',
                    'remaining': '25分钟'
                }
            elif 14 <= hour < 17:
                return {
                    'status': 'break',
                    'next_name': '物理',
                    'next_time': '14:30'
                }
            else:
                return {'status': 'finished'}
                
        except Exception as e:
            self.logger.error(f"获取课程信息失败: {e}")
            return {'status': 'error'}
    
    def update_content(self) -> None:
        """更新课程内容"""
        text = self.get_display_text()
        self.content_updated.emit(text)


class CountdownModule(FloatingModule):
    """倒计时模块"""
    
    def __init__(self, app_manager: Optional['AppManager'] = None):
        super().__init__('countdown', app_manager)
        self.events = []
        self.load_countdown_events()
    
    def get_display_text(self) -> str:
        """获取倒计时显示文本"""
        try:
            nearest_event = self.get_nearest_event()
            if not nearest_event:
                return "📅 暂无倒计时事件"
            
            remaining = self.calculate_remaining_time(nearest_event['target_time'])
            return f"⏳ {nearest_event['name']}: {remaining}"
            
        except Exception as e:
            self.logger.error(f"获取倒计时失败: {e}")
            return "倒计时错误"
    
    def get_tooltip_text(self) -> str:
        """获取倒计时工具提示"""
        try:
            nearest_event = self.get_nearest_event()
            if not nearest_event:
                return "暂无倒计时事件"
            
            return f"事件: {nearest_event['name']}\n目标时间: {nearest_event['target_time']}\n描述: {nearest_event.get('description', '无')}"
        except Exception as e:
            return "倒计时信息不可用"
    
    def load_countdown_events(self) -> None:
        """加载倒计时事件"""
        try:
            # 从配置或数据库加载倒计时事件
            # 暂时使用模拟数据
            self.events = [
                {
                    'name': '期末考试',
                    'target_time': datetime(2024, 1, 15, 9, 0),
                    'description': '数学期末考试'
                },
                {
                    'name': '寒假开始',
                    'target_time': datetime(2024, 1, 20, 0, 0),
                    'description': '寒假正式开始'
                }
            ]
        except Exception as e:
            self.logger.error(f"加载倒计时事件失败: {e}")
            self.events = []
    
    def get_nearest_event(self) -> Optional[Dict[str, Any]]:
        """获取最近的倒计时事件"""
        try:
            now = datetime.now()
            future_events = [e for e in self.events if e['target_time'] > now]
            if not future_events:
                return None
            
            return min(future_events, key=lambda x: x['target_time'])
        except Exception as e:
            self.logger.error(f"获取最近事件失败: {e}")
            return None
    
    def calculate_remaining_time(self, target_time: datetime) -> str:
        """计算剩余时间"""
        try:
            now = datetime.now()
            remaining = target_time - now
            
            if remaining.days > 0:
                return f"{remaining.days}天"
            elif remaining.seconds > 3600:
                hours = remaining.seconds // 3600
                return f"{hours}小时"
            elif remaining.seconds > 60:
                minutes = remaining.seconds // 60
                return f"{minutes}分钟"
            else:
                return "即将到达"
        except Exception as e:
            return "计算错误"
    
    def update_content(self) -> None:
        """更新倒计时内容"""
        text = self.get_display_text()
        self.content_updated.emit(text)


class WeatherModule(FloatingModule):
    """天气信息模块"""

    def __init__(self, app_manager: Optional['AppManager'] = None):
        super().__init__('weather', app_manager)
        self.weather_data = {}
        self.api_key = self.config.get('api_key', '')
        self.city = self.config.get('city', 'Beijing')
        self.last_update = None
        self.update_interval = 30 * 60 * 1000  # 30分钟

    def get_display_text(self) -> str:
        """获取天气显示文本"""
        try:
            if not self.weather_data:
                return "🌤️ 天气加载中..."

            temp = self.weather_data.get('temperature', '--')
            desc = self.weather_data.get('description', '未知')
            icon = self.get_weather_icon(self.weather_data.get('condition', ''))

            return f"{icon} {temp}°C | {desc}"

        except Exception as e:
            self.logger.error(f"获取天气显示失败: {e}")
            return "🌤️ 天气不可用"

    def get_tooltip_text(self) -> str:
        """获取天气工具提示"""
        try:
            if not self.weather_data:
                return "天气信息加载中..."

            return (f"城市: {self.city}\n"
                   f"温度: {self.weather_data.get('temperature', '--')}°C\n"
                   f"体感温度: {self.weather_data.get('feels_like', '--')}°C\n"
                   f"湿度: {self.weather_data.get('humidity', '--')}%\n"
                   f"天气: {self.weather_data.get('description', '未知')}\n"
                   f"更新时间: {self.last_update or '未更新'}")
        except Exception as e:
            return "天气信息不可用"

    def get_weather_icon(self, condition: str) -> str:
        """根据天气条件获取图标"""
        icon_map = {
            'clear': '☀️',
            'clouds': '☁️',
            'rain': '🌧️',
            'snow': '❄️',
            'thunderstorm': '⛈️',
            'drizzle': '🌦️',
            'mist': '🌫️',
            'fog': '🌫️'
        }
        return icon_map.get(condition.lower(), '🌤️')

    def fetch_weather_data(self) -> None:
        """获取天气数据"""
        try:
            if not self.api_key:
                self.logger.warning("天气API密钥未配置")
                return

            # 使用 OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.weather_data = {
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'condition': data['weather'][0]['main']
            }

            self.last_update = datetime.now().strftime('%H:%M')
            self.logger.debug("天气数据更新成功")

        except requests.RequestException as e:
            self.logger.error(f"获取天气数据失败: {e}")
            self.error_occurred.emit(f"天气数据获取失败: {e}")
        except Exception as e:
            self.logger.error(f"处理天气数据失败: {e}")

    def update_content(self) -> None:
        """更新天气内容"""
        # 检查是否需要更新数据
        if (not self.last_update or
            not self.weather_data or
            (datetime.now() - datetime.strptime(self.last_update, '%H:%M')).seconds > 1800):
            self.fetch_weather_data()

        text = self.get_display_text()
        self.content_updated.emit(text)

    def start_updates(self, interval_ms: int = None) -> None:
        """开始天气更新"""
        super().start_updates(self.update_interval)


class SystemStatusModule(FloatingModule):
    """系统状态模块"""

    def __init__(self, app_manager: Optional['AppManager'] = None):
        super().__init__('system', app_manager)
        self.show_cpu = self.config.get('show_cpu', True)
        self.show_memory = self.config.get('show_memory', True)
        self.show_network = self.config.get('show_network', False)

    def get_display_text(self) -> str:
        """获取系统状态显示文本"""
        try:
            status_parts = []

            if self.show_cpu:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                status_parts.append(f"CPU: {cpu_percent:.0f}%")

            if self.show_memory:
                memory = psutil.virtual_memory()
                status_parts.append(f"内存: {memory.percent:.0f}%")

            if self.show_network:
                # 简化的网络状态
                status_parts.append("🌐")

            return " | ".join(status_parts) if status_parts else "💻 系统正常"

        except Exception as e:
            self.logger.error(f"获取系统状态失败: {e}")
            return "💻 系统状态不可用"

    def get_tooltip_text(self) -> str:
        """获取系统状态工具提示"""
        try:
            # CPU 信息
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            # 内存信息
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)

            # 磁盘信息
            disk = psutil.disk_usage('/')
            disk_gb = disk.total / (1024**3)
            disk_used_gb = disk.used / (1024**3)

            return (f"CPU: {cpu_percent:.1f}% ({cpu_count}核)\n"
                   f"内存: {memory.percent:.1f}% ({memory_used_gb:.1f}GB/{memory_gb:.1f}GB)\n"
                   f"磁盘: {disk.percent:.1f}% ({disk_used_gb:.1f}GB/{disk_gb:.1f}GB)")

        except Exception as e:
            return "系统信息不可用"

    def update_content(self) -> None:
        """更新系统状态内容"""
        text = self.get_display_text()
        self.content_updated.emit(text)

    def start_updates(self, interval_ms: int = None) -> None:
        """开始系统状态更新"""
        super().start_updates(5000)  # 5秒更新一次
