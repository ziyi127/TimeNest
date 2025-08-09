from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal


class ComponentSettings(QObject):
    """组件设置基类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()


class BaseComponent(QWidget):
    """组件基类"""
    
    def __init__(self, settings: ComponentSettings = None):
        super().__init__()
        self.settings = settings or ComponentSettings()
        self.settings.changed.connect(self.on_settings_changed)
    
    def on_settings_changed(self):
        """当设置发生变化时的回调"""
        pass
    
    def get_settings(self):
        """获取组件设置"""
        return self.settings
    
    def set_settings(self, settings):
        """设置组件设置"""
        self.settings = settings
        self.settings.changed.connect(self.on_settings_changed)
