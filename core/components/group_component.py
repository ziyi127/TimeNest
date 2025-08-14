import logging
from typing import List, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame

from core.models.component_settings.group_component_settings import GroupComponentSettings


class GroupComponent(QWidget):
    """分组组件 - 用于组织和分组其他组件，基于ClassIsland的GroupComponent实现"""
    
    def __init__(self, settings: Optional[GroupComponentSettings] = None) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or GroupComponentSettings()
        
        # 组件列表
        self.components: List[QWidget] = []
        
        # 初始化UI
        self.init_ui()
        
        # 初始化内容
        self.update_content()
        
        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)
        
    def init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建分组框架
        self.group_frame = QFrame()
        self.group_frame.setObjectName("groupFrame")
        self.group_frame.setFrameShape(QFrame.Shape.Box)
        self.group_frame.setFrameShadow(QFrame.Shadow.Raised)
        
        # 分组内部布局
        self.group_layout = QVBoxLayout(self.group_frame)
        self.group_layout.setContentsMargins(10, 10, 10, 10)
        self.group_layout.setSpacing(5)
        
        # 将框架添加到主布局
        layout.addWidget(self.group_frame)
        self.setLayout(layout)
        
    def update_content(self):
        """更新分组显示内容"""
        # 根据设置更新分组样式
        if self.settings.show_border:
            self.group_frame.setFrameShape(QFrame.Shape.Box)
            self.group_frame.setFrameShadow(QFrame.Shadow.Raised)
        else:
            self.group_frame.setFrameShape(QFrame.Shape.NoFrame)
            
        # 更新边框颜色和样式
        if self.settings.border_color:
            self.group_frame.setStyleSheet(f"QFrame#groupFrame {{ border: 1px solid {self.settings.border_color}; }}")
        else:
            self.group_frame.setStyleSheet("")
            
        # 更新标题显示
        if self.settings.show_title and self.settings.title:
            # 这里可以添加标题显示逻辑
            pass
            
    def add_component(self, component: QWidget) -> None:
        """添加组件到分组"""
        if component not in self.components:
            self.components.append(component)
            self.group_layout.addWidget(component)
            self.logger.debug(f"组件已添加到分组: {component}")
            
    def remove_component(self, component: QWidget) -> None:
        """从分组中移除组件"""
        if component in self.components:
            self.components.remove(component)
            self.group_layout.removeWidget(component)
            component.setParent(None)
            self.logger.debug(f"组件已从分组移除: {component}")
            
    def clear_components(self):
        """清空所有组件"""
        for component in self.components.copy():
            self.remove_component(component)
            
    def get_components(self) -> List[QWidget]:
        """获取所有组件"""
        return self.components.copy()
        
    def set_title(self, title: str):
        """设置分组标题"""
        self.settings.title = title
        self.update_content()
        
    def set_border_color(self, color: str):
        """设置边框颜色"""
        self.settings.border_color = color
        self.update_content()
        
    def set_show_border(self, show: bool):
        """设置是否显示边框"""
        self.settings.show_border = show
        self.update_content()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = GroupComponentSettings()
    settings.show_border = True
    settings.border_color = "#007bff"
    settings.title = "测试分组"
    
    # 创建分组组件
    group_component = GroupComponent(settings)
    group_component.show()
    
    sys.exit(app.exec())
