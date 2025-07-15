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
TimeNest 天气服务
支持多种天气数据源和图标包
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from PySide6.QtCore import QObject, Signal, QTimer, QThread, Slot
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication
import os


class WeatherCondition(Enum):
    """天气状况枚举"""
    CLEAR = "clear"  # 晴朗
    PARTLY_CLOUDY = "partly_cloudy"  # 多云
    CLOUDY = "cloudy"  # 阴天
    OVERCAST = "overcast"  # 阴霾
    LIGHT_RAIN = "light_rain"  # 小雨
    MODERATE_RAIN = "moderate_rain"  # 中雨
    HEAVY_RAIN = "heavy_rain"  # 大雨
    THUNDERSTORM = "thunderstorm"  # 雷暴
    LIGHT_SNOW = "light_snow"  # 小雪
    MODERATE_SNOW = "moderate_snow"  # 中雪
    HEAVY_SNOW = "heavy_snow"  # 大雪
    FOG = "fog"  # 雾
    HAZE = "haze"  # 霾
    SANDSTORM = "sandstorm"  # 沙尘暴
    UNKNOWN = "unknown"  # 未知


class AirQualityLevel(Enum):
    """空气质量等级"""
    EXCELLENT = "excellent"  # 优
    GOOD = "good"  # 良
    LIGHT_POLLUTION = "light_pollution"  # 轻度污染
    MODERATE_POLLUTION = "moderate_pollution"  # 中度污染
    HEAVY_POLLUTION = "heavy_pollution"  # 重度污染
    SEVERE_POLLUTION = "severe_pollution"  # 严重污染
    UNKNOWN = "unknown"  # 未知


@dataclass
class WeatherData:
    """天气数据"""
    location: str
    condition: WeatherCondition
    temperature: float  # 摄氏度
    feels_like: Optional[float] = None  # 体感温度
    humidity: Optional[int] = None  # 湿度百分比
    pressure: Optional[float] = None  # 气压 hPa
    wind_speed: Optional[float] = None  # 风速 km/h
    wind_direction: Optional[str] = None  # 风向
    visibility: Optional[float] = None  # 能见度 km
    uv_index: Optional[int] = None  # 紫外线指数
    air_quality: Optional[AirQualityLevel] = None  # 空气质量
    aqi: Optional[int] = None  # 空气质量指数
    description: str = ""  # 天气描述
    icon_code: str = ""  # 图标代码
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""  # 数据源
    

@dataclass
class WeatherForecast:
    """天气预报"""
    date: datetime
    condition: WeatherCondition
    high_temp: float
    low_temp: float
    description: str = ""
    icon_code: str = ""
    precipitation_chance: Optional[int] = None  # 降水概率
    

@dataclass
class WeatherAlert:
    """天气预警"""
    id: str
    title: str
    description: str
    severity: str  # 严重程度
    start_time: datetime
    end_time: datetime
    areas: List[str] = field(default_factory=list)
    

class IWeatherProvider(ABC):
    """天气数据提供者接口"""
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """提供者ID"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供者名称"""
        pass
    
    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """是否需要API密钥"""
        pass
    
    @abstractmethod
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        pass
    
    @abstractmethod
    def get_current_weather(self, location: str) -> Optional[WeatherData]:
        """获取当前天气"""
        pass
    
    @abstractmethod
    def get_forecast(self, location: str, days: int = 7) -> List[WeatherForecast]:
        """获取天气预报"""
        pass
    
    @abstractmethod
    def get_alerts(self, location: str) -> List[WeatherAlert]:
        """获取天气预警"""
        pass
    
    @abstractmethod
    def search_locations(self, query: str) -> List[Dict[str, str]]:
        """搜索位置"""
        pass


