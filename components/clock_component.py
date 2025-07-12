# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 时钟组件
显示当前时间和日期信息
"""

import logging
from datetime import datetime
from typing import Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtGui import QFont

from .base_component import BaseComponent

class ClockComponent(BaseComponent):
    """时钟组件"""
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        # UI组件
        self.time_label: Optional[QLabel] = None
        self.date_label: Optional[QLabel] = None
        self.seconds_label: Optional[QLabel] = None
        
        super().__init__(component_id, config)
    
    def initialize_component(self):
        """初始化时钟组件"""
        try:
            if not self.widget or not self.layout:
                return:
                return
            
            # 获取设置
            settings = self.config.get('settings', {})
            
            # 创建标题
            title_label = self.create_title_label(self.config.get('name', '时钟'))
            self.layout.addWidget(title_label)
            
            # 创建时间显示
            self._create_time_display(settings)
            
            # 创建日期显示
            if settings.get('show_date', True):
                self._create_date_display()
            
            # 初始化内容
            self.update_content()
            
        except Exception as e:
            self.logger.error(f"初始化时钟组件失败: {e}")
            self.show_error(str(e))
    
    def _create_time_display(self, settings: Dict[str, Any]):
        """创建时间显示"""
        try:
            # 主时间标签
            self.time_label = QLabel()
            time_font = QFont("Arial", 16, QFont.Weight.Bold)
            self.time_label.setFont(time_font)
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #2196f3;
                    background-color: #f8f9fa;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            self.layout.addWidget(self.time_label)
            
            # 秒数显示（如果启用）
            if settings.get('show_seconds', True):
                self.seconds_label = QLabel()
                seconds_font = QFont("Arial", 12)
                self.seconds_label.setFont(seconds_font)
                self.seconds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.seconds_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        margin: 2px;
                    }
                """)
                self.layout.addWidget(self.seconds_label)
            
        except Exception as e:
            self.logger.error(f"创建时间显示失败: {e}")
    
    def _create_date_display(self):
        """创建日期显示"""
        try:
            self.date_label = QLabel()
            date_font = QFont("Arial", 10)
            self.date_label.setFont(date_font)
            self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.date_label.setStyleSheet("""
                QLabel {
                    color: #495057;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 5px;
                    margin: 2px;
                }
            """)
            self.layout.addWidget(self.date_label)
            
        except Exception as e:
            self.logger.error(f"创建日期显示失败: {e}")
    
    def update_content(self):
        """更新时钟内容"""
        try:
            # 获取当前时间
            now = self._get_current_time()
            settings = self.config.get('settings', {})
            
            # 更新时间显示
            if self.time_label:
                if settings.get('format_24h', True):
                    time_format = "%H:%M"
                else:
                    time_format = "%I:%M %p"
                
                time_text = now.strftime(time_format)
                self.time_label.setText(time_text)
            
            # 更新秒数显示
            if self.seconds_label and settings.get('show_seconds', True):
                seconds_text = now.strftime("%S")
                self.seconds_label.setText(f":{seconds_text}")
            
            # 更新日期显示
            if self.date_label and settings.get('show_date', True):
                # 获取星期几的中文名称:
                # 获取星期几的中文名称
                weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                weekday_name = weekdays[now.weekday()]
                
                date_text = f"{now.strftime('%Y年%m月%d日')} {weekday_name}"
                self.date_label.setText(date_text)
            
        except Exception as e:
            self.logger.error(f"更新时钟内容失败: {e}")
    
    def _get_current_time(self) -> datetime:
        """获取当前时间（考虑调试模式）"""
        try:
            settings = self.config.get('settings', {})
            
            # 如果启用了显示真实时间，则忽略时间管理器的偏移
            if settings.get('show_real_time', False):
                return datetime.now()
            
            # 否则使用时间管理器的时间（如果可用）
            # 这里可以集成时间管理器的功能
            return datetime.now()
            
        except Exception as e:
            self.logger.error(f"获取当前时间失败: {e}")
            return datetime.now()
    
    def get_update_interval(self) -> int:
        """获取更新间隔"""
        settings = self.config.get('settings', {})
        if settings.get('show_seconds', True):
            return 1000  # 1秒更新一次
        else:
            return 60000  # 1分钟更新一次
    
    def on_config_updated(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置更新回调"""
        try:
            # 检查是否需要重新初始化UI
            old_settings = old_config.get('settings', {})
            new_settings = new_config.get('settings', {})
            
            ui_changed = (
                old_settings.get('show_date') != new_settings.get('show_date') or
                old_settings.get('show_seconds') != new_settings.get('show_seconds')
            )
            
            
            if ui_changed:
                # 重新初始化组件:
            
                # 重新初始化组件
                self.initialize_component()
            else:
                # 只更新内容
                self.update_content()
            
            # 更新定时器间隔
            new_interval = self.get_update_interval()
            if self.update_timer.interval() != new_interval:
                self.update_timer.stop()
                self.update_timer.start(new_interval)
            
        except Exception as e:
            self.logger.error(f"处理时钟配置更新失败: {e}")
    
    def cleanup_component(self):
        """清理组件资源"""
        try:
            # 时钟组件没有特殊资源需要清理
            pass
            
        except Exception as e:
            self.logger.error(f"清理时钟组件失败: {e}")