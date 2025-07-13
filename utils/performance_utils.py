#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 性能优化工具
提供常用的性能优化装饰器和工具函数
"""

import time
import functools
import threading
import weakref
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from collections import OrderedDict

F = TypeVar('F', bound=Callable[..., Any])


class LRUCache:
    """
    简单的LRU缓存实现
    线程安全，支持TTL
    """
    
    def __init__(self, max_size: int = 128, ttl: Optional[float] = None):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存大小
            ttl: 生存时间（秒），None表示永不过期
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[Any, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return default
            
            # 检查TTL
            if self.ttl and key in self._timestamps:
                if time.time() - self._timestamps[key] > self.ttl:
                    self._remove(key)
                    return default
            
            # 移动到末尾（最近使用）
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
    
    def put(self, key: Any, value: Any) -> None:
        """设置缓存值"""
        with self._lock:
            if key in self._cache:
                # 更新现有值
                self._cache.pop(key)
            elif len(self._cache) >= self.max_size:
                # 移除最久未使用的项
                oldest_key = next(iter(self._cache))
                self._remove(oldest_key)
            
            self._cache[key] = value
            if self.ttl:
                self._timestamps[key] = time.time()
    
    def _remove(self, key: Any) -> None:
        """移除缓存项"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


def lru_cache(max_size: int = 128, ttl: Optional[float] = None):
    """
    LRU缓存装饰器
    
    Args:
        max_size: 最大缓存大小
        ttl: 生存时间（秒）
    """
    def decorator(func: F) -> F:
        cache = LRUCache(max_size, ttl)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存键
            key = (args, tuple(sorted(kwargs.items())))
            
            # 尝试从缓存获取
            result = cache.get(key)
            if result is not None:
                return result
            
            # 计算结果并缓存
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result
        
        # 添加缓存管理方法
        wrapper.cache_clear = cache.clear
        wrapper.cache_info = lambda: {
            'size': cache.size(),
            'max_size': max_size,
            'ttl': ttl
        }
        
        return wrapper
    
    return decorator


def timing_decorator(threshold_ms: float = 100.0):
    """
    性能计时装饰器
    记录函数执行时间

    Args:
        threshold_ms: 警告阈值（毫秒），超过此时间会记录警告
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # 转换为毫秒

                # 只在超过阈值时记录
                if execution_time > threshold_ms:
                    import logging
                    logger = logging.getLogger(__name__)
                    func_name = f"{func.__module__}.{func.__qualname__}"
                    logger.warning(f"慢函数调用: {func_name} 耗时 {execution_time:.2f}ms")

        return wrapper

    # 支持直接使用 @timing_decorator 或 @timing_decorator()
    if callable(threshold_ms):
        func = threshold_ms
        threshold_ms = 100.0
        return decorator(func)

    return decorator


def debounce(wait: float):
    """
    防抖装饰器
    在指定时间内多次调用只执行最后一次
    
    Args:
        wait: 等待时间（秒）
    """
    def decorator(func: F) -> F:
        timer = None
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            def call_func():
                func(*args, **kwargs)
            
            
            if timer and hasattr(timer, "cancel"):
                timer.cancel()
            
            timer = threading.Timer(wait, call_func)
            timer.start()
        
        return wrapper
    
    return decorator


def throttle(interval: float):
    """
    节流装饰器
    限制函数在指定时间间隔内最多执行一次
    
    Args:
        interval: 时间间隔（秒）
    """
    def decorator(func: F) -> F:
        last_called = [0.0]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= interval:
                last_called[0] = now
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class ObjectPool:
    """
    对象池，用于重用昂贵的对象
    """
    
    def __init__(self, factory: Callable[[], Any], max_size: int = 10):
        """
        初始化对象池
        
        Args:
            factory: 对象工厂函数
            max_size: 最大池大小
        """
        self.factory = factory
        self.max_size = max_size
        self._pool = []
        self._lock = threading.Lock()
    
    def acquire(self) -> Any:
        """获取对象"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            else:
                return self.factory()
    
    def release(self, obj: Any) -> None:
        """释放对象回池中"""
        with self._lock:
            if len(self._pool) < self.max_size:
                # 重置对象状态（如果需要）
                if hasattr(obj, 'reset'):
                    obj.reset()
                self._pool.append(obj)
    
    def clear(self) -> None:
        """清空对象池"""
        with self._lock:
            self._pool.clear()


class WeakMethodRef:
    """
    弱引用方法包装器
    避免回调函数导致的循环引用
    """
    
    def __init__(self, method):
        self.obj_ref = weakref.ref(method.__self__)
        self.func_name = method.__func__.__name__
    
    def __call__(self, *args, **kwargs):
        obj = self.obj_ref()
        if obj is not None:
            return getattr(obj, self.func_name)(*args, **kwargs)


def weak_method_ref(method):
    """
    创建弱引用方法
    
    Args:
        method: 要包装的方法
        
    Returns:
        弱引用方法包装器
    """
    return WeakMethodRef(method)


def batch_processor(batch_size: int = 100, flush_interval: float = 1.0):
    """
    批处理装饰器
    将多个调用批量处理以提高性能

    Args:
        batch_size: 批处理大小
        flush_interval: 强制刷新间隔（秒）
    """
    def decorator(func: F) -> F:
        batch = []
        last_flush = time.time()
        lock = threading.Lock()

        def flush_batch():
            nonlocal batch, last_flush
            if batch:
                # 批量处理
                try:
                    func(batch.copy())
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"批处理失败: {e}")
                finally:
                    batch.clear()
                    last_flush = time.time()

        @functools.wraps(func)
        def wrapper(item):
            nonlocal batch, last_flush

            with lock:
                batch.append(item)

                # 检查是否需要刷新
                should_flush = (
                    len(batch) >= batch_size or
                    time.time() - last_flush >= flush_interval
                )


                if should_flush:
                    flush_batch()

                    flush_batch()

        # 添加手动刷新方法和状态查询
        wrapper.flush = lambda: flush_batch()
        wrapper.get_batch_size = lambda: len(batch)
        wrapper.clear_batch = lambda: batch.clear()

        return wrapper

    return decorator


def memory_efficient_generator(iterable, chunk_size: int = 1000):
    """
    内存高效的生成器
    分块处理大型可迭代对象
    
    Args:
        iterable: 可迭代对象
        chunk_size: 块大小
        
    Yields:
        数据块
    """
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    
    if chunk:
        yield chunk
