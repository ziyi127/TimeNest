"""
课程管理 API 接口
"""

from typing import List, Tuple, Any
from flask import Blueprint, request, jsonify, Response
from services.service_factory import ServiceFactory
from models.class_item import ClassItem, TimeSlot
from utils.exceptions import ValidationException, ConflictException

# 创建课程管理蓝图
courses_bp: Blueprint = Blueprint('courses', __name__)

# 获取课程服务实例
course_service = ServiceFactory.get_course_service()


@courses_bp.route('/courses', methods=['GET'])
def get_all_courses() -> Tuple[Response, int]:
    """
    获取所有课程
    """
    try:
        courses: List[ClassItem] = course_service.get_all_courses()
        return jsonify([course.to_dict() for course in courses]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route('/courses', methods=['POST'])
def create_course() -> Tuple[Response, int]:
    """
    创建课程
    """
    try:
        data: Any = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 创建时间段对象
        duration_data: Any = data.get('duration')
        if not duration_data:
            return jsonify({"error": "课程时间段不能为空"}), 400
        
        duration: TimeSlot = TimeSlot(
            start_time=duration_data.get('start_time'),
            end_time=duration_data.get('end_time')
        )
        
        # 创建课程对象
        course: ClassItem = ClassItem(
            id=data.get('id'),
            name=data.get('name'),
            teacher=data.get('teacher'),
            location=data.get('location'),
            duration=duration
        )
        
        # 创建课程
        created_course: ClassItem = course_service.create_course(course)
        return jsonify(created_course.to_dict()), 201
    except ValidationException as e:
        errors: List[str] = getattr(e, 'errors', [])
        return jsonify({"error": "数据验证失败", "details": errors}), 400
    except ConflictException as e:
        conflicts: List[str] = getattr(e, 'conflicts', [])
        return jsonify({"error": "课程冲突", "details": conflicts}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500