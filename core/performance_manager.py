#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 性能管理器
负责应用性能监控、内存管理、缓存策略等功能

该模块提供了完整的性能管理功能，包括：
- 内存使用监控和优化
- 智能缓存管理
- 性能指标收集
- 资源使用统计
- 性能瓶颈检测
- 自动优化建议
"""

import logging
import psutil
import gc
import threading
import time
from typing import Dict, Any, Optional, List, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from weakref import WeakValueDictionary
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread

T = TypeVar('T')


@dataclass
class PerformanceMetrics:
    """
    性能指标数据类
    
    Attributes:
        timestamp: 时间戳
        cpu_percent: CPU使用率
        memory_percent: 内存使用率
        memory_mb: 内存使用量(MB)
        cache_hit_rate: 缓存命中率
        active_threads: 活跃线程数
        response_time: 响应时间(ms)
        error_count: 错误计数
    """
    timestamp: datetime
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    cache_hit_rate: float = 0.0
    active_threads: int = 0
    response_time: float = 0.0
    error_count: int = 0


class LRUCache(Generic[T]):
    """
    LRU缓存实现
    
    线程安全的最近最少使用缓存，支持自动过期和内存限制。
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存过期时间（秒），None表示不过期
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, T] = {}
        self._access_times: Dict[str, datetime] = {}
        self._creation_times: Dict[str, datetime] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        with self._lock:
            if key in self._cache:
                # 检查是否过期
                if self._is_expired(key):
                    self._remove_key(key)
                    self._misses += 1
                    return default
                
                # 更新访问时间
                self._access_times[key] = datetime.now()
                self._hits += 1
                return self._cache[key]
            
            self._misses += 1
            return default
    
    def put(self, key: str, value: T) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        with self._lock:
            now = datetime.now()
            
            # 如果键已存在，更新值和时间
            if key in self._cache:
                self._cache[key] = value
                self._access_times[key] = now
                self._creation_times[key] = now
                return
            
            # 检查是否需要清理空间
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # 添加新条目
            self._cache[key] = value
            self._access_times[key] = now
            self._creation_times[key] = now
    
    def remove(self, key: str) -> bool:
        """
        移除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功移除
        """
        with self._lock:
            if key in self._cache:
                self._remove_key(key)
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._creation_times.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'memory_usage_mb': self._estimate_memory_usage()
            }
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存条目是否过期"""
        if self.ttl_seconds is None:
            return False
        
        creation_time = self._creation_times.get(key)
        if creation_time is None:
            return True
        
        return (datetime.now() - creation_time).total_seconds() > self.ttl_seconds
    
    def _evict_lru(self) -> None:
        """移除最近最少使用的条目"""
        if not self._access_times:
            return
        
        # 找到最久未访问的键
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove_key(lru_key)
    
    def _remove_key(self, key: str) -> None:
        """移除指定键的所有相关数据"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._creation_times.pop(key, None)
    
    def _estimate_memory_usage(self) -> float:
        """估算缓存内存使用量（MB）"""
        try:
            import sys
            total_size = 0
            for key, value in self._cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
            return total_size / (1024 * 1024)  # 转换为MB
        except Exception:
            return 0.0


