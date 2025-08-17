"""
临时调课管理 API 接口
"""

from flask import Blueprint, request, jsonify
from services.service_factory import ServiceFactory
from models.temp_change import TempChange
from utils.exceptions import ValidationException, NotFoundException, ConflictException

# 创建临时调课管理蓝图
temp_changes_bp = Blueprint('temp_changes', __name__)

# 获取临时调课服务实例
temp_change_service = ServiceFactory.get_temp_change_service()


@temp_changes_bp.route('/temp_changes', methods=['GET'])
def get_all_temp_changes():
    """
    获取所有临时调课
    """
    try:
        temp_changes = temp_change_service.get_all_temp_changes()
        return jsonify([temp_change.to_dict() for temp_change in temp_changes]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@temp_changes_bp.route('/temp_changes', methods=['POST'])
def create_temp_change():
    """
    创建临时调课
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 创建临时调课对象
        temp_change = TempChange(
            id=data.get('id'),
            original_schedule_id=data.get('original_schedule_id'),
            new_course_id=data.get('new_course_id'),
            change_date=data.get('change_date'),
            is_permanent=data.get('is_permanent', False),
            used=data.get('used', False)
        )
        
        # 创建临时调课
        created_temp_change = temp_change_service.create_temp_change(temp_change)
        return jsonify(created_temp_change.to_dict()), 201
    except ValidationException as e:
        return jsonify({"error": "数据验证失败", "details": e.errors}), 400
    except ConflictException as e:
        return jsonify({"error": "临时调课冲突", "details": e.conflicts}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@temp_changes_bp.route('/temp_changes/batch', methods=['POST'])
def batch_create_temp_changes():
    """
    批量创建临时调课
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        temp_changes_data = data.get('temp_changes', [])
        
        # 创建临时调课对象列表
        temp_changes = []
        for temp_change_data in temp_changes_data:
            # 创建临时调课对象
            temp_change = TempChange(
                id=temp_change_data.get('id'),
                original_schedule_id=temp_change_data.get('original_schedule_id'),
                new_course_id=temp_change_data.get('new_course_id'),
                change_date=temp_change_data.get('change_date'),
                is_permanent=temp_change_data.get('is_permanent', False),
                used=temp_change_data.get('used', False)
            )
            temp_changes.append(temp_change)
        
        # 批量保存临时调课
        for temp_change in temp_changes:
            try:
                temp_change_service.create_temp_change(temp_change)
            except ConflictException:
                # 忽略已存在的临时调课
                pass
        
        return jsonify({"message": "临时调课批量保存成功"}), 200
    except ValidationException as e:
        return jsonify({"error": "数据验证失败", "details": e.errors}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500