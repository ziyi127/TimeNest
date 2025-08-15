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
        
        # 验证循环课程表数据
        is_valid, errors = self._validate_cycle_schedule(cycle_schedule)
        if not is_valid:
            logger.warning(f"Cycle schedule validation failed: {errors}")
            raise ValidationException("循环课程表数据验证失败", errors)
        
        # 检查循环课程表ID是否已存在
        if self.get_cycle_schedule_by_id(cycle_schedule.id):
            logger.warning(f"Cycle schedule with id {cycle_schedule.id} already exists")
            raise ConflictException(f"循环课程表ID {cycle_schedule.id} 已存在")
        
        # 添加循环课程表
        self.cycle_schedules.append(cycle_schedule)
        logger.info(f"Cycle schedule {cycle_schedule.id} created successfully")
        return cycle_schedule
    
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
        
        # 验证循环课程表数据
        is_valid, errors = self._validate_cycle_schedule(updated_cycle_schedule)
        if not is_valid:
            logger.warning(f"Cycle schedule validation failed: {errors}")
            raise ValidationException("循环课程表数据验证失败", errors)
        
        # 查找要更新的循环课程表
        cycle_schedule_index = self._find_cycle_schedule_index(cycle_schedule_id)
        if cycle_schedule_index == -1:
            logger.warning(f"Cycle schedule {cycle_schedule_id} not found")
            raise NotFoundException(f"循环课程表 {cycle_schedule_id} 未找到")
        
        # 更新循环课程表
        self.cycle_schedules[cycle_schedule_index] = updated_cycle_schedule
        logger.info(f"Cycle schedule {cycle_schedule_id} updated successfully")
        return updated_cycle_schedule
    
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
        
        # 查找要删除的循环课程表
        cycle_schedule_index = self._find_cycle_schedule_index(cycle_schedule_id)
        if cycle_schedule_index == -1:
            logger.warning(f"Cycle schedule {cycle_schedule_id} not found")
            raise NotFoundException(f"循环课程表 {cycle_schedule_id} 未找到")
        
        # 删除循环课程表
        del self.cycle_schedules[cycle_schedule_index]
        logger.info(f"Cycle schedule {cycle_schedule_id} deleted successfully")
        return True
    
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
        
        # 查找循环课程表
        cycle_schedule = self.get_cycle_schedule_by_id(cycle_schedule_id)
        if not cycle_schedule:
            logger.warning(f"Cycle schedule {cycle_schedule_id} not found")
            raise NotFoundException(f"循环课程表 {cycle_schedule_id} 未找到")
        
        # 计算循环中的周索引
        week_index = get_cycle_week_index(date_str, start_date_str, cycle_schedule.cycle_length)
        
        # 查找对应周的课程表项
        for schedule_item in cycle_schedule.schedules:
            if schedule_item.week_index == week_index:
                logger.debug(f"Found schedule items for week index {week_index}")
                return schedule_item.schedule_items
        
        logger.debug(f"No schedule items found for week index {week_index}")
        return []
    
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
        errors = []
        
        # 验证ID
        if not cycle_schedule.id or not isinstance(cycle_schedule.id, str) or len(cycle_schedule.id.strip()) == 0:
            errors.append("循环课程表ID不能为空")
        
        # 验证名称
        if not cycle_schedule.name or not isinstance(cycle_schedule.name, str) or len(cycle_schedule.name.strip()) == 0:
            errors.append("循环课程表名称不能为空")
        
        # 验证循环长度
        if not isinstance(cycle_schedule.cycle_length, int) or cycle_schedule.cycle_length <= 0:
            errors.append("循环长度必须是正整数")
        
        # 验证课程表项
        if not isinstance(cycle_schedule.schedules, list):
            errors.append("课程表项必须是列表")
        else:
            for i, schedule_item in enumerate(cycle_schedule.schedules):
                if not isinstance(schedule_item, CycleScheduleItem):
                    errors.append(f"课程表项 {i} 类型不正确")
                    continue
                
                # 验证周索引
                if not isinstance(schedule_item.week_index, int) or schedule_item.week_index < 0:
                    errors.append(f"课程表项 {i} 的周索引必须是非负整数")
                
                # 验证课程表项列表
                if not isinstance(schedule_item.schedule_items, list):
                    errors.append(f"课程表项 {i} 的课程表项列表必须是列表")
                else:
                    for j, schedule_item_item in enumerate(schedule_item.schedule_items):
                        if not isinstance(schedule_item_item, ScheduleItem):
                            errors.append(f"课程表项 {i} 的课程表项 {j} 类型不正确")
                            continue
                        
                        # 验证星期几
                        if not isinstance(schedule_item_item.day_of_week, int) or schedule_item_item.day_of_week < 0 or schedule_item_item.day_of_week > 6:
                            errors.append(f"课程表项 {i} 的课程表项 {j} 的星期几必须是0-6之间的整数")
                        
                        # 验证课程ID
                        if not schedule_item_item.course_id or not isinstance(schedule_item_item.course_id, str) or len(schedule_item_item.course_id.strip()) == 0:
                            errors.append(f"课程表项 {i} 的课程表项 {j} 的课程ID不能为空")
        
        return len(errors) == 0, errors