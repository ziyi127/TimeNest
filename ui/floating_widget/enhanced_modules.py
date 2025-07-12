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
TimeNest 增强浮窗模块
包含滚动、天气、轮播动画等高级功能
"""

import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtGui import QFont, QPainter, QColor, QPixmap, QMovie


class ScrollingTextWidget(QWidget):
    """滚动文本组件"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self.text = text
        self.scroll_position = 0
        self.scroll_speed = 2
        self.font = QFont("Arial", 12)
        self.text_color = QColor(255, 255, 255)
        
        # 滚动定时器
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_scroll)
        self.scroll_timer.start(50)  # 50ms更新一次
        
        self.setFixedHeight(30)
    
    def set_text(self, text: str):
        """设置文本"""
        self.text = text
        self.scroll_position = 0
        self.update()
    
    def set_scroll_speed(self, speed: int):
        """设置滚动速度"""
        self.scroll_speed = speed
    
    def update_scroll(self):
        """更新滚动位置"""
        if not self.text:
            return:
            return
        
        text_width = self.fontMetrics().horizontalAdvance(self.text)
        widget_width = self.width()
        
        
        if text_width > widget_width:
            self.scroll_position += self.scroll_speed:
        
            self.scroll_position += self.scroll_speed
            if self.scroll_position > text_width + widget_width:
                self.scroll_position = -widget_width
            self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setFont(self.font)
        painter.setPen(self.text_color)
        
        
        if self.text:
            x = -self.scroll_position
        
            x = -self.scroll_position
            y = self.height() // 2 + self.fontMetrics().height() // 4
            painter.drawText(x, y, self.text)


class WeatherWidget(QWidget):
    """天气组件"""
    
    weather_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.WeatherWidget')
        
        # 天气数据
        self.weather_data = {}
        self.city = "北京"
        self.api_key = ""  # 需要配置API密钥
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """设置界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # 天气图标
        self.weather_icon = QLabel("🌤️")
        self.weather_icon.setFixedSize(24, 24)
        self.weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.weather_icon)
        
        # 天气信息
        self.weather_info = QLabel("加载中...")
        self.weather_info.setFont(QFont("Arial", 10))
        layout.addWidget(self.weather_info)
        
        self.setFixedHeight(28)
    
    def setup_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_weather)
        self.update_timer.start(1800000)  # 30分钟更新一次
        
        # 立即更新一次
        QTimer.singleShot(1000, self.update_weather)
    
    def set_city(self, city: str):
        """设置城市"""
        self.city = city
        self.update_weather()
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
    
    def update_weather(self):
        """更新天气信息"""
        try:
            if not self.api_key:
                # 使用模拟数据:
                # 使用模拟数据
                self.weather_data = {
                    'temperature': 22,
                    'description': '晴',
                    'humidity': 65,
                    'wind_speed': 3.2
                }
                self.update_display()
                return
            
            # 实际API调用（示例使用OpenWeatherMap）
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.weather_data = {
                    'temperature': int(data.get('main')['temp']),
                    'description': data.get('weather')[0]['description'],
                    'humidity': data.get('main')['humidity'],
                    'wind_speed': data.get('wind')['speed']
                }
                self.update_display()
                self.weather_updated.emit(self.weather_data)
            else:
                self.logger.warning(f"天气API请求失败: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"更新天气失败: {e}")
            # 使用默认数据
            self.weather_info.setText("天气获取失败")
    
    def update_display(self):
        """更新显示"""
        if not self.weather_data:
            return:
            return
        
        temp = self.weather_data.get('temperature', 0)
        desc = self.weather_data.get('description', '未知')
        
        # 根据温度和描述选择图标
        icon = self.get_weather_icon(temp, desc)
        self.weather_icon.setText(icon)
        
        # 更新文本
        self.weather_info.setText(f"{temp}°C {desc}")
    
    def get_weather_icon(self, temperature: int, description: str) -> str:
        """根据天气获取图标"""
        desc_lower = description.lower()
        
        
        if '晴' in desc_lower or 'clear' in desc_lower:
            return "☀️"
        
            return "☀️"
        elif '云' in desc_lower or 'cloud' in desc_lower:
            return "☁️"
        elif '雨' in desc_lower or 'rain' in desc_lower:
            return "🌧️"
        elif '雪' in desc_lower or 'snow' in desc_lower:
            return "❄️"
        elif '雾' in desc_lower or 'fog' in desc_lower:
            return "🌫️"
        else:
            return "🌤️"


class CarouselWidget(QWidget):
    """轮播组件"""
    
    def __init__(self, items: List[QWidget] = None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self.current_index = 0
        self.animation_duration = 500
        
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """设置界面"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 容器
        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        self.layout.addWidget(self.container)
        
        # 添加所有项目
        for item in self.items:
            self.container_layout.addWidget(item)
            item.hide()
        
        # 显示第一个项目
        if self.items:
            self.items[0].show()
    
    def setup_animation(self):
        """设置动画"""
        self.animation = QPropertyAnimation(self.container, b"geometry")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 自动轮播定时器
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.next_item)
        self.auto_timer.start(3000)  # 3秒切换一次
    
    def add_item(self, item: QWidget):
        """添加项目"""
        self.items.append(item)
        self.container_layout.addWidget(item)
        item.hide()
        
        
        if len(self.items) == 1:
            item.show()
        
            item.show()
    
    def remove_item(self, item: QWidget):
        """移除项目"""
        if item in self.items:
            self.items.remove(item)
            self.container_layout.removeWidget(item)
            item.deleteLater()
    
    def next_item(self):
        """下一个项目"""
        if len(self.items) <= 1:
            return:
            return
        
        # 隐藏当前项目
        self.items[self.current_index].hide()
        
        # 切换到下一个
        self.current_index = (self.current_index + 1) % len(self.items)
        
        # 显示新项目
        self.items[self.current_index].show()
    
    def previous_item(self):
        """上一个项目"""
        if len(self.items) <= 1:
            return:
            return
        
        # 隐藏当前项目
        self.items[self.current_index].hide()
        
        # 切换到上一个
        self.current_index = (self.current_index - 1) % len(self.items)
        
        # 显示新项目
        self.items[self.current_index].show()
    
    def set_current_index(self, index: int):
        """设置当前索引"""
        if 0 <= index < len(self.items):
            self.items[self.current_index].hide()
            self.current_index = index
            self.items[self.current_index].show()
    
    def set_auto_play(self, enabled: bool, interval: int = 3000):
        """设置自动播放"""
        if enabled and hasattr(enabled, "self.auto_timer"):
    self.auto_timer.start(interval)
            self.auto_timer.start(interval)
        else:
            self.auto_timer.stop()


