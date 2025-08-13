import logging
from datetime import datetime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from core.models.component_settings.weather_component_settings import WeatherComponentSettings


class WeatherComponent(QWidget):
    """天气组件 - 显示天气信息，基于ClassIsland的WeatherComponent实现"""
    
    def __init__(self, settings: WeatherComponentSettings = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 设置组件
        self.settings = settings or WeatherComponentSettings()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化内容
        self.update_content()
        
        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)
        
        # 定时器更新天气（每30分钟更新一次）
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(30 * 60 * 1000)  # 30分钟
        
    def init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # 天气图标显示
        self.weather_icon = QLabel()
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.setObjectName("weatherIcon")
        self.weather_icon.setMinimumSize(64, 64)
        
        # 天气温度显示
        self.temperature_label = QLabel()
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setObjectName("temperatureLabel")
        
        # 天气描述显示
        self.weather_description = QLabel()
        self.weather_description.setAlignment(Qt.AlignCenter)
        self.weather_description.setObjectName("weatherDescription")
        
        # 添加到布局
        layout.addWidget(self.weather_icon)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.weather_description)
        
        self.setLayout(layout)
        
    def update_content(self):
        """更新天气显示内容"""
        # 更新天气信息显示
        self.update_weather_display()
        
    def update_weather(self):
        """更新天气信息"""
        # 这里应该从天气API获取最新的天气数据
        # 简化实现，使用模拟数据
        self.update_weather_display()
        
    def update_weather_display(self):
        """更新天气显示"""
        # 模拟天气数据
        temperature = "22°C"
        description = "晴朗"
        icon_path = ":/icons/weather/sunny.png"  # 实际应用中应该使用真实的天气图标
        
        # 更新显示
        self.temperature_label.setText(temperature)
        self.weather_description.setText(description)
        
        # 更新图标（如果需要）
        if icon_path:
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    self.weather_icon.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.weather_icon.setText("☀️")
            except Exception:
                self.weather_icon.setText("☀️")
        else:
            self.weather_icon.setText("☀️")
    
    def get_current_temperature(self):
        """获取当前温度"""
        return self.temperature_label.text()
        
    def get_current_weather_description(self):
        """获取当前天气描述"""
        return self.weather_description.text()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建设置对象
    settings = WeatherComponentSettings()
    settings.show_temperature = True
    settings.show_description = True
    
    # 创建天气组件
    weather_component = WeatherComponent(settings)
    weather_component.show()
    
    sys.exit(app.exec())
