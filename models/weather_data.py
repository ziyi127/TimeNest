#!/usr/bin/env python3
"""
天气数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Union, Any


@dataclass
class WeatherData:
    """天气数据模型"""
    location: str
    temperature: float
    humidity: int
    pressure: int
    wind_speed: float
    weather_condition: str
    forecast: List[Dict[str, Union[str, int, float, bool, None]]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        from dataclasses import asdict
        data = asdict(self)
        # 处理datetime字段
        data['last_updated'] = data['last_updated'].isoformat()
        return data


@dataclass
class WeatherSettings:
    """天气设置模型"""
    api_id: Optional[str] = None  # 用户的接口ID
    api_key: Optional[str] = None  # 用户的接口密钥
    location: str = ""
    update_interval: int = 3600  # 更新间隔(秒)
    unit: str = "metric"  # 温度单位: metric(摄氏度), imperial(华氏度)
    enabled: bool = True
    
    def __post_init__(self):
        if not self.location:
            self.location = "北京"