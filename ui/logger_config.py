"""
日志配置模块
提供统一的日志配置和初始化功能
"""

import logging
import logging.handlers
import os
from pathlib import Path
import platform


def setup_logger(name: str = "TimeNest", level: str = "INFO", log_dir: str = None):
    """
    设置日志配置
    
    Args:
        name: 日志器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志文件目录，如果为None则使用默认文档目录
    
    Returns:
        配置好的日志器实例
    """
    
    # 获取跨平台日志目录
    if log_dir is None:
        system = platform.system().lower()
        if system == "windows":
            log_dir = Path.home() / "Documents" / "TimeNest-TkTT" / "logs"
        elif system == "darwin":  # macOS
            log_dir = Path.home() / "Documents" / "TimeNest-TkTT" / "logs"
        else:  # Linux
            log_dir = Path.home() / "Documents" / "TimeNest-TkTT" / "logs"
    
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 如果日志器已经有处理器，则清除它们
    logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # 文件处理器（按日期轮转）
    log_file = log_dir / "timetable.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    # 错误日志处理器
    error_log_file = log_dir / "error.log"
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str = "TimeNest"):
    """
    获取已配置的日志器
    
    Args:
        name: 日志器名称
    
    Returns:
        日志器实例
    """
    return logging.getLogger(name)