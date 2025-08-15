"""
课程相关插件接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from plugins.plugin_interface import PluginInterface
from models.class_item import ClassItem


class CoursePluginInterface(PluginInterface, ABC):
    """课程相关插件接口"""
    
    @abstractmethod
    def add_course(self, course: ClassItem) -> bool:
        """
        添加课程
        
        Args:
            course: 课程对象
            
        Returns:
            bool: 是否添加成功
        """
        pass
    
    @abstractmethod
    def remove_course(self, course_id: str) -> bool:
        """
        删除课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def update_course(self, course_id: str, course: ClassItem) -> bool:
        """
        更新课程
        
        Args:
            course_id: 课程ID
            course: 新的课程对象
            
        Returns:
            bool: 是否更新成功
        """
        pass
    
    @abstractmethod
    def get_course(self, course_id: str) -> Optional[ClassItem]:
        """
        获取课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            Optional[ClassItem]: 课程对象或None
        """
        pass
    
    @abstractmethod
    def list_courses(self) -> List[ClassItem]:
        """
        列出所有课程
        
        Returns:
            List[ClassItem]: 课程列表
        """
        pass