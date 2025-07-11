# -*- coding: utf-8 -*-
"""
TimeNest 倒计时组件
显示重要事件的倒计时
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtGui import QFont

from .base_component import BaseComponent

class CountdownComponent(BaseComponent):
    """倒计时组件"""
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        # 倒计时事件列表
        self.countdown_events: List[Dict[str, Any]] = []
        
        # UI组件
        self.events_container: Optional[QWidget] = None
        
        # 连接词强调色设置
        self.connector_highlight_enabled = False
        self.connector_highlight_color = "#ff6b6b"
        
        super().__init__(component_id, config)
    
    def initialize_component(self):
        """初始化倒计时组件"""
        try:
            if not self.widget or not self.layout:
                return
            
            # 创建标题
            title_label = self.create_title_label(self.config.get('name', '倒计时'))
            self.layout.addWidget(title_label)
            
            # 创建事件容器
            self.events_container = QWidget()
            events_layout = QVBoxLayout(self.events_container)
            events_layout.setContentsMargins(0, 0, 0, 0)
            events_layout.setSpacing(5)
            
            self.layout.addWidget(self.events_container)
            
            # 加载倒计时事件
            self._load_countdown_events()
            
            # 初始化内容
            self.update_content()
            
        except Exception as e:
            self.logger.error(f"初始化倒计时组件失败: {e}")
            self.show_error(str(e))
    
    def _load_countdown_events(self):
        """加载倒计时事件"""
        try:
            settings = self.config.get('settings', {})
            self.countdown_events = settings.get('events', [])
            
            # 如果没有配置事件，创建默认事件
            if not self.countdown_events:
                self._create_default_events()
            
            # 按时间排序
            self.countdown_events.sort(key=lambda x: datetime.fromisoformat(x['target_time']))
            
        except Exception as e:
            self.logger.error(f"加载倒计时事件失败: {e}")
            self.countdown_events = []
    
    def _create_default_events(self):
        """创建默认倒计时事件"""
        try:
            now = datetime.now()
            
            # 创建一些示例事件
            default_events = [
                {
                    'id': 'weekend',
                    'name': '周末',
                    'target_time': self._get_next_weekend().isoformat(),
                    'color': '#4caf50',
                    'enabled': True
                },
                {
                    'id': 'month_end',
                    'name': '月末',
                    'target_time': self._get_month_end().isoformat(),
                    'color': '#2196f3',
                    'enabled': True
                },
                {
                    'id': 'year_end',
                    'name': '年末',
                    'target_time': f"{now.year}-12-31T23:59:59",
                    'color': '#ff9800',
                    'enabled': True
                }
            ]
            
            self.countdown_events = default_events
            
            # 保存到配置
            settings = self.config.setdefault('settings', {})
            settings['events'] = self.countdown_events
            
        except Exception as e:
            self.logger.error(f"创建默认倒计时事件失败: {e}")
    
    def _get_next_weekend(self) -> datetime:
        """获取下个周末的时间"""
        now = datetime.now()
        days_until_saturday = (5 - now.weekday()) % 7  # 5 = Saturday
        if days_until_saturday == 0 and now.hour >= 18:  # 如果是周六且已过18点
            days_until_saturday = 7
        
        next_weekend = now + timedelta(days=days_until_saturday)
        return next_weekend.replace(hour=18, minute=0, second=0, microsecond=0)
    
    def _get_month_end(self) -> datetime:
        """获取月末时间"""
        now = datetime.now()
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        
        month_end = next_month - timedelta(days=1)
        return month_end.replace(hour=23, minute=59, second=59, microsecond=0)
    
    def update_content(self):
        """更新倒计时内容"""
        try:
            if not self.events_container:
                return
            
            # 清除现有内容
            layout = self.events_container.layout()
            if layout:
                for i in reversed(range(layout.count())):
                    child = layout.itemAt(i).widget()
                    if child:
                        child.deleteLater()
            
            # 获取当前时间
            now = datetime.now()
            
            # 过滤并显示有效的倒计时事件
            active_events = []
            for event in self.countdown_events:
                if not event.get('enabled', True):
                    continue
                
                try:
                    target_time = datetime.fromisoformat(event['target_time'])
                    if target_time > now:
                        active_events.append((event, target_time))
                except ValueError:
                    self.logger.warning(f"无效的时间格式: {event.get('target_time')}")
                    continue
            
            if not active_events:
                # 没有活动的倒计时事件
                no_events_label = QLabel("暂无倒计时事件")
                no_events_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_events_label.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(no_events_label)
                return
            
            # 显示倒计时事件
            settings = self.config.get('settings', {})
            max_events = settings.get('max_display_events', 3)
            
            for i, (event, target_time) in enumerate(active_events[:max_events]):
                event_widget = self._create_event_widget(event, target_time, now)
                layout.addWidget(event_widget)
            
        except Exception as e:
            self.logger.error(f"更新倒计时内容失败: {e}")
    
    def _create_event_widget(self, event: Dict[str, Any], target_time: datetime, now: datetime) -> QWidget:
        """创建倒计时事件widget"""
        try:
            widget = QWidget()
            widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {event.get('color', '#f5f5f5')};
                    border-radius: 8px;
                    padding: 8px;
                    margin: 2px;
                }}
            """)
            
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(4)
            
            # 事件名称
            name_label = QLabel(event.get('name', '未命名事件'))
            name_font = QFont("Arial", 10, QFont.Weight.Bold)
            name_label.setFont(name_font)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("color: white;")
            layout.addWidget(name_label)
            
            # 目标时间
            target_label = QLabel(target_time.strftime('%Y-%m-%d %H:%M'))
            target_font = QFont("Arial", 8)
            target_label.setFont(target_font)
            target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            target_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
            layout.addWidget(target_label)
            
            # 倒计时
            countdown_text = self._calculate_countdown(target_time, now)
            countdown_label = QLabel(countdown_text)
            countdown_font = QFont("Arial", 12, QFont.Weight.Bold)
            countdown_label.setFont(countdown_font)
            countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            countdown_label.setStyleSheet("color: white;")
            
            # 如果启用了连接词强调色，则支持富文本
            if self.connector_highlight_enabled:
                countdown_label.setTextFormat(Qt.TextFormat.RichText)
            
            layout.addWidget(countdown_label)
            
            return widget
            
        except Exception as e:
            self.logger.error(f"创建倒计时事件widget失败: {e}")
            return QWidget()
    
    def _calculate_countdown(self, target_time: datetime, now: datetime) -> str:
        """计算倒计时文本"""
        try:
            delta = target_time - now
            
            if delta.total_seconds() <= 0:
                return "已到期"
            
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # 获取连接词强调色设置
            settings = self.config.get('settings', {})
            self.connector_highlight_enabled = settings.get('connector_highlight_enabled', False)
            self.connector_highlight_color = settings.get('connector_highlight_color', '#ff6b6b')
            
            # 根据剩余时间选择显示格式
            if days > 0:
                if days >= 30:
                    months = days // 30
                    remaining_days = days % 30
                    if remaining_days > 0:
                        if self.connector_highlight_enabled:
                            return f"{months}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>个月</span>{remaining_days}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>天</span>"
                        else:
                            return f"{months}个月{remaining_days}天"
                    else:
                        if self.connector_highlight_enabled:
                            return f"{months}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>个月</span>"
                        else:
                            return f"{months}个月"
                else:
                    if self.connector_highlight_enabled:
                        return f"{days}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>天</span>{hours}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>小时</span>"
                    else:
                        return f"{days}天{hours}小时"
            elif hours > 0:
                if self.connector_highlight_enabled:
                    return f"{hours}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>小时</span>{minutes}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>分钟</span>"
                else:
                    return f"{hours}小时{minutes}分钟"
            elif minutes > 0:
                if self.connector_highlight_enabled:
                    return f"{minutes}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>分钟</span>{seconds}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>秒</span>"
                else:
                    return f"{minutes}分钟{seconds}秒"
            else:
                if self.connector_highlight_enabled:
                    return f"{seconds}<span style='color: {self.connector_highlight_color}; font-weight: bold;'>秒</span>"
                else:
                    return f"{seconds}秒"
                
        except Exception as e:
            self.logger.error(f"计算倒计时失败: {e}")
            return "计算错误"
    
    def add_countdown_event(self, name: str, target_time: datetime, color: str = '#4caf50') -> str:
        """添加倒计时事件"""
        try:
            import uuid
            event_id = str(uuid.uuid4())
            
            event = {
                'id': event_id,
                'name': name,
                'target_time': target_time.isoformat(),
                'color': color,
                'enabled': True
            }
            
            self.countdown_events.append(event)
            self.countdown_events.sort(key=lambda x: datetime.fromisoformat(x['target_time']))
            
            # 保存到配置
            settings = self.config.setdefault('settings', {})
            settings['events'] = self.countdown_events
            
            # 更新显示
            self.update_content()
            
            self.logger.info(f"添加倒计时事件: {name}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"添加倒计时事件失败: {e}")
            return ""
    
    def remove_countdown_event(self, event_id: str) -> bool:
        """移除倒计时事件"""
        try:
            original_count = len(self.countdown_events)
            self.countdown_events = [e for e in self.countdown_events if e.get('id') != event_id]
            
            if len(self.countdown_events) < original_count:
                # 保存到配置
                settings = self.config.setdefault('settings', {})
                settings['events'] = self.countdown_events
                
                # 更新显示
                self.update_content()
                
                self.logger.info(f"移除倒计时事件: {event_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"移除倒计时事件失败: {e}")
            return False
    
    def get_countdown_events(self) -> List[Dict[str, Any]]:
        """获取倒计时事件列表"""
        return self.countdown_events.copy()
    
    def get_update_interval(self) -> int:
        """获取更新间隔（1秒）"""
        return 1000
    
    def on_config_updated(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置更新回调"""
        try:
            # 重新加载倒计时事件
            self._load_countdown_events()
            
            # 更新显示
            self.update_content()
            
        except Exception as e:
            self.logger.error(f"处理倒计时配置更新失败: {e}")
    
    def cleanup_component(self):
        """清理组件资源"""
        try:
            self.countdown_events.clear()
            
        except Exception as e:
            self.logger.error(f"清理倒计时组件失败: {e}")