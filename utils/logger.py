"""
日志工具函数
提供统一的日志记录功能
"""

import logging
import os
from datetime import datetime


# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置并返回一个日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径 (可选)
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_service_logger(service_name: str) -> logging.Logger:
    """
    获取服务专用的日志记录器
    
    Args:
        service_name: 服务名称
        
    Returns:
        服务专用的日志记录器
    """
    # 创建logs目录
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名
    log_file = os.path.join(log_dir, f"{service_name}.log")
    
    return setup_logger(f"TimeNest.{service_name}", log_file)


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    记录异常信息
    
    Args:
        logger: 日志记录器
        exception: 异常对象
        context: 异常上下文信息
    """
    if context:
        logger.error(f"{context} - 发生异常: {str(exception)}")
    else:
        logger.error(f"发生异常: {str(exception)}", exc_info=True)