#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知数据模型
定义通知相关的数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class NotificationPriority(Enum):
    """通知优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class NotificationType(Enum):
    """通知类型枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationStatus(Enum):
    """通知状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NotificationRequest:
    """通知请求数据模型"""
    id: str
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    notification_type: NotificationType = NotificationType.INFO
    channels: List[str] = field(default_factory=list)
    template_data: Optional[Dict[str, Any]] = None
    callback: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationResult:
    """通知结果数据模型"""
    request_id: str
    status: NotificationStatus
    sent_channels: List[str] = field(default_factory=list)
    failed_channels: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    response_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationHistory:
    """通知历史记录数据模型"""
    id: str
    request: NotificationRequest
    result: NotificationResult
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.request.title,
            'message': self.request.message,
            'priority': self.request.priority.value,
            'type': self.request.notification_type.value,
            'channels': self.request.channels,
            'status': self.result.status.value,
            'sent_channels': self.result.sent_channels,
            'failed_channels': self.result.failed_channels,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.result.sent_at.isoformat() if self.result.sent_at else None
        }


@dataclass
class NotificationTemplate:
    """通知模板数据模型"""
    id: str
    name: str
    title_template: str
    message_template: str
    default_channels: List[str] = field(default_factory=list)
    default_priority: NotificationPriority = NotificationPriority.NORMAL
    variables: List[str] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def render(self, data: Dict[str, Any]) -> tuple[str, str]:
        """渲染模板"""
        try:
            title = self.title_template.format(**data)
            message = self.message_template.format(**data)
            return title, message
        except KeyError as e:
            raise ValueError(f"模板变量缺失: {e}")


@dataclass
class NotificationSettings:
    """通知设置数据模型"""
    enabled: bool = True
    default_channels: List[str] = field(default_factory=lambda: ['popup'])
    do_not_disturb: bool = False
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"
    max_notifications_per_minute: int = 10
    auto_dismiss_timeout: int = 5000  # 毫秒
    sound_enabled: bool = True
    sound_file: str = ""
    voice_enabled: bool = False
    voice_speed: float = 1.0
    popup_position: str = "top-right"
    popup_theme: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'default_channels': self.default_channels,
            'do_not_disturb': self.do_not_disturb,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'max_notifications_per_minute': self.max_notifications_per_minute,
            'auto_dismiss_timeout': self.auto_dismiss_timeout,
            'sound_enabled': self.sound_enabled,
            'sound_file': self.sound_file,
            'voice_enabled': self.voice_enabled,
            'voice_speed': self.voice_speed,
            'popup_position': self.popup_position,
            'popup_theme': self.popup_theme
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationSettings'
        """从字典创建"""
        return cls(**data)


@dataclass
class NotificationStatistics:
    """通知统计数据模型"""
    total_notifications: int = 0
    successful_notifications: int = 0
    failed_notifications: int = 0
    cancelled_notifications: int = 0
    notifications_by_channel: Dict[str, int] = field(default_factory=dict)
    notifications_by_priority: Dict[str, int] = field(default_factory=dict)
    notifications_by_type: Dict[str, int] = field(default_factory=dict)
    average_response_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_notifications == 0:
            return 0.0
        return self.successful_notifications / self.total_notifications
    
    @property
    def failure_rate(self) -> float:
        """失败率"""
        if self.total_notifications == 0:
            return 0.0
        return self.failed_notifications / self.total_notifications
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_notifications': self.total_notifications,
            'successful_notifications': self.successful_notifications,
            'failed_notifications': self.failed_notifications,
            'cancelled_notifications': self.cancelled_notifications,
            'success_rate': self.success_rate,
            'failure_rate': self.failure_rate,
            'notifications_by_channel': self.notifications_by_channel,
            'notifications_by_priority': self.notifications_by_priority,
            'notifications_by_type': self.notifications_by_type,
            'average_response_time': self.average_response_time,
            'last_updated': self.last_updated.isoformat()
        }


# 导出所有模型
__all__ = [
    'NotificationPriority',
    'NotificationType', 
    'NotificationStatus',
    'NotificationRequest',
    'NotificationResult',
    'NotificationHistory',
    'NotificationTemplate',
    'NotificationSettings',
    'NotificationStatistics'
]
