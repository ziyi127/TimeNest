"""
天气数据服务
提供实时天气数据获取和管理功能
作者: TimeNest团队
创建日期: 2024-01-01
版本: 1.0.0
描述: 提供实时天气数据获取和管理功能，包括天气API调用、数据缓存和设置管理
"""

import requests
import json
import os
from typing import Optional, Dict, Any, List, Union
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
                    # 使用关键字参数创建实例
                    self.settings = WeatherSettings(**data)
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
                
                # 将settings对象转换为字典
                settings_dict: Dict[str, Union[str, int, bool, None]] = {
                    "api_id": self.settings.api_id,
                    "api_key": self.settings.api_key,
                    "location": self.settings.location,
                    "update_interval": self.settings.update_interval,
                    "unit": self.settings.unit,
                    "enabled": self.settings.enabled
                }
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(settings_dict, f, ensure_ascii=False, indent=2)
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
                    # 处理datetime字段
                    if 'last_updated' in data:
                        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
                    self.current_weather = WeatherData(**data)
                logger.debug("天气数据加载成功")
        except Exception as e:
            logger.error(f"加载天气数据失败: {str(e)}")
    
    def _save_weather_data(self):
        """保存天气数据"""
        try:
            if self.current_weather:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                # 将weather_data对象转换为字典
                weather_dict: Dict[str, Union[str, int, float, bool, List[Dict[str, Union[str, int, float, bool, None]]]]] = {
                    "location": self.current_weather.location,
                    "temperature": self.current_weather.temperature,
                    "humidity": self.current_weather.humidity,
                    "pressure": self.current_weather.pressure,
                    "wind_speed": self.current_weather.wind_speed,
                    "weather_condition": self.current_weather.weather_condition,
                    "forecast": self.current_weather.forecast,
                    "last_updated": self.current_weather.last_updated.isoformat()
                }
                
                with open(self.weather_data_file, 'w', encoding='utf-8') as f:
                    json.dump(weather_dict, f, ensure_ascii=False, indent=2)
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
        # 天气功能已禁用
        return None
    
    def fetch_weather_data(self) -> Optional[WeatherData]:
        """
        从API获取天气数据
        
        Returns:
            Optional[WeatherData]: 天气数据
        """
        # 天气功能已禁用
        logger.info("天气功能已禁用，不获取天气数据")
        return None
    
    def refresh_weather_data(self) -> Optional[WeatherData]:
        """
        刷新天气数据
        
        Returns:
            Optional[WeatherData]: 天气数据
        """
        # 天气功能已禁用
        logger.info("天气功能已禁用，不刷新天气数据")
        return None
    
    def get_weather_info(self) -> Dict[str, Any]:
        """
        获取天气信息
        
        Returns:
            Dict[str, Any]: 天气信息字典
        """
        # 天气功能已禁用
        logger.info("天气功能已禁用，不获取天气信息")
        return {}
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        # 天气功能已禁用
        return False