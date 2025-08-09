from PySide6.QtCore import QObject, Signal
from typing import List


class SlideComponentSettings(QObject):
    """幻灯片组件设置类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._children = []  # 子组件列表
        self._auto_slide_enabled = True  # 是否自动轮播
        self._slide_interval_seconds = 5  # 轮播间隔（秒）
        self._is_pause_on_rule_enabled = False  # 是否根据规则暂停
        self._pause_rule = {}  # 暂停规则
        
    @property
    def children(self):
        """子组件列表"""
        return self._children
    
    @children.setter
    def children(self, value):
        if value != self._children:
            self._children = value
            self.changed.emit()
    
    @property
    def auto_slide_enabled(self):
        """是否自动轮播"""
        return self._auto_slide_enabled
    
    @auto_slide_enabled.setter
    def auto_slide_enabled(self, value):
        if value != self._auto_slide_enabled:
            self._auto_slide_enabled = value
            self.changed.emit()
    
    @property
    def slide_interval_seconds(self):
        """轮播间隔（秒）"""
        return self._slide_interval_seconds
    
    @slide_interval_seconds.setter
    def slide_interval_seconds(self, value):
        if value != self._slide_interval_seconds:
            self._slide_interval_seconds = max(1, value)  # 确保至少1秒
            self.changed.emit()
    
    @property
    def is_pause_on_rule_enabled(self):
        """是否根据规则暂停"""
        return self._is_pause_on_rule_enabled
    
    @is_pause_on_rule_enabled.setter
    def is_pause_on_rule_enabled(self, value):
        if value != self._is_pause_on_rule_enabled:
            self._is_pause_on_rule_enabled = value
            self.changed.emit()
    
    @property
    def pause_rule(self):
        """暂停规则"""
        return self._pause_rule
    
    @pause_rule.setter
    def pause_rule(self, value):
        if value != self._pause_rule:
            self._pause_rule = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = SlideComponentSettings()
    
    # 测试属性
    print(f"Auto slide enabled: {settings.auto_slide_enabled}")
    print(f"Slide interval seconds: {settings.slide_interval_seconds}")
    print(f"Is pause on rule enabled: {settings.is_pause_on_rule_enabled}")
    print(f"Pause rule: {settings.pause_rule}")
    
    # 测试设置变更
    settings.auto_slide_enabled = False
    print(f"After setting auto_slide_enabled=False: {settings.auto_slide_enabled}")
    
    settings.slide_interval_seconds = 10
    print(f"After setting slide_interval_seconds=10: {settings.slide_interval_seconds}")
    
    settings.is_pause_on_rule_enabled = True
    print(f"After setting is_pause_on_rule_enabled=True: {settings.is_pause_on_rule_enabled}")
    
    settings.pause_rule = {"condition": "focus", "value": True}
    print(f"After setting pause_rule: {settings.pause_rule}")