#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 组件系统
支持动态组件加载、管理和布局
"""

# 标准库
import importlib
import inspect
import json
import logging
import os
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

# 第三方库
from PySide6.QtCore import QEasingCurve, QObject, QPoint, QPropertyAnimation, QRect, QSize, Signal, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, 
    QVBoxLayout, QWidget
)


class ComponentType(Enum):
    """组件类型"""
    WIDGET = "widget"  # 普通控件
    DISPLAY = "display"  # 显示组件
    INTERACTIVE = "interactive"  # 交互组件
    NOTIFICATION = "notification"  # 通知组件
    UTILITY = "utility"  # 工具组件
    CUSTOM = "custom"  # 自定义组件


class ComponentState(Enum):
    """组件状态"""
    DISABLED = "disabled"  # 禁用
    ENABLED = "enabled"  # 启用
    LOADING = "loading"  # 加载中
    ERROR = "error"  # 错误
    UPDATING = "updating"  # 更新中


@dataclass
class ComponentInfo:
    """组件信息"""
    id: str
    name: str
    description: str
    version: str
    author: str
    component_type: ComponentType
    icon: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    min_size: tuple = (100, 100)
    max_size: tuple = (1000, 1000)
    default_size: tuple = (200, 150)
    resizable: bool = True
    configurable: bool = True
    update_interval: int = 0  # 更新间隔（秒），0表示不自动更新
    

@dataclass
class ComponentConfig:
    """组件配置"""
    component_id: str
    enabled: bool = True
    position: tuple = (0, 0)
    size: tuple = (200, 150)
    settings: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    

class IComponent(ABC):
    """组件接口"""
    
    @property
    @abstractmethod
    def info(self) -> ComponentInfo:
        """组件信息"""
        pass
    
    @property
    @abstractmethod
    def widget(self) -> QWidget:
        """组件控件"""
        pass
    
    @property
    @abstractmethod
    def state(self) -> ComponentState:
        """组件状态"""
        pass
    
    @abstractmethod
    def initialize(self, config: ComponentConfig) -> bool:
        """初始化组件"""
        pass
    
    @abstractmethod
    def update(self) -> bool:
        """更新组件"""
        pass
    
    @abstractmethod
    def configure(self, settings: Dict[str, Any]) -> bool:
        """配置组件"""
        pass
    
    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass


# 创建兼容的 metaclass
class QObjectABCMeta(type(QObject), ABCMeta):
    """兼容 QObject 和 ABC 的 metaclass"""
    pass


class BaseComponent(QObject, IComponent, metaclass=QObjectABCMeta):
    """基础组件类"""
    
    state_changed = Signal(ComponentState)
    update_requested = Signal()
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self._state = ComponentState.DISABLED
        self._widget: Optional[QWidget] = None
        self._config: Optional[ComponentConfig] = None
        self._update_timer: Optional[QTimer] = None
        
    @property
    def state(self) -> ComponentState:
        return self._state
    
    @property
    def widget(self) -> QWidget:
        if self._widget is None:
            self._widget = self.create_widget()
        return self._widget
    
    @abstractmethod
    def create_widget(self) -> QWidget:
        """创建控件"""
        pass
    
    def initialize(self, config: ComponentConfig) -> bool:
        """初始化组件"""
        try:
            self._config = config
            self.set_state(ComponentState.LOADING)
            
            # 应用配置
            if not self.configure(config.settings):
                self.set_state(ComponentState.ERROR)
                return False
            
            # 设置更新定时器
            if self.info.update_interval > 0:
                self._update_timer = QTimer()
                self._update_timer.timeout.connect(self.update)
                self._update_timer.start(self.info.update_interval * 1000)
            
            self.set_state(ComponentState.ENABLED)
            return True
            
        except Exception as e:
            self.logger.error(f"初始化组件失败: {e}", exc_info=True)
            self.set_state(ComponentState.ERROR)
            self.error_occurred.emit(str(e))
            return False
    
    def set_state(self, state: ComponentState):
        """设置状态"""
        if self._state != state:
            self._state = state
            self.state_changed.emit(state)
    
    def cleanup(self):
        """清理资源"""
        try:
            if self._update_timer:
                self._update_timer.stop()
                self._update_timer = None
            
            
            if self._widget:
                self._widget.deleteLater()
            
                self._widget.deleteLater()
                self._widget = None
                
        except Exception as e:
            self.logger.error(f"清理组件失败: {e}", exc_info=True)


class ClockComponent(BaseComponent):
    """时钟组件"""
    
    def __init__(self):
        super().__init__()
        self.format_24h = True
        self.show_seconds = True
        self.show_date = True
        
    @property
    def info(self) -> ComponentInfo:
        return ComponentInfo(
            id="clock",
            name="时钟",
            description="显示当前时间和日期",
            version="1.0.0",
            author="TimeNest",
            component_type=ComponentType.DISPLAY,
            icon="clock",
            tags=["时间", "日期"],
            update_interval=1
        )
    
    def create_widget(self) -> QWidget:
        """创建时钟控件"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(widget)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 14px; color: gray;")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        
        return widget
    
    def update(self) -> bool:
        """更新时钟"""
        try:
            now = datetime.now()
            
            # 格式化时间
            if self.format_24h:
                time_format = "%H:%M:%S" if self.show_seconds else "%H:%M"
            else:
                time_format = "%I:%M:%S %p" if self.show_seconds else "%I:%M %p"
            
            time_str = now.strftime(time_format)
            self.time_label.setText(time_str)
            
            # 格式化日期
            if self.show_date:
                date_str = now.strftime("%Y年%m月%d日 %A")
                self.date_label.setText(date_str)
                self.date_label.show()
            else:
                self.date_label.hide()
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新时钟失败: {e}", exc_info=True)
            return False
    
    def configure(self, settings: Dict[str, Any]) -> bool:
        """配置时钟"""
        try:
            self.format_24h = settings.get("format_24h", True)
            self.show_seconds = settings.get("show_seconds", True)
            self.show_date = settings.get("show_date", True)
            
            # 立即更新显示
            self.update()
            return True
            
        except Exception as e:
            self.logger.error(f"配置时钟失败: {e}", exc_info=True)
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        return {
            "format_24h": self.format_24h,
            "show_seconds": self.show_seconds,
            "show_date": self.show_date
        }


