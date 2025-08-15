"""
时间表相关插件接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from plugins.plugin_interface import PluginInterface
from models.class_plan import ClassPlan


class SchedulePluginInterface(PluginInterface, ABC):
    """时间表相关插件接口"""
    
    @abstractmethod
    def add_schedule(self, schedule: ClassPlan) -> bool:
        """
        添加时间表项
        
        Args:
            schedule: 时间表项对象
            
        Returns:
            bool: 是否添加成功
        """
        pass
    
    @abstractmethod
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        删除时间表项
        
        Args:
            schedule_id: 时间表项ID
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def update_schedule(self, schedule_id: str, schedule: ClassPlan) -> bool:
        """
        更新时间表项
        
        Args:
            schedule_id: 时间表项ID
            schedule: 新的时间表项对象
            
        Returns:
            bool: 是否更新成功
        """
        pass
    
    @abstractmethod
    def get_schedule(self, schedule_id: str) -> Optional[ClassPlan]:
        """
        获取时间表项
        
        Args:
            schedule_id: 时间表项ID
            
        Returns:
            Optional[ClassPlan]: 时间表项对象或None
        """
        pass
    
    @abstractmethod
    def list_schedules(self) -> List[ClassPlan]:
        """
        列出所有时间表项
        
        Returns:
            List[ClassPlan]: 时间表项列表
        """
        pass