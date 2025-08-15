"""
增强异常处理工具
提供跨平台的异常处理、恢复机制和更友好的错误信息
"""

import traceback
import sys
import os
from typing import Callable, Any, Dict
from datetime import datetime
from utils.logger import get_service_logger
from utils.exceptions import TimeNestException, ValidationException, ConflictException, NotFoundException

# 初始化日志记录器
logger = get_service_logger("enhanced_exception_handler")

# 初始化日志记录器
logger = get_service_logger("enhanced_exception_handler")


class EnhancedExceptionHandler:
    """增强异常处理器类"""
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = "", 
                        error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
        """
        处理异常并返回标准化的错误信息，增强跨平台兼容性
        
        Args:
            exception: 异常对象
            context: 异常上下文信息
            error_code: 错误代码
            
        Returns:
            标准化的错误信息字典
        """
        # 记录详细的异常信息
        logger.error(f"处理异常 - 上下文: {context}, 异常: {str(exception)}")
        logger.error(f"异常详情: {traceback.format_exc()}")
        
        # 根据异常类型构建错误信息
        if isinstance(exception, TimeNestException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": exception.error_code or error_code,
                "details": getattr(exception, 'errors', None) or getattr(exception, 'conflicts', None),
                "platform": sys.platform
            }
        elif isinstance(exception, ValidationException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": "VALIDATION_ERROR",
                "details": getattr(exception, 'errors', []),
                "platform": sys.platform
            }
        elif isinstance(exception, ConflictException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": "CONFLICT_ERROR",
                "details": getattr(exception, 'conflicts', []),
                "platform": sys.platform
            }
        elif isinstance(exception, NotFoundException):
            return {
                "success": False,
                "error": exception.message,
                "error_code": "NOT_FOUND_ERROR",
                "details": getattr(exception, 'resource_id', None),
                "platform": sys.platform
            }
        else:
            # 处理未预期的异常
            error_message = str(exception) if str(exception) else "未知错误"
            return {
                "success": False,
                "error": error_message,
                "error_code": error_code,
                "details": None,
                "platform": sys.platform
            }
    
    @staticmethod
    def safe_execute(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        安全执行函数，捕获并处理异常，增强跨平台兼容性
        
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
                "data": result,
                "platform": sys.platform
            }
        except Exception as e:
            return EnhancedExceptionHandler.handle_exception(e, f"执行函数 {func.__name__}")
    
    @staticmethod
    def retry_on_failure(func: Callable[..., Any], max_retries: int = 3, 
                        delay: float = 1.0, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        失败重试执行函数，增强跨平台兼容性
        
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
        
        last_exception: Exception | None = None
        
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"函数 {func.__name__} 在第 {attempt + 1} 次尝试后成功")
                return {
                    "success": True,
                    "data": result,
                    "attempts": attempt + 1,
                    "platform": sys.platform
                }
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}")
                    time.sleep(delay)
                else:
                    logger.error(f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败")
        
        # 所有重试都失败了
        if last_exception is not None:
            return EnhancedExceptionHandler.handle_exception(
                last_exception, 
                f"执行函数 {func.__name__} 重试 {max_retries} 次后仍然失败"
            )
        else:
            # 这种情况理论上不应该发生，但如果真的发生了，返回一个默认错误
            return {
                "success": False,
                "error": "执行函数失败且无异常信息",
                "error_code": "EXECUTION_FAILED",
                "details": None,
                "platform": sys.platform
            }

    @staticmethod
    def create_platform_safe_backup(original_file: str, backup_suffix: str = ".backup") -> str:
        """
        创建跨平台兼容的文件备份
        
        Args:
            original_file: 原始文件路径
            backup_suffix: 备份文件后缀
            
        Returns:
            备份文件路径
        """
        try:
            # 标准化路径，确保跨平台兼容性
            original_file = os.path.normpath(original_file)
            backup_file = original_file + backup_suffix + "." + datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 复制文件
            import shutil
            shutil.copy2(original_file, backup_file)
            
            return backup_file
        except Exception as e:
            logger.error(f"创建备份文件失败: {str(e)}")
            return ""

    @staticmethod
    def restore_from_backup(backup_file: str, target_file: str) -> bool:
        """
        从备份文件恢复，确保跨平台兼容性
        
        Args:
            backup_file: 备份文件路径
            target_file: 目标文件路径
            
        Returns:
            是否恢复成功
        """
        try:
            # 标准化路径，确保跨平台兼容性
            backup_file = os.path.normpath(backup_file)
            target_file = os.path.normpath(target_file)
            
            # 检查备份文件是否存在
            if not os.path.exists(backup_file):
                logger.error(f"备份文件不存在: {backup_file}")
                return False
            
            # 复制文件
            import shutil
            shutil.copy2(backup_file, target_file)
            
            return True
        except Exception as e:
            logger.error(f"从备份恢复文件失败: {str(e)}")
            return False


def global_exception_handler(exc_type, exc_value, exc_traceback) -> None:
    """
    全局异常处理器，增强跨平台兼容性
    可以通过 sys.excepthook = global_exception_handler 设置
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 不处理键盘中断
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("未捕获的全局异常", exc_info=(exc_type, exc_value, exc_traceback))


# 设置全局异常处理器
sys.excepthook = global_exception_handler
