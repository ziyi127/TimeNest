"""
悬浮窗管理器 - RinUI版本
"""

import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal, QTimer, QUrl
from PySide6.QtQml import qmlRegisterType, QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtGui import QGuiApplication


class FloatingWindowManager(QObject):
    """悬浮窗管理器"""
    
    # 信号定义
    visibility_changed = Signal(bool)
    position_changed = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.FloatingWindowManager')
        
        # 悬浮窗实例
        self.floating_engine: Optional[QQmlApplicationEngine] = None
        self.floating_window: Optional[QQuickWindow] = None
        self.is_visible = False
        
        # 配置
        self.config = {
            'width': 450,
            'height': 70,
            'opacity': 0.9,
            'auto_hide': False,
            'mouse_through': False,
            'position_x': None,
            'position_y': None
        }
        
        # 数据更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)  # 每秒更新一次
        
    def create_floating_window(self) -> bool:
        """创建悬浮窗"""
        try:
            if self.floating_window is not None:
                return True

            # 创建QQmlApplicationEngine
            self.floating_engine = QQmlApplicationEngine()

            # 设置QML文件
            qml_file = QUrl.fromLocalFile("qml/FloatingWindow.qml")
            self.floating_engine.load(qml_file)

            # 获取根对象
            root_objects = self.floating_engine.rootObjects()
            if not root_objects:
                self.logger.error("悬浮窗QML加载失败：没有根对象")
                self.floating_engine = None
                return False

            # 获取窗口对象
            self.floating_window = root_objects[0]
            if not self.floating_window:
                self.logger.error("悬浮窗QML加载失败：根对象无效")
                self.floating_engine = None
                return False

            # 检查是否是Window类型
            if not hasattr(self.floating_window, 'show'):
                self.logger.error("悬浮窗QML根对象不是Window类型")
                self.floating_engine = None
                self.floating_window = None
                return False

            # 连接信号
            self._setup_connections()

            self.logger.info("悬浮窗创建成功")
            return True

        except Exception as e:
            self.logger.error(f"创建悬浮窗失败: {e}")
            self.floating_engine = None
            self.floating_window = None
            return False
            
    def _setup_connections(self):
        """设置信号连接"""
        if not self.floating_window:
            return
            
        # 获取根对象
        root_object = self.floating_window.rootObject()
        if not root_object:
            return
            
        # 连接QML信号到Python槽
        try:
            # 这里可以连接QML中定义的信号
            pass
        except Exception as e:
            self.logger.warning(f"连接QML信号失败: {e}")
            
    def show_floating_window(self):
        """显示悬浮窗"""
        if not self.floating_window:
            if not self.create_floating_window():
                return

        try:
            # 设置位置
            if self.config['position_x'] is not None and self.config['position_y'] is not None:
                self.floating_window.setProperty("x", self.config['position_x'])
                self.floating_window.setProperty("y", self.config['position_y'])
            else:
                # 默认位置：屏幕右上角
                screen = QGuiApplication.primaryScreen()
                if screen:
                    geometry = screen.availableGeometry()
                    self.floating_window.setProperty("x", geometry.width() - self.config['width'] - 20)
                    self.floating_window.setProperty("y", 20)

            # 显示窗口
            self.floating_window.show()
            self.is_visible = True
            self.visibility_changed.emit(True)

            # 调用QML的显示动画
            if hasattr(self.floating_window, 'showWithAnimation'):
                self.floating_window.showWithAnimation()

            self.logger.info("悬浮窗已显示")

        except Exception as e:
            self.logger.error(f"显示悬浮窗失败: {e}")
            
    def hide_floating_window(self):
        """隐藏悬浮窗"""
        if not self.floating_window or not self.is_visible:
            return

        try:
            # 调用QML的隐藏动画
            if hasattr(self.floating_window, 'hideWithAnimation'):
                self.floating_window.hideWithAnimation()
            else:
                self.floating_window.hide()

            self.is_visible = False
            self.visibility_changed.emit(False)
            self.logger.info("悬浮窗已隐藏")

        except Exception as e:
            self.logger.error(f"隐藏悬浮窗失败: {e}")
            
    def toggle_floating_window(self):
        """切换悬浮窗显示状态"""
        if self.is_visible:
            self.hide_floating_window()
        else:
            self.show_floating_window()
            
    def update_config(self, config: dict):
        """更新配置"""
        self.config.update(config)
        
        if self.floating_window:
            root_object = self.floating_window.rootObject()
            if root_object:
                # 更新QML属性
                if 'opacity' in config:
                    root_object.setProperty("windowOpacity", config['opacity'])
                if 'auto_hide' in config:
                    root_object.setProperty("autoHide", config['auto_hide'])
                if 'mouse_through' in config:
                    root_object.setProperty("mouseThrough", config['mouse_through'])
                    
    def _update_data(self):
        """更新悬浮窗数据"""
        if not self.floating_window or not self.is_visible:
            return
            
        try:
            if not self.floating_window:
                return

            # 更新下节课程信息
            next_class = self._get_next_class()
            if next_class and hasattr(self.floating_window, 'updateNextClass'):
                self.floating_window.updateNextClass(next_class)

            # 更新天气信息
            weather = self._get_weather_info()
            if weather and hasattr(self.floating_window, 'updateWeather'):
                self.floating_window.updateWeather(weather)

        except Exception as e:
            self.logger.debug(f"更新悬浮窗数据失败: {e}")
            
    def _get_next_class(self) -> str:
        """获取下节课程信息"""
        # TODO: 从课程表管理器获取下节课程
        return "数学课 14:00"
        
    def _get_weather_info(self) -> str:
        """获取天气信息"""
        # TODO: 从天气服务获取天气信息
        return "25°C"
        
    def save_position(self, x: int, y: int):
        """保存窗口位置"""
        self.config['position_x'] = x
        self.config['position_y'] = y
        self.position_changed.emit(x, y)
        
    def get_position(self) -> tuple:
        """获取窗口位置"""
        if self.floating_window:
            try:
                x = self.floating_window.property("x") or 0
                y = self.floating_window.property("y") or 0
                return (x, y)
            except:
                pass
        return (self.config.get('position_x', 0), self.config.get('position_y', 0))
        
    def is_window_visible(self) -> bool:
        """检查悬浮窗是否可见"""
        return self.is_visible
        
    def cleanup(self):
        """清理资源"""
        if self.update_timer:
            self.update_timer.stop()

        if self.floating_window:
            self.floating_window.hide()
            self.floating_window = None

        if self.floating_engine:
            self.floating_engine.deleteLater()
            self.floating_engine = None

        self.is_visible = False
        self.logger.info("悬浮窗管理器已清理")


class FloatingWindowBridge(QObject):
    """悬浮窗桥接类，用于QML和Python之间的通信"""
    
    def __init__(self, manager: FloatingWindowManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.logger = logging.getLogger(f'{__name__}.FloatingWindowBridge')
        
    def saveSetting(self, key: str, value):
        """保存设置"""
        try:
            if key == "floating_window_x":
                self.manager.save_position(value, self.manager.get_position()[1])
            elif key == "floating_window_y":
                self.manager.save_position(self.manager.get_position()[0], value)
            else:
                self.manager.config[key.replace("floating_window_", "")] = value
                
            self.logger.debug(f"保存设置: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            
    def loadSetting(self, key: str):
        """加载设置"""
        try:
            if key == "floating_window_x":
                return self.manager.get_position()[0]
            elif key == "floating_window_y":
                return self.manager.get_position()[1]
            else:
                config_key = key.replace("floating_window_", "")
                return self.manager.config.get(config_key)
                
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            return None
