from enum import Enum
from typing import Optional
import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor


class ThemeType(Enum):
    """主题类型枚举"""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class ThemeManager(QObject):
    """主题管理器 - 管理应用主题和样式"""
    
    # 主题变化信号
    theme_changed_signal = Signal(ThemeType)
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """初始化主题管理器"""
        if self._initialized:
            return
        super().__init__()
            
        self.logger = logging.getLogger(__name__)
        self._current_theme = ThemeType.DARK
        self._theme_changed = False
        
        # 定义主题颜色
        self._themes = {
            ThemeType.DARK: {
                'background': QColor(20, 20, 20, 220),  # 深色半透明背景
                'border': QColor(255, 255, 255, 30),    # 浅色边框
                'shadow': QColor(0, 0, 0, 102),         # 阴影颜色
                'text_primary': QColor(255, 255, 255),  # 主要文字颜色
                'text_secondary': QColor(204, 204, 204),# 次要文字颜色
                'accent': QColor(0, 120, 212),          # 强调色
                'hover': QColor(255, 255, 255, 25)      # 悬停效果颜色
            },
            ThemeType.LIGHT: {
                'background': QColor(245, 245, 245, 230), # 浅色半透明背景
                'border': QColor(0, 0, 0, 30),            # 深色边框
                'shadow': QColor(0, 0, 0, 51),            # 阴影颜色
                'text_primary': QColor(30, 30, 30),       # 主要文字颜色
                'text_secondary': QColor(100, 100, 100),  # 次要文字颜色
                'accent': QColor(0, 120, 212),            # 强调色
                'hover': QColor(0, 0, 0, 15)              # 悬停效果颜色
            }
        }
        
        self._initialized = True
        
    @property
    def current_theme(self):
        """获取当前主题"""
        return self._current_theme
        
    @current_theme.setter
    def current_theme(self, theme: ThemeType):
        """设置当前主题"""
        if self._current_theme != theme:
            self._current_theme = theme
            self._theme_changed = True
            self.theme_changed_signal.emit(theme)
            
    def get_theme_colors(self, theme: Optional[ThemeType] = None):
        """获取主题颜色"""
        if theme is None:
            theme = self._current_theme
        return self._themes.get(theme, self._themes[ThemeType.DARK])
        
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
                border-radius: 16px;
                border: 1px solid {colors['border'].name()};
                box-shadow: 0 10px 32px {colors['shadow'].name()};
            }}
            QLabel {{
                color: {colors['text_primary'].name()};
            }}
            QLabel#mainTimeDisplay {{
                color: {colors['text_primary'].name()};
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
                font-size: 18px;
                font-weight: bold;
            }}
            QLabel#dateDisplay {{
                color: {colors['text_primary'].name()};
                text-shadow: 0 0 6px rgba(255, 255, 255, 0.7);
                font-size: 15px;
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
                background-color: {colors['hover'].name()};
            }}
            QFrame {{
                border-radius: 8px;
                transition: background-color 0.3s ease;
            }}
        """
        return stylesheet
        
    def apply_theme_to_widget(self, widget: 'QWidget'):
        """将当前主题应用到指定窗口部件"""
        try:
            # 应用样式表
            widget.setStyleSheet(self.get_theme_stylesheet())
            
            # 更新窗口属性
            if hasattr(widget, 'setWindowOpacity'):
                widget.setWindowOpacity(0.95)
                
            # 更新窗口背景
            if hasattr(widget, 'setAttribute'):
                widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                
        except Exception as e:
            self.logger.error(f"应用主题到窗口部件时出错: {e}")
    
    def apply_theme_to_component(self, component: 'QWidget'):
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
                                font-size: 18px;
                                text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
                            }}
                        """)
                    elif obj_name == "dateDisplay":
                        component.setStyleSheet(f"""
                            QLabel {{
                                color: {colors['text_primary'].name()};
                                background: transparent;
                                font-family: "Microsoft YaHei";
                                font-weight: normal;
                                font-size: 15px;
                                text-shadow: 0 0 6px rgba(255, 255, 255, 0.7);
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