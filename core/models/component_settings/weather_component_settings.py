from PySide6.QtCore import QObject, Signal


class WeatherComponentSettings(QObject):
    """天气组件设置类"""
    
    # 设置变更信号
    changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._show_alerts = True
        self._alerts_title_show_mode = 1
        self._show_rain_time = True
        self._show_main_weather_info = True
        self._main_weather_info_kind = 0
        
    @property
    def show_alerts(self):
        """是否显示警报"""
        return self._show_alerts
    
    @show_alerts.setter
    def show_alerts(self, value):
        if value != self._show_alerts:
            self._show_alerts = value
            self.changed.emit()
    
    @property
    def alerts_title_show_mode(self):
        """警报标题显示模式"""
        return self._alerts_title_show_mode
    
    @alerts_title_show_mode.setter
    def alerts_title_show_mode(self, value):
        if value != self._alerts_title_show_mode:
            self._alerts_title_show_mode = value
            self.changed.emit()
    
    @property
    def show_rain_time(self):
        """是否显示降雨时间"""
        return self._show_rain_time
    
    @show_rain_time.setter
    def show_rain_time(self, value):
        if value != self._show_rain_time:
            self._show_rain_time = value
            self.changed.emit()
    
    @property
    def show_main_weather_info(self):
        """是否显示主要天气信息"""
        return self._show_main_weather_info
    
    @show_main_weather_info.setter
    def show_main_weather_info(self, value):
        if value != self._show_main_weather_info:
            self._show_main_weather_info = value
            self.changed.emit()
    
    @property
    def main_weather_info_kind(self):
        """主要天气信息类型"""
        return self._main_weather_info_kind
    
    @main_weather_info_kind.setter
    def main_weather_info_kind(self, value):
        if value != self._main_weather_info_kind:
            self._main_weather_info_kind = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = WeatherComponentSettings()
    
    # 测试属性
    print(f"Show alerts: {settings.show_alerts}")
    print(f"Alerts title show mode: {settings.alerts_title_show_mode}")
    print(f"Show rain time: {settings.show_rain_time}")
    print(f"Show main weather info: {settings.show_main_weather_info}")
    print(f"Main weather info kind: {settings.main_weather_info_kind}")
    
    # 测试设置变更
    settings.show_alerts = False
    print(f"After setting show_alerts=False: {settings.show_alerts}")
    
    settings.alerts_title_show_mode = 2
    print(f"After setting alerts_title_show_mode=2: {settings.alerts_title_show_mode}")
