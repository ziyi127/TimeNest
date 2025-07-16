#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 通知管理器
负责上下课提醒、音效播放、语音提醒等功能
支持多通道、链式提醒、数据模板、智能特性

该模块提供了完整的通知管理功能，包括：
- 多通道通知支持（弹窗、托盘、声音、语音、邮件、浮窗）
- 链式提醒和条件触发
- 通知模板和数据绑定
- 智能提醒策略
- 通知历史和统计
- 性能优化和错误恢复
"""

import logging
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Callable, Dict, Generic, List, Optional, Protocol, TypeVar, Union,
    TYPE_CHECKING
)
from functools import lru_cache
from collections import deque

from utils.common_imports import QObject, Signal, QTimer
from utils.config_constants import DEFAULT_NOTIFICATION_SETTINGS
from utils.shared_utilities import is_within_time_range, debounce

try:
    from PySide6.QtCore import QMutex, QMutexLocker, Qt, QThread
    from PySide6.QtGui import QGuiApplication, QIcon
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer, QSoundEffect
    from PySide6.QtWidgets import QApplication, QStyle, QSystemTrayIcon
    QT_MULTIMEDIA_AVAILABLE = True
except ImportError:
    logging.error("PySide6 multimedia components not available")
    QT_MULTIMEDIA_AVAILABLE = False

    class QMutex:
        pass

    class QMutexLocker:
        def __init__(self, *args):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    class QThread:
        pass

    class QMediaPlayer:
        pass

    class QSoundEffect:
        pass

try:
    from core.notification_service import NotificationPriority, NotificationRequest, NotificationType
    from models.schedule import ClassItem, Schedule
    from utils.text_to_speech import TextToSpeech
except ImportError as e:
    logging.error(f"Failed to import notification dependencies: {e}")

    class NotificationPriority:
        LOW = "low"
        NORMAL = "normal"
        HIGH = "high"

    class NotificationRequest:
        pass

    class NotificationType:
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"

    class ClassItem:
        pass

    class Schedule:
        pass

    class TextToSpeech:
        def __init__(self):
            pass
        def speak(self, text):
            pass

if TYPE_CHECKING:
    from core.config_manager import ConfigManager

# 类型变量定义
T = TypeVar('T')
NotificationCallback = Callable[[str, bool], None]  # notification_id, success

class NotificationChannelType(Enum):
    """通知通道类型枚举"""
    POPUP = "popup"
    TRAY = "tray"
    SOUND = "sound"
    VOICE = "voice"
    EMAIL = "email"
    FLOATING = "floating"


class NotificationChannel(ABC):
    """
    通知通道基类

    所有通知通道必须继承此类并实现抽象方法
    """

    def __init__(self, channel_id: str, name: str):
        """
        初始化通知通道

        Args:
            channel_id: 通道唯一标识
            name: 通道显示名称
        """
        self.channel_id = channel_id
        self.name = name
        self.enabled = True
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @abstractmethod
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        发送通知

        Args:
            title: 通知标题
            message: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 发送是否成功
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查通道是否可用

        Returns:
            bool: 通道是否可用
        """
        pass

    def configure(self, config: Dict[str, Any]) -> None:
        """
        配置通道

        Args:
            config: 配置字典
        """
        self.config.update(config)
        self.logger.debug(f"通道 {self.channel_id} 配置已更新")

    def set_enabled(self, enabled: bool) -> None:
        """
        设置通道启用状态

        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
        self.logger.info(f"通道 {self.channel_id} {'启用' if enabled else '禁用'}")

class PopupChannel(NotificationChannel):
    """弹窗通知通道"""

    def __init__(self, manager):
        """
        初始化弹窗通道

        Args:
            manager: 通知管理器实例
        """
        super().__init__("popup", "弹窗通知")
        self.manager = manager

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        发送弹窗通知

        Args:
            title: 通知标题
            message: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 发送是否成功
        """
        try:
            if not self.enabled:
                return False

            notification_type = kwargs.get('notification_type', 'custom')
            return self.manager._show_popup_notification(title, message, notification_type)
        except Exception as e:
            self.logger.error(f"发送弹窗通知失败: {e}")
            return False

    def is_available(self) -> bool:
        """检查弹窗通道是否可用"""
        return True


class TrayChannel(NotificationChannel):
    """系统托盘通知通道"""

    def __init__(self, manager):
        """
        初始化托盘通道

        Args:
            manager: 通知管理器实例
        """
        super().__init__("tray", "系统托盘通知")
        self.manager = manager

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        发送托盘通知

        Args:
            title: 通知标题
            message: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 发送是否成功
        """
        try:
            if not self.enabled:
                return False

            return self.manager._show_tray_notification(title, message)
        except Exception as e:
            self.logger.error(f"发送托盘通知失败: {e}")
            return False

    def is_available(self) -> bool:
        """检查托盘通道是否可用"""
        return QSystemTrayIcon.isSystemTrayAvailable()


class SoundChannel(NotificationChannel):
    """音效通知通道"""

    def __init__(self, manager):
        """
        初始化音效通道

        Args:
            manager: 通知管理器实例
        """
        super().__init__("sound", "音效通知")
        self.manager = manager

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        播放通知音效

        Args:
            title: 通知标题
            message: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 播放是否成功
        """
        try:
            if not self.enabled:
                return False

            sound_file = kwargs.get('sound_file', '')
            return self.manager._play_sound(sound_file)
        except Exception as e:
            self.logger.error(f"播放音效失败: {e}")
            return False

    def is_available(self) -> bool:
        """检查音效通道是否可用"""
        return True


