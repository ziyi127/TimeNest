"""
系统调试服务
提供系统调试模式配置和日志管理功能
"""

import json
import os
import logging
from typing import Optional, Dict, Any
from models.debug_config import DebugSettings
from utils.logger import get_service_logger, set_debug_mode

# 初始化服务日志记录器
service_logger = get_service_logger("debug_service")


class DebugService:
    """系统调试服务类"""
    
    def __init__(self):
        """初始化系统调试服务"""
        self.config_file = "./data/debug_config.json"
        self.settings: Optional[DebugSettings] = None
        self._ensure_data_directory()
        self._load_settings()
        self._apply_debug_settings()
        service_logger.info("DebugService initialized")
    
    def _ensure_data_directory(self):
        """确保数据目录存在"""
        try:
            data_dir = os.path.dirname(self.config_file)
            if data_dir:
                os.makedirs(data_dir, exist_ok=True)
                service_logger.debug(f"确保数据目录存在: {data_dir}")
        except Exception as e:
            service_logger.error(f"创建数据目录失败: {str(e)}")
    
    def _load_settings(self):
        """加载调试设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = DebugSettings.from_dict(data)
                service_logger.debug("调试设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = DebugSettings()
                self._save_settings()
                service_logger.debug("创建默认调试设置")
        except Exception as e:
            service_logger.error(f"加载调试设置失败: {str(e)}")
            self.settings = DebugSettings()
    
    def _save_settings(self):
        """保存调试设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                service_logger.debug("调试设置保存成功")
        except Exception as e:
            service_logger.error(f"保存调试设置失败: {str(e)}")
            raise Exception("保存调试设置失败")
    
    def _apply_debug_settings(self):
        """应用调试设置到系统"""
        try:
            if self.settings:
                # 设置调试模式
                set_debug_mode(self.settings.enabled)
                
                # 配置根日志记录器
                root_logger = logging.getLogger()
                if self.settings.enabled:
                    root_logger.setLevel(getattr(logging, self.settings.log_level.upper()))
                else:
                    root_logger.setLevel(logging.INFO)
                
                # 如果启用文件日志，则添加文件处理器
                if self.settings.log_to_file and self.settings.log_file_path:
                    # 确保日志目录存在
                    log_dir = os.path.dirname(self.settings.log_file_path)
                    if log_dir:
                        os.makedirs(log_dir, exist_ok=True)
                    
                    # 创建文件处理器
                    file_handler = logging.FileHandler(
                        self.settings.log_file_path, 
                        encoding='utf-8'
                    )
                    file_handler.setFormatter(
                        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                    )
                    root_logger.addHandler(file_handler)
                
                service_logger.debug("调试设置已应用到系统")
        except Exception as e:
            service_logger.error(f"应用调试设置失败: {str(e)}")
    
    def get_settings(self) -> DebugSettings:
        """
        获取调试设置
        
        Returns:
            DebugSettings: 调试设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or DebugSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新调试设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        service_logger.info("更新调试设置")
        
        try:
            if not self.settings:
                self.settings = DebugSettings()
            
            # 更新设置字段
            for key, value in settings_data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # 保存设置
            self._save_settings()
            
            # 应用新的调试设置
            self._apply_debug_settings()
            
            service_logger.info("调试设置更新成功")
            return True
        except Exception as e:
            service_logger.error(f"更新调试设置失败: {str(e)}")
            return False
    
    def enable_debug_mode(self) -> bool:
        """
        启用调试模式
        
        Returns:
            bool: 是否启用成功
        """
        try:
            if not self.settings:
                self.settings = DebugSettings()
            
            self.settings.enabled = True
            self._save_settings()
            self._apply_debug_settings()
            
            service_logger.info("调试模式已启用")
            return True
        except Exception as e:
            service_logger.error(f"启用调试模式失败: {str(e)}")
            return False
    
    def disable_debug_mode(self) -> bool:
        """
        禁用调试模式
        
        Returns:
            bool: 是否禁用成功
        """
        try:
            if not self.settings:
                self.settings = DebugSettings()
            
            self.settings.enabled = False
            self._save_settings()
            self._apply_debug_settings()
            
            service_logger.info("调试模式已禁用")
            return True
        except Exception as e:
            service_logger.error(f"禁用调试模式失败: {str(e)}")
            return False
    
    def set_log_level(self, level: str) -> bool:
        """
        设置日志级别
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            bool: 是否设置成功
        """
        try:
            if not self.settings:
                self.settings = DebugSettings()
            
            # 验证日志级别
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if level.upper() not in valid_levels:
                service_logger.warning(f"无效的日志级别: {level}")
                return False
            
            self.settings.log_level = level.upper()
            self._save_settings()
            self._apply_debug_settings()
            
            service_logger.info(f"日志级别已设置为: {level.upper()}")
            return True
        except Exception as e:
            service_logger.error(f"设置日志级别失败: {str(e)}")
            return False
    
    def enable_file_logging(self, file_path: str) -> bool:
        """
        启用文件日志记录
        
        Args:
            file_path: 日志文件路径
            
        Returns:
            bool: 是否启用成功
        """
        try:
            if not self.settings:
                self.settings = DebugSettings()
            
            self.settings.log_to_file = True
            self.settings.log_file_path = file_path
            self._save_settings()
            self._apply_debug_settings()
            
            service_logger.info(f"文件日志记录已启用: {file_path}")
            return True
        except Exception as e:
            service_logger.error(f"启用文件日志记录失败: {str(e)}")
            return False
    
    def disable_file_logging(self) -> bool:
        """
        禁用文件日志记录
        
        Returns:
            bool: 是否禁用成功
        """
        try:
            if not self.settings:
                self.settings = DebugSettings()
            
            self.settings.log_to_file = False
            self._save_settings()
            self._apply_debug_settings()
            
            service_logger.info("文件日志记录已禁用")
            return True
        except Exception as e:
            service_logger.error(f"禁用文件日志记录失败: {str(e)}")
            return False
    
    def get_debug_status(self) -> Dict[str, Any]:
        """
        获取调试状态
        
        Returns:
            Dict[str, Any]: 调试状态信息
        """
        try:
            return {
                "enabled": self.settings.enabled if self.settings else False,
                "log_level": self.settings.log_level if self.settings else "INFO",
                "log_to_file": self.settings.log_to_file if self.settings else False,
                "log_file_path": self.settings.log_file_path if self.settings else None
            }
        except Exception as e:
            service_logger.error(f"获取调试状态失败: {str(e)}")
            return {
                "enabled": False,
                "log_level": "INFO",
                "log_to_file": False,
                "log_file_path": None
            }
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return True  # 调试服务始终启用