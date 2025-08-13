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
        
        # 服务依赖
        self.lessons_service = lessons_service
        self.exact_time_service = exact_time_service
        self.settings_service = settings_service
        
        # 设置组件
        self.settings = ClockComponentSettings()
        
        # 动画相关
        self.separator_animation = None
        self.animations = []  # 保存动画引用防止被垃圾回收
        
        # 初始化UI
        self.init_ui()
        
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
        font = QFont("Microsoft YaHei", 18, QFont.Weight.Bold)
        self.main_time_display.setFont(font)
        
        # 应用样式表 - 改进的样式
        self.main_time_display.setStyleSheet("""
            QLabel#mainTimeDisplay {
                color: white;
                background: transparent;
                font-family: "Microsoft YaHei";
                font-weight: bold;
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
                qproperty-alignment: AlignVCenter | AlignLeft;
            }
        """)
        
        # 添加到布局
        layout.addWidget(self.main_time_display)
        
        self.setLayout(layout)
        # 移除样式表设置，避免与主窗口冲突
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置固定高度以确保正确显示
        self.setFixedHeight(40)  # 稍微增加高度以适应更好的显示效果
        
        # 启用鼠标穿透，允许点击穿透到下方
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    
    def update_content(self):
        """更新时间显示内容"""
        try:
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
            self.main_time_display.setText(self.current_time.strftime(time_format))
            
            # 更新分隔符显示状态 - 严格按照ClassIsland逻辑
            self.update_separator_visibility()
            
        except Exception as e:
            self.logger.error(f"更新时钟组件内容时出错: {e}")
            # 出错时显示错误信息
            self.main_time_display.setText("时间错误")
    
    def update_separator_visibility(self):
        """更新分隔符可见性 - 严格按照ClassIsland逻辑实现"""
        # ClassIsland逻辑：当不显示秒数且启用了分隔符闪烁时才控制分隔符显示
        # 当显示秒数时，分隔符应该隐藏
        if not self.settings.flash_time_separator or self.settings.show_seconds:
            self.is_time_separator_showing = True
        else:
            # 每秒切换一次显示状态 - 奇数秒显示，偶数秒隐藏
            self.is_time_separator_showing = self.current_time.second % 2 == 1
            
        # 添加动画效果到分隔符
        if self.settings.flash_time_separator and not self.settings.show_seconds:
            self.animate_separator()
    
    def animate_separator(self):
        """为时间分隔符添加动画效果"""
        # 停止正在运行的动画
        if self.separator_animation and self.separator_animation.state() == QPropertyAnimation.Running:
            self.separator_animation.stop()
            
        if not self.is_time_separator_showing:
            # 淡出效果
            self.separator_animation = QPropertyAnimation(self.main_time_display, b"windowOpacity")
            self.separator_animation.setDuration(500)
            self.separator_animation.setStartValue(1.0)
            self.separator_animation.setEndValue(0.5)
            self.separator_animation.setEasingCurve(QEasingCurve.InOutQuad)
        else:
            # 淡入效果
            self.separator_animation = QPropertyAnimation(self.main_time_display, b"windowOpacity")
            self.separator_animation.setDuration(500)
            self.separator_animation.setStartValue(0.5)
            self.separator_animation.setEndValue(1.0)
            self.separator_animation.setEasingCurve(QEasingCurve.InOutQuad)
            
        # 保存动画引用防止被垃圾回收
        self.animations.append(self.separator_animation)
        self.separator_animation.finished.connect(lambda: self._remove_animation(self.separator_animation))
        
        self.separator_animation.start()
        
    def _remove_animation(self, animation):
        """从动画列表中移除已完成的动画"""
        if animation in self.animations:
            self.animations.remove(animation)
            
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
    clock_component = ClockComponent()
    clock_component.show()
    
    sys.exit(app.exec())