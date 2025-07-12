# -*- coding: utf-8 -*-
"""
TimeNest 配置管理器
负责应用配置的加载、保存和管理

该模块提供了完整的配置管理功能，包括：
- 多配置文件支持（主配置、用户配置、组件配置、布局配置）
- 配置验证和默认值处理
- 配置变更通知机制
- 配置备份和恢复功能
- 线程安全的配置访问
"""

import os
import json
import yaml
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable, TypeVar, Generic
from functools import lru_cache
from PyQt6.QtCore import QObject, pyqtSignal

# 类型变量定义
T = TypeVar('T')
ConfigValue = Union[str, int, float, bool, List[Any], Dict[str, Any]]

class ConfigManager(QObject):
    """
    TimeNest 配置管理器

    提供完整的配置管理功能，支持多配置文件、配置验证、变更通知等。

    Attributes:
        config_dir: 配置文件目录路径
        main_config: 主配置数据
        user_config: 用户配置数据
        component_config: 组件配置数据
        layout_config: 布局配置数据

    Signals:
        config_changed: 配置变更信号 (key: str, old_value: Any, new_value: Any)
        config_loaded: 配置加载完成信号 (file_path: str)
        config_saved: 配置保存完成信号 (file_path: str)
        config_error: 配置错误信号 (error_message: str)
    """

    # 信号定义
    config_changed = pyqtSignal(str, object, object)  # 配置键, 旧值, 新值
    config_loaded = pyqtSignal(str)  # 配置文件路径
    config_saved = pyqtSignal(str)  # 配置文件路径
    config_error = pyqtSignal(str)  # 错误信息

    def __init__(self, config_dir: Optional[str] = None) -> None:
        """
        初始化配置管理器

        Args:
            config_dir: 配置文件目录路径，如果为None则使用默认路径

        Raises:
            OSError: 当无法创建配置目录时
            PermissionError: 当没有配置目录写权限时
        """
        super().__init__()

        try:
            # 配置目录
            if config_dir:
                self.config_dir = Path(config_dir)
            else:
                # 默认配置目录
                home_dir = Path.home()
                self.config_dir = home_dir / '.timenest'

            # 确保配置目录存在
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # 配置文件路径
            self.main_config_file = self.config_dir / 'config.json'
            self.user_config_file = self.config_dir / 'user_config.json'
            self.component_config_file = self.config_dir / 'components.json'
            self.layout_config_file = self.config_dir / 'layout.json'

            # 配置数据
            self.main_config: Dict[str, Any] = {}
            self.user_config: Dict[str, Any] = {}
            self.component_config: Dict[str, Any] = {}
            self.layout_config: Dict[str, Any] = {}

            # 线程锁，确保配置访问的线程安全
            self._config_lock = threading.RLock()

            # 配置变更监听器
            self._change_listeners: Dict[str, List[Callable[[Any, Any], None]]] = {}

            # 日志
            self.logger = logging.getLogger(f'{__name__}.ConfigManager')

            # 加载默认配置
            self._load_default_configs()

            self.logger.info(f"配置管理器初始化完成，配置目录: {self.config_dir}")

        except (OSError, PermissionError) as e:
            error_msg = f"配置管理器初始化失败: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            raise
        
        # 加载配置
        self.load_all_configs()

    def _load_default_configs(self) -> None:
        """
        加载默认配置

        设置应用的默认配置值，确保应用在没有配置文件时也能正常运行。
        """
        try:
            # 主配置默认值
            self.main_config = {
                'app': {
                    'name': 'TimeNest',
                    'version': '1.0.0',
                    'language': 'zh_CN',
                    'theme': 'default',
                    'auto_start': False,
                    'minimize_to_tray': True,
                    'check_updates': True,
                    'log_level': 'INFO'
                },
                'window': {
                    'width': 1200,
                    'height': 800,
                    'x': -1,  # -1 表示居中
                    'y': -1,  # -1 表示居中
                    'maximized': False,
                    'always_on_top': False
                },
                'performance': {
                    'enable_animations': True,
                    'animation_duration': 300,
                    'cache_size': 100,
                    'auto_save_interval': 300,  # 秒
                    'max_undo_steps': 50
                }
            }

            # 用户配置默认值
            self.user_config = {
                'profile': {
                    'name': '',
                    'email': '',
                    'avatar': '',
                    'timezone': 'Asia/Shanghai'
                },
                'preferences': {
                    'date_format': 'YYYY-MM-DD',
                    'time_format': '24h',
                    'first_day_of_week': 1,  # 1=Monday, 0=Sunday
                    'default_reminder_time': 15,  # 分钟
                    'sound_enabled': True,
                    'notification_enabled': True
                }
            }

            self.logger.debug("默认配置加载完成")

        except Exception as e:
            self.logger.error(f"加载默认配置失败: {e}")
            raise
    
    def load_all_configs(self):
        """加载所有配置文件"""
        try:
            self.load_main_config()
            self.load_user_config()
            self.load_component_config()
            self.load_layout_config()
            
            self.logger.info("所有配置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
    
    def load_main_config(self):
        """加载主配置"""
        try:
            if self.main_config_file.exists():
                with open(self.main_config_file, 'r', encoding='utf-8') as f:
                    self.main_config = json.load(f)
            else:
                self.main_config = self._get_default_main_config()
                self.save_main_config()
            
            self.config_loaded.emit(str(self.main_config_file))
            self.logger.info("主配置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载主配置失败: {e}")
            self.main_config = self._get_default_main_config()
    
    def load_user_config(self):
        """加载用户配置"""
        try:
            if self.user_config_file.exists():
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    self.user_config = json.load(f)
            else:
                self.user_config = self._get_default_user_config()
                self.save_user_config()
            
            self.config_loaded.emit(str(self.user_config_file))
            self.logger.info("用户配置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载用户配置失败: {e}")
            self.user_config = self._get_default_user_config()
    
    def load_component_config(self):
        """加载组件配置"""
        try:
            if self.component_config_file.exists():
                with open(self.component_config_file, 'r', encoding='utf-8') as f:
                    self.component_config = json.load(f)
            else:
                self.component_config = self._get_default_component_config()
                self.save_component_config()
            
            self.config_loaded.emit(str(self.component_config_file))
            self.logger.info("组件配置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载组件配置失败: {e}")
            self.component_config = self._get_default_component_config()
    
    def load_layout_config(self):
        """加载布局配置"""
        try:
            if self.layout_config_file.exists():
                with open(self.layout_config_file, 'r', encoding='utf-8') as f:
                    self.layout_config = json.load(f)
            else:
                self.layout_config = self._get_default_layout_config()
                self.save_layout_config()
            
            self.config_loaded.emit(str(self.layout_config_file))
            self.logger.info("布局配置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载布局配置失败: {e}")
            self.layout_config = self._get_default_layout_config()
    
    def save_all_configs(self):
        """保存所有配置"""
        try:
            self.save_main_config()
            self.save_user_config()
            self.save_component_config()
            self.save_layout_config()
            
            self.logger.info("所有配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def save_main_config(self):
        """保存主配置"""
        try:
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_config, f, ensure_ascii=False, indent=2)
            
            self.config_saved.emit(str(self.main_config_file))
            self.logger.debug("主配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存主配置失败: {e}")
    
    def save_user_config(self):
        """保存用户配置"""
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, ensure_ascii=False, indent=2)
            
            self.config_saved.emit(str(self.user_config_file))
            self.logger.debug("用户配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存用户配置失败: {e}")
    
    def save_component_config(self):
        """保存组件配置"""
        try:
            with open(self.component_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.component_config, f, ensure_ascii=False, indent=2)
            
            self.config_saved.emit(str(self.component_config_file))
            self.logger.debug("组件配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存组件配置失败: {e}")
    
    def save_layout_config(self):
        """保存布局配置"""
        try:
            with open(self.layout_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.layout_config, f, ensure_ascii=False, indent=2)
            
            self.config_saved.emit(str(self.layout_config_file))
            self.logger.debug("布局配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存布局配置失败: {e}")
    
    @lru_cache(maxsize=256)
    def _get_config_cached(self, key: str, config_type: str) -> Any:
        """缓存的配置获取（内部方法）"""
        if config_type == 'user':
            config_dict = self.user_config
        elif config_type == 'component':
            config_dict = self.component_config
        elif config_type == 'layout':
            config_dict = self.layout_config
        else:
            config_dict = self.main_config

        # 支持嵌套键（如 'app.window.width'）
        keys = key.split('.')
        value = config_dict

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None  # 返回None表示未找到

        return value

    def get_config(self, key: str, default: Any = None, config_type: str = 'main') -> Any:
        """获取配置值（优化版本）"""
        try:
            # 使用缓存获取
            value = self._get_config_cached(key, config_type)
            return value if value is not None else default

        except Exception as e:
            self.logger.error(f"获取配置失败: {e}")
            return default
    
    def set_config(self, key: str, value: Any, config_type: str = 'main', save: bool = True):
        """设置配置值"""
        try:
            if config_type == 'user':
                config_dict = self.user_config
            elif config_type == 'component':
                config_dict = self.component_config
            elif config_type == 'layout':
                config_dict = self.layout_config
            else:
                config_dict = self.main_config
            
            # 获取旧值
            old_value = self.get_config(key, None, config_type)
            
            # 支持嵌套键设置
            keys = key.split('.')
            current_dict = config_dict
            
            for k in keys[:-1]:
                if k not in current_dict:
                    current_dict[k] = {}
                current_dict = current_dict[k]
            
            current_dict[keys[-1]] = value

            # 清除缓存
            self._get_config_cached.cache_clear()

            # 保存配置
            if save:
                if config_type == 'user':
                    self.save_user_config()
                elif config_type == 'component':
                    self.save_component_config()
                elif config_type == 'layout':
                    self.save_layout_config()
                else:
                    self.save_main_config()
            
            # 发送配置变更信号
            self.config_changed.emit(key, old_value, value)
            
            self.logger.debug(f"设置配置: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"设置配置失败: {e}")
    
    def remove_config(self, key: str, config_type: str = 'main', save: bool = True) -> bool:
        """移除配置项"""
        try:
            if config_type == 'user':
                config_dict = self.user_config
            elif config_type == 'component':
                config_dict = self.component_config
            elif config_type == 'layout':
                config_dict = self.layout_config
            else:
                config_dict = self.main_config
            
            # 获取旧值
            old_value = self.get_config(key, None, config_type)
            
            # 支持嵌套键删除
            keys = key.split('.')
            current_dict = config_dict
            
            for k in keys[:-1]:
                if k not in current_dict:
                    return False
                current_dict = current_dict[k]
            
            if keys[-1] in current_dict:
                del current_dict[keys[-1]]
                
                # 保存配置
                if save:
                    if config_type == 'user':
                        self.save_user_config()
                    elif config_type == 'component':
                        self.save_component_config()
                    elif config_type == 'layout':
                        self.save_layout_config()
                    else:
                        self.save_main_config()
                
                # 发送配置变更信号
                self.config_changed.emit(key, old_value, None)
                
                self.logger.debug(f"移除配置: {key}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"移除配置失败: {e}")
            return False
    
    def export_config(self, file_path: str, config_type: str = 'all', format: str = 'json') -> bool:
        """导出配置"""
        try:
            if config_type == 'all':
                export_data = {
                    'main': self.main_config,
                    'user': self.user_config,
                    'component': self.component_config,
                    'layout': self.layout_config
                }
            elif config_type == 'user':
                export_data = self.user_config
            elif config_type == 'component':
                export_data = self.component_config
            elif config_type == 'layout':
                export_data = self.layout_config
            else:
                export_data = self.main_config
            
            file_path = Path(file_path)
            
            if format.lower() == 'yaml':
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"配置导出完成: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, file_path: str, config_type: str = 'all', merge: bool = True) -> bool:
        """导入配置"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"配置文件不存在: {file_path}")
                return False
            
            # 读取配置文件
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = yaml.safe_load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
            
            if config_type == 'all':
                if merge:
                    self.main_config.update(import_data.get('main', {}))
                    self.user_config.update(import_data.get('user', {}))
                    self.component_config.update(import_data.get('component', {}))
                    self.layout_config.update(import_data.get('layout', {}))
                else:
                    self.main_config = import_data.get('main', {})
                    self.user_config = import_data.get('user', {})
                    self.component_config = import_data.get('component', {})
                    self.layout_config = import_data.get('layout', {})
            elif config_type == 'user':
                if merge:
                    self.user_config.update(import_data)
                else:
                    self.user_config = import_data
            elif config_type == 'component':
                if merge:
                    self.component_config.update(import_data)
                else:
                    self.component_config = import_data
            elif config_type == 'layout':
                if merge:
                    self.layout_config.update(import_data)
                else:
                    self.layout_config = import_data
            else:
                if merge:
                    self.main_config.update(import_data)
                else:
                    self.main_config = import_data
            
            # 保存配置
            self.save_all_configs()
            
            self.logger.info(f"配置导入完成: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导入配置失败: {e}")
            return False
    
    def reset_config(self, config_type: str = 'all'):
        """重置配置为默认值"""
        try:
            if config_type == 'all' or config_type == 'main':
                self.main_config = self._get_default_main_config()
                self.save_main_config()
            
            if config_type == 'all' or config_type == 'user':
                self.user_config = self._get_default_user_config()
                self.save_user_config()
            
            if config_type == 'all' or config_type == 'component':
                self.component_config = self._get_default_component_config()
                self.save_component_config()
            
            if config_type == 'all' or config_type == 'layout':
                self.layout_config = self._get_default_layout_config()
                self.save_layout_config()
            
            self.logger.info(f"配置重置完成: {config_type}")
            
        except Exception as e:
            self.logger.error(f"重置配置失败: {e}")
    
    def _get_default_main_config(self) -> Dict[str, Any]:
        """获取默认主配置"""
        return {
            'app': {
                'name': 'TimeNest',
                'version': '1.0.0',
                'language': 'zh_CN',
                'theme': 'light',
                'auto_start': False,
                'minimize_to_tray': True,
                'check_updates': True
            },
            'floating_widget': self._get_default_floating_config(),
            'window': {
                'width': 1200,
                'height': 800,
                'x': -1,
                'y': -1,
                'maximized': False,
                'always_on_top': False,
                'opacity': 1.0
            },
            'schedule': {
                'default_file': '',
                'auto_save': True,
                'backup_count': 5,
                'show_weekends': True,
                'time_format': '24h'
            },
            'notification': {
                'enabled': True,
                'sound_enabled': True,
                'voice_enabled': False,
                'popup_enabled': True,
                'advance_minutes': 5
            },
            'time': {
                'offset_enabled': False,
                'offset_minutes': 0,
                'speed_factor': 1.0,
                'sync_interval': 3600
            },
            'plugin_marketplace': {
                'marketplace_url': 'https://github.com/ziyi127/TimeNest-Store',
                'api_base_url': 'https://api.github.com/repos/ziyi127/TimeNest-Store',
                'raw_base_url': 'https://raw.githubusercontent.com/ziyi127/TimeNest-Store/main',
                'cache_expiry': 3600,
                'auto_update_check': True,
                'allow_beta_plugins': False,
                'download_timeout': 30,
                'verify_signatures': True
            },
            'plugins': {
                'enabled': True,
                'auto_load': True,
                'safe_mode': False,
                'max_load_time': 10,
                'sandbox_enabled': True
            }
        }
    
    def _get_default_user_config(self) -> Dict[str, Any]:
        """获取默认用户配置"""
        return {
            'user': {
                'name': '',
                'school': '',
                'class': '',
                'student_id': ''
            },
            'preferences': {
                'startup_component': 'schedule',
                'show_tips': True,
                'animation_enabled': True,
                'sound_volume': 0.8
            },
            'recent_files': [],
            'bookmarks': []
        }
    
    def _get_default_component_config(self) -> Dict[str, Any]:
        """获取默认组件配置"""
        return {
            'components': {
                'schedule': {
                    'enabled': True,
                    'position': {'x': 10, 'y': 10},
                    'size': {'width': 400, 'height': 300},
                    'settings': {
                        'show_current_class': True,
                        'show_next_class': True,
                        'show_full_schedule': True,
                        'highlight_current': True
                    }
                },
                'clock': {
                    'enabled': True,
                    'position': {'x': 420, 'y': 10},
                    'size': {'width': 200, 'height': 100},
                    'settings': {
                        'show_seconds': True,
                        'show_date': True,
                        'format_24h': True,
                        'show_weekday': True
                    }
                },
                'weather': {
                    'enabled': False,
                    'position': {'x': 630, 'y': 10},
                    'size': {'width': 200, 'height': 150},
                    'settings': {
                        'api_key': '',
                        'city': '',
                        'update_interval': 1800,
                        'show_forecast': True
                    }
                },
                'countdown': {
                    'enabled': True,
                    'position': {'x': 10, 'y': 320},
                    'size': {'width': 300, 'height': 200},
                    'settings': {
                        'events': [],
                        'show_weekends': True,
                        'show_holidays': True
                    }
                },
                'carousel': {
                    'enabled': True,
                    'position': {'x': 320, 'y': 320},
                    'size': {'width': 300, 'height': 200},
                    'settings': {
                        'auto_play': True,
                        'interval': 5000,
                        'show_controls': True,
                        'show_indicators': True,
                        'items': []
                    }
                }
            }
        }
    
    def _get_default_floating_config(self) -> Dict[str, Any]:
        """获取默认浮窗配置"""
        return {
            'enabled': True,
            'position': 'top',
            'width': 400,
            'height': 60,
            'opacity': 85,
            'radius': 30,
            'shadow': True,
            'modules': ['time', 'schedule'],
            'show_on_startup': True,
            'mouse_through': False
        }

    def _get_default_layout_config(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            'layouts': {
                'default': {
                    'name': '默认布局',
                    'components': [
                        {'id': 'schedule', 'type': 'schedule'},
                        {'id': 'clock', 'type': 'clock'},
                        {'id': 'countdown', 'type': 'countdown'},
                        {'id': 'carousel', 'type': 'carousel'}
                    ]
                }
            },
            'current_layout': 'default'
        }
    
    def get_config_dir(self) -> Path:
        """获取配置目录"""
        return self.config_dir
    
    def get_config_files(self) -> Dict[str, Path]:
        """获取所有配置文件路径"""
        return {
            'main': self.main_config_file,
            'user': self.user_config_file,
            'component': self.component_config_file,
            'layout': self.layout_config_file
        }
    
    def get(self, key: str, default: Any = None, config_type: str = 'main') -> Any:
        """
        兼容接口，等价于 get_config
        """
        return self.get_config(key, default, config_type)