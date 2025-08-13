import logging
from enum import Enum
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, Signal, QObject
from PySide6.QtGui import QPalette, QColor, QFont


class ThemeType(Enum):
    """主题类型枚举"""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class ThemeManager:
    """主题管理器 - 管理应用主题和样式"""
    
    # 主题变化信号
    theme_changed_signal = Signal(object)
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化主题管理器"""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self._current_theme = ThemeType.DARK
            self._theme_changed = False
            self._initialized = True
            
            # 定义主题颜色方案
            self._themes = {
                ThemeType.DARK: {
                    'background': QColor(20, 20, 20, 220),
                    'border': QColor(255, 255, 255, 40),
                    'text_primary': QColor(255, 255, 255),
                    'text_secondary': QColor(204, 204, 204),
                    'accent': QColor(0, 120, 212),
                    'success': QColor(76, 175, 80),
                    'warning': QColor(255, 152, 0),
                    'error': QColor(244, 67, 54),
                    'info': QColor(33, 150, 243),
                    'shadow': QColor(0, 0, 0, 50)
                },
                ThemeType.LIGHT: {
                    'background': QColor(245, 245, 245),
                    'border': QColor(200, 200, 200),
                    'text_primary': QColor(0, 0, 0),
                    'text_secondary': QColor(100, 100, 100),
                    'accent': QColor(0, 120, 212),
                    'success': QColor(76, 175, 80),
                    'warning': QColor(255, 152, 0),
                    'error': QColor(244, 67, 54),
                    'info': QColor(33, 150, 243),
                    'shadow': QColor(0, 0, 0, 30)
                }
            }
    
    @property
    def current_theme(self):
        """获取当前主题"""
        return self._current_theme
    
    @current_theme.setter
    def current_theme(self, theme_type):
        """设置当前主题"""
        if isinstance(theme_type, str):
            try:
                theme_type = ThemeType(theme_type)
            except ValueError:
                theme_type = ThemeType.DARK  # 默认为深色主题
        
        if self._current_theme != theme_type:
            self._current_theme = theme_type
            self._theme_changed = True
            self.logger.info(f"主题已切换为: {theme_type.value}")
            self.theme_changed_signal.emit(self._current_theme)
    
    def get_theme_color(self, color_name, theme_type=None):
        """获取指定主题的颜色值"""
        if theme_type is None:
            theme_type = self._current_theme
            
        theme_colors = self._themes.get(theme_type, self._themes[ThemeType.DARK])
        return theme_colors.get(color_name, QColor(0, 0, 0))
    
    def get_theme_stylesheet(self):
        """获取当前主题的样式表"""
        theme = self._current_theme
        colors = self._themes[theme]
        
        stylesheet = f"""
            QMainWindow {{
                background: transparent;
                font-family: "Microsoft YaHei", "SimHei", "sans-serif";
            }}
            #MainWindowRoot {{
                background-color: {colors['background'].name()};
                border-radius: 12px;
                border: 1px solid {colors['border'].name()};
                box-shadow: 0 8px 32px {colors['shadow'].name()};
            }}
            QLabel {{
                color: {colors['text_primary'].name()};
            }}
            QLabel#mainTimeDisplay {{
                color: {colors['text_primary'].name()};
                text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
            }}
            QLabel#dateDisplay {{
                color: {colors['text_secondary'].name()};
                text-shadow: 0 0 4px rgba(255, 255, 255, 0.3);
            }}
            QLabel#Tomorrow {{
                background-color: {colors['accent'].name()};
                color: white;
                border-radius: 16px;
                padding: 4px 12px;
                margin: 0 4px 0 0;
                font-size: 13px;
                font-weight: bold;
                min-width: 40px;
            }}
            QLabel#EmptyPlaceholder {{
                color: {colors['text_secondary'].name()};
                font-size: 14px;
                font-style: italic;
            }}
            QFrame:hover {{
                background-color: rgba(0, 120, 212, 0.1);
            }}
        """
        return stylesheet
    
    def apply_theme_to_widget(self, widget):
        """将当前主题应用到指定窗口部件"""
        try:
            # 应用样式表
            widget.setStyleSheet(self.get_theme_stylesheet())
            
            # 更新窗口属性
            if hasattr(widget, 'setWindowOpacity'):
                widget.setWindowOpacity(0.95)
                
            # 更新窗口背景
            if hasattr(widget, 'setAttribute'):
                widget.setAttribute(Qt.WA_TranslucentBackground, True)
                
        except Exception as e:
            self.logger.error(f"应用主题到窗口部件时出错: {e}")
    
    def apply_theme_to_component(self, component):
        """将主题应用到指定组件"""
        try:
            # 获取当前主题颜色
            theme = self._current_theme
            colors = self._themes[theme]
            
            # 为不同组件应用不同样式
            if hasattr(component, 'setStyleSheet'):
                if hasattr(component, 'objectName'):
                    obj_name = component.objectName()
                    if obj_name == "mainTimeDisplay":
                        component.setStyleSheet(f"""
                            QLabel {{
                                color: {colors['text_primary'].name()};
                                background: transparent;
                                font-family: "Microsoft YaHei";
                                font-weight: bold;
                                text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
                            }}
                        """)
                    elif obj_name == "dateDisplay":
                        component.setStyleSheet(f"""
                            QLabel {{
                                color: {colors['text_secondary'].name()};
                                background: transparent;
                                font-family: "Microsoft YaHei";
                                font-weight: normal;
                                text-shadow: 0 0 4px rgba(255, 255, 255, 0.3);
                            }}
                        """)
                        
        except Exception as e:
            self.logger.error(f"应用主题到组件时出错: {e}")
    
    def get_available_themes(self):
        """获取可用的主题列表"""
        return list(ThemeType)
    
    def is_theme_changed(self):
        """检查主题是否已改变"""
        return self._theme_changed
    
    def reset_theme_changed_flag(self):
        """重置主题改变标志"""
        self._theme_changed = False


# 创建全局主题管理器实例
theme_manager = ThemeManager()
