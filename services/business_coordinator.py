"""
业务逻辑层主协调器
协调各个服务之间的交互，处理复杂的业务逻辑
"""

from typing import List
from datetime import datetime, timedelta
from models.class_item import ClassItem
from models.class_plan import ClassPlan
from models.temp_change import TempChange
from models.cycle_schedule import CycleSchedule, ScheduleItem
from services.service_factory import ServiceFactory
from utils.logger import get_service_logger

# 初始化日志记录器
logger = get_service_logger("business_coordinator")


class BusinessCoordinator:
    """业务逻辑层主协调器类"""
    
    def __init__(self):
        """初始化业务协调器"""
        logger.info("BusinessCoordinator initialized")
    
    def create_course_with_schedule(self, course: ClassItem, schedule: ClassPlan) -> tuple[ClassItem, ClassPlan]:
        """
        创建课程并关联课程表项
        
        Args:
            course: 课程对象
            schedule: 课程表对象
            
        Returns:
            (创建的课程对象, 创建的课程表对象)
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 课程或课程表冲突
        """
        logger.info(f"Creating course with schedule: course={course.id}, schedule={schedule.id}")
        
        try:
            # 获取服务实例
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            
            # 创建课程
            created_course = course_service.create_course(course)
            
            # 设置课程表项的课程ID
            schedule.course_id = created_course.id
            
            # 创建课程表项
            created_schedule = schedule_service.create_schedule(schedule)
            
            logger.info(f"Course {created_course.id} and schedule {created_schedule.id} created successfully")
            return created_course, created_schedule
        except Exception as e:
            logger.error(f"Failed to create course with schedule: {str(e)}")
            raise
    
    def apply_temp_change(self, temp_change: TempChange) -> bool:
        """
        应用临时换课
        
        Args:
            temp_change: 临时换课对象
            
        Returns:
            是否应用成功
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 原课程表项未找到
            ConflictException: 临时换课冲突
        """
        logger.info(f"Applying temp change: {temp_change.id}")
        
        try:
            # 获取服务实例
            temp_change_service = ServiceFactory.get_temp_change_service()
            
            # 创建临时换课
            created_temp_change = temp_change_service.create_temp_change(temp_change)
            
            # 标记临时换课为已使用
            temp_change_service.mark_temp_change_as_used(created_temp_change.id)
            
            logger.info(f"Temp change {created_temp_change.id} applied successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to apply temp change: {str(e)}")
            raise
    
    def generate_cycle_schedule(self, cycle_schedule: CycleSchedule, start_date_str: str, weeks: int) -> List[ClassPlan]:
        """
        生成循环课程表
        
        Args:
            cycle_schedule: 循环课程表对象
            start_date_str: 开始日期字符串 (YYYY-MM-DD)
            weeks: 生成周数
            
        Returns:
            生成的课程表项列表
        """
        logger.info(f"Generating cycle schedule: {cycle_schedule.id} for {weeks} weeks starting from {start_date_str}")
        
        try:
            # 获取服务实例
            cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
            schedule_service = ServiceFactory.get_schedule_service()
            
            # 创建循环课程表
            created_cycle_schedule = cycle_schedule_service.create_cycle_schedule(cycle_schedule)
            
            # 生成课程表项
            generated_schedules = []
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            
            for i in range(weeks):
                # 计算当前周的日期
                current_date = start_date + timedelta(weeks=i)
                current_date_str = current_date.strftime("%Y-%m-%d")
                
                # 生成当前周的课程表项
                schedule_items = cycle_schedule_service.generate_schedule_for_date(
                    created_cycle_schedule.id, 
                    current_date_str, 
                    start_date_str
                )
                
                # 创建课程表项
                for schedule_item in schedule_items:
                    # 计算星期几
                    day_of_week = schedule_item.day_of_week
                    # 计算具体日期
                    # 获取当前周的周一
                    monday = current_date - timedelta(days=current_date.weekday())
                    schedule_date = monday + timedelta(days=day_of_week)
                    schedule_date_str = schedule_date.strftime("%Y-%m-%d")
                    
                    # 创建课程表对象
                    schedule = ClassPlan(
                        id=f"schedule_{created_cycle_schedule.id}_{schedule_date_str}_{schedule_item.course_id}",
                        day_of_week=day_of_week,
                        week_parity="both",  # 循环课程表默认为每周都有
                        course_id=schedule_item.course_id,
                        valid_from=schedule_date_str,
                        valid_to=schedule_date_str
                    )
                    
                    # 创建课程表项
                    created_schedule = schedule_service.create_schedule(schedule)
                    generated_schedules.append(created_schedule)
            
            logger.info(f"Generated {len(generated_schedules)} schedules for cycle schedule {created_cycle_schedule.id}")
            return generated_schedules
        except Exception as e:
            logger.error(f"Failed to generate cycle schedule: {str(e)}")
            raise
    
    def get_weekly_schedule(self, date_str: str) -> List[tuple[ClassItem, ClassPlan]]:
        """
        获取指定日期的周课程表
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            课程和课程表项的元组列表
        """
        logger.info(f"Getting weekly schedule for date: {date_str}")
        
        try:
            # 获取服务实例
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            temp_change_service = ServiceFactory.get_temp_change_service()
            
            # 获取指定日期的课程表项
            schedules = schedule_service.get_schedules_by_date(date_str)
            
            # 获取临时换课
            temp_changes = temp_change_service.get_temp_changes_by_date(date_str)
            
            # 构建课程表
            weekly_schedule = []
            for schedule in schedules:
                # 检查是否有临时换课
                temp_change = None
                for tc in temp_changes:
                    if tc.original_schedule_id == schedule.id and not tc.used:
                        temp_change = tc
                        break
                
                # 获取课程
                course = course_service.get_course_by_id(
                    temp_change.new_course_id if temp_change else schedule.course_id
                )
                
                if course:
                    weekly_schedule.append((course, schedule))
            
            logger.info(f"Retrieved {len(weekly_schedule)} items for weekly schedule")
            return weekly_schedule
        except Exception as e:
            logger.error(f"Failed to get weekly schedule: {str(e)}")
            raise