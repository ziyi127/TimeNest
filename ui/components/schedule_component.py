import logging
from datetime import datetime, timedelta, time
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont

from models.component_settings.schedule_component_settings import ScheduleComponentSettings
from core.services.time_service import TimeService
from core.models.profile import TimeNestProfile
from core.services.lessons_service import TimeState


class ScheduleComponent(QWidget):
    """课程表组件 - 显示当前和明天的课程安排，基于ClassIsland的ScheduleComponent实现"""
    
    # 信号定义
    current_time_state_changed = Signal()
    on_class = Signal()
    on_breaking_time = Signal()
    on_after_school = Signal()
    
    def __init__(self, lessons_service=None, exact_time_service: TimeService = None, 
                 profile_service=None, settings_service=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # 服务依赖
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.profile_service = profile_service
        self.settings_service = settings_service
        
        # 组件设置
        self.settings = ScheduleComponentSettings()
        
        # 状态变量
        self.tomorrow_class_plan = None
        self.is_after_school = False
        self.show_current_lesson_only_on_class = False
        self.lessons_listbox_selected_index = -1
        self.current_class_plan = None
        self.current_subject = None
        self.current_time_layout_item = None
        self.current_state = TimeState.NONE
        self.next_class_subject = None
        self.next_breaking_time_layout_item = None
        self.on_class_left_time = timedelta()
        self.on_breaking_time_left_time = timedelta()
        self.is_lesson_confirmed = False
        self.is_class_plan_loaded = False
        self.next_class_time_layout_item = None
        
        # 初始化UI
        self.init_ui()
        
        # 连接事件
        if self.lessons_service:
            self.lessons_service.post_main_timer_ticked.connect(self.on_post_main_timer_ticked)
            self.lessons_service.current_time_state_changed.connect(self.on_current_time_state_changed)
            # 初始化状态
            self.sync_with_lessons_service()
        else:
            # 如果没有课程服务，使用自己的定时器
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_content)
            self.timer.start(60000)  # 1分钟检查一次
        
        # 初始化内容
        self.update_content()
        
    def init_ui(self):
        """初始化UI - 严格按照ClassIsland的XAML结构实现"""
        # 设置对象名称
        self.setObjectName("ScheduleComponent")
        
        # 设置布局
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setColumnStretch(0, 0)  # Tomorrow标签列
        main_layout.setColumnStretch(1, 1)  # 课程列表列
        
        # 明天标签
        self.tomorrow_label = QLabel("明天")
        self.tomorrow_label.setObjectName("Tomorrow")
        self.tomorrow_label.setStyleSheet("""
            QLabel#Tomorrow {
                background-color: #0078D4;  /* AccentFillColorDefaultBrush */
                color: white;               /* TextOnAccentFillColorPrimaryBrush */
                border-radius: 16px;
                padding: 4px 12px;
                margin: 0 4px 0 0;
                font-size: 13px;
                font-weight: bold;
                min-width: 40px;
            }
        """)
        self.tomorrow_label.setVisible(False)  # 默认隐藏
        
        # 主课程列表显示区域
        self.main_lessons_listbox = QWidget()
        self.main_lessons_listbox.setObjectName("MainLessonsListBox")
        self.main_lessons_listbox_layout = QVBoxLayout(self.main_lessons_listbox)
        self.main_lessons_listbox_layout.setContentsMargins(0, 0, 0, 0)
        self.main_lessons_listbox_layout.setSpacing(6)  # 增加间距
        
        # 空课程表占位符
        self.empty_placeholder = QLabel()
        self.empty_placeholder.setObjectName("EmptyPlaceholder")
        self.empty_placeholder.setAlignment(Qt.AlignCenter)
        self.empty_placeholder.setVisible(False)
        self.empty_placeholder.setStyleSheet("""
            QLabel#EmptyPlaceholder {
                color: #888888;
                font-size: 14px;
                font-style: italic;
            }
        """)
        
        # 添加组件到主布局
        main_layout.addWidget(self.tomorrow_label, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(self.main_lessons_listbox, 0, 1)
        
        # 占位符覆盖在课程列表上
        placeholder_layout = QHBoxLayout()
        placeholder_layout.addWidget(self.empty_placeholder)
        placeholder_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建一个容器来容纳占位符
        placeholder_container = QWidget()
        placeholder_container.setLayout(placeholder_layout)
        placeholder_container.setAttribute(Qt.WA_TransparentForMouseEvents)  # 鼠标事件穿透
        placeholder_container.setObjectName("PlaceholderContainer")
        
        # 将占位符容器添加到布局中，覆盖整个区域
        main_layout.addWidget(placeholder_container, 0, 0, 1, 2)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 应用初始样式
        self.apply_styles()
        
        # 设置最小高度
        self.setMinimumHeight(80)
        
    def apply_styles(self):
        """应用样式"""
        # 根据状态应用不同的样式类
        style_classes = []
        if self.is_after_school:
            style_classes.append("AfterSchool")
        if self.settings.hide_finished_class:
            style_classes.append("HideFinishedClass")
        if self.settings.show_placeholder_on_empty_class_plan:
            style_classes.append("ShowEmptyPlaceholder")
            
        # 构建样式类字符串
        class_string = " ".join(style_classes)
        if class_string:
            self.setProperty("class", class_string)
            
    def on_post_main_timer_ticked(self):
        """处理主定时器触发事件"""
        self.update_content()
        
    def on_current_time_state_changed(self):
        """处理当前时间状态变化事件"""
        self.current_time_state_changed.emit()
        self.update_content()
        
    def update_content(self):
        """更新课程表内容"""
        try:
            # 获取当前日期
            if self.exact_time_service:
                current_date = self.exact_time_service.get_current_local_datetime().date()
            else:
                current_date = datetime.now().date()
                
            # 获取今天的课程表
            self.current_class_plan = self.get_current_class_plan(current_date)
            self.tomorrow_class_plan = self.get_class_plan_by_date(current_date + timedelta(days=1))
            
            # 更新明天标签显示
            self.update_tomorrow_label()
            
            # 更新课程列表
            self.update_lessons_list()
            
            # 更新占位符
            self.update_empty_placeholder()
            
            # 更新样式
            self.apply_styles()
            
        except Exception as e:
            self.logger.error(f"更新课程表组件内容时出错: {e}")
            # 出错时显示错误信息
            self.empty_placeholder.setText("课程表加载错误")
            self.empty_placeholder.setVisible(True)
        
    def get_current_class_plan(self, date: datetime.date) -> Optional[Dict[str, Any]]:
        """获取当前日期的课程表"""
        if not self.profile_service:
            return self.get_sample_class_plan()
            
        # 简化实现 - 实际应该从profile_service获取
        return self.get_sample_class_plan()
        
    def get_class_plan_by_date(self, date: datetime.date) -> Optional[Dict[str, Any]]:
        """根据日期获取课程表"""
        if not self.profile_service:
            return self.get_sample_tomorrow_class_plan()
            
        # 简化实现 - 实际应该从profile_service获取
        return self.get_sample_tomorrow_class_plan()
        
    def get_sample_class_plan(self):
        """获取示例课程表数据"""
        # 简化实现 - 实际应用中应该从profile_service获取真实数据
        return {
            "name": "今日课表",
            "lessons": [
                {"name": "数学", "start_time": "08:00", "end_time": "08:45", "subject_id": "math1"},
                {"name": "英语", "start_time": "08:55", "end_time": "09:40", "subject_id": "english1"},
                {"name": "语文", "start_time": "09:50", "end_time": "10:35", "subject_id": "chinese1"},
                {"name": "物理", "start_time": "10:45", "end_time": "11:30", "subject_id": "physics1"}
            ]
        }
        
    def get_sample_tomorrow_class_plan(self):
        """获取示例明天课程表数据"""
        # 简化实现
        return {
            "name": "明日课表",
            "lessons": [
                {"name": "化学", "start_time": "08:00", "end_time": "08:45", "subject_id": "chemistry1"},
                {"name": "生物", "start_time": "08:55", "end_time": "09:40", "subject_id": "biology1"}
            ]
        }
        
    def update_tomorrow_label(self):
        """更新明天标签显示状态"""
        show_tomorrow = False
        tomorrow_schedule_empty = not self.tomorrow_class_plan or not self.tomorrow_class_plan.get("lessons")
        today_schedule_empty = not self.current_class_plan or not self.current_class_plan.get("lessons")
        
        # 根据设置决定是否显示明天课表
        if self.settings.tomorrow_schedule_show_mode == 2:  # 总是显示
            show_tomorrow = True
        elif self.settings.tomorrow_schedule_show_mode == 1:  # 放学后显示
            show_tomorrow = self.is_after_school and not tomorrow_schedule_empty
            
        # 如果有明天的课程表且需要显示，则显示标签
        if show_tomorrow and self.tomorrow_class_plan and not tomorrow_schedule_empty:
            self.tomorrow_label.setVisible(True)
        else:
            self.tomorrow_label.setVisible(False)
            
    def update_lessons_list(self):
        """更新课程列表显示"""
        # 清除现有课程项
        for i in reversed(range(self.main_lessons_listbox_layout.count())):
            widget = self.main_lessons_listbox_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # 确定使用哪个课程表
        target_class_plan = None
        show_tomorrow = False
        
        # 检查是否应该显示明天课表
        if (self.settings.tomorrow_schedule_show_mode == 2 or 
            (self.settings.tomorrow_schedule_show_mode == 1 and self.is_after_school)):
            if self.tomorrow_class_plan and self.tomorrow_class_plan.get("lessons"):
                show_tomorrow = True
                target_class_plan = self.tomorrow_class_plan
                
        # 如果不显示明天课表，则显示今天的课表
        if not show_tomorrow:
            target_class_plan = self.current_class_plan
            
        if not target_class_plan or not target_class_plan.get("lessons"):
            return
            
        # 添加课程项
        lessons = target_class_plan["lessons"]
        for i, lesson in enumerate(lessons):
            lesson_widget = self.create_lesson_widget(lesson, i)
            self.main_lessons_listbox_layout.addWidget(lesson_widget)
            
    def create_lesson_widget(self, lesson: Dict[str, Any], index: int) -> QWidget:
        """创建课程项控件"""
        widget = QFrame()
        widget.setObjectName(f"LessonItem_{index}")
        widget.setFrameStyle(QFrame.NoFrame)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        
        # 课程名称
        name_label = QLabel(lesson.get("name", "未知课程"))
        name_label.setObjectName(f"LessonName_{index}")
        name_label.setStyleSheet("""
            QLabel {
                font-weight: normal;
                font-size: 14px;
            }
        """)
        
        # 课程时间
        start_time = lesson.get("start_time", "00:00")
        end_time = lesson.get("end_time", "00:00")
        time_text = f"{start_time}-{end_time}"
        time_label = QLabel(time_text)
        time_label.setObjectName(f"LessonTime_{index}")
        time_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
            }
        """)
        
        # 添加到布局
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(time_label)
        
        # 设置课程项样式
        widget.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 4px;
            }
            QFrame:hover {
                background-color: rgba(0, 120, 212, 0.1);
            }
        """)
        
        return widget
        
    def update_empty_placeholder(self):
        """更新空课程表占位符"""
        target_class_plan = self.current_class_plan
        show_tomorrow = False
        
        # 检查是否应该显示明天课表
        if (self.settings.tomorrow_schedule_show_mode == 2 or 
            (self.settings.tomorrow_schedule_show_mode == 1 and self.is_after_school)):
            if self.tomorrow_class_plan and self.tomorrow_class_plan.get("lessons"):
                show_tomorrow = True
                target_class_plan = self.tomorrow_class_plan
                
        if not target_class_plan or not target_class_plan.get("lessons"):
            if self.settings.show_placeholder_on_empty_class_plan:
                if self.is_after_school:
                    self.empty_placeholder.setText(self.settings.placeholder_text_all_class_ended)
                else:
                    self.empty_placeholder.setText(self.settings.placeholder_text_no_class)
                self.empty_placeholder.setVisible(True)
            else:
                self.empty_placeholder.setVisible(False)
        else:
            self.empty_placeholder.setVisible(False)
                
    def get_tomorrow_class_plan(self):
        """获取明天的课程表"""
        return self.tomorrow_class_plan
        
    def get_is_after_school(self):
        """获取是否放学状态"""
        return self.is_after_school
        
    def set_is_after_school(self, value: bool):
        """设置是否放学状态"""
        if self.is_after_school != value:
            self.is_after_school = value
            self.update_content()
            
    def set_show_current_lesson_only_on_class(self, value: bool):
        """设置是否仅在上课时显示当前课程"""
        if self.show_current_lesson_only_on_class != value:
            self.show_current_lesson_only_on_class = value
            self.update_content()
            
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
        
    def sync_with_lessons_service(self):
        """与课程服务同步状态"""
        if not self.lessons_service:
            return
            
        # 同步状态变量
        self.is_after_school = (self.lessons_service.current_state == TimeState.AFTER_SCHOOL or
                               self.lessons_service.current_class_plan is None)
        self.current_state = self.lessons_service.current_state
        self.current_subject = self.lessons_service.current_subject
        self.current_time_layout_item = self.lessons_service.current_time_layout_item
        self.show_current_lesson_only_on_class = getattr(self.lessons_service, 'show_current_lesson_only_on_class', False)
        
        # 更新UI
        self.update_content()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建课程表组件
    schedule_component = ScheduleComponent()
    schedule_component.show()
    
    sys.exit(app.exec())
