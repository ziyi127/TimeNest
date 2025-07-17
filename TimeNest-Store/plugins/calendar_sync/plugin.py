#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日历同步插件
与主流日历服务同步
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                            QFrame, QHBoxLayout)

# 导入插件基类
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from core.plugin_base import IPlugin, PluginStatus


class EventWidget(QFrame):
    """事件显示组件"""
    
    def __init__(self, event_data: Dict[str, Any]):
        super().__init__()
        self.event_data = event_data
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                margin: 2px;
                padding: 4px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 4, 6, 4)
        
        # 事件标题
        title_label = QLabel(self.event_data.get('title', '无标题'))
        title_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #333;")
        layout.addWidget(title_label)
        
        # 时间信息
        time_layout = QHBoxLayout()
        
        start_time = self.event_data.get('start_time', '')
        end_time = self.event_data.get('end_time', '')
        
        if self.event_data.get('all_day', False):
            time_text = "全天"
        else:
            time_text = f"{start_time} - {end_time}"
        
        time_label = QLabel(time_text)
        time_label.setStyleSheet("font-size: 9px; color: #666;")
        time_layout.addWidget(time_label)
        
        # 状态指示器
        status = self.event_data.get('status', 'upcoming')
        if status == 'ongoing':
            status_label = QLabel("进行中")
            status_label.setStyleSheet("font-size: 8px; color: #e74c3c; font-weight: bold;")
        elif status == 'soon':
            status_label = QLabel("即将开始")
            status_label.setStyleSheet("font-size: 8px; color: #f39c12; font-weight: bold;")
        else:
            status_label = QLabel("")
        
        time_layout.addWidget(status_label)
        time_layout.addStretch()
        
        layout.addLayout(time_layout)


class CalendarWidget(QWidget):
    """日历显示组件"""
    
    def __init__(self, plugin_instance):
        super().__init__()
        self.plugin = plugin_instance
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 标题
        self.title_label = QLabel("📅 今日日程")
        self.title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333;")
        layout.addWidget(self.title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(150)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 事件容器
        self.events_widget = QWidget()
        self.events_layout = QVBoxLayout(self.events_widget)
        self.events_layout.setSpacing(2)
        self.events_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.events_widget)
        layout.addWidget(scroll_area)
        
        # 状态标签
        self.status_label = QLabel("正在同步...")
        self.status_label.setStyleSheet("font-size: 8px; color: #999;")
        layout.addWidget(self.status_label)
    
    def update_events(self, events: List[Dict[str, Any]], sync_status: str):
        """更新事件显示"""
        # 清空现有事件
        for i in reversed(range(self.events_layout.count())):
            child = self.events_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        if not events:
            no_events_label = QLabel("今日无日程安排")
            no_events_label.setStyleSheet("font-size: 10px; color: #666; text-align: center;")
            no_events_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_layout.addWidget(no_events_label)
        else:
            # 添加事件
            for event in events:
                event_widget = EventWidget(event)
                self.events_layout.addWidget(event_widget)
        
        # 添加弹性空间
        self.events_layout.addStretch()
        
        # 更新状态
        self.status_label.setText(sync_status)


