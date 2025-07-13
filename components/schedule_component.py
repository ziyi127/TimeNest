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
TimeNest 课程表组件
显示当前课程表信息和状态
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QPushButton
)
from PyQt6.QtGui import QFont, QPalette, QColor

from .base_component import BaseComponent
from models.schedule import Schedule, ClassItem, Subject

class ScheduleComponent(BaseComponent):
    """课程表组件"""
    
    # 信号定义
    class_clicked = pyqtSignal(str)  # 课程ID
    schedule_edit_requested = pyqtSignal()  # 请求编辑课程表
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        self.schedule: Optional[Schedule] = None
        self.current_class: Optional[ClassItem] = None
        self.next_class: Optional[ClassItem] = None
        
        # UI组件
        self.title_label: Optional[QLabel] = None
        self.current_class_frame: Optional[QFrame] = None
        self.next_class_frame: Optional[QFrame] = None
        self.schedule_scroll: Optional[QScrollArea] = None
        self.schedule_container: Optional[QWidget] = None
        self.edit_button: Optional[QPushButton] = None
        
        super().__init__(component_id, config)
    
    def initialize_component(self):
        """初始化课程表组件"""
        try:
            if not self.widget or not self.layout:
                return
            
            # 创建标题
            self.title_label = self.create_title_label(self.config.get('name', '课程表'))
            self.layout.addWidget(self.title_label)
            
            # 创建当前课程显示区域
            self._create_current_class_area()
            
            # 创建下节课显示区域
            self._create_next_class_area()
            
            # 创建课程表滚动区域
            self._create_schedule_area()
            
            # 创建编辑按钮
            self._create_edit_button()
            
            # 初始化内容
            self.update_content()
            
        except Exception as e:
            self.logger.error(f"初始化课程表组件失败: {e}")
            self.show_error(str(e))
    
    def _create_current_class_area(self):
        """创建当前课程显示区域"""
        try:
            settings = self.config.get('settings', {})
            if not settings.get('show_current_class', True):
                return
            
            self.current_class_frame = QFrame()
            self.current_class_frame.setFrameStyle(QFrame.Shape.StyledPanel)
            self.current_class_frame.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            
            layout = QVBoxLayout(self.current_class_frame)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(4)
            
            # 当前课程标题
            title = QLabel("当前课程")
            title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            self.layout.addWidget(self.current_class_frame)
            
        except Exception as e:
            self.logger.error(f"创建当前课程区域失败: {e}")
    
    def _create_next_class_area(self):
        """创建下节课显示区域"""
        try:
            settings = self.config.get('settings', {})
            if not settings.get('show_next_class', True):
                return
            
            self.next_class_frame = QFrame()
            self.next_class_frame.setFrameStyle(QFrame.Shape.StyledPanel)
            self.next_class_frame.setStyleSheet("""
                QFrame {
                    background-color: #f3e5f5;
                    border: 2px solid #9c27b0;
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            
            layout = QVBoxLayout(self.next_class_frame)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(4)
            
            # 下节课标题
            title = QLabel("下节课")
            title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            self.layout.addWidget(self.next_class_frame)
            
        except Exception as e:
            self.logger.error(f"创建下节课区域失败: {e}")
    
    def _create_schedule_area(self):
        """创建课程表显示区域"""
        try:
            # 创建滚动区域
            self.schedule_scroll = QScrollArea()
            self.schedule_scroll.setWidgetResizable(True)
            self.schedule_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.schedule_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.schedule_scroll.setMaximumHeight(200)
            
            # 创建容器widget
            self.schedule_container = QWidget()
            self.schedule_scroll.setWidget(self.schedule_container)
            
            self.layout.addWidget(self.schedule_scroll)
            
        except Exception as e:
            self.logger.error(f"创建课程表区域失败: {e}")
    
    def _create_edit_button(self):
        """创建编辑按钮"""
        try:
            self.edit_button = QPushButton("编辑课程表")
            self.edit_button.setMaximumHeight(30)
            self.edit_button.clicked.connect(self._on_edit_clicked)
            self.edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            
            self.layout.addWidget(self.edit_button)
            
        except Exception as e:
            self.logger.error(f"创建编辑按钮失败: {e}")
    
    def _on_edit_clicked(self):
        """编辑按钮点击事件"""
        self.schedule_edit_requested.emit()
    
    def update_content(self):
        """更新组件内容"""
        try:
            # 获取当前时间
            now = datetime.now()
            
            # 更新当前课程和下节课信息
            self._update_current_and_next_class(now)
            
            # 更新课程表显示
            self._update_schedule_display(now)
            
        except Exception as e:
            self.logger.error(f"更新课程表内容失败: {e}")
    
    def _update_current_and_next_class(self, now: datetime):
        """更新当前课程和下节课信息"""
        try:
            if not self.schedule:
                self._clear_current_class_display()
                self._clear_next_class_display()
                return
            
            # 获取今天的课程
            weekday = now.weekday()  # 0=Monday, 6=Sunday
            today_classes = self.schedule.get_classes_by_day(weekday)
            
            
            if not today_classes:
                self._clear_current_class_display()
            
                self._clear_current_class_display()
                self._clear_next_class_display()
                return
            
            # 按时间排序
            today_classes.sort(key=lambda x: x.start_time)
            
            # 查找当前课程和下节课
            current_time = now.time()
            current_class = None
            next_class = None
            
            for class_item in today_classes:
                if class_item.start_time <= current_time <= class_item.end_time:
                    current_class = class_item
                elif class_item.start_time > current_time:
                    if next_class is None:
                        next_class = class_item
                    break
            
            # 更新显示
            self._update_current_class_display(current_class, now)
            self._update_next_class_display(next_class, now)
            
        except Exception as e:
            self.logger.error(f"更新当前课程信息失败: {e}")
    
    def _update_current_class_display(self, class_item: Optional[ClassItem], now: datetime):
        """更新当前课程显示"""
        try:
            if not self.current_class_frame:
                return
            
            layout = self.current_class_frame.layout()
            if not layout:
                return
                return
            
            # 清除现有内容（保留标题）
            for i in reversed(range(1, layout.count())):
                child = layout.itemAt(i).widget()
                if child and hasattr(child, "deleteLater"):
                    child.deleteLater()
                    child.deleteLater()
            
            
            if not class_item:
                # 没有当前课程:
            
                # 没有当前课程
                no_class_label = QLabel("暂无课程")
                no_class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_class_label.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(no_class_label)
                return
            
            # 获取科目信息
            subject = self.schedule.get_subject(class_item.subject_id) if self.schedule else None
            subject_name = subject.name if subject else "未知科目"
            
            # 科目名称
            subject_label = QLabel(subject_name)
            subject_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            subject_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subject_label)
            
            # 时间信息
            time_text = f"{class_item.start_time.strftime('%H:%M')} - {class_item.end_time.strftime('%H:%M')}"
            time_label = QLabel(time_text)
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(time_label)
            
            # 教室信息
            if class_item.classroom:
                classroom_label = QLabel(f"教室: {class_item.classroom}")
                classroom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(classroom_label)
            
            # 剩余时间
            end_datetime = datetime.combine(now.date(), class_item.end_time)
            remaining = end_datetime - now
            if remaining.total_seconds() > 0:
                remaining_text = self._format_duration(remaining)
                remaining_label = QLabel(f"剩余: {remaining_text}")
                remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                remaining_label.setStyleSheet("color: #f44336; font-weight: bold;")
                layout.addWidget(remaining_label)
            
        except Exception as e:
            self.logger.error(f"更新当前课程显示失败: {e}")
    
    def _update_next_class_display(self, class_item: Optional[ClassItem], now: datetime):
        """更新下节课显示"""
        try:
            if not self.next_class_frame:
                return
                return
            
            layout = self.next_class_frame.layout()
            if not layout:
                return
                return
            
            # 清除现有内容（保留标题）
            for i in reversed(range(1, layout.count())):
                child = layout.itemAt(i).widget()
                if child and hasattr(child, "deleteLater"):
                    child.deleteLater()
                    child.deleteLater()
            
            
            if not class_item:
                # 没有下节课:
            
                # 没有下节课
                no_class_label = QLabel("今日课程已结束")
                no_class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_class_label.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(no_class_label)
                return
            
            # 获取科目信息
            subject = self.schedule.get_subject(class_item.subject_id) if self.schedule else None
            subject_name = subject.name if subject else "未知科目"
            
            # 科目名称
            subject_label = QLabel(subject_name)
            subject_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            subject_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subject_label)
            
            # 时间信息
            time_text = f"{class_item.start_time.strftime('%H:%M')} - {class_item.end_time.strftime('%H:%M')}"
            time_label = QLabel(time_text)
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(time_label)
            
            # 教室信息
            if class_item.classroom:
                classroom_label = QLabel(f"教室: {class_item.classroom}")
                classroom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(classroom_label)
            
            # 距离开始时间
            start_datetime = datetime.combine(now.date(), class_item.start_time)
            time_until = start_datetime - now
            if time_until.total_seconds() > 0:
                until_text = self._format_duration(time_until)
                until_label = QLabel(f"距离开始: {until_text}")
                until_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                until_label.setStyleSheet("color: #ff9800; font-weight: bold;")
                layout.addWidget(until_label)
            
        except Exception as e:
            self.logger.error(f"更新下节课显示失败: {e}")
    
    def _clear_current_class_display(self):
        """清空当前课程显示"""
        self._update_current_class_display(None, datetime.now())
    
    def _clear_next_class_display(self):
        """清空下节课显示"""
        self._update_next_class_display(None, datetime.now())
    
    def _update_schedule_display(self, now: datetime):
        """更新课程表显示"""
        try:
            if not self.schedule_container:
                return
                return
            
            # 清除现有内容
            if self.schedule_container.layout():
                for i in reversed(range(self.schedule_container.layout().count())):
                    child = self.schedule_container.layout().itemAt(i).widget()
                    if child and hasattr(child, "deleteLater"):
                        child.deleteLater()
                        child.deleteLater()
            
            # 创建新布局
            layout = QVBoxLayout(self.schedule_container)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(3)
            
            
            if not self.schedule:
                no_schedule_label = QLabel("未加载课程表")
            
                no_schedule_label = QLabel("未加载课程表")
                no_schedule_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_schedule_label.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(no_schedule_label)
                return
            
            # 获取设置
            settings = self.config.get('settings', {})
            show_tomorrow = settings.get('show_tomorrow', False)
            hide_finished = settings.get('hide_finished_classes', False)
            
            # 显示今天的课程
            self._add_day_schedule(layout, now, 0, "今天", hide_finished)
            
            # 显示明天的课程（如果启用）
            if show_tomorrow:
                tomorrow = now + timedelta(days=1)
                self._add_day_schedule(layout, tomorrow, 1, "明天", False)
            
        except Exception as e:
            self.logger.error(f"更新课程表显示失败: {e}")
    
    def _add_day_schedule(self, layout: QVBoxLayout, date: datetime, day_offset: int, day_name: str, hide_finished: bool):
        """添加某一天的课程表"""
        try:
            weekday = date.weekday()
            day_classes = self.schedule.get_classes_by_day(weekday)
            
            
            if not day_classes:
                return
            
                return
            
            # 按时间排序
            day_classes.sort(key=lambda x: x.start_time)
            
            # 过滤已结束的课程（仅对今天有效）
            if day_offset == 0 and hide_finished:
                current_time = date.time()
                day_classes = [c for c in day_classes if c.end_time > current_time]
            
            
            if not day_classes:
                return
            
                return
            
            # 添加日期标题
            day_title = QLabel(day_name)
            day_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            day_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_title.setStyleSheet("color: #333; margin: 5px 0;")
            layout.addWidget(day_title)
            
            # 添加课程
            for class_item in day_classes:
                class_widget = self._create_class_widget(class_item, date)
                layout.addWidget(class_widget)
            
        except Exception as e:
            self.logger.error(f"添加日程显示失败: {e}")
    
    def _create_class_widget(self, class_item: ClassItem, date: datetime) -> QWidget:
        """创建课程widget"""
        try:
            widget = QFrame()
            widget.setFrameStyle(QFrame.Shape.StyledPanel)
            widget.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 3px;
                }
                QFrame:hover {
                    background-color: #e8f5e8;
                    border-color: #4caf50;
                }
            """)
            
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 3, 5, 3)
            layout.setSpacing(5)
            
            # 获取科目信息
            subject = self.schedule.get_subject(class_item.subject_id) if self.schedule else None
            subject_name = subject.name if subject else "未知科目"
            
            # 时间标签
            time_text = f"{class_item.start_time.strftime('%H:%M')}-{class_item.end_time.strftime('%H:%M')}"
            time_label = QLabel(time_text)
            time_label.setFont(QFont("Arial", 8))
            time_label.setStyleSheet("color: #666;")
            time_label.setMinimumWidth(80)
            layout.addWidget(time_label)
            
            # 科目标签
            subject_label = QLabel(subject_name)
            subject_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            layout.addWidget(subject_label)
            
            # 教室标签
            if class_item.classroom:
                classroom_label = QLabel(class_item.classroom)
                classroom_label.setFont(QFont("Arial", 8))
                classroom_label.setStyleSheet("color: #888;")
                layout.addWidget(classroom_label)
            
            layout.addStretch()
            
            # 添加点击事件
            widget.mousePressEvent = lambda event: self.class_clicked.emit(class_item.id)
            
            return widget
            
        except Exception as e:
            self.logger.error(f"创建课程widget失败: {e}")
            return QWidget()
    
    def _format_duration(self, duration: timedelta) -> str:
        """格式化时间间隔"""
        try:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            
            if hours > 0:
                return f"{hours}小时{minutes}分钟"
            
                return f"{hours}小时{minutes}分钟"
            elif minutes > 0:
                return f"{minutes}分钟{seconds}秒"
            else:
                return f"{seconds}秒"
                
        except Exception:
            return "未知"
    
    def set_schedule(self, schedule: Optional[Schedule]):
        """设置课程表"""
        try:
            self.schedule = schedule
            self.update_content()
            self.logger.debug(f"设置课程表: {schedule.name if schedule else None}")
            
        except Exception as e:
            self.logger.error(f"设置课程表失败: {e}")
    
    def get_update_interval(self) -> int:
        """获取更新间隔（1秒）"""
        return 1000
    
    def on_config_updated(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """配置更新回调"""
        try:
            # 检查是否需要重新初始化UI
            old_settings = old_config.get('settings', {})
            new_settings = new_config.get('settings', {})
            
            ui_changed = (
                old_settings.get('show_current_class') != new_settings.get('show_current_class') or
                old_settings.get('show_next_class') != new_settings.get('show_next_class')
            )
            
            
            if ui_changed:
                # 重新初始化组件:
            
                # 重新初始化组件
                self.initialize_component()
            else:
                # 只更新内容
                self.update_content()
            
        except Exception as e:
            self.logger.error(f"处理配置更新失败: {e}")
    
    def cleanup_component(self):
        """清理组件资源"""
        try:
            # 断开编辑按钮信号连接
            if self.edit_button:
                self.edit_button.clicked.disconnect()
            
            self.schedule = None
            self.current_class = None
            self.next_class = None
            
        except Exception as e:
            self.logger.error(f"清理课程表组件失败: {e}")