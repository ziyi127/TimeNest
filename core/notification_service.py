#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知服务
基于 ClassIsland NotificationHostService 规范实现
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QSystemTrayIcon, QApplication
from PyQt6.QtGui import QIcon
import sentry_sdk
from plyer import notification


class NotificationType(Enum):
    """通知类型枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CLASS_REMINDER = "class_reminder"
    HOMEWORK_REMINDER = "homework_reminder"
    EXAM_REMINDER = "exam_reminder"
    WEATHER_ALERT = "weather_alert"


class NotificationPriority(Enum):
    """通知优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class NotificationRequest:
    """通知请求"""
    id: str
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    duration: Optional[int] = None  # 显示时长（毫秒），None表示不自动消失
    icon: Optional[str] = None
    actions: List[Dict[str, Any]] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    channel_id: Optional[str] = None  # 通知渠道ID
    chain_id: Optional[str] = None  # 链式通知ID
    

class INotificationProvider(ABC):
    """通知提供者接口"""
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """提供者ID"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供者名称"""
        pass
    
    @property
    @abstractmethod
    def supported_types(self) -> List[NotificationType]:
        """支持的通知类型"""
        pass
    
    @abstractmethod
    def can_handle(self, request: NotificationRequest) -> bool:
        """检查是否可以处理指定的通知请求"""
        pass
    
    @abstractmethod
    def send_notification(self, request: NotificationRequest) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    def cancel_notification(self, notification_id: str) -> bool:
        """取消通知"""
        pass


