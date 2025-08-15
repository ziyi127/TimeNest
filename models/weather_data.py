"""
天气数据模型
定义天气数据相关的核心数据结构
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class WeatherData:
    """天气数据模型类"""
    location: str
    temperature: float
    weather_condition: str
    humidity: int
    wind_speed: float
    wind_direction: str
    pressure: float
    visibility: float
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherData':
        """从字典创建WeatherData实例"""
        return cls(
            location=data.get('location', ''),
            temperature=data.get('temperature', 0.0),
            weather_condition=data.get('weather_condition', ''),
            humidity=data.get('humidity', 0),
            wind_speed=data.get('wind_speed', 0.0),
            wind_direction=data.get('wind_direction', ''),
            pressure=data.get('pressure', 0.0),
            visibility=data.get('visibility', 0.0),
            last_updated=data.get('last_updated', datetime.now().isoformat())
        )


@dataclass
class WeatherSettings:
    """天气设置模型类"""
    enabled: bool = True
    location: str = "Beijing"
    auto_refresh: bool = True
    refresh_interval: int = 30  # 分钟
    api_key: str = ""
    units: str = "metric"  # metric, imperial, kelvin
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherSettings':
        """从字典创建WeatherSettings实例"""
        return cls(
            enabled=data.get('enabled', True),
            location=data.get('location', 'Beijing'),
            auto_refresh=data.get('auto_refresh', True),
            refresh_interval=data.get('refresh_interval', 30),
            api_key=data.get('api_key', ''),
            units=data.get('units', 'metric')
        )