# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

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
from functools import lru_cache
from PySide6.QtCore import QObject, Signal

from models.schedule import Schedule, ClassItem, TimeSlot, Subject
from core.config_manager import ConfigManager
from core.attached_settings import AttachedSettingsHostService
from core.notification_service import NotificationHostService, create_notification, NotificationType, NotificationPriority
from utils.excel_exporter_v2 import ExcelExporterV2

class ScheduleManager(QObject):
    """课程表管理器"""
    
    # 信号定义
    current_class_changed = Signal(object)  # 当前课程变化
    schedule_updated = Signal()  # 课程表更新
    class_status_changed = Signal(str, str)  # 课程状态变化 (class_id, status)
    
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

        # 课程数据缓存
        self._courses_cache = None
        self._courses_cache_timestamp = None

        # 查找字典缓存
        self._subjects_dict = {}
        self._time_slots_dict = {}
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
                    if slot_idx < 4:  # 上午课程:
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
                    elif slot_idx >= 4:  # 下午课程:
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
                # ==  == = doc/AttachedSettings.md: 按优先级获取附加设置并自动提醒 ==  == =
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
        weekday = self._get_weekday_name(current_date.weekday())

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
        weekday = self._get_weekday_name(current_date.weekday())
        
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
    
    @lru_cache(maxsize=7)
    def _get_weekday_name(self, weekday_index: int) -> str:
        """获取星期名称（缓存版本）"""
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        return weekdays[weekday_index]
    
    def get_current_class(self) -> Optional[ClassItem]:
        """获取当前课程"""
        return self.current_class
    
    def get_today_schedule(self) -> List[ClassItem]:
        """获取今日课程表"""
        if not self.current_schedule:
            return []
        
        today = date.today()
        weekday = self._get_weekday_name(today.weekday())
        return self.current_schedule.get_classes_by_weekday(weekday)
    
    def get_tomorrow_schedule(self) -> List[ClassItem]:
        """获取明日课程表"""
        if not self.current_schedule:
            return []
        
        tomorrow = date.today() + timedelta(days=1)
        weekday = self._get_weekday_name(tomorrow.weekday())
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

    def clear_all_courses(self) -> bool:
        """清空所有课程"""
        try:
            if not self.current_schedule:
                self.logger.error("没有加载的课程表")
                return False

            # 清空课程表中的所有课程
            self.current_schedule.classes.clear()
            self.schedule_updated.emit()
            self.logger.info("已清空所有课程")
            return True

        except Exception as e:
            self.logger.error(f"清空课程失败: {e}")
            return False

    def _invalidate_cache(self):
        """清除缓存"""
        if hasattr(self, '_courses_cache'):
            self._courses_cache = None
            self._cache_timestamp = None
        if hasattr(self, '_subjects_dict'):
            self._subjects_dict.clear()
        if hasattr(self, '_time_slots_dict'):
            self._time_slots_dict.clear()

    def _update_lookup_dicts(self):
        """更新查找字典"""
        if not self.current_schedule:
            return

        # 构建subjects查找字典
        if not hasattr(self, '_subjects_dict'):
            self._subjects_dict = {}
        self._subjects_dict = {s.id: s for s in self.current_schedule.subjects}

        # 构建time_slots查找字典
        if not hasattr(self, '_time_slots_dict'):
            self._time_slots_dict = {}
        self._time_slots_dict = {ts.id: ts for ts in self.current_schedule.time_slots}

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """获取所有课程数据（优化版本，带缓存）"""
        try:
            # 检查缓存是否有效
            current_time = datetime.now()
            if (hasattr(self, '_courses_cache') and self._courses_cache is not None and
                hasattr(self, '_cache_timestamp') and self._cache_timestamp is not None and
                (current_time - self._cache_timestamp).total_seconds() < 300):  # 5分钟缓存
                return self._courses_cache.copy()

            if not self.current_schedule:
                self.logger.warning("没有加载的课程表")
                return []

            # 更新查找字典
            self._update_lookup_dicts()

            courses = []
            for class_item in self.current_schedule.classes:
                # 使用字典查找，O(1)时间复杂度
                subject = self._subjects_dict.get(class_item.subject_id) if hasattr(self, '_subjects_dict') else None
                time_slot = self._time_slots_dict.get(class_item.time_slot_id) if hasattr(self, '_time_slots_dict') else None

                # 如果字典查找失败，回退到线性查找
                if not subject:
                    for s in self.current_schedule.subjects:
                        if s.id == class_item.subject_id:
                            subject = s
                            break

                if not time_slot:
                    for ts in self.current_schedule.time_slots:
                        if ts.id == class_item.time_slot_id:
                            time_slot = ts
                            break

                # 构建课程数据
                course_data = {
                    'id': class_item.id,
                    'name': subject.name if subject else f'课程{class_item.subject_id}',
                    'teacher': class_item.teacher or '未知教师',
                    'location': class_item.classroom or '未知地点',
                    'weekday': self._get_weekday_name_from_string(class_item.weekday),
                    'time': f"{time_slot.start_time}-{time_slot.end_time}" if time_slot else '未知时间',
                    'start_week': class_item.start_week or 1,
                    'end_week': class_item.end_week or 16,
                    'week': class_item.start_week or 1,  # 兼容字段
                    'day_of_week': self._get_weekday_number(class_item.weekday),
                    'start_time': time_slot.start_time if time_slot else '08:00',
                    'end_time': time_slot.end_time if time_slot else '09:40'
                }
                courses.append(course_data)

            # 更新缓存
            self._courses_cache = courses.copy()
            self._cache_timestamp = current_time

            return courses

        except Exception as e:
            self.logger.error(f"获取课程数据失败: {e}")
            return []

    def _get_weekday_number(self, weekday_str: str) -> int:
        """将星期字符串转换为数字"""
        weekday_map = {
            '周一': 1, '星期一': 1, 'Monday': 1,
            '周二': 2, '星期二': 2, 'Tuesday': 2,
            '周三': 3, '星期三': 3, 'Wednesday': 3,
            '周四': 4, '星期四': 4, 'Thursday': 4,
            '周五': 5, '星期五': 5, 'Friday': 5,
            '周六': 6, '星期六': 6, 'Saturday': 6,
            '周日': 7, '星期日': 7, 'Sunday': 7
        }
        return weekday_map.get(weekday_str, 1)

    def add_course(self, name: str, teacher: str, location: str, time: str, start_week: int, end_week: int, weekday: str = None) -> bool:
        """添加课程（简化接口）"""
        try:
            # 解析时间信息
            time_parts = time.split('-')
            if len(time_parts) != 2:
                self.logger.error(f"时间格式错误: {time}")
                return False

            start_time = time_parts[0].strip()
            end_time = time_parts[1].strip()

            # 转换weekday为英文格式
            weekday_en = self._convert_weekday_to_english(weekday) if weekday else 'monday'

            # 创建课程对象
            from models.schedule import Subject, TimeSlot, ClassItem
            from datetime import time as dt_time
            import uuid

            # 解析时间字符串为time对象
            try:
                start_time_obj = dt_time.fromisoformat(start_time + ':00')
                end_time_obj = dt_time.fromisoformat(end_time + ':00')
            except ValueError:
                # 如果时间格式不正确，尝试其他格式
                try:
                    start_hour, start_min = map(int, start_time.split(':'))
                    end_hour, end_min = map(int, end_time.split(':'))
                    start_time_obj = dt_time(start_hour, start_min)
                    end_time_obj = dt_time(end_hour, end_min)
                except:
                    self.logger.error(f"无法解析时间格式: {start_time} - {end_time}")
                    return False

            subject_id = f"SUBJ_{uuid.uuid4().hex[:8]}"
            time_slot_id = f"TS_{uuid.uuid4().hex[:8]}"

            # 创建Subject对象
            subject = Subject(
                id=subject_id,
                name=name,
                teacher=teacher
            )

            # 创建TimeSlot对象
            time_slot = TimeSlot(
                id=time_slot_id,
                name=f"{start_time}-{end_time}",
                start_time=start_time_obj,
                end_time=end_time_obj
            )

            # 创建ClassItem对象
            class_item = ClassItem(
                id=f"CLASS_{uuid.uuid4().hex[:8]}",
                subject_id=subject_id,
                time_slot_id=time_slot_id,
                weekday=weekday_en,
                classroom=location,
                teacher=teacher,
                start_week=start_week,
                end_week=end_week
            )

            # 添加到当前课程表
            if not self.current_schedule:
                from models.schedule import Schedule
                self.current_schedule = Schedule(name="导入的课程表")

            # 添加Subject和TimeSlot到Schedule
            self.current_schedule.add_subject(subject)
            self.current_schedule.add_time_slot(time_slot)
            self.current_schedule.add_class(class_item)

            self.schedule_updated.emit()
            self.logger.info(f"成功添加课程: {name}")
            return True

        except Exception as e:
            self.logger.error(f"添加课程失败: {e}")
            return False

    def _convert_weekday_to_english(self, weekday: str) -> str:
        """将星期字符串转换为英文格式"""
        weekday_map = {
            '周一': 'monday', '星期一': 'monday', 'monday': 'monday',
            '周二': 'tuesday', '星期二': 'tuesday', 'tuesday': 'tuesday',
            '周三': 'wednesday', '星期三': 'wednesday', 'wednesday': 'wednesday',
            '周四': 'thursday', '星期四': 'thursday', 'thursday': 'thursday',
            '周五': 'friday', '星期五': 'friday', 'friday': 'friday',
            '周六': 'saturday', '星期六': 'saturday', 'saturday': 'saturday',
            '周日': 'sunday', '星期日': 'sunday', 'sunday': 'sunday'
        }
        return weekday_map.get(weekday.lower() if weekday else '', 'monday')

    def delete_course(self, course_id: int) -> bool:
        """删除课程（通过ID）"""
        try:
            # 将数字ID转换为字符串ID进行查找
            course_id_str = str(course_id)

            if not self.current_schedule:
                return False

            # 查找并删除课程
            for class_item in self.current_schedule.classes[:]:  # 使用切片复制避免修改时迭代
                if class_item.id == course_id_str or class_item.id.endswith(course_id_str):
                    self.current_schedule.classes.remove(class_item)
                    self.schedule_updated.emit()
                    self.logger.info(f"删除课程: {course_id}")
                    return True

            self.logger.warning(f"未找到课程: {course_id}")
            return False

        except Exception as e:
            self.logger.error(f"删除课程失败: {e}")
            return False

    def update_course(self, course_id: int, course_data: Dict[str, Any]) -> bool:
        """更新课程信息"""
        try:
            course_id_str = str(course_id)

            if not self.current_schedule:
                return False

            # 查找并更新课程
            for class_item in self.current_schedule.classes:
                if class_item.id == course_id_str or class_item.id.endswith(course_id_str):
                    # 更新课程信息
                    if 'name' in course_data and class_item.subject:
                        class_item.subject.name = course_data['name']
                    if 'teacher' in course_data:
                        class_item.teacher = course_data['teacher']
                    if 'location' in course_data:
                        class_item.location = course_data['location']
                    if 'start_week' in course_data:
                        class_item.start_week = course_data['start_week']
                    if 'end_week' in course_data:
                        class_item.end_week = course_data['end_week']

                    self.schedule_updated.emit()
                    self.logger.info(f"更新课程: {course_id}")
                    return True

            self.logger.warning(f"未找到课程: {course_id}")
            return False

        except Exception as e:
            self.logger.error(f"更新课程失败: {e}")
            return False

    def _get_weekday_name(self, weekday: int) -> str:
        """获取星期名称"""
        weekday_names = {
            1: "周一", 2: "周二", 3: "周三", 4: "周四",
            5: "周五", 6: "周六", 7: "周日"
        }
        return weekday_names.get(weekday, "未知")

    def _get_weekday_name_from_string(self, weekday: str) -> str:
        """从字符串获取星期名称"""
        weekday_map = {
            'monday': '周一', 'tuesday': '周二', 'wednesday': '周三',
            'thursday': '周四', 'friday': '周五', 'saturday': '周六', 'sunday': '周日'
        }
        return weekday_map.get(weekday.lower(), weekday)