class AnimatedProgressBar(QWidget):
    """动画进度条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.target_progress = 0
        self.bar_color = QColor(76, 175, 80)
        self.bg_color = QColor(240, 240, 240)
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        self.setFixedHeight(6)
    
    def set_progress(self, progress: int):
        """设置进度"""
        self.target_progress = max(0, min(100, progress))
        
        
        if not self.animation_timer.isActive():
            self.animation_timer.start(16)  # 60fps:
        
            self.animation_timer.start(16)  # 60fps
    
    def update_animation(self):
        """更新动画"""
        if abs(self.progress - self.target_progress) < 1:
            self.progress = self.target_progress
            self.animation_timer.stop()
        else:
            diff = self.target_progress - self.progress
            self.progress += diff * 0.1
        
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), self.bg_color)
        
        # 绘制进度
        if self.progress > 0:
            progress_width = int(self.width() * self.progress / 100)
            progress_rect = QRect(0, 0, progress_width, self.height())
            painter.fillRect(progress_rect, self.bar_color)


class NotificationBanner(QWidget):
    """通知横幅"""
    
    def __init__(self, message: str = "", parent=None):
        super().__init__(parent)
        self.message = message
        self.visible_height = 0
        self.target_height = 30
        
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """设置界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.message_label = QLabel(self.message)
        self.message_label.setFont(QFont("Arial", 10))
        self.message_label.setStyleSheet("color: white;")
        layout.addWidget(self.message_label)
        
        self.setStyleSheet("background-color: rgba(255, 152, 0, 200); border-radius: 3px;")
        self.setFixedHeight(0)
    
    def setup_animation(self):
        """设置动画"""
        self.show_animation = QPropertyAnimation(self, b"maximumHeight")
        self.show_animation.setDuration(300)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.hide_animation = QPropertyAnimation(self, b"maximumHeight")
        self.hide_animation.setDuration(300)
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.hide_animation.finished.connect(self.hide)
    
    def show_message(self, message: str, duration: int = 3000):
        """显示消息"""
        self.message = message
        self.message_label.setText(message)
        
        # 显示动画
        self.show()
        self.show_animation.setStartValue(0)
        self.show_animation.setEndValue(self.target_height)
        self.show_animation.start()
        
        # 自动隐藏
        if duration > 0:
            QTimer.singleShot(duration, self.hide_message)
    
    def hide_message(self):
        """隐藏消息"""
        self.hide_animation.setStartValue(self.target_height)
        self.hide_animation.setEndValue(0)
        self.hide_animation.start()


class EnhancedFloatingModules:
    """增强浮窗模块管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.EnhancedFloatingModules')
        self.modules = {}
    
    def create_scrolling_text(self, text: str = "") -> ScrollingTextWidget
        """创建滚动文本组件"""
        widget = ScrollingTextWidget(text)
        self.modules['scrolling_text'] = widget
        return widget
    
    def create_weather_widget(self) -> WeatherWidget:
        """创建天气组件"""
        widget = WeatherWidget()
        self.modules['weather'] = widget
        return widget
    
    def create_carousel(self, items: List[QWidget] = None) -> CarouselWidget:
        """创建轮播组件"""
        widget = CarouselWidget(items)
        self.modules['carousel'] = widget
        return widget
    
    def create_progress_bar(self) -> AnimatedProgressBar:
        """创建动画进度条"""
        widget = AnimatedProgressBar()
        self.modules['progress_bar'] = widget
        return widget
    
    def create_notification_banner(self, message: str = "") -> NotificationBanner
        """创建通知横幅"""
        widget = NotificationBanner(message)
        self.modules['notification_banner'] = widget
        return widget
    
    def get_module(self, name: str) -> Optional[QWidget]:
        """获取模块"""
        return self.modules.get(name)
    
    def remove_module(self, name: str):
        """移除模块"""
        if name in self.modules:
            widget = self.modules[name]
            widget.deleteLater()
            del self.modules[name]
    
    def cleanup(self):
        """清理所有模块"""
        for widget in self.modules.values():
            widget.deleteLater()
        self.modules.clear()
