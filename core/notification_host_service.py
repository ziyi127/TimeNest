#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知主机服务
基于 ClassIsland NotificationHostService 规范实现
"""

import logging
from typing import List, Protocol, Any, Dict
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import asyncio


class INotificationProvider(Protocol):
    """
    通知提供者接口，所有通知提供者需实现 send_notification 方法。
    """
    def send_notification(self, message: str, **kwargs) -> None:
        ...


class IHostedService(ABC):
    """
    托管服务接口（对应.NET的IHostedService）
    """

    @abstractmethod
    async def start_async(self) -> None:
        """启动服务"""
        pass

    @abstractmethod
    async def stop_async(self) -> None:
        """停止服务"""
        pass


class NotificationHostService(QObject, IHostedService):
    """
    通知主机服务（严格遵循 doc/NotificationHostService.md）
    提醒主机服务，实现IHostedService和INotifyPropertyChanged接口
    """

    # 信号定义（对应INotifyPropertyChanged）
    property_changed = pyqtSignal(str, object)  # property_name, new_value
    notification_sent = pyqtSignal(str, dict)  # message, extra kwargs
    service_started = pyqtSignal()
    service_stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.NotificationHostService')
        self._providers: Dict[str, INotificationProvider] = {}
        self._is_running = False
        self._start_time = None

        # 定时器用于服务监控
        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(self._monitor_service)

    @property
    def is_running(self) -> bool:
        """服务是否正在运行"""
        return self._is_running

    @property
    def provider_count(self) -> int:
        """注册的提供者数量"""
        return len(self._providers)

    def register_notification_provider(self, provider: INotificationProvider) -> None:
        """
        注册提醒服务（严格遵循文档规范）

        Args:
            provider: 通知提供者实例
        """
        try:
            provider_id = f"provider_{id(provider)}"
            if provider_id not in self._providers:
                self._providers[provider_id] = provider
                self.logger.info(f"已注册通知提供者: {provider.__class__.__name__} (ID: {provider_id})")

                # 发送属性变化信号
                self.property_changed.emit("provider_count", self.provider_count)
            else:
                self.logger.warning(f"通知提供者已存在: {provider_id}")

        except Exception as e:
            self.logger.error(f"注册通知提供者失败: {e}", exc_info=True)

    def unregister_notification_provider(self, provider: INotificationProvider) -> None:
        """
        注销通知服务提供者

        Args:
            provider: 要注销的通知提供者实例
        """
        try:
            provider_id = f"provider_{id(provider)}"
            if provider_id in self._providers:
                del self._providers[provider_id]
                self.logger.info(f"已注销通知提供者: {provider.__class__.__name__} (ID: {provider_id})")

                # 发送属性变化信号
                self.property_changed.emit("provider_count", self.provider_count)
            else:
                self.logger.warning(f"通知提供者不存在: {provider_id}")

        except Exception as e:
            self.logger.error(f"注销通知提供者失败: {e}", exc_info=True)

    def send_notification(self, message: str, **kwargs) -> None:
        """
        向所有已注册的通知提供者分发通知

        Args:
            message: 通知消息
            **kwargs: 额外参数
        """
        if not self._is_running:
            self.logger.warning("服务未运行，无法发送通知")
            return

        success_count = 0
        total_count = len(self._providers)

        for provider_id, provider in self._providers.items():
            try:
                provider.send_notification(message, **kwargs)
                success_count += 1
                self.logger.debug(f"通知发送成功: {provider_id}")
            except Exception as e:
                self.logger.error(f"通知发送失败 ({provider_id}): {e}", exc_info=True)

        self.logger.info(f"通知分发完成: {success_count}/{total_count} 成功")
        self.notification_sent.emit(message, kwargs)

    async def start_async(self) -> None:
        """
        启动服务（实现IHostedService接口）
        """
        try:
            if self._is_running:
                self.logger.warning("服务已在运行")
                return

            self.logger.info("启动通知主机服务...")
            self._is_running = True
            self._start_time = asyncio.get_event_loop().time()

            # 启动监控定时器
            self._monitor_timer.start(5000)  # 每5秒监控一次

            self.service_started.emit()
            self.property_changed.emit("is_running", True)

            self.logger.info("通知主机服务启动完成")

        except Exception as e:
            self.logger.error(f"启动服务失败: {e}", exc_info=True)
            self._is_running = False
            raise

    async def stop_async(self) -> None:
        """
        停止服务（实现IHostedService接口）
        """
        try:
            if not self._is_running:
                self.logger.warning("服务未运行")
                return

            self.logger.info("停止通知主机服务...")
            self._is_running = False

            # 停止监控定时器
            self._monitor_timer.stop()

            # 清理资源
            self._providers.clear()

            self.service_stopped.emit()
            self.property_changed.emit("is_running", False)
            self.property_changed.emit("provider_count", 0)

            self.logger.info("通知主机服务已停止")

        except Exception as e:
            self.logger.error(f"停止服务失败: {e}", exc_info=True)
            raise

    def _monitor_service(self):
        """监控服务状态"""
        try:
            if self._is_running:
                self.logger.debug(f"服务监控: 运行中, 提供者数量: {self.provider_count}")

        except Exception as e:
            self.logger.error(f"服务监控失败: {e}", exc_info=True)

    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "is_running": self._is_running,
            "provider_count": self.provider_count,
            "start_time": self._start_time,
            "providers": [provider.__class__.__name__ for provider in self._providers.values()]
        }
