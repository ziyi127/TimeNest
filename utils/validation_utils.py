"""
数据验证工具函数
提供各种数据验证和业务规则验证功能
<<<<<<< HEAD

=======
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

import re
from datetime import datetime
from typing import List, Tuple
from models.class_item import ClassItem
from models.class_plan import ClassPlan


def validate_course_data(course: ClassItem) -> Tuple[bool, List[str]]:
    """
    验证课程数据
    
    Args:
        course: 课程对象
        
    Returns:
        (is_valid, errors): 是否有效和错误信息列表
    """
    errors = []
    
    # 验证课程ID
    if not course.id or not isinstance(course.id, str) or len(course.id.strip()) == 0:
        errors.append("课程ID不能为空")
    
    # 验证课程名称
    if not course.name or not isinstance(course.name, str) or len(course.name.strip()) == 0:
        errors.append("课程名称不能为空")
    
    # 验证教师姓名
    if not course.teacher or not isinstance(course.teacher, str) or len(course.teacher.strip()) == 0:
        errors.append("教师姓名不能为空")
    
    # 验证教室位置
    if not course.location or not isinstance(course.location, str) or len(course.location.strip()) == 0:
        errors.append("教室位置不能为空")
    
    # 验证时间格式
    if not course.duration:
        errors.append("课程时间不能为空")
    else:
        start_time = course.duration.start_time
        end_time = course.duration.end_time
        
        # 验证时间格式 (HH:MM)
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, start_time):
            errors.append(f"开始时间格式不正确: {start_time}")
        if not re.match(time_pattern, end_time):
            errors.append(f"结束时间格式不正确: {end_time}")
        
        # 验证开始时间应该早于结束时间
        if re.match(time_pattern, start_time) and re.match(time_pattern, end_time):
            start_h, start_m = map(int, start_time.split(':'))
            end_h, end_m = map(int, end_time.split(':'))
            if start_h > end_h or (start_h == end_h and start_m >= end_m):
                errors.append("开始时间应该早于结束时间")
    
    return len(errors) == 0, errors


def validate_schedule_data(schedule: ClassPlan) -> Tuple[bool, List[str]]:
    """
    验证课程表数据
    
    Args:
        schedule: 课程表对象
        
    Returns:
        (is_valid, errors): 是否有效和错误信息列表
    """
    errors = []
    
    # 验证课程表ID
    if not schedule.id or not isinstance(schedule.id, str) or len(schedule.id.strip()) == 0:
        errors.append("课程表ID不能为空")
    
    # 验证星期几 (0-6)
    if not isinstance(schedule.day_of_week, int) or schedule.day_of_week < 0 or schedule.day_of_week > 6:
        errors.append("星期几必须是0-6之间的整数")
    
    # 验证周奇偶性
    valid_parity = ["odd", "even", "both"]
    if schedule.week_parity not in valid_parity:
        errors.append(f"周奇偶性必须是以下值之一: {', '.join(valid_parity)}")
    
    # 验证课程ID
    if not schedule.course_id or not isinstance(schedule.course_id, str) or len(schedule.course_id.strip()) == 0:
        errors.append("课程ID不能为空")
    
    # 验证日期格式
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, schedule.valid_from):
        errors.append(f"开始日期格式不正确: {schedule.valid_from}")
    if not re.match(date_pattern, schedule.valid_to):
        errors.append(f"结束日期格式不正确: {schedule.valid_to}")
    
    # 验证日期逻辑 (开始日期应该早于或等于结束日期)
    if re.match(date_pattern, schedule.valid_from) and re.match(date_pattern, schedule.valid_to):
        try:
            start_date = datetime.strptime(schedule.valid_from, "%Y-%m-%d")
            end_date = datetime.strptime(schedule.valid_to, "%Y-%m-%d")
            if start_date > end_date:
                errors.append("开始日期应该早于或等于结束日期")
        except ValueError:
            errors.append("日期格式无法解析")
    
    return len(errors) == 0, errors


def validate_time_conflict(course1: ClassItem, course2: ClassItem) -> bool:
    """
    检查两个课程的时间是否冲突
    
    Args:
        course1: 第一个课程
        course2: 第二个课程
        
    Returns:
        是否冲突
    """
    # 如果是同一个课程，不冲突
    if course1.id == course2.id:
        return False
    
    # 检查时间是否冲突
    return _has_time_overlap(
        course1.duration.start_time,
        course1.duration.end_time,
        course2.duration.start_time,
        course2.duration.end_time
    )

def _has_time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """
    检查两个时间段是否有重叠
    
    Args:
        start1: 第一个时间段的开始时间(HH:MM)
        end1: 第一个时间段的结束时间(HH:MM)
        start2: 第二个时间段的开始时间(HH:MM)
        end2: 第二个时间段的结束时间(HH:MM)
        
    Returns:
        是否有时间重叠
    """
    start1_h, start1_m = map(int, start1.split(':'))
    end1_h, end1_m = map(int, end1.split(':'))
    start2_h, start2_m = map(int, start2.split(':'))
    end2_h, end2_m = map(int, end2.split(':'))
    
    # 转换为分钟进行比较
    start1_minutes = start1_h * 60 + start1_m
    end1_minutes = end1_h * 60 + end1_m
    start2_minutes = start2_h * 60 + start2_m
    end2_minutes = end2_h * 60 + end2_m
    
    # 检查是否有时间重叠
    return not (end1_minutes <= start2_minutes or end2_minutes <= start1_minutes)


def validate_teacher_conflict(teacher: str, existing_courses: List[ClassItem]) -> Tuple[bool, List[str]]:
    """
    验证教师时间冲突
    
    Args:
        teacher: 教师姓名
        existing_courses: 已存在的课程列表
        
    Returns:
        (is_valid, conflicts): 是否有效和冲突信息列表
    """
    conflicts = []
    
    # 查找该教师的所有课程
    teacher_courses = [course for course in existing_courses if course.teacher == teacher]
    
    # 检查是否有时间冲突
    for i in range(len(teacher_courses)):
        for j in range(i + 1, len(teacher_courses)):
            if validate_time_conflict(teacher_courses[i], teacher_courses[j]):
                conflicts.append(f"教师 {teacher} 在 {teacher_courses[i].duration.start_time}-{teacher_courses[i].duration.end_time} 和 {teacher_courses[j].duration.start_time}-{teacher_courses[j].duration.end_time} 时间段有课程冲突")
    
    return len(conflicts) == 0, conflicts


def validate_location_conflict(location: str, existing_courses: List[ClassItem]) -> Tuple[bool, List[str]]:
    """
    验证教室资源冲突
    
    Args:
        location: 教室位置
        existing_courses: 已存在的课程列表
        
    Returns:
        (is_valid, conflicts): 是否有效和冲突信息列表
    """
    conflicts = []
    
    # 查找该教室的所有课程
    location_courses = [course for course in existing_courses if course.location == location]
    
    # 检查是否有时间冲突
    for i in range(len(location_courses)):
        for j in range(i + 1, len(location_courses)):
            if validate_time_conflict(location_courses[i], location_courses[j]):
                conflicts.append(f"教室 {location} 在 {location_courses[i].duration.start_time}-{location_courses[i].duration.end_time} 和 {location_courses[j].duration.start_time}-{location_courses[j].duration.end_time} 时间段有课程冲突")
    
    return len(conflicts) == 0, conflicts