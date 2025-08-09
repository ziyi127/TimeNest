import logging
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QScreen

from core.models.component_settings.lesson_control_settings import LessonControlSettings


class FloatingWindow(QMainWindow):
    """浮动窗口组件 - 提供可移动的浮动窗口功能，基于ClassIsland的FloatingWindow实现"""
    
    def __init__(self, settings: LessonControlSettings = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or LessonControlSettings()
        
        # 窗口状态变量
        self.is_dragging = False
        self.drag_position = QPoint()
        self.is_pinned = False
        
        # 初始化窗口
        self.init_window()
        
        # 初始化UI
        self.init_ui()
        
    def init_window(self):
        """初始化窗口属性"""
        # 设置窗口标志
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)  # 稍微透明以提高视觉效果
        
        # 设置初始大小
        self.resize(300, 200)
        
        # 设置窗口位置到屏幕中心
        self.center_window()
        
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加一些占位内容
        from PySide6.QtWidgets import QLabel
        label = QLabel("浮动窗口内容")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
    def center_window(self):
        """将窗口居中显示"""
        screen = QScreen.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(screen_geometry.center())
            self.move(window_geometry.topLeft())
            
    def mousePressEvent(self, event):
        """鼠标按下事件 - 实现拖拽功能"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 实现拖拽功能"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
            
    def toggle_pin(self):
        """切换固定/取消固定状态"""
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
    def set_pinned(self, pinned: bool):
        """设置固定状态"""
        self.is_pinned = pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
    def get_is_pinned(self):
        """获取固定状态"""
        return self.is_pinned
        
    def set_transparency(self, opacity: float):
        """设置窗口透明度"""
        self.setWindowOpacity(max(0.1, min(1.0, opacity)))
        
    def set_position(self, x: int, y: int):
        """设置窗口位置"""
        self.move(x, y)
        
    def get_position(self):
        """获取窗口位置"""
        return self.pos()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建浮动窗口
    floating_window = FloatingWindow()
    floating_window.show()
    
    sys.exit(app.exec())
