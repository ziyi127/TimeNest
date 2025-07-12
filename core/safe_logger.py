#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 安全日志记录器
防止日志递归和循环引用问题
"""

import logging
import sys
import threading
from typing import Any, Dict, Optional
from datetime import datetime


class SafeLogger:
    """
    安全的日志记录器，防止递归调用和循环引用
    """
    
    def __init__(self, name: str, fallback_to_print: bool = True):
        """
        初始化安全日志记录器
        
        Args:
            name: 日志记录器名称
            fallback_to_print: 当日志记录失败时是否回退到print
        """
        self.name = name
        self.fallback_to_print = fallback_to_print
        self._logger = logging.getLogger(name)
        
        # 递归保护
        self._in_logging = threading.local()
        self._max_recursion_depth = 3
        
        # 错误计数器
        self._error_count = 0
        self._max_errors = 10
        
    def _is_logging_safe(self) -> bool:
        """检查当前是否可以安全记录日志"""
        try:
            # 检查递归深度
            if not hasattr(self._in_logging, 'depth'):
                self._in_logging.depth = 0
            
            if self._in_logging.depth >= self._max_recursion_depth:
                return False
                
            # 检查错误计数
            if self._error_count >= self._max_errors:
                return False
                
            return True
            
        except Exception:
            return False
    
    def _safe_log(self, level: str, message: str, *args, **kwargs) -> None:
        """安全的日志记录"""
        try:
            if not self._is_logging_safe():
                if self.fallback_to_print:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] SAFE_{level.upper()}: {self.name} - {message}")
                return
            
            # 增加递归深度
            self._in_logging.depth += 1
            
            try:
                # 获取日志方法
                log_method = getattr(self._logger, level.lower(), None)
                if log_method:
                    log_method(message, *args, **kwargs)
                else:
                    # 未知日志级别，使用info
                    self._logger.info(f"[{level.upper()}] {message}", *args, **kwargs)
                    
            finally:
                # 减少递归深度
                self._in_logging.depth -= 1
                
        except Exception as e:
            self._error_count += 1
            
            if self.fallback_to_print:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] LOG_ERROR: {self.name} - Failed to log: {message}")
                print(f"[{timestamp}] LOG_ERROR: {self.name} - Error: {e}")
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """记录调试信息"""
        self._safe_log('debug', message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """记录信息"""
        self._safe_log('info', message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """记录警告"""
        self._safe_log('warning', message, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs) -> None:
        """记录警告（别名）"""
        self.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """记录错误"""
        self._safe_log('error', message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """记录严重错误"""
        self._safe_log('critical', message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """记录异常（包含堆栈跟踪）"""
        try:
            if self._is_logging_safe():
                self._in_logging.depth += 1
                try:
                    self._logger.exception(message, *args, **kwargs)
                finally:
                    self._in_logging.depth -= 1
            else:
                if self.fallback_to_print:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] SAFE_EXCEPTION: {self.name} - {message}")
                    import traceback
                    traceback.print_exc()
                    
        except Exception as e:
            self._error_count += 1
            if self.fallback_to_print:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] LOG_ERROR: {self.name} - Failed to log exception: {message}")
                print(f"[{timestamp}] LOG_ERROR: {self.name} - Error: {e}")
    
    def reset_error_count(self) -> None:
        """重置错误计数器"""
        self._error_count = 0
    
    def get_error_count(self) -> int:
        """获取错误计数"""
        return self._error_count
    
    def set_level(self, level) -> None:
        """设置日志级别"""
        try:
            self._logger.setLevel(level)
        except Exception as e:
            if self.fallback_to_print:
                print(f"LOG_ERROR: Failed to set log level: {e}")
    
    def add_handler(self, handler) -> None:
        """添加日志处理器"""
        try:
            self._logger.addHandler(handler)
        except Exception as e:
            if self.fallback_to_print:
                print(f"LOG_ERROR: Failed to add handler: {e}")
    
    def remove_handler(self, handler) -> None:
        """移除日志处理器"""
        try:
            self._logger.removeHandler(handler)
        except Exception as e:
            if self.fallback_to_print:
                print(f"LOG_ERROR: Failed to remove handler: {e}")


def get_safe_logger(name: str, fallback_to_print: bool = True) -> SafeLogger:
    """
    获取安全日志记录器实例
    
    Args:
        name: 日志记录器名称
        fallback_to_print: 当日志记录失败时是否回退到print
        
    Returns:
        SafeLogger实例
    """
    return SafeLogger(name, fallback_to_print)


# 全局安全日志记录器缓存
_safe_loggers: Dict[str, SafeLogger] = {}
_logger_lock = threading.Lock()


def get_cached_safe_logger(name: str, fallback_to_print: bool = True) -> SafeLogger:
    """
    获取缓存的安全日志记录器实例
    
    Args:
        name: 日志记录器名称
        fallback_to_print: 当日志记录失败时是否回退到print
        
    Returns:
        SafeLogger实例
    """
    with _logger_lock:
        if name not in _safe_loggers:
            _safe_loggers[name] = SafeLogger(name, fallback_to_print)
        return _safe_loggers[name]


def clear_logger_cache() -> None:
    """清除日志记录器缓存"""
    with _logger_lock:
        _safe_loggers.clear()


def reset_all_error_counts() -> None:
    """重置所有日志记录器的错误计数"""
    with _logger_lock:
        for logger in _safe_loggers.values():
            logger.reset_error_count()


def get_logger_stats() -> Dict[str, Dict[str, Any]]:
    """获取所有日志记录器的统计信息"""
    with _logger_lock:
        stats = {}
        for name, logger in _safe_loggers.items():
            stats[name] = {
                'error_count': logger.get_error_count(),
                'fallback_enabled': logger.fallback_to_print
            }
        return stats


# 便捷函数
def safe_debug(name: str, message: str, *args, **kwargs) -> None:
    """便捷的安全调试日志"""
    get_cached_safe_logger(name).debug(message, *args, **kwargs)


def safe_info(name: str, message: str, *args, **kwargs) -> None:
    """便捷的安全信息日志"""
    get_cached_safe_logger(name).info(message, *args, **kwargs)


def safe_warning(name: str, message: str, *args, **kwargs) -> None:
    """便捷的安全警告日志"""
    get_cached_safe_logger(name).warning(message, *args, **kwargs)


def safe_error(name: str, message: str, *args, **kwargs) -> None:
    """便捷的安全错误日志"""
    get_cached_safe_logger(name).error(message, *args, **kwargs)


def safe_exception(name: str, message: str, *args, **kwargs) -> None:
    """便捷的安全异常日志"""
    get_cached_safe_logger(name).exception(message, *args, **kwargs)


# 测试函数
def test_safe_logger():
    """测试安全日志记录器"""
    print("Testing SafeLogger...")
    
    # 创建测试日志记录器
    logger = get_safe_logger("test_logger")
    
    # 测试各种日志级别
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # 测试异常记录
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Test exception occurred")
    
    # 测试递归保护
    def recursive_log(depth=0):
        if depth < 10:
            logger.info(f"Recursive log depth: {depth}")
            recursive_log(depth + 1)
    
    recursive_log()
    
    print(f"Logger error count: {logger.get_error_count()}")
    print("SafeLogger test completed.")


if __name__ == "__main__":
    test_safe_logger()