class WeatherComponent(BaseComponent):
    """天气组件"""
    
    def __init__(self, weather_service=None):
        super().__init__()
        self.weather_service = weather_service
        self.location = "北京"
        self.show_forecast = True
        
    @property
    def info(self) -> ComponentInfo:
        return ComponentInfo(
            id="weather",
            name="天气",
            description="显示当前天气和预报",
            version="1.0.0",
            author="TimeNest",
            component_type=ComponentType.DISPLAY,
            icon="weather",
            tags=["天气", "预报"],
            dependencies=["weather_service"],
            update_interval=1800  # 30分钟
        )
    
    def create_widget(self) -> QWidget:
        """创建天气控件"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(widget)
        
        # 当前天气
        current_layout = QHBoxLayout()
        
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(48, 48)
        
        info_layout = QVBoxLayout()
        self.location_label = QLabel(self.location)
        self.location_label.setStyleSheet("font-weight: bold;")
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("font-size: 18px;")
        
        self.desc_label = QLabel("--")
        self.desc_label.setStyleSheet("color: gray;")
        
        info_layout.addWidget(self.location_label)
        info_layout.addWidget(self.temp_label)
        info_layout.addWidget(self.desc_label)
        
        current_layout.addWidget(self.weather_icon)
        current_layout.addLayout(info_layout)
        
        layout.addLayout(current_layout)
        
        # 预报（可选）
        self.forecast_widget = QWidget()
        self.forecast_layout = QHBoxLayout(self.forecast_widget)
        layout.addWidget(self.forecast_widget)
        
        return widget
    
    def update(self) -> bool:
        """更新天气"""
        try:
            if not self.weather_service:
                return False
            
            # 获取当前天气
            current_weather = self.weather_service.get_current_weather()
            if current_weather:
                self.temp_label.setText(f"{current_weather.temperature:.0f}°C")
                self.desc_label.setText(current_weather.description)
                
                # 设置图标
                icon = self.weather_service.get_weather_icon(current_weather.condition, 48)
                self.weather_icon.setPixmap(icon.pixmap(48, 48))
            
            # 更新预报
            if self.show_forecast:
                self.update_forecast()
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新天气失败: {e}", exc_info=True)
            return False
    
    def update_forecast(self):
        """更新预报"""
        try:
            if not self.weather_service:
                return
            
            # 清除现有预报
            while self.forecast_layout.count():
                child = self.forecast_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # 获取预报数据
            forecast = self.weather_service.get_current_forecast()
            
            # 显示未来3天
            for i, day_forecast in enumerate(forecast[:3]):
                day_widget = QFrame()
                day_widget.setFrameStyle(QFrame.Shape.Box)
                day_layout = QVBoxLayout(day_widget)
                
                # 日期
                date_label = QLabel(day_forecast.date.strftime("%m/%d"))
                date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                date_label.setStyleSheet("font-size: 10px;")
                
                # 图标
                icon = self.weather_service.get_weather_icon(day_forecast.condition, 24)
                icon_label = QLabel()
                icon_label.setPixmap(icon.pixmap(24, 24))
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # 温度
                temp_label = QLabel(f"{day_forecast.high_temp:.0f}°/{day_forecast.low_temp:.0f}°")
                temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                temp_label.setStyleSheet("font-size: 10px;")
                
                day_layout.addWidget(date_label)
                day_layout.addWidget(icon_label)
                day_layout.addWidget(temp_label)
                
                self.forecast_layout.addWidget(day_widget)
                
        except Exception as e:
            self.logger.error(f"更新预报失败: {e}", exc_info=True)
    
    def configure(self, settings: Dict[str, Any]) -> bool:
        """配置天气"""
        try:
            self.location = settings.get("location", "北京")
            self.show_forecast = settings.get("show_forecast", True)
            
            self.location_label.setText(self.location)
            
            # 设置天气服务位置
            if self.weather_service:
                self.weather_service.set_location(self.location)
            
            # 显示/隐藏预报
            self.forecast_widget.setVisible(self.show_forecast)
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置天气失败: {e}", exc_info=True)
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        return {
            "location": self.location,
            "show_forecast": self.show_forecast
        }


class ScrollingTextComponent(BaseComponent):
    """滚动文本组件"""
    
    def __init__(self):
        super().__init__()
        self.text = "欢迎使用 TimeNest！"
        self.scroll_speed = 50  # 像素/秒
        self.text_color = "#000000"
        self.background_color = "#ffffff"
        self.font_size = 14
        self.scroll_direction = "left"  # left, right, up, down
        
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.scroll_text)
        self.scroll_position = 0
        
    @property
    def info(self) -> ComponentInfo:
        return ComponentInfo(
            id="scrolling_text",
            name="滚动文本",
            description="显示滚动的文本信息",
            version="1.0.0",
            author="TimeNest",
            component_type=ComponentType.DISPLAY,
            icon="text",
            tags=["文本", "滚动", "信息"]
        )
    
    def create_widget(self) -> QWidget:
        """创建滚动文本控件"""
        self.scroll_widget = ScrollingTextWidget()
        self.scroll_widget.set_text(self.text)
        self.scroll_widget.set_scroll_speed(self.scroll_speed)
        self.scroll_widget.set_colors(self.text_color, self.background_color)
        self.scroll_widget.set_font_size(self.font_size)
        self.scroll_widget.set_direction(self.scroll_direction)
        
        return self.scroll_widget
    
    def update(self) -> bool:
        """更新滚动文本"""
        # 滚动文本组件通常不需要定期更新内容
        return True
    
    def configure(self, settings: Dict[str, Any]) -> bool:
        """配置滚动文本"""
        try:
            self.text = settings.get("text", "欢迎使用 TimeNest！")
            self.scroll_speed = settings.get("scroll_speed", 50)
            self.text_color = settings.get("text_color", "#000000")
            self.background_color = settings.get("background_color", "#ffffff")
            self.font_size = settings.get("font_size", 14)
            self.scroll_direction = settings.get("scroll_direction", "left")
            
            # 应用设置到控件
            if hasattr(self, 'scroll_widget'):
                self.scroll_widget.set_text(self.text)
                self.scroll_widget.set_scroll_speed(self.scroll_speed)
                self.scroll_widget.set_colors(self.text_color, self.background_color)
                self.scroll_widget.set_font_size(self.font_size)
                self.scroll_widget.set_direction(self.scroll_direction)
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置滚动文本失败: {e}", exc_info=True)
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        return {
            "text": self.text,
            "scroll_speed": self.scroll_speed,
            "text_color": self.text_color,
            "background_color": self.background_color,
            "font_size": self.font_size,
            "scroll_direction": self.scroll_direction
        }


class ScrollingTextWidget(QWidget):
    """滚动文本控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
        self.scroll_speed = 50
        self.text_color = QColor("#000000")
        self.background_color = QColor("#ffffff")
        self.font_size = 14
        self.scroll_direction = "left"
        
        self.scroll_position = 0
        self.text_width = 0
        self.show_usage_tip = True
        
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_scroll)
        self.scroll_timer.start(50)  # 20 FPS
        
        # 修复显示大小错误：设置更合适的最小尺寸和大小策略
        self.setMinimumSize(200, 40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 设置工具提示
        self.setToolTip("滚动文本组件\n\n使用方法：\n• 在设置中配置显示文本\n• 可调整滚动速度和方向\n• 支持自定义字体大小和颜色")
    
    def set_text(self, text: str):
        """设置文本"""
        self.text = text
        self.calculate_text_width()
        self.scroll_position = 0
        self.update()
    
    def set_scroll_speed(self, speed: int):
        """设置滚动速度"""
        self.scroll_speed = speed
    
    def set_colors(self, text_color: str, background_color: str):
        """设置颜色"""
        self.text_color = QColor(text_color)
        self.background_color = QColor(background_color)
        self.update()
    
    def set_font_size(self, size: int):
        """设置字体大小"""
        self.font_size = size
        self.calculate_text_width()
        self.update()
    
    def set_direction(self, direction: str):
        """设置滚动方向"""
        self.scroll_direction = direction
        self.scroll_position = 0
    
    def set_usage_tip_visible(self, visible: bool):
        """设置使用提示是否可见"""
        self.show_usage_tip = visible
        self.update()
    
    def calculate_text_width(self):
        """计算文本宽度"""
        font = QFont()
        font.setPointSize(self.font_size)
        metrics = QFontMetrics(font)  # 修复：使用正确的字体度量
        self.text_width = metrics.horizontalAdvance(self.text)
        
        # 修复显示大小错误：根据文本内容调整控件高度
        text_height = metrics.height()
        preferred_height = max(40, text_height + 20)  # 添加边距
        self.setFixedHeight(preferred_height)
    
    def update_scroll(self):
        """更新滚动位置"""
        if not self.text:
            return
        
        # 计算移动距离
        move_distance = self.scroll_speed / 20  # 20 FPS
        
        
        if self.scroll_direction == "left":
            self.scroll_position -= move_distance
            if self.scroll_position < -self.text_width:
                self.scroll_position = self.width()
        elif self.scroll_direction == "right":
            self.scroll_position += move_distance
            if self.scroll_position > self.width():
                self.scroll_position = -self.text_width
        elif self.scroll_direction == "up":
            self.scroll_position -= move_distance
            if self.scroll_position < -50:  # 文本高度
                self.scroll_position = self.height()
        elif self.scroll_direction == "down":
            self.scroll_position += move_distance
            if self.scroll_position > self.height():
                self.scroll_position = -50
        
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), self.background_color)
        
        # 如果没有文本且显示使用提示，则显示提示信息
        if not self.text and self.show_usage_tip:
            painter.setPen(QColor("#888888"))
            font = QFont()
            font.setPointSize(max(10, self.font_size - 2))
            font.setItalic(True)
            painter.setFont(font)
            
            tip_text = "点击设置配置滚动文本内容"
            text_rect = painter.fontMetrics().boundingRect(tip_text)
            x = (self.width() - text_rect.width()) // 2
            y = (self.height() + text_rect.height()) // 2
            painter.drawText(x, y, tip_text)
            painter.end()
            return
        
        
        if not self.text:
            painter.end()
            return
        
        # 设置字体和颜色
        font = QFont()
        font.setPointSize(self.font_size)
        painter.setFont(font)
        painter.setPen(self.text_color)
        
        # 修复显示大小错误：改进文本垂直居中计算
        font_metrics = painter.fontMetrics()
        text_height = font_metrics.height()
        y = (self.height() + text_height) // 2 - font_metrics.descent()
        
        
        if self.scroll_direction in ["left", "right"]:
            painter.drawText(int(self.scroll_position), y, self.text)
        elif self.scroll_direction == "up":
            # 支持垂直滚动
            x = (self.width() - self.text_width) // 2
            painter.drawText(x, int(self.scroll_position), self.text)
        elif self.scroll_direction == "down":
            x = (self.width() - self.text_width) // 2
            painter.drawText(x, int(self.scroll_position), self.text)
        
        painter.end()