class SystemTrayNotificationProvider(INotificationProvider):
    """系统托盘通知提供者"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.SystemTrayNotificationProvider')
        self.active_notifications: Dict[str, QSystemTrayIcon] = {}
    
    @property
    def provider_id(self) -> str:
        return "system_tray"
    
    @property
    def provider_name(self) -> str:
        return "系统托盘通知"
    
    @property
    def supported_types(self) -> List[NotificationType]:
        return list(NotificationType)
    
    def can_handle(self, request: NotificationRequest) -> bool:
        """检查系统是否支持托盘通知"""
        return QSystemTrayIcon.isSystemTrayAvailable()
    
    def send_notification(self, request: NotificationRequest) -> bool:
        """发送系统托盘通知"""
        try:
            if not self.can_handle(request):
                return False
            
            # 获取图标
            icon = QIcon(request.icon) if request.icon else QApplication.instance().windowIcon()
            
            # 确定消息类型
            if request.notification_type == NotificationType.ERROR:
                msg_type = QSystemTrayIcon.MessageIcon.Critical
            elif request.notification_type == NotificationType.WARNING:
                msg_type = QSystemTrayIcon.MessageIcon.Warning
            else:
                msg_type = QSystemTrayIcon.MessageIcon.Information
            
            # 创建托盘图标（如果不存在）
            tray_icon = QSystemTrayIcon(icon)
            tray_icon.show()
            
            # 发送通知
            duration = request.duration or 5000  # 默认5秒
            tray_icon.showMessage(
                request.title,
                request.message,
                msg_type,
                duration
            )
            
            # 保存活动通知
            self.active_notifications[request.id] = tray_icon
            
            # 设置自动清理
            if request.duration:
                QTimer.singleShot(duration, lambda: self._cleanup_notification(request.id))
            
            self.logger.info(f"系统托盘通知已发送: {request.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送系统托盘通知失败: {e}", exc_info=True)
            return False
    
    def cancel_notification(self, notification_id: str) -> bool:
        """取消通知"""
        try:
            if notification_id in self.active_notifications:
                tray_icon = self.active_notifications[notification_id]
                tray_icon.hide()
                del self.active_notifications[notification_id]
                return True
            return False
        except Exception as e:
            self.logger.error(f"取消通知失败: {e}", exc_info=True)
            return False
    
    def _cleanup_notification(self, notification_id: str):
        """清理通知"""
        self.cancel_notification(notification_id)


class ConsoleNotificationProvider(INotificationProvider):
    """控制台通知提供者（用于调试）"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.ConsoleNotificationProvider')
    
    @property
    def provider_id(self) -> str:
        return "console"
    
    @property
    def provider_name(self) -> str:
        return "控制台通知"
    
    @property
    def supported_types(self) -> List[NotificationType]:
        return list(NotificationType)
    
    def can_handle(self, request: NotificationRequest) -> bool:
        return True
    
    def send_notification(self, request: NotificationRequest) -> bool:
        """在控制台输出通知"""
        try:
            timestamp = request.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            priority_str = request.priority.name
            type_str = request.notification_type.value
            
            print(f"\n{'='*50}")
            print(f"[{timestamp}] 通知 - {priority_str} - {type_str}")
            print(f"标题: {request.title}")
            print(f"内容: {request.message}")
            if request.data:
                print(f"数据: {request.data}")
            print(f"{'='*50}\n")
            
            self.logger.info(f"控制台通知已输出: {request.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"输出控制台通知失败: {e}", exc_info=True)
            return False
    
    def cancel_notification(self, notification_id: str) -> bool:
        """控制台通知无法取消"""
        return True


class NotificationProvider(ABC):
    """通知提供者基类"""
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化通知提供者"""
        pass
    
    @abstractmethod
    def notify(self, title: str, message: str, **kwargs) -> None:
        """发送通知"""
        pass


class SystemNotificationProvider(NotificationProvider):
    """系统通知提供者"""
    
    def initialize(self) -> None:
        pass
    
    def notify(self, title: str, message: str, **kwargs) -> None:
        notification.notify(
            title=title,
            message=message,
            app_name="TimeNest",
            timeout=kwargs.get("timeout", 10)
        )


class NotificationHostService(QObject):
    """通知主机服务"""
    
    # 信号
    notification_sent = pyqtSignal(NotificationRequest)
    notification_failed = pyqtSignal(NotificationRequest, str)
    notification_cancelled = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.NotificationHostService')
        self.providers: Dict[str, INotificationProvider] = {}
        self.notification_queue: List[NotificationRequest] = []
        self.active_notifications: Dict[str, NotificationRequest] = {}
        self.notification_chains: Dict[str, List[str]] = {}  # 链式通知
        self.enabled = True
        
        # 注册默认提供者
        self.register_notification_provider(SystemTrayNotificationProvider())
        self.register_notification_provider(ConsoleNotificationProvider())
        
        # 设置处理定时器
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_queue)
        self.process_timer.start(100)  # 每100ms处理一次队列
    
    def register_notification_provider(self, provider: INotificationProvider):
        """
        注册提醒服务（严格遵循 doc/NotificationHostService.md）
        :param provider: INotificationProvider 实例
        """
        try:
            self.providers[provider.provider_id] = provider
            self.logger.info(f"通知提供者已注册: {provider.provider_name} ({provider.provider_id})")
        except Exception as e:
            self.logger.error(f"注册通知提供者失败: {e}", exc_info=True)
    
    def unregister_notification_provider(self, provider_id: str):
        """注销通知提供者"""
        try:
            if provider_id in self.providers:
                provider = self.providers.pop(provider_id)
                self.logger.info(f"通知提供者已注销: {provider.provider_name}")
        except Exception as e:
            self.logger.error(f"注销通知提供者失败: {e}", exc_info=True)
    
    def send_notification(self, request: NotificationRequest) -> bool:
        """
        发送通知（严格遵循 doc/NotificationHostService.md）
        :param request: NotificationRequest
        :return: 是否成功加入队列
        """
        if not self.enabled:
            self.logger.debug("通知服务已禁用，跳过通知")
            return False
        try:
            self.notification_queue.append(request)
            self.logger.debug(f"通知已添加到队列: {request.title}")
            return True
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}", exc_info=True)
            self.notification_failed.emit(request, str(e))
            return False
    
    def cancel_notification(self, notification_id: str) -> bool:
        """取消通知"""
        try:
            success = False
            
            # 从队列中移除
            self.notification_queue = [req for req in self.notification_queue if req.id != notification_id]
            
            # 取消活动通知
            if notification_id in self.active_notifications:
                request = self.active_notifications[notification_id]
                
                # 尝试从所有提供者取消
                for provider in self.providers.values():
                    if provider.cancel_notification(notification_id):
                        success = True
                
                del self.active_notifications[notification_id]
                
                # 处理链式通知
                if request.chain_id and request.chain_id in self.notification_chains:
                    chain_notifications = self.notification_chains[request.chain_id]
                    for chain_id in chain_notifications:
                        if chain_id != notification_id:
                            self.cancel_notification(chain_id)
                    del self.notification_chains[request.chain_id]
            
            if success:
                self.notification_cancelled.emit(notification_id)
                self.logger.info(f"通知已取消: {notification_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"取消通知失败: {e}", exc_info=True)
            return False
    
    def cancel_chain_notifications(self, chain_id: str) -> bool:
        """取消链式通知"""
        try:
            if chain_id not in self.notification_chains:
                return False
            
            chain_notifications = self.notification_chains[chain_id]
            for notification_id in chain_notifications:
                self.cancel_notification(notification_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"取消链式通知失败: {e}", exc_info=True)
            return False
    
    def _process_queue(self):
        """处理通知队列"""
        if not self.notification_queue or not self.enabled:
            return
        
        try:
            # 按优先级排序
            self.notification_queue.sort(key=lambda x: x.priority.value, reverse=True)
            
            # 处理队列中的通知
            while self.notification_queue:
                request = self.notification_queue.pop(0)
                self._send_notification_internal(request)
                
        except Exception as e:
            self.logger.error(f"处理通知队列失败: {e}", exc_info=True)
    
    def _send_notification_internal(self, request: NotificationRequest):
        """内部发送通知方法"""
        try:
            sent = False
            
            # 寻找合适的提供者
            for provider in self.providers.values():
                if provider.can_handle(request) and request.notification_type in provider.supported_types:
                    if provider.send_notification(request):
                        sent = True
                        break
            
            if sent:
                # 记录活动通知
                self.active_notifications[request.id] = request
                
                # 处理链式通知
                if request.chain_id:
                    if request.chain_id not in self.notification_chains:
                        self.notification_chains[request.chain_id] = []
                    self.notification_chains[request.chain_id].append(request.id)
                
                # 发送信号
                self.notification_sent.emit(request)
                
                self.logger.info(f"通知发送成功: {request.title}")
            else:
                error_msg = "没有可用的通知提供者"
                self.logger.warning(f"通知发送失败: {request.title} - {error_msg}")
                self.notification_failed.emit(request, error_msg)
                
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}", exc_info=True)
            self.notification_failed.emit(request, str(e))
    
    def set_enabled(self, enabled: bool):
        """设置通知服务启用状态"""
        self.enabled = enabled
        self.logger.info(f"通知服务{'启用' if enabled else '禁用'}")
    
    def get_active_notifications(self) -> List[NotificationRequest]:
        """获取活动通知列表"""
        return list(self.active_notifications.values())
    
    def get_providers(self) -> List[INotificationProvider]:
        """获取所有注册的提供者"""
        return list(self.providers.values())
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止定时器
            if self.process_timer.isActive():
                self.process_timer.stop()
            
            # 取消所有活动通知
            for notification_id in list(self.active_notifications.keys()):
                self.cancel_notification(notification_id)
            
            # 清空队列
            self.notification_queue.clear()
            
            self.logger.info("通知服务已清理")
            
        except Exception as e:
            self.logger.error(f"清理通知服务失败: {e}", exc_info=True)


# 便捷函数
def create_notification(title: str, message: str, 
                       notification_type: NotificationType = NotificationType.INFO,
                       priority: NotificationPriority = NotificationPriority.NORMAL,
                       duration: Optional[int] = None,
                       **kwargs) -> NotificationRequest:
    """创建通知请求的便捷函数"""
    import uuid
    
    return NotificationRequest(
        id=str(uuid.uuid4()),
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        duration=duration,
        **kwargs
    )