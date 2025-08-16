"""
课表管理 API 接口
"""

from flask import Blueprint, request, jsonify
from services.service_factory import ServiceFactory
from models.class_plan import ClassPlan
from utils.exceptions import ValidationException, NotFoundException, ConflictException

# 创建课表管理蓝图
schedules_bp = Blueprint('schedules', __name__)

# 获取课表服务实例
schedule_service = ServiceFactory.get_schedule_service()


@schedules_bp.route('/schedules', methods=['GET'])
def get_all_schedules():
    """
    获取所有课表
    """
    try:
        schedules = schedule_service.get_all_schedules()
        return jsonify([schedule.to_dict() for schedule in schedules]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@schedules_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """
    创建课表
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 创建课表对象
        schedule = ClassPlan(
            id=data.get('id'),
            day_of_week=data.get('day_of_week'),
            week_parity=data.get('week_parity'),
            course_id=data.get('course_id'),
            valid_from=data.get('valid_from'),
            valid_to=data.get('valid_to')
        )
        
        # 创建课表
        created_schedule = schedule_service.create_schedule(schedule)
        return jsonify(created_schedule.to_dict()), 201
    except ValidationException as e:
        return jsonify({"error": "数据验证失败", "details": e.errors}), 400
    except ConflictException as e:
        return jsonify({"error": "课表冲突", "details": e.conflicts}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500