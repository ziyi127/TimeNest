"""
统计分析服务
提供课程统计、时间统计、教师统计等业务逻辑处理
"""

from typing import Dict, List
from models.statistics import CourseStatistics, TimeStatistics, TeacherStatistics
from utils.logger import get_service_logger

# 初始化日志记录器
logger = get_service_logger("statistics_service")


class StatisticsService:
    """统计分析服务类"""
    
    def __init__(self):
        """初始化统计分析服务"""
        logger.info("StatisticsService initialized")
    
    def get_course_statistics(self) -> CourseStatistics:
        """
        获取课程统计信息
        
        Returns:
            课程统计对象
        """
        logger.info("获取课程统计信息")
        
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory
            
            # 获取课程服务
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            
            # 获取所有课程和课程表项
            courses = course_service.get_all_courses()
            schedules = schedule_service.get_all_schedules()
            
            # 统计总数
            total_courses = len(courses)
            
            # 按教师统计
            courses_by_teacher: Dict[str, int] = {}
            for course in courses:
                teacher = course.teacher
                courses_by_teacher[teacher] = courses_by_teacher.get(teacher, 0) + 1
            # 按教师统计
            courses_by_teacher: Dict[str, int] = {}
            for course in courses:
                teacher = course.teacher
                courses_by_teacher[teacher] = courses_by_teacher.get(teacher, 0) + 1
            
            # 按地点统计
            courses_by_location: Dict[str, int] = {}
            for course in courses:
                location = course.location
                courses_by_location[location] = courses_by_location.get(location, 0) + 1
            # 按地点统计
            courses_by_location: Dict[str, int] = {}
            for course in courses:
                location = course.location
                courses_by_location[location] = courses_by_location.get(location, 0) + 1
            
            # 按星期统计
            courses_by_day: Dict[int, int] = {}
            for schedule in schedules:
                day = schedule.day_of_week
                courses_by_day[day] = courses_by_day.get(day, 0) + 1
            # 按星期统计
            courses_by_day: Dict[int, int] = {}
            for schedule in schedules:
                day = schedule.day_of_week
                courses_by_day[day] = courses_by_day.get(day, 0) + 1
            
            # 创建统计对象
            stats = CourseStatistics(
                total_courses=total_courses,
                courses_by_teacher=courses_by_teacher,
                courses_by_location=courses_by_location,
                courses_by_day=courses_by_day
            )
            
            logger.info(f"课程统计完成: 共{total_courses}门课程")
            return stats
            
        except Exception as e:
            logger.error(f"获取课程统计信息失败: {str(e)}")
            # 返回空的统计对象
            return CourseStatistics()
    
    def get_time_statistics(self) -> TimeStatistics:
        """
        获取时间统计信息
        
        Returns:
            时间统计对象
        """
        logger.info("获取时间统计信息")
        
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory
            
            # 获取课程服务
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            
            # 获取所有课程和课程表项
            courses = course_service.get_all_courses()
            schedules = schedule_service.get_all_schedules()
            
            # 计算总课时
            total_class_hours = 0.0
            class_hours_by_day: Dict[int, float] = {}
            class_hours_by_teacher: Dict[str, float] = {}
            time_slots: Dict[str, float] = {}  # 用于统计高峰时段
            
            # 遍历课程表项和课程
            for schedule in schedules:
                # 查找对应的课程
                course = course_service.get_course_by_id(schedule.course_id)
                if not course:
                    continue
                
                # 简化计算课程时长（小时）
                try:
                    # 解析开始时间
                    start_parts = course.duration.start_time.split(':')
                    start_hour = int(start_parts[0])
                    start_minute = int(start_parts[1])
                    
                    # 解析结束时间
                    end_parts = course.duration.end_time.split(':')
                    end_hour = int(end_parts[0])
                    end_minute = int(end_parts[1])
                    
                    # 计算时长（小时）
                    duration = (end_hour * 60 + end_minute - start_hour * 60 - start_minute) / 60.0
                except Exception as e:
                    logger.warning(f"计算课程 {course.id} 时长失败: {str(e)}")
                    continue
                
                # 累加总课时
                total_class_hours += duration
                
                # 按星期统计
                day = schedule.day_of_week
                class_hours_by_day[day] = class_hours_by_day.get(day, 0.0) + duration
                
                # 按教师统计
                teacher = course.teacher
                class_hours_by_teacher[teacher] = class_hours_by_teacher.get(teacher, 0.0) + duration
                
                # 统计时间段（用于高峰时段分析）
                time_key = f"{course.duration.start_time}-{course.duration.end_time}"
                time_slots[time_key] = time_slots.get(time_key, 0.0) + 1
            
            # 找出高峰时段（前3个最繁忙的时间段）
            sorted_time_slots = sorted(time_slots.items(), key=lambda x: x[1], reverse=True)
            peak_hours = [slot[0] for slot in sorted_time_slots[:3]]
            
            # 创建统计对象
            stats = TimeStatistics(
                total_class_hours=total_class_hours,
                class_hours_by_day=class_hours_by_day,
                class_hours_by_teacher=class_hours_by_teacher,
                peak_hours=peak_hours
            )
            
            logger.info(f"时间统计完成: 总课时{total_class_hours:.2f}小时")
            return stats
            
        except Exception as e:
            logger.error(f"获取时间统计信息失败: {str(e)}")
            # 返回空的统计对象
            return TimeStatistics()
    
    def get_teacher_statistics(self) -> TeacherStatistics:
        """
        获取教师统计信息
        
        Returns:
            教师统计对象
        """
        logger.info("获取教师统计信息")
        
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory
            
            # 获取课程服务
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            
            # 获取所有课程和课程表项
            courses = course_service.get_all_courses()
            schedules = schedule_service.get_all_schedules()
            
            # 统计教师总数
            teachers = set(course.teacher for course in courses)
            total_teachers = len(teachers)
            
            # 按教师统计课程数
            courses_per_teacher: Dict[str, int] = {}
            for course in courses:
                teacher = course.teacher
                courses_per_teacher[teacher] = courses_per_teacher.get(teacher, 0) + 1
            
            # 按教师统计课时
            hours_per_teacher: Dict[str, float] = {}
            
            # 遍历课程表项和课程
            for schedule in schedules:
                # 查找对应的课程
                course = course_service.get_course_by_id(schedule.course_id)
                if not course:
                    continue
                
                # 简化计算课程时长（小时）
                try:
                    # 解析开始时间
                    start_parts = course.duration.start_time.split(':')
                    start_hour = int(start_parts[0])
                    start_minute = int(start_parts[1])
                    
                    # 解析结束时间
                    end_parts = course.duration.end_time.split(':')
                    end_hour = int(end_parts[0])
                    end_minute = int(end_parts[1])
                    
                    # 计算时长（小时）
                    duration = (end_hour * 60 + end_minute - start_hour * 60 - start_minute) / 60.0
                except Exception as e:
                    logger.warning(f"计算课程 {course.id} 时长失败: {str(e)}")
                    continue
                
                # 按教师统计课时
                teacher = course.teacher
                hours_per_teacher[teacher] = hours_per_teacher.get(teacher, 0.0) + duration
            
            # 找出最繁忙的教师（按课时排序，前3名）
            sorted_teachers = sorted(hours_per_teacher.items(), key=lambda x: x[1], reverse=True)
            most_busy_teachers = [teacher[0] for teacher in sorted_teachers[:3]]
            
            # 创建统计对象
            stats = TeacherStatistics(
                total_teachers=total_teachers,
                courses_per_teacher=courses_per_teacher,
                hours_per_teacher=hours_per_teacher,
                most_busy_teachers=most_busy_teachers
            )
            
            logger.info(f"教师统计完成: 共{total_teachers}名教师")
            return stats
            
        except Exception as e:
            logger.error(f"获取教师统计信息失败: {str(e)}")
            # 返回空的统计对象
            return TeacherStatistics()
    
    def get_all_statistics(self) -> Dict[str, object]:
        """
        获取所有统计信息
        
        Returns:
            包含所有统计信息的字典
        """
        logger.info("获取所有统计信息")
        
        stats: Dict[str, object] = {
            "course_statistics": self.get_course_statistics(),
            "time_statistics": self.get_time_statistics(),
            "teacher_statistics": self.get_teacher_statistics()
        }
        
        logger.info("所有统计信息获取完成")
        return stats
