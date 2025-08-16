"""
服务工厂类
用于统一管理所有服务的创建和访问
"""

from typing import Dict, Type, Any
from services.course_service import CourseService
from services.schedule_service import ScheduleService
from services.temp_change_service import TempChangeService
from services.cycle_schedule_service import CycleScheduleService

# 新增的服务导入
from services.user_service import UserService
from services.notification_service import NotificationService
from services.statistics_service import StatisticsService
from services.data_service import DataService
from services.backup_service import BackupService
from services.conflict_detection_service import ConflictDetectionService
from services.reminder_service import ReminderService
from services.sync_service import SyncService
from services.config_service import ConfigService

# 新增的功能模块服务导入
from services.weather_service import WeatherService
from services.countdown_service import CountdownService
from services.course_alias_service import CourseAliasService
from services.task_scheduler_service import TaskSchedulerService
from services.startup_service import StartupService
from services.debug_service import DebugService
from services.time_sync_service import TimeSyncService


class ServiceFactory:
    """服务工厂类"""
    
    _services: Dict[str, Any] = {}
    
    @classmethod
    def get_service(cls, service_type: str) -> Any:
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
    def _create_service(cls, service_type: str) -> Any:
        """
        创建指定类型的服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
            
        Raises:
            ValueError: 不支持的服务类型
        """
        service_map = cls._get_service_map()
        
        if service_type not in service_map:
            raise ValueError(f"不支持的服务类型: {service_type}")
        
        return service_map[service_type]()
    
    @classmethod
    def _get_service_map(cls) -> Dict[str, Type[Any]]:
        """
        获取服务映射表
        
        Returns:
            Dict[str, Type]: 服务类型到服务类的映射字典
        """
        return {
            "course": CourseService,
            "schedule": ScheduleService,
            "temp_change": TempChangeService,
            "cycle_schedule": CycleScheduleService,
            # 新增的服务映射
            "user": UserService,
            "notification": NotificationService,
            "statistics": StatisticsService,
            "data": DataService,
            "backup": BackupService,
            "conflict_detection": ConflictDetectionService,
            "reminder": ReminderService,
            "sync": SyncService,
            "config": ConfigService,
            # 新增的功能模块服务映射
            "weather": WeatherService,
            "countdown": CountdownService,
            "course_alias": CourseAliasService,
            "task_scheduler": TaskSchedulerService,
            "startup": StartupService,
            "debug": DebugService,
            "time_sync": TimeSyncService
        }
    
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
    
    # 新增的服务获取方法
    @classmethod
    def get_user_service(cls) -> UserService:
        """
        获取用户服务实例
        
        Returns:
            用户服务实例
        """
        return cls.get_service("user")
    
    @classmethod
    def get_notification_service(cls) -> NotificationService:
        """
        获取通知服务实例
        
        Returns:
            通知服务实例
        """
        return cls.get_service("notification")
    
    @classmethod
    def get_statistics_service(cls) -> StatisticsService:
        """
        获取统计服务实例
        
        Returns:
            统计服务实例
        """
        return cls.get_service("statistics")
    
    @classmethod
    def get_data_service(cls) -> DataService:
        """
        获取数据服务实例
        
        Returns:
            数据服务实例
        """
        return cls.get_service("data")
    
    @classmethod
    def get_backup_service(cls) -> BackupService:
        """
        获取备份服务实例
        
        Returns:
            备份服务实例
        """
        return cls.get_service("backup")
    
    @classmethod
    def get_conflict_detection_service(cls) -> ConflictDetectionService:
        """
        获取冲突检测服务实例
        
        Returns:
            冲突检测服务实例
        """
        return cls.get_service("conflict_detection")
    
    @classmethod
    def get_reminder_service(cls) -> ReminderService:
        """
        获取提醒服务实例
        
        Returns:
            提醒服务实例
        """
        return cls.get_service("reminder")
    
    @classmethod
    def get_sync_service(cls) -> SyncService:
        """
        获取同步服务实例
        
        Returns:
            同步服务实例
        """
        return cls.get_service("sync")
    
    @classmethod
    def get_config_service(cls) -> ConfigService:
        """
        获取配置服务实例
        
        Returns:
            配置服务实例
        """
        return cls.get_service("config")
    
    # 新增的功能模块服务获取方法
    @classmethod
    def get_weather_service(cls) -> WeatherService:
        """
        获取天气服务实例
        
        Returns:
            天气服务实例
        """
        return cls.get_service("weather")
    
    @classmethod
    def get_countdown_service(cls) -> CountdownService:
        """
        获取倒计时服务实例
        
        Returns:
            倒计时服务实例
        """
        return cls.get_service("countdown")
    
    @classmethod
    def get_course_alias_service(cls) -> CourseAliasService:
        """
        获取课程简称服务实例
        
        Returns:
            课程简称服务实例
        """
        return cls.get_service("course_alias")
    
    @classmethod
    def get_task_scheduler_service(cls) -> TaskSchedulerService:
        """
        获取任务调度服务实例
        
        Returns:
            任务调度服务实例
        """
        return cls.get_service("task_scheduler")
    
    @classmethod
    def get_startup_service(cls) -> StartupService:
        """
        获取开机启动服务实例
        
        Returns:
            开机启动服务实例
        """
        return cls.get_service("startup")
    
    @classmethod
    def get_debug_service(cls) -> DebugService:
        """
        获取调试服务实例
        
        Returns:
            调试服务实例
        """
        return cls.get_service("debug")
    
    @classmethod
    def get_time_sync_service(cls) -> TimeSyncService:
        """
        获取时间同步服务实例
        
        Returns:
            时间同步服务实例
        """
        return cls.get_service("time_sync")
