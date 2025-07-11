#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest Remind API v2
支持多渠道、链式提醒、条件控制的高级提醒系统
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon


class ReminderChannel(Enum):
    """提醒渠道枚举"""
    DESKTOP = "desktop"          # 桌面通知
    FLOATING = "floating"        # 浮窗提醒
    SOUND = "sound"             # 声音提醒
    EMAIL = "email"             # 邮件提醒
    SYSTEM_TRAY = "system_tray" # 系统托盘提醒
    POPUP = "popup"             # 弹窗提醒


class ReminderPriority(Enum):
    """提醒优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class ReminderStatus(Enum):
    """提醒状态"""
    PENDING = "pending"         # 等待中
    ACTIVE = "active"           # 激活中
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消
    FAILED = "failed"           # 失败


@dataclass
class ReminderCondition:
    """提醒条件"""
    type: str                   # 条件类型: time, event, custom
    value: Any                  # 条件值
    operator: str = "=="        # 操作符: ==, !=, >, <, >=, <=
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估条件是否满足"""
        try:
            if self.type == "time":
                current_time = datetime.now()
                target_time = datetime.fromisoformat(self.value) if isinstance(self.value, str) else self.value
                
                if self.operator == "==":
                    return abs((current_time - target_time).total_seconds()) < 60
                elif self.operator == "<=":
                    return current_time <= target_time
                elif self.operator == ">=":
                    return current_time >= target_time
                    
            elif self.type == "event":
                return context.get(self.value, False)
                
            elif self.type == "custom":
                # 自定义条件评估
                return bool(context.get(self.value, False))
                
            return False
            
        except Exception:
            return False


@dataclass
class ReminderAction:
    """提醒动作"""
    channel: ReminderChannel
    message: str
    title: str = ""
    data: Dict[str, Any] = None
    delay: int = 0              # 延迟秒数
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class ChainedReminder:
    """链式提醒"""
    id: str
    name: str
    description: str
    conditions: List[ReminderCondition]
    actions: List[ReminderAction]
    priority: ReminderPriority = ReminderPriority.NORMAL
    status: ReminderStatus = ReminderStatus.PENDING
    created_at: datetime = None
    triggered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_interval: int = 300   # 重试间隔（秒）
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 处理枚举类型
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['conditions'] = [asdict(c) for c in self.conditions]
        data['actions'] = [
            {
                **asdict(a),
                'channel': a.channel.value
            } for a in self.actions
        ]
        # 处理日期时间
        for field in ['created_at', 'triggered_at', 'completed_at']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChainedReminder':
        """从字典创建"""
        # 处理枚举类型
        data['priority'] = ReminderPriority(data['priority'])
        data['status'] = ReminderStatus(data['status'])
        
        # 处理条件
        conditions = []
        for c_data in data['conditions']:
            conditions.append(ReminderCondition(**c_data))
        data['conditions'] = conditions
        
        # 处理动作
        actions = []
        for a_data in data['actions']:
            a_data['channel'] = ReminderChannel(a_data['channel'])
            actions.append(ReminderAction(**a_data))
        data['actions'] = actions
        
        # 处理日期时间
        for field in ['created_at', 'triggered_at', 'completed_at']:
            if data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


