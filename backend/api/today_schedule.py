"""
今日课程安排 API 接口
"""

from flask import Blueprint, jsonify
from services.service_factory import ServiceFactory
from datetime import datetime

# 创建今日课程安排蓝图
today_schedule_bp = Blueprint('today_schedule', __name__)

# 获取服务实例
course_service = ServiceFactory.get_course_service()
schedule_service = ServiceFactory.get_schedule_service()
temp_change_service = ServiceFactory.get_temp_change_service()


@today_schedule_bp.route('/today_schedule', methods=['GET'])
def get_today_schedule():
    """
    获取今天的课程安排
    """
    try:
        # 获取今天的日期
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        # 获取今天的临时换课
        temp_changes = temp_change_service.get_temp_changes_by_date(today_str)
        
        # 检查是否有未使用的临时换课
        for temp_change in temp_changes:
            if not temp_change.used:
                # 获取新课程
                course = course_service.get_course_by_id(temp_change.new_course_id)
                if course:
                    return jsonify({
                        "type": "temp",
                        "course": course.to_dict()
                    }), 200
        
        # 获取今天的课程表项
        schedules = schedule_service.get_schedules_by_date(today_str)
        
        # 如果有课程表项，返回第一个
        if schedules:
            schedule = schedules[0]
            course = course_service.get_course_by_id(schedule.course_id)
            if course:
                return jsonify({
                    "type": "regular",
                    "course": course.to_dict()
                }), 200
        
        # 没有课程
        return jsonify({"type": "none"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500