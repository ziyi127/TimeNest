#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面前端应用
API客户端，用于与后端服务通信
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入服务工厂
from services.service_factory import ServiceFactory
from models.class_item import ClassItem, TimeSlot
from models.class_plan import ClassPlan
from models.temp_change import TempChange
from models.user_settings import UserSettings


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化API客户端
        
        Args:
            base_url: 后端服务的基础URL（此参数在新实现中不再使用）
        """
        # 获取服务实例
        self.course_service = ServiceFactory.get_course_service()
        self.schedule_service = ServiceFactory.get_schedule_service()
        self.temp_change_service = ServiceFactory.get_temp_change_service()
        self.user_service = ServiceFactory.get_user_service()
        
    def get_courses(self) -> List[Dict[str, Any]]:
        """
        获取所有课程
        
        Returns:
            课程列表
        """
        try:
            courses = self.course_service.get_all_courses()
            return [course.to_dict() for course in courses]
        except Exception as e:
            print(f"获取课程失败: {e}")
            return []
            
    def get_schedules(self) -> List[Dict[str, Any]]:
        """
        获取所有课程表项
        
        Returns:
            课程表项列表
        """
        try:
            schedules = self.schedule_service.get_all_schedules()
            return [schedule.to_dict() for schedule in schedules]
        except Exception as e:
            print(f"获取课程表项失败: {e}")
            return []
            
    def get_temp_changes(self) -> List[Dict[str, Any]]:
        """
        获取所有临时换课记录
        
        Returns:
            临时换课记录列表
        """
        try:
            temp_changes = self.temp_change_service.get_all_temp_changes()
            return [temp_change.to_dict() for temp_change in temp_changes]
        except Exception as e:
            print(f"获取临时换课记录失败: {e}")
            return []
            
    def get_settings(self) -> Dict[str, Any]:
        """
        获取应用设置
        
        Returns:
            应用设置字典
        """
        try:
            settings = self.user_service.get_user_settings()
            return settings.to_dict()
        except Exception as e:
            print(f"获取设置失败: {e}")
            # 返回默认设置
            return {
                "window_position": {
                    "x": 100,
                    "y": 100
                },
                "auto_hide_timeout": 5000,
                "update_interval": 1000,
                "floating_window": {
                    "hide_tray_menu": False,
                    "remember_position": True,
                    "auto_hide_threshold": 50,
                    "transparency": 80,
                    "snap_to_edge": False,
                    "snap_priority": "右侧 > 顶部 > 左侧",
                    "weather_display": "温度 + 天气描述",
                    "temp_course_style": "临时调课标红边框"
                }
            }
            
    def save_courses(self, courses: List[Dict[str, Any]]) -> bool:
        """
        保存课程数据
        
        Args:
            courses: 课程列表
            
        Returns:
            保存是否成功
        """
        try:
            # 先删除所有现有课程
            existing_courses = self.course_service.get_all_courses()
            for course in existing_courses:
                self.course_service.delete_course(course.id)
            
            # 创建新课程
            for course_data in courses:
                duration_data = course_data.get('duration', {})
                duration = TimeSlot(
                    start_time=duration_data.get('start_time'),
                    end_time=duration_data.get('end_time')
                )
                
                course = ClassItem(
                    id=course_data.get('id'),
                    name=course_data.get('name'),
                    teacher=course_data.get('teacher'),
                    location=course_data.get('location'),
                    duration=duration
                )
                
                self.course_service.create_course(course)
            
            return True
        except Exception as e:
            print(f"保存课程失败: {e}")
            return False
            
    def save_schedules(self, schedules: List[Dict[str, Any]]) -> bool:
        """
        保存课程表项数据
        
        Args:
            schedules: 课程表项列表
            
        Returns:
            保存是否成功
        """
        try:
            # 先删除所有现有课程表项
            existing_schedules = self.schedule_service.get_all_schedules()
            for schedule in existing_schedules:
                self.schedule_service.delete_schedule(schedule.id)
            
            # 创建新课程表项
            for schedule_data in schedules:
                schedule = ClassPlan(
                    id=schedule_data.get('id'),
                    day_of_week=schedule_data.get('day_of_week'),
                    week_parity=schedule_data.get('week_parity'),
                    course_id=schedule_data.get('course_id'),
                    valid_from=schedule_data.get('valid_from'),
                    valid_to=schedule_data.get('valid_to')
                )
                
                self.schedule_service.create_schedule(schedule)
            
            return True
        except Exception as e:
            print(f"保存课程表项失败: {e}")
            return False
            
    def save_temp_changes(self, temp_changes: List[Dict[str, Any]]) -> bool:
        """
        保存临时换课记录数据
        
        Args:
            temp_changes: 临时换课记录列表
            
        Returns:
            保存是否成功
        """
        try:
            # 先删除所有现有临时换课记录
            existing_temp_changes = self.temp_change_service.get_all_temp_changes()
            for temp_change in existing_temp_changes:
                self.temp_change_service.delete_temp_change(temp_change.id)
            
            # 创建新临时换课记录
            for temp_change_data in temp_changes:
                temp_change = TempChange(
                    id=temp_change_data.get('id'),
                    original_schedule_id=temp_change_data.get('original_schedule_id'),
                    new_course_id=temp_change_data.get('new_course_id'),
                    change_date=temp_change_data.get('change_date'),
                    is_permanent=temp_change_data.get('is_permanent', False),
                    used=temp_change_data.get('used', False)
                )
                
                self.temp_change_service.create_temp_change(temp_change)
            
            return True
        except Exception as e:
            print(f"保存临时换课记录失败: {e}")
            return False
            
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        保存应用设置数据
        
        Args:
            settings: 应用设置字典
            
        Returns:
            保存是否成功
        """
        try:
            # 创建用户设置对象
            user_settings = UserSettings(
                theme=settings.get('theme', 'light'),
                language=settings.get('language', 'zh-CN'),
                auto_backup=settings.get('auto_backup', True),
                backup_interval=settings.get('backup_interval', 24),
                data_dir=settings.get('data_dir', './data')
            )
            
            # 更新用户设置
            self.user_service.update_user_settings(user_settings)
            
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False
            
    def get_today_schedule(self) -> Dict[str, Any]:
        """
        获取今天的课程安排
        
        Returns:
            今天的课程安排信息
        """
        try:
            # 导入需要的服务
            from datetime import datetime
            from services.service_factory import ServiceFactory
            
            # 获取服务实例
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            temp_change_service = ServiceFactory.get_temp_change_service()
            
            # 获取今天的日期
            today = datetime.now().date()
            today_str = today.strftime("%Y-%m-%d")
            
            # 获取今天的临时换课
            temp_changes = temp_change_service.get_temp_changes_by_date(today_str)
            
            # 检查是否有未使用的临时换课
            for temp_change in temp_changes:
                if not temp_change.used:
                    # 获取新课程
                    course = course_service.get_course_by_id(temp_change.new_course_id)
                    if course:
                        return {
                            "type": "temp",
                            "course": course.to_dict()
                        }
            
            # 获取今天的课程表项
            schedules = schedule_service.get_schedules_by_date(today_str)
            
            # 如果有课程表项，返回第一个
            if schedules:
                schedule = schedules[0]
                course = course_service.get_course_by_id(schedule.course_id)
                if course:
                    return {
                        "type": "regular",
                        "course": course.to_dict()
                    }
            
            # 没有课程
            return {"type": "none"}
        except Exception as e:
            print(f"获取今日课程安排失败: {e}")
            return {"type": "none"}
            
    def get_weather_data(self) -> Dict[str, Any] | None:
        """
        获取天气数据
        
        Returns:
            天气数据字典或None
        """
        try:
            # 获取天气服务实例
            from services.service_factory import ServiceFactory
            weather_service = ServiceFactory.get_weather_service()
            
            # 获取当前天气数据
            weather_data = weather_service.get_current_weather()
            
            if weather_data:
                # 转换为字典格式
                weather_dict = {
                    "location": weather_data.location,
                    "temperature": weather_data.temperature,
                    "humidity": weather_data.humidity,
                    "pressure": weather_data.pressure,
                    "wind_speed": weather_data.wind_speed,
                    "weather_condition": weather_data.weather_condition,
                    "forecast": weather_data.forecast,
                    "last_updated": weather_data.last_updated.isoformat() if weather_data.last_updated else None
                }
                
                return weather_dict
            else:
                return None
        except Exception as e:
            print(f"获取天气数据时发生错误: {str(e)}")
            return None