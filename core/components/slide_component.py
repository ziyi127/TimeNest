import logging
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer

from core.models.component_settings.slide_component_settings import SlideComponentSettings


class SlideComponent(QWidget):
    """幻灯片组件 - 轮播显示多个组件，基于ClassIsland的SlideComponent实现"""
    
    def __init__(self, settings: SlideComponentSettings = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or SlideComponentSettings()
        
        # 幻灯片相关变量
        self.components = []
        self.current_slide_index = 0
        self.is_sliding = False
        
        # 初始化UI
        self.init_ui()
        
        # 初始化内容
        self.update_content()
        
        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)
        
        # 定时器控制幻灯片切换
        self.slide_timer = QTimer(self)
        self.slide_timer.timeout.connect(self.next_slide)
        if self.settings.slide_interval > 0:
            self.slide_timer.start(self.settings.slide_interval * 1000)
        
    def init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建堆叠窗口用于幻灯片效果
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
    def update_content(self):
        """更新幻灯片显示内容"""
        # 根据设置更新幻灯片配置
        self.update_slides()
        
        # 更新定时器
        if self.settings.slide_interval > 0 and not self.slide_timer.isActive():
            self.slide_timer.start(self.settings.slide_interval * 1000)
        elif self.settings.slide_interval <= 0 and self.slide_timer.isActive():
            self.slide_timer.stop()
            
    def update_slides(self):
        """更新幻灯片内容"""
        # 清空现有组件
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.setParent(None)
            
        # 添加新组件
        self.components = self.settings.slide_components.copy() if self.settings.slide_components else []
        for component in self.components:
            self.stacked_widget.addWidget(component)
            
        # 设置当前显示的幻灯片
        if self.components:
            self.stacked_widget.setCurrentIndex(0)
            self.current_slide_index = 0
        else:
            self.current_slide_index = 0
            
    def next_slide(self):
        """切换到下一个幻灯片"""
        if not self.components:
            return
            
        self.current_slide_index = (self.current_slide_index + 1) % len(self.components)
        self.stacked_widget.setCurrentIndex(self.current_slide_index)
        
    def previous_slide(self):
        """切换到上一个幻灯片"""
        if not self.components:
            return
            
        self.current_slide_index = (self.current_slide_index - 1) % len(self.components)
        self.stacked_widget.setCurrentIndex(self.current_slide_index)
        
    def goto_slide(self, index: int):
        """跳转到指定幻灯片"""
        if 0 <= index < len(self.components):
            self.current_slide_index = index
            self.stacked_widget.setCurrentIndex(index)
            
    def start_sliding(self):
        """开始幻灯片播放"""
        if not self.is_sliding and self.settings.slide_interval > 0:
            self.is_sliding = True
            if not self.slide_timer.isActive():
                self.slide_timer.start(self.settings.slide_interval * 1000)
                
    def stop_sliding(self):
        """停止幻灯片播放"""
        self.is_sliding = False
        if self.slide_timer.isActive():
            self.slide_timer.stop()
            
    def add_component(self, component):
        """添加组件到幻灯片"""
        if component not in self.components:
            self.components.append(component)
            self.settings.slide_components = self.components.copy()
            self.stacked_widget.addWidget(component)
            
    def remove_component(self, component):
        """从幻灯片中移除组件"""
        if component in self.components:
            self.components.remove(component)
            self.settings.slide_components = self.components.copy()
            # 重新构建堆叠窗口
            self.update_slides()
            
    def get_components(self):
        """获取所有幻灯片组件"""
        return self.components.copy()
        
    def get_current_slide_index(self):
        """获取当前幻灯片索引"""
        return self.current_slide_index
        
    def get_current_component(self):
        """获取当前显示的组件"""
        if self.components and self.current_slide_index < len(self.components):
            return self.components[self.current_slide_index]
        return None


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = SlideComponentSettings()
    settings.slide_interval = 3
    
    # 创建幻灯片组件
    slide_component = SlideComponent(settings)
    slide_component.show()
    
    sys.exit(app.exec())
