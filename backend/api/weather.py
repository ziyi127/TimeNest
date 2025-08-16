"""
天气服务API接口
"""

from flask import Blueprint, jsonify, request
from services.service_factory import ServiceFactory
from services.weather_service import WeatherSettings
from typing import Dict, Any
import logging

# 创建天气服务蓝图
weather_bp = Blueprint('weather', __name__)

# 获取日志记录器
logger = logging.getLogger(__name__)

@weather_bp.route('/weather/settings', methods=['POST'])
def update_weather_settings():
    """
    更新天气设置
    """
    try:
        # 获取天气服务实例
        weather_service = ServiceFactory.get_weather_service()
        
        # 获取请求数据
        settings_data = request.get_json()
        
        # 更新设置
        success = weather_service.update_settings(settings_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "天气设置更新成功"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "天气设置更新失败"
            }), 400
            
    except Exception as e:
        logger.error(f"更新天气设置时发生错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"更新天气设置时发生错误: {str(e)}"
        }), 500

@weather_bp.route('/weather/current', methods=['GET'])
def get_current_weather():
    """
    获取当前天气数据
    """
    try:
        # 获取天气服务实例
        weather_service = ServiceFactory.get_weather_service()
        
        # 获取当前天气数据
        weather_data = weather_service.get_current_weather()
        
        if weather_data:
            # 转换为字典格式
            weather_dict = {
                "location": weather_data.location,
                "temperature": weather_data.temperature,
                "humidity": weather_data.humidity,
                "pressure": weather_data.pressure,
                "wind_speed": weather_data.wind_speed,
                "weather_condition": weather_data.weather_condition,
                "forecast": weather_data.forecast,
                "last_updated": weather_data.last_updated.isoformat() if weather_data.last_updated else None
            }
            
            return jsonify(weather_dict), 200
        else:
            return jsonify({
                "error": "无法获取天气数据"
            }), 404
            
    except Exception as e:
        logger.error(f"获取天气数据时发生错误: {str(e)}")
        return jsonify({
            "error": f"获取天气数据时发生错误: {str(e)}"
        }), 500

@weather_bp.route('/weather/refresh', methods=['POST'])
def refresh_weather_data():
    """
    手动刷新天气数据
    """
    try:
        # 获取天气服务实例
        weather_service = ServiceFactory.get_weather_service()
        
        # 刷新天气数据
        success = weather_service.refresh_weather_data()
        
        if success:
            return jsonify({
                "success": True,
                "message": "天气数据刷新成功"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "天气数据刷新失败"
            }), 400
            
    except Exception as e:
        logger.error(f"刷新天气数据时发生错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"刷新天气数据时发生错误: {str(e)}"
        }), 500