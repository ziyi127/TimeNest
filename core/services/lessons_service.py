import logging
from datetime import datetime, timedelta, time
from typing import Optional, Dict, Any, List
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication

from core.services.time_service import TimeService
from core.models.profile import TimeNestProfile
from models.class_plan import ClassPlan, ClassInfo, TimeRule
from models.time_layout import TimeLayout, TimeLayoutItem
from models.subject import Subject

# 时间状态枚举
class TimeState:
    NONE = "None"
    ON_CLASS = "OnClass" 
    BREAKING = "Breaking"
    AFTER_SCHOOL = "AfterSchool"
    PREPARE_ON_CLASS = "PrepareOnClass"

class LessonsService(QObject):
    """课程服务 - 管理课程表逻辑，基于ClassIsland的LessonsService实现"""
    
    # 信号定义
    pre_main_timer_ticked = Signal()
    post_main_timer_ticked = Signal()
    on_class = Signal()
    on_breaking_time = Signal()
    on_after_school = Signal()
    current_time_state_changed = Signal()
    
    def __init__(self, settings_service=None, profile_service=None, 
                 exact_time_service: TimeService = None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # 服务依赖
        self.settings_service = settings_service
        self.profile_service = profile_service
        self.exact_time_service = exact_time_service
        
        # 状态变量
        self.current_class_plan = None
        self.current_selected_index = -1
        self.next_class_subject = None
        self.next_breaking_time_layout_item = None
        self.on_class_left_time = timedelta()
        self.current_state = TimeState.NONE
        self.current_overlay_status = TimeState.NONE
        self.current_time_layout_item = None
        self.current_subject = None
        self.is_class_plan_enabled = True
        self.current_overlay_event_status = TimeState.NONE
        self.is_class_plan_loaded = False
        self.is_lesson_confirmed = False
        self.on_breaking_time_left_time = timedelta()
        self.next_class_time_layout_item = None
        
        # 初始化主定时器
        self.main_timer = QTimer(self)
        self.main_timer.setInterval(50)  # 50毫秒
        self.main_timer.timeout.connect(self.main_timer_on_tick)
        
        # 启动定时器
        self.start_main_timer()
        
        # 初始化课程表
        self.process_lessons()
        
    def start_main_timer(self):
        """启动主定时器"""
        self.main_timer.start()
        
    def stop_main_timer(self):
        """停止主定时器"""
        self.main_timer.stop()
        
    def main_timer_on_tick(self):
        """主定时器触发事件"""
        try:
            # 发出预处理信号
            self.pre_main_timer_ticked.emit()
            
            # 处理课程逻辑
            self.process_lessons()
            
            # 发出后处理信号
            self.post_main_timer_ticked.emit()
            
        except Exception as e:
            self.logger.error(f"主定时器处理出错: {e}")
            
    def process_lessons(self):
        """处理课程逻辑"""
        # 加载当前课程表
        self.load_current_class_plan()
        
        # 预定所有需要更新的信息
        current_selected_index = None
        current_state = None
        current_subject = None
        next_class_subject = None
        current_time_layout_item = None
        next_class_time_layout_item = None
        next_breaking_time_layout_item = None
        on_class_left_time = None
        on_breaking_time_left_time = None
        is_lesson_confirmed = None
        is_class_plan_loaded = None
        
        # 获取时间布局
        layout = None
        if self.current_class_plan and "time_layout" in self.current_class_plan:
            layout = self.current_class_plan["time_layout"].get("layouts", [])
            
        if not layout:  # 当前没有课表时，跳过获取信息
            goto_final = True
        else:
            goto_final = False
            
        if not goto_final:
            # 开始获取信息
            is_class_plan_loaded = True
            
            # 获取当前时间
            if self.exact_time_service:
                now = self.exact_time_service.get_current_local_datetime().time()
            else:
                now = datetime.now().time()
                
            # 获取有效的课程表时间点
            valid_time_layout_items = self.get_valid_time_layout_items()
            
            # 获取当前时间点信息
            current_time_layout_item = None
            for item in valid_time_layout_items:
                start_time = self.parse_time_string(item.get("start_time", "00:00"))
                end_time = self.parse_time_string(item.get("end_time", "00:00"))
                if item.get("time_type", 0) in [0, 1] and start_time <= now <= end_time:
                    current_time_layout_item = item
                    break
                    
            if current_time_layout_item:
                current_selected_index = layout.index(current_time_layout_item) if current_time_layout_item in layout else -1
                time_type = current_time_layout_item.get("time_type", 0)
                
                if time_type == 0:  # 上课
                    current_state = TimeState.ON_CLASS
                    # 获取当前科目
                    class_index = self.get_class_index(current_selected_index)
                    if (class_index >= 0 and self.current_class_plan and 
                        "classes" in self.current_class_plan and 
                        len(self.current_class_plan["classes"]) > class_index):
                        class_info = self.current_class_plan["classes"][class_index]
                        subject_id = class_info.get("subject_id")
                        if subject_id and self.profile_service:
                            subjects = self.profile_service.get_all_subjects()
                            current_subject = subjects.get(subject_id)
                elif time_type == 1:  # 课间
                    current_state = TimeState.BREAKING
                    current_subject = {
                        "name": current_time_layout_item.get("break_name_text", "课间休息"),
                        "initial": "休"
                    }
                is_lesson_confirmed = True
                
            # 获取下节时间点信息
            next_class_time_layout_item = None
            for item in valid_time_layout_items:
                start_time = self.parse_time_string(item.get("start_time", "00:00"))
                if item.get("time_type", 0) == 0 and start_time >= now:
                    next_class_time_layout_item = item
                    break
                    
            if next_class_time_layout_item:
                class_index = self.get_class_index(layout.index(next_class_time_layout_item))
                if (class_index >= 0 and self.current_class_plan and 
                    "classes" in self.current_class_plan and 
                    len(self.current_class_plan["classes"]) > class_index):
                    class_info = self.current_class_plan["classes"][class_index]
                    subject_id = class_info.get("subject_id")
                    if subject_id and self.profile_service:
                        subjects = self.profile_service.get_all_subjects()
                        next_class_subject = subjects.get(subject_id)
                        
            # 获取下个课间时间点信息
            next_breaking_time_layout_item = None
            for item in valid_time_layout_items:
                start_time = self.parse_time_string(item.get("start_time", "00:00"))
                if item.get("time_type", 0) == 1 and start_time >= now:
                    next_breaking_time_layout_item = item
                    break
                    
            # 获取剩余时间信息
            if current_state == TimeState.ON_CLASS and next_breaking_time_layout_item:
                next_break_start = self.parse_time_string(next_breaking_time_layout_item.get("start_time", "00:00"))
                on_breaking_time_left_time = datetime.combine(datetime.today(), next_break_start) - datetime.combine(datetime.today(), now)
            elif next_class_time_layout_item:
                next_class_start = self.parse_time_string(next_class_time_layout_item.get("start_time", "00:00"))
                on_class_left_time = datetime.combine(datetime.today(), next_class_start) - datetime.combine(datetime.today(), now)
                
            # 检查是否放学
            if not next_class_time_layout_item and not next_breaking_time_layout_item:
                current_state = TimeState.AFTER_SCHOOL
                
        # 统一更新信息
        self.current_selected_index = current_selected_index if current_selected_index is not None else -1
        self.current_state = current_state if current_state is not None else TimeState.NONE
        self.current_subject = current_subject
        self.next_class_subject = next_class_subject
        self.current_time_layout_item = current_time_layout_item
        self.next_class_time_layout_item = next_class_time_layout_item
        self.next_breaking_time_layout_item = next_breaking_time_layout_item
        self.on_class_left_time = self.at_least_zero(on_class_left_time) if on_class_left_time is not None else timedelta()
        self.on_breaking_time_left_time = self.at_least_zero(on_breaking_time_left_time) if on_breaking_time_left_time is not None else timedelta()
        self.is_lesson_confirmed = is_lesson_confirmed if is_lesson_confirmed is not None else False
        self.is_class_plan_loaded = is_class_plan_loaded if is_class_plan_loaded is not None else False
        
        # 发出状态变更事件
        if self.current_state != self.current_overlay_event_status:
            self.current_time_state_changed.emit()
            
            # 根据状态发出相应事件
            if self.current_state == TimeState.ON_CLASS:
                self.on_class.emit()
            elif self.current_state == TimeState.BREAKING:
                self.on_breaking_time.emit()
            elif self.current_state == TimeState.AFTER_SCHOOL:
                self.on_after_school.emit()
                
            self.current_overlay_event_status = self.current_state
            
    def at_least_zero(self, time_delta: Optional[timedelta]) -> Optional[timedelta]:
        """确保时间差不为负数"""
        if time_delta is None:
            return None
        return time_delta if time_delta >= timedelta() else timedelta()
        
    def get_class_index(self, index: int) -> int:
        """获取课程索引"""
        if (index < 0 or not self.current_class_plan or 
            "time_layout" not in self.current_class_plan or
            "layouts" not in self.current_class_plan["time_layout"]):
            return -1
            
        layouts = self.current_class_plan["time_layout"]["layouts"]
        if index >= len(layouts):
            return -1
            
        # 获取所有上课时间点
        class_time_points = [layout for layout in layouts if layout.get("time_type", 0) == 0]
        target_layout = layouts[index]
        
        # 找到目标时间点在上课时间点中的索引
        try:
            class_index = class_time_points.index(target_layout)
            return class_index
        except ValueError:
            return -1
            
    def load_current_class_plan(self):
        """加载当前课程表"""
        if not self.is_class_plan_enabled:
            self.current_class_plan = None
            return
            
        # 获取当前时间
        if self.exact_time_service:
            current_time = self.exact_time_service.get_current_local_datetime()
        else:
            current_time = datetime.now()
            
        # 获取课程表
        self.current_class_plan = self.get_class_plan_by_date(current_time.date())
        
    def get_class_plan_by_date(self, date: datetime.date) -> Optional[Dict[str, Any]]:
        """根据日期获取课程表"""
        if not self.profile_service:
            return self.get_sample_class_plan()
            
        # 简化实现 - 实际应该从profile_service获取
        return self.get_sample_class_plan()
        
    def get_sample_class_plan(self) -> Optional[Dict[str, Any]]:
        """获取示例课程表"""
        return {
            "id": "sample-plan-1",
            "name": "示例课表",
            "time_layout_id": "sample-layout-1",
            "time_layout": {
                "id": "sample-layout-1",
                "name": "示例时间表",
                "layouts": [
                    {
                        "id": "layout-1",
                        "start_time": "08:00",
                        "end_time": "08:45",
                        "time_type": 0,  # 上课
                        "default_class_id": "math1"
                    },
                    {
                        "id": "layout-2",
                        "start_time": "08:45",
                        "end_time": "08:55",
                        "time_type": 1,  # 课间
                        "break_name_text": "课间休息"
                    },
                    {
                        "id": "layout-3",
                        "start_time": "08:55",
                        "end_time": "09:40",
                        "time_type": 0,  # 上课
                        "default_class_id": "english1"
                    },
                    {
                        "id": "layout-4",
                        "start_time": "09:40",
                        "end_time": "09:50",
                        "time_type": 1,  # 课间
                        "break_name_text": "课间休息"
                    },
                    {
                        "id": "layout-5",
                        "start_time": "09:50",
                        "end_time": "10:35",
                        "time_type": 0,  # 上课
                        "default_class_id": "chinese1"
                    }
                ]
            },
            "classes": [
                {
                    "id": "class-1",
                    "subject_id": "math1",
                    "index": 0,
                    "is_enabled": True
                },
                {
                    "id": "class-2",
                    "subject_id": "english1",
                    "index": 1,
                    "is_enabled": True
                },
                {
                    "id": "class-3",
                    "subject_id": "chinese1",
                    "index": 2,
                    "is_enabled": True
                }
            ]
        }
        
    def get_valid_time_layout_items(self) -> List[Dict[str, Any]]:
        """获取有效的课程表时间点"""
        if not self.current_class_plan or "time_layout" not in self.current_class_plan:
            return []
            
        time_layout = self.current_class_plan["time_layout"]
        if "layouts" not in time_layout:
            return []
            
        # 过滤出有效的时间点（上课、课间、分割线）
        valid_items = [item for item in time_layout["layouts"] 
                      if item.get("time_type", 0) in [0, 1, 2]]
                      
        return valid_items
        
    def parse_time_string(self, time_str: str) -> time:
        """解析时间字符串"""
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return time(0, 0)
            
    def debug_trigger_on_class(self):
        """调试触发上课事件"""
        self.on_class.emit()
        
    def debug_trigger_on_breaking_time(self):
        """调试触发课间事件"""
        self.on_breaking_time.emit()
        
    def debug_trigger_on_after_school(self):
        """调试触发放学事件"""
        self.on_after_school.emit()
        
    def debug_trigger_on_state_changed(self):
        """调试触发状态变化事件"""
        self.current_time_state_changed.emit()
        
    @property
    def is_timer_running(self) -> bool:
        """获取定时器是否正在运行"""
        return self.main_timer.isActive()
