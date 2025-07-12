#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 基础管理器类
提供所有管理器的通用功能和接口
"""

import logging
import threading
from abc import ABC, abstractmethod, ABCMeta
from typing import Any, Dict, Optional, TYPE_CHECKING
from functools import lru_cache
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

if TYPE_CHECKING:
    from core.config_manager import ConfigManager


class QObjectABCMeta(type(QObject), ABCMeta):
    """
    Custom metaclass that combines QObject's metaclass with ABCMeta

    This resolves the metaclass conflict when inheriting from both QObject and ABC.
    The metaclass properly handles both PyQt's signal/slot mechanism and
    abstract base class functionality.
    """
    pass


class BaseManager(QObject, ABC, metaclass=QObjectABCMeta):
    """
    基础管理器类
    
    提供所有管理器的通用功能：
    - 统一的初始化模式
    - 配置管理集成
    - 错误处理
    - 生命周期管理
    - 性能监控
    """
    
    # 通用信号
    manager_initialized = pyqtSignal()
    manager_error = pyqtSignal(str, str)  # error_type, error_message
    config_updated = pyqtSignal(str, dict)  # section, config
    
    def __init__(self, config_manager: 'ConfigManager', manager_name: str = None):
        """
        初始化基础管理器
        
        Args:
            config_manager: 配置管理器实例
            manager_name: 管理器名称，用于日志和配置
        """
        super().__init__()
        
        # 基础属性
        self.manager_name = manager_name or self.__class__.__name__
        self.config_manager = config_manager
        self.logger = logging.getLogger(f'{__name__}.{self.manager_name}')
        
        # 状态管理
        self._initialized = False
        self._running = False
        self._lock = threading.RLock()
        
        # 性能监控
        self._operation_count = 0
        self._error_count = 0
        self._last_operation_time = None
        
        # 配置缓存（优化版本）
        self._config_cache: Dict[str, Any] = {}
        self._cache_timeout = 300  # 5分钟缓存超时
        self._cache_hits = 0
        self._cache_misses = 0
        
        # 清理定时器
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._periodic_cleanup)
        self._cleanup_timer.start(60000)  # 每分钟清理一次
        
        # 连接配置变更信号
        if self.config_manager:
            self.config_manager.config_changed.connect(self._on_config_changed)
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化管理器
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理管理器资源"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（带缓存）
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            # 检查缓存
            if key in self._config_cache:
                self._cache_hits += 1
                return self._config_cache[key]

            # 从配置管理器获取
            self._cache_misses += 1
            value = self.config_manager.get_config(key, default)

            # 缓存配置值（限制缓存大小）
            if len(self._config_cache) < 100:
                self._config_cache[key] = value

            return value

        except Exception as e:
            self.logger.error(f"获取配置失败 {key}: {e}")
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            # 更新配置管理器
            self.config_manager.set_config(key, value)
            
            # 更新缓存
            self._config_cache[key] = value
            
            return True
            
        except Exception as e:
            self.logger.error(f"设置配置失败 {key}: {e}")
            return False
    
    def _on_config_changed(self, section: str, config: dict) -> None:
        """
        处理配置变更
        
        Args:
            section: 配置节
            config: 配置数据
        """
        try:
            # 清理相关缓存
            keys_to_remove = [key for key in self._config_cache.keys() 
                             if key.startswith(f"{section}.")]
            for key in keys_to_remove:
                del self._config_cache[key]
            
            # 发出配置更新信号
            self.config_updated.emit(section, config)
            
            # 调用子类处理方法
            self.on_config_changed(section, config)
            
        except Exception as e:
            self.logger.error(f"处理配置变更失败: {e}")
            self._handle_error("config_change", str(e))
    
    def on_config_changed(self, section: str, config: dict) -> None:
        """
        子类可重写的配置变更处理方法
        
        Args:
            section: 配置节
            config: 配置数据
        """
        pass
    
    def _handle_error(self, error_type: str, error_message: str) -> None:
        """
        统一错误处理
        
        Args:
            error_type: 错误类型
            error_message: 错误消息
        """
        self._error_count += 1
        self.logger.error(f"{error_type}: {error_message}")
        self.manager_error.emit(error_type, error_message)
    
    def _periodic_cleanup(self) -> None:
        """定期清理任务"""
        try:
            # 清理过期缓存
            self._cleanup_cache()
            
            # 调用子类清理方法
            self.periodic_cleanup()
            
        except Exception as e:
            self.logger.error(f"定期清理失败: {e}")
    
    def _cleanup_cache(self) -> None:
        """清理过期缓存（优化版本）"""
        if len(self._config_cache) > 100:  # 缓存过多时清理
            # 保留最近使用的50个配置项
            keys_to_remove = list(self._config_cache.keys())[:-50]
            for key in keys_to_remove:
                self._config_cache.pop(key, None)
    
    def periodic_cleanup(self) -> None:
        """子类可重写的定期清理方法"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取管理器统计信息
        
        Returns:
            统计信息字典
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'manager_name': self.manager_name,
            'initialized': self._initialized,
            'running': self._running,
            'operation_count': self._operation_count,
            'error_count': self._error_count,
            'cache_size': len(self._config_cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': f"{hit_rate:.1f}%"
        }
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running
    
    def start(self) -> bool:
        """启动管理器"""
        with self._lock:
            if not self._initialized:
                if not self.initialize():
                    return False
                self._initialized = True
                self.manager_initialized.emit()
            
            self._running = True
            return True
    
    def stop(self) -> None:
        """停止管理器"""
        with self._lock:
            self._running = False
            self.cleanup()
            
            # 停止清理定时器
            if self._cleanup_timer:
                self._cleanup_timer.stop()


class CachedProperty:
    """
    缓存属性装饰器
    用于缓存计算结果，提高性能
    """
    
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.__doc__ = func.__doc__
    
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        
        # 检查是否已缓存
        cache_name = f'_cached_{self.name}'
        if hasattr(obj, cache_name):
            return getattr(obj, cache_name)
        
        # 计算并缓存结果
        result = self.func(obj)
        setattr(obj, cache_name, result)
        return result
    
    def __set__(self, obj, value):
        # 允许设置缓存值
        cache_name = f'_cached_{self.name}'
        setattr(obj, cache_name, value)
    
    def __delete__(self, obj):
        # 清除缓存
        cache_name = f'_cached_{self.name}'
        if hasattr(obj, cache_name):
            delattr(obj, cache_name)


def clear_cached_property(obj, property_name: str):
    """
    清除指定的缓存属性
    
    Args:
        obj: 对象实例
        property_name: 属性名称
    """
    cache_name = f'_cached_{property_name}'
    if hasattr(obj, cache_name):
        delattr(obj, cache_name)


def clear_all_cached_properties(obj):
    """
    清除对象的所有缓存属性
    
    Args:
        obj: 对象实例
    """
    cached_attrs = [attr for attr in dir(obj) if attr.startswith('_cached_')]
    for attr in cached_attrs:
        delattr(obj, attr)
