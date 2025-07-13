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
        self.compact_mode = False
        self.auto_hide = False
        self.priority = 0
        
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
            
            
            if current_info and current_info['status'] == 'in_class':
                name = current_info.get('name', '未知课程')
            
                name = current_info.get('name', '未知课程')
                room = current_info.get('room', '未知教室')
                return f"📚 {name} | {room}"
            elif current_info and current_info['status'] == 'break':
                next_name = current_info.get('next_name', '未知课程')
                return f"⏰ 课间 | 下节: {next_name}"
            else:
                return "📖 今日课程已结束"
                
        except Exception as e:
            self.logger.error(f"获取课程信息失败: {e}")
            return "课程信息不可用"
    
    def get_tooltip_text(self) -> str:
        """获取课程工具提示"""
        try:
            current_info = self.get_current_class_info()
            if not current_info:
                return "课程信息不可用"

            status = current_info.get('status', 'no_class')
            if status == 'in_class':
                name = current_info.get('name', '未知课程')
                room = current_info.get('room', '未知教室')
                remaining = current_info.get('remaining', '未知')
                return f"当前课程: {name}\n教室: {room}\n剩余时间: {remaining}"
            elif status == 'break':
                next_name = current_info.get('next_name', '未知课程')
                next_time = current_info.get('next_time', '未知时间')
                return f"课间休息\n下节课程: {next_name}\n开始时间: {next_time}"
            else:
                return "今日课程已全部结束"
        except Exception as e:
            self.logger.error(f"获取课程工具提示失败: {e}")
            return "课程信息不可用"
    
    def get_current_class_info(self) -> Dict[str, Any]:
        """获取当前课程信息"""
        try:
            # 默认返回值，防止KeyError
            default_info = {
                'status': 'no_class',
                'name': '',
                'room': '',
                'remaining': '',
                'next_name': '',
                'next_time': ''
            }

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
            
            remaining = self.calculate_remaining_time(nearest_event.get('target_time'))
            return f"⏳ {nearest_event.get('name')}: {remaining}"
            
        except Exception as e:
            self.logger.error(f"获取倒计时失败: {e}")
            return "倒计时错误"
    
    def get_tooltip_text(self) -> str:
        """获取倒计时工具提示"""
        try:
            nearest_event = self.get_nearest_event()
            if not nearest_event:
                return "暂无倒计时事件"
            
            return f"事件: {nearest_event.get('name')}\n目标时间: {nearest_event.get('target_time')}\n描述: {nearest_event.get('description', '无')}"
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
            future_events = [e for e in self.events if e.get('target_time') > now]
            if not future_events:
                return None
            
            return min(future_events, key=lambda x: x.get('target_time'))
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
                'temperature': round(data.get('main')['temp']),
                'feels_like': round(data.get('main')['feels_like']),
                'humidity': data.get('main')['humidity'],
                'description': data.get('weather')[0]['description'],
                'condition': data.get('weather')[0]['main']
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

    def get_quick_actions(self) -> list[Dict[str, Any]]:
        """获取系统状态快速操作"""
        return [
            {
                'name': '打开任务管理器',
                'icon': '🖥️',
                'action': 'open_task_manager'
            },
            {
                'name': '系统信息',
                'icon': 'ℹ️',
                'action': 'show_system_info'
            }
        ]


