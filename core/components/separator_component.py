import logging
from datetime import datetime
from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt

from core.models.component_settings.separator_component_settings import SeparatorComponentSettings


class SeparatorComponent(QWidget):
    """分割线组件 - 显示视觉分割线，基于ClassIsland的SeparatorComponent实现"""
    
    def __init__(self, settings: SeparatorComponentSettings = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or SeparatorComponentSettings()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化内容
        self.update_content()
        
        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)
        
    def init_ui(self):
        """初始化UI"""
        # 创建分割线
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.HLine)  # 水平分割线
        self.separator.setFrameShadow(QFrame.Plain)
        
        # 设置布局
        layout = self.layout()
        if layout is None:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.setLayout(layout)
            
        layout.addWidget(self.separator)
        
    def update_content(self):
        """更新分割线显示内容"""
        # 根据设置更新分割线样式
        if self.settings.orientation == "vertical":
            self.separator.setFrameShape(QFrame.VLine)
            self.separator.setFrameShadow(QFrame.Plain)
        else:
            self.separator.setFrameShape(QFrame.HLine)
            self.separator.setFrameShadow(QFrame.Plain)
            
        # 更新分割线样式
        if self.settings.line_style == "solid":
            self.separator.setLineWidth(1)
        elif self.settings.line_style == "dashed":
            self.separator.setLineWidth(1)
            # 注意：PySide6中需要通过样式表实现虚线效果
            self.separator.setStyleSheet("QFrame#separator { border: 1px solid gray; }")
        elif self.settings.line_style == "dotted":
            self.separator.setLineWidth(1)
            self.separator.setStyleSheet("QFrame#separator { border: 1px dotted gray; }")
        else:
            self.separator.setLineWidth(1)
            
        # 更新颜色
        if self.settings.color:
            self.separator.setStyleSheet(f"QFrame#separator {{ border: 1px solid {self.settings.color}; }}")
        else:
            self.separator.setStyleSheet("QFrame#separator { border: 1px solid gray; }")
            
        # 更新高度
        if self.settings.thickness:
            self.separator.setLineWidth(self.settings.thickness)
            
    def set_orientation(self, orientation: str):
        """设置分割线方向"""
        self.settings.orientation = orientation
        self.update_content()
        
    def set_line_style(self, style: str):
        """设置分割线样式"""
        self.settings.line_style = style
        self.update_content()
        
    def set_color(self, color: str):
        """设置分割线颜色"""
        self.settings.color = color
        self.update_content()
        
    def set_thickness(self, thickness: int):
        """设置分割线厚度"""
        self.settings.thickness = thickness
        self.update_content()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = SeparatorComponentSettings()
    settings.orientation = "horizontal"
    settings.line_style = "solid"
    settings.color = "#007bff"
    settings.thickness = 2
    
    # 创建分割线组件
    separator_component = SeparatorComponent(settings)
    separator_component.show()
    
    sys.exit(app.exec())
