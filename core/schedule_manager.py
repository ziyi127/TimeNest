# -*- coding: utf-8 -*-
"""
TimeNest 课程表管理器
负责课程表数据的加载、保存、状态管理等功能
"""

import logging
import json
import yaml
from typing import List, Dict, Optional, Any
from datetime import datetime, date, time, timedelta
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from models.schedule import Schedule, ClassItem, TimeSlot, Subject
from core.config_manager import ConfigManager
from core.attached_settings import AttachedSettingsHostService
from core.notification_service import NotificationHostService, create_notification, NotificationType, NotificationPriority
from utils.excel_exporter_v2 import ExcelExporterV2

class ScheduleManager(QObject):
    """课程表管理器"""
    
    # 信号定义
    current_class_changed = pyqtSignal(object)  # 当前课程变化
    schedule_updated = pyqtSignal()  # 课程表更新
    class_status_changed = pyqtSignal(str, str)  # 课程状态变化 (class_id, status)
    
    def __init__(self, config_manager: ConfigManager,
                 attached_settings_service: Optional[AttachedSettingsHostService] = None,
                 notification_service: Optional[NotificationHostService] = None):
        """
        课程表管理器
        :param config_manager: 配置管理器
        :param attached_settings_service: 附加设置主机服务
        :param notification_service: 通知主机服务
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.attached_settings_service = attached_settings_service or AttachedSettingsHostService()
        self.notification_service = notification_service or NotificationHostService()
        # 当前加载的课程表
        self.current_schedule: Optional[Schedule] = None
        self.current_class: Optional[ClassItem] = None
        self.last_update_time: Optional[datetime] = None
        # 课程状态缓存
        self.class_status_cache: Dict[str, str] = {}

        # 性能优化缓存
        self._current_class_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 30  # 缓存30秒
        # 加载默认课程表
        self._load_default_schedule()
        self.logger.info("课程表管理器初始化完成")
    
    def _load_default_schedule(self):
        """加载默认课程表"""
        try:
            default_schedule_path = self.config_manager.get('schedule.default_file')
            if default_schedule_path and Path(default_schedule_path).exists():
                self.load_schedule_file(default_schedule_path)
            else:
                # 创建示例课程表
                self._create_sample_schedule()
        except Exception as e:
            self.logger.error(f"加载默认课程表失败: {e}")
            self._create_sample_schedule()
    
    def _create_sample_schedule(self):
        """创建示例课程表"""
        try:
            # 创建示例时间段
            time_slots = [
                TimeSlot("1", "第一节", time(8, 0), time(8, 45)),
                TimeSlot("2", "第二节", time(8, 55), time(9, 40)),
                TimeSlot("3", "第三节", time(10, 0), time(10, 45)),
                TimeSlot("4", "第四节", time(10, 55), time(11, 40)),
                TimeSlot("5", "第五节", time(14, 0), time(14, 45)),
                TimeSlot("6", "第六节", time(14, 55), time(15, 40)),
                TimeSlot("7", "第七节", time(16, 0), time(16, 45)),
                TimeSlot("8", "第八节", time(16, 55), time(17, 40)),
            ]
            
            # 创建示例科目
            subjects = [
                Subject("math", "数学", "#FF5722"),
                Subject("chinese", "语文", "#2196F3"),
                Subject("english", "英语", "#4CAF50"),
                Subject("physics", "物理", "#9C27B0"),
                Subject("chemistry", "化学", "#FF9800"),
                Subject("biology", "生物", "#795548"),
                Subject("history", "历史", "#607D8B"),
                Subject("geography", "地理", "#009688"),
            ]
            
            # 创建示例课程表
            schedule = Schedule(
                name="示例课程表",
                time_slots=time_slots,
                subjects=subjects
            )
            
            # 添加示例课程
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
            subject_rotation = ["math", "chinese", "english", "physics", "chemistry", "biology", "history", "geography"]
            
            for day_idx, weekday in enumerate(weekdays):
                for slot_idx, time_slot in enumerate(time_slots):
                    if slot_idx < 4:  # 上午课程
                        subject_id = subject_rotation[(day_idx * 4 + slot_idx) % len(subject_rotation)]
                        class_item = ClassItem(
                            id=f"{weekday}_{time_slot.id}",
                            subject_id=subject_id,
                            time_slot_id=time_slot.id,
                            weekday=weekday,
                            classroom="教室A",
                            teacher="老师"
                        )
                        schedule.add_class(class_item)
                    elif slot_idx >= 4:  # 下午课程
                        subject_id = subject_rotation[(day_idx * 4 + slot_idx - 4) % len(subject_rotation)]
                        class_item = ClassItem(
                            id=f"{weekday}_{time_slot.id}",
                            subject_id=subject_id,
                            time_slot_id=time_slot.id,
                            weekday=weekday,
                            classroom="教室B",
                            teacher="老师"
                        )
                        schedule.add_class(class_item)
            
            self.current_schedule = schedule
            self.schedule_updated.emit()
            self.logger.info("创建示例课程表完成")
            
        except Exception as e:
            self.logger.error(f"创建示例课程表失败: {e}")
    
    def load_schedule_file(self, file_path: str) -> bool:
        """加载课程表文件"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"课程表文件不存在: {file_path}")
                return False
            
            # 根据文件扩展名选择加载方式
            if file_path.suffix.lower() == '.json':
                schedule = self._load_json_schedule(file_path)
            elif file_path.suffix.lower() in ['.yml', '.yaml']:
                schedule = self._load_yaml_schedule(file_path)
            else:
                self.logger.error(f"不支持的文件格式: {file_path.suffix}")
                return False
            
            if schedule:
                self.current_schedule = schedule
                self.schedule_updated.emit()
                self.config_manager.set('schedule.default_file', str(file_path))
                self.logger.info(f"成功加载课程表: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"加载课程表文件失败: {e}")
            return False
    
    def _load_json_schedule(self, file_path: Path) -> Optional[Schedule]:
        """从JSON文件加载课程表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Schedule.from_dict(data)
        except Exception as e:
            self.logger.error(f"解析JSON课程表失败: {e}")
            return None
    
    def _load_yaml_schedule(self, file_path: Path) -> Optional[Schedule]:
        """从YAML文件加载课程表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return Schedule.from_dict(data)
        except Exception as e:
            self.logger.error(f"解析YAML课程表失败: {e}")
            return None
    
    def save_schedule_file(self, file_path: str) -> bool:
        """保存课程表文件"""
        try:
            if not self.current_schedule:
                self.logger.error("没有可保存的课程表")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 根据文件扩展名选择保存方式
            if file_path.suffix.lower() == '.json':
                return self._save_json_schedule(file_path)
            elif file_path.suffix.lower() in ['.yml', '.yaml']:
                return self._save_yaml_schedule(file_path)
            else:
                self.logger.error(f"不支持的文件格式: {file_path.suffix}")
                return False
                
        except Exception as e:
            self.logger.error(f"保存课程表文件失败: {e}")
            return False
    
    def _save_json_schedule(self, file_path: Path) -> bool:
        """保存为JSON格式"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_schedule.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功保存JSON课程表: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存JSON课程表失败: {e}")
            return False
    
    def _save_yaml_schedule(self, file_path: Path) -> bool:
        """保存为YAML格式"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.current_schedule.to_dict(), f, allow_unicode=True, default_flow_style=False)
            self.logger.info(f"成功保存YAML课程表: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存YAML课程表失败: {e}")
            return False
    
    def export_to_excel(self, file_path: str) -> bool:
        """导出课程表到Excel"""
        try:
            if not self.current_schedule:
                self.logger.error("没有可导出的课程表")
                return False
            
            exporter = ExcelExporter()
            return exporter.export_schedule(self.current_schedule, file_path)
            
        except Exception as e:
            self.logger.error(f"导出Excel失败: {e}")
            return False
    
    def update_current_status(self, current_time: datetime):
        """
        更新当前课程状态，并根据附加设置和通知服务自动提醒。
        """
        try:
            if not self.current_schedule:
                return
            # 获取当前时间对应的课程
            new_current_class = self._get_current_class_at_time(current_time)
            # 检查当前课程是否发生变化
            if new_current_class != self.current_class:
                old_class = self.current_class
                self.current_class = new_current_class
                self.current_class_changed.emit(new_current_class)
                # 更新课程状态
                self._update_class_statuses(current_time)
                self.logger.debug(f"当前课程变化: {old_class} -> {new_current_class}")
                # ===== doc/AttachedSettings.md: 按优先级获取附加设置并自动提醒 =====
                if new_current_class:
                    subject = self.current_schedule.get_subject(new_current_class.subject_id)
                    time_layout_item = new_current_class
                    class_plan = None  # 可扩展
                    time_layout = None  # 可扩展
                    # 获取附加设置
                    attached_settings = self.attached_settings_service.get_attached_settings_by_priority(
                        subject, time_layout_item, class_plan, time_layout)
                    # 检查是否启用提醒
                    enable_reminder = attached_settings.get("enable_reminder")
                    reminder_minutes = attached_settings.get("reminder_minutes")
                    if enable_reminder and getattr(enable_reminder, "value", True):
                        # 发送通知
                        title = f"即将上课：{subject.name if subject else ''}"
                        message = f"{subject.name if subject else ''} 即将在 {reminder_minutes.value if reminder_minutes else 5} 分钟后开始。"
                        notification_req = create_notification(
                            title=title,
                            message=message,
                            notification_type=NotificationType.CLASS_REMINDER,
                            priority=NotificationPriority.HIGH
                        )
                        self.notification_service.send_notification(notification_req)
            self.last_update_time = current_time
        except Exception as e:
            self.logger.error(f"更新课程状态失败: {e}")
    
    def _get_current_class_at_time(self, current_time: datetime) -> Optional[ClassItem]:
        """获取指定时间的当前课程（带缓存优化）"""
        if not self.current_schedule:
            return None

        # 检查缓存是否有效
        if (self._cache_timestamp and
            self._current_class_cache is not None and
            (current_time.timestamp() - self._cache_timestamp) < self._cache_ttl):
            return self._current_class_cache

        current_date = current_time.date()
        current_time_only = current_time.time()
        weekday = self._get_weekday_name(current_date)

        # 获取当天的课程
        today_classes = self.current_schedule.get_classes_by_weekday(weekday)

        current_class = None
        for class_item in today_classes:
            time_slot = self.current_schedule.get_time_slot(class_item.time_slot_id)
            if time_slot and time_slot.start_time <= current_time_only <= time_slot.end_time:
                current_class = class_item
                break

        # 更新缓存
        self._current_class_cache = current_class
        self._cache_timestamp = current_time.timestamp()

        return current_class
    
    def _update_class_statuses(self, current_time: datetime):
        """更新所有课程的状态"""
        if not self.current_schedule:
            return
        
        current_date = current_time.date()
        current_time_only = current_time.time()
        weekday = self._get_weekday_name(current_date)
        
        today_classes = self.current_schedule.get_classes_by_weekday(weekday)
        
        for class_item in today_classes:
            time_slot = self.current_schedule.get_time_slot(class_item.time_slot_id)
            if not time_slot:
                continue
            
            # 确定课程状态
            if current_time_only < time_slot.start_time:
                status = "即将开始"
            elif time_slot.start_time <= current_time_only <= time_slot.end_time:
                status = "进行中"
            else:
                status = "已结束"
            
            # 检查状态是否发生变化
            old_status = self.class_status_cache.get(class_item.id)
            if old_status != status:
                self.class_status_cache[class_item.id] = status
                self.class_status_changed.emit(class_item.id, status)
    
    def _get_weekday_name(self, date_obj: date) -> str:
        """获取星期名称"""
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        return weekdays[date_obj.weekday()]
    
    def get_current_class(self) -> Optional[ClassItem]:
        """获取当前课程"""
        return self.current_class
    
    def get_today_schedule(self) -> List[ClassItem]:
        """获取今日课程表"""
        if not self.current_schedule:
            return []
        
        today = date.today()
        weekday = self._get_weekday_name(today)
        return self.current_schedule.get_classes_by_weekday(weekday)
    
    def get_tomorrow_schedule(self) -> List[ClassItem]:
        """获取明日课程表"""
        if not self.current_schedule:
            return []
        
        tomorrow = date.today() + timedelta(days=1)
        weekday = self._get_weekday_name(tomorrow)
        return self.current_schedule.get_classes_by_weekday(weekday)
    
    def get_schedule(self) -> Optional[Schedule]:
        """获取当前课程表"""
        return self.current_schedule
    
    def get_class_status(self, class_id: str) -> str:
        """获取课程状态"""
        return self.class_status_cache.get(class_id, "未知")
    
    def add_class(self, class_item: ClassItem) -> bool:
        """添加课程"""
        try:
            if not self.current_schedule:
                self.logger.error("没有加载的课程表")
                return False
            
            self.current_schedule.add_class(class_item)
            self.schedule_updated.emit()
            self.logger.info(f"添加课程: {class_item.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加课程失败: {e}")
            return False
    
    def remove_class(self, class_id: str) -> bool:
        """移除课程"""
        try:
            if not self.current_schedule:
                self.logger.error("没有加载的课程表")
                return False
            
            self.current_schedule.remove_class(class_id)
            self.schedule_updated.emit()
            self.logger.info(f"移除课程: {class_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除课程失败: {e}")
            return False
    
    def update_class(self, class_item: ClassItem) -> bool:
        """更新课程"""
        try:
            if not self.current_schedule:
                self.logger.error("没有加载的课程表")
                return False
            
            self.current_schedule.update_class(class_item)
            self.schedule_updated.emit()
            self.logger.info(f"更新课程: {class_item.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新课程失败: {e}")
            return False