class OpenWeatherMapProvider(IWeatherProvider):
    """OpenWeatherMap 天气提供者"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.OpenWeatherMapProvider')
        self.api_key = ""
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
        self.session.timeout = 10
    
    @property
    def provider_id(self) -> str:
        return "openweathermap"
    
    @property
    def provider_name(self) -> str:
        return "OpenWeatherMap"
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    def set_api_key(self, api_key: str):
        self.api_key = api_key
    
    def get_current_weather(self, location: str) -> Optional[WeatherData]:
        """获取当前天气"""
        try:
            if not self.api_key:
                self.logger.error("OpenWeatherMap API密钥未设置")
                return None
            
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析天气状况
            condition = self._parse_condition(data.get("weather")[0]["id"])
            
            weather_data = WeatherData(
                location=data.get("name"),
                condition=condition,
                temperature=data.get("main")["temp"],
                feels_like=data.get("main").get("feels_like"),
                humidity=data.get("main").get("humidity"),
                pressure=data.get("main").get("pressure"),
                wind_speed=(data.get("wind", {}) or {}).get("speed", 0) * 3.6,  # m/s to km/h
                wind_direction=self._parse_wind_direction((data.get("wind", {}) or {}).get("deg")),
                visibility=data.get("visibility", 0) / 1000,  # m to km
                description=data.get("weather")[0]["description"],
                icon_code=data.get("weather")[0]["icon"],
                source=self.provider_name
            )
            
            return weather_data
            
        except Exception as e:
            self.logger.error(f"获取当前天气失败: {e}", exc_info=True)
            return None
    
    def get_forecast(self, location: str, days: int = 7) -> List[WeatherForecast]:
        """获取天气预报"""
        try:
            if not self.api_key:
                self.logger.error("OpenWeatherMap API密钥未设置")
                return []
            
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecasts = []
            
            # 按日期分组
            daily_data = {}
            for item in data.get("list"):
                date = datetime.fromtimestamp(item.get("dt")).date()
                if date not in daily_data:
                    daily_data[date] = []
                daily_data[date].append(item)
            
            # 生成每日预报
            for date, items in list(daily_data.items())[:days]:
                # 计算最高最低温度
                temps = [item.get("main")["temp"] for item in items]
                high_temp = max(temps)
                low_temp = min(temps)
                
                # 选择中午的天气作为主要天气
                main_item = min(items, key=lambda x: abs(datetime.fromtimestamp(x.get("dt")).hour - 12))
                
                condition = self._parse_condition(main_item.get("weather")[0]["id"])
                
                forecast = WeatherForecast(
                    date=datetime.combine(date, datetime.min.time()),
                    condition=condition,
                    high_temp=high_temp,
                    low_temp=low_temp,
                    description=main_item.get("weather")[0]["description"],
                    icon_code=main_item.get("weather")[0]["icon"]
                )
                
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            self.logger.error(f"获取天气预报失败: {e}", exc_info=True)
            return []
    
    def get_alerts(self, location: str) -> List[WeatherAlert]:
        """获取天气预警（OpenWeatherMap免费版不支持）"""
        return []
    
    def search_locations(self, query: str) -> List[Dict[str, str]]:
        """搜索位置"""
        try:
            if not self.api_key:
                return []
            
            url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": query,
                "limit": 5,
                "appid": self.api_key
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            locations = []
            
            for item in data:
                location = {
                    "name": item.get("name"),
                    "country": item.get("country", ""),
                    "state": item.get("state", ""),
                    "lat": str(item.get("lat")),
                    "lon": str(item.get("lon"))
                }
                locations.append(location)
            
            return locations
            
        except Exception as e:
            self.logger.error(f"搜索位置失败: {e}", exc_info=True)
            return []
    
    def _parse_condition(self, weather_id: int) -> WeatherCondition:
        """解析天气状况"""
        if 200 <= weather_id <= 232:
            return WeatherCondition.THUNDERSTORM
        elif 300 <= weather_id <= 321:
            return WeatherCondition.LIGHT_RAIN
        elif 500 <= weather_id <= 504:
            return WeatherCondition.MODERATE_RAIN
        elif weather_id == 511:
            return WeatherCondition.LIGHT_SNOW
        elif 520 <= weather_id <= 531:
            return WeatherCondition.HEAVY_RAIN
        elif 600 <= weather_id <= 622:
            if weather_id <= 612:
                return WeatherCondition.LIGHT_SNOW
            elif weather_id <= 616:
                return WeatherCondition.MODERATE_SNOW
            else:
                return WeatherCondition.HEAVY_SNOW
        elif 701 <= weather_id <= 781:
            if weather_id == 741:
                return WeatherCondition.FOG
            elif weather_id == 751 or weather_id == 761:
                return WeatherCondition.SANDSTORM
            else:
                return WeatherCondition.HAZE
        elif weather_id == 800:
            return WeatherCondition.CLEAR
        elif weather_id == 801:
            return WeatherCondition.PARTLY_CLOUDY
        elif weather_id == 802:
            return WeatherCondition.CLOUDY
        elif weather_id >= 803:
            return WeatherCondition.OVERCAST
        else:
            return WeatherCondition.UNKNOWN
    
    def _parse_wind_direction(self, degrees: Optional[float]) -> str:
        """解析风向"""
        if degrees is None:
            return "无风"
        
        directions = [
            "北", "北北东", "东北", "东北东",
            "东", "东南东", "东南", "南南东",
            "南", "南南西", "西南", "西南西",
            "西", "西北西", "西北", "北北西"
        ]
        
        index = int((degrees + 11.25) / 22.5) % 16
        return directions[index]


class WeatherIconManager:
    """天气图标管理器"""
    
    def __init__(self, icon_pack_dir: str):
        self.logger = logging.getLogger(f'{__name__}.WeatherIconManager')
        self.icon_pack_dir = icon_pack_dir
        self.icon_cache: Dict[str, QIcon] = {}
        self.current_pack = "MaterialDesign"  # 默认图标包
        
        # 图标映射
        self.icon_mapping = {
            WeatherCondition.CLEAR: "weather-sunny",
            WeatherCondition.PARTLY_CLOUDY: "weather-partly-cloudy",
            WeatherCondition.CLOUDY: "weather-cloudy",
            WeatherCondition.OVERCAST: "weather-cloudy",
            WeatherCondition.LIGHT_RAIN: "weather-rainy",
            WeatherCondition.MODERATE_RAIN: "weather-rainy",
            WeatherCondition.HEAVY_RAIN: "weather-pouring",
            WeatherCondition.THUNDERSTORM: "weather-lightning-rainy",
            WeatherCondition.LIGHT_SNOW: "weather-snowy",
            WeatherCondition.MODERATE_SNOW: "weather-snowy-heavy",
            WeatherCondition.HEAVY_SNOW: "weather-snowy-heavy",
            WeatherCondition.FOG: "weather-fog",
            WeatherCondition.HAZE: "weather-hazy",
            WeatherCondition.SANDSTORM: "weather-dust",
            WeatherCondition.UNKNOWN: "weather-cloudy"
        }
    
    def get_icon(self, condition: WeatherCondition, size: int = 64) -> QIcon:
        """获取天气图标"""
        try:
            cache_key = f"{condition.value}_{size}_{self.current_pack}"
            
            
            if cache_key in self.icon_cache:
                return self.icon_cache[cache_key]
            
            icon_name = self.icon_mapping.get(condition, "weather-cloudy")
            icon_path = self._find_icon_file(icon_name)
            
            
            if icon_path and os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    if size != pixmap.width() or size != pixmap.height():
                        pixmap = pixmap.scaled(size, size)
                    icon = QIcon(pixmap)
                    self.icon_cache[cache_key] = icon
                    return icon
            
            # 返回默认图标
            return QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon)
            
        except Exception as e:
            self.logger.error(f"获取天气图标失败: {e}", exc_info=True)
            return QIcon()
    
    def _find_icon_file(self, icon_name: str) -> Optional[str]:
        """查找图标文件"""
        try:
            pack_dir = os.path.join(self.icon_pack_dir, self.current_pack)
            if not os.path.exists(pack_dir):
                return None
            
            # 支持的图标格式
            extensions = [".svg", ".png", ".jpg", ".jpeg", ".ico"]
            
            for ext in extensions:
                icon_path = os.path.join(pack_dir, f"{icon_name}{ext}")
                if os.path.exists(icon_path):
                    return icon_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"查找图标文件失败: {e}", exc_info=True)
            return None
    
    def set_icon_pack(self, pack_name: str):
        """设置图标包"""
        try:
            pack_dir = os.path.join(self.icon_pack_dir, pack_name)
            if os.path.exists(pack_dir):
                self.current_pack = pack_name
                self.icon_cache.clear()  # 清除缓存
                self.logger.info(f"图标包已切换到: {pack_name}")
            else:
                self.logger.warning(f"图标包不存在: {pack_name}")
                
        except Exception as e:
            self.logger.error(f"设置图标包失败: {e}", exc_info=True)
    
    def get_available_packs(self) -> List[str]:
        """获取可用的图标包"""
        try:
            if not os.path.exists(self.icon_pack_dir):
                return []
            
            packs = []
            for item in os.listdir(self.icon_pack_dir):
                pack_path = os.path.join(self.icon_pack_dir, item)
                if os.path.isdir(pack_path):
                    packs.append(item)
            
            return sorted(packs)
            
        except Exception as e:
            self.logger.error(f"获取可用图标包失败: {e}", exc_info=True)
            return []


class WeatherUpdateThread(QThread):
    """天气更新线程"""
    
    weather_updated = Signal(WeatherData)
    forecast_updated = Signal(list)
    alerts_updated = Signal(list)
    update_failed = Signal(str)
    
    def __init__(self, provider: IWeatherProvider, location: str):
        super().__init__()
        self.provider = provider
        self.location = location
        self.logger = logging.getLogger(f'{__name__}.WeatherUpdateThread')
    
    def run(self):
        """运行更新"""
        try:
            # 获取当前天气
            current_weather = self.provider.get_current_weather(self.location)
            if current_weather:
                self.weather_updated.emit(current_weather)
            
            # 获取预报
            forecast = self.provider.get_forecast(self.location)
            if forecast:
                self.forecast_updated.emit(forecast)
            
            # 获取预警
            alerts = self.provider.get_alerts(self.location)
            self.alerts_updated.emit(alerts)
            
        except Exception as e:
            self.logger.error(f"天气更新失败: {e}", exc_info=True)
            self.update_failed.emit(str(e))


from functools import wraps
from typing import Any, Callable
import time

def cache_result(expire_seconds: int = 300):
    """缓存装饰器"""
    def decorator(func: Callable):
        cache = {}
        
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            
            # 检查缓存是否有效
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < expire_seconds:
                    return cached_data
            
            # 调用原函数并缓存结果
            result = func(self, *args, **kwargs)
            if result is not None:
                cache[cache_key] = (result, time.time())
            return result
            
        return wrapper
    return decorator

class WeatherService(QObject):
    """天气服务"""
    
    weather_updated = Signal(WeatherData)
    forecast_updated = Signal(list)
    alerts_updated = Signal(list)
    update_failed = Signal(str)
    
    def __init__(self, icon_pack_dir: str = None):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.WeatherService')
        self.providers: Dict[str, IWeatherProvider] = {}
        self.current_provider_id = ""
        self.current_location = ""
        self.update_interval = 30  # 分钟
        self.enabled = True
        
        # 缓存设置
        self.cache_enabled = True
        self.cache_expire = 300  # 5分钟
        self.weather_cache: Dict[str, tuple] = {}
        self.forecast_cache: Dict[str, tuple] = {}
        self.alerts_cache: Dict[str, tuple] = {}
        
        # 图标管理器
        icon_dir = icon_pack_dir if icon_pack_dir else os.path.join(os.path.dirname(__file__), "../../resources/icons/weather")
        self.icon_manager = WeatherIconManager(icon_dir)
        
        # 当前数据
        self.current_weather: Optional[WeatherData] = None
        self.current_forecast: List[WeatherForecast] = []
        self.current_alerts: List[WeatherAlert] = []
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_weather)
        
        # 更新线程
        self.update_thread: Optional[WeatherUpdateThread] = None
        
        # 注册默认提供者
        self.register_provider(OpenWeatherMapProvider())
    
    def register_provider(self, provider: IWeatherProvider):
        """注册天气提供者"""
        try:
            self.providers[provider.provider_id] = provider
            
            # 如果是第一个提供者，设为当前提供者
            if not self.current_provider_id:
                self.current_provider_id = provider.provider_id
            
            self.logger.info(f"天气提供者已注册: {provider.provider_name}")
            
        except Exception as e:
            self.logger.error(f"注册天气提供者失败: {e}", exc_info=True)
    
    def set_provider(self, provider_id: str):
        """设置当前提供者"""
        try:
            if provider_id in self.providers:
                self.current_provider_id = provider_id
                self.logger.info(f"天气提供者已切换到: {self.providers[provider_id].provider_name}")
            else:
                self.logger.warning(f"天气提供者不存在: {provider_id}")
                
        except Exception as e:
            self.logger.error(f"设置天气提供者失败: {e}", exc_info=True)
    
    def set_api_key(self, provider_id: str, api_key: str):
        """设置API密钥"""
        try:
            if provider_id in self.providers:
                self.providers[provider_id].set_api_key(api_key)
                self.logger.info(f"API密钥已设置: {provider_id}")
            else:
                self.logger.warning(f"天气提供者不存在: {provider_id}")
                
        except Exception as e:
            self.logger.error(f"设置API密钥失败: {e}", exc_info=True)
    
    def set_location(self, location: str):
        """设置位置"""
        try:
            self.current_location = location
            self.logger.info(f"位置已设置: {location}")
            
            # 立即更新天气
            if self.enabled:
                self.update_weather()
                
        except Exception as e:
            self.logger.error(f"设置位置失败: {e}", exc_info=True)
    
    def set_update_interval(self, minutes: int):
        """设置更新间隔"""
        try:
            self.update_interval = max(1, minutes)
            
            
            if self.update_timer.isActive():
                self.update_timer.stop()
            
                self.update_timer.stop()
                self.update_timer.start(self.update_interval * 60 * 1000)
            
            self.logger.info(f"更新间隔已设置: {self.update_interval}分钟")
            
        except Exception as e:
            self.logger.error(f"设置更新间隔失败: {e}", exc_info=True)
    
    def start_auto_update(self):
        """开始自动更新"""
        try:
            if not self.update_timer.isActive():
                self.update_timer.start(self.update_interval * 60 * 1000)
                self.logger.info("天气自动更新已启动")
                
        except Exception as e:
            self.logger.error(f"启动自动更新失败: {e}", exc_info=True)
    
    def stop_auto_update(self):
        """停止自动更新"""
        try:
            if self.update_timer.isActive():
                self.update_timer.stop()
                self.logger.info("天气自动更新已停止")
                
        except Exception as e:
            self.logger.error(f"停止自动更新失败: {e}", exc_info=True)
    
    def update_weather(self):
        """更新天气"""
        try:
            if not self.enabled or not self.current_location or not self.current_provider_id:
                return
            
            provider = self.providers.get(self.current_provider_id)
            if not provider:
                return
            
            # 停止之前的更新线程
            if self.update_thread and self.update_thread.isRunning():
                self.update_thread.quit()
                self.update_thread.wait()
            
            # 创建新的更新线程
            self.update_thread = WeatherUpdateThread(provider, self.current_location)
            self.update_thread.weather_updated.connect(self._on_weather_updated)
            self.update_thread.forecast_updated.connect(self._on_forecast_updated)
            self.update_thread.alerts_updated.connect(self._on_alerts_updated)
            self.update_thread.update_failed.connect(self._on_update_failed)
            self.update_thread.start()
            
        except Exception as e:
            self.logger.error(f"更新天气失败: {e}", exc_info=True)
            self.update_failed.emit(str(e))
    
    @Slot(WeatherData)
    def _on_weather_updated(self, weather_data: WeatherData):
        """天气更新完成"""
        try:
            self.current_weather = weather_data
            if self.cache_enabled:
                cache_key = f"weather_{self.current_location}"
                self.weather_cache[cache_key] = (weather_data, time.time())
            
            self.weather_updated.emit(weather_data)
            self.logger.info(f"天气已更新: {weather_data.location} {weather_data.temperature}°C")
            
            # 预加载预报数据
            self._preload_forecast()
            
        except Exception as e:
            self.logger.error(f"处理天气更新失败: {e}", exc_info=True)
    
    @Slot(list)
    def _on_forecast_updated(self, forecast: List[WeatherForecast]):
        """预报更新完成"""
        try:
            self.current_forecast = forecast
            if self.cache_enabled:
                cache_key = f"forecast_{self.current_location}"
                self.forecast_cache[cache_key] = (forecast.copy(), time.time())
            
            self.forecast_updated.emit(forecast)
            self.logger.info(f"天气预报已更新: {len(forecast)}天")
            
        except Exception as e:
            self.logger.error(f"处理预报更新失败: {e}", exc_info=True)
    
    @Slot(list)
    def _on_alerts_updated(self, alerts: List[WeatherAlert]):
        """预警更新完成"""
        try:
            self.current_alerts = alerts
            if self.cache_enabled:
                cache_key = f"alerts_{self.current_location}"
                self.alerts_cache[cache_key] = (alerts.copy(), time.time())
            
            self.alerts_updated.emit(alerts)
            if alerts:
                self.logger.info(f"天气预警已更新: {len(alerts)}条")
                
        except Exception as e:
            self.logger.error(f"处理预警更新失败: {e}", exc_info=True)
    
    @Slot(str)
    def _on_update_failed(self, error: str):
        """更新失败"""
        self.update_failed.emit(error)
    
    def search_locations(self, query: str) -> List[Dict[str, str]]:
        """搜索位置"""
        try:
            if not self.current_provider_id:
                return []
            
            provider = self.providers.get(self.current_provider_id)
            if not provider:
                return []
            
            return provider.search_locations(query)
            
        except Exception as e:
            self.logger.error(f"搜索位置失败: {e}", exc_info=True)
            return []
    
    def get_weather_icon(self, condition: WeatherCondition, size: int = 64) -> QIcon:
        """获取天气图标"""
        return self.icon_manager.get_icon(condition, size)
    
    def set_icon_pack(self, pack_name: str):
        """设置图标包"""
        self.icon_manager.set_icon_pack(pack_name)
    
    def get_available_icon_packs(self) -> List[str]:
        """获取可用图标包"""
        return self.icon_manager.get_available_packs()
    
    def set_enabled(self, enabled: bool):
        """设置启用状态"""
        self.enabled = enabled
        if enabled:
            self.start_auto_update()
        else:
            self.stop_auto_update()
        
        self.logger.info(f"天气服务{'启用' if enabled else '禁用'}")
    
    @cache_result(expire_seconds=300)
    def get_current_weather(self) -> Optional[WeatherData]:
        """获取当前天气数据"""
        if not self.cache_enabled or not hasattr(self, 'current_weather'):
            return self.current_weather
        
        cache_key = f"weather_{self.current_location}"
        if cache_key in self.weather_cache:
            data, timestamp = self.weather_cache[cache_key]
            if time.time() - timestamp < self.cache_expire:
                return data
        
        return self.current_weather
    
    @cache_result(expire_seconds=3600)  # 预报缓存1小时
    def get_current_forecast(self) -> List[WeatherForecast]:
        """获取当前预报数据"""
        if not self.cache_enabled or not hasattr(self, 'current_forecast'):
            return self.current_forecast.copy()
        
        cache_key = f"forecast_{self.current_location}"
        if cache_key in self.forecast_cache:
            data, timestamp = self.forecast_cache[cache_key]
            if time.time() - timestamp < self.cache_expire:
                return data.copy()
        
        return self.current_forecast.copy()
    
    @cache_result(expire_seconds=1800)  # 预警缓存30分钟
    def get_current_alerts(self) -> List[WeatherAlert]:
        """获取当前预警数据"""
        if not self.cache_enabled or not hasattr(self, 'current_alerts'):
            return self.current_alerts.copy()
        
        cache_key = f"alerts_{self.current_location}"
        if cache_key in self.alerts_cache:
            data, timestamp = self.alerts_cache[cache_key]
            if time.time() - timestamp < self.cache_expire:
                return data.copy()
        
        return self.current_alerts.copy()
    
    def get_providers(self) -> List[IWeatherProvider]:
        """获取所有提供者"""
        return list(self.providers.values())
    
    def _preload_forecast(self):
        """预加载预报数据"""
        if not self.enabled or not self.current_location or not self.current_provider_id:
            return
        
        provider = self.providers.get(self.current_provider_id)
        if not provider:
            return
        
        # 使用线程预加载
        thread = WeatherUpdateThread(provider, self.current_location)
        thread.forecast_updated.connect(self._on_forecast_updated)
        thread.start()
    
    def set_cache_enabled(self, enabled: bool):
        """设置缓存启用状态"""
        self.cache_enabled = enabled
        self.logger.info(f"天气缓存已{'启用' if enabled else '禁用'}")
    
    def set_cache_expire(self, seconds: int):
        """设置缓存过期时间(秒)"""
        self.cache_expire = max(60, seconds)
        self.logger.info(f"缓存过期时间已设置为: {self.cache_expire}秒")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.stop_auto_update()
            
            
            if self.update_thread and self.update_thread.isRunning():
                self.update_thread.quit()
            
                self.update_thread.quit()
                self.update_thread.wait()
            
            # 清空缓存
            self.weather_cache.clear()
            self.forecast_cache.clear()
            self.alerts_cache.clear()
            
            self.logger.info("天气服务已清理")
            
        except Exception as e:
            self.logger.error(f"清理天气服务失败: {e}", exc_info=True)