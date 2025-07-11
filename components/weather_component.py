# -*- coding: utf-8 -*-
"""
TimeNest 天气组件 - 增强版
显示详细天气信息，支持动画效果和多种数据源
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QGridLayout,
                           QProgressBar, QFrame, QScrollArea, QWidget)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QPen
import requests
import json

from .base_component import BaseComponent

class WeatherWorker(QThread):
    """天气数据获取工作线程 - 增强版"""

    weather_updated = pyqtSignal(dict)  # 当前天气数据
    forecast_updated = pyqtSignal(list)  # 预报数据
    air_quality_updated = pyqtSignal(dict)  # 空气质量数据
    error_occurred = pyqtSignal(str)  # 错误信息

    def __init__(self, api_key: str, city: str, provider: str = "openweather"):
        super().__init__()
        self.api_key = api_key
        self.city = city
        self.provider = provider
        self.running = True
        self.logger = logging.getLogger(f'{__name__}.WeatherWorker')

    def run(self):
        """获取天气数据"""
        try:
            if not self.api_key:
                # 使用模拟数据
                self._emit_mock_data()
                return

            if self.provider == "openweather":
                self._fetch_openweather_data()
            elif self.provider == "qweather":
                self._fetch_qweather_data()
            else:
                self._emit_mock_data()

        except Exception as e:
            self.logger.error(f"获取天气数据失败: {e}")
            self.error_occurred.emit(str(e))

    def _fetch_openweather_data(self):
        """获取OpenWeatherMap数据"""
        try:
            # 当前天气
            current_url = "http://api.openweathermap.org/data/2.5/weather"
            current_params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }

            response = requests.get(current_url, params=current_params, timeout=10)
            response.raise_for_status()
            current_data = response.json()

            # 处理当前天气数据
            weather_data = self._process_openweather_current(current_data)
            self.weather_updated.emit(weather_data)

            # 获取预报数据
            forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }

            response = requests.get(forecast_url, params=forecast_params, timeout=10)
            response.raise_for_status()
            forecast_data = response.json()

            # 处理预报数据
            forecast_list = self._process_openweather_forecast(forecast_data)
            self.forecast_updated.emit(forecast_list)

        except Exception as e:
            self.logger.error(f"获取OpenWeatherMap数据失败: {e}")
            raise

    def _process_openweather_current(self, data: dict) -> dict:
        """处理OpenWeatherMap当前天气数据"""
        try:
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            clouds = data.get('clouds', {})
            sys_data = data.get('sys', {})

            return {
                'temperature': round(main.get('temp', 0)),
                'feels_like': round(main.get('feels_like', 0)),
                'humidity': main.get('humidity', 0),
                'pressure': main.get('pressure', 0),
                'description': weather.get('description', ''),
                'icon': weather.get('icon', ''),
                'wind_speed': wind.get('speed', 0),
                'wind_direction': wind.get('deg', 0),
                'cloudiness': clouds.get('all', 0),
                'visibility': data.get('visibility', 0) / 1000,  # 转换为公里
                'sunrise': datetime.fromtimestamp(sys_data.get('sunrise', 0)),
                'sunset': datetime.fromtimestamp(sys_data.get('sunset', 0)),
                'city': data.get('name', self.city),
                'country': sys_data.get('country', ''),
                'update_time': datetime.now()
            }

        except Exception as e:
            self.logger.error(f"处理当前天气数据失败: {e}")
            return {}

    def _process_openweather_forecast(self, data: dict) -> List[dict]:
        """处理OpenWeatherMap预报数据"""
        try:
            forecast_list = []
            items = data.get('list', [])

            # 取未来5天的数据（每天取中午12点的数据）
            for item in items[:40]:  # 5天 * 8次/天
                dt = datetime.fromtimestamp(item.get('dt', 0))
                if dt.hour == 12:  # 只取中午的数据
                    main = item.get('main', {})
                    weather = item.get('weather', [{}])[0]

                    forecast_list.append({
                        'date': dt.date(),
                        'temperature_max': round(main.get('temp_max', 0)),
                        'temperature_min': round(main.get('temp_min', 0)),
                        'description': weather.get('description', ''),
                        'icon': weather.get('icon', ''),
                        'humidity': main.get('humidity', 0),
                        'pop': item.get('pop', 0) * 100  # 降水概率转换为百分比
                    })

                    if len(forecast_list) >= 5:
                        break

            return forecast_list

        except Exception as e:
            self.logger.error(f"处理预报数据失败: {e}")
            return []

    def _emit_mock_data(self):
        """发送模拟数据"""
        try:
            # 模拟当前天气
            mock_weather = {
                'temperature': 22,
                'feels_like': 24,
                'humidity': 65,
                'pressure': 1013,
                'description': '多云',
                'icon': '03d',
                'wind_speed': 3.5,
                'wind_direction': 180,
                'cloudiness': 40,
                'visibility': 10.0,
                'sunrise': datetime.now().replace(hour=6, minute=30),
                'sunset': datetime.now().replace(hour=18, minute=45),
                'city': self.city,
                'country': 'CN',
                'update_time': datetime.now()
            }
            self.weather_updated.emit(mock_weather)

            # 模拟预报数据
            mock_forecast = []
            for i in range(5):
                date = datetime.now().date() + timedelta(days=i+1)
                mock_forecast.append({
                    'date': date,
                    'temperature_max': 25 + i,
                    'temperature_min': 15 + i,
                    'description': ['晴', '多云', '小雨', '阴', '晴'][i],
                    'icon': ['01d', '03d', '10d', '04d', '01d'][i],
                    'humidity': 60 + i * 5,
                    'pop': i * 20
                })
            self.forecast_updated.emit(mock_forecast)

            # 模拟空气质量数据
            mock_air_quality = {
                'aqi': 85,
                'level': '良',
                'pm25': 35,
                'pm10': 55,
                'so2': 8,
                'no2': 25,
                'co': 0.8,
                'o3': 120
            }
            self.air_quality_updated.emit(mock_air_quality)

        except Exception as e:
            self.logger.error(f"发送模拟数据失败: {e}")

    def stop(self):
        """停止工作线程"""
        self.running = False
        self.quit()
        self.wait()


class WeatherComponent:
    """天气组件类"""

    def __init__(self):
        """初始化天气组件"""
        self.weather_data = None

    def update_weather(self, data):
        """更新天气数据"""
        self.weather_data = data

    def get_weather_info(self):
        """获取天气信息"""
        return self.weather_data or {}

    def cleanup(self):
        """清理资源"""
        self.weather_data = None
