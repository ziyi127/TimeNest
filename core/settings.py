# TimeNest 设置管理类
# 完整重构自Classisland的Settings类

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class TimeNestSettings(QObject):
    """TimeNest应用设置类"""

    # 设置变更信号
    settings_changed = Signal(str)

    def __init__(self, app_data_path: Path) -> None:
        """
        初始化设置管理器

        Args:
            app_data_path: 应用数据目录路径
        """
        super().__init__()
        self.app_data_path = app_data_path
        self.settings_file = app_data_path / "settings.json"
        self._settings: Dict[str, Any] = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """
        从文件加载设置

        Returns:
            设置字典
        """
        if not self.settings_file.exists():
            # 如果设置文件不存在，创建默认设置
            default_settings = self._get_default_settings()
            self._save_settings(default_settings)
            return default_settings

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                # 确保所有默认设置都存在
                default_settings = self._get_default_settings()
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            logger.error("加载设置时出错: %s", e)
            # 返回默认设置
            return self._get_default_settings()

    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        保存设置到文件

        Args:
            settings: 要保存的设置字典

        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True

        except Exception as e:
            logger.error("保存设置时出错: %s", e)
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
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
        设置值

        Args:
            key: 设置键名
            value: 设置值

        Returns:
            是否设置成功
        """
        try:
            old_value = self._settings.get(key)
            self._settings[key] = value

            # 保存到文件
            if not self._save_settings(self._settings):
                return False

            # 发送设置变更信号
            self.settings_changed.emit(key)

            # 记录日志（避免记录敏感信息）
            if key not in ["password", "token"]:
                logger.debug(f"设置变更: {key} = {value} (之前: {old_value})")

            return True
        except Exception as e:
            logger.error("设置值时出错: %s", e)
            return False

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        获取默认设置

        Returns:
            默认设置字典
        """
        return {
            "selected_profile": "Default.json",
            "is_main_window_visible": True,
            "is_welcome_window_showed": False,
            "theme": 2,  # 0:浅色 1:深色 2:系统默认
            "window_docking_location": 1,  # 0:左上 1:右上 2:左下 3:右下
            "is_notification_enabled": True,
            "current_component_config": "Default",
            "last_updated": datetime.now().isoformat(),
        }

    def get_all_settings(self) -> Dict[str, Any]:
        """
        获取所有设置的副本

        Returns:
            所有设置的字典
        """
        return self._settings.copy()

    def reset_to_defaults(self) -> None:
        """重置为默认设置"""
        self._settings = self._get_default_settings()
        logger.info("设置已重置为默认值")

    # 属性访问器 - 为常用设置提供便捷访问
    @property
    def selected_profile(self) -> str:
        """获取选中的档案"""
        return self.get_setting("selected_profile", "Default.json")

    @selected_profile.setter
    def selected_profile(self, value: str) -> None:
        """设置选中的档案"""
        self.set_setting("selected_profile", value)

    @property
    def is_main_window_visible(self) -> bool:
        """获取主窗口是否可见"""
        return self.get_setting("is_main_window_visible", True)

    @is_main_window_visible.setter
    def is_main_window_visible(self, value: bool) -> None:
        """设置主窗口是否可见"""
        self.set_setting("is_main_window_visible", value)

    @property
    def is_welcome_window_showed(self) -> bool:
        """获取欢迎窗口是否已显示"""
        return self.get_setting("is_welcome_window_showed", False)

    @is_welcome_window_showed.setter
    def is_welcome_window_showed(self, value: bool) -> None:
        """设置欢迎窗口是否已显示"""
        self.set_setting("is_welcome_window_showed", value)

    @property
    def theme(self) -> int:
        """获取主题设置"""
        return self.get_setting("theme", 2)

    @theme.setter
    def theme(self, value: int) -> None:
        """设置主题"""
        self.set_setting("theme", value)

    @property
    def window_docking_location(self) -> int:
        """获取窗口停靠位置"""
        return self.get_setting("window_docking_location", 1)

    @window_docking_location.setter
    def window_docking_location(self, value: int) -> None:
        """设置窗口停靠位置"""
        self.set_setting("window_docking_location", value)

    @property
    def is_notification_enabled(self) -> bool:
        """获取通知是否启用"""
        return self.get_setting("is_notification_enabled", True)

    @is_notification_enabled.setter
    def is_notification_enabled(self, value: bool) -> None:
        """设置通知是否启用"""
        self.set_setting("is_notification_enabled", value)

    @property
    def current_component_config(self) -> str:
        """获取当前组件配置"""
        return self.get_setting("current_component_config", "Default")

    @current_component_config.setter
    def current_component_config(self, value: str) -> None:
        """设置当前组件配置"""
        self.set_setting("current_component_config", value)
