#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知服务模块

提供通知相关的数据类型和枚举定义
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationType(Enum):
    """通知类型枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    REMINDER = "reminder"
    SCHEDULE = "schedule"
    SYSTEM = "system"


class NotificationPriority(Enum):
    """通知优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class NotificationRequest:
    """通知请求数据类"""
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    duration: int = 5000  # 显示时长（毫秒）
    sound_enabled: bool = True
    persistent: bool = False  # 是否持久显示
    action_buttons: Optional[Dict[str, str]] = None  # 操作按钮
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class NotificationResponse:
    """通知响应数据类"""
    notification_id: str
    action: str  # 用户执行的操作
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class NotificationChannel(Enum):
    """通知渠道枚举"""
    DESKTOP = "desktop"
    SYSTEM_TRAY = "system_tray"
    SOUND = "sound"
    SPEECH = "speech"
    EMAIL = "email"
    POPUP = "popup"


@dataclass
class NotificationSettings:
    """通知设置数据类"""
    enabled: bool = True
    sound_enabled: bool = True
    speech_enabled: bool = False
    desktop_enabled: bool = True
    system_tray_enabled: bool = True
    default_duration: int = 5000
    max_notifications: int = 10
    priority_filter: NotificationPriority = NotificationPriority.LOW
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    channels: Dict[NotificationChannel, bool] = None
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = {
                NotificationChannel.DESKTOP: True,
                NotificationChannel.SYSTEM_TRAY: True,
                NotificationChannel.SOUND: True,
                NotificationChannel.SPEECH: False,
                NotificationChannel.EMAIL: False,
                NotificationChannel.POPUP: True,
            }


class NotificationStatus(Enum):
    """通知状态枚举"""
    PENDING = "pending"
    DISPLAYED = "displayed"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class NotificationHistory:
    """通知历史记录"""
    notification_id: str
    request: NotificationRequest
    status: NotificationStatus
    displayed_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    response: Optional[NotificationResponse] = None
    error_message: Optional[str] = None


class NotificationHostService:
    """通知主机服务"""

    def __init__(self):
        self.notifications: Dict[str, NotificationRequest] = {}
        self.history: Dict[str, NotificationHistory] = {}
        self.settings = NotificationSettings()

    def create_notification(self, title: str, message: str,
                          notification_type: NotificationType = NotificationType.INFO,
                          priority: NotificationPriority = NotificationPriority.NORMAL,
                          **kwargs) -> str:
        """创建通知"""
        import uuid
        notification_id = str(uuid.uuid4())

        request = NotificationRequest(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            **kwargs
        )

        self.notifications[notification_id] = request
        return notification_id

    def send_notification(self, notification_id: str) -> bool:
        """发送通知"""
        if notification_id in self.notifications:
            # 这里应该实际发送通知，现在只是标记为已发送
            return True
        return False

    def get_notification(self, notification_id: str) -> Optional[NotificationRequest]:
        """获取通知"""
        return self.notifications.get(notification_id)


def create_notification(title: str, message: str,
                       notification_type: NotificationType = NotificationType.INFO,
                       priority: NotificationPriority = NotificationPriority.NORMAL,
                       **kwargs) -> NotificationRequest:
    """创建通知请求的便捷函数"""
    return NotificationRequest(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        **kwargs
    )