class PerformanceMonitor(QThread):
    """
    性能监控线程
    
    定期收集系统性能指标，检测性能问题。
    """
    
    metrics_updated = pyqtSignal(object)  # PerformanceMetrics
    performance_warning = pyqtSignal(str, float)  # 警告类型, 数值
    
    def __init__(self, interval_seconds: int = 5):
        """
        初始化性能监控器
        
        Args:
            interval_seconds: 监控间隔（秒）
        """
        super().__init__()
        self.interval_seconds = interval_seconds
        self.running = False
        self.logger = logging.getLogger(f'{__name__}.PerformanceMonitor')
        
        # 性能阈值
        self.cpu_threshold = 80.0  # CPU使用率阈值
        self.memory_threshold = 85.0  # 内存使用率阈值
        self.response_time_threshold = 1000.0  # 响应时间阈值(ms)
        
        # 历史数据
        self.metrics_history: deque = deque(maxlen=1000)
        
    def run(self) -> None:
        """运行性能监控"""
        self.running = True
        self.logger.info("性能监控开始")
        
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self.metrics_updated.emit(metrics)
                
                # 检查性能警告
                self._check_performance_warnings(metrics)
                
                time.sleep(self.interval_seconds)
                
            except Exception as e:
                self.logger.error(f"性能监控错误: {e}")
                time.sleep(self.interval_seconds)
        
        self.logger.info("性能监控结束")
    
    def stop(self) -> None:
        """停止性能监控"""
        self.running = False
        self.wait()
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        try:
            # 获取当前进程
            process = psutil.Process()
            
            # 收集系统指标
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            memory_mb = memory_info.rss / (1024 * 1024)  # 转换为MB
            
            # 线程数
            active_threads = threading.active_count()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_mb,
                active_threads=active_threads
            )
            
        except Exception as e:
            self.logger.error(f"收集性能指标失败: {e}")
            return PerformanceMetrics(timestamp=datetime.now())
    
    def _check_performance_warnings(self, metrics: PerformanceMetrics) -> None:
        """检查性能警告"""
        if metrics.cpu_percent > self.cpu_threshold:
            self.performance_warning.emit("high_cpu", metrics.cpu_percent)
        
        if metrics.memory_percent > self.memory_threshold:
            self.performance_warning.emit("high_memory", metrics.memory_percent)
        
        if metrics.response_time > self.response_time_threshold:
            self.performance_warning.emit("slow_response", metrics.response_time)
    
    def get_average_metrics(self, minutes: int = 5) -> Optional[PerformanceMetrics]:
        """
        获取指定时间内的平均性能指标
        
        Args:
            minutes: 时间范围（分钟）
            
        Returns:
            平均性能指标
        """
        if not self.metrics_history:
            return None
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return None
        
        # 计算平均值
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory_mb = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        avg_threads = sum(m.active_threads for m in recent_metrics) / len(recent_metrics)
        avg_response = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            memory_mb=avg_memory_mb,
            active_threads=int(avg_threads),
            response_time=avg_response
        )


