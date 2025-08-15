"""
天气数据服务
提供实时天气数据获取和管理功能
"""

import requests
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from models.weather_data import WeatherData, WeatherSettings
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("weather_service")


class WeatherService:
    """天气数据服务类"""
    
    def __init__(self):
        """初始化天气数据服务"""
        self.config_file = "./data/weather_config.json"
        self.weather_data_file = "./data/weather_data.json"
        self.settings: Optional[WeatherSettings] = None
        self.current_weather: Optional[WeatherData] = None
        self._ensure_data_directory()
        self._load_settings()
        self._load_weather_data()
        logger.info("WeatherService initialized")
    
    def _ensure_data_directory(self):
        """确保数据目录存在"""
        try:
            data_dir = os.path.dirname(self.config_file)
            if data_dir:
                os.makedirs(data_dir, exist_ok=True)
                logger.debug(f"确保数据目录存在: {data_dir}")
        except Exception as e:
            logger.error(f"创建数据目录失败: {str(e)}")
    
    def _load_settings(self):
        """加载天气设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = WeatherSettings.from_dict(data)
                logger.debug("天气设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = WeatherSettings()
                self._save_settings()
                logger.debug("创建默认天气设置")
        except Exception as e:
            logger.error(f"加载天气设置失败: {str(e)}")
            self.settings = WeatherSettings()
    
    def _save_settings(self):
        """保存天气设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("天气设置保存成功")
        except Exception as e:
            logger.error(f"保存天气设置失败: {str(e)}")
            raise ValidationException("保存天气设置失败")
    
    def _load_weather_data(self):
        """加载天气数据"""
        try:
            if os.path.exists(self.weather_data_file):
                with open(self.weather_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_weather = WeatherData.from_dict(data)
                logger.debug("天气数据加载成功")
        except Exception as e:
            logger.error(f"加载天气数据失败: {str(e)}")
    
    def _save_weather_data(self):
        """保存天气数据"""
        try:
            if self.current_weather:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.weather_data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_weather.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("天气数据保存成功")
        except Exception as e:
            logger.error(f"保存天气数据失败: {str(e)}")
    
    def get_settings(self) -> WeatherSettings:
        """
        获取天气设置
        
        Returns:
            WeatherSettings: 天气设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or WeatherSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新天气设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        logger.info("更新天气设置")
        
        try:
            if not self.settings:
                self.settings = WeatherSettings()
            
            # 更新设置字段
            for key, value in settings_data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # 保存设置
            self._save_settings()
            
            logger.info("天气设置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新天气设置失败: {str(e)}")
            return False
    
    def get_current_weather(self) -> Optional[WeatherData]:
        """
        获取当前天气数据
        
        Returns:
            Optional[WeatherData]: 天气数据
        """
        return self.current_weather
    
    def fetch_weather_data(self) -> Optional[WeatherData]:
        """
        从API获取天气数据
        
        Returns:
            Optional[WeatherData]: 天气数据
        """
        if not self.settings or not self.settings.enabled:
            logger.warning("天气服务未启用")
            return None
        
        if not self.settings.api_key:
            logger.warning("未配置天气API密钥")
            return None
        
        try:
            # 使用OpenWeatherMap API获取天气数据
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": self.settings.location,
                "appid": self.settings.api_key,
                "units": self.settings.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析天气数据
            weather_data = WeatherData(
                location=data["name"],
                temperature=data["main"]["temp"],
                weather_condition=data["weather"][0]["description"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
                wind_direction=str(data["wind"].get("deg", "N/A")),
                pressure=data["main"]["pressure"],
                visibility=data.get("visibility", 0) / 1000.0,  # 转换为公里
                last_updated=datetime.now().isoformat()
            )
            
            # 更新当前天气数据
            self.current_weather = weather_data
            self._save_weather_data()
            
            logger.info(f"成功获取天气数据: {weather_data.location}")
            return weather_data
        except Exception as e:
            logger.error(f"获取天气数据失败: {str(e)}")
            return None
    
    def refresh_weather_data(self) -> Optional[WeatherData]:
        """
        刷新天气数据
        
        Returns:
            Optional[WeatherData]: 天气数据
        """
        if not self.settings or not self.settings.enabled:
            logger.warning("天气服务未启用")
            return None
        
        # 检查是否需要自动刷新
        if not self.settings.auto_refresh:
            logger.debug("自动刷新未启用，返回缓存数据")
            return self.current_weather
        
        # 如果没有缓存数据或需要刷新，则获取新数据
        if not self.current_weather:
            return self.fetch_weather_data()
        
        # 检查上次更新时间
        try:
            last_update = datetime.fromisoformat(self.current_weather.last_updated)
            time_diff = (datetime.now() - last_update).total_seconds() / 60  # 分钟
            
            if time_diff >= self.settings.refresh_interval:
                return self.fetch_weather_data()
            else:
                logger.debug("天气数据未过期，返回缓存数据")
                return self.current_weather
        except Exception as e:
            logger.error(f"检查天气数据更新时间失败: {str(e)}")
            return self.fetch_weather_data()
    
    def get_weather_info(self) -> Dict[str, Any]:
        """
        获取天气信息
        
        Returns:
            Dict[str, Any]: 天气信息字典
        """
        weather_data = self.refresh_weather_data()
        
        if weather_data:
            return weather_data.to_dict()
        else:
            return {}
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False