class VoiceChannel(NotificationChannel):
    """语音通知通道"""

    def __init__(self, manager):
        """
        初始化语音通道

        Args:
            manager: 通知管理器实例
        """
        super().__init__("voice", "语音通知")
        self.manager = manager

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        语音播报通知

        Args:
            title: 通知标题
            message: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 播报是否成功
        """
        try:
            if not self.enabled:
                return False

            voice_text = kwargs.get('voice_text', message)
            return self.manager._speak_text(voice_text)
        except Exception as e:
            self.logger.error(f"语音播报失败: {e}")
            return False

    def is_available(self) -> bool:
        """检查语音通道是否可用"""
        return hasattr(self.manager, 'tts') and self.manager.tts is not None


class EmailChannel(NotificationChannel):
    """邮件通知通道"""

    def __init__(self, manager):
        """
        初始化邮件通道

        Args:
            manager: 通知管理器实例
        """
        super().__init__("email", "邮件通知")
        self.manager = manager

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        发送邮件通知

        Args:
            title: 通知标题
            message: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 发送是否成功
        """
        try:
            if not self.enabled:
                return False

            # 获取邮件配置
            email_config = self.config.get('email', {})
            if not email_config.get('enabled', False):
                return False

            # 这里应该实现实际的邮件发送逻辑
            self.logger.info(f"邮件通知: {title} - {message}")
            return True

        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {e}")
            return False

    def is_available(self) -> bool:
        """检查邮件通道是否可用"""
        email_config = self.config.get('email', {})
        return (email_config.get('enabled', False) and
                email_config.get('smtp_server') and
                email_config.get('username') and
                email_config.get('password'))

