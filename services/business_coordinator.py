"""
业务逻辑层主协调器
协调各个服务之间的交互，处理复杂的业务逻辑
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from models.class_item import ClassItem
from models.class_plan import ClassPlan
from models.temp_change import TempChange
from models.cycle_schedule import CycleSchedule, ScheduleItem
from services.service_factory import ServiceFactory
from services.course_service import CourseService
from services.schedule_service import ScheduleService
from services.temp_change_service import TempChangeService
from services.cycle_schedule_service import CycleScheduleService
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
            # 执行创建课程和课程表项的步骤
            result = self._create_course_with_schedule_steps(course, schedule)
            
            logger.info(f"Course {result[0].id} and schedule {result[1].id} created successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to create course with schedule: {str(e)}")
            raise
    
    def _create_course_with_schedule_steps(self, course: ClassItem, schedule: ClassPlan) -> tuple[ClassItem, ClassPlan]:
        """
        执行创建课程和课程表项的步骤
        
        Args:
            course: 课程对象
            schedule: 课程表对象
            
        Returns:
            (创建的课程对象, 创建的课程表对象)
        """
        # 获取服务实例
        services = self._get_course_schedule_services()
        
        # 创建课程和课程表项
        return self._create_course_and_schedule(services, course, schedule)
    
    def _get_course_schedule_services(self) -> Dict[str, object]:
        """
        获取创建课程和课程表所需的服务实例
        
        Returns:
            包含所需服务实例的字典
        """
        return {
            "course_service": ServiceFactory.get_course_service(),
            "schedule_service": ServiceFactory.get_schedule_service()
        }
    
    def _create_course_and_schedule(self, services: Dict[str, object], course: ClassItem, 
                                    schedule: ClassPlan) -> Tuple[ClassItem, ClassPlan]:
        """
        创建课程和课程表项
        
        Args:
            services: 服务实例字典
            course: 课程对象
            schedule: 课程表对象
            
        Returns:
            (创建的课程对象, 创建的课程表对象)
        """
        # 获取服务实例
        course_service: CourseService = services["course_service"]
        schedule_service: ScheduleService = services["schedule_service"]
        
        # 创建课程
        created_course = course_service.create_course(course)
        
        # 设置课程表项的课程ID
        schedule.course_id = created_course.id
        
        # 创建课程表项
        created_schedule = schedule_service.create_schedule(schedule)
        
        return created_course, created_schedule
    
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
            # 执行应用临时换课的步骤
            self._apply_temp_change_steps(temp_change)
            
            logger.info(f"Temp change {temp_change.id} applied successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to apply temp change: {str(e)}")
            raise
    
    def _apply_temp_change_steps(self, temp_change: TempChange) -> None:
        """
        执行应用临时换课的步骤
        
        Args:
            temp_change: 临时换课对象
        """
        # 获取服务实例
        temp_change_service = self._get_temp_change_service()
        
        # 创建并标记临时换课为已使用
        self._create_and_mark_temp_change(temp_change_service, temp_change)
    
    def _get_temp_change_service(self) -> TempChangeService:
        """
        获取临时换课服务实例
        
        Returns:
            临时换课服务实例
        """
        return ServiceFactory.get_temp_change_service()
    
    def _create_and_mark_temp_change(self, temp_change_service: TempChangeService, temp_change: TempChange) -> None:
        """
        创建并标记临时换课为已使用
        
        Args:
            temp_change_service: 临时换课服务实例
            temp_change: 临时换课对象
        """
        # 创建临时换课
        created_temp_change = temp_change_service.create_temp_change(temp_change)
        
        # 标记临时换课为已使用
        temp_change_service.mark_temp_change_as_used(created_temp_change.id)
    
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
            services = self._get_cycle_schedule_services()
            
            # 创建并生成循环课程表
            result = self._create_and_generate_cycle_schedule(services, cycle_schedule, start_date_str, weeks)
            
            logger.info(f"Generated {len(result)} schedules for cycle schedule {result[0].id if result else 'unknown'}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate cycle schedule: {str(e)}")
            raise
    
    def _get_cycle_schedule_services(self) -> Dict[str, object]:
        """
        获取循环课程表所需的服务实例
        
        Returns:
            包含所需服务实例的字典
        """
        return {
            "cycle_schedule_service": ServiceFactory.get_cycle_schedule_service(),
            "schedule_service": ServiceFactory.get_schedule_service()
        }
    
    def _create_and_generate_cycle_schedule(self, services: Dict[str, object], cycle_schedule: CycleSchedule, 
                                            start_date_str: str, weeks: int) -> List[ClassPlan]:
        """
        创建并生成循环课程表
        
        Args:
            services: 服务实例字典
            cycle_schedule: 循环课程表对象
            start_date_str: 开始日期字符串 (YYYY-MM-DD)
            weeks: 生成周数
            
        Returns:
            生成的课程表项列表
        """
        # 获取服务实例
        cycle_schedule_service: CycleScheduleService = services["cycle_schedule_service"]
        schedule_service: ScheduleService = services["schedule_service"]
        
        # 创建循环课程表
        created_cycle_schedule = cycle_schedule_service.create_cycle_schedule(cycle_schedule)
        
        # 生成课程表项
        generated_schedules = self._generate_schedules_for_cycle(
            cycle_schedule_service, schedule_service, 
            created_cycle_schedule, start_date_str, weeks)
        
        return generated_schedules
    
    def _generate_schedules_for_cycle(self, cycle_schedule_service: CycleScheduleService, schedule_service: ScheduleService, 
                                      cycle_schedule: CycleSchedule, start_date_str: str, weeks: int) -> List[ClassPlan]:
        """
        为循环课程表生成课程表项
        
        Args:
            cycle_schedule_service: 循环课程表服务实例
            schedule_service: 课程表服务实例
            cycle_schedule: 循环课程表对象
            start_date_str: 开始日期字符串 (YYYY-MM-DD)
            weeks: 生成周数
            
        Returns:
            生成的课程表项列表
        """
        generated_schedules: List[ClassPlan] = []
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        for i in range(weeks):
            # 计算当前周的日期
            current_date = start_date + timedelta(weeks=i)
            current_date_str = current_date.strftime("%Y-%m-%d")
            
            # 生成当前周的课程表项
            schedule_items = cycle_schedule_service.generate_schedule_for_date(
                cycle_schedule.id, 
                current_date_str, 
                start_date_str
            )
            
            # 创建课程表项
            week_schedules = self._create_schedules_for_week(
                schedule_service, cycle_schedule, schedule_items, current_date)
            generated_schedules.extend(week_schedules)
            
        return generated_schedules
    
    def _create_schedules_for_week(self, schedule_service: ScheduleService, cycle_schedule: CycleSchedule, 
                                   schedule_items: List[ScheduleItem], current_date: datetime) -> List[ClassPlan]:
        """
        为一周创建课程表项
        
        Args:
            schedule_service: 课程表服务实例
            cycle_schedule: 循环课程表对象
            schedule_items: 课程表项列表
            current_date: 当前日期
            
        Returns:
            创建的课程表项列表
        """
        week_schedules: List[ClassPlan] = []
        
        for schedule_item in schedule_items:
            # 处理单个课程表项
            created_schedule = self._process_schedule_item(
                schedule_service, cycle_schedule, schedule_item, current_date)
            week_schedules.append(created_schedule)
            
        return week_schedules
    
    def _process_schedule_item(self, schedule_service: ScheduleService, cycle_schedule: CycleSchedule, 
                               schedule_item: ScheduleItem, current_date: datetime) -> ClassPlan:
        """
        处理单个课程表项
        
        Args:
            schedule_service: 课程表服务实例
            cycle_schedule: 循环课程表对象
            schedule_item: 课程表项
            current_date: 当前日期
            
        Returns:
            创建的课程表项
        """
        # 计算具体日期
        schedule_date = self._calculate_schedule_date(current_date, schedule_item.day_of_week)
        schedule_date_str = schedule_date.strftime("%Y-%m-%d")
        
        # 创建课程表对象
        schedule = self._create_schedule_object(cycle_schedule, schedule_item, schedule_date_str)
        
        # 创建课程表项
        return schedule_service.create_schedule(schedule)
    
    def _calculate_schedule_date(self, current_date: datetime, day_of_week: int) -> datetime:
        """
        计算课程表项的具体日期
        
        Args:
            current_date: 当前日期
            day_of_week: 星期几
            
        Returns:
            课程表项的具体日期
        """
        # 获取当前周的周一
        monday = current_date - timedelta(days=current_date.weekday())
        return monday + timedelta(days=day_of_week)
    
    def _create_schedule_object(self, cycle_schedule: CycleSchedule, schedule_item: ScheduleItem, 
                                schedule_date_str: str) -> ClassPlan:
        """
        创建课程表对象
        
        Args:
            cycle_schedule: 循环课程表对象
            schedule_item: 课程表项
            schedule_date_str: 课程表日期字符串
            
        Returns:
            课程表对象
        """
        return ClassPlan(
            id=f"schedule_{cycle_schedule.id}_{schedule_date_str}_{schedule_item.course_id}",
            day_of_week=schedule_item.day_of_week,
            week_parity="both",  # 循环课程表默认为每周都有
            course_id=schedule_item.course_id,
            valid_from=schedule_date_str,
            valid_to=schedule_date_str
        )
    
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
            # 执行获取周课程表的步骤
            weekly_schedule = self._get_weekly_schedule_steps(date_str)
            
            logger.info(f"Retrieved {len(weekly_schedule)} items for weekly schedule")
            return weekly_schedule
        except Exception as e:
            logger.error(f"Failed to get weekly schedule: {str(e)}")
            raise
    
    def _get_weekly_schedule_steps(self, date_str: str) -> List[tuple[ClassItem, ClassPlan]]:
        """
        执行获取周课程表的步骤
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            课程和课程表项的元组列表
        """
        # 获取服务实例
        services = self._get_weekly_schedule_services()
        
        # 获取指定日期的课程表项和临时换课
        schedules, temp_changes = self._get_schedule_data(services, date_str)
        
        # 构建课程表
        return self._build_weekly_schedule(services, schedules, temp_changes)
    
    def _get_weekly_schedule_services(self) -> Dict[str, object]:
        """
        获取周课程表所需的服务实例
        
        Returns:
            包含所需服务实例的字典
        """
        return {
            "course_service": ServiceFactory.get_course_service(),
            "schedule_service": ServiceFactory.get_schedule_service(),
            "temp_change_service": ServiceFactory.get_temp_change_service()
        }
    
    def _get_schedule_data(self, services: Dict[str, object], date_str: str) -> Tuple[List[ClassPlan], List[TempChange]]:
        """
        获取课程表数据
        
        Args:
            services: 服务实例字典
            date_str: 日期字符串
            
        Returns:
            (课程表项列表, 临时换课列表) 的元组
        """
        # 获取服务实例
        schedule_service: ScheduleService = services["schedule_service"]
        temp_change_service: TempChangeService = services["temp_change_service"]
        
        schedules = schedule_service.get_schedules_by_date(date_str)
        temp_changes = temp_change_service.get_temp_changes_by_date(date_str)
        return schedules, temp_changes
    
    def _build_weekly_schedule(self, services: Dict[str, object], schedules: List[ClassPlan], 
                               temp_changes: List[TempChange]) -> List[Tuple[ClassItem, ClassPlan]]:
        """
        构建周课程表
        
        Args:
            services: 服务实例字典
            schedules: 课程表项列表
            temp_changes: 临时换课列表
            
        Returns:
            课程和课程表项的元组列表
        """
        # 获取服务实例
        course_service: CourseService = services["course_service"]
        
        weekly_schedule: List[Tuple[ClassItem, ClassPlan]] = []
        
        for schedule in schedules:
            # 构建单个课程表项
            schedule_item = self._build_schedule_item(services, schedule, temp_changes)
            if schedule_item:
                weekly_schedule.append(schedule_item)
                
        return weekly_schedule
    
    def _build_schedule_item(self, services: Dict[str, object], schedule: ClassPlan, 
                             temp_changes: List[TempChange]) -> Optional[Tuple[ClassItem, ClassPlan]]:
        """
        构建单个课程表项
        
        Args:
            services: 服务实例字典
            schedule: 课程表项
            temp_changes: 临时换课列表
            
        Returns:
            课程和课程表项的元组，如果课程不存在则返回None
        """
        # 获取服务实例
        course_service: CourseService = services["course_service"]
        
        # 检查是否有临时换课
        temp_change = self._find_applicable_temp_change(temp_changes, schedule)
        
        # 获取课程
        course_id = temp_change.new_course_id if temp_change else schedule.course_id
        course = course_service.get_course_by_id(course_id)
        
        if course:
            return (course, schedule)
        return None
    
    def _find_applicable_temp_change(self, temp_changes: List[TempChange], schedule: ClassPlan) -> Optional[TempChange]:
        """
        查找适用于课程表项的临时换课
        
        Args:
            temp_changes: 临时换课列表
            schedule: 课程表项
            
        Returns:
            适用的临时换课，如果未找到则返回None
        """
        for temp_change in temp_changes:
            if temp_change.original_schedule_id == schedule.id and not temp_change.used:
                return temp_change
        return None
