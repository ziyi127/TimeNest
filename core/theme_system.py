#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 主题系统
支持动态主题切换、主题市场、自定义主题等功能
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor


class ThemeType(Enum):
    """主题类型"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    CUSTOM = "custom"


@dataclass
class ThemeColors:
    """主题颜色配置"""
    # 基础颜色
    primary: str = "#2196F3"
    secondary: str = "#FFC107"
    accent: str = "#FF5722"
    
    # 背景颜色
    background: str = "#FFFFFF"
    surface: str = "#F5F5F5"
    card: str = "#FFFFFF"
    
    # 文本颜色
    text_primary: str = "#212121"
    text_secondary: str = "#757575"
    text_disabled: str = "#BDBDBD"
    
    # 状态颜色
    success: str = "#4CAF50"
    warning: str = "#FF9800"
    error: str = "#F44336"
    info: str = "#2196F3"
    
    # 边框和分割线
    border: str = "#E0E0E0"
    divider: str = "#EEEEEE"
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            'primary': self.primary,
            'secondary': self.secondary,
            'accent': self.accent,
            'background': self.background,
            'surface': self.surface,
            'card': self.card,
            'text_primary': self.text_primary,
            'text_secondary': self.text_secondary,
            'text_disabled': self.text_disabled,
            'success': self.success,
            'warning': self.warning,
            'error': self.error,
            'info': self.info,
            'border': self.border,
            'divider': self.divider
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ThemeColors':
        """从字典创建"""
        return cls(**data)


@dataclass
class ThemeMetadata:
    """主题元数据"""
    id: str
    name: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    theme_type: ThemeType = ThemeType.LIGHT
    preview_image: str = ""
    tags: List[str] = field(default_factory=list)
    created_date: str = ""
    updated_date: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'version': self.version,
            'theme_type': self.theme_type.value,
            'preview_image': self.preview_image,
            'tags': self.tags,
            'created_date': self.created_date,
            'updated_date': self.updated_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeMetadata':
        """从字典创建"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            author=data.get('author', ''),
            version=data.get('version', '1.0.0'),
            theme_type=ThemeType(data.get('theme_type', 'light')),
            preview_image=data.get('preview_image', ''),
            tags=data.get('tags', []),
            created_date=data.get('created_date', ''),
            updated_date=data.get('updated_date', '')
        )


@dataclass
class Theme:
    """主题定义"""
    metadata: ThemeMetadata
    colors: ThemeColors
    styles: Dict[str, Any] = field(default_factory=dict)
    fonts: Dict[str, Any] = field(default_factory=dict)
    animations: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'metadata': self.metadata.to_dict(),
            'colors': self.colors.to_dict(),
            'styles': self.styles,
            'fonts': self.fonts,
            'animations': self.animations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """从字典创建"""
        return cls(
            metadata=ThemeMetadata.from_dict(data.get('metadata', {})),
            colors=ThemeColors.from_dict(data.get('colors', {})),
            styles=data.get('styles', {}),
            fonts=data.get('fonts', {}),
            animations=data.get('animations', {})
        )


