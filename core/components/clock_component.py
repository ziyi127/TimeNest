import logging
from datetime import datetime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from core.models.component_settings.clock_component_settings import ClockComponentSettings


class ClockComponent(QWidget):
    """时钟组件 - 显示当前时间，支持精确到秒，基于ClassIsland的ClockComponent实现"""
    
    def __init__(self, lessons_service=None, exact_time_service=None, settings_service=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_time = datetime.now()
        self.is_time_separator_showing = True
        
        # 动画
        self.fade_animation = None
        
        # 服务依赖
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.settings_service = settings_service
        
        # 设置组件
        self.settings = ClockComponentSettings()
        
        # 初始化UI
        self.init_ui()
        self.init_animations()
        
        # 连接事件
        if self.lessons_service:
            # 如果有课程服务，连接到课程服务的定时器
            self.lessons_service.post_main_timer_ticked.connect(self.update_content)
        else:
            # 否则使用自己的定时器
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_content)
            self.timer.start(1000)  # 每秒更新一次，符合ClassIsland逻辑
        
        # 初始化内容
        self.update_content()
        
    def init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # 主时间显示
        self.main_time_display = QLabel()
        self.main_time_display.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.main_time_display.setObjectName("mainTimeDisplay")
        
        # 设置字体样式 - 更接近ClassIsland风格
        font = QFont("Microsoft YaHei", 16, QFont.Bold)  # 增大字体
        self.main_time_display.setFont(font)
        
        # 应用样式表
        self.main_time_display.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                font-family: "Microsoft YaHei", "Segoe UI";
                text-shadow: 0 0 6px rgba(0, 0, 0, 0.5);
            }
        """)
        
        # 添加到布局
        layout.addWidget(self.main_time_display)
        
        self.setLayout(layout)
        # 移除样式表设置，避免与主窗口冲突
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置固定高度以确保正确显示
        self.setFixedHeight(36)
    
    def init_animations(self):
        """初始化动画"""
        self.fade_animation = QPropertyAnimation(self.main_time_display, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.OutQuad)
    
    def update_content(self):
        """更新时间显示内容"""
        # 获取当前时间 - 根据设置决定使用实时时间还是精确时间
        if self.settings.show_real_time:
            self.current_time = datetime.now()
        elif self.exact_time_service:
            self.current_time = self.exact_time_service.get_current_local_datetime()
        else:
            self.current_time = datetime.now()
            
        # 根据设置决定时间格式
        if self.settings.show_seconds:
            time_format = "{:%H:%M:%S}"
        else:
            time_format = "{:%H:%M}"
            
        # 更新主时间显示
        old_text = self.main_time_display.text()
        new_text = self.current_time.strftime(time_format)
        
        # 如果文本发生变化，添加淡入淡出动画
        if old_text != new_text:
            # 简单的文本变化动画
            self.fade_animation.setStartValue(0.7)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.start()
            
        self.main_time_display.setText(new_text)
        
        # 更新分隔符显示状态 - 严格按照ClassIsland逻辑
        self.update_separator_visibility()
    
    def update_separator_visibility(self):
        """更新分隔符可见性 - 严格按照ClassIsland逻辑实现"""
        # ClassIsland逻辑：当不显示秒数且启用了分隔符闪烁时才控制分隔符显示
        # 当显示秒数时，分隔符应该隐藏
        if not self.settings.flash_time_separator or self.settings.show_seconds:
            self.is_time_separator_showing = True
        else:
            # 每秒切换一次显示状态 - 奇数秒显示，偶数秒隐藏
            self.is_time_separator_showing = self.current_time.second % 2 == 1
            
        # 根据显示状态设置可见性
        # 注意：这里应该实际控制分隔符的显示，而不是主时间显示
        # 由于我们没有单独的分隔符控件，这个方法目前只保持主时间显示始终可见
        self.main_time_display.setVisible(True)
    
    def get_current_time(self):
        """获取当前时间"""
        return self.current_time
    
    def get_is_time_separator_showing(self):
        """获取分隔符显示状态"""
        return self.is_time_separator_showing


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = ClockComponentSettings()
    settings.show_seconds = True
    settings.flash_time_separator = True
    
    # 创建时钟组件
    clock_component = ClockComponent(settings)
    clock_component.show()
    
    sys.exit(app.exec())