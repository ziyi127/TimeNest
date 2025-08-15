"""
系统配置服务
提供系统参数查询和更新功能
"""

import os
import json
from typing import Dict, Any, Optional
from models.user_settings import UserSettings
from utils.logger import get_service_logger
from utils.exceptions import ValidationException
import datetime

# 初始化日志记录器
logger = get_service_logger("config_service")


class ConfigService:
    """系统配置服务类"""
    
    def __init__(self):
        """初始化系统配置服务"""
        self.config_file = "./data/config.json"
        self.user_settings: Optional[UserSettings] = None
        self._ensure_config_directory()
        self._load_user_settings()
        logger.info("ConfigService initialized")
    
    def _ensure_config_directory(self):
        """确保配置目录存在"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
                logger.debug(f"确保配置目录存在: {config_dir}")
        except Exception as e:
            logger.error(f"创建配置目录失败: {str(e)}")
    
    def _load_user_settings(self):
        """加载用户设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_settings = UserSettings.from_dict(data)
                logger.debug("用户设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.user_settings = UserSettings()
                self._save_user_settings()
                logger.debug("创建默认用户设置")
        except Exception as e:
            logger.error(f"加载用户设置失败: {str(e)}")
            self.user_settings = UserSettings()
    
    def _save_user_settings(self):
        """保存用户设置"""
        try:
            if self.user_settings:
                # 确保配置目录存在
                self._ensure_config_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.user_settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("用户设置保存成功")
        except Exception as e:
            logger.error(f"保存用户设置失败: {str(e)}")
            raise ValidationException("保存用户设置失败")
    
    def get_system_config(self) -> Dict[str, Any]:
        """
        获取系统配置
        
        Returns:
            系统配置字典
        """
        logger.debug("获取系统配置")
        
        try:
            if self.user_settings:
                config = self.user_settings.to_dict()
                # 添加一些系统级配置
                config["system_info"] = {
                    "config_file": self.config_file,
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return config
            else:
                return {}
                
        except Exception as e:
            logger.error(f"获取系统配置失败: {str(e)}")
            return {}
    
    def update_system_config(self, config_data: Dict[str, Any]) -> bool:
        """
        更新系统配置
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            是否更新成功
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info("更新系统配置")
        
        try:
            if not self.user_settings:
                self.user_settings = UserSettings()
            
            # 更新用户设置字段
            if "theme" in config_data:
                self.user_settings.theme = config_data["theme"]
            
            if "language" in config_data:
                self.user_settings.language = config_data["language"]
            
            if "auto_backup" in config_data:
                self.user_settings.auto_backup = config_data["auto_backup"]
            
            if "backup_interval" in config_data:
                self.user_settings.backup_interval = config_data["backup_interval"]
            
            if "data_dir" in config_data:
                self.user_settings.data_dir = config_data["data_dir"]
            
            # 保存设置
            self._save_user_settings()
            
            logger.info("系统配置更新成功")
            return True
            
        except Exception as e:
            logger.error(f"更新系统配置失败: {str(e)}")
            raise ValidationException(f"更新系统配置失败: {str(e)}")
    
    def reset_to_default(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            是否重置成功
        """
        logger.info("重置为默认配置")
        
        try:
            self.user_settings = UserSettings()
            self._save_user_settings()
            
            logger.info("重置为默认配置成功")
            return True
            
        except Exception as e:
            logger.error(f"重置为默认配置失败: {str(e)}")
            return False
    
    def get_config_value(self, key: str, default_value: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default_value: 默认值
            
        Returns:
            配置值
        """
        logger.debug(f"获取配置值: {key}")
        
        try:
            if not self.user_settings:
                return default_value
            
            # 使用getattr获取属性值
            return getattr(self.user_settings, key, default_value)
            
        except Exception as e:
            logger.warning(f"获取配置值失败: {str(e)}")
            return default_value
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否设置成功
        """
        logger.debug(f"设置配置值: {key} = {value}")
        
        try:
            if not self.user_settings:
                self.user_settings = UserSettings()
            
            # 使用setattr设置属性值
            setattr(self.user_settings, key, value)
            
            # 保存设置
            self._save_user_settings()
            
            logger.debug(f"配置值设置成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"设置配置值失败: {str(e)}")
            return False