class ThemeManager(QObject):
    """主题管理器"""
    
    # 信号定义
    theme_changed = pyqtSignal(str)  # 主题ID
    theme_loaded = pyqtSignal(str)   # 主题ID
    theme_error = pyqtSignal(str, str)  # 主题ID, 错误信息
    
    def __init__(self, config_manager=None):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.ThemeManager')
        self.config_manager = config_manager
        
        # 主题存储
        self.themes: Dict[str, Theme] = {}
        self.current_theme_id: Optional[str] = None
        self.current_theme: Optional[Theme] = None
        
        # 主题目录
        self.themes_dir = Path.home() / '.timenest' / 'themes'
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # 系统主题检测定时器
        self.system_theme_timer = QTimer()
        self.system_theme_timer.timeout.connect(self._check_system_theme)
        
        # 初始化
        self._load_builtin_themes()
        self._load_custom_themes()
        self._apply_default_theme()
    
    def _load_builtin_themes(self):
        """加载内置主题"""
        try:
            # 浅色主题
            light_theme = Theme(
                metadata=ThemeMetadata(
                    id="builtin_light",
                    name="浅色主题",
                    description="默认的浅色主题",
                    author="TimeNest Team",
                    theme_type=ThemeType.LIGHT
                ),
                colors=ThemeColors()  # 使用默认浅色配置
            )
            
            # 深色主题
            dark_colors = ThemeColors(
                primary="#1976D2",
                secondary="#FFC107",
                accent="#FF5722",
                background="#121212",
                surface="#1E1E1E",
                card="#2D2D2D",
                text_primary="#FFFFFF",
                text_secondary="#B0B0B0",
                text_disabled="#666666",
                border="#404040",
                divider="#333333"
            )
            
            dark_theme = Theme(
                metadata=ThemeMetadata(
                    id="builtin_dark",
                    name="深色主题",
                    description="默认的深色主题",
                    author="TimeNest Team",
                    theme_type=ThemeType.DARK
                ),
                colors=dark_colors
            )
            
            self.themes["builtin_light"] = light_theme
            self.themes["builtin_dark"] = dark_theme
            
            self.logger.info("内置主题加载完成")
            
        except Exception as e:
            self.logger.error(f"加载内置主题失败: {e}")
    
    def _load_custom_themes(self):
        """加载自定义主题"""
        try:
            theme_files = list(self.themes_dir.glob("*.json"))
            for theme_file in theme_files:
                try:
                    # 检查文件大小，避免加载过大的文件
                    if theme_file.stat().st_size > 1024 * 1024:  # 1MB限制
                        self.logger.warning(f"主题文件过大，跳过: {theme_file}")
                        continue

                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)

                    theme = Theme.from_dict(theme_data)
                    self.themes[theme.metadata.id] = theme

                    self.logger.debug(f"加载自定义主题: {theme.metadata.name}")

                except Exception as e:
                    self.logger.error(f"加载主题文件失败 {theme_file}: {e}")
            
            self.logger.info(f"自定义主题加载完成，共{len(self.themes)}个主题")
            
        except Exception as e:
            self.logger.error(f"加载自定义主题失败: {e}")
    
    def _apply_default_theme(self):
        """应用默认主题"""
        try:
            # 从配置中获取默认主题
            if self.config_manager:
                default_theme_id = self.config_manager.get_config('theme.current', 'builtin_light')
            else:
                default_theme_id = 'builtin_light'
            
            
            if default_theme_id in self.themes:
                self.apply_theme(default_theme_id)
            
                self.apply_theme(default_theme_id)
            else:
                self.apply_theme('builtin_light')
                
        except Exception as e:
            self.logger.error(f"应用默认主题失败: {e}")
    
    def get_available_themes(self) -> List[Theme]:
        """获取可用主题列表"""
        return list(self.themes.values())
    
    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """获取指定主题"""
        return self.themes.get(theme_id)
    
    def apply_theme(self, theme_id: str) -> bool:
        """应用主题"""
        try:
            if theme_id not in self.themes:
                self.logger.error(f"主题不存在: {theme_id}")
                return False
            
            theme = self.themes[theme_id]
            
            # 应用主题到Qt应用
            self._apply_qt_theme(theme)
            
            # 更新当前主题
            self.current_theme_id = theme_id
            self.current_theme = theme
            
            # 保存到配置
            if self.config_manager:
                self.config_manager.set_config('theme.current', theme_id)
            
            # 发送信号
            self.theme_changed.emit(theme_id)
            
            self.logger.info(f"主题应用成功: {theme.metadata.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")
            self.theme_error.emit(theme_id, str(e))
            return False
    
    def _apply_qt_theme(self, theme: Theme):
        """应用主题到Qt应用"""
        try:
            app = QApplication.instance()
            if not app:
                return
            
            # 创建调色板
            palette = QPalette()
            colors = theme.colors
            
            # 设置基础颜色
            palette.setColor(QPalette.ColorRole.Window, QColor(colors.background))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.text_primary))
            palette.setColor(QPalette.ColorRole.Base, QColor(colors.surface))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.card))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors.surface))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors.text_primary))
            palette.setColor(QPalette.ColorRole.Text, QColor(colors.text_primary))
            palette.setColor(QPalette.ColorRole.Button, QColor(colors.surface))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.text_primary))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(colors.accent))
            palette.setColor(QPalette.ColorRole.Link, QColor(colors.primary))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.primary))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.background))
            
            # 应用调色板
            app.setPalette(palette)
            
            # 生成并应用样式表
            stylesheet = self._generate_stylesheet(theme)
            app.setStyleSheet(stylesheet)
            
        except Exception as e:
            self.logger.error(f"应用Qt主题失败: {e}")
    
    def _generate_stylesheet(self, theme: Theme) -> str:
        """生成样式表"""
        try:
            colors = theme.colors
            
            # 基础样式
            stylesheet = f"""
            QMainWindow {{
                background-color: {colors.background};
                color: {colors.text_primary};
            }}
            
            QWidget {{
                background-color: {colors.background};
                color: {colors.text_primary};
            }}
            
            QPushButton {{
                background-color: {colors.primary};
                color: {colors.background};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {colors.secondary};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.accent};
            }}
            
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                padding: 4px 8px;
                border-radius: 4px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {colors.primary};
            }}
            
            QLabel {{
                color: {colors.text_primary};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.border};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }}
            
            QGroupBox:title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
            
            QTabWidget:pane {{
                border: 1px solid {colors.border};
                background-color: {colors.surface};
            }}
            
            QTabBar:tab {{
                background-color: {colors.card};
                color: {colors.text_secondary};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar:tab:selected {{
                background-color: {colors.primary};
                color: {colors.background};
            }}
            
            QMenuBar {{
                background-color: {colors.surface};
                color: {colors.text_primary};
            }}
            
            QMenuBar:item:selected {{
                background-color: {colors.primary};
                color: {colors.background};
            }}
            
            QMenu {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
            }}
            
            QMenu:item:selected {{
                background-color: {colors.primary};
                color: {colors.background};
            }}
            
            QStatusBar {{
                background-color: {colors.surface};
                color: {colors.text_secondary};
            }}
            
            QScrollBar:vertical {{
                background-color: {colors.surface};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar:handle:vertical {{
                background-color: {colors.border};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar:handle:vertical:hover {{
                background-color: {colors.primary};
            }}
            """
            
            # 添加自定义样式
            if theme.styles:
                for selector, style_dict in theme.styles.items():
                    style_rules = []
                    for property_name, value in style_dict.items():
                        style_rules.append(f"{property_name}: {value};")
                    
                    stylesheet += f"\n{selector} {{\n    {chr(10).join(style_rules)}\n}}\n"
            
            return stylesheet

        except Exception as e:
            self.logger.error(f"生成样式表失败: {e}")
            return ""

    def install_theme(self, theme_data: Dict[str, Any]) -> bool:
        """安装主题"""
        try:
            theme = Theme.from_dict(theme_data)

            # 验证主题数据
            if not theme.metadata.id or not theme.metadata.name:
                raise ValueError("主题ID和名称不能为空")

            # 检查是否已存在
            if theme.metadata.id in self.themes:
                self.logger.warning(f"主题已存在，将覆盖: {theme.metadata.name}")

            # 保存主题文件
            theme_file = self.themes_dir / f"{theme.metadata.id}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)

            # 添加到主题列表
            self.themes[theme.metadata.id] = theme

            self.logger.info(f"主题安装成功: {theme.metadata.name}")
            return True

        except Exception as e:
            self.logger.error(f"安装主题失败: {e}")
            return False

    def uninstall_theme(self, theme_id: str) -> bool:
        """卸载主题"""
        try:
            if theme_id.startswith('builtin_'):
                self.logger.error("不能卸载内置主题")
                return False


            if theme_id not in self.themes:
                self.logger.error(f"主题不存在: {theme_id}")

                self.logger.error(f"主题不存在: {theme_id}")
                return False

            # 如果是当前主题，切换到默认主题
            if theme_id == self.current_theme_id:
                self.apply_theme('builtin_light')

            # 删除主题文件
            theme_file = self.themes_dir / f"{theme_id}.json"
            if theme_file.exists():
                theme_file.unlink()

            # 从主题列表中移除
            del self.themes[theme_id]

            self.logger.info(f"主题卸载成功: {theme_id}")
            return True

        except Exception as e:
            self.logger.error(f"卸载主题失败: {e}")
            return False

    def export_theme(self, theme_id: str, export_path: str) -> bool:
        """导出主题"""
        try:
            if theme_id not in self.themes:
                self.logger.error(f"主题不存在: {theme_id}")
                return False

            theme = self.themes[theme_id]
            theme_data = theme.to_dict()

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"主题导出成功: {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"导出主题失败: {e}")
            return False

    def import_theme(self, import_path: str) -> bool:
        """导入主题"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)

            return self.install_theme(theme_data)

        except Exception as e:
            self.logger.error(f"导入主题失败: {e}")
            return False

    def _check_system_theme(self):
        """检查系统主题变化（用于自动主题）"""
        try:
            if self.current_theme and self.current_theme.metadata.theme_type == ThemeType.AUTO:
                # 这里可以添加系统主题检测逻辑:
                # 这里可以添加系统主题检测逻辑
                # 例如检查系统是否为深色模式
                pass

        except Exception as e:
            self.logger.error(f"检查系统主题失败: {e}")

    def start_auto_theme_detection(self):
        """启动自动主题检测"""
        self.system_theme_timer.start(5000)  # 每5秒检查一次

    def stop_auto_theme_detection(self):
        """停止自动主题检测"""
        self.system_theme_timer.stop()

    def get_current_theme(self) -> Optional[Theme]:
        """获取当前主题"""
        return self.current_theme

    def get_current_theme_id(self) -> Optional[str]:
        """获取当前主题ID"""
        return self.current_theme_id


class ThemeMarketManager(QObject):
    """主题市场管理器"""

    # 信号定义
    themes_loaded = pyqtSignal(list)  # 主题列表
    theme_downloaded = pyqtSignal(str)  # 主题ID
    download_progress = pyqtSignal(str, int)  # 主题ID, 进度
    download_error = pyqtSignal(str, str)  # 主题ID, 错误信息

    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.ThemeMarketManager')
        self.theme_manager = theme_manager

        # 主题市场配置
        self.market_url = "https://api.timenest.org/themes"  # 示例URL
        self.cache_dir = Path.home() / '.timenest' / 'theme_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 缓存的主题列表
        self.market_themes: List[Dict[str, Any]] = []

    def load_market_themes(self) -> bool:
        """加载市场主题列表"""
        try:
            # 这里应该从实际的API获取主题列表
            # 现在使用模拟数据
            mock_themes = [
                {
                    "id": "material_blue",
                    "name": "Material Blue",
                    "description": "基于Material Design的蓝色主题",
                    "author": "Design Team",
                    "version": "1.2.0",
                    "theme_type": "light",
                    "preview_image": "https://example.com/preview1.png",
                    "download_url": "https://example.com/themes/material_blue.json",
                    "tags": ["material", "blue", "modern"],
                    "downloads": 1250,
                    "rating": 4.8,
                    "created_date": "2024-01-15",
                    "updated_date": "2024-06-20"
                },
                {
                    "id": "dark_purple",
                    "name": "Dark Purple",
                    "description": "优雅的紫色深色主题",
                    "author": "Purple Studio",
                    "version": "1.0.3",
                    "theme_type": "dark",
                    "preview_image": "https://example.com/preview2.png",
                    "download_url": "https://example.com/themes/dark_purple.json",
                    "tags": ["dark", "purple", "elegant"],
                    "downloads": 890,
                    "rating": 4.6,
                    "created_date": "2024-02-10",
                    "updated_date": "2024-05-15"
                }
            ]

            self.market_themes = mock_themes
            self.themes_loaded.emit(mock_themes)

            self.logger.info(f"市场主题列表加载完成，共{len(mock_themes)}个主题")
            return True

        except Exception as e:
            self.logger.error(f"加载市场主题失败: {e}")
            return False

    def download_theme(self, theme_id: str) -> bool:
        """下载主题"""
        try:
            # 查找主题信息
            theme_info = None
            for theme in self.market_themes:
                if theme['id'] == theme_id:
                    theme_info = theme
                    break


            if not theme_info:
                self.logger.error(f"市场中未找到主题: {theme_id}")
                return False

            # 模拟下载过程
            self.download_progress.emit(theme_id, 0)

            # 这里应该实际下载主题文件
            # 现在使用模拟数据
            mock_theme_data = {
                "metadata": {
                    "id": theme_id,
                    "name": theme_info.get('name'),
                    "description": theme_info.get('description'),
                    "author": theme_info.get('author'),
                    "version": theme_info.get('version'),
                    "theme_type": theme_info.get('theme_type'),
                    "preview_image": theme_info.get('preview_image'),
                    "tags": theme_info.get('tags'),
                    "created_date": theme_info.get('created_date'),
                    "updated_date": theme_info.get('updated_date')
                },
                "colors": {
                    "primary": "#1976D2" if theme_id == "material_blue" else "#7B1FA2",
                    "secondary": "#FFC107",
                    "accent": "#FF5722",
                    "background": "#FFFFFF" if theme_info['theme_type'] == "light" else "#121212",
                    "surface": "#F5F5F5" if theme_info['theme_type'] == "light" else "#1E1E1E",
                    "card": "#FFFFFF" if theme_info['theme_type'] == "light" else "#2D2D2D",
                    "text_primary": "#212121" if theme_info['theme_type'] == "light" else "#FFFFFF",
                    "text_secondary": "#757575" if theme_info['theme_type'] == "light" else "#B0B0B0",
                    "text_disabled": "#BDBDBD" if theme_info['theme_type'] == "light" else "#666666",
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "error": "#F44336",
                    "info": "#2196F3",
                    "border": "#E0E0E0" if theme_info['theme_type'] == "light" else "#404040",
                    "divider": "#EEEEEE" if theme_info['theme_type'] == "light" else "#333333"
                },
                "styles": {},
                "fonts": {},
                "animations": {}
            }

            self.download_progress.emit(theme_id, 50)

            # 安装主题
            success = self.theme_manager.install_theme(mock_theme_data)

            if success:
                self.download_progress.emit(theme_id, 100)
                self.theme_downloaded.emit(theme_id)
                self.logger.info(f"主题下载安装成功: {theme_info.get('name')}")
            else:
                self.download_error.emit(theme_id, "安装失败")

            return success

        except Exception as e:
            error_msg = f"下载主题失败: {e}"
            self.logger.error(error_msg)
            self.download_error.emit(theme_id, error_msg)
            return False

    def get_market_themes(self) -> List[Dict[str, Any]]:
        """获取市场主题列表"""
        return self.market_themes

    def search_themes(self, query: str, tags: List[str] = None) -> List[Dict[str, Any]]:
        """搜索主题"""
        try:
            results = []
            query_lower = query.lower()

            for theme in self.market_themes:
                # 搜索名称和描述
                if (query_lower in theme.get('name').lower() or
                    query_lower in theme.get('description').lower() or
                    query_lower in theme.get('author').lower()):

                    # 如果指定了标签，检查标签匹配
                    if tags:
                        theme_tags = [tag.lower() for tag in theme.get('tags', [])]
                        if any(tag.lower() in theme_tags for tag in tags):
                            results.append(theme)
                    else:
                        results.append(theme)

            return results

        except Exception as e:
            self.logger.error(f"搜索主题失败: {e}")
            return []