class NotificationManager(QObject):
    """
    通知管理器 v2

    支持多通道、链式提醒、数据模板、智能特性
    提供完整的通知生命周期管理
    """

    # 标准信号定义
    notification_sent = Signal(str, dict)  # 通知ID, 通知数据
    notification_failed = Signal(str, str)  # 通知ID, 错误信息
    channel_status_changed = Signal(str, bool)  # 通道名, 状态
    config_updated = Signal(dict)  # 配置变更
    important_notification_received = Signal()  # 重要通知接收
    batch_notification_completed = Signal(str, int, int)  # 批次ID, 成功数, 失败数

    def __init__(self, config_manager: 'ConfigManager', theme_manager=None, floating_manager=None):
        """
        初始化通知管理器

        Args:
            config_manager: 配置管理器
            theme_manager: 主题管理器（可选）
            floating_manager: 浮窗管理器（可选）
        """
        super().__init__()

        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.NotificationManager')

        # 核心组件
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.floating_manager = floating_manager

        # 加载设置
        self.settings = self._load_settings()

        # 多媒体组件
        self.sound_effect = QSoundEffect()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # 语音合成
        self.tts: Optional[TextToSpeech] = None
        self._init_tts()

        # 系统托盘
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self._init_tray_icon()

        # 通知窗口管理 (已迁移到RinUI)
        # self.notification_windows: List[NotificationWindow] = []

        # 定时器管理 - 使用弱引用避免内存泄漏
        import weakref
        self.reminder_timers: Dict[str, QTimer] = {}
        self._timer_cleanup_counter = 0

        # 状态跟踪
        self.last_notified_class: Optional[ClassItem] = None
        # 使用有界队列防止内存泄漏
        from collections import deque
        self.notification_history: deque = deque(maxlen=1000)  # 最多保存1000条历史
        self.failed_notifications: deque = deque(maxlen=100)   # 最多保存100条失败记录

        # 通道注册表
        self.channels: Dict[str, NotificationChannel] = {}
        self._register_builtin_channels()

        # 链式提醒管理
        self.chained_reminders: Dict[str, List[str]] = {}  # chain_id -> [reminder_id,...]
        self.notification_chains: Dict[str, Dict[str, Any]] = {}

        # 批量通知管理
        self.batch_notifications: Dict[str, Dict[str, Any]] = {}

        # 免打扰模式
        self.do_not_disturb_active = False

        # 连接信号
        self._connect_signals()

        self.logger.info("通知管理器v2初始化完成")

    def _init_tts(self) -> None:
        """初始化语音合成"""
        try:
            self.tts = TextToSpeech()
            self.logger.debug("语音合成初始化完成")
        except Exception as e:
            self.logger.warning(f"语音合成初始化失败: {e}")
            self.tts = None

    def _connect_signals(self) -> None:
        """连接信号和槽"""
        try:
            # 连接配置管理器信号
            if self.config_manager and hasattr(self.config_manager, 'config_changed'):
                self.config_manager.config_changed.connect(self._on_config_changed)

            # 连接主题管理器信号
            if self.theme_manager and hasattr(self.theme_manager, 'theme_changed'):
                self.theme_manager.theme_changed.connect(self._on_theme_changed)

            self.logger.debug("信号连接完成")

        except Exception as e:
            self.logger.error(f"连接信号失败: {e}")

    def _register_builtin_channels(self) -> None:
        """注册内置通知通道"""
        try:
            builtin_channels = [
                PopupChannel(self),
                TrayChannel(self),
                SoundChannel(self),
                VoiceChannel(self),
                EmailChannel(self)
            ]

            for channel in builtin_channels:
                self.register_channel(channel.channel_id, channel)

            self.logger.debug("内置通道注册完成")

        except Exception as e:
            self.logger.error(f"注册内置通道失败: {e}")

    def register_channel(self, name: str, channel: NotificationChannel) -> bool:
        """
        注册通知通道

        Args:
            name: 通道名称
            channel: 通道实例

        Returns:
            bool: 注册是否成功
        """
        try:
            if name in self.channels:
                self.logger.warning(f"通道 {name} 已存在，将被覆盖")

            self.channels[name] = channel

            # 应用通道配置
            channel_config = self.settings.get('channels', {}).get(name, {})
            if channel_config:
                channel.configure(channel_config)

            # 发出信号
            self.channel_status_changed.emit(name, channel.enabled)

            self.logger.info(f"已注册通知通道: {name}")
            return True

        except Exception as e:
            self.logger.error(f"注册通道失败: {e}")
            return False

    def unregister_channel(self, name: str) -> bool:
        """
        注销通知通道

        Args:
            name: 通道名称

        Returns:
            bool: 注销是否成功
        """
        try:
            if name in self.channels:
                del self.channels[name]
                self.channel_status_changed.emit(name, False)
                self.logger.info(f"已注销通知通道: {name}")
                return True
            else:
                self.logger.warning(f"通道 {name} 不存在")
                return False

        except Exception as e:
            self.logger.error(f"注销通道失败: {e}")
            return False

    def get_available_channels(self) -> List[str]:
        """
        获取可用的通知通道列表

        Returns:
            List[str]: 可用通道名称列表
        """
        try:
            available = []
            for name, channel in self.channels.items():
                if channel.enabled and channel.is_available():
                    available.append(name)
            return available

        except Exception as e:
            self.logger.error(f"获取可用通道失败: {e}")
            return []

    def set_channel_enabled(self, name: str, enabled: bool) -> bool:
        """
        设置通道启用状态

        Args:
            name: 通道名称
            enabled: 是否启用

        Returns:
            bool: 设置是否成功
        """
        try:
            if name in self.channels:
                self.channels[name].set_enabled(enabled)
                self.channel_status_changed.emit(name, enabled)
                return True
            else:
                self.logger.warning(f"通道 {name} 不存在")
                return False

        except Exception as e:
            self.logger.error(f"设置通道状态失败: {e}")
            return False

    def send_notification(
        self,
        title: str,
        message: str,
        channels: List[str] = None,
        priority: int = 1,
        callback: Optional[Callable[[bool], None]] = None,
        template_data: Optional[Dict[str, Any]] = None,
        chain_id: Optional[str] = None,
        reminder_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        发送单个通知

        Args:
            title: 通知标题
            message: 通知内容
            channels: 通知通道列表，None表示使用默认通道
            priority: 优先级 (1-4)
            callback: 完成回调函数
            template_data: 模板数据
            chain_id: 链式通知ID
            reminder_id: 提醒ID
            **kwargs: 额外参数

        Returns:
            str: 通知ID

        Example:
            >>> manager.send_notification("测试", "这是测试消息", ["popup", "sound"])
            "notification_12345"
        """
        try:
            # 生成通知ID
            notification_id = f"notification_{uuid.uuid4().hex[:8]}"

            # 检查免打扰模式
            if self._is_do_not_disturb_time(datetime.now()) and priority < 3:
                self.logger.debug(f"免打扰模式，跳过通知: {notification_id}")
                if callback:
                    callback(False)
                return notification_id

            # 使用默认通道
            if channels is None:
                channels = self._get_default_channels()

            # 数据模板渲染
            rendered_title, rendered_message = self._render_template(
                title, message, template_data
            )

            # 链式提醒登记
            if chain_id and reminder_id:
                self._register_chain_notification(chain_id, reminder_id, notification_id)

            # 构建通知数据
            notification_data = {
                'id': notification_id,
                'title': rendered_title,
                'message': rendered_message,
                'channels': channels,
                'priority': priority,
                'timestamp': datetime.now().isoformat(),
                'chain_id': chain_id,
                'reminder_id': reminder_id,
                **kwargs
            }

            # 分发到各通道
            success_count = 0
            failed_channels = []

            for channel_name in channels:
                channel = self.channels.get(channel_name)
                if channel and channel.enabled and channel.is_available():
                    try:
                        success = channel.send(rendered_title, rendered_message, **kwargs)
                        if success:
                            success_count += 1
                        else:
                            failed_channels.append(channel_name)
                    except Exception as e:
                        self.logger.error(f"通道 {channel_name} 发送失败: {e}")
                        failed_channels.append(channel_name)
                else:
                    failed_channels.append(channel_name)

            # 记录历史
            self._record_notification_history(notification_data, success_count > 0)

            # 处理重要通知
            if priority >= 3:
                self.important_notification_received.emit()

            # 发出信号
            if success_count > 0:
                self.notification_sent.emit(notification_id, notification_data)
                if callback:
                    callback(True)
            else:
                error_msg = f"所有通道发送失败: {failed_channels}"
                self.notification_failed.emit(notification_id, error_msg)
                if callback:
                    callback(False)

            self.logger.info(f"通知发送完成: {notification_id}, 成功: {success_count}/{len(channels)}")
            return notification_id

        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            error_msg = str(e)
            self.notification_failed.emit(notification_id if 'notification_id' in locals() else 'unknown', error_msg)
            if callback:
                callback(False)
            return ""

    def send_batch_notifications(
        self,
        notifications: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> str:
        """
        批量发送通知

        Args:
            notifications: 通知列表，每个元素包含title, message等字段
            batch_id: 批次ID，None表示自动生成

        Returns:
            str: 批次ID
        """
        try:
            if batch_id is None:
                batch_id = f"batch_{uuid.uuid4().hex[:8]}"

            success_count = 0
            failed_count = 0

            # 记录批次信息
            self.batch_notifications[batch_id] = {
                'total': len(notifications),
                'success': 0,
                'failed': 0,
                'start_time': datetime.now(),
                'notifications': []
            }

            for notification in notifications:
                try:
                    notification_id = self.send_notification(**notification)
                    if notification_id:
                        success_count += 1
                        self.batch_notifications[batch_id]['notifications'].append(notification_id)
                    else:
                        failed_count += 1
                except Exception as e:
                    self.logger.error(f"批量通知中的单个通知发送失败: {e}")
                    failed_count += 1

            # 更新批次统计
            self.batch_notifications[batch_id]['success'] = success_count
            self.batch_notifications[batch_id]['failed'] = failed_count
            self.batch_notifications[batch_id]['end_time'] = datetime.now()

            # 发出完成信号
            self.batch_notification_completed.emit(batch_id, success_count, failed_count)

            self.logger.info(f"批量通知完成: {batch_id}, 成功: {success_count}, 失败: {failed_count}")
            return batch_id

        except Exception as e:
            self.logger.error(f"批量发送通知失败: {e}")
            return ""
    
    def cancel_notification(self, notification_id: str) -> bool:
        """
        取消待发送通知

        Args:
            notification_id: 通知ID

        Returns:
            bool: 取消是否成功
        """
        try:
            # 取消定时器
            if notification_id in self.reminder_timers:
                timer = self.reminder_timers[notification_id]
                timer.stop()
                del self.reminder_timers[notification_id]
                self.logger.info(f"已取消通知: {notification_id}")
                return True
            else:
                self.logger.warning(f"通知不存在或已发送: {notification_id}")
                return False

        except Exception as e:
            self.logger.error(f"取消通知失败: {e}")
            return False

    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取通知历史记录

        Args:
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 通知历史记录列表
        """
        try:
            return self.notification_history[-limit:] if self.notification_history else []
        except Exception as e:
            self.logger.error(f"获取通知历史失败: {e}")
            return []

    def _get_default_channels(self) -> List[str]:
        """获取默认通知通道"""
        default_channels = self.settings.get('default_channels', ['popup', 'sound'])
        available_channels = self.get_available_channels()
        return [ch for ch in default_channels if ch in available_channels]

    def _render_template(
        self,
        title: str,
        message: str,
        template_data: Optional[Dict[str, Any]]
    ) -> tuple[str, str]:
        """
        渲染模板

        Args:
            title: 原始标题
            message: 原始消息
            template_data: 模板数据

        Returns:
            tuple[str, str]: 渲染后的标题和消息
        """
        try:
            if template_data:
                rendered_title = title.format(**template_data)
                rendered_message = message.format(**template_data)
                return rendered_title, rendered_message
            return title, message

        except Exception as e:
            self.logger.warning(f"模板渲染失败: {e}")
            return title, message

    def _register_chain_notification(
        self,
        chain_id: str,
        reminder_id: str,
        notification_id: str
    ) -> None:
        """注册链式通知"""
        try:
            if chain_id not in self.notification_chains:
                self.notification_chains[chain_id] = {
                    'reminders': [],
                    'created_at': datetime.now(),
                    'active': True
                }

            self.notification_chains[chain_id]['reminders'].append({
                'reminder_id': reminder_id,
                'notification_id': notification_id,
                'timestamp': datetime.now()
            })

            # 同时保持旧格式兼容性
            self.chained_reminders.setdefault(chain_id, []).append(reminder_id)

        except Exception as e:
            self.logger.error(f"注册链式通知失败: {e}")

    def _record_notification_history(
        self,
        notification_data: Dict[str, Any],
        success: bool
    ) -> None:
        """记录通知历史"""
        try:
            history_entry = {
                **notification_data,
                'success': success,
                'recorded_at': datetime.now().isoformat()
            }

            self.notification_history.append(history_entry)

            # deque自动限制大小，无需手动清理

            # 记录失败通知
            if not success:
                self.failed_notifications.append(history_entry)

        except Exception as e:
            self.logger.error(f"记录通知历史失败: {e}")

    def _on_theme_changed(self) -> None:
        """主题变化处理"""
        try:
            if self.theme_manager:
                current_theme = self.theme_manager.get_current_theme()
                if current_theme:
                    # 应用主题到通知窗口
                    theme_colors = current_theme.get_colors()
                    for window in self.notification_windows:
                        if hasattr(window, 'apply_theme'):
                            window.apply_theme(theme_colors)

                    self.logger.debug("通知主题已更新")

        except Exception as e:
            self.logger.error(f"应用通知主题失败: {e}")

    def _on_config_changed(self, section: str, config: Dict[str, Any]) -> None:
        """处理配置变更"""
        try:
            if section == 'notification':
                self.logger.debug("处理通知配置变更")

                # 更新通知设置
                for key, value in config.items():
                    if key in self.settings:
                        self.settings[key] = value

                # 重新加载通道配置
                self._reload_channels()

                self.logger.debug("通知配置已更新")

        except Exception as e:
            self.logger.error(f"处理配置变更失败: {e}")

    def _reload_channels(self) -> None:
        """重新加载通知通道"""
        try:
            # 重新配置现有通道
            for channel in self.channels.values():
                if hasattr(channel, 'configure'):
                    channel.configure(self.settings)

            self.logger.debug("通知通道已重新加载")

        except Exception as e:
            self.logger.error(f"重新加载通知通道失败: {e}")

    def setup_schedule_notifications(self, schedule: Schedule) -> None:
        """
        设置课程表相关通知

        Args:
            schedule: 课程表对象
        """
        try:
            # 清除现有的课程通知定时器
            for timer_id in list(self.reminder_timers.keys()):
                if timer_id.startswith('schedule_'):
                    self.reminder_timers[timer_id].stop()
                    del self.reminder_timers[timer_id]

            # 为每个课程设置通知
            for class_item in schedule.get_all_classes():
                self._setup_class_notifications(class_item)

            self.logger.info(f"课程表通知设置完成: {schedule.name}")

        except Exception as e:
            self.logger.error(f"设置课程表通知失败: {e}")

    def _setup_class_notifications(self, class_item: ClassItem) -> None:
        """为单个课程设置通知"""
        try:
            # 这里应该根据课程时间设置提醒
            # 由于需要具体的时间计算逻辑，这里只是框架
            self.logger.debug(f"设置课程通知: {class_item.id}")

        except Exception as e:
            self.logger.error(f"设置课程通知失败: {e}")

    def _cleanup_expired_timers(self) -> None:
        """清理过期的定时器，防止内存泄漏"""
        try:
            # 增加计数器
            self._timer_cleanup_counter += 1
        except Exception as e:
            self.logger.error(f"增加计数器失败: {e}")
            # 增加计数器
            # 增加计数器
            self._timer_cleanup_counter += 1

            # 每100次调用清理一次
            if self._timer_cleanup_counter % 100 == 0:
                expired_timers = []

                for timer_id, timer in self.reminder_timers.items():
                    if not timer.isActive():
                        expired_timers.append(timer_id)

                # 移除过期定时器
                for timer_id in expired_timers:
                    timer = self.reminder_timers.pop(timer_id, None)
                    if timer and hasattr(timer, "deleteLater"):
                        timer.deleteLater()

                if expired_timers:
                    self.logger.debug(f"清理了 {len(expired_timers)} 个过期定时器")

        except Exception as e:
            self.logger.error(f"清理定时器失败: {e}")

    def _load_settings(self) -> Dict[str, Any]:
        """
        加载通知设置

        Returns:
            Dict[str, Any]: 通知设置字典
        """
        default_settings = {
            # 基本设置
            'enabled': True,
            'default_channels': ['popup', 'sound'],
            'max_history_records': 1000,

            # 通道配置
            'channels': {
                'popup': {
                    'enabled': True,
                    'duration': 5000,
                    'position': 'top_right',
                    'theme': 'default'
                },
                'tray': {
                    'enabled': True,
                    'duration': 5000,
                    'show_icon': True
                },
                'sound': {
                    'enabled': True,
                    'volume': 0.7,
                    'sound_file': '',
                    'use_system_sound': True
                },
                'voice': {
                    'enabled': False,
                    'speed': 1.0,
                    'volume': 0.9,
                    'engine': 'system'
                },
                'email': {
                    'enabled': False,
                    'smtp_server': '',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'to_email': '',
                    'use_tls': True
                }
            },

            # 课程提醒设置
            'class_start_reminder': {
                'enabled': True,
                'advance_minutes': 5,
                'channels': ['popup', 'sound'],
                'priority': 3,  # HIGH priority
                'voice_text': '即将开始{subject}课程',
                'template': {
                    'title': '上课提醒',
                    'message': '{subject} 即将在 {classroom} 开始'
                }
            },
            'class_end_reminder': {
                'enabled': True,
                'channels': ['popup'],
                'priority': 2,  # NORMAL priority
                'voice_text': '{subject}课程结束',
                'template': {
                    'title': '下课提醒',
                    'message': '{subject} 课程结束'
                }
            },
            'break_reminder': {
                'enabled': True,
                'channels': ['tray'],
                'priority': 1,  # LOW priority
                'voice_text': '课间休息时间',
                'template': {
                    'title': '课间休息',
                    'message': '课间休息时间，下节课是 {next_subject}'
                }
            },

            # 免打扰设置
            'do_not_disturb': {
                'enabled': False,
                'start_time': '22:00',
                'end_time': '07:00',
                'allow_urgent': True,  # 允许紧急通知
                'weekends_only': False  # 仅周末启用
            },

            # 智能特性
            'smart_features': {
                'duplicate_detection': True,  # 重复通知检测
                'auto_retry': True,  # 失败自动重试
                'retry_count': 3,
                'retry_interval': 5,  # 秒
                'priority_queue': True,  # 优先级队列
                'batch_processing': True  # 批量处理
            },

            # 集成设置
            'integrations': {
                'floating_widget': {
                    'enabled': True,
                    'show_in_widget': True
                },
                'theme_sync': {
                    'enabled': True,
                    'auto_apply': True
                }
            }
        }

        try:
            loaded_settings = self.config_manager.get('notifications', default_settings)

            # 合并默认设置，确保所有必需的键都存在
            def merge_settings(default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
                result = default.copy()
                for key, value in loaded.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = merge_settings(result[key], value)
                    else:
                        result[key] = value
                return result

            return merge_settings(default_settings, loaded_settings)

        except Exception as e:
            self.logger.error(f"加载通知设置失败: {e}")
            return default_settings
    
    def _init_tray_icon(self):
        """初始化系统托盘图标"""
        from PySide6.QtCore import Qt  # 确保Qt在本地作用域可用
        try:
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon()
                # 设置图标
                icon_path = Path(__file__).parent.parent / "resources" / "icons" / "tray_icon.png"
                if icon_path.exists():
                    self.tray_icon.setIcon(QIcon(str(icon_path)))
                else:
                    # 使用默认图标
                    self.tray_icon.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
                self.tray_icon.setToolTip("TimeNest - 课程表助手")
                self.tray_icon.show()
                self.logger.info("系统托盘图标初始化完成")
            else:
                self.logger.warning("系统不支持托盘图标")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.logger.error(f"初始化托盘图标失败: {e}")

    def check_pending_notifications(self):
        """检查待处理的通知"""
        try:
            # 检查是否有待处理的通知
            current_time = datetime.now()

            # 这里可以添加具体的通知检查逻辑
            # 例如：检查课程提醒、系统通知等

            # 清理过期的定时器
            self._cleanup_expired_timers()

        except Exception as e:
            self.logger.error(f"检查待处理通知失败: {e}")

    def _cleanup_expired_timers(self):
        """清理过期的定时器"""
        try:
            expired_timers = []
            for timer_id, timer in self.reminder_timers.items():
                if not timer.isActive():
                    expired_timers.append(timer_id)

            for timer_id in expired_timers:
                timer = self.reminder_timers.pop(timer_id, None)
                if timer and hasattr(timer, "deleteLater"):
                    timer.deleteLater()

            if expired_timers:
                self.logger.debug(f"清理了 {len(expired_timers)} 个过期定时器")

        except Exception as e:
            self.logger.error(f"清理过期定时器失败: {e}")
    
    def on_class_changed(self, new_class: Optional[ClassItem]):
        """处理课程变化事件"""
        try:
            current_time = datetime.now()
            
            # 检查是否在免打扰时间
            if self._is_do_not_disturb_time(current_time):
                return
            
            # 处理课程开始提醒
            if new_class and new_class != self.last_notified_class:
                self._send_class_start_notification(new_class)
            
            # 处理课程结束提醒
            if self.last_notified_class and self.last_notified_class != new_class:
                self._send_class_end_notification(self.last_notified_class)
            
            self.last_notified_class = new_class
            
        except Exception as e:
            self.logger.error(f"处理课程变化事件失败: {e}")
    
    def _is_do_not_disturb_time(self, current_time: datetime) -> bool:
        """检查是否在免打扰时间"""
        if not self.settings.get('do_not_disturb', {}).get('enabled', False):
            return False
        
        try:
            dnd_settings = self.settings.get('do_not_disturb')
            start_time = time.fromisoformat(dnd_settings.get('start_time', '22:00'))
            end_time = time.fromisoformat(dnd_settings.get('end_time', '07:00'))
            current_time_only = current_time.time()
            
            # 处理跨天的情况
            if start_time <= end_time:
                return start_time <= current_time_only <= end_time
            else:
                return current_time_only >= start_time or current_time_only <= end_time
                
        except Exception as e:
            self.logger.error(f"检查免打扰时间失败: {e}")
            return False
    
    def _send_class_start_notification(self, class_item: ClassItem):
        """发送上课提醒"""
        try:
            if not self.settings.get('class_start_reminder', {}).get('enabled', True):
                return
            
            reminder_settings = self.settings.get('class_start_reminder')
            
            # 获取科目名称（这里需要从schedule_manager获取）
            subject_name = "课程"  # 临时使用，实际应该从科目ID获取名称
            
            # 构建提醒消息
            message = f"即将开始{subject_name}"
            if class_item.classroom:
                message += f"，教室：{class_item.classroom}"
            
            # 发送各种类型的通知
            self._send_notification(
                notification_type="class_start",
                title="上课提醒",
                message=message,
                settings=reminder_settings,
                class_item=class_item
            )
            
        except Exception as e:
            self.logger.error(f"发送上课提醒失败: {e}")
    
    def _send_class_end_notification(self, class_item: ClassItem):
        """发送下课提醒"""
        try:
            if not self.settings.get('class_end_reminder', {}).get('enabled', True):
                return
            
            reminder_settings = self.settings.get('class_end_reminder')
            
            # 获取科目名称
            subject_name = "课程"  # 临时使用
            
            message = f"{subject_name}课程结束"
            
            # 发送各种类型的通知
            self._send_notification(
                notification_type="class_end",
                title="下课提醒",
                message=message,
                settings=reminder_settings,
                class_item=class_item
            )
            
        except Exception as e:
            self.logger.error(f"发送下课提醒失败: {e}")
    
    def _send_notification(self, notification_type: str, title: str, message: str, 
                          settings: Dict[str, Any], class_item: Optional[ClassItem] = None):
        """发送通知"""
        # Check priority and emit signal for smart always-on-top
        if settings.get('priority', 2) >= 3:  # NORMAL >= HIGH:
            self.important_notification_received.emit()

        channel_settings = self.settings.get('channels', {})

        try:
            # 播放音效
            if channel_settings.get('sound', {}).get('enabled', False):
                self._play_sound(channel_settings.get('sound', {}).get('sound_file', ''))
            
            # 语音提醒
            if channel_settings.get('voice', {}).get('enabled', False):
                voice_text = channel_settings.get('voice', {}).get('voice_text', message)
                if class_item:
                    # 替换模板变量
                    voice_text = voice_text.replace('{subject}', '课程')  # 临时使用
                    voice_text = voice_text.replace('{classroom}', class_item.classroom or '')
                    voice_text = voice_text.replace('{teacher}', class_item.teacher or '')
                
                self._speak_text(voice_text)
            
            # 弹窗通知
            if channel_settings.get('popup', {}).get('enabled', False):
                self._show_popup_notification(title, message, notification_type)
            
            # 系统托盘通知
            if channel_settings.get('tray', {}).get('enabled', False) and self.tray_icon:
                self._show_tray_notification(title, message)
            
            # 发出信号
            self.notification_sent.emit(notification_type, message)
            
            self.logger.info(f"发送通知: {notification_type} - {message}")
            
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
    
    def _play_sound(self, sound_file: str = "") -> bool:
        """
        播放音效

        Args:
            sound_file: 音效文件路径，空字符串表示使用默认音效

        Returns:
            bool: 播放是否成功
        """
        try:
            sound_config = self.settings.get('channels', {}).get('sound', {})

            if not sound_config.get('enabled', True):
                return False

            volume = sound_config.get('volume', 0.7)

            if sound_file and Path(sound_file).exists():
                # 使用自定义音效文件
                self.sound_effect.setSource(Path(sound_file).as_uri())
                self.sound_effect.setVolume(volume)
                self.sound_effect.play()
                self.logger.debug(f"播放自定义音效: {sound_file}")
            elif sound_config.get('use_system_sound', True):
                # 使用系统默认提示音
                QApplication.beep()
                self.logger.debug("播放系统提示音")
            else:
                return False

            return True

        except Exception as e:
            self.logger.error(f"播放音效失败: {e}")
            return False

    def _speak_text(self, text: str) -> bool:
        """
        语音播报

        Args:
            text: 要播报的文本

        Returns:
            bool: 播报是否成功
        """
        try:
            if not self.tts:
                return False

            voice_config = self.settings.get('channels', {}).get('voice', {})

            if not voice_config.get('enabled', False):
                return False

            speed = voice_config.get('speed', 1.0)
            self.tts.speak(text, speed=speed)
            self.logger.debug(f"语音播报: {text}")
            return True

        except Exception as e:
            self.logger.error(f"语音播报失败: {e}")
            return False

    def _show_popup_notification(self, title: str, message: str, notification_type: str) -> bool:
        """
        显示弹窗通知

        Args:
            title: 通知标题
            message: 通知内容
            notification_type: 通知类型

        Returns:
            bool: 显示是否成功
        """
        try:
            popup_config = self.settings.get('channels', {}).get('popup', {})

            if not popup_config.get('enabled', True):
                return False

            notification_window = NotificationWindow(
                title=title,
                message=message,
                notification_type=notification_type,
                duration=popup_config.get('duration', 5000),
                position=popup_config.get('position', 'top_right')
            )

            # 应用主题
            if self.theme_manager:
                current_theme = self.theme_manager.get_current_theme()
                if current_theme and hasattr(notification_window, 'apply_theme'):
                    theme_colors = current_theme.get_colors()
                    notification_window.apply_theme(theme_colors)

            self.notification_windows.append(notification_window)
            notification_window.show()

            # 设置自动关闭
            duration = popup_config.get('duration', 5000)
            QTimer.singleShot(
                duration,
                lambda: self._close_notification_window(notification_window)
            )

            self.logger.debug(f"显示弹窗通知: {title}")
            return True

        except Exception as e:
            self.logger.error(f"显示弹窗通知失败: {e}")
            return False

    def _show_tray_notification(self, title: str, message: str) -> bool:
        """
        显示系统托盘通知

        Args:
            title: 通知标题
            message: 通知内容

        Returns:
            bool: 显示是否成功
        """
        try:
            tray_config = self.settings.get('channels', {}).get('tray', {})

            if not tray_config.get('enabled', True):
                return False

            if self.tray_icon and self.tray_icon.isVisible():
                duration = tray_config.get('duration', 5000)
                self.tray_icon.showMessage(
                    title,
                    message,
                    QSystemTrayIcon.MessageIcon.Information,
                    duration
                )
                self.logger.debug(f"显示托盘通知: {title}")
                return True
            else:
                self.logger.warning("系统托盘不可用")
                return False

        except Exception as e:
            self.logger.error(f"显示托盘通知失败: {e}")
            return False
    
    def _close_notification_window(self, window):
        """关闭通知窗口 (已迁移到RinUI)"""
        try:
            # if window in self.notification_windows:
            #     self.notification_windows.remove(window)
            #     window.close()
            pass
        except Exception as e:
            self.logger.error(f"关闭通知窗口失败: {e}")
    
    def schedule_advance_reminder(self, class_item: ClassItem, start_time: datetime):
        """安排提前提醒"""
        try:
            if not self.settings.get('class_start_reminder', {}).get('enabled', True):
                return
            
            advance_minutes = self.settings.get('class_start_reminder').get('advance_minutes', 5)
            reminder_time = start_time - timedelta(minutes=advance_minutes)
            
            # 计算延迟时间
            now = datetime.now()
            if reminder_time <= now:
                return  # 已经过了提醒时间
            
            delay_ms = int((reminder_time - now).total_seconds() * 1000)
            
            # 创建定时器
            timer_id = f"advance_{class_item.id}"
            if timer_id in self.reminder_timers:
                self.reminder_timers[timer_id].stop()
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._send_advance_reminder(class_item))
            timer.start(delay_ms)
            
            self.reminder_timers[timer_id] = timer
            
            self.logger.debug(f"安排提前提醒: {class_item.id} 在 {reminder_time}")
            
        except Exception as e:
            self.logger.error(f"安排提前提醒失败: {e}")
    
    def _send_advance_reminder(self, class_item: ClassItem):
        """发送提前提醒"""
        try:
            reminder_settings = self.settings.get('class_start_reminder')
            advance_minutes = reminder_settings.get('advance_minutes', 5)
            
            subject_name = "课程"  # 临时使用
            message = f"{advance_minutes}分钟后开始{subject_name}"
            
            self._send_notification(
                notification_type="advance_reminder",
                title="课程提醒",
                message=message,
                settings=reminder_settings,
                class_item=class_item
            )
            
        except Exception as e:
            self.logger.error(f"发送提前提醒失败: {e}")
    
    def send_custom_notification(self, title: str, message: str, 
                               notification_type: str = "custom"):
        """发送自定义通知"""
        try:
            # 使用默认设置
            default_settings = {
                'sound_enabled': True,
                'voice_enabled': False,
                'popup_enabled': True,
                'tray_enabled': True
            }
            
            self._send_notification(notification_type, title, message, default_settings)
            
        except Exception as e:
            self.logger.error(f"发送自定义通知失败: {e}")
    
    def get_settings(self) -> Dict[str, Any]:
        """
        获取通知设置

        Returns:
            Dict[str, Any]: 通知设置的副本
        """
        return self.settings.copy()

    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """
        更新通知设置

        Args:
            new_settings: 新的设置字典

        Returns:
            bool: 更新是否成功
        """
        try:
            old_settings = self.settings.copy()

            # 深度合并设置
            def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
                for key, value in source.items():
                    if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                        deep_merge(target[key], value)
                    else:
                        target[key] = value

            deep_merge(self.settings, new_settings)

            # 保存到配置管理器
            self.config_manager.set('notifications', self.settings)

            # 更新音频设置
            sound_config = self.settings.get('channels', {}).get('sound', {})
            if 'volume' in sound_config:
                self.audio_output.setVolume(sound_config.get('volume'))

            # 更新通道配置
            for channel_name, channel in self.channels.items():
                channel_config = self.settings.get('channels', {}).get(channel_name, {})
                if channel_config and hasattr(channel, "configure"):
                    channel.configure(channel_config)
                    channel.set_enabled(channel_config.get('enabled', True))

            # 发出配置更新信号
            self.config_updated.emit(self.settings)

            self.logger.info("通知设置已更新")
            return True

        except Exception as e:
            self.logger.error(f"更新通知设置失败: {e}")
            # 恢复旧设置
            self.settings = old_settings
            return False

    def test_notification(self, notification_type: str = "test", channels: List[str] = None) -> str:
        """
        测试通知功能

        Args:
            notification_type: 通知类型
            channels: 测试的通道列表

        Returns:
            str: 通知ID
        """
        try:
            if channels is None:
                channels = ['popup', 'sound']

            return self.send_notification(
                title="测试通知",
                message="这是一个测试通知，用于验证通知功能是否正常工作。",
                channels=channels,
                priority=2,
                notification_type=notification_type
            )

        except Exception as e:
            self.logger.error(f"测试通知失败: {e}")
            return ""

    def test_all_channels(self) -> Dict[str, bool]:
        """
        测试所有通道

        Returns:
            Dict[str, bool]: 各通道测试结果
        """
        results = {}

        for channel_name, channel in self.channels.items():
            try:
                if channel.enabled and channel.is_available():
                    success = channel.send(
                        f"测试 {channel.name}",
                        f"这是 {channel.name} 的测试消息",
                        notification_type="test"
                    )
                    results[channel_name] = success
                else:
                    results[channel_name] = False

            except Exception as e:
                self.logger.error(f"测试通道 {channel_name} 失败: {e}")
                results[channel_name] = False

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取通知统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            total_notifications = len(self.notification_history)
            successful_notifications = sum(1 for n in self.notification_history if n.get('success', False))
            failed_notifications = len(self.failed_notifications)

            channel_stats = {}
            for name, channel in self.channels.items():
                channel_stats[name] = {
                    'enabled': channel.enabled,
                    'available': channel.is_available()
                }

            return {
                'total_notifications': total_notifications,
                'successful_notifications': successful_notifications,
                'failed_notifications': failed_notifications,
                'success_rate': successful_notifications / total_notifications if total_notifications > 0 else 0,
                'active_timers': len(self.reminder_timers),
                'active_windows': len(self.notification_windows),
                'channels': channel_stats,
                'chains': len(self.notification_chains),
                'batches': len(self.batch_notifications)
            }

        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止所有定时器
            for timer in self.reminder_timers.values():
                if timer.isActive():
                    timer.stop()
            self.reminder_timers.clear()

            # 关闭所有通知窗口
            for window in self.notification_windows:
                try:
                    window.close()
                except Exception as e:
                    self.logger.warning(f"关闭通知窗口失败: {e}")
            self.notification_windows.clear()

            # 隐藏托盘图标
            if self.tray_icon:
                try:
                    self.tray_icon.hide()
                except Exception as e:
                    self.logger.warning(f"隐藏托盘图标失败: {e}")

            # 清理语音合成
            if self.tts and hasattr(self.tts, 'cleanup'):
                try:
                    self.tts.cleanup()
                except Exception as e:
                    self.logger.warning(f"清理语音合成失败: {e}")

            # 清理多媒体组件
            try:
                self.sound_effect.stop()
                self.media_player.stop()
            except Exception as e:
                self.logger.warning(f"清理多媒体组件失败: {e}")

            self.logger.info("通知管理器清理完成")

        except Exception as e:
            self.logger.error(f"清理通知管理器失败: {e}")

    def apply_config(self, config: Dict[str, Any]):
        """应用通知配置"""
        try:
            if not config:
                return

            # 更新设置
            self.settings.update(config)

            # 应用到各个通道
            for channel_name, channel in self.channels.items():
                if hasattr(channel, 'configure'):
                    channel_config = config.get('channels', {}).get(channel_name, {})
                    if channel_config:
                        channel.configure(channel_config)

            # 保存配置
            if self.config_manager:
                self.config_manager.set_config('notification', config, save=True)

            self.logger.info("通知配置已应用")

        except Exception as e:
            self.logger.error(f"应用通知配置失败: {e}")