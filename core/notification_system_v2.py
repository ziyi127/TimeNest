#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知系统 v2
支持多通道、链式提醒、数据模板、渠道注册等高级功能
"""

import logging
import uuid
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread


class NotificationPriority(Enum):
    """通知优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannelType(Enum):
    """通知通道类型"""
    POPUP = "popup"
    TRAY = "tray"
    SOUND = "sound"
    VOICE = "voice"
    EMAIL = "email"


class NotificationStatus(Enum):
    """通知状态"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChainedNotificationType(Enum):
    """链式提醒类型"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    CONDITIONAL = "conditional"  # 条件执行


@dataclass
class NotificationTemplate:
    """通知模板"""
    id: str
    name: str
    title_template: str
    message_template: str
    channels: List[str] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.NORMAL
    variables: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def render(self, data: Dict[str, Any]) -> Dict[str, str]:
        """渲染模板"""
        try:
            # 合并变量
            render_data = {**self.variables, **data}
            
            # 渲染标题和消息
            title = self.title_template.format(**render_data)
            message = self.message_template.format(**render_data)
            
            return {"title": title, "message": message}
            
        except Exception as e:
            logging.error(f"模板渲染失败: {e}")
            return {"title": self.title_template, "message": self.message_template}


@dataclass
class NotificationRequest:
    """通知请求"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    message: str = ""
    channels: List[str] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    template_id: Optional[str] = None
    chain_id: Optional[str] = None
    delay_seconds: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'channels': self.channels,
            'priority': self.priority.value,
            'data': self.data,
            'template_id': self.template_id,
            'chain_id': self.chain_id,
            'delay_seconds': self.delay_seconds,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat(),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'status': self.status.value
        }


@dataclass
class ChainedNotificationRule:
    """链式提醒规则"""
    condition: str = ""  # 条件表达式
    delay_seconds: int = 0  # 延迟秒数
    max_retries: int = 1  # 最大重试次数
    stop_on_success: bool = True  # 成功后停止链
    stop_on_failure: bool = False  # 失败后停止链


@dataclass
class ChainedNotification:
    """链式提醒"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    chain_type: ChainedNotificationType = ChainedNotificationType.SEQUENTIAL
    notifications: List[NotificationRequest] = field(default_factory=list)
    rules: List[ChainedNotificationRule] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: NotificationStatus = NotificationStatus.PENDING
    current_step: int = 0
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'chain_type': self.chain_type.value,
            'notifications': [n.to_dict() for n in self.notifications],
            'rules': [
                {
                    'condition': rule.condition,
                    'delay_seconds': rule.delay_seconds,
                    'max_retries': rule.max_retries,
                    'stop_on_success': rule.stop_on_success,
                    'stop_on_failure': rule.stop_on_failure
                } for rule in self.rules
            ],
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'current_step': self.current_step,
            'completed_steps': self.completed_steps,
            'failed_steps': self.failed_steps
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChainedNotification':
        """从字典创建"""
        notifications = []
        for n_data in data.get('notifications', []):
            notification = NotificationRequest(
                id=n_data.get('id', str(uuid.uuid4())),
                title=n_data.get('title', ''),
                message=n_data.get('message', ''),
                channels=n_data.get('channels', []),
                priority=NotificationPriority(n_data.get('priority', 'normal')),
                data=n_data.get('data', {}),
                template_id=n_data.get('template_id'),
                chain_id=n_data.get('chain_id'),
                delay_seconds=n_data.get('delay_seconds', 0),
                retry_count=n_data.get('retry_count', 0),
                max_retries=n_data.get('max_retries', 3),
                status=NotificationStatus(n_data.get('status', 'pending'))
            )
            notifications.append(notification)

        rules = []
        for r_data in data.get('rules', []):
            rule = ChainedNotificationRule(
                condition=r_data.get('condition', ''),
                delay_seconds=r_data.get('delay_seconds', 0),
                max_retries=r_data.get('max_retries', 1),
                stop_on_success=r_data.get('stop_on_success', True),
                stop_on_failure=r_data.get('stop_on_failure', False)
            )
            rules.append(rule)

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description', ''),
            chain_type=ChainedNotificationType(data.get('chain_type', 'sequential')),
            notifications=notifications,
            rules=rules,
            status=NotificationStatus(data.get('status', 'pending')),
            current_step=data.get('current_step', 0),
            completed_steps=data.get('completed_steps', []),
            failed_steps=data.get('failed_steps', [])
        )


