#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 通知系统增强功能
在原有框架基础上新增智能通知和提醒功能
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.base_manager import BaseManager


class ReminderType(Enum):
    """提醒类型"""
    COURSE_START = "course_start"
    COURSE_END = "course_end"
    BREAK_TIME = "break_time"
    TASK_DUE = "task_due"
    EXAM_APPROACHING = "exam_approaching"
    STUDY_SESSION = "study_session"
    CUSTOM = "custom"


class NotificationStyle(Enum):
    """通知样式"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    URGENT = "urgent"


@dataclass
class SmartReminder:
    """智能提醒"""
    id: str
    title: str
    message: str
    reminder_type: ReminderType
    trigger_time: datetime
    style: NotificationStyle
    repeat_interval: Optional[int] = None  # 重复间隔（分钟）
    max_repeats: int = 1
    current_repeats: int = 0
    is_active: bool = True
    custom_action: Optional[Callable] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class NotificationRule:
    """通知规则"""
    id: str
    name: str
    condition: str  # 条件表达式
    action: str  # 动作类型
    parameters: Dict[str, Any]
    is_enabled: bool = True
    priority: int = 0


class FocusMode:
    """专注模式"""
    def __init__(self):
        self.is_active = False
        self.start_time: Optional[datetime] = None
        self.duration: int = 25  # 默认25分钟
        self.break_duration: int = 5  # 默认5分钟休息
        self.allowed_notifications: List[ReminderType] = [
            ReminderType.COURSE_START,
            ReminderType.EXAM_APPROACHING
        ]


class NotificationEnhancementManager(BaseManager):
    """通知系统增强功能管理器"""
    
    # 信号定义
    reminder_triggered = pyqtSignal(str)  # 提醒ID
    focus_mode_started = pyqtSignal()
    focus_mode_ended = pyqtSignal()
    break_time_started = pyqtSignal()
    notification_rule_matched = pyqtSignal(str, str)  # 规则ID, 动作
    
    def __init__(self, config_manager=None, notification_manager=None):
        super().__init__("NotificationEnhancement", config_manager)
        
        self.notification_manager = notification_manager
        
        # 数据存储
        self.smart_reminders: Dict[str, SmartReminder] = {}
        self.notification_rules: Dict[str, NotificationRule] = {}
        
        # 专注模式
        self.focus_mode = FocusMode()
        
        # 定时器
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(30000)  # 每30秒检查一次
        
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self._handle_focus_timer)
        
        # 智能提醒模板
        self.reminder_templates = {
            ReminderType.COURSE_START: {
                'title': '课程即将开始',
                'message': '{course_name} 将在 {minutes} 分钟后开始',
                'style': NotificationStyle.STANDARD
            },
            ReminderType.TASK_DUE: {
                'title': '任务即将到期',
                'message': '任务 "{task_name}" 将在 {hours} 小时后到期',
                'style': NotificationStyle.URGENT
            },
            ReminderType.BREAK_TIME: {
                'title': '休息时间',
                'message': '您已经学习了 {duration} 分钟，建议休息一下',
                'style': NotificationStyle.MINIMAL
            }
        }
        
        self.logger.info("通知系统增强功能管理器初始化完成")
    
    def create_smart_reminder(self, title: str, message: str, 
                            reminder_type: ReminderType,
                            trigger_time: datetime,
                            style: NotificationStyle = NotificationStyle.STANDARD,
                            repeat_interval: Optional[int] = None,
                            max_repeats: int = 1,
                            metadata: Dict[str, Any] = None) -> str:
        """创建智能提醒"""
        try:
            reminder_id = f"reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            reminder = SmartReminder(
                id=reminder_id,
                title=title,
                message=message,
                reminder_type=reminder_type,
                trigger_time=trigger_time,
                style=style,
                repeat_interval=repeat_interval,
                max_repeats=max_repeats,
                metadata=metadata or {}
            )
            
            self.smart_reminders[reminder_id] = reminder
            self.logger.info(f"智能提醒已创建: {title}")
            return reminder_id
            
        except Exception as e:
            self.logger.error(f"创建智能提醒失败: {e}")
            return ""
    
    def create_course_reminder(self, course_name: str, start_time: datetime,
                             advance_minutes: int = 10) -> str:
        """创建课程提醒"""
        try:
            trigger_time = start_time - timedelta(minutes=advance_minutes)
            template = self.reminder_templates[ReminderType.COURSE_START]
            
            message = template['message'].format(
                course_name=course_name,
                minutes=advance_minutes
            )
            
            return self.create_smart_reminder(
                title=template['title'],
                message=message,
                reminder_type=ReminderType.COURSE_START,
                trigger_time=trigger_time,
                style=template['style'],
                metadata={'course_name': course_name, 'start_time': start_time}
            )
            
        except Exception as e:
            self.logger.error(f"创建课程提醒失败: {e}")
            return ""
    
    def create_task_reminder(self, task_name: str, due_time: datetime,
                           advance_hours: int = 2) -> str:
        """创建任务提醒"""
        try:
            trigger_time = due_time - timedelta(hours=advance_hours)
            template = self.reminder_templates[ReminderType.TASK_DUE]
            
            message = template['message'].format(
                task_name=task_name,
                hours=advance_hours
            )
            
            return self.create_smart_reminder(
                title=template['title'],
                message=message,
                reminder_type=ReminderType.TASK_DUE,
                trigger_time=trigger_time,
                style=template['style'],
                metadata={'task_name': task_name, 'due_time': due_time}
            )
            
        except Exception as e:
            self.logger.error(f"创建任务提醒失败: {e}")
            return ""
    
    def start_focus_mode(self, duration: int = 25, break_duration: int = 5) -> bool:
        """开始专注模式"""
        try:
            if self.focus_mode.is_active:
                self.logger.warning("专注模式已经激活")
                return False
            
            self.focus_mode.is_active = True
            self.focus_mode.start_time = datetime.now()
            self.focus_mode.duration = duration
            self.focus_mode.break_duration = break_duration
            
            # 启动定时器
            self.focus_timer.start(duration * 60 * 1000)  # 转换为毫秒
            
            self.focus_mode_started.emit()
            self.logger.info(f"专注模式已启动: {duration} 分钟")
            
            # 发送开始通知
            if self.notification_manager:
                self.notification_manager.send_notification(
                    title="专注模式",
                    message=f"专注模式已启动，将持续 {duration} 分钟",
                    notification_type="info"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动专注模式失败: {e}")
            return False
    
    def end_focus_mode(self) -> bool:
        """结束专注模式"""
        try:
            if not self.focus_mode.is_active:
                return False
            
            self.focus_mode.is_active = False
            self.focus_timer.stop()
            
            # 计算实际专注时间
            if self.focus_mode.start_time:
                actual_duration = (datetime.now() - self.focus_mode.start_time).total_seconds() / 60
                self.logger.info(f"专注模式结束，实际专注时间: {actual_duration:.1f} 分钟")
            
            self.focus_mode_ended.emit()
            
            # 发送结束通知
            if self.notification_manager:
                self.notification_manager.send_notification(
                    title="专注模式结束",
                    message="专注时间结束，建议休息一下",
                    notification_type="success"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"结束专注模式失败: {e}")
            return False
    
    def _handle_focus_timer(self):
        """处理专注模式定时器"""
        try:
            if self.focus_mode.is_active:
                self.end_focus_mode()
                
                # 开始休息时间
                self.break_time_started.emit()
                
                if self.notification_manager:
                    self.notification_manager.send_notification(
                        title="休息时间",
                        message=f"建议休息 {self.focus_mode.break_duration} 分钟",
                        notification_type="info"
                    )
                
        except Exception as e:
            self.logger.error(f"处理专注模式定时器失败: {e}")
    
    def _check_reminders(self):
        """检查待触发的提醒"""
        try:
            current_time = datetime.now()
            
            for reminder in list(self.smart_reminders.values()):
                if not reminder.is_active:
                    continue
                
                # 检查是否到达触发时间
                if current_time >= reminder.trigger_time:
                    self._trigger_reminder(reminder)
                    
        except Exception as e:
            self.logger.error(f"检查提醒失败: {e}")
    
    def _trigger_reminder(self, reminder: SmartReminder):
        """触发提醒"""
        try:
            # 检查专注模式
            if (self.focus_mode.is_active and 
                reminder.reminder_type not in self.focus_mode.allowed_notifications):
                self.logger.debug(f"专注模式中跳过提醒: {reminder.title}")
                return
            
            # 发送通知
            if self.notification_manager:
                notification_type = self._get_notification_type(reminder.style)
                self.notification_manager.send_notification(
                    title=reminder.title,
                    message=reminder.message,
                    notification_type=notification_type
                )
            
            # 执行自定义动作
            if reminder.custom_action:
                try:
                    reminder.custom_action(reminder)
                except Exception as e:
                    self.logger.error(f"执行自定义动作失败: {e}")
            
            self.reminder_triggered.emit(reminder.id)
            self.logger.info(f"提醒已触发: {reminder.title}")
            
            # 处理重复提醒
            reminder.current_repeats += 1
            
            if (reminder.repeat_interval and 
                reminder.current_repeats < reminder.max_repeats):
                # 设置下次提醒时间
                reminder.trigger_time += timedelta(minutes=reminder.repeat_interval)
            else:
                # 停用提醒
                reminder.is_active = False
                
        except Exception as e:
            self.logger.error(f"触发提醒失败: {e}")
    
    def _get_notification_type(self, style: NotificationStyle) -> str:
        """根据样式获取通知类型"""
        style_mapping = {
            NotificationStyle.MINIMAL: "info",
            NotificationStyle.STANDARD: "info",
            NotificationStyle.DETAILED: "info",
            NotificationStyle.URGENT: "warning"
        }
        return style_mapping.get(style, "info")
    
    def add_notification_rule(self, name: str, condition: str, action: str,
                            parameters: Dict[str, Any] = None) -> str:
        """添加通知规则"""
        try:
            rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            rule = NotificationRule(
                id=rule_id,
                name=name,
                condition=condition,
                action=action,
                parameters=parameters or {}
            )
            
            self.notification_rules[rule_id] = rule
            self.logger.info(f"通知规则已添加: {name}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"添加通知规则失败: {e}")
            return ""
    
    def get_active_reminders(self) -> List[SmartReminder]:
        """获取活动的提醒"""
        return [r for r in self.smart_reminders.values() if r.is_active]
    
    def cancel_reminder(self, reminder_id: str) -> bool:
        """取消提醒"""
        try:
            if reminder_id in self.smart_reminders:
                self.smart_reminders[reminder_id].is_active = False
                self.logger.info(f"提醒已取消: {reminder_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"取消提醒失败: {e}")
            return False
    
    def get_focus_mode_status(self) -> Dict[str, Any]:
        """获取专注模式状态"""
        if not self.focus_mode.is_active:
            return {'active': False}
        
        elapsed = (datetime.now() - self.focus_mode.start_time).total_seconds() / 60
        remaining = max(0, self.focus_mode.duration - elapsed)
        
        return {
            'active': True,
            'elapsed_minutes': elapsed,
            'remaining_minutes': remaining,
            'total_duration': self.focus_mode.duration
        }
    
    def cleanup(self):
        """清理资源"""
        try:
            self.reminder_timer.stop()
            self.focus_timer.stop()
            
            if self.focus_mode.is_active:
                self.end_focus_mode()
            
            super().cleanup()
            self.logger.info("通知系统增强功能管理器已清理")
            
        except Exception as e:
            self.logger.error(f"清理通知系统增强功能失败: {e}")
