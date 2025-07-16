#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data processing utilities for TimeNest
Handles common data transformation and validation tasks
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

def safe_json_load(file_path: Union[str, Path], default: Any = None) -> Any:
    """Safely load JSON file with fallback"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {file_path}")
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default

def safe_json_save(data: Any, file_path: Union[str, Path], 
                  create_backup: bool = True) -> bool:
    """Safely save data to JSON file"""
    try:
        file_path = Path(file_path)
        
        if create_backup and file_path.exists():
            backup_path = file_path.with_suffix(f'.backup{file_path.suffix}')
            file_path.rename(backup_path)
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
        
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False

def json_serializer(obj: Any) -> str:
    """Custom JSON serializer for datetime and other objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Path):
        return str(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)

def convert_courses_to_qml_format(courses: List[Dict]) -> List[Dict]:
    """Convert course data to QML-compatible format"""
    if not courses:
        return []
    
    return [
        {
            'id': str(course.get('id', 0)),
            'course_id': str(course.get('id', 0)),
            'name': course.get('name') or '',
            'teacher': course.get('teacher') or '',
            'location': course.get('location') or '',
            'time': course.get('time') or '',
            'start_week': course.get('start_week', 1),
            'end_week': course.get('end_week', 16),
            'weeks': f"{course.get('start_week', 1)}-{course.get('end_week', 16)}周",
            'day_of_week': course.get('day_of_week', 1),
            'start_time': course.get('start_time') or '08:00',
            'end_time': course.get('end_time') or '09:40'
        }
        for course in courses
    ]

def convert_tasks_to_qml_format(tasks: List[Dict]) -> List[Dict]:
    """Convert task data to QML-compatible format"""
    if not tasks:
        return []
    
    return [
        {
            'id': str(task.get('id', 0)),
            'task_id': str(task.get('id', 0)),
            'title': task.get('title') or '',
            'description': task.get('description') or '',
            'priority': task.get('priority') or '中',
            'status': task.get('status', '进行中'),
            'due_date': task.get('due_date') or '',
            'created_date': task.get('created_date') or '',
            'completed': task.get('status', '进行中') == '已完成'
        }
        for task in tasks
    ]

def validate_course_data(course: Dict) -> bool:
    """Validate course data structure"""
    required_fields = ['name', 'teacher', 'location', 'time']
    
    for field in required_fields:
        if not course.get(field):
            logger.warning(f"Missing required field '{field}' in course data")
            return False
    
    if not isinstance(course.get('start_week', 1), int):
        logger.warning("start_week must be an integer")
        return False
    
    if not isinstance(course.get('end_week', 16), int):
        logger.warning("end_week must be an integer")
        return False
    
    return True

def validate_task_data(task: Dict) -> bool:
    """Validate task data structure"""
    required_fields = ['title']
    
    for field in required_fields:
        if not task.get(field):
            logger.warning(f"Missing required field '{field}' in task data")
            return False
    
    valid_priorities = ['低', '中', '高']
    if task.get('priority') not in valid_priorities:
        logger.warning(f"Invalid priority: {task.get('priority')}")
        return False
    
    valid_statuses = ['进行中', '已完成', '已取消']
    if task.get('status') not in valid_statuses:
        logger.warning(f"Invalid status: {task.get('status')}")
        return False
    
    return True

def normalize_weekday(weekday: str) -> str:
    """Normalize weekday string to standard format"""
    weekday_map = {
        '周一': '周一', '星期一': '周一', 'Monday': '周一', 'Mon': '周一',
        '周二': '周二', '星期二': '周二', 'Tuesday': '周二', 'Tue': '周二',
        '周三': '周三', '星期三': '周三', 'Wednesday': '周三', 'Wed': '周三',
        '周四': '周四', '星期四': '周四', 'Thursday': '周四', 'Thu': '周四',
        '周五': '周五', '星期五': '周五', 'Friday': '周五', 'Fri': '周五',
        '周六': '周六', '星期六': '周六', 'Saturday': '周六', 'Sat': '周六',
        '周日': '周日', '星期日': '周日', 'Sunday': '周日', 'Sun': '周日'
    }
    return weekday_map.get(weekday, weekday)

