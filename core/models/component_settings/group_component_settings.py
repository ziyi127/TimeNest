from PySide6.QtCore import QObject, Signal
from typing import List


class GroupComponentSettings(QObject):
    """分组组件设置类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._children = []  # 子组件列表
        
    @property
    def children(self):
        """子组件列表"""
        return self._children
    
    @children.setter
    def children(self, value):
        if value != self._children:
            self._children = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = GroupComponentSettings()
    
    # 测试属性
    print(f"Children: {settings.children}")
    
    # 测试设置变更
    settings.children = ["时钟", "日期", "天气"]
    print(f"After setting children=['时钟', '日期', '天气']: {settings.children}")
