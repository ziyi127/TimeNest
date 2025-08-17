"""
用户服务
提供用户管理相关的业务逻辑处理
"""

import hashlib
import secrets
import datetime
import os
from typing import Optional
from models.password_config import PasswordConfig
from models.user_settings import UserSettings
from utils.logger import get_service_logger
from utils.exceptions import ValidationException
from data_access.json_data_access import JSONDataAccess

# 初始化日志记录器
logger = get_service_logger("user_service")


class UserService:
    """用户服务类"""
    
    def __init__(self):
        """初始化用户服务"""
        self.data_access = JSONDataAccess()
        self.password_config: Optional[PasswordConfig] = None
        self.user_settings: Optional[UserSettings] = None
        self._load_password_config()
        self._load_user_settings()
        logger.info("UserService initialized")
    
    def _load_password_config(self):
        """加载密码配置"""
        try:
            data = self.data_access.read_json("password_config.json")
            if data:
                self.password_config = PasswordConfig.from_dict(data)
            else:
                # 如果配置文件不存在，创建默认配置
                self.password_config = PasswordConfig()
                self._save_password_config()
        except Exception as e:
            logger.error(f"加载密码配置失败: {str(e)}")
            self.password_config = PasswordConfig()
    
    def _load_user_settings(self):
        """加载用户设置"""
        try:
            data = self.data_access.read_json("user_settings.json")
            if data:
                self.user_settings = UserSettings.from_dict(data)
            else:
                # 如果配置文件不存在，创建默认配置
                self.user_settings = UserSettings()
                self._save_user_settings()
        except Exception as e:
            logger.error(f"加载用户设置失败: {str(e)}")
            self.user_settings = UserSettings()
    
    def _save_password_config(self):
        """保存密码配置"""
        try:
            if self.password_config:
                data = self.password_config.to_dict()
                self.data_access.write_json("password_config.json", data)
                logger.info("密码配置已保存")
        except Exception as e:
            logger.error(f"保存密码配置失败: {str(e)}")
            raise ValidationException("保存密码配置失败")
    
    def _save_user_settings(self):
        """保存用户设置"""
        try:
            if self.user_settings:
                data = self.user_settings.to_dict()
                self.data_access.write_json("user_settings.json", data)
                logger.info("用户设置已保存")
        except Exception as e:
            logger.error(f"保存用户设置失败: {str(e)}")
            raise ValidationException("保存用户设置失败")
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        对密码进行哈希处理
        
        Args:
            password: 明文密码
            salt: 盐值，如果为None则生成新的盐值
            
        Returns:
            (hashed_password, salt): 哈希密码和盐值
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用SHA-256进行哈希
        password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return password_hash, salt
    
    def set_password(self, password: str) -> bool:
        """
        设置系统密码
        
        Args:
            password: 新密码
            
        Returns:
            是否设置成功
            
        Raises:
            ValidationException: 密码验证失败
        """
        logger.info("设置系统密码")
        
        # 验证密码强度
        self._validate_password_strength(password)
        
        # 生成哈希密码和盐值
        password_hash, salt = self._hash_password(password)
        
        # 更新并保存密码配置
        self._update_and_save_password_config(password_hash, salt)
        
        logger.info("系统密码设置成功")
        return True
    
    def _validate_password_strength(self, password: str) -> None:
        """
        验证密码强度
        
        Args:
            password: 要验证的密码
            
        Raises:
            ValidationException: 密码验证失败
        """
        if not password or len(password) < 4:
            logger.warning("密码长度不足")
            raise ValidationException("密码长度至少为4位")
    
    def _update_and_save_password_config(self, password_hash: str, salt: str) -> None:
        """
        更新并保存密码配置
        
        Args:
            password_hash: 哈希密码
            salt: 盐值
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.password_config is None:
            self.password_config = PasswordConfig()
            
        self.password_config.is_enabled = True
        self.password_config.password_hash = password_hash
        self.password_config.salt = salt
        self.password_config.updated_at = current_time
        
        if not self.password_config.created_at:
            self.password_config.created_at = current_time
        
        # 保存配置
        self._save_password_config()
    
    def disable_password(self) -> bool:
        """
        禁用密码保护
        
        Returns:
            是否禁用成功
        """
        logger.info("禁用密码保护")
        
        # 禁用并保存密码配置
        self._disable_and_save_password_config()
        
        logger.info("密码保护已禁用")
        return True
    
    def _disable_and_save_password_config(self) -> None:
        """
        禁用并保存密码配置
        """
        if self.password_config is None:
            self.password_config = PasswordConfig()
            
        self.password_config.is_enabled = False
        self.password_config.password_hash = ""
        self.password_config.salt = ""
        
        # 保存配置
        self._save_password_config()
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 要验证的密码
            
        Returns:
            密码是否正确
        """
        logger.debug("验证系统密码")
        
        # 检查是否需要验证密码
        if not self._is_password_verification_needed():
            return True
        
        # 验证密码
        is_valid = self._validate_password(password)
        
        # 记录验证结果
        self._log_password_verification_result(is_valid)
        
        return is_valid
    
    def _is_password_verification_needed(self) -> bool:
        """
        检查是否需要验证密码
        
        Returns:
            是否需要验证密码
        """
        # 如果未启用密码保护，直接返回False
        if self.password_config is None or not self.password_config.is_enabled:
            return False
        
        # 如果没有设置密码，直接返回False
        if not self.password_config.password_hash:
            return False
        
        return True
    
    def _validate_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 要验证的密码
            
        Returns:
            密码是否正确
        """
        # 哈希输入的密码
        input_hash, _ = self._hash_password(password, self.password_config.salt)
        
        # 比较哈希值
        return input_hash == self.password_config.password_hash
    
    def _log_password_verification_result(self, is_valid: bool) -> None:
        """
        记录密码验证结果
        
        Args:
            is_valid: 密码是否有效
        """
        if is_valid:
            logger.info("密码验证成功")
        else:
            logger.warning("密码验证失败")
    
    def is_password_enabled(self) -> bool:
        """
        检查是否启用了密码保护
        
        Returns:
            是否启用了密码保护
        """
        return self.password_config.is_enabled if self.password_config else False
    
    def get_password_config(self) -> PasswordConfig:
        """
        获取密码配置
        
        Returns:
            密码配置对象
        """
        return self._ensure_password_config_exists()
    
    def _ensure_password_config_exists(self) -> PasswordConfig:
        """
        确保密码配置对象存在
        
        Returns:
            密码配置对象
        """
        if self.password_config is None:
            self.password_config = PasswordConfig()
        return self.password_config
    
    def get_user_settings(self) -> UserSettings:
        """
        获取用户设置
        
        Returns:
            用户设置对象
        """
        return self._ensure_user_settings_exists()
    
    def _ensure_user_settings_exists(self) -> UserSettings:
        """
        确保用户设置对象存在
        
        Returns:
            用户设置对象
        """
        if self.user_settings is None:
            self.user_settings = UserSettings()
        return self.user_settings
    
    def update_user_settings(self, user_settings: UserSettings) -> UserSettings:
        """
        更新用户设置
        
        Args:
            user_settings: 新的用户设置对象
            
        Returns:
            更新后的用户设置对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info("更新用户设置")
        
        # 更新用户设置
        self.user_settings = user_settings
        
        # 保存配置
        self._save_user_settings()
        
        # 清空变更字段记录
        self.user_settings.clear_changed_fields()
        
        logger.info("用户设置更新成功")
        return self.user_settings