def get_weekday_number(weekday: str) -> int:
    """Convert weekday string to number (1-7)"""
    weekday_map = {
        '周一': 1, '星期一': 1, 'Monday': 1,
        '周二': 2, '星期二': 2, 'Tuesday': 2,
        '周三': 3, '星期三': 3, 'Wednesday': 3,
        '周四': 4, '星期四': 4, 'Thursday': 4,
        '周五': 5, '星期五': 5, 'Friday': 5,
        '周六': 6, '星期六': 6, 'Saturday': 6,
        '周日': 7, '星期日': 7, 'Sunday': 7
    }
    return weekday_map.get(normalize_weekday(weekday), 1)

def parse_time_range(time_str: str) -> tuple:
    """Parse time range string like '08:00-09:40'"""
    try:
        if '-' in time_str:
            start_time, end_time = time_str.split('-', 1)
            return start_time.strip(), end_time.strip()
        else:
            return time_str.strip(), time_str.strip()
    except Exception as e:
        logger.error(f"Error parsing time range '{time_str}': {e}")
        return '08:00', '09:40'

def merge_schedule_data(base_schedule: Dict, new_schedule: Dict) -> Dict:
    """Merge two schedule data dictionaries"""
    merged = base_schedule.copy()
    
    for key, value in new_schedule.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            merged[key].extend(value)
        else:
            merged[key] = value
    
    return merged

def filter_courses_by_week(courses: List[Dict], week_number: int) -> List[Dict]:
    """Filter courses by week number"""
    return [
        course for course in courses
        if course.get('start_week', 1) <= week_number <= course.get('end_week', 16)
    ]

def filter_tasks_by_status(tasks: List[Dict], status: str) -> List[Dict]:
    """Filter tasks by status"""
    return [task for task in tasks if task.get('status') == status]

def sort_courses_by_time(courses: List[Dict]) -> List[Dict]:
    """Sort courses by day of week and start time"""
    def sort_key(course):
        day = get_weekday_number(course.get('weekday', '周一'))
        time_str = course.get('start_time', '08:00')
        try:
            hour, minute = map(int, time_str.split(':'))
            return (day, hour, minute)
        except:
            return (day, 8, 0)
    
    return sorted(courses, key=sort_key)

def generate_course_id(course: Dict) -> str:
    """Generate unique ID for course"""
    name = course.get('name', 'course')
    teacher = course.get('teacher', 'teacher')
    time = course.get('time', 'time')
    
    import hashlib
    content = f"{name}_{teacher}_{time}"
    return hashlib.md5(content.encode()).hexdigest()[:8]

def generate_task_id(task: Dict) -> str:
    """Generate unique ID for task"""
    title = task.get('title', 'task')
    created = task.get('created_date', datetime.now().isoformat())
    
    import hashlib
    content = f"{title}_{created}"
    return hashlib.md5(content.encode()).hexdigest()[:8]

def clean_data_dict(data: Dict) -> Dict:
    """Clean dictionary by removing None values and empty strings"""
    return {
        key: value for key, value in data.items()
        if value is not None and value != ''
    }

def ensure_data_types(data: Dict, schema: Dict) -> Dict:
    """Ensure data types match schema"""
    result = {}
    
    for key, expected_type in schema.items():
        value = data.get(key)
        
        if value is None:
            result[key] = None
            continue
        
        try:
            if expected_type == int:
                result[key] = int(value)
            elif expected_type == float:
                result[key] = float(value)
            elif expected_type == str:
                result[key] = str(value)
            elif expected_type == bool:
                result[key] = bool(value)
            else:
                result[key] = value
        except (ValueError, TypeError):
            logger.warning(f"Type conversion failed for {key}: {value} -> {expected_type}")
            result[key] = value
    
    return result
