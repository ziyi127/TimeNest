"""
循环课程表服务
提供循环课程表相关的业务逻辑处理
"""

from typing import List, Optional
from models.cycle_schedule import CycleSchedule, CycleScheduleItem, ScheduleItem
from utils.logger import get_service_logger
from utils.exceptions import ValidationException, NotFoundException, ConflictException
from utils.date_utils import get_cycle_week_index

# 初始化日志记录器
logger = get_service_logger("cycle_schedule_service")


class CycleScheduleService:
    """循环课程表服务类"""
    
    def __init__(self):
        """初始化循环课程表服务"""
        self.cycle_schedules: List[CycleSchedule] = []
        logger.info("CycleScheduleService initialized")
    
    def create_cycle_schedule(self, cycle_schedule: CycleSchedule) -> CycleSchedule:
        """
        创建循环课程表
        
        Args:
            cycle_schedule: 循环课程表对象
            
        Returns:
            创建的循环课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 循环课程表冲突
        """
        logger.info(f"Creating cycle schedule: {cycle_schedule.id}")
        
        # 执行创建循环课程表的步骤
        self._execute_create_cycle_schedule_steps(cycle_schedule)
        
        logger.info(f"Cycle schedule {cycle_schedule.id} created successfully")
        return cycle_schedule
    
    def _execute_create_cycle_schedule_steps(self, cycle_schedule: CycleSchedule) -> None:
        """
        执行创建循环课程表的步骤
        
        Args:
            cycle_schedule: 循环课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 循环课程表冲突
        """
        # 验证循环课程表数据
        self._validate_cycle_schedule_data(cycle_schedule)
        
        # 检查循环课程表ID是否已存在
        self._ensure_cycle_schedule_id_unique(cycle_schedule.id)
        
        # 添加循环课程表
        self._add_cycle_schedule(cycle_schedule)
    
    def _validate_cycle_schedule_data(self, cycle_schedule: CycleSchedule) -> None:
        """
        验证循环课程表数据
        
        Args:
            cycle_schedule: 循环课程表对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        is_valid, errors = self._validate_cycle_schedule(cycle_schedule)
        if not is_valid:
            logger.warning(f"Cycle schedule validation failed: {errors}")
            raise ValidationException("循环课程表数据验证失败", errors)
    
    def _ensure_cycle_schedule_id_unique(self, cycle_schedule_id: str) -> None:
        """
        确保循环课程表ID唯一
        
        Args:
            cycle_schedule_id: 循环课程表ID
            
        Raises:
            ConflictException: 循环课程表ID已存在
        """
        if self.get_cycle_schedule_by_id(cycle_schedule_id):
            logger.warning(f"Cycle schedule with id {cycle_schedule_id} already exists")
            raise ConflictException(f"循环课程表ID {cycle_schedule_id} 已存在")
    
    def _add_cycle_schedule(self, cycle_schedule: CycleSchedule) -> None:
        """
        添加循环课程表到列表
        
        Args:
            cycle_schedule: 循环课程表对象
        """
        self.cycle_schedules.append(cycle_schedule)
    
    def update_cycle_schedule(self, cycle_schedule_id: str, updated_cycle_schedule: CycleSchedule) -> CycleSchedule:
        """
        更新循环课程表
        
        Args:
            cycle_schedule_id: 循环课程表ID
            updated_cycle_schedule: 更新的循环课程表对象
            
        Returns:
            更新后的循环课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 循环课程表未找到
        """
        logger.info(f"Updating cycle schedule: {cycle_schedule_id}")
        
        # 执行更新循环课程表的步骤
        self._execute_update_cycle_schedule_steps(cycle_schedule_id, updated_cycle_schedule)
        
        logger.info(f"Cycle schedule {cycle_schedule_id} updated successfully")
        return updated_cycle_schedule
    
    def _execute_update_cycle_schedule_steps(self, cycle_schedule_id: str, updated_cycle_schedule: CycleSchedule) -> None:
        """
        执行更新循环课程表的步骤
        
        Args:
            cycle_schedule_id: 循环课程表ID
            updated_cycle_schedule: 更新的循环课程表对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 循环课程表未找到
        """
        # 验证循环课程表数据
        self._validate_cycle_schedule_data(updated_cycle_schedule)
        
        # 查找要更新的循环课程表
        cycle_schedule_index = self._find_cycle_schedule_index(cycle_schedule_id)
        self._ensure_cycle_schedule_exists(cycle_schedule_id, cycle_schedule_index)
        
        # 更新循环课程表
        self._update_cycle_schedule_at_index(cycle_schedule_index, updated_cycle_schedule)
    
    def _ensure_cycle_schedule_exists(self, cycle_schedule_id: str, cycle_schedule_index: int) -> None:
        """
        确保循环课程表存在
        
        Args:
            cycle_schedule_id: 循环课程表ID
            cycle_schedule_index: 循环课程表索引
            
        Raises:
            NotFoundException: 循环课程表未找到
        """
        if cycle_schedule_index == -1:
            logger.warning(f"Cycle schedule {cycle_schedule_id} not found")
            raise NotFoundException(f"循环课程表 {cycle_schedule_id} 未找到")
    
    def _update_cycle_schedule_at_index(self, index: int, cycle_schedule: CycleSchedule) -> None:
        """
        在指定索引处更新循环课程表
        
        Args:
            index: 循环课程表索引
            cycle_schedule: 新的循环课程表对象
        """
        self.cycle_schedules[index] = cycle_schedule
    
    def delete_cycle_schedule(self, cycle_schedule_id: str) -> bool:
        """
        删除循环课程表
        
        Args:
            cycle_schedule_id: 循环课程表ID
            
        Returns:
            是否删除成功
            
        Raises:
            NotFoundException: 循环课程表未找到
        """
        logger.info(f"Deleting cycle schedule: {cycle_schedule_id}")
        
        # 执行删除循环课程表的步骤
        self._execute_delete_cycle_schedule_steps(cycle_schedule_id)
        
        logger.info(f"Cycle schedule {cycle_schedule_id} deleted successfully")
        return True
    
    def _execute_delete_cycle_schedule_steps(self, cycle_schedule_id: str) -> None:
        """
        执行删除循环课程表的步骤
        
        Args:
            cycle_schedule_id: 循环课程表ID
            
        Raises:
            NotFoundException: 循环课程表未找到
        """
        # 查找要删除的循环课程表
        cycle_schedule_index = self._find_cycle_schedule_index(cycle_schedule_id)
        self._ensure_cycle_schedule_exists(cycle_schedule_id, cycle_schedule_index)
        
        # 删除循环课程表
        self._remove_cycle_schedule_at_index(cycle_schedule_index)
    
    def _remove_cycle_schedule_at_index(self, index: int) -> None:
        """
        删除指定索引处的循环课程表
        
        Args:
            index: 循环课程表索引
        """
        del self.cycle_schedules[index]
    
    def get_cycle_schedule_by_id(self, cycle_schedule_id: str) -> Optional[CycleSchedule]:
        """
        根据ID获取循环课程表
        
        Args:
            cycle_schedule_id: 循环课程表ID
            
        Returns:
            循环课程表对象，如果未找到则返回None
        """
        logger.debug(f"Getting cycle schedule by id: {cycle_schedule_id}")
        
        for cycle_schedule in self.cycle_schedules:
            if cycle_schedule.id == cycle_schedule_id:
                logger.debug(f"Cycle schedule {cycle_schedule_id} found")
                return cycle_schedule
        
        logger.debug(f"Cycle schedule {cycle_schedule_id} not found")
        return None
    
    def get_all_cycle_schedules(self) -> List[CycleSchedule]:
        """
        获取所有循环课程表
        
        Returns:
            循环课程表列表
        """
        logger.debug("Getting all cycle schedules")
        return self.cycle_schedules.copy()
    
    def generate_schedule_for_date(self, cycle_schedule_id: str, date_str: str, start_date_str: str) -> List[ScheduleItem]:
        """
        为指定日期生成课程表项
        
        Args:
            cycle_schedule_id: 循环课程表ID
            date_str: 日期字符串 (YYYY-MM-DD)
            start_date_str: 循环开始日期字符串 (YYYY-MM-DD)
            
        Returns:
            指定日期的课程表项列表
            
        Raises:
            NotFoundException: 循环课程表未找到
        """
        logger.debug(f"Generating schedule for date: {date_str} using cycle schedule: {cycle_schedule_id}")
        
        # 查找并验证循环课程表
        cycle_schedule = self._get_cycle_schedule_or_raise(cycle_schedule_id)
        
        # 计算循环中的周索引
        week_index = self._calculate_week_index(date_str, start_date_str, cycle_schedule.cycle_length)
        
        # 查找对应周的课程表项
        return self._find_schedule_items_by_week_index(cycle_schedule, week_index)
    
    def _get_cycle_schedule_or_raise(self, cycle_schedule_id: str) -> CycleSchedule:
        """
        获取循环课程表，如果未找到则抛出异常
        
        Args:
            cycle_schedule_id: 循环课程表ID
            
        Returns:
            循环课程表对象
            
        Raises:
            NotFoundException: 循环课程表未找到
        """
        cycle_schedule = self.get_cycle_schedule_by_id(cycle_schedule_id)
        if not cycle_schedule:
            logger.warning(f"Cycle schedule {cycle_schedule_id} not found")
            raise NotFoundException(f"循环课程表 {cycle_schedule_id} 未找到")
        return cycle_schedule
    
    def _calculate_week_index(self, date_str: str, start_date_str: str, cycle_length: int) -> int:
        """
        计算循环中的周索引
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            start_date_str: 循环开始日期字符串 (YYYY-MM-DD)
            cycle_length: 循环长度
            
        Returns:
            周索引
        """
        return get_cycle_week_index(date_str, start_date_str, cycle_length)
    
    def _find_schedule_items_by_week_index(self, cycle_schedule: CycleSchedule, week_index: int) -> List[ScheduleItem]:
        """
        根据周索引查找课程表项
        
        Args:
            cycle_schedule: 循环课程表对象
            week_index: 周索引
            
        Returns:
            课程表项列表
        """
        for schedule_item in cycle_schedule.schedules:
            if self._is_matching_week_index(schedule_item, week_index):
                logger.debug(f"Found schedule items for week index {week_index}")
                return schedule_item.schedule_items
        
        logger.debug(f"No schedule items found for week index {week_index}")
        return []
    
    def _is_matching_week_index(self, schedule_item: CycleScheduleItem, week_index: int) -> bool:
        """
        检查课程表项是否匹配指定的周索引
        
        Args:
            schedule_item: 循环课程表项对象
            week_index: 周索引
            
        Returns:
            课程表项是否匹配指定的周索引
        """
        return schedule_item.week_index == week_index
    
    def _find_cycle_schedule_index(self, cycle_schedule_id: str) -> int:
        """
        查找循环课程表在列表中的索引
        
        Args:
            cycle_schedule_id: 循环课程表ID
            
        Returns:
            循环课程表索引，如果未找到则返回-1
        """
        for i, cycle_schedule in enumerate(self.cycle_schedules):
            if cycle_schedule.id == cycle_schedule_id:
                return i
        return -1
    
    def _validate_cycle_schedule(self, cycle_schedule: CycleSchedule) -> tuple[bool, List[str]]:
        """
        验证循环课程表数据
        
        Args:
            cycle_schedule: 循环课程表对象
            
        Returns:
            (is_valid, errors): 是否有效和错误信息列表
        """
        errors: List[str] = []
        
        # 验证基本字段
        self._validate_cycle_schedule_basic_fields(cycle_schedule, errors)
        
        # 验证课程表项
        self._validate_cycle_schedule_items(cycle_schedule, errors)
        
        result: tuple[bool, List[str]] = len(errors) == 0, errors
        return result
    
    def _validate_cycle_schedule_basic_fields(self, cycle_schedule: CycleSchedule, errors: List[str]) -> None:
        """
        验证循环课程表的基本字段
        
        Args:
            cycle_schedule: 循环课程表对象
            errors: 错误信息列表
        """
        # 验证ID
        if not cycle_schedule.id or len(cycle_schedule.id.strip()) == 0:
            errors.append("循环课程表ID不能为空")
        
        # 验证名称
        if not cycle_schedule.name or len(cycle_schedule.name.strip()) == 0:
            errors.append("循环课程表名称不能为空")
        
        # 验证循环长度
        if cycle_schedule.cycle_length <= 0:
            errors.append("循环长度必须是正整数")
    
    def _validate_cycle_schedule_items(self, cycle_schedule: CycleSchedule, errors: List[str]) -> None:
        """
        验证循环课程表的课程表项
        
        Args:
            cycle_schedule: 循环课程表对象
            errors: 错误信息列表
        """
        # 验证课程表项
        for i, schedule_item in enumerate(cycle_schedule.schedules):
            # 验证周索引
            if schedule_item.week_index < 0:
                errors.append(f"课程表项 {i} 的周索引必须是非负整数")
            
            # 验证课程表项列表
            self._validate_schedule_item_list(schedule_item, i, errors)
    
    def _validate_schedule_item_list(self, schedule_item: CycleScheduleItem, index: int, errors: List[str]) -> None:
        """
        验证课程表项列表
        
        Args:
            schedule_item: 循环课程表项对象
            index: 课程表项索引
            errors: 错误信息列表
        """
        for j, schedule_item_item in enumerate(schedule_item.schedule_items):
            # 验证星期几
            if schedule_item_item.day_of_week < 0 or schedule_item_item.day_of_week > 6:
                errors.append(f"课程表项 {index} 的课程表项 {j} 的星期几必须是0-6之间的整数")
            
            # 验证课程ID
            if not schedule_item_item.course_id or len(schedule_item_item.course_id.strip()) == 0:
                errors.append(f"课程表项 {index} 的课程表项 {j} 的课程ID不能为空")
