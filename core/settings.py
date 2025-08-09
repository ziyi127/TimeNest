# TimeNest 设置管理类
# 完整重构自Classisland的Settings类

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class TimeNestSettings(QObject):
    """TimeNest应用设置类"""
    
    # 设置变更信号
    settings_changed = Signal(str)
    
    def __init__(self, app_data_path: Path):
        """
        初始化设置管理器
        
        Args:
            app_data_path: 应用数据目录路径
        """
        super().__init__()
        
        self.app_data_path = app_data_path
        self.settings_file = app_data_path / 'settings.json'
        
        # 初始化默认设置
        self._settings = self._get_default_settings()
        
        # 加载已保存的设置
        self.load_settings()
        
        logger.info("TimeNest设置管理器已初始化")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            # 一般设置
            "selected_profile": "Default.json",
            "is_main_window_visible": True,
            "is_welcome_window_showed": False,
            
            # 外观设置
            "theme": 2,
            "primary_color": "#007bff",
            "secondary_color": "#6c757d",
            "color_source": 1,
            "background_color": "#000000",
            "is_custom_background_color_enabled": False,
            "opacity": 0.5,
            "scale": 1.0,
            "main_window_font": "Arial",
            "main_window_font_weight": 400,
            
            # 时间设置
            "single_week_start_time": datetime.now().strftime("%Y-%m-%d"),
            "class_prepare_notify_seconds": 60,
            "show_date": True,
            "hide_on_class": False,
            "is_class_changing_notification_enabled": True,
            "is_class_prepare_notification_enabled": True,
            "is_class_off_notification_enabled": True,
            
            # 窗口设置
            "window_docking_location": 1,
            "window_docking_offset_x": 0,
            "window_docking_offset_y": 0,
            "window_docking_monitor_index": 0,
            "window_layer": 1,
            "is_mouse_clicking_enabled": False,
            "hide_on_fullscreen": False,
            "hide_on_max_window": False,
            
            # 通知设置
            "is_notification_enabled": True,
            "notification_providers_enable_states": {},
            "notification_providers_priority": [],
            "notification_providers_settings": {},
            
            # 组件设置
            "current_component_config": "Default",
            "components": [],
            
            # 更新设置
            "update_mode": 3,
            "auto_install_update_next_startup": True,
            "selected_channel": "https://install.appcenter.ms/api/v0.1/apps/hellowrc/classisland/distribution_groups/public",
            
            # 调试设置
            "is_debug_enabled": False,
            "is_debug_options_enabled": False,
            "is_main_window_debug_enabled": False,
            
            # 其他设置
            "is_reporting_enabled": True,
            "is_fallback_mode_enabled": True,
            "is_sentry_enabled": True,
            "is_auto_backup_enabled": True,
            "auto_backup_limit": 16,
            "auto_backup_interval_days": 7,
            "is_plugin_market_warning_visible": True,
            "is_theme_warning_visible": True,
        }
    
    def load_settings(self) -> bool:
        """
        从文件加载设置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 合并默认设置和已保存的设置
                self._settings.update(loaded_settings)
                logger.info("设置已从文件加载")
                return True
            else:
                # 文件不存在，使用默认设置
                logger.info("设置文件不存在，使用默认设置")
                return True
                
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            return False
    
    def save_settings(self) -> bool:
        """
        保存设置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            self.app_data_path.mkdir(parents=True, exist_ok=True)
            
            # 保存设置到文件
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            
            logger.info("设置已保存到文件")
            return True
            
        except Exception as e:
            logger.error(f"保存设置时出错: {e}")
            return False
    
    def get_setting(self, key: str, default=None) -> Any:
        """
        获取设置值
        
        Args:
            key: 设置键名
            default: 默认值
            
        Returns:
            设置值
        """
        return self._settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        设置设置值
        
        Args:
            key: 设置键名
            value: 设置值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            old_value = self._settings.get(key)
            self._settings[key] = value
            
            # 发送设置变更信号
            if old_value != value:
                self.settings_changed.emit(key)
            
            logger.debug(f"设置 {key} 已更新为 {value}")
            return True
            
        except Exception as e:
            logger.error(f"设置 {key} 时出错: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        获取所有设置
        
        Returns:
            Dict[str, Any]: 所有设置的字典
        """
        return self._settings.copy()
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        self._settings = self._get_default_settings()
        logger.info("设置已重置为默认值")
    
    # 属性访问器 - 为常用设置提供便捷访问
    @property
    def selected_profile(self) -> str:
        """获取选中的档案"""
        return self.get_setting("selected_profile", "Default.json")
    
    @selected_profile.setter
    def selected_profile(self, value: str):
        """设置选中的档案"""
        self.set_setting("selected_profile", value)
    
    @property
    def is_main_window_visible(self) -> bool:
        """获取主窗口是否可见"""
        return self.get_setting("is_main_window_visible", True)
    
    @is_main_window_visible.setter
    def is_main_window_visible(self, value: bool):
        """设置主窗口是否可见"""
        self.set_setting("is_main_window_visible", value)
    
    @property
    def is_welcome_window_showed(self) -> bool:
        """获取欢迎窗口是否已显示"""
        return self.get_setting("is_welcome_window_showed", False)
    
    @is_welcome_window_showed.setter
    def is_welcome_window_showed(self, value: bool):
        """设置欢迎窗口是否已显示"""
        self.set_setting("is_welcome_window_showed", value)
    
    @property
    def theme(self) -> int:
        """获取主题设置"""
        return self.get_setting("theme", 2)
    
    @theme.setter
    def theme(self, value: int):
        """设置主题"""
        self.set_setting("theme", value)
    
    @property
    def window_docking_location(self) -> int:
        """获取窗口停靠位置"""
        return self.get_setting("window_docking_location", 1)
    
    @window_docking_location.setter
    def window_docking_location(self, value: int):
        """设置窗口停靠位置"""
        self.set_setting("window_docking_location", value)
    
    @property
    def is_notification_enabled(self) -> bool:
        """获取通知是否启用"""
        return self.get_setting("is_notification_enabled", True)
    
    @is_notification_enabled.setter
    def is_notification_enabled(self, value: bool):
        """设置通知是否启用"""
        self.set_setting("is_notification_enabled", value)
    
    @property
    def current_component_config(self) -> str:
        """获取当前组件配置"""
        return self.get_setting("current_component_config", "Default")
    
    @current_component_config.setter
    def current_component_config(self, value: str):
        """设置当前组件配置"""
        self.set_setting("current_component_config", value)
