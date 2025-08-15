"""
异常处理工具
提供统一的异常处理框架和错误恢复机制
"""

import traceback
import sys
from typing import Optional, Callable, Any
from utils.logger import get_service_logger
from utils.exceptions import TimeNestException, ValidationException, ConflictException, NotFoundException

# 初始化日志记录器
logger = get_service_logger("exception_handler")


class ExceptionHandler:
    """异常处理器类"""
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = "", 
                        error_code: str = "UNKNOWN_ERROR") -> dict:
        """
        处理异常并返回标准化的错误信息
        
        Args:
            exception: 异常对象
            context: 异常上下文信息
            error_code: 错误代码
            
        Returns:
            标准化的错误信息字典
        """
        logger.error(f"处理异常 - 上下文: {context}, 异常: {str(exception)}")
        
        # 记录详细的异常信息
        logger.error(f"异常详情: {traceback.format_exc()}")
        
        # 根据异常类型构建错误信息
        if isinstance(exception, TimeNestException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": exception.error_code or error_code,
                "details": getattr(exception, 'errors', None) or getattr(exception, 'conflicts', None)
            }
        elif isinstance(exception, ValidationException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": "VALIDATION_ERROR",
                "details": getattr(exception, 'errors', [])
            }
        elif isinstance(exception, ConflictException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": "CONFLICT_ERROR",
                "details": getattr(exception, 'conflicts', [])
            }
        elif isinstance(exception, NotFoundException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": "NOT_FOUND_ERROR",
                "details": getattr(exception, 'resource_id', None)
            }
        else:
            # 处理未预期的异常
            error_message = str(exception) if str(exception) else "未知错误"
            return {
                "success": False,
                "error": error_message,
                "error_code": error_code,
                "details": None
            }
    
    @staticmethod
    def safe_execute(func: Callable, *args, **kwargs) -> dict:
        """
        安全执行函数，捕获并处理异常
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            执行结果或错误信息字典
        """
        try:
            result = func(*args, **kwargs)
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return ExceptionHandler.handle_exception(e, f"执行函数 {func.__name__}")
    
    @staticmethod
    def retry_on_failure(func: Callable, max_retries: int = 3, 
                        delay: float = 1.0, *args, **kwargs) -> dict:
        """
        失败重试执行函数
        
        Args:
            func: 要执行的函数
            max_retries: 最大重试次数
            delay: 重试延迟（秒）
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            执行结果或错误信息字典
        """
        import time
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"函数 {func.__name__} 在第 {attempt + 1} 次尝试后成功")
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}")
                    time.sleep(delay)
                else:
                    logger.error(f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败")
        
        # 所有重试都失败了
        return ExceptionHandler.handle_exception(
            last_exception, 
            f"执行函数 {func.__name__} 重试 {max_retries} 次后仍然失败"
        )


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    全局异常处理器
    可以通过 sys.excepthook = global_exception_handler 设置
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 不处理键盘中断
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("未捕获的全局异常", exc_info=(exc_type, exc_value, exc_traceback))


# 设置全局异常处理器
sys.excepthook = global_exception_handler