class ComponentManager(QObject):
    """组件管理器"""
    
    component_added = Signal(str, IComponent)
    component_removed = Signal(str)
    component_state_changed = Signal(str, ComponentState)
    
    def __init__(self, components_dir: str):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.ComponentManager')
        self.components_dir = components_dir
        self.components: Dict[str, IComponent] = {}
        self.component_configs: Dict[str, ComponentConfig] = {}
        self.component_classes: Dict[str, Type[IComponent]] = {}
        
        # 注册内置组件
        self.register_component_class("clock", ClockComponent)
        self.register_component_class("weather", WeatherComponent)
        self.register_component_class("scrolling_text", ScrollingTextComponent)
        
        # 加载外部组件
        self.load_external_components()
    
    def register_component_class(self, component_id: str, component_class: Type[IComponent]):
        """注册组件类"""
        try:
            self.component_classes[component_id] = component_class
            self.logger.info(f"组件类已注册: {component_id}")
        except Exception as e:
            self.logger.error(f"注册组件类失败: {e}", exc_info=True)
    
    def load_external_components(self):
        """加载外部组件"""
        try:
            if not os.path.exists(self.components_dir):
                os.makedirs(self.components_dir)
                return
            
            # 添加组件目录到Python路径
            if self.components_dir not in sys.path:
                sys.path.insert(0, self.components_dir)
            
            # 扫描组件文件
            for filename in os.listdir(self.components_dir):
                if filename.endswith('.py') and not filename.startswith('_'):
                    module_name = filename[:-3]
                    try:
                        module = importlib.import_module(module_name)
                        
                        # 查找组件类
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and
                                issubclass(obj, IComponent) and 
                                obj != IComponent and 
                                obj != BaseComponent):
                                
                                # 创建实例获取信息
                                instance = obj()
                                component_id = instance.info.id
                                
                                self.register_component_class(component_id, obj)
                                
                    except Exception as e:
                        self.logger.error(f"加载组件模块失败 {module_name}: {e}", exc_info=True)
                        
        except Exception as e:
            self.logger.error(f"加载外部组件失败: {e}", exc_info=True)
    
    def create_component(self, component_id: str, config: Optional[ComponentConfig] = None) -> Optional[IComponent]:
        """创建组件实例"""
        try:
            if component_id not in self.component_classes:
                self.logger.error(f"组件类不存在: {component_id}")
                return None
            
            component_class = self.component_classes[component_id]
            
            # 创建实例
            if component_id == "weather":
                # 天气组件需要天气服务
                from .weather_service import WeatherService
                weather_service = WeatherService("")
                component = component_class(weather_service)
            else:
                component = component_class()
            
            # 连接信号
            component.state_changed.connect(
                lambda state, cid=component_id: self.component_state_changed.emit(cid, state)
            )
            
            # 初始化
            if config is None:
                config = ComponentConfig(
                    component_id=component_id,
                    size=component.info.default_size
                )
            
            
            if component.initialize(config):
                self.components[component_id] = component
                self.component_configs[component_id] = config
                self.component_added.emit(component_id, component)
                return component
            else:
                component.cleanup()
                return None
                
        except Exception as e:
            self.logger.error(f"创建组件失败: {e}", exc_info=True)
            return None
    
    def remove_component(self, component_id: str) -> bool:
        """移除组件"""
        try:
            if component_id in self.components:
                component = self.components[component_id]
                component.cleanup()
                
                del self.components[component_id]
                if component_id in self.component_configs:
                    del self.component_configs[component_id]
                    del self.component_configs[component_id]
                
                self.component_removed.emit(component_id)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"移除组件失败: {e}", exc_info=True)
            return False
    
    def get_component(self, component_id: str) -> Optional[IComponent]:
        """获取组件"""
        return self.components.get(component_id)
    
    def get_all_components(self) -> Dict[str, IComponent]:
        """获取所有组件"""
        return self.components.copy()
    
    def get_available_component_classes(self) -> Dict[str, Type[IComponent]]:
        """获取可用的组件类"""
        return self.component_classes.copy()
    
    def configure_component(self, component_id: str, settings: Dict[str, Any]) -> bool:
        """配置组件"""
        try:
            if component_id in self.components:
                component = self.components[component_id]
                if component.configure(settings):
                    # 更新配置:
                    # 更新配置
                    if component_id in self.component_configs:
                        self.component_configs[component_id].settings = settings
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"配置组件失败: {e}", exc_info=True)
            return False
    
    def update_all_components(self):
        """更新所有组件"""
        try:
            for component_id, component in self.components.items():
                if component.state == ComponentState.ENABLED:
                    component.update()
                    
        except Exception as e:
            self.logger.error(f"更新所有组件失败: {e}", exc_info=True)
    
    def cleanup(self):
        """清理所有组件"""
        try:
            for component in self.components.values():
                component.cleanup()
            
            self.components.clear()
            self.component_configs.clear()
            
            self.logger.info("组件管理器已清理")
            
        except Exception as e:
            self.logger.error(f"清理组件管理器失败: {e}", exc_info=True)


