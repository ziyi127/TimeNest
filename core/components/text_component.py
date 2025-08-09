"""
文本组件
用于显示自定义文本内容
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .base_component import BaseComponent, ComponentSettings


class TextComponentSettings(ComponentSettings):
    """文本组件设置"""
    
    def __init__(self):
        super().__init__()
        self.text = "自定义文本"  # 显示的文本内容
        self.font_size = 14      # 字体大小
        self.font_family = "Microsoft YaHei"  # 字体族
        self.font_weight = QFont.Weight.Normal  # 字体粗细
        self.italic = False      # 是否斜体
        self.color = "#FFFFFF"   # 文本颜色
        self.background_color = "transparent"  # 背景颜色
        self.alignment = Qt.AlignmentFlag.AlignCenter  # 文本对齐方式


class TextComponent(BaseComponent):
    """文本组件"""
    
    def __init__(self, settings=None):
        super().__init__(settings or TextComponentSettings())
        self.label = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.label = QLabel()
        self.label.setAlignment(self.settings.alignment)
        
        # 设置样式
        self.update_style()
        
        # 设置文本
        self.label.setText(self.settings.text)
        
        # 设置组件
        self.setLayout(self.create_layout(self.label))
        
    def update_style(self):
        """更新样式"""
        if self.label:
            # 构建样式表
            style_sheet = f"""
                QLabel {{
                    color: {self.settings.color};
                    background-color: {self.settings.background_color};
                    font-family: "{self.settings.font_family}";
                    font-size: {self.settings.font_size}px;
                    font-weight: {self.settings.font_weight};
                    font-style: {"italic" if self.settings.italic else "normal"};
                }}
            """
            self.label.setStyleSheet(style_sheet)
            
    def update_settings(self, settings):
        """更新设置"""
        super().update_settings(settings)
        
        if self.label:
            # 更新文本
            if hasattr(settings, 'text'):
                self.label.setText(settings.text)
                
            # 更新样式
            self.update_style()
            
    def get_widget(self):
        """获取组件的QWidget"""
        return self