class CalendarSyncPlugin(IPlugin):
    """日历同步插件"""
    
    # 定义信号
    events_updated = pyqtSignal(list, str)  # events, sync_status
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.CalendarSyncPlugin')
        
        # 插件状态
        self.status = PluginStatus.LOADED
        
        # 组件
        self.calendar_widget = None
        self.sync_timer = None
        self.plugin_manager = None
        
        # 数据
        self.events = []
        self.last_sync_time = None
        
        # 设置
        self.settings = {
            'sync_enabled': True,
            'sync_interval': 15,
            'google_calendar_enabled': False,
            'google_api_key': '',
            'outlook_enabled': False,
            'outlook_client_id': '',
            'show_upcoming_events': 3,
            'event_reminder': True,
            'reminder_minutes': 15,
            'show_all_day_events': True,
            'time_format': '24h'
        }
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.logger.info("日历同步插件初始化开始")
            
            # 创建日历组件
            self.calendar_widget = CalendarWidget(self)
            
            # 创建同步定时器
            self.sync_timer = QTimer()
            self.sync_timer.timeout.connect(self.sync_calendars)
            
            # 连接信号
            self.events_updated.connect(self.calendar_widget.update_events)
            
            self.status = PluginStatus.INITIALIZED
            self.logger.info("日历同步插件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            if self.status != PluginStatus.INITIALIZED:
                self.logger.error("插件未正确初始化")
                return False
            
            # 开始定时同步
            if self.settings['sync_enabled']:
                interval = self.settings['sync_interval'] * 60 * 1000  # 转换为毫秒
                self.sync_timer.start(interval)
                
                # 立即同步一次
                self.sync_calendars()
            
            self.status = PluginStatus.ENABLED
            self.logger.info("日历同步插件已激活")
            return True
            
        except Exception as e:
            self.logger.error(f"插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            # 停止同步定时器
            if self.sync_timer and self.sync_timer.isActive():
                self.sync_timer.stop()
            
            self.status = PluginStatus.DISABLED
            self.logger.info("日历同步插件已停用")
            return True
            
        except Exception as e:
            self.logger.error(f"插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理插件资源"""
        try:
            # 停用插件
            self.deactivate()
            
            # 清理组件
            if self.calendar_widget:
                self.calendar_widget.deleteLater()
                self.calendar_widget = None
            
            if self.sync_timer:
                self.sync_timer.deleteLater()
                self.sync_timer = None
            
            self.status = PluginStatus.UNLOADED
            self.logger.info("日历同步插件资源清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
            return False
    
    def sync_calendars(self):
        """同步日历"""
        try:
            self.logger.info("开始同步日历")
            
            # 模拟同步过程（实际应用中应该调用真实的API）
            events = self.generate_sample_events()
            
            # 过滤和排序事件
            filtered_events = self.filter_events(events)
            
            self.events = filtered_events
            self.last_sync_time = datetime.now()
            
            # 更新显示
            sync_status = f"最后同步: {self.last_sync_time.strftime('%H:%M')}"
            self.events_updated.emit(self.events, sync_status)
            
            # 检查提醒
            self.check_reminders()
            
            self.logger.info(f"日历同步完成，获取到 {len(self.events)} 个事件")
            
        except Exception as e:
            self.logger.error(f"同步日历失败: {e}")
            self.events_updated.emit([], f"同步失败: {str(e)}")
    
    def generate_sample_events(self) -> List[Dict[str, Any]]:
        """生成示例事件（模拟API调用）"""
        now = datetime.now()
        events = []
        
        # 示例事件
        sample_events = [
            {
                'title': '团队会议',
                'start': now + timedelta(hours=1),
                'end': now + timedelta(hours=2),
                'all_day': False
            },
            {
                'title': '项目评审',
                'start': now + timedelta(hours=3),
                'end': now + timedelta(hours=4),
                'all_day': False
            },
            {
                'title': '客户拜访',
                'start': now + timedelta(hours=5),
                'end': now + timedelta(hours=6),
                'all_day': False
            },
            {
                'title': '生日聚会',
                'start': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'end': now.replace(hour=23, minute=59, second=59, microsecond=0),
                'all_day': True
            }
        ]
        
        for event in sample_events:
            # 格式化时间
            time_format = '%H:%M' if self.settings['time_format'] == '24h' else '%I:%M %p'
            
            event_data = {
                'title': event['title'],
                'start_time': event['start'].strftime(time_format),
                'end_time': event['end'].strftime(time_format),
                'all_day': event['all_day'],
                'start_datetime': event['start'],
                'end_datetime': event['end']
            }
            
            # 判断事件状态
            if event['start'] <= now <= event['end']:
                event_data['status'] = 'ongoing'
            elif event['start'] <= now + timedelta(minutes=30):
                event_data['status'] = 'soon'
            else:
                event_data['status'] = 'upcoming'
            
            events.append(event_data)
        
        return events
    
    def filter_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤和排序事件"""
        filtered = []
        
        for event in events:
            # 过滤全天事件
            if not self.settings['show_all_day_events'] and event['all_day']:
                continue
            
            filtered.append(event)
        
        # 按开始时间排序
        filtered.sort(key=lambda x: x['start_datetime'])
        
        # 限制显示数量
        max_events = self.settings['show_upcoming_events']
        return filtered[:max_events]
    
    def check_reminders(self):
        """检查事件提醒"""
        if not self.settings['event_reminder']:
            return
        
        try:
            now = datetime.now()
            reminder_minutes = self.settings['reminder_minutes']
            
            for event in self.events:
                start_time = event['start_datetime']
                time_diff = (start_time - now).total_seconds() / 60
                
                # 如果事件在提醒时间范围内
                if 0 <= time_diff <= reminder_minutes:
                    self.send_reminder(event)
            
        except Exception as e:
            self.logger.error(f"检查提醒失败: {e}")
    
    def send_reminder(self, event: Dict[str, Any]):
        """发送事件提醒"""
        try:
            title = "日程提醒"
            message = f"'{event['title']}' 即将在 {event['start_time']} 开始"
            
            # 这里应该调用通知管理器发送通知
            self.logger.info(f"提醒: {title} - {message}")
            
        except Exception as e:
            self.logger.error(f"发送提醒失败: {e}")
    
    def get_widget(self) -> Optional[QWidget]:
        """获取插件组件"""
        return self.calendar_widget
    
    def get_settings(self) -> Dict[str, Any]:
        """获取插件设置"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """更新插件设置"""
        try:
            old_sync_enabled = self.settings['sync_enabled']
            old_sync_interval = self.settings['sync_interval']
            
            self.settings.update(new_settings)
            
            # 更新同步定时器
            if self.settings['sync_enabled'] != old_sync_enabled or \
               self.settings['sync_interval'] != old_sync_interval:
                
                if self.sync_timer:
                    self.sync_timer.stop()
                
                if self.settings['sync_enabled']:
                    interval = self.settings['sync_interval'] * 60 * 1000
                    self.sync_timer.start(interval)
            
            # 重新同步
            if self.status == PluginStatus.ENABLED and self.settings['sync_enabled']:
                self.sync_calendars()
            
            self.logger.info("插件设置已更新")
            return True
            
        except Exception as e:
            self.logger.error(f"更新插件设置失败: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            'id': 'calendar_sync',
            'name': '日历同步插件',
            'version': '1.3.1',
            'description': '与主流日历服务同步',
            'author': 'Sync Solutions',
            'status': self.status.value,
            'settings': self.settings,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'events_count': len(self.events)
        }


# 插件入口点
def create_plugin():
    """创建插件实例"""
    return CalendarSyncPlugin()
