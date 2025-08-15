"""
增强日志记录工具
提供更详细的日志记录功能和跨平台兼容性处理

作者: TimeNest团队
创建日期: 2024-01-01
版本: 1.0.0
描述: 提供增强的日志记录功能，包括跨平台兼容性处理和错误恢复机制
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
from utils.logger import setup_logger as base_setup_logger

# 跨平台路径处理
def get_cross_platform_path(path: str) -> str:
    """
    获取跨平台兼容的路径
    
    Args:
        path: 原始路径
        
    Returns:
        跨平台兼容的路径
    """
    # 使用os.path.join处理路径分隔符
    # 使用os.path.normpath标准化路径
    return os.path.normpath(path)

# 跨平台文件权限处理
def set_cross_platform_permissions(file_path: str, mode: int = 0o644):
    """
    设置跨平台兼容的文件权限
    
    Args:
        file_path: 文件路径
        mode: 权限模式
    """
    try:
        # 在Unix/Linux/Mac系统上设置权限
        if hasattr(os, 'chmod'):
            os.chmod(file_path, mode)
    except Exception as e:
        # 忽略权限设置错误，因为在某些系统上可能不支持
        pass

# 跨平台编码处理
def get_cross_platform_encoding() -> str:
    """
    获取跨平台兼容的文件编码
    
    Returns:
        文件编码
    """
    # 优先使用UTF-8编码
    return 'utf-8'

class EnhancedLogger:
    """增强日志记录器类"""
    
    def __init__(self, name: str, log_file: Optional[str] = None, level: int = logging.INFO):
        """
        初始化增强日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径（可选）
            level: 日志级别
        """
        # 处理跨平台路径
        if log_file:
            log_file = get_cross_platform_path(log_file)
        
        # 设置基础日志记录器
        self.logger = base_setup_logger(name, log_file, level)
        
        # 设置日志格式包含更多信息
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
        )
        
        # 更新所有处理器的格式
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常信息"""
        self.logger.exception(message, *args, **kwargs)

def setup_enhanced_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> EnhancedLogger:
    """
    设置并返回一个增强的日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径 (可选)
        level: 日志级别
        
    Returns:
        配置好的增强日志记录器
    """
    # 创建logs目录（跨平台兼容）
    if log_file:
        log_dir = os.path.dirname(get_cross_platform_path(log_file))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            # 设置目录权限
            set_cross_platform_permissions(log_dir, 0o755)
    
    return EnhancedLogger(name, log_file, level)

# 创建默认的增强日志记录器
default_logger = setup_enhanced_logger("TimeNest")

# 导出常用的日志函数
debug = default_logger.debug
info = default_logger.info
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
exception = default_logger.exception

# 跨平台系统信息记录
def log_system_info(logger: EnhancedLogger):
    """
    记录系统信息
    
    Args:
        logger: 日志记录器
    """
    logger.info(f"操作系统: {sys.platform}")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 记录时间信息
    logger.info(f"当前时间: {datetime.now().isoformat()}")
    logger.info(f"时区信息: {datetime.now().astimezone().tzinfo}")

# 错误恢复机制
class ErrorRecovery:
    """错误恢复机制类"""
    
    @staticmethod
    def create_backup_file(original_file: str, backup_suffix: str = ".backup") -> str:
        """
        创建文件备份
        
        Args:
            original_file: 原始文件路径
            backup_suffix: 备份文件后缀
            
        Returns:
            备份文件路径
        """
        try:
            # 处理跨平台路径
            original_file = get_cross_platform_path(original_file)
            backup_file = original_file + backup_suffix + "." + datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 复制文件
            import shutil
            shutil.copy2(original_file, backup_file)
            
            # 设置跨平台权限
            set_cross_platform_permissions(backup_file)
            
            return backup_file
        except Exception as e:
            default_logger.error(f"创建备份文件失败: {str(e)}")
            return ""
    
    @staticmethod
    def restore_from_backup(backup_file: str, target_file: str) -> bool:
        """
        从备份文件恢复
        
        Args:
            backup_file: 备份文件路径
            target_file: 目标文件路径
            
        Returns:
            是否恢复成功
        """
        try:
            # 处理跨平台路径
            backup_file = get_cross_platform_path(backup_file)
            target_file = get_cross_platform_path(target_file)
            
            # 检查备份文件是否存在
            if not os.path.exists(backup_file):
                default_logger.error(f"备份文件不存在: {backup_file}")
                return False
            
            # 复制文件
            import shutil
            shutil.copy2(backup_file, target_file)
            
            # 设置跨平台权限
            set_cross_platform_permissions(target_file)
            
            return True
        except Exception as e:
            default_logger.error(f"从备份恢复文件失败: {str(e)}")
            return False

# 友好的错误提示信息
def format_friendly_error_message(error_code: str, message: str, details: Optional[str] = None) -> str:
    """
    格式化友好的错误提示信息
    
    Args:
        error_code: 错误代码
        message: 错误消息
        details: 详细信息（可选）
        
    Returns:
        格式化后的错误提示信息
    """
    # 中文友好的错误提示
    friendly_messages = {
        "VALIDATION_ERROR": "数据验证失败",
        "CONFLICT_ERROR": "资源冲突",
        "NOT_FOUND_ERROR": "资源未找到",
        "DATA_ACCESS_ERROR": "数据访问错误",
        "BUSINESS_LOGIC_ERROR": "业务逻辑错误",
        "UNKNOWN_ERROR": "未知错误"
    }
    
    # 获取友好的错误描述
    friendly_description = friendly_messages.get(error_code, "未知错误")
    
    # 构建完整的错误提示信息
    error_info = f"[{error_code}] {friendly_description}: {message}"
    
    if details:
        error_info += f" (详细信息: {details})"
    
    return error_info