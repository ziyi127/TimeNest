"""
文本组件
用于显示自定义文本内容
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .base_component import BaseComponent, ComponentSettings
from typing import Optional, Union, Any


class TextComponentSettings(ComponentSettings):
    """文本组件设置"""
    
    def __init__(self):
        super().__init__()
        self.text: str = "自定义文本"  # 显示的文本内容
        self.font_size: int = 14      # 字体大小
        self.font_family: str = "Microsoft YaHei"  # 字体族
        self.font_weight: QFont.Weight = QFont.Weight.Normal  # 字体粗细
        self.italic: bool = False      # 是否斜体
        self.color: str = "#FFFFFF"   # 文本颜色
        self.background_color: str = "transparent"  # 背景颜色
        self.alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter  # 文本对齐方式


class TextComponent(BaseComponent):
    """文本组件"""
    
    def __init__(self, settings: Optional[TextComponentSettings] = None):
        super().__init__(settings or TextComponentSettings())
        self.label: Optional[QLabel] = None
        self.widget: Optional[QWidget] = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 创建一个容器widget来设置布局
        self.widget = QWidget()
        self.label = QLabel()
        
        # 类型检查：确保 settings 是 TextComponentSettings 类型
        # type: ignore 是因为 Pylance 无法正确推断 self.settings 的类型
        if isinstance(self.settings, TextComponentSettings):  # type: ignore
            self.label.setAlignment(self.settings.alignment)
        
        # 设置样式
        self.update_style()
        
        # 设置文本
        # type: ignore 是因为 Pylance 无法正确推断 self.settings 的类型
        if isinstance(self.settings, TextComponentSettings):  # type: ignore
            self.label.setText(self.settings.text)
        
        # 设置组件
        layout = self.create_layout(self.label)
        self.widget.setLayout(layout)
        
    def create_layout(self, widget: QLabel) -> QVBoxLayout:
        """创建布局"""
        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout
        
    def update_style(self):
        """更新样式"""
        if self.label:
            # 类型检查：确保 settings 是 TextComponentSettings 类型
            # type: ignore 是因为 Pylance 无法正确推断 self.settings 的类型
            if isinstance(self.settings, TextComponentSettings):  # type: ignore
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
            
    def update_settings(self, settings: Union[TextComponentSettings, ComponentSettings, Any]):
        """更新设置"""
        # 调用父类的 update_settings 方法
        # type: ignore 是因为 Pylance 无法正确识别继承的方法
        super().update_settings(settings)  # type: ignore
        
        if self.label:
            # 类型检查：确保 settings 有 text 属性
            if hasattr(settings, 'text') and isinstance(settings, TextComponentSettings):
                self.label.setText(settings.text)
                
            # 更新样式
            self.update_style()
            
    def get_widget(self):
        """获取组件的QWidget"""
        return self.widget if self.widget else self