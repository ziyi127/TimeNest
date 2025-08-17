"""
用户设置管理 API 接口
"""

from flask import Blueprint, request, jsonify
from services.service_factory import ServiceFactory
from models.user_settings import UserSettings
from utils.exceptions import ValidationException

# 创建用户设置管理蓝图
settings_bp = Blueprint('settings', __name__)

# 获取用户服务实例
user_service = ServiceFactory.get_user_service()


@settings_bp.route('/settings', methods=['GET'])
def get_user_settings():
    """
    获取用户设置
    """
    try:
        # 获取用户设置
        user_settings = user_service.get_user_settings()
        return jsonify(user_settings.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/settings', methods=['PUT'])
def update_user_settings():
    """
    更新用户设置
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 获取当前用户设置
        current_settings = user_service.get_user_settings()
        
        # 更新变更的字段
        for key, value in data.items():
            if hasattr(current_settings, key):
                setattr(current_settings, key, value)
        
        # 更新用户设置
        updated_settings = user_service.update_user_settings(current_settings)
        
        # 清空变更字段记录
        updated_settings.clear_changed_fields()
        
        return jsonify(updated_settings.to_dict()), 200
    except ValidationException as e:
        return jsonify({"error": "数据验证失败", "details": e.errors}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500