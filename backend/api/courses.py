"""
课程管理 API 接口
"""

from typing import List, Tuple, Any, Dict
from flask import Blueprint, request, jsonify

from services.service_factory import ServiceFactory
from models.class_item import ClassItem, TimeSlot
from utils.exceptions import ValidationException, ConflictException

# 创建课程管理蓝图
courses_bp = Blueprint('courses', __name__)

# 获取课程服务实例
course_service = ServiceFactory.get_course_service()

@courses_bp.route('/courses', methods=['GET'])
def get_all_courses() -> Tuple[Any, int]:
    """
    获取所有课程
    """
    try:
        courses: List[ClassItem] = course_service.get_all_courses()
        return jsonify([course.to_dict() for course in courses]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@courses_bp.route('/courses', methods=['POST'])
def create_course() -> Tuple[Any, int]:
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


@courses_bp.route('/courses/batch', methods=['POST'])
def batch_create_courses() -> Tuple[Any, int]:
    """
    批量创建课程
    """
    try:
        data: Any = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        courses_data: List[Any] = data.get('courses', [])
        
        # 创建课程对象列表
        courses: List[ClassItem] = []
        for course_data in courses_data:
            # 创建时间段对象
            duration_data: Any = course_data.get('duration')
            if not duration_data:
                return jsonify({"error": "课程时间段不能为空"}), 400
            
            duration: TimeSlot = TimeSlot(
                start_time=duration_data.get('start_time'),
                end_time=duration_data.get('end_time')
            )
            
            # 创建课程对象
            course: ClassItem = ClassItem(
                id=course_data.get('id'),
                name=course_data.get('name'),
                teacher=course_data.get('teacher'),
                location=course_data.get('location'),
                duration=duration
            )
            courses.append(course)
        
        # 批量保存课程
        for course in courses:
            try:
                course_service.create_course(course)
            except ConflictException:
                # 忽略已存在的课程
                pass
        
        return jsonify({"message": "课程批量保存成功"}), 200
    except ValidationException as e:
        errors: List[str] = getattr(e, 'errors', [])
        return jsonify({"error": "数据验证失败", "details": errors}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500