from PySide6.QtCore import QObject, Signal, QStringListModel
from PySide6.QtGui import QColor
from typing import List, Optional
import json


class RollingComponentSettings(QObject):
    """滚动组件设置类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._children = []  # 子组件列表
        self._speed_pixel_per_second = 40.0
        self._is_pause_enabled = True
        self._pause_offset_x = 0.0
        self._pause_seconds = 10.0
        self._pause_on_rule = False
        self._stop_on_rule = False
        self._pause_rule = {}  # 规则设置
        self._stop_rule = {}   # 停止规则设置
        
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
    def speed_pixel_per_second(self):
        """滚动速度(像素/秒)"""
        return self._speed_pixel_per_second
    
    @speed_pixel_per_second.setter
    def speed_pixel_per_second(self, value):
        if value != self._speed_pixel_per_second:
            self._speed_pixel_per_second = value
            self.changed.emit()
    
    @property
    def is_pause_enabled(self):
        """是否启用暂停"""
        return self._is_pause_enabled
    
    @is_pause_enabled.setter
    def is_pause_enabled(self, value):
        if value != self._is_pause_enabled:
            self._is_pause_enabled = value
            self.changed.emit()
    
    @property
    def pause_offset_x(self):
        """暂停偏移量X"""
        return self._pause_offset_x
    
    @pause_offset_x.setter
    def pause_offset_x(self, value):
        if value != self._pause_offset_x:
            self._pause_offset_x = value
            self.changed.emit()
    
    @property
    def pause_seconds(self):
        """暂停秒数"""
        return self._pause_seconds
    
    @pause_seconds.setter
    def pause_seconds(self, value):
        if value != self._pause_seconds:
            self._pause_seconds = value
            self.changed.emit()
    
    @property
    def pause_on_rule(self):
        """是否根据规则暂停"""
        return self._pause_on_rule
    
    @pause_on_rule.setter
    def pause_on_rule(self, value):
        if value != self._pause_on_rule:
            self._pause_on_rule = value
            self.changed.emit()
    
    @property
    def stop_on_rule(self):
        """是否根据规则停止"""
        return self._stop_on_rule
    
    @stop_on_rule.setter
    def stop_on_rule(self, value):
        if value != self._stop_on_rule:
            self._stop_on_rule = value
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
    
    @property
    def stop_rule(self):
        """停止规则"""
        return self._stop_rule
    
    @stop_rule.setter
    def stop_rule(self, value):
        if value != self._stop_rule:
            self._stop_rule = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = RollingComponentSettings()
    
    # 测试属性
    print(f"Speed pixel per second: {settings.speed_pixel_per_second}")
    print(f"Is pause enabled: {settings.is_pause_enabled}")
    print(f"Pause seconds: {settings.pause_seconds}")
    print(f"Pause on rule: {settings.pause_on_rule}")
    print(f"Stop on rule: {settings.stop_on_rule}")
    
    # 测试设置变更
    settings.speed_pixel_per_second = 50.0
    print(f"After setting speed_pixel_per_second=50.0: {settings.speed_pixel_per_second}")
    
    settings.is_pause_enabled = False
    print(f"After setting is_pause_enabled=False: {settings.is_pause_enabled}")
