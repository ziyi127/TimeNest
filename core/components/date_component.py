import logging
from datetime import datetime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from core.services.time_service import TimeService
from core.models.component_settings.date_component_settings import DateComponentSettings


class DateComponent(QWidget):
    """日期组件 - 显示当前日期和星期，基于ClassIsland的DateComponent实现"""
    
    def __init__(self, lessons_service=None, exact_time_service: TimeService = None, settings_service=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_date = datetime.now()
        
        # 服务依赖
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.settings_service = settings_service
        
        # 设置组件
        self.settings = DateComponentSettings()
        
        # 动画相关
        self.fade_animation = None
        self.animations = []  # 保存动画引用防止被垃圾回收
        
        # 初始化UI
        self.init_ui()
        
        # 连接事件 - 严格按照ClassIsland逻辑
        if self.lessons_service:
            self.lessons_service.post_main_timer_ticked.connect(self.update_date)
        else:
            # 如果没有课程服务，使用自己的定时器
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_date)
            self.timer.start(60000)  # 1分钟检查一次
        
        # 初始化内容
        self.update_date()
        
    def init_ui(self):
        """初始化UI - 严格按照ClassIsland的XAML结构实现"""
        # 设置布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # 日期显示 - 使用ClassIsland的格式化方式
        self.date_display = QLabel()
        self.date_display.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.date_display.setObjectName("dateDisplay")
        
        # 设置字体样式 - 更接近ClassIsland风格
        font = QFont("Microsoft YaHei", 15)
        self.date_display.setFont(font)
        
        # 应用样式表 - 改进的样式
        self.date_display.setStyleSheet("""
            QLabel#dateDisplay {
                color: #CCCCCC;
                background: transparent;
                font-family: "Microsoft YaHei";
                font-weight: normal;
                text-shadow: 0 0 6px rgba(255, 255, 255, 0.4);
                qproperty-alignment: AlignVCenter | AlignLeft;
            }
        """)
        
        layout.addWidget(self.date_display)
        self.setLayout(layout)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(40)  # 设置固定高度
        
        # 启用鼠标穿透，允许点击穿透到下方
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
    def update_date(self):
        """更新日期显示内容 - 严格按照ClassIsland逻辑实现"""
        try:
            # 获取当前日期 - 根据设置决定使用实时时间还是精确时间
            if self.settings.show_real_time:
                self.current_date = datetime.now()
            elif self.exact_time_service:
                self.current_date = self.exact_time_service.get_current_local_datetime()
            else:
                self.current_date = datetime.now()
                
            # 格式化日期显示 - 严格按照ClassIsland的格式: "ddd MM/dd"
            # 注意：ClassIsland使用的是英文星期缩写，需要对应转换
            weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
            weekday = weekday_names[self.current_date.weekday()]
            formatted_date = f"{weekday} {self.current_date.strftime('%m/%d')}"
            
            # 更新显示
            self.date_display.setText(formatted_date)
            
            # 添加淡入效果
            self.animate_fade_in()
            
        except Exception as e:
            self.logger.error(f"更新日期组件内容时出错: {e}")
            # 出错时显示错误信息
            self.date_display.setText("日期错误")
        
    def animate_fade_in(self):
        """淡入动画效果"""
        # 停止正在运行的动画
        if self.fade_animation and self.fade_animation.state() == QPropertyAnimation.Running:
            self.fade_animation.stop()
            
        self.fade_animation = QPropertyAnimation(self.date_display, b"windowOpacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0.3)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 保存动画引用防止被垃圾回收
        self.animations.append(self.fade_animation)
        self.fade_animation.finished.connect(lambda: self._remove_animation(self.fade_animation))
        
        self.fade_animation.start()
        
    def _remove_animation(self, animation):
        """从动画列表中移除已完成的动画"""
        if animation in self.animations:
            self.animations.remove(animation)
        
    def get_current_date(self):
        """获取当前日期"""
        return self.current_date


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = DateComponentSettings()
    settings.show_real_time = True
    
    # 创建日期组件
    date_component = DateComponent(settings)
    date_component.show()
    
    sys.exit(app.exec())