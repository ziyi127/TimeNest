from PySide6.QtCore import QObject, Signal


class ClockComponentSettings(QObject):
    """时钟组件设置类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._show_seconds = False
        self._show_real_time = False
        self._flash_time_separator = True
        
    @property
    def show_seconds(self):
        """是否显示秒数"""
        return self._show_seconds
    
    @show_seconds.setter
    def show_seconds(self, value):
        if value != self._show_seconds:
            self._show_seconds = value
            self.changed.emit()
    
    @property
    def show_real_time(self):
        """是否显示实时时间"""
        return self._show_real_time
    
    @show_real_time.setter
    def show_real_time(self, value):
        if value != self._show_real_time:
            self._show_real_time = value
            self.changed.emit()
    
    @property
    def flash_time_separator(self):
        """是否闪烁时间分隔符"""
        return self._flash_time_separator
    
    @flash_time_separator.setter
    def flash_time_separator(self, value):
        if value != self._flash_time_separator:
            self._flash_time_separator = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = ClockComponentSettings()
    
    # 测试属性
    print(f"Show seconds: {settings.show_seconds}")
    print(f"Show real time: {settings.show_real_time}")
    print(f"Flash time separator: {settings.flash_time_separator}")
    
    # 测试设置变更
    settings.show_seconds = True
    print(f"After setting show_seconds=True: {settings.show_seconds}")
    
    settings.show_real_time = True
    print(f"After setting show_real_time=True: {settings.show_real_time}")
    
    settings.flash_time_separator = False
    print(f"After setting flash_time_separator=False: {settings.flash_time_separator}")