class ReminderExecutor(QThread):
    """提醒执行器"""
    
    reminder_triggered = pyqtSignal(str)  # 提醒ID
    reminder_completed = pyqtSignal(str)  # 提醒ID
    reminder_failed = pyqtSignal(str, str)  # 提醒ID, 错误信息
    
    def __init__(self, reminder: ChainedReminder, app_manager):
        super().__init__()
        self.reminder = reminder
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.ReminderExecutor')
    
    def run(self):
        """执行提醒"""
        try:
            self.logger.info(f"开始执行提醒: {self.reminder.name}")
            
            # 执行所有动作
            for action in self.reminder.actions:
                if action.delay > 0:
                    self.msleep(action.delay * 1000)
                
                self.execute_action(action)
            
            self.reminder.status = ReminderStatus.COMPLETED
            self.reminder.completed_at = datetime.now()
            self.reminder_completed.emit(self.reminder.id)
            
        except Exception as e:
            self.logger.error(f"执行提醒失败: {e}")
            self.reminder.status = ReminderStatus.FAILED
            self.reminder_failed.emit(self.reminder.id, str(e))
    
    def execute_action(self, action: ReminderAction):
        """执行单个动作"""
        try:
            if action.channel == ReminderChannel.DESKTOP:
                self.execute_desktop_notification(action)
            elif action.channel == ReminderChannel.FLOATING:
                self.execute_floating_reminder(action)
            elif action.channel == ReminderChannel.SOUND:
                self.execute_sound_reminder(action)
            elif action.channel == ReminderChannel.EMAIL:
                self.execute_email_reminder(action)
            elif action.channel == ReminderChannel.SYSTEM_TRAY:
                self.execute_system_tray_reminder(action)
            elif action.channel == ReminderChannel.POPUP:
                self.execute_popup_reminder(action)
                
        except Exception as e:
            self.logger.error(f"执行动作失败 {action.channel}: {e}")
            raise
    
    def execute_desktop_notification(self, action: ReminderAction):
        """执行桌面通知"""
        if self.app_manager and self.app_manager.notification_manager:
            self.app_manager.notification_manager.show_notification(
                action.title or "TimeNest 提醒",
                action.message,
                duration=action.data.get('duration', 5000)
            )
    
    def execute_floating_reminder(self, action: ReminderAction):
        """执行浮窗提醒"""
        if self.app_manager and self.app_manager.floating_manager:
            # 在浮窗中显示提醒消息
            floating_widget = self.app_manager.floating_manager.floating_widget
            if floating_widget:
                floating_widget.show_reminder_message(action.message)
    
    def execute_sound_reminder(self, action: ReminderAction):
        """执行声音提醒"""
        try:
            from PyQt6.QtMultimedia import QSoundEffect
            from PyQt6.QtCore import QUrl
            
            sound_file = action.data.get('sound_file', 'default.wav')
            sound = QSoundEffect()
            sound.setSource(QUrl.fromLocalFile(sound_file))
            sound.play()
            
        except Exception as e:
            self.logger.warning(f"播放提醒声音失败: {e}")
    
    def execute_email_reminder(self, action: ReminderAction):
        """执行邮件提醒"""
        # 这里可以集成邮件发送功能
        self.logger.info(f"邮件提醒: {action.message}")
    
    def execute_system_tray_reminder(self, action: ReminderAction):
        """执行系统托盘提醒"""
        if self.app_manager and hasattr(self.app_manager, 'system_tray'):
            tray = self.app_manager.system_tray
            if tray and isinstance(tray, QSystemTrayIcon):
                tray.showMessage(
                    action.title or "TimeNest 提醒",
                    action.message,
                    QSystemTrayIcon.MessageIcon.Information,
                    action.data.get('duration', 5000)
                )
    
    def execute_popup_reminder(self, action: ReminderAction):
        """执行弹窗提醒"""
        QMessageBox.information(
            None,
            action.title or "TimeNest 提醒",
            action.message
        )


