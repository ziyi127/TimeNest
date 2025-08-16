"""
课程表管理服务
提供课程表相关的业务逻辑处理
"""

from typing import List, Optional
from models.class_item import ClassItem
from models.class_plan import ClassPlan
from utils.validation_utils import validate_schedule_data
from utils.date_utils import is_date_in_range
from utils.logger import get_service_logger
from utils.exceptions import ValidationException, NotFoundException, ConflictException

# 初始化日志记录器
logger = get_service_logger("schedule_service")


class ScheduleService:
    """课程表管理服务类"""
    
    def __init__(self):
        """初始化课程表服务"""
        self.schedules: List[ClassPlan] = []
        logger.info("ScheduleService initialized")
    
    def create_schedule(self, schedule: ClassPlan) -> ClassPlan:
        """
        创建课程表项
        
        Args:
            schedule: 课程表对象
            
        Returns:
            创建的课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 课程表冲突
        """
        logger.info(f"Creating schedule: {schedule.id}")
        
        # 执行创建课程表项的步骤
        self._execute_create_schedule_steps(schedule)
        
        logger.info(f"Schedule {schedule.id} created successfully")
        return schedule
    
    def _execute_create_schedule_steps(self, schedule: ClassPlan) -> None:
        """
        执行创建课程表项的步骤
        
        Args:
            schedule: 课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 课程表冲突
        """
        # 验证课程表数据
        self._validate_schedule_data(schedule)
        
        # 检查课程表ID是否已存在
        self._ensure_schedule_id_unique(schedule.id)
        
        # 添加课程表项
        self._add_schedule(schedule)
    
    def _validate_schedule_data(self, schedule: ClassPlan) -> None:
        """
        验证课程表数据
        
        Args:
            schedule: 课程表对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        is_valid, errors = validate_schedule_data(schedule)
        if not is_valid:
            logger.warning(f"Schedule validation failed: {errors}")
            raise ValidationException("课程表数据验证失败", errors)
    
    def _ensure_schedule_id_unique(self, schedule_id: str) -> None:
        """
        确保课程表ID唯一
        
        Args:
            schedule_id: 课程表ID
            
        Raises:
            ConflictException: 课程表ID已存在
        """
        if self.get_schedule_by_id(schedule_id):
            logger.warning(f"Schedule with id {schedule_id} already exists")
            raise ConflictException(f"课程表ID {schedule_id} 已存在")
    
    def _add_schedule(self, schedule: ClassPlan) -> None:
        """
        添加课程表项到列表
        
        Args:
            schedule: 课程表对象
        """
        self.schedules.append(schedule)
    
    def update_schedule(self, schedule_id: str, updated_schedule: ClassPlan) -> ClassPlan:
        """
        更新课程表项
        
        Args:
            schedule_id: 课程表ID
            updated_schedule: 更新的课程表对象
            
        Returns:
            更新后的课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 课程表未找到
        """
        logger.info(f"Updating schedule: {schedule_id}")
        
        # 执行更新课程表项的步骤
        self._execute_update_schedule_steps(schedule_id, updated_schedule)
        
        logger.info(f"Schedule {schedule_id} updated successfully")
        return updated_schedule
    
    def _execute_update_schedule_steps(self, schedule_id: str, updated_schedule: ClassPlan) -> None:
        """
        执行更新课程表项的步骤
        
        Args:
            schedule_id: 课程表ID
            updated_schedule: 更新的课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 课程表未找到
        """
        # 验证课程表数据
        self._validate_schedule_data(updated_schedule)
        
        # 查找要更新的课程表项
        schedule_index = self._find_schedule_index(schedule_id)
        self._ensure_schedule_exists(schedule_id, schedule_index)
        
        # 更新课程表项
        self._update_schedule_at_index(schedule_index, updated_schedule)
    
    def _ensure_schedule_exists(self, schedule_id: str, schedule_index: int) -> None:
        """
        确保课程表项存在
        
        Args:
            schedule_id: 课程表ID
            schedule_index: 课程表项索引
            
        Raises:
            NotFoundException: 课程表未找到
        """
        if schedule_index == -1:
            logger.warning(f"Schedule {schedule_id} not found")
            raise NotFoundException(f"课程表 {schedule_id} 未找到")
    
    def _update_schedule_at_index(self, index: int, schedule: ClassPlan) -> None:
        """
        在指定索引处更新课程表项
        
        Args:
            index: 课程表项索引
            schedule: 新的课程表对象
        """
        self.schedules[index] = schedule
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """
        删除课程表项
        
        Args:
            schedule_id: 课程表ID
            
        Returns:
            是否删除成功
            
        Raises:
            NotFoundException: 课程表未找到
        """
        logger.info(f"Deleting schedule: {schedule_id}")
        
        # 执行删除课程表项的步骤
        self._execute_delete_schedule_steps(schedule_id)
        
        logger.info(f"Schedule {schedule_id} deleted successfully")
        return True
    
    def _execute_delete_schedule_steps(self, schedule_id: str) -> None:
        """
        执行删除课程表项的步骤
        
        Args:
            schedule_id: 课程表ID
            
        Raises:
            NotFoundException: 课程表未找到
        """
        # 查找要删除的课程表项
        schedule_index = self._find_schedule_index(schedule_id)
        self._ensure_schedule_exists(schedule_id, schedule_index)
        
        # 删除课程表项
        self._remove_schedule_at_index(schedule_index)
    
    def _remove_schedule_at_index(self, index: int) -> None:
        """
        删除指定索引处的课程表项
        
        Args:
            index: 课程表项索引
        """
        del self.schedules[index]
    
    def get_schedule_by_id(self, schedule_id: str) -> Optional[ClassPlan]:
        """
        根据ID获取课程表项
        
        Args:
            schedule_id: 课程表ID
            
        Returns:
            课程表对象，如果未找到则返回None
        """
        logger.debug(f"Getting schedule by id: {schedule_id}")
        
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                logger.debug(f"Schedule {schedule_id} found")
                return schedule
        
        logger.debug(f"Schedule {schedule_id} not found")
        return None
    
    def get_all_schedules(self) -> List[ClassPlan]:
        """
        获取所有课程表项
        
        Returns:
            课程表项列表
        """
        logger.debug("Getting all schedules")
        return self.schedules.copy()
    
    def get_schedules_by_date(self, date_str: str) -> List[ClassPlan]:
        """
        根据日期获取课程表项
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            指定日期的课程表项列表
        """
        logger.debug(f"Getting schedules by date: {date_str}")
        
        result = self._filter_schedules_by_date(date_str)
        
        logger.debug(f"Found {len(result)} schedules for date {date_str}")
        return result
    
    def _filter_schedules_by_date(self, date_str: str) -> List[ClassPlan]:
        """
        根据日期过滤课程表项
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            指定日期的课程表项列表
        """
        return [
            schedule for schedule in self.schedules 
            if self._is_schedule_valid_on_date(schedule, date_str)
        ]
    
    def _is_schedule_valid_on_date(self, schedule: ClassPlan, date_str: str) -> bool:
        """
        检查课程表项在指定日期是否有效
        
        Args:
            schedule: 课程表项
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            课程表项在指定日期是否有效
        """
        return is_date_in_range(date_str, schedule.valid_from, schedule.valid_to)
    
    def get_schedules_by_course(self, course_id: str) -> List[ClassPlan]:
        """
        根据课程ID获取课程表项
        
        Args:
            course_id: 课程ID
            
        Returns:
            指定课程的课程表项列表
        """
        logger.debug(f"Getting schedules by course: {course_id}")
        
        result = self._filter_schedules_by_course(course_id)
        
        logger.debug(f"Found {len(result)} schedules for course {course_id}")
        return result
    
    def _filter_schedules_by_course(self, course_id: str) -> List[ClassPlan]:
        """
        根据课程ID过滤课程表项
        
        Args:
            course_id: 课程ID
            
        Returns:
            指定课程的课程表项列表
        """
        return [
            schedule for schedule in self.schedules 
            if self._is_schedule_for_course(schedule, course_id)
        ]
    
    def _is_schedule_for_course(self, schedule: ClassPlan, course_id: str) -> bool:
        """
        检查课程表项是否属于指定课程
        
        Args:
            schedule: 课程表项
            course_id: 课程ID
            
        Returns:
            课程表项是否属于指定课程
        """
        return schedule.course_id == course_id
    
    def _find_schedule_index(self, schedule_id: str) -> int:
        """
        查找课程表项在列表中的索引
        
        Args:
            schedule_id: 课程表ID
            
        Returns:
            课程表项索引，如果未找到则返回-1
        """
        for i, schedule in enumerate(self.schedules):
            if schedule.id == schedule_id:
                return i
        return -1