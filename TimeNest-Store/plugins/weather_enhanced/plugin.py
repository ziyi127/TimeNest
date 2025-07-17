#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强天气插件
展示如何创建一个完整的TimeNest插件
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

# 导入插件基类
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from core.plugin_base import IPlugin, PluginStatus, PluginMetadata, PluginType


class WeatherWidget(QWidget):
    """天气显示组件"""
    
    def __init__(self, plugin_instance):
        super().__init__()
        self.plugin = plugin_instance
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 主要天气信息
        self.main_info = QLabel("获取天气中...")
        self.main_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        layout.addWidget(self.main_info)
        
        # 详细信息布局
        details_layout = QHBoxLayout()
        
        # 湿度信息
        self.humidity_label = QLabel("湿度: --")
        self.humidity_label.setStyleSheet("font-size: 10px; color: #666;")
        details_layout.addWidget(self.humidity_label)
        
        # 风速信息
        self.wind_label = QLabel("风速: --")
        self.wind_label.setStyleSheet("font-size: 10px; color: #666;")
        details_layout.addWidget(self.wind_label)
        
        layout.addLayout(details_layout)
        
        # 更新时间
        self.update_time = QLabel("更新时间: --")
        self.update_time.setStyleSheet("font-size: 8px; color: #999;")
        layout.addWidget(self.update_time)
    
    def update_weather_display(self, weather_data: Dict[str, Any]):
        """更新天气显示"""
        try:
            # 获取设置
            settings = self.plugin.get_settings()
            temp_unit = settings.get('temperature_unit', 'celsius')
            show_humidity = settings.get('show_humidity', True)
            show_wind = settings.get('show_wind', True)
            location = settings.get('location', '北京')
            
            # 主要信息
            temp = weather_data.get('temperature', 0)
            condition = weather_data.get('condition', '未知')
            
            if temp_unit == 'fahrenheit':
                temp = temp * 9/5 + 32
                unit = '°F'
            else:
                unit = '°C'
            
            self.main_info.setText(f"{location} {condition} {temp:.1f}{unit}")
            
            # 详细信息
            if show_humidity:
                humidity = weather_data.get('humidity', 0)
                self.humidity_label.setText(f"湿度: {humidity}%")
                self.humidity_label.setVisible(True)
            else:
                self.humidity_label.setVisible(False)
            
            if show_wind:
                wind_speed = weather_data.get('wind_speed', 0)
                self.wind_label.setText(f"风速: {wind_speed} km/h")
                self.wind_label.setVisible(True)
            else:
                self.wind_label.setVisible(False)
            
            # 更新时间
            current_time = datetime.now().strftime("%H:%M")
            self.update_time.setText(f"更新时间: {current_time}")
            
        except Exception as e:
            self.plugin.logger.error(f"更新天气显示失败: {e}")
            self.main_info.setText("天气信息获取失败")


class WeatherEnhancedPlugin(IPlugin):
    """增强天气插件"""
    
    # 定义信号
    weather_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.WeatherEnhancedPlugin')
        
        # 插件状态
        self.status = PluginStatus.LOADED
        
        # 组件
        self.weather_widget = None
        self.update_timer = None
        self.plugin_manager = None
        
        # 设置
        self.settings = {
            'api_key': '',
            'update_interval': 300,
            'show_humidity': True,
            'show_wind': True,
            'temperature_unit': 'celsius',
            'location': '北京'
        }
        
        # 天气数据
        self.current_weather = {}
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.logger.info("增强天气插件初始化开始")
            
            # 创建天气组件
            self.weather_widget = WeatherWidget(self)
            
            # 创建更新定时器
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_weather)
            
            # 连接信号
            self.weather_updated.connect(self.weather_widget.update_weather_display)
            
            self.status = PluginStatus.INITIALIZED
            self.logger.info("增强天气插件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            if self.status != PluginStatus.INITIALIZED:
                self.logger.error("插件未正确初始化")
                return False
            
            # 开始定时更新
            interval = self.settings.get('update_interval', 300) * 1000  # 转换为毫秒
            self.update_timer.start(interval)
            
            # 立即更新一次
            self.update_weather()
            
            self.status = PluginStatus.ENABLED
            self.logger.info("增强天气插件已激活")
            return True
            
        except Exception as e:
            self.logger.error(f"插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            # 停止定时器
            if self.update_timer:
                self.update_timer.stop()
            
            self.status = PluginStatus.DISABLED
            self.logger.info("增强天气插件已停用")
            return True
            
        except Exception as e:
            self.logger.error(f"插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理插件资源"""
        try:
            # 停用插件
            self.deactivate()
            
            # 清理组件
            if self.weather_widget:
                self.weather_widget.deleteLater()
                self.weather_widget = None
            
            if self.update_timer:
                self.update_timer.deleteLater()
                self.update_timer = None
            
            self.status = PluginStatus.UNLOADED
            self.logger.info("增强天气插件资源清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
            return False
    
    def update_weather(self):
        """更新天气信息"""
        try:
            # 模拟天气数据（实际应用中应该调用真实的天气API）
            import random
            
            conditions = ['晴天', '多云', '阴天', '小雨', '中雨', '雷阵雨', '雪']
            
            weather_data = {
                'temperature': random.randint(15, 30),
                'condition': random.choice(conditions),
                'humidity': random.randint(40, 80),
                'wind_speed': random.randint(5, 20)
            }
            
            self.current_weather = weather_data
            self.weather_updated.emit(weather_data)
            
            self.logger.debug(f"天气信息已更新: {weather_data}")
            
        except Exception as e:
            self.logger.error(f"更新天气信息失败: {e}")
    
    def get_widget(self) -> Optional[QWidget]:
        """获取插件组件"""
        return self.weather_widget
    
    def get_settings(self) -> Dict[str, Any]:
        """获取插件设置"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """更新插件设置"""
        try:
            self.settings.update(new_settings)
            
            # 更新定时器间隔
            if 'update_interval' in new_settings and self.update_timer:
                interval = new_settings['update_interval'] * 1000
                self.update_timer.setInterval(interval)
            
            # 重新更新显示
            if self.current_weather:
                self.weather_updated.emit(self.current_weather)
            
            self.logger.info("插件设置已更新")
            return True
            
        except Exception as e:
            self.logger.error(f"更新插件设置失败: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            'id': 'weather_enhanced',
            'name': '增强天气插件',
            'version': '1.0.0',
            'description': '提供详细的天气信息显示',
            'author': 'TimeNest Team',
            'status': self.status.value,
            'settings': self.settings
        }


# 插件入口点
def create_plugin():
    """创建插件实例"""
    return WeatherEnhancedPlugin()


# 用于测试的主函数
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建插件实例
    plugin = WeatherEnhancedPlugin()
    
    # 模拟插件管理器
    class MockPluginManager:
        pass
    
    # 初始化和激活插件
    plugin.initialize(MockPluginManager())
    plugin.activate()
    
    # 显示插件组件
    widget = plugin.get_widget()
    if widget:
        widget.show()
    
    sys.exit(app.exec())
