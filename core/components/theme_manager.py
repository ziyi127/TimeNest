import logging
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QPalette, QColor

from core.models.component_settings.lesson_control_settings import LessonControlSettings


class ThemeManager(QObject):
    """主题管理器 - 管理应用主题和外观，基于ClassIsland的ThemeService实现"""
    
    # 主题变更信号
    theme_changed = Signal(str)
    
    # 颜色变更信号
    colors_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 主题相关变量
        self.current_theme = "default"
        self.primary_color = QColor("#007bff")
        self.secondary_color = QColor("#6c757d")
        self.background_color = QColor("#ffffff")
        self.foreground_color = QColor("#000000")
        
        # 初始化应用样式
        self.init_application_style()
        
    def init_application_style(self):
        """初始化应用样式"""
        # 获取应用实例
        app = QApplication.instance()
        if app:
            # 应用默认样式
            app.setStyle("Fusion")
            
    def set_theme(self, theme_name: str):
        """设置主题"""
        old_theme = self.current_theme
        self.current_theme = theme_name
        
        # 根据主题应用相应的颜色配置
        self.apply_theme_colors(theme_name)
        
        # 发送主题变更信号
        self.theme_changed.emit(theme_name)
        
        self.logger.info(f"主题已从 {old_theme} 切换到 {theme_name}")
        
    def apply_theme_colors(self, theme_name: str):
        """应用主题颜色"""
        if theme_name == "light":
            self.set_light_theme()
        elif theme_name == "dark":
            self.set_dark_theme()
        elif theme_name == "blue":
            self.set_blue_theme()
        else:
            self.set_default_theme()
            
        # 更新应用样式
        self.update_application_palette()
        
    def set_light_theme(self):
        """设置浅色主题"""
        self.primary_color = QColor("#007bff")
        self.secondary_color = QColor("#6c757d")
        self.background_color = QColor("#ffffff")
        self.foreground_color = QColor("#000000")
        
    def set_dark_theme(self):
        """设置深色主题"""
        self.primary_color = QColor("#0d6efd")
        self.secondary_color = QColor("#6c757d")
        self.background_color = QColor("#121212")
        self.foreground_color = QColor("#ffffff")
        
    def set_blue_theme(self):
        """设置蓝色主题"""
        self.primary_color = QColor("#007bff")
        self.secondary_color = QColor("#0056b3")
        self.background_color = QColor("#f8f9fa")
        self.foreground_color = QColor("#212529")
        
    def set_default_theme(self):
        """设置默认主题"""
        self.primary_color = QColor("#007bff")
        self.secondary_color = QColor("#6c757d")
        self.background_color = QColor("#ffffff")
        self.foreground_color = QColor("#000000")
        
    def set_primary_color(self, color: QColor):
        """设置主色调"""
        self.primary_color = color
        self.colors_changed.emit()
        
    def set_secondary_color(self, color: QColor):
        """设置辅助色调"""
        self.secondary_color = color
        self.colors_changed.emit()
        
    def set_background_color(self, color: QColor):
        """设置背景色"""
        self.background_color = color
        self.colors_changed.emit()
        
    def set_foreground_color(self, color: QColor):
        """设置前景色"""
        self.foreground_color = color
        self.colors_changed.emit()
        
    def get_primary_color(self):
        """获取主色调"""
        return self.primary_color
        
    def get_secondary_color(self):
        """获取辅助色调"""
        return self.secondary_color
        
    def get_background_color(self):
        """获取背景色"""
        return self.background_color
        
    def get_foreground_color(self):
        """获取前景色"""
        return self.foreground_color
        
    def update_application_palette(self):
        """更新应用调色板"""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            
            # 设置各种颜色
            palette.setColor(QPalette.Window, self.background_color)
            palette.setColor(QPalette.WindowText, self.foreground_color)
            palette.setColor(QPalette.Base, self.background_color)
            palette.setColor(QPalette.AlternateBase, self.background_color.darker(110))
            palette.setColor(QPalette.ToolTipBase, self.background_color)
            palette.setColor(QPalette.ToolTipText, self.foreground_color)
            palette.setColor(QPalette.Text, self.foreground_color)
            palette.setColor(QPalette.Button, self.background_color)
            palette.setColor(QPalette.ButtonText, self.foreground_color)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, self.primary_color)
            palette.setColor(QPalette.HighlightedText, Qt.white)
            
            app.setPalette(palette)
            
    def get_current_theme(self):
        """获取当前主题"""
        return self.current_theme
        
    def get_theme_info(self):
        """获取主题信息"""
        return {
            "theme": self.current_theme,
            "primary_color": self.primary_color.name(),
            "secondary_color": self.secondary_color.name(),
            "background_color": self.background_color.name(),
            "foreground_color": self.foreground_color.name()
        }


# 全局主题管理器实例
theme_manager = ThemeManager()


def get_theme_manager():
    """获取主题管理器实例"""
    return theme_manager


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建主题管理器
    theme_manager = ThemeManager()
    
    # 测试主题设置
    print("当前主题:", theme_manager.get_current_theme())
    theme_manager.set_theme("dark")
    print("切换后主题:", theme_manager.get_current_theme())
    
    # 测试颜色设置
    theme_manager.set_primary_color(QColor("#ff0000"))
    print("主色调:", theme_manager.get_primary_color().name())
    
    sys.exit(app.exec())
