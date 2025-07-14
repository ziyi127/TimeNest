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
TimeNest 天气组件UI
显示天气信息的用户界面组件
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap, QIcon

from core.weather_service import WeatherService, WeatherData

class WeatherWidget(QWidget):
    """
    天气显示组件
    
    显示当前天气信息，包括温度、天气状况、空气质量等
    """
    
    # 信号定义
    weather_clicked = pyqtSignal()  # 天气组件被点击
    refresh_requested = pyqtSignal()  # 请求刷新天气
    
    def __init__(self, weather_service: WeatherService, parent=None):
        """
        初始化天气组件
        
        Args:
            weather_service: 天气服务实例
            parent: 父组件
        """
        super().__init__(parent)
        
        self.weather_service = weather_service
        self.logger = logging.getLogger(f'{__name__}.WeatherWidget')
        
        # 当前天气数据
        self.current_weather: Optional[WeatherData] = None
        
        # UI组件
        self.main_layout: Optional[QVBoxLayout] = None
        self.header_layout: Optional[QHBoxLayout] = None
        self.content_layout: Optional[QVBoxLayout] = None
        
        self.title_label: Optional[QLabel] = None
        self.refresh_button: Optional[QPushButton] = None
        self.weather_icon: Optional[QLabel] = None
        self.temperature_label: Optional[QLabel] = None
        self.condition_label: Optional[QLabel] = None
        self.location_label: Optional[QLabel] = None
        self.humidity_label: Optional[QLabel] = None
        self.wind_label: Optional[QLabel] = None
        self.air_quality_label: Optional[QLabel] = None
        self.update_time_label: Optional[QLabel] = None
        
        # 初始化UI
        self.init_ui()
        self.init_connections()
        
        # 设置样式
        self.apply_styles()
        
        # 加载初始数据
        self.load_weather_data()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        try:
            # 设置组件属性
            self.setFixedSize(280, 200)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            
            # 主布局
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(10, 10, 10, 10)
            self.main_layout.setSpacing(8)
            
            # 标题栏
            self.header_layout = QHBoxLayout()
            
            self.title_label = QLabel("天气")
            self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
            self.header_layout.addWidget(self.title_label)
            
            self.header_layout.addStretch()
            
            self.refresh_button = QPushButton("刷新")
            self.refresh_button.setFixedSize(50, 25)
            self.refresh_button.clicked.connect(self.refresh_weather)
            self.header_layout.addWidget(self.refresh_button)
            
            self.main_layout.addLayout(self.header_layout)
            
            # 分隔线
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            self.main_layout.addWidget(separator)
            
            # 内容区域
            self.content_layout = QVBoxLayout()
            self.content_layout.setSpacing(5)
            
            # 天气图标和温度
            weather_layout = QHBoxLayout()
            
            self.weather_icon = QLabel()
            self.weather_icon.setFixedSize(48, 48)
            self.weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_icon.setStyleSheet("border: 1px solid #ddd; border-radius: 4px;")
            weather_layout.addWidget(self.weather_icon)
            
            temp_layout = QVBoxLayout()
            
            self.temperature_label = QLabel("--°C")
            self.temperature_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
            self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp_layout.addWidget(self.temperature_label)
            
            self.condition_label = QLabel("--")
            self.condition_label.setFont(QFont("Microsoft YaHei", 10))
            self.condition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp_layout.addWidget(self.condition_label)
            
            weather_layout.addLayout(temp_layout)
            weather_layout.addStretch()
            
            self.content_layout.addLayout(weather_layout)
            
            # 位置信息
            self.location_label = QLabel("位置: --")
            self.location_label.setFont(QFont("Microsoft YaHei", 9))
            self.content_layout.addWidget(self.location_label)
            
            # 详细信息
            details_layout = QHBoxLayout()
            
            left_details = QVBoxLayout()
            self.humidity_label = QLabel("湿度: --%")
            self.humidity_label.setFont(QFont("Microsoft YaHei", 9))
            left_details.addWidget(self.humidity_label)
            
            self.wind_label = QLabel("风速: -- km/h")
            self.wind_label.setFont(QFont("Microsoft YaHei", 9))
            left_details.addWidget(self.wind_label)
            
            details_layout.addLayout(left_details)
            
            right_details = QVBoxLayout()
            self.air_quality_label = QLabel("空气质量: --")
            self.air_quality_label.setFont(QFont("Microsoft YaHei", 9))
            right_details.addWidget(self.air_quality_label)
            
            details_layout.addLayout(right_details)
            
            self.content_layout.addLayout(details_layout)
            
            # 更新时间
            self.update_time_label = QLabel("更新时间: --")
            self.update_time_label.setFont(QFont("Microsoft YaHei", 8))
            self.update_time_label.setStyleSheet("color: #666;")
            self.content_layout.addWidget(self.update_time_label)
            
            self.main_layout.addLayout(self.content_layout)
            self.main_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")
    
    def init_connections(self):
        """
        初始化信号连接
        """
        try:
            # 连接天气服务信号
            if self.weather_service:
                self.weather_service.weather_updated.connect(self.on_weather_updated)
                self.weather_service.weather_error.connect(self.on_weather_error)
            
            # 点击事件
            self.mousePressEvent = self.on_widget_clicked
            
        except Exception as e:
            self.logger.error(f"初始化信号连接失败: {e}")
    
    def apply_styles(self):
        """
        应用样式
        """
        try:
            self.setStyleSheet("""
                WeatherWidget {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                WeatherWidget:hover {
                    border-color: #3498db;
                    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
                }
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """)
            
        except Exception as e:
            self.logger.error(f"应用样式失败: {e}")
    
    def load_weather_data(self):
        """
        加载天气数据
        """
        try:
            if self.weather_service:
                # 获取当前天气数据:
                # 获取当前天气数据
                self.current_weather = self.weather_service.get_current_weather()
                self.update_display()
            
        except Exception as e:
            self.logger.error(f"加载天气数据失败: {e}")
    
    def refresh_weather(self):
        """
        刷新天气数据
        """
        try:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("刷新中...")
            
            
            if self.weather_service:
                self.weather_service.update_weather()
            
                self.weather_service.update_weather()
            
            self.refresh_requested.emit()
            
            # 2秒后恢复按钮状态
            QTimer.singleShot(2000, self.restore_refresh_button)
            
        except Exception as e:
            self.logger.error(f"刷新天气失败: {e}")
            self.restore_refresh_button()
    
    def restore_refresh_button(self):
        """
        恢复刷新按钮状态
        """
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("刷新")
    
    def on_weather_updated(self, weather_data: WeatherData):
        """
        天气数据更新处理
        
        Args:
            weather_data: 新的天气数据
        """
        try:
            self.current_weather = weather_data
            self.update_display()
            
        except Exception as e:
            self.logger.error(f"处理天气更新失败: {e}")
    
    def on_weather_error(self, error_message: str):
        """
        天气错误处理
        
        Args:
            error_message: 错误信息
        """
        try:
            self.logger.warning(f"天气服务错误: {error_message}")
            
            # 显示错误状态
            self.temperature_label.setText("错误")
            self.condition_label.setText(error_message)
            
        except Exception as e:
            self.logger.error(f"处理天气错误失败: {e}")
    
    def update_display(self):
        """
        更新显示内容
        """
        try:
            if not self.current_weather:
                return
            
            # 更新温度
            if self.current_weather.temperature is not None:
                self.temperature_label.setText(f"{self.current_weather.temperature:.1f}°C")
            
            # 更新天气状况
            if self.current_weather.condition:
                self.condition_label.setText(self.current_weather.condition.value)
            
            # 更新位置
            if self.current_weather.location:
                self.location_label.setText(f"位置: {self.current_weather.location}")
            
            # 更新湿度
            if self.current_weather.humidity is not None:
                self.humidity_label.setText(f"湿度: {self.current_weather.humidity}%")
            
            # 更新风速
            if self.current_weather.wind_speed is not None:
                self.wind_label.setText(f"风速: {self.current_weather.wind_speed:.1f} km/h")
            
            # 更新空气质量
            if self.current_weather.air_quality:
                self.air_quality_label.setText(f"空气质量: {self.current_weather.air_quality.value}")
            
            # 更新时间
            if self.current_weather.timestamp:
                time_str = self.current_weather.timestamp.strftime("%H:%M")
                self.update_time_label.setText(f"更新时间: {time_str}")
            
            # 更新天气图标
            self.update_weather_icon()
            
        except Exception as e:
            self.logger.error(f"更新显示失败: {e}")
    
    def update_weather_icon(self):
        """
        更新天气图标
        """
        try:
            if not self.current_weather or not self.current_weather.condition:
                return
            
            # 根据天气状况设置图标
            condition = self.current_weather.condition
            icon_text = "☀️"  # 默认晴天图标
            
            
            if condition.name in ['CLOUDY', 'OVERCAST']:
                icon_text = "☁️"
            
                icon_text = "☁️"
            elif condition.name in ['RAINY', 'DRIZZLE']:
                icon_text = "🌧️"
            elif condition.name in ['SNOWY']:
                icon_text = "❄️"
            elif condition.name in ['THUNDERSTORM']:
                icon_text = "⛈️"
            elif condition.name in ['FOGGY', 'HAZY']:
                icon_text = "🌫️"
            
            self.weather_icon.setText(icon_text)
            self.weather_icon.setStyleSheet("""
                QLabel {
                    font-size: 32px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                }
            """)
            
        except Exception as e:
            self.logger.error(f"更新天气图标失败: {e}")
    
    def on_widget_clicked(self, event):
        """
        组件点击事件处理
        
        Args:
            event: 鼠标事件
        """
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.weather_clicked.emit()
            
        except Exception as e:
            self.logger.error(f"处理点击事件失败: {e}")
    
    def get_weather_data(self) -> Optional[WeatherData]:
        """
        获取当前天气数据
        
        Returns:
            当前天气数据
        """
        return self.current_weather
    
    def set_location(self, location: str):
        """
        设置位置
        
        Args:
            location: 位置名称
        """
        try:
            if self.weather_service:
                self.weather_service.set_location(location)
                self.refresh_weather()
            
        except Exception as e:
            self.logger.error(f"设置位置失败: {e}")
    
    def cleanup(self):
        """
        清理资源
        """
        try:
            # 断开天气服务信号连接
            if self.weather_service:
                if hasattr(self.weather_service, 'weather_updated'):
                    self.weather_service.weather_updated.disconnect()
                if hasattr(self.weather_service, 'weather_error'):
                    self.weather_service.weather_error.disconnect()
            
            # 断开按钮信号连接
            if self.refresh_button:
                self.refresh_button.clicked.disconnect()
            
            self.logger.debug("天气组件清理完成")
            
        except Exception as e:
            self.logger.error(f"清理天气组件失败: {e}")