class StudyProgressModule(FloatingModule):
    """学习进度模块"""

    def __init__(self, module_id: str, app_manager=None):
        super().__init__(module_id, "学习进度", app_manager)
        self.study_assistant = getattr(app_manager, 'study_assistant', None) if app_manager else None

        # 进度数据
        self.current_session = None
        self.daily_progress = 0.0
        self.weekly_progress = 0.0

    def create_content(self) -> QWidget:
        """创建学习进度内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 当前会话
        self.session_label = QLabel("无活动会话")
        self.session_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.session_label)

        # 今日进度
        self.daily_label = QLabel("今日: 0分钟")
        layout.addWidget(self.daily_label)

        # 本周进度
        self.weekly_label = QLabel("本周: 0分钟")
        layout.addWidget(self.weekly_label)

        # 进度条
        from PyQt6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 16px;
            }
            QProgressBar:chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        return widget

    def update_content(self):
        """更新学习进度内容"""
        try:
            if not self.study_assistant:
                return

            # 获取今日总结
            daily_summary = self.study_assistant.get_daily_study_summary()
            if daily_summary:
                daily_time = daily_summary.get('total_study_time', 0)
                goal_progress = daily_summary.get('goal_progress', 0.0)

                self.daily_label.setText(f"今日: {daily_time}分钟")
                self.progress_bar.setValue(int(goal_progress * 100))

            # 获取学习分析
            analytics = self.study_assistant.get_learning_analytics()
            if analytics:
                # 计算本周时间（简化计算）
                weekly_time = analytics.total_study_time
                self.weekly_label.setText(f"本周: {weekly_time}分钟")

            # 检查活动会话
            if (hasattr(self.study_assistant, 'schedule_enhancement') and
                self.study_assistant.schedule_enhancement.active_session):
                session = self.study_assistant.schedule_enhancement.active_session
                task = self.study_assistant.schedule_enhancement.get_task_by_id(session.task_id)
                if task:
                    elapsed = (datetime.now() - session.start_time).total_seconds() / 60
                    self.session_label.setText(f"学习中: {task.title} ({elapsed:.0f}分钟)")
                else:
                    self.session_label.setText("学习会话进行中")
            else:
                self.session_label.setText("无活动会话")

        except Exception as e:
            self.logger.error(f"更新学习进度失败: {e}")

    def get_quick_actions(self) -> list[Dict[str, Any]]:
        """获取学习进度快速操作"""
        return [
            {
                'name': '开始学习',
                'icon': '📚',
                'action': 'start_study'
            },
            {
                'name': '查看统计',
                'icon': '📊',
                'action': 'show_statistics'
            },
            {
                'name': '设置目标',
                'icon': '🎯',
                'action': 'set_goal'
            }
        ]


class EnvironmentModule(FloatingModule):
    """学习环境模块"""

    def __init__(self, module_id: str, app_manager=None):
        super().__init__(module_id, "学习环境", app_manager)
        self.environment_optimizer = getattr(app_manager, 'environment_optimizer', None) if app_manager else None

        # 环境数据
        self.environment_score = 0.0
        self.environment_grade = "未知"

    def create_content(self) -> QWidget:
        """创建学习环境内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 环境评分
        self.score_label = QLabel("环境评分: --")
        self.score_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.score_label)

        # 环境等级
        self.grade_label = QLabel("等级: 未知")
        layout.addWidget(self.grade_label)

        # 建议数量
        self.suggestions_label = QLabel("建议: 0条")
        layout.addWidget(self.suggestions_label)

        # 状态指示器
        self.status_widget = QWidget()
        self.status_widget.setFixedHeight(8)
        self.status_widget.setStyleSheet("background-color: #ccc; border-radius: 4px;")
        layout.addWidget(self.status_widget)

        return widget

    def update_content(self):
        """更新学习环境内容"""
        try:
            if not self.environment_optimizer:
                return

            # 获取环境总结
            summary = self.environment_optimizer.get_environment_summary()
            if summary['status'] == 'success':
                score = summary.get('overall_score', 0.0)
                grade = summary.get('grade', '未知')
                color = summary.get('color', 'gray')
                suggestions_count = summary.get('suggestions_count', 0)

                self.score_label.setText(f"环境评分: {score:.1%}")
                self.grade_label.setText(f"等级: {grade}")
                self.suggestions_label.setText(f"建议: {suggestions_count}条")

                # 更新状态颜色
                self.status_widget.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            else:
                self.score_label.setText("环境评分: 检测中...")
                self.grade_label.setText("等级: --")
                self.suggestions_label.setText("建议: --")

        except Exception as e:
            self.logger.error(f"更新学习环境失败: {e}")

    def get_quick_actions(self) -> list[Dict[str, Any]]:
        """获取环境模块快速操作"""
        return [
            {
                'name': '优化环境',
                'icon': '🔧',
                'action': 'optimize_environment'
            },
            {
                'name': '查看建议',
                'icon': '💡',
                'action': 'show_suggestions'
            },
            {
                'name': '刷新检测',
                'icon': '🔄',
                'action': 'refresh_detection'
            }
        ]


