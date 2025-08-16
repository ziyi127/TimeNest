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
        
        # 执行创建临时换课的步骤
        self._execute_create_temp_change_steps(temp_change)
        
        logger.info(f"Temp change {temp_change.id} created successfully")
        return temp_change
    
    def _execute_create_temp_change_steps(self, temp_change: TempChange) -> None:
        """
        执行创建临时换课的步骤
        
        Args:
            temp_change: 临时换课对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 临时换课冲突
        """
        # 验证临时换课数据
        self._validate_temp_change_data(temp_change)
        
        # 检查临时换课ID是否已存在
        self._ensure_temp_change_id_unique(temp_change.id)
        
        # 添加临时换课
        self._add_temp_change(temp_change)
    
    def _validate_temp_change_data(self, temp_change: TempChange) -> None:
        """
        验证临时换课数据
        
        Args:
            temp_change: 临时换课对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        is_valid, errors = self._validate_temp_change(temp_change)
        if not is_valid:
            logger.warning(f"Temp change validation failed: {errors}")
            raise ValidationException("临时换课数据验证失败", errors)
    
    def _ensure_temp_change_id_unique(self, temp_change_id: str) -> None:
        """
        确保临时换课ID唯一
        
        Args:
            temp_change_id: 临时换课ID
            
        Raises:
            ConflictException: 临时换课ID已存在
        """
        if self.get_temp_change_by_id(temp_change_id):
            logger.warning(f"Temp change with id {temp_change_id} already exists")
            raise ConflictException(f"临时换课ID {temp_change_id} 已存在")
    
    def _add_temp_change(self, temp_change: TempChange) -> None:
        """
        添加临时换课到列表
        
        Args:
            temp_change: 临时换课对象
        """
        self.temp_changes.append(temp_change)
    
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
        
        # 执行更新临时换课的步骤
        self._execute_update_temp_change_steps(temp_change_id, updated_temp_change)
        
        logger.info(f"Temp change {temp_change_id} updated successfully")
        return updated_temp_change
    
    def _execute_update_temp_change_steps(self, temp_change_id: str, updated_temp_change: TempChange) -> None:
        """
        执行更新临时换课的步骤
        
        Args:
            temp_change_id: 临时换课ID
            updated_temp_change: 更新的临时换课对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 临时换课未找到
        """
        # 验证临时换课数据
        self._validate_temp_change_data(updated_temp_change)
        
        # 查找要更新的临时换课
        temp_change_index = self._find_temp_change_index(temp_change_id)
        self._ensure_temp_change_exists(temp_change_id, temp_change_index)
        
        # 更新临时换课
        self._update_temp_change_at_index(temp_change_index, updated_temp_change)
    
    def _ensure_temp_change_exists(self, temp_change_id: str, temp_change_index: int) -> None:
        """
        确保临时换课存在
        
        Args:
            temp_change_id: 临时换课ID
            temp_change_index: 临时换课索引
            
        Raises:
            NotFoundException: 临时换课未找到
        """
        if temp_change_index == -1:
            logger.warning(f"Temp change {temp_change_id} not found")
            raise NotFoundException(f"临时换课 {temp_change_id} 未找到")
    
    def _update_temp_change_at_index(self, index: int, temp_change: TempChange) -> None:
        """
        在指定索引处更新临时换课
        
        Args:
            index: 临时换课索引
            temp_change: 新的临时换课对象
        """
        self.temp_changes[index] = temp_change
    
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
        
        # 执行删除临时换课的步骤
        self._execute_delete_temp_change_steps(temp_change_id)
        
        logger.info(f"Temp change {temp_change_id} deleted successfully")
        return True
    
    def _execute_delete_temp_change_steps(self, temp_change_id: str) -> None:
        """
        执行删除临时换课的步骤
        
        Args:
            temp_change_id: 临时换课ID
            
        Raises:
            NotFoundException: 临时换课未找到
        """
        # 查找要删除的临时换课
        temp_change_index = self._find_temp_change_index(temp_change_id)
        self._ensure_temp_change_exists(temp_change_id, temp_change_index)
        
        # 删除临时换课
        self._remove_temp_change_at_index(temp_change_index)
    
    def _remove_temp_change_at_index(self, index: int) -> None:
        """
        删除指定索引处的临时换课
        
        Args:
            index: 临时换课索引
        """
        del self.temp_changes[index]
    
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
        
        result = self._filter_temp_changes_by_date(date_str)
        
        logger.debug(f"Found {len(result)} temp changes for date {date_str}")
        return result
    
    def _filter_temp_changes_by_date(self, date_str: str) -> List[TempChange]:
        """
        根据日期过滤临时换课
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            指定日期的临时换课列表
        """
        return [
            temp_change for temp_change in self.temp_changes
            if self._is_temp_change_on_date(temp_change, date_str)
        ]
    
    def _is_temp_change_on_date(self, temp_change: TempChange, date_str: str) -> bool:
        """
        检查临时换课是否在指定日期
        
        Args:
            temp_change: 临时换课对象
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            临时换课是否在指定日期
        """
        return temp_change.change_date == date_str
    
    def get_temp_changes_by_schedule(self, schedule_id: str) -> List[TempChange]:
        """
        根据原课程表ID获取临时换课
        
        Args:
            schedule_id: 原课程表ID
            
        Returns:
            指定课程表的临时换课列表
        """
        logger.debug(f"Getting temp changes by schedule: {schedule_id}")
        
        result = self._filter_temp_changes_by_schedule(schedule_id)
        
        logger.debug(f"Found {len(result)} temp changes for schedule {schedule_id}")
        return result
    
    def _filter_temp_changes_by_schedule(self, schedule_id: str) -> List[TempChange]:
        """
        根据原课程表ID过滤临时换课
        
        Args:
            schedule_id: 原课程表ID
            
        Returns:
            指定课程表的临时换课列表
        """
        return [
            temp_change for temp_change in self.temp_changes
            if self._is_temp_change_for_schedule(temp_change, schedule_id)
        ]
    
    def _is_temp_change_for_schedule(self, temp_change: TempChange, schedule_id: str) -> bool:
        """
        检查临时换课是否属于指定课程表
        
        Args:
            temp_change: 临时换课对象
            schedule_id: 原课程表ID
            
        Returns:
            临时换课是否属于指定课程表
        """
        return temp_change.original_schedule_id == schedule_id
    
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
        
        # 执行标记临时换课为已使用的步骤
        return self._execute_mark_temp_change_as_used_steps(temp_change_id)
    
    def _execute_mark_temp_change_as_used_steps(self, temp_change_id: str) -> TempChange:
        """
        执行标记临时换课为已使用的步骤
        
        Args:
            temp_change_id: 临时换课ID
            
        Returns:
            更新后的临时换课对象
            
        Raises:
            NotFoundException: 临时换课未找到
        """
        # 查找并验证临时换课
        temp_change_index = self._find_temp_change_index(temp_change_id)
        self._ensure_temp_change_exists(temp_change_id, temp_change_index)
        
        # 标记为已使用并返回
        return self._mark_temp_change_used_at_index(temp_change_index)
    
    def _mark_temp_change_used_at_index(self, index: int) -> TempChange:
        """
        标记指定索引处的临时换课为已使用
        
        Args:
            index: 临时换课索引
            
        Returns:
            更新后的临时换课对象
        """
        self.temp_changes[index].used = True
        logger.info(f"Temp change {self.temp_changes[index].id} marked as used")
        return self.temp_changes[index]
    
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
        
        # 验证各个字段
        self._validate_temp_change_fields(temp_change, errors)
        
        return len(errors) == 0, errors
    
    def _validate_temp_change_fields(self, temp_change: TempChange, errors: List[str]) -> None:
        """
        验证临时换课的各个字段
        
        Args:
            temp_change: 临时换课对象
            errors: 错误信息列表
        """
        errors.extend(self._validate_temp_change_id(temp_change.id))
        errors.extend(self._validate_schedule_id(temp_change.original_schedule_id))
        errors.extend(self._validate_new_course_id(temp_change.new_course_id))
        errors.extend(self._validate_change_date_format(temp_change.change_date))
    
    def _validate_temp_change_id(self, temp_change_id: str) -> List[str]:
        """
        验证临时换课ID
        
        Args:
            temp_change_id: 临时换课ID
            
        Returns:
            错误信息列表
        """
        errors = []
        if not temp_change_id or not isinstance(temp_change_id, str) or len(temp_change_id.strip()) == 0:
            errors.append("临时换课ID不能为空")
        return errors
    
    def _validate_schedule_id(self, schedule_id: str) -> List[str]:
        """
        验证原课程表ID
        
        Args:
            schedule_id: 原课程表ID
            
        Returns:
            错误信息列表
        """
        errors = []
        if not schedule_id or not isinstance(schedule_id, str) or len(schedule_id.strip()) == 0:
            errors.append("原课程表ID不能为空")
        return errors
    
    def _validate_new_course_id(self, new_course_id: str) -> List[str]:
        """
        验证新课程ID
        
        Args:
            new_course_id: 新课程ID
            
        Returns:
            错误信息列表
        """
        errors = []
        if not new_course_id or not isinstance(new_course_id, str) or len(new_course_id.strip()) == 0:
            errors.append("新课程ID不能为空")
        return errors
    
    def _validate_change_date(self, change_date: str) -> List[str]:
        """
        验证换课日期格式
        
        Args:
            change_date: 换课日期字符串
            
        Returns:
            错误信息列表
        """
        errors = []
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, change_date):
            errors.append(f"换课日期格式不正确: {change_date}")
        return errors