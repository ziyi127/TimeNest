import json
import logging
import os
from pathlib import Path
from typing import Dict, Any


class UserPreferences:
    """用户偏好设置管理器"""
    
    def __init__(self, app_name: str = "TimeNest"):
        self.logger = logging.getLogger(__name__)
        self.app_name = app_name
        self.preferences = {}
        self.config_path = self._get_config_path()
        self._load_preferences()
        
    def _get_config_path(self) -> Path:
        """获取配置文件路径"""
        import sys
        # 根据操作系统确定配置文件位置
        if sys.platform == "win32":  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / self.app_name
        elif sys.platform == "darwin":  # macOS
            config_dir = Path.home() / 'Library' / 'Application Support' / self.app_name
        elif sys.platform.startswith("linux"):  # Linux
            config_dir = Path.home() / '.config' / self.app_name
        else:
            # 默认使用用户目录
            config_dir = Path.home() / f'.{self.app_name.lower()}'
            
        return config_dir / 'preferences.json'
        
    def _load_preferences(self):
        """从文件加载偏好设置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
                self.logger.info(f"已从 {self.config_path} 加载偏好设置")
            else:
                # 创建默认偏好设置
                self._set_default_preferences()
                self._save_preferences()
                self.logger.info("创建默认偏好设置")
        except Exception as e:
            self.logger.error(f"加载偏好设置失败: {e}")
            # 创建默认设置
            self._set_default_preferences()
            
    def _set_default_preferences(self):
        """设置默认偏好设置"""
        self.preferences = {
            'theme': 'dark',  # 'dark', 'light', 'auto'
            'window_position': {'x': 0, 'y': 0},
            'window_size': {'width': 600, 'height': 40},
            'auto_update': True,
            'show_notifications': True,
            'language': 'zh-CN',
            'last_used_profile': '默认档案'
        }
        
    def _save_preferences(self):
        """保存偏好设置到文件"""
        try:
            # 确保配置目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存设置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"偏好设置已保存到 {self.config_path}")
        except Exception as e:
            self.logger.error(f"保存偏好设置失败: {e}")
            
    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取偏好设置值"""
        return self.preferences.get(key, default)
        
    def set_preference(self, key: str, value: Any):
        """设置偏好设置值"""
        self.preferences[key] = value
        self._save_preferences()
        
    def get_all_preferences(self) -> Dict[str, Any]:
        """获取所有偏好设置"""
        return self.preferences.copy()
        
    def reset_to_defaults(self):
        """重置为默认设置"""
        self._set_default_preferences()
        self._save_preferences()
        self.logger.info("偏好设置已重置为默认值")
        
    def update_window_position(self, x: int, y: int):
        """更新窗口位置"""
        self.preferences['window_position'] = {'x': x, 'y': y}
        self._save_preferences()
        
    def update_window_size(self, width: int, height: int):
        """更新窗口大小"""
        self.preferences['window_size'] = {'width': width, 'height': height}
        self._save_preferences()
        
    def is_dark_theme(self) -> bool:
        """检查是否为深色主题"""
        theme = self.preferences.get('theme', 'dark')
        return theme in ['dark', 'auto']
        
    def is_light_theme(self) -> bool:
        """检查是否为浅色主题"""
        theme = self.preferences.get('theme', 'dark')
        return theme == 'light'


# 创建全局用户偏好实例
user_preferences = UserPreferences()
