#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
课程表工具函数
提供周次计算、多周循环等功能
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any


class ScheduleWeekCalculator:
    """课程表周次计算器"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(f'{__name__}.ScheduleWeekCalculator')
    
    def get_current_week(self) -> int:
        """获取当前周次"""
        try:
            if not self.config_manager:
                return 1
            
            # 尝试从配置获取手动设置的当前周次
            manual_week = self.config_manager.get_config('schedule.current_week', 0, 'user')
            if manual_week > 0:
                return manual_week
            
            # 根据开学日期自动计算
            start_date_str = self.config_manager.get_config('schedule.start_date', '', 'user')
            if start_date_str:
                return self.calculate_week_from_date(start_date_str)
            
            return 1
            
        except Exception as e:
            self.logger.error(f"获取当前周次失败: {e}")
            return 1
    
    def calculate_week_from_date(self, start_date_str: str) -> int:
        """根据开学日期计算当前周次"""
        try:
            if not start_date_str:
                return 1
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            today = date.today()
            
            days_diff = (today - start_date).days
            if days_diff < 0:
                return 1
            
            # 计算周次（从第1周开始）
            week = (days_diff // 7) + 1
            
            # 限制在合理范围内
            max_weeks = 30
            if self.config_manager:
                max_weeks = self.config_manager.get_config('schedule.semester_weeks', 20, 'user')
            
            return min(week, max_weeks)
            
        except Exception as e:
            self.logger.error(f"根据日期计算周次失败: {e}")
            return 1
    
    def is_course_active_this_week(self, course_data: Dict[str, Any], week: Optional[int] = None) -> bool:
        """判断课程在指定周次是否有效"""
        try:
            if week is None:
                week = self.get_current_week()
            
            # 检查周次范围
            start_week = course_data.get('start_week', 1)
            end_week = course_data.get('end_week', 20)
            
            if not (start_week <= week <= end_week):
                return False
            
            # 检查周次类型
            week_type = course_data.get('week_type', 'all')
            
            if week_type == 'all':
                return True
            elif week_type == 'odd':
                return week % 2 == 1
            elif week_type == 'even':
                return week % 2 == 0
            
            return True
            
        except Exception as e:
            self.logger.error(f"判断课程有效性失败: {e}")
            return True
    
    def get_week_type_display(self, week_type: str) -> str:
        """获取周次类型的显示文本"""
        week_type_map = {
            'all': '全部周次',
            'odd': '单周',
            'even': '双周'
        }
        return week_type_map.get(week_type, '全部周次')
    
    def get_week_display(self, start_week: int, end_week: int, week_type: str = 'all') -> str:
        """获取周次的完整显示文本"""
        if start_week == end_week:
            week_text = f"第{start_week}周"
        else:
            week_text = f"第{start_week}-{end_week}周"
        
        if week_type == 'odd':
            week_text += "(单周)"
        elif week_type == 'even':
            week_text += "(双周)"
        
        return week_text
    
    def get_courses_for_week(self, schedule_data: Dict[str, Any], week: Optional[int] = None) -> Dict[str, Any]:
        """获取指定周次的课程数据"""
        try:
            if week is None:
                week = self.get_current_week()
            
            filtered_schedule = {}
            
            for day, day_courses in schedule_data.items():
                filtered_day_courses = {}
                
                for time_key, course in day_courses.items():
                    if self.is_course_active_this_week(course, week):
                        filtered_day_courses[time_key] = course
                
                if filtered_day_courses:
                    filtered_schedule[day] = filtered_day_courses
            
            return filtered_schedule
            
        except Exception as e:
            self.logger.error(f"获取周次课程失败: {e}")
            return schedule_data
    
    def validate_course_data(self, course_data: Dict[str, Any]) -> bool:
        """验证课程数据的有效性"""
        try:
            # 检查必需字段
            required_fields = ['name']
            for field in required_fields:
                if not course_data.get(field, '').strip():
                    return False
            
            # 检查周次范围
            start_week = course_data.get('start_week', 1)
            end_week = course_data.get('end_week', 20)
            
            if start_week < 1 or end_week < 1 or start_week > end_week:
                return False
            
            # 检查周次类型
            week_type = course_data.get('week_type', 'all')
            if week_type not in ['all', 'odd', 'even']:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证课程数据失败: {e}")
            return False


def get_schedule_calculator(config_manager=None) -> ScheduleWeekCalculator:
    """获取课程表计算器实例"""
    return ScheduleWeekCalculator(config_manager)


def format_course_display(course_data: Dict[str, Any], show_week_info: bool = True) -> str:
    """格式化课程显示文本"""
    try:
        course_name = course_data.get('name', '')
        classroom = course_data.get('classroom', '')
        
        if not show_week_info:
            return f"{course_name}\n{classroom}" if classroom else course_name
        
        # 添加周次信息
        start_week = course_data.get('start_week', 1)
        end_week = course_data.get('end_week', 20)
        week_type = course_data.get('week_type', 'all')
        
        calculator = ScheduleWeekCalculator()
        week_text = calculator.get_week_display(start_week, end_week, week_type)
        
        parts = [course_name]
        if classroom:
            parts.append(classroom)
        parts.append(week_text)
        
        return '\n'.join(parts)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"格式化课程显示失败: {e}")
        return course_data.get('name', '未知课程')


def get_week_color(week_type: str) -> tuple:
    """获取周次类型对应的颜色"""
    color_map = {
        'all': (240, 255, 240),    # 浅绿色
        'odd': (255, 240, 240),    # 浅红色
        'even': (240, 240, 255)    # 浅蓝色
    }
    return color_map.get(week_type, (240, 255, 240))
