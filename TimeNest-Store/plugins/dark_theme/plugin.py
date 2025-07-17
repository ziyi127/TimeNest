#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
深色主题插件
提供多种深色主题变体
"""

import logging
from datetime import datetime, time
from typing import Dict, Any, Optional
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

# 导入插件基类
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from core.plugin_base import IPlugin, PluginStatus


class DarkThemePlugin(IPlugin):
    """深色主题插件"""
    
    # 定义信号
    theme_changed = pyqtSignal(str, dict)  # theme_id, theme_data
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.DarkThemePlugin')
        
        # 插件状态
        self.status = PluginStatus.LOADED
        
        # 组件
        self.auto_switch_timer = None
        self.plugin_manager = None
        
        # 设置
        self.settings = {
            'theme_variant': 'midnight',
            'accent_color': 'blue',
            'auto_switch': False,
            'switch_time_start': '18:00',
            'switch_time_end': '06:00',
            'apply_to_floating': True,
            'apply_to_dialogs': True
        }
        
        # 主题定义
        self.themes = {
            'midnight': {
                'name': '午夜蓝',
                'background': '#1a1a2e',
                'surface': '#16213e',
                'primary': '#0f3460',
                'text': '#e94560',
                'text_secondary': '#a8a8a8',
                'border': '#2d3748'
            },
            'charcoal': {
                'name': '炭黑',
                'background': '#2d3748',
                'surface': '#4a5568',
                'primary': '#718096',
                'text': '#f7fafc',
                'text_secondary': '#cbd5e0',
                'border': '#4a5568'
            },
            'obsidian': {
                'name': '黑曜石',
                'background': '#000000',
                'surface': '#1a1a1a',
                'primary': '#333333',
                'text': '#ffffff',
                'text_secondary': '#cccccc',
                'border': '#333333'
            },
            'slate': {
                'name': '石板灰',
                'background': '#1e293b',
                'surface': '#334155',
                'primary': '#475569',
                'text': '#f1f5f9',
                'text_secondary': '#cbd5e1',
                'border': '#475569'
            }
        }
        
        # 强调色定义
        self.accent_colors = {
            'blue': '#3b82f6',
            'green': '#10b981',
            'purple': '#8b5cf6',
            'orange': '#f59e0b',
            'red': '#ef4444'
        }
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.logger.info("深色主题插件初始化开始")
            
            # 创建自动切换定时器
            self.auto_switch_timer = QTimer()
            self.auto_switch_timer.timeout.connect(self.check_auto_switch)
            
            # 如果启用自动切换，开始定时检查
            if self.settings['auto_switch']:
                self.auto_switch_timer.start(60000)  # 每分钟检查一次
            
            self.status = PluginStatus.INITIALIZED
            self.logger.info("深色主题插件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            if self.status != PluginStatus.INITIALIZED:
                self.logger.error("插件未正确初始化")
                return False
            
            # 应用当前主题
            self.apply_current_theme()
            
            self.status = PluginStatus.ENABLED
            self.logger.info("深色主题插件已激活")
            return True
            
        except Exception as e:
            self.logger.error(f"插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            # 停止自动切换定时器
            if self.auto_switch_timer and self.auto_switch_timer.isActive():
                self.auto_switch_timer.stop()
            
            # 恢复默认主题
            self.restore_default_theme()
            
            self.status = PluginStatus.DISABLED
            self.logger.info("深色主题插件已停用")
            return True
            
        except Exception as e:
            self.logger.error(f"插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理插件资源"""
        try:
            # 停用插件
            self.deactivate()
            
            # 清理定时器
            if self.auto_switch_timer:
                self.auto_switch_timer.deleteLater()
                self.auto_switch_timer = None
            
            self.status = PluginStatus.UNLOADED
            self.logger.info("深色主题插件资源清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
            return False
    
    def apply_current_theme(self):
        """应用当前主题"""
        try:
            theme_variant = self.settings['theme_variant']
            accent_color = self.settings['accent_color']
            
            if theme_variant not in self.themes:
                self.logger.warning(f"未知主题变体: {theme_variant}")
                theme_variant = 'midnight'
            
            theme_data = self.themes[theme_variant].copy()
            theme_data['accent'] = self.accent_colors.get(accent_color, '#3b82f6')
            
            # 生成样式表
            stylesheet = self.generate_stylesheet(theme_data)
            
            # 应用主题
            self.apply_theme_to_app(stylesheet, theme_data)
            
            # 发送主题变化信号
            self.theme_changed.emit(theme_variant, theme_data)
            
            self.logger.info(f"已应用主题: {theme_data['name']}")
            
        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")
    
    def generate_stylesheet(self, theme_data: Dict[str, str]) -> str:
        """生成样式表"""
        return f"""
        QWidget {{
            background-color: {theme_data['background']};
            color: {theme_data['text']};
            border: none;
        }}
        
        QDialog, QMainWindow {{
            background-color: {theme_data['background']};
            color: {theme_data['text']};
        }}
        
        QLabel {{
            color: {theme_data['text']};
            background-color: transparent;
        }}
        
        QPushButton {{
            background-color: {theme_data['surface']};
            color: {theme_data['text']};
            border: 1px solid {theme_data['border']};
            border-radius: 4px;
            padding: 6px 12px;
        }}
        
        QPushButton:hover {{
            background-color: {theme_data['primary']};
            border-color: {theme_data['accent']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme_data['accent']};
        }}
        
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {theme_data['surface']};
            color: {theme_data['text']};
            border: 1px solid {theme_data['border']};
            border-radius: 4px;
            padding: 4px 8px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {theme_data['accent']};
        }}
        
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {theme_data['surface']};
            color: {theme_data['text']};
            border: 1px solid {theme_data['border']};
            alternate-background-color: {theme_data['primary']};
        }}
        
        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {theme_data['accent']};
            color: {theme_data['background']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {theme_data['border']};
            background-color: {theme_data['surface']};
        }}
        
        QTabBar::tab {{
            background-color: {theme_data['primary']};
            color: {theme_data['text']};
            border: 1px solid {theme_data['border']};
            padding: 6px 12px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme_data['accent']};
            color: {theme_data['background']};
        }}
        
        QScrollBar:vertical {{
            background-color: {theme_data['surface']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme_data['primary']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme_data['accent']};
        }}
        
        QProgressBar {{
            background-color: {theme_data['surface']};
            border: 1px solid {theme_data['border']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {theme_data['accent']};
            border-radius: 3px;
        }}
        """
    
    def apply_theme_to_app(self, stylesheet: str, theme_data: Dict[str, str]):
        """应用主题到应用程序"""
        try:
            # 这里应该调用应用程序的主题管理器
            # 由于我们在插件中，需要通过插件管理器来访问
            if self.plugin_manager and hasattr(self.plugin_manager, 'app_manager'):
                app_manager = self.plugin_manager.app_manager
                if hasattr(app_manager, 'theme_manager'):
                    theme_manager = app_manager.theme_manager
                    # 应用自定义样式表
                    # theme_manager.apply_custom_stylesheet(stylesheet)
            
            self.logger.debug("主题已应用到应用程序")
            
        except Exception as e:
            self.logger.error(f"应用主题到应用程序失败: {e}")
    
    def restore_default_theme(self):
        """恢复默认主题"""
        try:
            # 这里应该恢复应用程序的默认主题
            if self.plugin_manager and hasattr(self.plugin_manager, 'app_manager'):
                app_manager = self.plugin_manager.app_manager
                if hasattr(app_manager, 'theme_manager'):
                    theme_manager = app_manager.theme_manager
                    # 恢复默认主题
                    # theme_manager.restore_default_theme()
            
            self.logger.info("已恢复默认主题")
            
        except Exception as e:
            self.logger.error(f"恢复默认主题失败: {e}")
    
    def check_auto_switch(self):
        """检查自动切换"""
        try:
            if not self.settings['auto_switch']:
                return
            
            now = datetime.now().time()
            start_time = time.fromisoformat(self.settings['switch_time_start'])
            end_time = time.fromisoformat(self.settings['switch_time_end'])
            
            # 判断是否在深色主题时间段内
            if start_time <= end_time:
                # 同一天内的时间段
                should_use_dark = start_time <= now <= end_time
            else:
                # 跨天的时间段
                should_use_dark = now >= start_time or now <= end_time
            
            if should_use_dark:
                # 应用深色主题
                self.apply_current_theme()
            else:
                # 恢复默认主题
                self.restore_default_theme()
            
        except Exception as e:
            self.logger.error(f"自动切换检查失败: {e}")
    
    def get_widget(self) -> Optional[QWidget]:
        """获取插件组件"""
        # 主题插件通常不需要显示组件
        return None
    
    def get_settings(self) -> Dict[str, Any]:
        """获取插件设置"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """更新插件设置"""
        try:
            old_auto_switch = self.settings['auto_switch']
            self.settings.update(new_settings)
            
            # 如果自动切换设置改变，更新定时器
            if self.settings['auto_switch'] != old_auto_switch:
                if self.settings['auto_switch']:
                    if self.auto_switch_timer:
                        self.auto_switch_timer.start(60000)
                else:
                    if self.auto_switch_timer:
                        self.auto_switch_timer.stop()
            
            # 重新应用主题
            if self.status == PluginStatus.ENABLED:
                self.apply_current_theme()
            
            self.logger.info("插件设置已更新")
            return True
            
        except Exception as e:
            self.logger.error(f"更新插件设置失败: {e}")
            return False
    
    def get_available_themes(self) -> Dict[str, Dict[str, str]]:
        """获取可用主题列表"""
        return self.themes.copy()
    
    def get_available_accent_colors(self) -> Dict[str, str]:
        """获取可用强调色列表"""
        return self.accent_colors.copy()
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            'id': 'dark_theme',
            'name': '深色主题包',
            'version': '1.5.2',
            'description': '精美的深色主题集合',
            'author': 'Design Studio',
            'status': self.status.value,
            'settings': self.settings,
            'themes': list(self.themes.keys()),
            'accent_colors': list(self.accent_colors.keys())
        }


# 插件入口点
def create_plugin():
    """创建插件实例"""
    return DarkThemePlugin()
