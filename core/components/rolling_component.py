import logging
from datetime import datetime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

from core.models.component_settings.rolling_component_settings import RollingComponentSettings


class RollingComponent(QWidget):
    """滚动组件 - 显示滚动文本，基于ClassIsland的RollingComponent实现"""
    
    def __init__(self, settings: RollingComponentSettings = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or RollingComponentSettings()
        
        # 滚动相关变量
        self.current_index = 0
        self.scroll_texts = []
        self.is_scrolling = False
        
        # 初始化UI
        self.init_ui()
        
        # 初始化内容
        self.update_content()
        
        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)
        
        # 定时器控制滚动
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.update_scroll)
        if self.settings.scroll_interval > 0:
            self.scroll_timer.start(self.settings.scroll_interval * 1000)
        
    def init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # 滚动文本显示标签
        self.scroll_label = QLabel()
        self.scroll_label.setAlignment(Qt.AlignCenter)
        self.scroll_label.setObjectName("scrollLabel")
        self.scroll_label.setMinimumWidth(200)  # 设置最小宽度
        
        layout.addWidget(self.scroll_label)
        self.setLayout(layout)
        
    def update_content(self):
        """更新滚动显示内容"""
        # 根据设置更新滚动文本
        self.scroll_texts = self.settings.scroll_texts.copy() if self.settings.scroll_texts else []
        
        if self.scroll_texts:
            self.current_index = 0
            self.scroll_label.setText(self.scroll_texts[0])
        else:
            self.scroll_label.setText("滚动文本")
            
        # 更新定时器
        if self.settings.scroll_interval > 0 and not self.scroll_timer.isActive():
            self.scroll_timer.start(self.settings.scroll_interval * 1000)
        elif self.settings.scroll_interval <= 0 and self.scroll_timer.isActive():
            self.scroll_timer.stop()
            
    def update_scroll(self):
        """更新滚动显示"""
        if not self.scroll_texts:
            return
            
        if len(self.scroll_texts) == 1:
            self.scroll_label.setText(self.scroll_texts[0])
            return
            
        # 更新索引
        self.current_index = (self.current_index + 1) % len(self.scroll_texts)
        self.scroll_label.setText(self.scroll_texts[self.current_index])
        
    def start_scrolling(self):
        """开始滚动"""
        if not self.is_scrolling and self.settings.scroll_interval > 0:
            self.is_scrolling = True
            if not self.scroll_timer.isActive():
                self.scroll_timer.start(self.settings.scroll_interval * 1000)
                
    def stop_scrolling(self):
        """停止滚动"""
        self.is_scrolling = False
        if self.scroll_timer.isActive():
            self.scroll_timer.stop()
            
    def add_scroll_text(self, text: str):
        """添加滚动文本"""
        if text not in self.scroll_texts:
            self.scroll_texts.append(text)
            self.settings.scroll_texts = self.scroll_texts.copy()
            
    def remove_scroll_text(self, text: str):
        """移除滚动文本"""
        if text in self.scroll_texts:
            self.scroll_texts.remove(text)
            self.settings.scroll_texts = self.scroll_texts.copy()
            
    def clear_scroll_texts(self):
        """清空滚动文本"""
        self.scroll_texts.clear()
        self.settings.scroll_texts = []
        
    def get_current_text(self):
        """获取当前显示的文本"""
        return self.scroll_label.text()
        
    def get_scroll_texts(self):
        """获取所有滚动文本"""
        return self.scroll_texts.copy()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = RollingComponentSettings()
    settings.scroll_texts = ["滚动文本1", "滚动文本2", "滚动文本3"]
    settings.scroll_interval = 2
    
    # 创建滚动组件
    rolling_component = RollingComponent(settings)
    rolling_component.show()
    
    sys.exit(app.exec())