class ResourceQuickAccessModule(FloatingModule):
    """资源快速访问模块"""

    def __init__(self, module_id: str, app_manager=None):
        super().__init__(module_id, "快速资源", app_manager)
        self.resource_manager = getattr(app_manager, 'resource_manager', None) if app_manager else None

        # 最近资源
        self.recent_resources = []
        self.favorite_resources = []

    def create_content(self) -> QWidget:
        """创建资源快速访问内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 最近使用
        recent_label = QLabel("最近使用:")
        recent_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px;")
        layout.addWidget(recent_label)

        self.recent_list = QLabel("暂无资源")
        self.recent_list.setStyleSheet("color: #666; font-size: 10px;")
        self.recent_list.setWordWrap(True)
        layout.addWidget(self.recent_list)

        # 收藏资源
        favorite_label = QLabel("收藏资源:")
        favorite_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px;")
        layout.addWidget(favorite_label)

        self.favorite_list = QLabel("暂无收藏")
        self.favorite_list.setStyleSheet("color: #666; font-size: 10px;")
        self.favorite_list.setWordWrap(True)
        layout.addWidget(self.favorite_list)

        return widget

    def update_content(self):
        """更新资源快速访问内容"""
        try:
            if not self.resource_manager:
                return

            # 获取最近访问的资源
            recent_resources = sorted(
                [r for r in self.resource_manager.resources.values() if r.last_accessed],
                key=lambda r: r.last_accessed,
                reverse=True
            )[:3]


            if recent_resources:
                recent_text = "\n".join([f"• {r.title[:20]}..." if len(r.title) > 20 else f"• {r.title}"
                                       for r in recent_resources])
                self.recent_list.setText(recent_text)
            else:
                self.recent_list.setText("暂无最近资源")

            # 获取高评分资源作为"收藏"
            favorite_resources = sorted(
                [r for r in self.resource_manager.resources.values() if r.rating >= 4],
                key=lambda r: r.rating,
                reverse=True
            )[:3]


            if favorite_resources:
                favorite_text = "\n".join([f"⭐ {r.title[:20]}..." if len(r.title) > 20 else f"⭐ {r.title}"
                                         for r in favorite_resources])
                self.favorite_list.setText(favorite_text)
            else:
                self.favorite_list.setText("暂无收藏资源")

        except Exception as e:
            self.logger.error(f"更新资源快速访问失败: {e}")

    def get_quick_actions(self) -> list[Dict[str, Any]]:
        """获取资源快速操作"""
        return [
            {
                'name': '添加资源',
                'icon': '➕',
                'action': 'add_resource'
            },
            {
                'name': '搜索资源',
                'icon': '🔍',
                'action': 'search_resources'
            },
            {
                'name': '资源管理',
                'icon': '📁',
                'action': 'manage_resources'
            }
        ]


class FocusModeModule(FloatingModule):
    """专注模式模块"""

    def __init__(self, module_id: str, app_manager=None):
        super().__init__(module_id, "专注模式", app_manager)
        self.notification_enhancement = getattr(app_manager, 'notification_enhancement', None) if app_manager else None

        # 专注状态
        self.is_focus_active = False
        self.focus_remaining = 0

    def create_content(self) -> QWidget:
        """创建专注模式内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 专注状态
        self.status_label = QLabel("专注模式: 未激活")
        self.status_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.status_label)

        # 剩余时间
        self.time_label = QLabel("--:--")
        self.time_label.setStyleSheet("font-size: 16px; color: #007ACC;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)

        # 控制按钮
        from PyQt6.QtWidgets import QPushButton
        self.control_button = QPushButton("开始专注")
        self.control_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.control_button.clicked.connect(self._toggle_focus_mode)
        layout.addWidget(self.control_button)

        return widget

    def update_content(self):
        """更新专注模式内容"""
        try:
            if not self.notification_enhancement:
                return

            # 获取专注模式状态
            status = self.notification_enhancement.get_focus_mode_status()


            if status.get('active'):
                self.is_focus_active = True
                remaining = status.get('remaining_minutes', 0)

                self.status_label.setText("专注模式: 激活中")
                self.time_label.setText(f"{int(remaining):02d}:{int((remaining % 1) * 60):02d}")
                self.control_button.setText("结束专注")
                self.control_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                    }
                """)
            else:
                self.is_focus_active = False
                self.status_label.setText("专注模式: 未激活")
                self.time_label.setText("--:--")
                self.control_button.setText("开始专注")
                self.control_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)

        except Exception as e:
            self.logger.error(f"更新专注模式失败: {e}")

    def _toggle_focus_mode(self):
        """切换专注模式"""
        try:
            if not self.notification_enhancement:
                return


            if self.is_focus_active:
                # 结束专注模式
                self.notification_enhancement.end_focus_mode()
            else:
                # 开始专注模式
                self.notification_enhancement.start_focus_mode(duration=25)

        except Exception as e:
            self.logger.error(f"切换专注模式失败: {e}")

    def get_quick_actions(self) -> list[Dict[str, Any]]:
        """获取专注模式快速操作"""
        return [
            {
                'name': '25分钟专注',
                'icon': '🍅',
                'action': 'focus_25'
            },
            {
                'name': '45分钟专注',
                'icon': '⏰',
                'action': 'focus_45'
            },
            {
                'name': '自定义时长',
                'icon': '⚙️',
                'action': 'custom_focus'
            }
        ]
