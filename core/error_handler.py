#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 错误处理工具
提供统一的错误处理和异常捕获机制
"""

import functools
import logging
import traceback
from typing import Any, Callable, Optional, Union, Dict
from core.safe_logger import get_cached_safe_logger


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self, logger_name="error_handler"):
        self.logger = get_cached_safe_logger(logger_name)
        self.error_counts = {}
        self.max_errors_per_function = 10
        
    def safe_execute(self, func: Callable, *args, default_return=None, **kwargs) -> Any:
        """安全执行函数，捕获所有异常"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            func_name = getattr(func, '__name__', str(func))
            self.logger.error(f"执行函数 {func_name} 失败: {e}")
            return default_return
    
    def with_error_handling(self, 
                          default_return=None, 
                          log_errors=True, 
                          reraise=False,
                          max_retries=0):
        """错误处理装饰器"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = f"{func.__module__}.{func.__qualname__}"
                
                # 检查错误计数
                if func_name in self.error_counts:
                    if self.error_counts[func_name] >= self.max_errors_per_function:
                        if log_errors:
                            self.logger.warning(f"函数 {func_name} 错误次数过多，跳过执行")
                        return default_return
                
                retries = 0
                while retries <= max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        retries += 1
                        
                        # 更新错误计数
                        self.error_counts[func_name] = self.error_counts.get(func_name, 0) + 1
                        
                        if log_errors:
                            if retries <= max_retries:
                                self.logger.warning(f"函数 {func_name} 执行失败 (重试 {retries}/{max_retries}): {e}")
                            else:
                                self.logger.error(f"函数 {func_name} 执行失败: {e}")
                                if self.logger.logger.isEnabledFor(logging.DEBUG):
                                    self.logger.error(f"详细错误信息:\n{traceback.format_exc()}")
                        
                        if retries > max_retries:
                            if reraise:
                                raise
                            return default_return
                            
                return default_return
            return wrapper
        return decorator
    
    def reset_error_counts(self, func_name: Optional[str] = None):
        """重置错误计数"""
        if func_name:
            self.error_counts.pop(func_name, None)
        else:
            self.error_counts.clear()
    
    def get_error_stats(self) -> Dict[str, int]:
        """获取错误统计"""
        return self.error_counts.copy()


# 全局错误处理器实例
_global_error_handler = ErrorHandler()


def safe_call(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """安全调用函数的便捷方法"""
    return _global_error_handler.safe_execute(func, *args, default_return=default_return, **kwargs)


def error_handler(default_return=None, log_errors=True, reraise=False, max_retries=0):
    """错误处理装饰器的便捷方法"""
    return _global_error_handler.with_error_handling(
        default_return=default_return,
        log_errors=log_errors,
        reraise=reraise,
        max_retries=max_retries
    )


def safe_getattr(obj: Any, attr: str, default=None) -> Any:
    """安全获取对象属性"""
    try:
        if obj is None:
            return default
        return getattr(obj, attr, default)
    except Exception:
        return default


def safe_getitem(obj: Any, key: Union[str, int], default=None) -> Any:
    """安全获取字典/列表项"""
    try:
        if obj is None:
            return default
        if hasattr(obj, 'get') and callable(obj.get):
            return obj.get(key, default)
        elif hasattr(obj, '__getitem__'):
            return obj[key] if key in obj else default
        else:
            return default
    except (KeyError, IndexError, TypeError):
        return default


def safe_call_method(obj: Any, method_name: str, *args, default_return=None, **kwargs) -> Any:
    """安全调用对象方法"""
    try:
        if obj is None:
            return default_return
        method = getattr(obj, method_name, None)
        if method and callable(method):
            return method(*args, **kwargs)
        else:
            return default_return
    except Exception as e:
        logger = get_cached_safe_logger("safe_call_method")
        logger.error(f"调用方法 {method_name} 失败: {e}")
        return default_return


def validate_not_none(value: Any, name: str = "value") -> Any:
    """验证值不为None"""
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    return value


def validate_type(value: Any, expected_type: type, name: str = "value") -> Any:
    """验证值的类型"""
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} 必须是 {expected_type.__name__} 类型，实际是 {type(value).__name__}")
    return value


def validate_not_empty(value: Union[str, list, dict], name: str = "value") -> Any:
    """验证值不为空"""
    if not value:
        raise ValueError(f"{name} 不能为空")
    return value


class SafeDict(dict):
    """安全字典，访问不存在的键时返回None而不是抛出异常"""
    
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return None
    
    def get_safe(self, key, default=None):
        """安全获取值"""
        try:
            return self[key] if key in self else default
        except Exception:
            return default


class SafeList(list):
    """安全列表，访问越界索引时返回None而不是抛出异常"""
    
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            return None
    
    def get_safe(self, index, default=None):
        """安全获取值"""
        try:
            return self[index] if 0 <= index < len(self) else default
        except Exception:
            return default


def create_safe_dict(data: dict = None) -> SafeDict:
    """创建安全字典"""
    return SafeDict(data or {})


def create_safe_list(data: list = None) -> SafeList:
    """创建安全列表"""
    return SafeList(data or [])


# 异常类型映射，用于更好的错误处理
EXCEPTION_HANDLERS = {
    AttributeError: lambda e: f"属性错误: {e}",
    KeyError: lambda e: f"键错误: {e}",
    IndexError: lambda e: f"索引错误: {e}",
    TypeError: lambda e: f"类型错误: {e}",
    ValueError: lambda e: f"值错误: {e}",
    ImportError: lambda e: f"导入错误: {e}",
    FileNotFoundError: lambda e: f"文件未找到: {e}",
    PermissionError: lambda e: f"权限错误: {e}",
}


def format_exception(e: Exception) -> str:
    """格式化异常信息"""
    exception_type = type(e)
    if exception_type in EXCEPTION_HANDLERS:
        return EXCEPTION_HANDLERS[exception_type](e)
    else:
        return f"未知错误 ({exception_type.__name__}): {e}"


def log_exception(logger, e: Exception, context: str = ""):
    """记录异常信息"""
    formatted_error = format_exception(e)
    if context:
        logger.error(f"{context}: {formatted_error}")
    else:
        logger.error(formatted_error)
    
    # 在调试模式下记录完整堆栈
    if logger.logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"完整堆栈信息:\n{traceback.format_exc()}")


# 导出的便捷函数
__all__ = [
    'ErrorHandler',
    'safe_call',
    'error_handler', 
    'safe_getattr',
    'safe_getitem',
    'safe_call_method',
    'validate_not_none',
    'validate_type',
    'validate_not_empty',
    'SafeDict',
    'SafeList',
    'create_safe_dict',
    'create_safe_list',
    'format_exception',
    'log_exception'
]