class RemindAPIv2(QObject):
    """Remind API v2 主类"""
    
    reminder_added = pyqtSignal(str)      # 提醒ID
    reminder_triggered = pyqtSignal(str)   # 提醒ID
    reminder_completed = pyqtSignal(str)   # 提醒ID
    reminder_failed = pyqtSignal(str, str) # 提醒ID, 错误信息
    
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.RemindAPIv2')
        
        # 存储提醒
        self.reminders: Dict[str, ChainedReminder] = {}
        self.active_executors: Dict[str, ReminderExecutor] = {}
        
        # 检查定时器
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_reminders)
        self.check_timer.start(10000)  # 每10秒检查一次
        
        self.logger.info("Remind API v2 初始化完成")
    
    def add_reminder(self, reminder: ChainedReminder) -> bool:
        """添加提醒"""
        try:
            self.reminders[reminder.id] = reminder
            self.reminder_added.emit(reminder.id)
            self.logger.info(f"添加提醒: {reminder.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加提醒失败: {e}")
            return False
    
    def remove_reminder(self, reminder_id: str) -> bool:
        """移除提醒"""
        try:
            if reminder_id in self.reminders:
                # 停止执行器
                if reminder_id in self.active_executors:
                    self.active_executors[reminder_id].terminate()
                    del self.active_executors[reminder_id]
                
                del self.reminders[reminder_id]
                self.logger.info(f"移除提醒: {reminder_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"移除提醒失败: {e}")
            return False
    
    def check_reminders(self):
        """检查提醒条件"""
        try:
            current_context = self.get_current_context()
            
            for reminder in self.reminders.values():
                if reminder.status != ReminderStatus.PENDING:
                    continue
                
                # 检查所有条件
                all_conditions_met = True
                for condition in reminder.conditions:
                    if not condition.evaluate(current_context):
                        all_conditions_met = False
                        break
                
                if all_conditions_met:
                    self.trigger_reminder(reminder)
                    
        except Exception as e:
            self.logger.error(f"检查提醒失败: {e}")
    
    def trigger_reminder(self, reminder: ChainedReminder):
        """触发提醒"""
        try:
            reminder.status = ReminderStatus.ACTIVE
            reminder.triggered_at = datetime.now()
            
            # 创建执行器
            executor = ReminderExecutor(reminder, self.app_manager)
            executor.reminder_completed.connect(self.on_reminder_completed)
            executor.reminder_failed.connect(self.on_reminder_failed)
            
            self.active_executors[reminder.id] = executor
            executor.start()
            
            self.reminder_triggered.emit(reminder.id)
            self.logger.info(f"触发提醒: {reminder.name}")
            
        except Exception as e:
            self.logger.error(f"触发提醒失败: {e}")
            reminder.status = ReminderStatus.FAILED
    
    def get_current_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return {
            'current_time': datetime.now(),
            'day_of_week': datetime.now().weekday(),
            'hour': datetime.now().hour,
            'minute': datetime.now().minute,
            # 可以添加更多上下文信息
        }
    
    def on_reminder_completed(self, reminder_id: str):
        """提醒完成处理"""
        if reminder_id in self.active_executors:
            del self.active_executors[reminder_id]
        self.reminder_completed.emit(reminder_id)
    
    def on_reminder_failed(self, reminder_id: str, error: str):
        """提醒失败处理"""
        if reminder_id in self.active_executors:
            del self.active_executors[reminder_id]
        
        # 重试逻辑
        if reminder_id in self.reminders:
            reminder = self.reminders[reminder_id]
            if reminder.retry_count < reminder.max_retries:
                reminder.retry_count += 1
                reminder.status = ReminderStatus.PENDING
                self.logger.info(f"提醒重试 {reminder.retry_count}/{reminder.max_retries}: {reminder_id}")
            else:
                self.logger.error(f"提醒最终失败: {reminder_id}")
        
        self.reminder_failed.emit(reminder_id, error)
    
    def get_reminders(self, status: Optional[ReminderStatus] = None) -> List[ChainedReminder]:
        """获取提醒列表"""
        if status is None:
            return list(self.reminders.values())
        return [r for r in self.reminders.values() if r.status == status]
    
    def save_reminders(self, file_path: str) -> bool:
        """保存提醒到文件"""
        try:
            data = {
                'reminders': [r.to_dict() for r in self.reminders.values()],
                'saved_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存提醒失败: {e}")
            return False
    
    def load_reminders(self, file_path: str) -> bool:
        """从文件加载提醒"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for reminder_data in data.get('reminders', []):
                reminder = ChainedReminder.from_dict(reminder_data)
                self.reminders[reminder.id] = reminder
            
            return True
            
        except Exception as e:
            self.logger.error(f"加载提醒失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.check_timer.stop()
            
            # 停止所有执行器
            for executor in self.active_executors.values():
                executor.terminate()
                executor.wait()
            
            self.active_executors.clear()
            self.logger.info("Remind API v2 清理完成")
            
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
