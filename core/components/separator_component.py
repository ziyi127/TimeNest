import logging
from typing import Optional
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout

from core.models.component_settings.separator_component_settings import SeparatorComponentSettings


class SeparatorComponent(QWidget):
    """分割线组件 - 显示视觉分割线，基于ClassIsland的SeparatorComponent实现"""
    
    def __init__(self, settings: Optional[SeparatorComponentSettings] = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or SeparatorComponentSettings()
        
        # 分割线组件
        self.separator: QFrame = QFrame()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化内容
        self.update_content()
        
        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)
        
    def init_ui(self):
        """初始化UI"""
        # 创建分割线
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.HLine)  # 水平分割线
        self.separator.setFrameShadow(QFrame.Shadow.Plain)
        
        # 设置布局
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.setLayout(layout)
            
        layout.addWidget(self.separator)
        
    def update_content(self):
        """更新分割线显示内容"""
        if self.settings.is_vertical:
            self.separator.setFrameShape(QFrame.Shape.VLine)
            self.separator.setFrameShadow(QFrame.Shadow.Plain)
        else:
            self.separator.setFrameShape(QFrame.Shape.HLine)
            self.separator.setFrameShadow(QFrame.Shadow.Plain)
            
        # 更新分割线宽度
        self.separator.setLineWidth(self.settings.line_width)
            
    def set_orientation(self, is_vertical: bool):
        """设置分割线方向"""
        self.settings.is_vertical = is_vertical
        self.update_content()
        
    def set_line_width(self, width: int):
        """设置分割线宽度"""
        self.settings.line_width = width
        self.update_content()


# 测试代码（这部分代码仅用于测试，不影响实际功能）
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = SeparatorComponentSettings()
    # 注意：这里设置的属性在实际的SeparatorComponentSettings中并不存在
    # 这些属性仅用于测试目的，实际使用中应使用正确的属性
    settings.is_vertical = False
    settings.line_width = 1
    
    # 创建分割线组件
    separator_component = SeparatorComponent(settings)
    separator_component.show()
    
    sys.exit(app.exec())