class ComponentLayoutManager(QObject):
    """组件布局管理器"""
    
    def __init__(self, container_widget: QWidget):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.ComponentLayoutManager')
        self.container = container_widget
        self.layout_type = "grid"  # grid, flow, custom
        self.grid_columns = 3
        self.auto_arrange = True
        self.component_widgets: Dict[str, QWidget] = {}
        
        # 设置布局
        self.setup_layout()
    
    def setup_layout(self):
        """设置布局"""
        try:
            # 清除现有布局
            if self.container.layout():
                while self.container.layout().count():
                    child = self.container.layout().takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                self.container.layout().deleteLater()
            
            # 创建新布局
            if self.layout_type == "grid":
                self.layout = QGridLayout(self.container)
            else:
                self.layout = QVBoxLayout(self.container)
            
            self.container.setLayout(self.layout)
            
        except Exception as e:
            self.logger.error(f"设置布局失败: {e}", exc_info=True)
    
    def add_component_widget(self, component_id: str, widget: QWidget):
        """添加组件控件"""
        try:
            self.component_widgets[component_id] = widget
            
            if self.auto_arrange:
                self.arrange_components()
            else:
                self.layout.addWidget(widget)
                
        except Exception as e:
            self.logger.error(f"添加组件控件失败: {e}", exc_info=True)
    
    def remove_component_widget(self, component_id: str):
        """移除组件控件"""
        try:
            if component_id in self.component_widgets:
                widget = self.component_widgets[component_id]
                self.layout.removeWidget(widget)
                widget.setParent(None)
                del self.component_widgets[component_id]
                
                if self.auto_arrange:
                    self.arrange_components()
                    
        except Exception as e:
            self.logger.error(f"移除组件控件失败: {e}", exc_info=True)
    
    def arrange_components(self):
        """排列组件"""
        try:
            if self.layout_type == "grid":
                self.arrange_grid()
            else:
                self.arrange_flow()
                
        except Exception as e:
            self.logger.error(f"排列组件失败: {e}", exc_info=True)
    
    def arrange_grid(self):
        """网格排列"""
        try:
            # 清除现有布局项
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            
            # 重新排列
            row = 0
            col = 0
            
            for widget in self.component_widgets.values():
                self.layout.addWidget(widget, row, col)
                
                col += 1
                if col >= self.grid_columns:
                    col = 0
                    row += 1
                    
        except Exception as e:
            self.logger.error(f"网格排列失败: {e}", exc_info=True)
    
    def arrange_flow(self):
        """流式排列"""
        try:
            # 清除现有布局项
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            
            # 重新添加
            for widget in self.component_widgets.values():
                self.layout.addWidget(widget)
                
        except Exception as e:
            self.logger.error(f"流式排列失败: {e}", exc_info=True)
    
    def set_layout_type(self, layout_type: str):
        """设置布局类型"""
        try:
            self.layout_type = layout_type
            self.setup_layout()
            
            # 重新添加所有组件
            for component_id, widget in self.component_widgets.items():
                self.layout.addWidget(widget)
            
            if self.auto_arrange:
                self.arrange_components()
                
        except Exception as e:
            self.logger.error(f"设置布局类型失败: {e}", exc_info=True)
    
    def set_grid_columns(self, columns: int):
        """设置网格列数"""
        try:
            self.grid_columns = max(1, columns)
            
            if self.layout_type == "grid" and self.auto_arrange:
                self.arrange_components()
                
        except Exception as e:
            self.logger.error(f"设置网格列数失败: {e}", exc_info=True)
    
    def set_auto_arrange(self, auto_arrange: bool):
        """设置自动排列"""
        self.auto_arrange = auto_arrange
        
        if auto_arrange:
            self.arrange_components()