"""
临时换课服务
提供临时换课相关的业务逻辑处理
"""

from typing import List, Optional
from models.temp_change import TempChange
from models.class_plan import ClassPlan
from utils.logger import get_service_logger
from utils.exceptions import ValidationException, NotFoundException, ConflictException

# 初始化日志记录器
logger = get_service_logger("temp_change_service")


class TempChangeService:
    """临时换课服务类"""
    
    def __init__(self):
        """初始化临时换课服务"""
        self.temp_changes: List[TempChange] = []
        logger.info("TempChangeService initialized")
    
    def create_temp_change(self, temp_change: TempChange) -> TempChange:
        """
        创建临时换课
        
        Args:
            temp_change: 临时换课对象
            
        Returns:
            创建的临时换课对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 临时换课冲突
        """
        logger.info(f"Creating temp change: {temp_change.id}")
        
        # 验证临时换课数据
        is_valid, errors = self._validate_temp_change(temp_change)
        if not is_valid:
            logger.warning(f"Temp change validation failed: {errors}")
            raise ValidationException("临时换课数据验证失败", errors)
        
        # 检查临时换课ID是否已存在
        if self.get_temp_change_by_id(temp_change.id):
            logger.warning(f"Temp change with id {temp_change.id} already exists")
            raise ConflictException(f"临时换课ID {temp_change.id} 已存在")
        
        # 添加临时换课
        self.temp_changes.append(temp_change)
        logger.info(f"Temp change {temp_change.id} created successfully")
        return temp_change
    
    def update_temp_change(self, temp_change_id: str, updated_temp_change: TempChange) -> TempChange:
        """
        更新临时换课
        
        Args:
            temp_change_id: 临时换课ID
            updated_temp_change: 更新的临时换课对象
            
        Returns:
            更新后的临时换课对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 临时换课未找到
        """
        logger.info(f"Updating temp change: {temp_change_id}")
        
        # 验证临时换课数据
        is_valid, errors = self._validate_temp_change(updated_temp_change)
        if not is_valid:
            logger.warning(f"Temp change validation failed: {errors}")
            raise ValidationException("临时换课数据验证失败", errors)
        
        # 查找要更新的临时换课
        temp_change_index = self._find_temp_change_index(temp_change_id)
        if temp_change_index == -1:
            logger.warning(f"Temp change {temp_change_id} not found")
            raise NotFoundException(f"临时换课 {temp_change_id} 未找到")
        
        # 更新临时换课
        self.temp_changes[temp_change_index] = updated_temp_change
        logger.info(f"Temp change {temp_change_id} updated successfully")
        return updated_temp_change
    
    def delete_temp_change(self, temp_change_id: str) -> bool:
        """
        删除临时换课
        
        Args:
            temp_change_id: 临时换课ID
            
        Returns:
            是否删除成功
            
        Raises:
            NotFoundException: 临时换课未找到
        """
        logger.info(f"Deleting temp change: {temp_change_id}")
        
        # 查找要删除的临时换课
        temp_change_index = self._find_temp_change_index(temp_change_id)
        if temp_change_index == -1:
            logger.warning(f"Temp change {temp_change_id} not found")
            raise NotFoundException(f"临时换课 {temp_change_id} 未找到")
        
        # 删除临时换课
        del self.temp_changes[temp_change_index]
        logger.info(f"Temp change {temp_change_id} deleted successfully")
        return True
    
    def get_temp_change_by_id(self, temp_change_id: str) -> Optional[TempChange]:
        """
        根据ID获取临时换课
        
        Args:
            temp_change_id: 临时换课ID
            
        Returns:
            临时换课对象，如果未找到则返回None
        """
        logger.debug(f"Getting temp change by id: {temp_change_id}")
        
        for temp_change in self.temp_changes:
            if temp_change.id == temp_change_id:
                logger.debug(f"Temp change {temp_change_id} found")
                return temp_change
        
        logger.debug(f"Temp change {temp_change_id} not found")
        return None
    
    def get_all_temp_changes(self) -> List[TempChange]:
        """
        获取所有临时换课
        
        Returns:
            临时换课列表
        """
        logger.debug("Getting all temp changes")
        return self.temp_changes.copy()
    
    def get_temp_changes_by_date(self, date_str: str) -> List[TempChange]:
        """
        根据日期获取临时换课
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            指定日期的临时换课列表
        """
        logger.debug(f"Getting temp changes by date: {date_str}")
        
        result = []
        for temp_change in self.temp_changes:
            if temp_change.change_date == date_str:
                result.append(temp_change)
        
        logger.debug(f"Found {len(result)} temp changes for date {date_str}")
        return result
    
    def get_temp_changes_by_schedule(self, schedule_id: str) -> List[TempChange]:
        """
        根据原课程表ID获取临时换课
        
        Args:
            schedule_id: 原课程表ID
            
        Returns:
            指定课程表的临时换课列表
        """
        logger.debug(f"Getting temp changes by schedule: {schedule_id}")
        
        result = []
        for temp_change in self.temp_changes:
            if temp_change.original_schedule_id == schedule_id:
                result.append(temp_change)
        
        logger.debug(f"Found {len(result)} temp changes for schedule {schedule_id}")
        return result
    
    def mark_temp_change_as_used(self, temp_change_id: str) -> TempChange:
        """
        标记临时换课为已使用
        
        Args:
            temp_change_id: 临时换课ID
            
        Returns:
            更新后的临时换课对象
            
        Raises:
            NotFoundException: 临时换课未找到
        """
        logger.info(f"Marking temp change as used: {temp_change_id}")
        
        # 查找临时换课
        temp_change_index = self._find_temp_change_index(temp_change_id)
        if temp_change_index == -1:
            logger.warning(f"Temp change {temp_change_id} not found")
            raise NotFoundException(f"临时换课 {temp_change_id} 未找到")
        
        # 标记为已使用
        self.temp_changes[temp_change_index].used = True
        logger.info(f"Temp change {temp_change_id} marked as used")
        return self.temp_changes[temp_change_index]
    
    def _find_temp_change_index(self, temp_change_id: str) -> int:
        """
        查找临时换课在列表中的索引
        
        Args:
            temp_change_id: 临时换课ID
            
        Returns:
            临时换课索引，如果未找到则返回-1
        """
        for i, temp_change in enumerate(self.temp_changes):
            if temp_change.id == temp_change_id:
                return i
        return -1
    
    def _validate_temp_change(self, temp_change: TempChange) -> tuple[bool, List[str]]:
        """
        验证临时换课数据
        
        Args:
            temp_change: 临时换课对象
            
        Returns:
            (is_valid, errors): 是否有效和错误信息列表
        """
        errors = []
        
        # 验证ID
        if not temp_change.id or not isinstance(temp_change.id, str) or len(temp_change.id.strip()) == 0:
            errors.append("临时换课ID不能为空")
        
        # 验证原课程表ID
        if not temp_change.original_schedule_id or not isinstance(temp_change.original_schedule_id, str) or len(temp_change.original_schedule_id.strip()) == 0:
            errors.append("原课程表ID不能为空")
        
        # 验证新课程ID
        if not temp_change.new_course_id or not isinstance(temp_change.new_course_id, str) or len(temp_change.new_course_id.strip()) == 0:
            errors.append("新课程ID不能为空")
        
        # 验证换课日期格式
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, temp_change.change_date):
            errors.append(f"换课日期格式不正确: {temp_change.change_date}")
        
        return len(errors) == 0, errors