class NotificationChannel(ABC):
    """通知渠道基类"""
    
    def __init__(self, channel_id: str, name: str):
        self.channel_id = channel_id
        self.name = name
        self.enabled = True
        self.config = {}
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
    
    @abstractmethod
    def send(self, request: NotificationRequest) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查渠道是否可用"""
        pass
    
    def configure(self, config: Dict[str, Any]):
        """配置渠道"""
        self.config.update(config)
    
    def set_enabled(self, enabled: bool):
        """设置启用状态"""
        self.enabled = enabled


class PopupNotificationChannel(NotificationChannel):
    """弹窗通知渠道"""
    
    def __init__(self):
        super().__init__("popup", "弹窗通知")
    
    def send(self, request: NotificationRequest) -> bool:
        """发送弹窗通知"""
        try:
            if not self.enabled:
                return False
            
            # 这里应该显示实际的弹窗
            # 现在只是记录日志
            self.logger.info(f"弹窗通知: {request.title} - {request.message}")
            
            # 模拟发送成功
            return True
            
        except Exception as e:
            self.logger.error(f"发送弹窗通知失败: {e}")
            return False
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class SoundNotificationChannel(NotificationChannel):
    """音效通知渠道"""
    
    def __init__(self):
        super().__init__("sound", "音效通知")
    
    def send(self, request: NotificationRequest) -> bool:
        """播放通知音效"""
        try:
            if not self.enabled:
                return False
            
            # 获取音效文件路径
            sound_file = self.config.get('sound_file', 'default.wav')
            volume = self.config.get('volume', 0.8)
            
            # 这里应该播放实际的音效
            # 现在只是记录日志
            self.logger.info(f"播放音效: {sound_file}, 音量: {volume}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"播放音效失败: {e}")
            return False
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class VoiceNotificationChannel(NotificationChannel):
    """语音通知渠道"""
    
    def __init__(self):
        super().__init__("voice", "语音通知")
    
    def send(self, request: NotificationRequest) -> bool:
        """语音播报"""
        try:
            if not self.enabled:
                return False
            
            # 获取语音配置
            voice_engine = self.config.get('engine', 'system')
            voice_rate = self.config.get('rate', 150)
            voice_volume = self.config.get('volume', 0.9)
            
            # 构建语音文本
            text = f"{request.title}。{request.message}"
            
            # 这里应该使用实际的TTS引擎
            # 现在只是记录日志
            self.logger.info(f"语音播报: {text}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"语音播报失败: {e}")
            return False
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class SystemTrayNotificationChannel(NotificationChannel):
    """系统托盘通知渠道"""
    
    def __init__(self):
        super().__init__("tray", "系统托盘通知")
    
    def send(self, request: NotificationRequest) -> bool:
        """发送系统托盘通知"""
        try:
            if not self.enabled:
                return False
            
            # 获取配置
            duration = self.config.get('duration', 5000)
            icon_type = self.config.get('icon_type', 'info')
            
            # 这里应该显示实际的系统托盘通知
            # 现在只是记录日志
            self.logger.info(f"系统托盘通知: {request.title} - {request.message}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"发送系统托盘通知失败: {e}")
            return False
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class EmailNotificationChannel(NotificationChannel):
    """邮件通知渠道"""
    
    def __init__(self):
        super().__init__("email", "邮件通知")
    
    def send(self, request: NotificationRequest) -> bool:
        """发送邮件通知"""
        try:
            if not self.enabled:
                return False
            
            # 获取邮件配置
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port', 587)
            username = self.config.get('username')
            password = self.config.get('password')
            to_email = self.config.get('to_email')
            
            if not all([smtp_server, username, password, to_email]):
                self.logger.error("邮件配置不完整")
                return False
            
            # 这里应该发送实际的邮件
            # 现在只是记录日志
            self.logger.info(f"发送邮件: {to_email} - {request.title}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
            return False
    
    def is_available(self) -> bool:
        """检查是否可用"""
        required_config = ['smtp_server', 'username', 'password', 'to_email']
        return all(key in self.config for key in required_config)


class NotificationChain:
    """通知链"""
    
    def __init__(self, chain_id: str, name: str):
        self.chain_id = chain_id
        self.name = name
        self.notifications: List[NotificationRequest] = []
        self.current_index = 0
        self.is_active = False
        self.created_at = datetime.now()
    
    def add_notification(self, request: NotificationRequest):
        """添加通知到链中"""
        request.chain_id = self.chain_id
        self.notifications.append(request)
    
    def get_next_notification(self) -> Optional[NotificationRequest]:
        """获取下一个通知"""
        if self.current_index < len(self.notifications):
            notification = self.notifications[self.current_index]
            self.current_index += 1
            return notification
        return None
    
    def reset(self):
        """重置链"""
        self.current_index = 0
        self.is_active = False
    
    def is_completed(self) -> bool:
        """检查是否完成"""
        return self.current_index >= len(self.notifications)


class NotificationSystemV2(QObject):
    """通知系统 v2"""
    
    # 信号定义
    notification_sent = pyqtSignal(str)  # 通知ID
    notification_failed = pyqtSignal(str, str)  # 通知ID, 错误信息
    channel_registered = pyqtSignal(str)  # 渠道ID
    template_added = pyqtSignal(str)  # 模板ID
    chain_started = pyqtSignal(str)  # 链ID
    chain_completed = pyqtSignal(str)  # 链ID
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.NotificationSystemV2')
        
        # 渠道管理
        self.channels: Dict[str, NotificationChannel] = {}
        
        # 模板管理
        self.templates: Dict[str, NotificationTemplate] = {}
        
        # 通知队列
        self.notification_queue: List[NotificationRequest] = []
        self.active_notifications: Dict[str, NotificationRequest] = {}
        
        # 链式通知
        self.notification_chains: Dict[str, NotificationChain] = {}
        
        # 处理定时器
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_queue)
        self.process_timer.start(100)  # 每100ms处理一次
        
        # 注册默认渠道
        self._register_default_channels()
        
        # 加载默认模板
        self._load_default_templates()
    
    def _register_default_channels(self):
        """注册默认通知渠道"""
        default_channels = [
            PopupNotificationChannel(),
            SoundNotificationChannel(),
            VoiceNotificationChannel(),
            SystemTrayNotificationChannel(),
            EmailNotificationChannel()
        ]
        
        for channel in default_channels:
            self.register_channel(channel)
    
    def _load_default_templates(self):
        """加载默认通知模板"""
        default_templates = [
            NotificationTemplate(
                id="class_start",
                name="上课提醒",
                title_template="上课提醒",
                message_template="{subject_name} 即将在 {classroom} 开始",
                channels=["popup", "sound"],
                priority=NotificationPriority.HIGH
            ),
            NotificationTemplate(
                id="class_end",
                name="下课提醒",
                title_template="下课提醒",
                message_template="{subject_name} 课程结束",
                channels=["popup"],
                priority=NotificationPriority.NORMAL
            ),
            NotificationTemplate(
                id="break_time",
                name="课间休息",
                title_template="课间休息",
                message_template="课间休息时间，下节课是 {next_subject}",
                channels=["tray"],
                priority=NotificationPriority.LOW
            )
        ]
        
        for template in default_templates:
            self.add_template(template)

    def register_channel(self, channel: NotificationChannel):
        """注册通知渠道"""
        try:
            self.channels[channel.channel_id] = channel
            self.channel_registered.emit(channel.channel_id)
            self.logger.info(f"通知渠道注册成功: {channel.name}")

        except Exception as e:
            self.logger.error(f"注册通知渠道失败: {e}")

    def unregister_channel(self, channel_id: str):
        """注销通知渠道"""
        try:
            if channel_id in self.channels:
                del self.channels[channel_id]
                self.logger.info(f"通知渠道注销成功: {channel_id}")

        except Exception as e:
            self.logger.error(f"注销通知渠道失败: {e}")

    def get_channel(self, channel_id: str) -> Optional[NotificationChannel]:
        """获取通知渠道"""
        return self.channels.get(channel_id)

    def get_available_channels(self) -> List[NotificationChannel]:
        """获取可用的通知渠道"""
        return [channel for channel in self.channels.values()
                if channel.enabled and channel.is_available()]

    def add_template(self, template: NotificationTemplate):
        """添加通知模板"""
        try:
            self.templates[template.id] = template
            self.template_added.emit(template.id)
            self.logger.info(f"通知模板添加成功: {template.name}")

        except Exception as e:
            self.logger.error(f"添加通知模板失败: {e}")

    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """获取通知模板"""
        return self.templates.get(template_id)

    def send_notification(self, request: NotificationRequest) -> bool:
        """发送通知"""
        try:
            # 如果使用模板，先渲染
            if request.template_id and request.template_id in self.templates:
                template = self.templates[request.template_id]
                rendered = template.render(request.data)
                request.title = rendered["title"]
                request.message = rendered["message"]

                # 如果请求中没有指定渠道，使用模板的渠道
                if not request.channels:
                    request.channels = template.channels

                # 使用模板的优先级
                if request.priority == NotificationPriority.NORMAL:
                    request.priority = template.priority

            # 设置调度时间
            if request.delay_seconds > 0:
                request.scheduled_at = datetime.now() + timedelta(seconds=request.delay_seconds)
            else:
                request.scheduled_at = datetime.now()

            # 添加到队列
            self.notification_queue.append(request)
            self.logger.info(f"通知已加入队列: {request.title}")

            return True

        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            return False

    def send_notification_with_template(self, template_id: str, data: Dict[str, Any],
                                      channels: List[str] = None,
                                      delay_seconds: int = 0) -> bool:
        """使用模板发送通知"""
        try:
            if template_id not in self.templates:
                self.logger.error(f"模板不存在: {template_id}")
                return False

            request = NotificationRequest(
                template_id=template_id,
                data=data,
                channels=channels or [],
                delay_seconds=delay_seconds
            )

            return self.send_notification(request)

        except Exception as e:
            self.logger.error(f"使用模板发送通知失败: {e}")
            return False

    def create_notification_chain(self, chain_id: str, name: str) -> NotificationChain:
        """创建通知链"""
        try:
            chain = NotificationChain(chain_id, name)
            self.notification_chains[chain_id] = chain
            self.logger.info(f"通知链创建成功: {name}")
            return chain

        except Exception as e:
            self.logger.error(f"创建通知链失败: {e}")
            return None

    def start_notification_chain(self, chain_id: str) -> bool:
        """启动通知链"""
        try:
            if chain_id not in self.notification_chains:
                self.logger.error(f"通知链不存在: {chain_id}")
                return False

            chain = self.notification_chains[chain_id]
            chain.is_active = True
            chain.reset()

            self.chain_started.emit(chain_id)
            self.logger.info(f"通知链启动: {chain.name}")

            # 处理第一个通知
            self._process_chain(chain)

            return True

        except Exception as e:
            self.logger.error(f"启动通知链失败: {e}")
            return False

    def _process_chain(self, chain: NotificationChain):
        """处理通知链"""
        try:
            if not chain.is_active:
                return

            next_notification = chain.get_next_notification()
            if next_notification:
                # 发送下一个通知
                self.send_notification(next_notification)
            else:
                # 链完成
                chain.is_active = False
                self.chain_completed.emit(chain.chain_id)
                self.logger.info(f"通知链完成: {chain.name}")

        except Exception as e:
            self.logger.error(f"处理通知链失败: {e}")

    def _process_queue(self):
        """处理通知队列"""
        try:
            current_time = datetime.now()

            # 处理待发送的通知
            pending_notifications = []
            for request in self.notification_queue:
                if request.scheduled_at and request.scheduled_at <= current_time:
                    # 时间到了，发送通知
                    self._send_notification_now(request)
                else:
                    # 还没到时间，保留在队列中
                    pending_notifications.append(request)

            self.notification_queue = pending_notifications

        except Exception as e:
            self.logger.error(f"处理通知队列失败: {e}")

    def _send_notification_now(self, request: NotificationRequest):
        """立即发送通知"""
        try:
            request.status = NotificationStatus.SENDING
            self.active_notifications[request.id] = request

            success_count = 0
            total_channels = len(request.channels)

            # 向所有指定渠道发送通知
            for channel_id in request.channels:
                if channel_id in self.channels:
                    channel = self.channels[channel_id]
                    if channel.enabled and channel.is_available():
                        try:
                            if channel.send(request):
                                success_count += 1
                                self.logger.debug(f"通知发送成功: {channel_id}")
                            else:
                                self.logger.warning(f"通知发送失败: {channel_id}")
                        except Exception as e:
                            self.logger.error(f"渠道发送失败 {channel_id}: {e}")
                    else:
                        self.logger.warning(f"渠道不可用: {channel_id}")
                else:
                    self.logger.warning(f"渠道不存在: {channel_id}")

            # 更新状态
            if success_count > 0:
                request.status = NotificationStatus.SENT
                self.notification_sent.emit(request.id)
                self.logger.info(f"通知发送完成: {request.title} ({success_count}/{total_channels})")

                # 如果是链式通知，处理下一个
                if request.chain_id and request.chain_id in self.notification_chains:
                    chain = self.notification_chains[request.chain_id]
                    self._process_chain(chain)

            else:
                request.status = NotificationStatus.FAILED

                # 重试逻辑
                if request.retry_count < request.max_retries:
                    request.retry_count += 1
                    request.status = NotificationStatus.PENDING
                    request.scheduled_at = datetime.now() + timedelta(seconds=30)  # 30秒后重试
                    self.notification_queue.append(request)
                    self.logger.info(f"通知重试: {request.title} ({request.retry_count}/{request.max_retries})")
                else:
                    self.notification_failed.emit(request.id, "所有渠道发送失败")
                    self.logger.error(f"通知发送失败: {request.title}")

            # 从活动通知中移除
            if request.id in self.active_notifications:
                del self.active_notifications[request.id]

        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            request.status = NotificationStatus.FAILED
            self.notification_failed.emit(request.id, str(e))

    def cancel_notification(self, notification_id: str) -> bool:
        """取消通知"""
        try:
            # 从队列中移除
            self.notification_queue = [req for req in self.notification_queue
                                     if req.id != notification_id]

            # 从活动通知中移除
            if notification_id in self.active_notifications:
                request = self.active_notifications[notification_id]
                request.status = NotificationStatus.CANCELLED
                del self.active_notifications[notification_id]

            self.logger.info(f"通知已取消: {notification_id}")
            return True

        except Exception as e:
            self.logger.error(f"取消通知失败: {e}")
            return False

    def get_notification_status(self, notification_id: str) -> Optional[NotificationStatus]:
        """获取通知状态"""
        # 检查活动通知
        if notification_id in self.active_notifications:
            return self.active_notifications[notification_id].status

        # 检查队列中的通知
        for request in self.notification_queue:
            if request.id == notification_id:
                return request.status

        return None

    def get_queue_size(self) -> int:
        """获取队列大小"""
        return len(self.notification_queue)

    def clear_queue(self):
        """清空队列"""
        self.notification_queue.clear()
        self.logger.info("通知队列已清空")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_channels': len(self.channels),
            'available_channels': len(self.get_available_channels()),
            'total_templates': len(self.templates),
            'queue_size': len(self.notification_queue),
            'active_notifications': len(self.active_notifications),
            'active_chains': len([c for c in self.notification_chains.values() if c.is_active])
        }