class PerformanceManager(QObject):
    """
    TimeNest 性能管理器

    提供完整的性能管理功能，包括监控、缓存、优化等。

    Attributes:
        cache: LRU缓存实例
        monitor: 性能监控器
        optimization_enabled: 是否启用自动优化

    Signals:
        performance_warning: 性能警告信号 (warning_type: str, value: float)
        cache_stats_updated: 缓存统计更新信号 (stats: Dict)
        optimization_applied: 优化应用信号 (optimization_type: str)
    """

    # 信号定义
    performance_warning = pyqtSignal(str, float)  # 警告类型, 数值
    cache_stats_updated = pyqtSignal(dict)  # 缓存统计
    optimization_applied = pyqtSignal(str)  # 优化类型

    def __init__(self, config_manager=None):
        """
        初始化性能管理器

        Args:
            config_manager: 配置管理器实例
        """
        super().__init__()

        self.logger = logging.getLogger(f'{__name__}.PerformanceManager')
        self.config_manager = config_manager

        # 获取配置
        cache_size = 1000
        monitor_interval = 5
        if config_manager:
            perf_config = config_manager.get('performance', {})
            cache_size = perf_config.get('cache_size', 1000)
            monitor_interval = perf_config.get('monitor_interval', 5)

        # 初始化缓存
        self.cache = LRUCache(max_size=cache_size, ttl_seconds=3600)  # 1小时TTL

        # 初始化性能监控器
        self.monitor = PerformanceMonitor(interval_seconds=monitor_interval)
        self.monitor.metrics_updated.connect(self._on_metrics_updated)
        self.monitor.performance_warning.connect(self._on_performance_warning)

        # 优化设置
        self.optimization_enabled = True
        self.last_gc_time = datetime.now()
        self.gc_interval = timedelta(minutes=5)  # 5分钟执行一次垃圾回收

        # 统计定时器
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_cache_stats)
        self.stats_timer.start(30000)  # 30秒更新一次统计

        self.logger.info("性能管理器初始化完成")

    def start_monitoring(self) -> None:
        """开始性能监控"""
        try:
            self.monitor.start()
            self.logger.info("性能监控已启动")
        except Exception as e:
            self.logger.error(f"启动性能监控失败: {e}")

    def stop_monitoring(self) -> None:
        """停止性能监控"""
        try:
            self.monitor.stop()
            self.logger.info("性能监控已停止")
        except Exception as e:
            self.logger.error(f"停止性能监控失败: {e}")

    def get_cache_value(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            缓存值或默认值
        """
        return self.cache.get(key, default)

    def set_cache_value(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        self.cache.put(key, value)

    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.logger.info("缓存已清空")

    def force_garbage_collection(self) -> None:
        """强制执行垃圾回收"""
        try:
            collected = gc.collect()
            self.last_gc_time = datetime.now()
            self.logger.debug(f"垃圾回收完成，回收对象数: {collected}")
            self.optimization_applied.emit("garbage_collection")
        except Exception as e:
            self.logger.error(f"垃圾回收失败: {e}")

    def optimize_memory(self) -> None:
        """内存优化"""
        try:
            # 清理过期缓存
            self._cleanup_expired_cache()

            # 执行垃圾回收
            if datetime.now() - self.last_gc_time > self.gc_interval:
                self.force_garbage_collection()

            self.logger.debug("内存优化完成")
            self.optimization_applied.emit("memory_optimization")

        except Exception as e:
            self.logger.error(f"内存优化失败: {e}")

    def get_performance_report(self) -> Dict[str, Any]:
        """
        获取性能报告

        Returns:
            性能报告字典
        """
        try:
            # 缓存统计
            cache_stats = self.cache.get_stats()

            # 平均性能指标
            avg_metrics = self.monitor.get_average_metrics(minutes=5)

            # 系统信息
            process = psutil.Process()
            system_info = {
                'pid': process.pid,
                'create_time': datetime.fromtimestamp(process.create_time()),
                'num_threads': process.num_threads(),
                'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0,
                'connections': len(process.connections()) if hasattr(process, 'connections') else 0
            }

            return {
                'timestamp': datetime.now().isoformat(),
                'cache_stats': cache_stats,
                'average_metrics': asdict(avg_metrics) if avg_metrics else None,
                'system_info': system_info,
                'optimization_enabled': self.optimization_enabled
            }

        except Exception as e:
            self.logger.error(f"生成性能报告失败: {e}")
            return {'error': str(e)}

    def _on_metrics_updated(self, metrics: PerformanceMetrics) -> None:
        """处理性能指标更新"""
        try:
            # 自动优化检查
            if self.optimization_enabled:
                if metrics.memory_percent > 80:
                    self.optimize_memory()

        except Exception as e:
            self.logger.error(f"处理性能指标更新失败: {e}")

    def _on_performance_warning(self, warning_type: str, value: float) -> None:
        """处理性能警告"""
        try:
            self.logger.warning(f"性能警告: {warning_type} = {value}")
            self.performance_warning.emit(warning_type, value)

            # 自动优化响应
            if self.optimization_enabled:
                if warning_type == "high_memory":
                    self.optimize_memory()
                elif warning_type == "high_cpu":
                    # CPU使用率过高时的优化策略
                    pass

        except Exception as e:
            self.logger.error(f"处理性能警告失败: {e}")

    def _update_cache_stats(self) -> None:
        """更新缓存统计"""
        try:
            stats = self.cache.get_stats()
            self.cache_stats_updated.emit(stats)
        except Exception as e:
            self.logger.error(f"更新缓存统计失败: {e}")

    def _cleanup_expired_cache(self) -> None:
        """清理过期缓存"""
        try:
            # 这里可以添加更复杂的缓存清理逻辑
            # 当前LRUCache已经在get方法中处理过期
            pass
        except Exception as e:
            self.logger.error(f"清理过期缓存失败: {e}")

    def cleanup(self) -> None:
        """清理资源"""
        try:
            self.stop_monitoring()
            self.stats_timer.stop()
            self.clear_cache()
            self.logger.info("性能管理器清理完成")
        except Exception as e:
            self.logger.error(f"性能管理器清理失败: {e}")
