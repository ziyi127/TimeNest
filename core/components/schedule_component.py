import logging
from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont

from core.services.time_service import TimeService
from core.models.component_settings.lesson_control_settings import LessonControlSettings


class ScheduleComponent(QWidget):
    """课程表组件 - 显示当前和明天的课程安排，基于ClassIsland的ScheduleComponent实现"""
    
    def __init__(self, lessons_service=None, exact_time_service: TimeService = None, 
                 profile_service=None, settings_service=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 服务依赖
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.profile_service = profile_service
        self.settings_service = settings_service
        
        # 组件设置
        self.settings = LessonControlSettings()
        
        # 状态变量
        self.tomorrow_class_plan = None
        self.is_after_school = False
        self.show_current_lesson_only_on_class = False
        self.lessons_listbox_selected_index = -1
        
        # 初始化UI
        self.init_ui()
        
        # 连接事件
        if self.lessons_service:
            self.lessons_service.post_main_timer_ticked.connect(self.update_content)
        else:
            # 如果没有课程服务，使用自己的定时器
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_content)
            self.timer.start(60000)  # 1分钟检查一次
        
        # 初始化内容
        self.update_content()
        
    def init_ui(self):
        """初始化UI - 严格按照ClassIsland的XAML结构实现"""
        # 设置布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # 明天标签
        self.tomorrow_label = QLabel("明天")
        self.tomorrow_label.setObjectName("Tomorrow")
        self.tomorrow_label.setStyleSheet("""
            QLabel#Tomorrow {
                background-color: #0078D4;  /* AccentFillColorDefaultBrush */
                color: white;               /* TextOnAccentFillColorPrimaryBrush */
                border-radius: 16px;
                padding: 2px 8px;
                margin: 0 2px 0 0;
                font-size: 10px;
                font-family: "Microsoft YaHei";
            }
        """)
        self.tomorrow_label.setVisible(False)  # 默认隐藏
        main_layout.addWidget(self.tomorrow_label)
        
        # 主课程列表显示区域
        self.main_lessons_listbox = QWidget()
        self.main_lessons_listbox.setObjectName("MainLessonsListBox")
        self.main_lessons_listbox_layout = QHBoxLayout(self.main_lessons_listbox)
        self.main_lessons_listbox_layout.setContentsMargins(0, 0, 0, 0)
        self.main_lessons_listbox_layout.setSpacing(5)
        main_layout.addWidget(self.main_lessons_listbox)
        
        # 空课程表占位符
        self.empty_placeholder = QLabel()
        self.empty_placeholder.setObjectName("EmptyPlaceholder")
        self.empty_placeholder.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.empty_placeholder.setVisible(False)
        self.empty_placeholder.setStyleSheet("""
            QLabel#EmptyPlaceholder {
                color: #CCCCCC;
                font-size: 12px;
                font-family: "Microsoft YaHei";
                background: transparent;
            }
        """)
        main_layout.addWidget(self.empty_placeholder)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 移除样式表设置，避免与主窗口冲突
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def update_content(self):
        """更新课程表内容"""
        # 获取当前日期
        if self.exact_time_service:
            current_date = self.exact_time_service.get_current_local_datetime().date()
        else:
            current_date = datetime.now().date()
            
        # 获取今天的课程表（简化实现）
        today_class_plan = self.get_sample_class_plan()
        self.tomorrow_class_plan = self.get_sample_tomorrow_class_plan()
        
        # 更新明天标签显示
        self.update_tomorrow_label()
        
        # 更新课程列表
        self.update_lessons_list(today_class_plan)
        
        # 更新占位符
        self.update_empty_placeholder(today_class_plan)
        
    def get_sample_class_plan(self):
        """获取示例课程表数据"""
        # 简化实现 - 实际应用中应该从profile_service获取真实数据
        return {
            "lessons": [
                {"name": "数学", "start_time": datetime.strptime("08:00", "%H:%M"), "end_time": datetime.strptime("08:45", "%H:%M")},
                {"name": "英语", "start_time": datetime.strptime("08:55", "%H:%M"), "end_time": datetime.strptime("09:40", "%H:%M")},
                {"name": "语文", "start_time": datetime.strptime("09:50", "%H:%M"), "end_time": datetime.strptime("10:35", "%H:%M")},
                {"name": "物理", "start_time": datetime.strptime("10:45", "%H:%M"), "end_time": datetime.strptime("11:30", "%H:%M")}
            ]
        }
        
    def get_sample_tomorrow_class_plan(self):
        """获取示例明天课程表数据"""
        # 简化实现
        return {
            "lessons": [
                {"name": "化学", "start_time": datetime.strptime("08:00", "%H:%M"), "end_time": datetime.strptime("08:45", "%H:%M")},
                {"name": "生物", "start_time": datetime.strptime("08:55", "%H:%M"), "end_time": datetime.strptime("09:40", "%H:%M")}
            ]
        }
        
    def update_tomorrow_label(self):
        """更新明天标签显示状态"""
        show_tomorrow = False
        
        # 根据设置决定是否显示明天课表
        if self.settings.tomorrow_schedule_show_mode == 2:  # 总是显示
            show_tomorrow = True
        elif self.settings.tomorrow_schedule_show_mode == 1:  # 放学后显示
            show_tomorrow = self.is_after_school
            
        # 如果有明天的课程表且需要显示，则显示标签
        if show_tomorrow and self.tomorrow_class_plan:
            self.tomorrow_label.setVisible(True)
        else:
            self.tomorrow_label.setVisible(False)
            
    def update_lessons_list(self, class_plan_data):
        """更新课程列表显示"""
        # 清除现有课程项
        for i in reversed(range(self.main_lessons_listbox_layout.count())):
            widget = self.main_lessons_listbox_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()
                
        if not class_plan_data or not class_plan_data.get("lessons"):
            return
            
        # 添加课程项
        for i, lesson in enumerate(class_plan_data["lessons"]):
            lesson_widget = self.create_lesson_widget(lesson, i)
            self.main_lessons_listbox_layout.addWidget(lesson_widget)
            
    def create_lesson_widget(self, lesson, index: int) -> QWidget:
        """创建课程项控件"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        widget.setAttribute(Qt.WA_TranslucentBackground)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 课程名称
        name_label = QLabel(lesson.get("name", "未知课程"))
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Microsoft YaHei";
                font-size: 12px;
                background: transparent;
            }
        """)
        layout.addWidget(name_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 课程时间
        start_time = lesson.get("start_time", datetime.min)
        end_time = lesson.get("end_time", datetime.min)
        time_text = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-family: "Microsoft YaHei";
                font-size: 10px;
                background: transparent;
            }
        """)
        layout.addWidget(time_label)
        
        return widget
        
    def update_empty_placeholder(self, class_plan_data):
        """更新空课程表占位符"""
        if not class_plan_data or not class_plan_data.get("lessons"):
            if self.settings.show_placeholder_on_empty_class_plan:
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


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = LessonControlSettings()
    
    # 创建课程表组件
    schedule_component = ScheduleComponent(settings)
    schedule_component.show()
    
    sys.exit(app.exec())
