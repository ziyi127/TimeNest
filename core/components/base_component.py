from PySide6.QtCore import QObject, Signal


class ComponentSettings(QObject):
    """组件设置基类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()


class BaseComponent(QObject):
    """组件基类"""
    
    def __init__(self, settings: ComponentSettings = None):
        super().__init__()
        self.settings = settings or ComponentSettings()
        if hasattr(self.settings, 'changed'):
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
        if hasattr(self.settings, 'changed'):
            self.settings.changed.connect(self.on_settings_changed)


class TimeNestClockComponent(BaseComponent):
    """TimeNest时钟组件"""
    
    def __init__(self):
        super().__init__()
        self.name = "时钟"
        self.component_id = "9E1AF71D-8F77-4B21-A342-448787104DD9"
        self.description = "显示现在的时间，支持精确到秒。"
    
    def get_component_info(self):
        """获取组件信息"""
        return {
            "name": self.name,
            "id": self.component_id,
            "description": self.description
        }


class TimeNestDateComponent(BaseComponent):
    """TimeNest日期组件"""
    
    def __init__(self):
        super().__init__()
        self.name = "日期"
        self.component_id = "DF3F8295-21F6-482E-BADA-FA0E5F14BB66"
        self.description = "显示今天的日期和星期。"
    
    def get_component_info(self):
        """获取组件信息"""
        return {
            "name": self.name,
            "id": self.component_id,
            "description": self.description
        }


class TimeNestScheduleComponent(BaseComponent):
    """TimeNest课程表组件"""
    
    def __init__(self):
        super().__init__()
        self.name = "课程表"
        self.component_id = "1DB2017D-E374-4BC6-9D57-0B4ADF03A6B8"
        self.description = "显示当前的课程表信息。"
    
    def get_component_info(self):
        """获取组件信息"""
        return {
            "name": self.name,
            "id": self.component_id,
            "description": self.description
        }
