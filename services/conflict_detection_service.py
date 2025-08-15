"""
课程冲突检测服务
提供课程时间、教师、地点冲突检测功能
"""

from typing import List, Dict
from models.class_item import ClassItem
from models.class_plan import ClassPlan
from utils.logger import get_service_logger

# 初始化日志记录器
logger = get_service_logger("conflict_detection_service")


class ConflictDetectionService:
    """课程冲突检测服务类"""
    
    def __init__(self):
        """初始化课程冲突检测服务"""
        logger.info("ConflictDetectionService initialized")
    
    def detect_course_conflicts(self, course: ClassItem) -> List[str]:
        """
        检测课程冲突
        
        Args:
            course: 要检测的课程
            
        Returns:
            冲突信息列表
        """
        logger.info(f"检测课程冲突: {course.id}")
        
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory
            
            # 获取课程服务
            course_service = ServiceFactory.get_course_service()
            
            # 获取所有现有课程（排除自身）
            existing_courses = [
                c for c in course_service.get_all_courses() 
                if c.id != course.id
            ]
            
            # 检测冲突
            conflicts = []
            
            # 检测教师时间冲突
            teacher_conflicts = self._detect_teacher_conflict(course, existing_courses)
            conflicts.extend(teacher_conflicts)
            
            # 检测地点资源冲突
            location_conflicts = self._detect_location_conflict(course, existing_courses)
            conflicts.extend(location_conflicts)
            
            # 检测课程时间冲突
            time_conflicts = self._detect_time_conflict(course, existing_courses)
            conflicts.extend(time_conflicts)
            
            if conflicts:
                logger.warning(f"检测到 {len(conflicts)} 个冲突")
            else:
                logger.info("未检测到冲突")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"检测课程冲突失败: {str(e)}")
            return []
    
    def detect_schedule_conflicts(self, schedule: ClassPlan) -> List[str]:
        """
        检测课程表冲突
        
        Args:
            schedule: 要检测的课程表项
            
        Returns:
            冲突信息列表
        """
        logger.info(f"检测课程表冲突: {schedule.id}")
        
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory
            
            # 获取课程服务和课程表服务
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            
            # 获取相关课程
            course = course_service.get_course_by_id(schedule.course_id)
            if not course:
                logger.warning(f"未找到课程: {schedule.course_id}")
                return []
            
            # 获取所有现有课程表项（排除自身）
            existing_schedules = [
                s for s in schedule_service.get_all_schedules() 
                if s.id != schedule.id
            ]
            
            # 检测冲突
            conflicts = []
            
            # 检测时间冲突
            time_conflicts = self._detect_schedule_time_conflict(
                schedule, course, existing_schedules, course_service
            )
            conflicts.extend(time_conflicts)
            
            if conflicts:
                logger.warning(f"检测到 {len(conflicts)} 个课程表冲突")
            else:
                logger.info("未检测到课程表冲突")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"检测课程表冲突失败: {str(e)}")
            return []
    
    def _detect_teacher_conflict(self, course: ClassItem, existing_courses: List[ClassItem]) -> List[str]:
        """
        检测教师时间冲突
        
        Args:
            course: 要检测的课程
            existing_courses: 现有课程列表
            
        Returns:
            冲突信息列表
        """
        conflicts = []
        
        for existing_course in existing_courses:
            # 如果是同一个教师且时间冲突
            if (existing_course.teacher == course.teacher and 
                self._is_time_conflict(course, existing_course)):
                conflicts.append(f"教师 {course.teacher} 在 {course.duration.start_time}-{course.duration.end_time} 时间段已有课程")
        
        return conflicts
    
    def _detect_location_conflict(self, course: ClassItem, existing_courses: List[ClassItem]) -> List[str]:
        """
        检测地点资源冲突
        
        Args:
            course: 要检测的课程
            existing_courses: 现有课程列表
            
        Returns:
            冲突信息列表
        """
        conflicts = []
        
        for existing_course in existing_courses:
            # 如果是同一个地点且时间冲突
            if (existing_course.location == course.location and 
                self._is_time_conflict(course, existing_course)):
                conflicts.append(f"地点 {course.location} 在 {course.duration.start_time}-{course.duration.end_time} 时间段已被占用")
        
        return conflicts
    
    def _detect_time_conflict(self, course1: ClassItem, existing_courses: List[ClassItem]) -> List[str]:
        """
        检测课程时间冲突
        
        Args:
            course1: 要检测的课程
            existing_courses: 现有课程列表
            
        Returns:
            冲突信息列表
        """
        conflicts = []
        
        for course2 in existing_courses:
            # 如果时间冲突
            if self._is_time_conflict(course1, course2):
                conflicts.append(f"课程时间 {course1.duration.start_time}-{course1.duration.end_time} 与课程 {course2.name} 冲突")
        
        return conflicts
    
    def _detect_schedule_time_conflict(self, schedule: ClassPlan, course: ClassItem, 
                                     existing_schedules: List[ClassPlan], 
                                     course_service) -> List[str]:
        """
        检测课程表时间冲突
        
        Args:
            schedule: 要检测的课程表项
            course: 对应的课程
            existing_schedules: 现有课程表项列表
            course_service: 课程服务实例
            
        Returns:
            冲突信息列表
        """
        conflicts = []
        
        for existing_schedule in existing_schedules:
            # 检查星期几是否相同
            if existing_schedule.day_of_week == schedule.day_of_week:
                # 获取对应的课程
                existing_course = course_service.get_course_by_id(existing_schedule.course_id)
                if not existing_course:
                    continue
                
                # 检查时间是否冲突
                if self._is_time_conflict(course, existing_course):
                    conflicts.append(f"星期{schedule.day_of_week}的{course.duration.start_time}-{course.duration.end_time}时间段与课程{existing_course.name}冲突")
        
        return conflicts
    
    def _is_time_conflict(self, course1: ClassItem, course2: ClassItem) -> bool:
        """
        检查两个课程的时间是否冲突
        
        Args:
            course1: 第一个课程
            course2: 第二个课程
            
        Returns:
            是否冲突
        """
        try:
            # 解析开始时间
            start1_parts = course1.duration.start_time.split(':')
            start1_hour = int(start1_parts[0])
            start1_minute = int(start1_parts[1])
            
            # 解析结束时间
            end1_parts = course1.duration.end_time.split(':')
            end1_hour = int(end1_parts[0])
            end1_minute = int(end1_parts[1])
            
            # 解析开始时间
            start2_parts = course2.duration.start_time.split(':')
            start2_hour = int(start2_parts[0])
            start2_minute = int(start2_parts[1])
            
            # 解析结束时间
            end2_parts = course2.duration.end_time.split(':')
            end2_hour = int(end2_parts[0])
            end2_minute = int(end2_parts[1])
            
            # 转换为分钟进行比较
            start1_minutes = start1_hour * 60 + start1_minute
            end1_minutes = end1_hour * 60 + end1_minute
            start2_minutes = start2_hour * 60 + start2_minute
            end2_minutes = end2_hour * 60 + end2_minute
            
            # 检查是否有时间重叠
            return not (end1_minutes <= start2_minutes or end2_minutes <= start1_minutes)
            
        except Exception as e:
            logger.warning(f"时间冲突检测失败: {str(e)}")
            return False  # 如果解析失败，默认不冲突