#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 事件总线系统
提供完整的事件驱动架构支持

该模块提供了完整的事件总线功能，包括：
- 事件发布和订阅
- 事件过滤和路由
- 异步事件处理
- 事件历史和重放
- 事件优先级管理
- 错误处理和恢复
"""

import logging
import threading
import asyncio
import uuid
from typing import Dict, List, Any, Callable, Optional, TypeVar, Generic, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, Future
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread

T = TypeVar('T')
EventHandler = Callable[[Any], None]
AsyncEventHandler = Callable[[Any], Any]  # 可以是协程


class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """
    事件数据类
    
    Attributes:
        id: 事件唯一标识
        type: 事件类型
        data: 事件数据
        timestamp: 事件时间戳
        priority: 事件优先级
        source: 事件源
        tags: 事件标签
        metadata: 事件元数据
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    source: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventSubscription:
    """
    事件订阅信息
    
    Attributes:
        id: 订阅唯一标识
        event_type: 事件类型
        handler: 事件处理器
        filter_func: 事件过滤函数
        priority: 处理优先级
        async_handler: 是否为异步处理器
        max_retries: 最大重试次数
        timeout: 处理超时时间（秒）
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    handler: Union[EventHandler, AsyncEventHandler] = None
    filter_func: Optional[Callable[[Event], bool]] = None
    priority: EventPriority = EventPriority.NORMAL
    async_handler: bool = False
    max_retries: int = 3
    timeout: float = 30.0


class EventBus(QObject):
    """
    TimeNest 事件总线
    
    提供完整的事件驱动架构支持，包括同步和异步事件处理。
    
    Attributes:
        subscriptions: 事件订阅字典
        event_history: 事件历史记录
        error_handlers: 错误处理器
        
    Signals:
        event_published: 事件发布信号 (event: Event)
        event_processed: 事件处理完成信号 (event_id: str, success: bool)
        subscription_added: 订阅添加信号 (subscription_id: str)
        subscription_removed: 订阅移除信号 (subscription_id: str)
    """
    
    # Qt信号定义
    event_published = pyqtSignal(object)  # Event
    event_processed = pyqtSignal(str, bool)  # event_id, success
    subscription_added = pyqtSignal(str)  # subscription_id
    subscription_removed = pyqtSignal(str)  # subscription_id
    
    def __init__(self, max_history: int = 10000, max_workers: int = 4):
        """
        初始化事件总线
        
        Args:
            max_history: 最大历史记录数
            max_workers: 最大工作线程数
        """
        super().__init__()
        
        self.logger = logging.getLogger(f'{__name__}.EventBus')
        
        # 订阅管理
        self.subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self._subscription_lock = threading.RLock()
        
        # 事件历史
        self.event_history: deque = deque(maxlen=max_history)
        self._history_lock = threading.RLock()
        
        # 错误处理
        self.error_handlers: List[Callable[[Exception, Event], None]] = []
        
        # 异步处理
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.event_loop = None
        self._async_tasks: List[asyncio.Task] = []
        
        # 统计信息
        self.stats = {
            'events_published': 0,
            'events_processed': 0,
            'events_failed': 0,
            'subscriptions_count': 0
        }
        
        # 性能监控
        self.processing_times: deque = deque(maxlen=1000)
        
        self.logger.info("事件总线初始化完成")
    
    def publish(self, event_type: str, data: Any = None, priority: EventPriority = EventPriority.NORMAL, 
                source: str = "", tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            priority: 事件优先级
            source: 事件源
            tags: 事件标签
            metadata: 事件元数据
            
        Returns:
            事件ID
        """
        try:
            # 创建事件
            event = Event(
                type=event_type,
                data=data,
                priority=priority,
                source=source,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # 记录历史
            with self._history_lock:
                self.event_history.append(event)
            
            # 更新统计
            self.stats['events_published'] = stats.get('events_published', 0) + 1
            
            # 发出Qt信号
            self.event_published.emit(event)
            
            # 处理事件
            self._process_event(event)
            
            self.logger.debug(f"发布事件: {event_type} (ID: {event.id})")
            return event.id
            
        except Exception as e:
            self.logger.error(f"发布事件失败: {event_type} - {e}")
            self._handle_error(e, None)
            raise
    
    def subscribe(self, event_type: str, handler: Union[EventHandler, AsyncEventHandler],
                  filter_func: Optional[Callable[[Event], bool]] = None,
                  priority: EventPriority = EventPriority.NORMAL,
                  async_handler: bool = False, max_retries: int = 3, timeout: float = 30.0) -> str:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理器
            filter_func: 事件过滤函数
            priority: 处理优先级
            async_handler: 是否为异步处理器
            max_retries: 最大重试次数
            timeout: 处理超时时间
            
        Returns:
            订阅ID
        """
        try:
            subscription = EventSubscription(
                event_type=event_type,
                handler=handler,
                filter_func=filter_func,
                priority=priority,
                async_handler=async_handler,
                max_retries=max_retries,
                timeout=timeout
            )
            
            with self._subscription_lock:
                self.subscriptions[event_type].append(subscription)
                # 按优先级排序
                self.subscriptions[event_type].sort(key=lambda s: s.priority.value, reverse=True)
            
            # 更新统计
            self.stats['subscriptions_count'] = stats.get('subscriptions_count', 0) + 1
            
            # 发出信号
            self.subscription_added.emit(subscription.id)
            
            self.logger.debug(f"添加订阅: {event_type} (ID: {subscription.id})")
            return subscription.id
            
        except Exception as e:
            self.logger.error(f"订阅事件失败: {event_type} - {e}")
            raise
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅
        
        Args:
            subscription_id: 订阅ID
            
        Returns:
            是否成功取消订阅
        """
        try:
            with self._subscription_lock:
                for event_type, subscriptions in self.subscriptions.items():
                    for i, subscription in enumerate(subscriptions):
                        if subscription.id == subscription_id:
                            del subscriptions[i]
                            self.stats['subscriptions_count'] = stats.get('subscriptions_count', 0) - 1
                            self.subscription_removed.emit(subscription_id)
                            self.logger.debug(f"移除订阅: {subscription_id}")
                            return True
            
            self.logger.warning(f"未找到订阅: {subscription_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"取消订阅失败: {subscription_id} - {e}")
            return False
    
    def unsubscribe_all(self, event_type: str) -> int:
        """
        取消指定事件类型的所有订阅
        
        Args:
            event_type: 事件类型
            
        Returns:
            取消的订阅数量
        """
        try:
            with self._subscription_lock:
                if event_type in self.subscriptions:
                    count = len(self.subscriptions[event_type])
                    self.subscriptions[event_type].clear()
                    self.stats['subscriptions_count'] = stats.get('subscriptions_count', 0) - count
                    self.logger.debug(f"移除所有订阅: {event_type} ({count}个)")
                    return count
            
            return 0
            
        except Exception as e:
            self.logger.error(f"取消所有订阅失败: {event_type} - {e}")
            return 0
    
    def add_error_handler(self, handler: Callable[[Exception, Event], None]) -> None:
        """
        添加错误处理器
        
        Args:
            handler: 错误处理函数
        """
        self.error_handlers.append(handler)
        self.logger.debug("添加错误处理器")
    
    def get_event_history(self, event_type: str = None, limit: int = None) -> List[Event]:
        """
        获取事件历史
        
        Args:
            event_type: 事件类型过滤
            limit: 限制数量
            
        Returns:
            事件历史列表
        """
        with self._history_lock:
            events = list(self.event_history)
        
        # 过滤事件类型
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        # 限制数量
        if limit:
            events = events[-limit:]
        
        return events
    
    def replay_events(self, event_type: str = None, since: datetime = None) -> int:
        """
        重放事件
        
        Args:
            event_type: 事件类型过滤
            since: 时间过滤
            
        Returns:
            重放的事件数量
        """
        try:
            events = self.get_event_history(event_type)
            
            # 时间过滤
            if since:
                events = [e for e in events if e.timestamp >= since]
            
            # 重放事件
            for event in events:
                self._process_event(event)
            
            self.logger.info(f"重放事件完成: {len(events)}个")
            return len(events)
            
        except Exception as e:
            self.logger.error(f"重放事件失败: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        avg_processing_time = 0.0
        if self.processing_times:
            avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        return {
            **self.stats,
            'average_processing_time_ms': avg_processing_time * 1000,
            'active_subscriptions': sum(len(subs) for subs in self.subscriptions.values()),
            'event_types': list(self.subscriptions.keys()),
            'history_size': len(self.event_history)
        }
    
    def _process_event(self, event: Event) -> None:
        """处理事件"""
        try:
            start_time = datetime.now()
            
            # 获取订阅者
            subscriptions = self.subscriptions.get(event.type, [])
            
            
            if not subscriptions:
                self.logger.debug(f"没有订阅者处理事件: {event.type}")
            
                self.logger.debug(f"没有订阅者处理事件: {event.type}")
                return
            
            # 处理每个订阅
            for subscription in subscriptions:
                try:
                    # 应用过滤器
                    if subscription.filter_func and not subscription.filter_func(event):
                        continue
                    
                    # 异步处理
                    if subscription.async_handler:
                        self._process_async_event(event, subscription)
                    else:
                        self._process_sync_event(event, subscription)
                
                except Exception as e:
                    self.logger.error(f"处理事件订阅失败: {subscription.id} - {e}")
                    self._handle_error(e, event)
                    self.stats['events_failed'] = self.stats.get('events_failed', 0) + 1
            
            # 记录处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_times.append(processing_time)
            
            # 更新统计
            self.stats['events_processed'] = self.stats.get('events_processed', 0) + 1
            
            # 发出处理完成信号
            self.event_processed.emit(event.id, True)
            
        except Exception as e:
            self.logger.error(f"处理事件失败: {event.type} - {e}")
            self._handle_error(e, event)
            self.event_processed.emit(event.id, False)
    
    def _process_sync_event(self, event: Event, subscription: EventSubscription) -> None:
        """处理同步事件"""
        try:
            subscription.handler(event)
        except Exception as e:
            self.logger.error(f"同步事件处理失败: {subscription.id} - {e}")
            raise
    
    def _process_async_event(self, event: Event, subscription: EventSubscription) -> None:
        """处理异步事件"""
        try:
            # 提交到线程池
            future = self.thread_pool.submit(self._run_async_handler, event, subscription)
            
            # 可以添加回调处理结果
            future.add_done_callback(lambda f: self._on_async_complete(f, event, subscription))
            
        except Exception as e:
            self.logger.error(f"异步事件处理失败: {subscription.id} - {e}")
            raise
    
    def _run_async_handler(self, event: Event, subscription: EventSubscription) -> Any:
        """运行异步处理器"""
        try:
            if asyncio.iscoroutinefunction(subscription.handler):
                # 协程处理器:
                # 协程处理器
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(subscription.handler(event))
                finally:
                    loop.close()
            else:
                # 普通函数
                return subscription.handler(event)
                
        except Exception as e:
            self.logger.error(f"运行异步处理器失败: {subscription.id} - {e}")
            raise
    
    def _on_async_complete(self, future: Future, event: Event, subscription: EventSubscription) -> None:
        """异步处理完成回调"""
        try:
            result = future.result()
            self.logger.debug(f"异步事件处理完成: {subscription.id}")
        except Exception as e:
            self.logger.error(f"异步事件处理异常: {subscription.id} - {e}")
            self._handle_error(e, event)
    
    def _handle_error(self, error: Exception, event: Optional[Event]) -> None:
        """处理错误"""
        try:
            for handler in self.error_handlers:
                handler(error, event)
        except Exception as e:
            self.logger.error(f"错误处理器执行失败: {e}")
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 清空订阅
            with self._subscription_lock:
                self.subscriptions.clear()
            
            # 清空历史
            with self._history_lock:
                self.event_history.clear()
            
            # 关闭线程池
            self.thread_pool.shutdown(wait=True)
            
            # 取消异步任务
            for task in self._async_tasks:
                if not task.done():
                    task.cancel()
            
            self.logger.info("事件总线清理完成")
            
        except Exception as e:
            self.logger.error(f"事件总线清理失败: {e}")


# 全局事件总线实例
_global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    return _global_event_bus


def publish_event(event_type: str, data: Any = None, **kwargs) -> str:
    """发布事件到全局事件总线"""
    return _global_event_bus.publish(event_type, data, **kwargs)


def subscribe_event(event_type: str, handler: Union[EventHandler, AsyncEventHandler], **kwargs) -> str:
    """订阅全局事件总线的事件"""
    return _global_event_bus.subscribe(event_type, handler, **kwargs)
