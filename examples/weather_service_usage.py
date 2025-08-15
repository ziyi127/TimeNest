#!/usr/bin/env python3
"""
天气服务使用示例
演示如何使用WeatherService获取天气数据
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.weather_service import WeatherService


def main():
    # 创建天气服务实例
    weather_service = WeatherService()
    
    # 更新天气设置，支持用户自定义API ID和KEY
    settings_data = {
        "api_id": "your_api_id_here",  # 替换为你的实际API ID（可选）
        "api_key": "your_api_key_here",  # 替换为你的实际API密钥（可选）
        "location": "四川,绵阳",  # 格式为"省份,城市"
        "update_interval": 1800,  # 30分钟更新一次
        "enabled": True
    }
    
    # 应用设置
    success = weather_service.update_settings(settings_data)
    if not success:
        print("更新天气设置失败")
        return
    
    # 获取当前设置
    settings = weather_service.get_settings()
    print(f"天气服务设置:")
    print(f"  API ID: {settings.api_id if settings.api_id else '使用默认公共ID'}")
    print(f"  API KEY: {'*' * len(settings.api_key) if settings.api_key else '使用默认公共KEY'}")
    print(f"  位置: {settings.location}")
    print(f"  更新间隔: {settings.update_interval} 秒")
    print(f"  是否启用: {settings.enabled}")
    
    # 获取天气数据
    print("\n正在获取天气数据...")
    weather_data = weather_service.fetch_weather_data()
    
    if weather_data:
        print(f"\n天气信息:")
        print(f"  位置: {weather_data.location}")
        print(f"  温度: {weather_data.temperature}°C")
        print(f"  湿度: {weather_data.humidity}%")
        print(f"  气压: {weather_data.pressure} hPa")
        print(f"  风速: {weather_data.wind_speed} m/s")
        print(f"  天气状况: {weather_data.weather_condition}")
        print(f"  最后更新: {weather_data.last_updated}")
        
        # 显示额外的天气信息
        if weather_data.forecast:
            extra_info = weather_data.forecast[0] if isinstance(weather_data.forecast, list) and weather_data.forecast else {}
            if isinstance(extra_info, dict):
                print(f"  风向: {extra_info.get('wind_direction', 'N/A')}")
                print(f"  风力: {extra_info.get('wind_scale', 'N/A')}")
                print(f"  降水量: {extra_info.get('precipitation', 'N/A')}")
                if extra_info.get('weather1img'):
                    print(f"  天气图标1: {extra_info.get('weather1img')}")
                if extra_info.get('weather2img'):
                    print(f"  天气图标2: {extra_info.get('weather2img')}")
                if extra_info.get('uptime'):
                    print(f"  数据更新时间: {extra_info.get('uptime')}")
    else:
        print("获取天气数据失败")


if __name__ == "__main__":
    main()