"""
服务工厂类
用于统一管理所有服务的创建和访问
"""

from typing import Dict, Type
from services.course_service import CourseService
from services.schedule_service import ScheduleService
from services.temp_change_service import TempChangeService
from services.cycle_schedule_service import CycleScheduleService


class ServiceFactory:
    """服务工厂类"""
    
    _services: Dict[str, object] = {}
    
    @classmethod
    def get_service(cls, service_type: str):
        """
        获取指定类型的服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
        """
        if service_type not in cls._services:
            cls._services[service_type] = cls._create_service(service_type)
        return cls._services[service_type]
    
    @classmethod
    def _create_service(cls, service_type: str):
        """
        创建指定类型的服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
            
        Raises:
            ValueError: 不支持的服务类型
        """
        service_map: Dict[str, Type] = {
            "course": CourseService,
            "schedule": ScheduleService,
            "temp_change": TempChangeService,
            "cycle_schedule": CycleScheduleService
        }
        
        if service_type not in service_map:
            raise ValueError(f"不支持的服务类型: {service_type}")
        
        return service_map[service_type]()
    
    @classmethod
    def get_course_service(cls) -> CourseService:
        """
        获取课程服务实例
        
        Returns:
            课程服务实例
        """
        return cls.get_service("course")
    
    @classmethod
    def get_schedule_service(cls) -> ScheduleService:
        """
        获取课程表服务实例
        
        Returns:
            课程表服务实例
        """
        return cls.get_service("schedule")
    
    @classmethod
    def get_temp_change_service(cls) -> TempChangeService:
        """
        获取临时换课服务实例
        
        Returns:
            临时换课服务实例
        """
        return cls.get_service("temp_change")
    
    @classmethod
    def get_cycle_schedule_service(cls) -> CycleScheduleService:
        """
        获取循环课程表服务实例
        
        Returns:
            循环课程表服务实例
        """
        return cls.get_service("cycle_schedule")