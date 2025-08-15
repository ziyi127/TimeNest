"""
日期时间工具函数
提供日期时间相关的计算和转换功能

该模块包含以下功能：
- 计算指定日期相对于学期开始日期的周奇偶性
- 获取指定日期所在周的日期列表
- 检查日期是否在指定范围内
- 计算指定日期在循环课程表中的周索引
"""

from datetime import datetime, timedelta
from typing import List, Tuple


def get_week_parity(date_str: str, start_date_str: str) -> str:
    """
    计算指定日期相对于学期开始日期的周奇偶性
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        start_date_str: 学期开始日期字符串 (YYYY-MM-DD)
        
    Returns:
        "odd"表示奇数周, "even"表示偶数周
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # 计算周数 (从0开始)
    week_number = (date - start_date).days // 7
    
    # 返回奇偶性
    return "odd" if week_number % 2 == 0 else "even"


def get_week_dates(date_str: str) -> List[str]:
    """
    获取指定日期所在周的日期列表
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        一周的日期列表，从周日开始
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    
    # 计算本周日的日期
    sunday = date - timedelta(days=date.weekday())
    
    # 生成一周的日期列表
    week_dates = []
    for i in range(7):
        day = sunday + timedelta(days=i)
        week_dates.append(day.strftime("%Y-%m-%d"))
    
    return week_dates


def is_date_in_range(date_str: str, start_date_str: str, end_date_str: str) -> bool:
    """
    检查日期是否在指定范围内
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        start_date_str: 开始日期字符串 (YYYY-MM-DD)
        end_date_str: 结束日期字符串 (YYYY-MM-DD)
        
    Returns:
        是否在范围内
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    return start_date <= date <= end_date


def get_cycle_week_index(date_str: str, start_date_str: str, cycle_length: int) -> int:
    """
    计算指定日期在循环课程表中的周索引
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        start_date_str: 循环开始日期字符串 (YYYY-MM-DD)
        cycle_length: 循环长度
        
    Returns:
        循环中的周索引 (0-based)
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # 计算周数 (从0开始)
    week_number = (date - start_date).days // 7
    
    # 返回循环中的周索引
    return week_number % cycle_length