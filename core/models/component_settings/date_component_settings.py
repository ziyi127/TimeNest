from PySide6.QtCore import QObject, Signal


class DateComponentSettings(QObject):
    """日期组件设置类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._show_chinese_format = True
        self._show_real_time = False
        
    @property
    def show_chinese_format(self):
        """是否显示中文格式"""
        return self._show_chinese_format
    
    @show_chinese_format.setter
    def show_chinese_format(self, value):
        if value != self._show_chinese_format:
            self._show_chinese_format = value
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


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = DateComponentSettings()
    
    # 测试属性
    print(f"Show chinese format: {settings.show_chinese_format}")
    print(f"Show real time: {settings.show_real_time}")
    
    # 测试设置变更
    settings.show_chinese_format = False
    print(f"After setting show_chinese_format=False: {settings.show_chinese_format}")
    
    settings.show_real_time = True
    print(f"After setting show_real_time=True: {settings.show_real_time}")
