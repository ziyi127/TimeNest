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
        
        # 使用用户配置的API ID和KEY，如果没有则使用默认的公共ID和KEY
        api_id: str = self.settings.api_id if self.settings.api_id else "88888888"
        api_key: str = self.settings.api_key if self.settings.api_key else "88888888"
        
        # API接口地址
        api_urls: List[str] = [
            "https://cn.apihz.cn/api/tianqi/tqyb.php",  # 域名接口(默认)
            "http://101.35.2.25/api/tianqi/tqybip.php",  # 集群IP接口1
            "http://124.222.204.22/api/tianqi/tqybip.php",  # 集群IP接口2
            "http://124.220.49.230/api/tianqi/tqybip.php",  # 集群IP接口3
            "https://vip.apihz.cn/api/tianqi/tqyb.php"  # 彩钻接口(高稳定性)
        ]
        
        # 尝试多个API接口以提高稳定性
        for i, api_url in enumerate(api_urls):
            try:
                logger.info(f"尝试使用API接口 {i+1}: {api_url}")
                
                # 根据API文档要求，需要将location拆分为省份和城市
                # 假设location格式为"省份,城市" 或 "城市"
                location_parts = self.settings.location.split(',')
                if len(location_parts) >= 2:
                    province = location_parts[0].strip()
                    city = location_parts[1].strip()
                else:
                    # 如果没有省份信息，直接使用城市名
                    province = ""
                    city = self.settings.location.strip()
                
                params: Dict[str, str] = {
                    "id": api_id,
                    "key": api_key,
                    "sheng": province if province else city,  # 如果没有省份，则使用城市名作为省份
                    "place": city
                }
                
                logger.info(f"正在获取天气数据: 省份={params['sheng']}, 城市={params['place']}")
                
                response = requests.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # 检查API返回的状态码
                if data.get("code") != 200:
                    logger.warning(f"API {api_url} 返回错误: {data.get('msg', '未知错误')}")
                    continue  # 尝试下一个API接口
                
                # 解析天气数据（根据新API文档）
                weather_data = WeatherData(
                    location=data.get("place", self.settings.location),
                    temperature=float(data.get("temperature", 0)),
                    humidity=int(data.get("humidity", 0)),
                    pressure=int(data.get("pressure", 0)),
                    wind_speed=float(data.get("windSpeed", 0)),
                    weather_condition=f"{data.get('weather1', '')}转{data.get('weather2', '')}".strip(),
                    last_updated=datetime.now()
                )
                
                # 添加额外的天气信息作为forecast的一部分
                extra_weather_info: Dict[str, Union[str, int, float, None]] = {
                    "wind_direction": data.get("windDirection", "未知"),
                    "wind_scale": data.get("windScale", "未知"),
                    "wind_direction_degree": data.get("windDirectionDegree", 0),
                    "precipitation": data.get("precipitation", 0),
                    "weather1img": data.get("weather1img", ""),
                    "weather2img": data.get("weather2img", ""),
                    "uptime": data.get("uptime", ""),
                }
                
                # 创建包含额外信息的forecast列表
                weather_data = WeatherData(
                    location=weather_data.location,
                    temperature=weather_data.temperature,
                    humidity=weather_data.humidity,
                    pressure=weather_data.pressure,
                    wind_speed=weather_data.wind_speed,
                    weather_condition=weather_data.weather_condition,
                    forecast=[extra_weather_info],
                    last_updated=weather_data.last_updated
                )
                
                # 更新当前天气数据
                self.current_weather = weather_data
                self._save_weather_data()
                
                logger.info(f"成功获取天气数据: {weather_data.location}")
                return weather_data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API {api_url} 请求失败: {str(e)}")
                continue  # 尝试下一个API接口
            except ValueError as e:
                logger.error(f"API {api_url} 数据解析失败: {str(e)}")
                continue  # 尝试下一个API接口
            except Exception as e:
                logger.error(f"使用API {api_url} 获取天气数据失败: {str(e)}")
                continue  # 尝试下一个API接口
        
        # 所有API接口都失败了
        logger.error("所有API接口都不可用，获取天气数据失败")
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
        
        # 如果没有缓存数据或需要刷新，则获取新数据
        if not self.current_weather:
            return self.fetch_weather_data()
        
        # 检查上次更新时间
        try:
            last_update = self.current_weather.last_updated
            time_diff = (datetime.now() - last_update).total_seconds()  # 秒
            
            if time_diff >= self.settings.update_interval:
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
            return {
                "location": weather_data.location,
                "temperature": weather_data.temperature,
                "humidity": weather_data.humidity,
                "pressure": weather_data.pressure,
                "wind_speed": weather_data.wind_speed,
                "weather_condition": weather_data.weather_condition,
                "forecast": weather_data.forecast,
                "last_updated": weather_data.last_updated.isoformat()
            }
        else:
            return {}
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False