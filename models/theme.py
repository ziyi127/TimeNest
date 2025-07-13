#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 主题数据模型
定义主题相关的数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ThemeType(Enum):
    """主题类型枚举"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    CUSTOM = "custom"


class ThemeCategory(Enum):
    """主题分类枚举"""
    SYSTEM = "system"
    COMMUNITY = "community"
    PREMIUM = "premium"
    CUSTOM = "custom"


@dataclass
class ThemeColors:
    """主题颜色配置"""
    primary: str = "#007ACC"
    secondary: str = "#5C6BC0"
    background: str = "#FFFFFF"
    surface: str = "#F5F5F5"
    text_primary: str = "#212121"
    text_secondary: str = "#757575"
    accent: str = "#FF4081"
    success: str = "#4CAF50"
    warning: str = "#FF9800"
    error: str = "#F44336"
    border: str = "#E0E0E0"
    shadow: str = "#00000020"
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            'primary': self.primary,
            'secondary': self.secondary,
            'background': self.background,
            'surface': self.surface,
            'text_primary': self.text_primary,
            'text_secondary': self.text_secondary,
            'accent': self.accent,
            'success': self.success,
            'warning': self.warning,
            'error': self.error,
            'border': self.border,
            'shadow': self.shadow
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ThemeColors':
        """从字典创建"""
        return cls(**data)


@dataclass
class ThemeFont:
    """主题字体配置"""
    family: str = "Arial"
    size: int = 12
    weight: str = "normal"  # normal, bold, lighter
    style: str = "normal"   # normal, italic
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'family': self.family,
            'size': self.size,
            'weight': self.weight,
            'style': self.style
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeFont':
        """从字典创建"""
        return cls(**data)


@dataclass
class ThemeSpacing:
    """主题间距配置"""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    
    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            'xs': self.xs,
            'sm': self.sm,
            'md': self.md,
            'lg': self.lg,
            'xl': self.xl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'ThemeSpacing':
        """从字典创建"""
        return cls(**data)


@dataclass
class Theme:
    """主题数据模型"""
    id: str
    name: str
    description: str = ""
    type: ThemeType = ThemeType.LIGHT
    category: ThemeCategory = ThemeCategory.CUSTOM
    colors: ThemeColors = field(default_factory=ThemeColors)
    font: ThemeFont = field(default_factory=ThemeFont)
    spacing: ThemeSpacing = field(default_factory=ThemeSpacing)
    author: str = ""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    preview_image: Optional[str] = None
    custom_css: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'category': self.category.value,
            'colors': self.colors.to_dict(),
            'font': self.font.to_dict(),
            'spacing': self.spacing.to_dict(),
            'author': self.author,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'preview_image': self.preview_image,
            'custom_css': self.custom_css,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """从字典创建"""
        # 处理嵌套对象
        colors_data = data.get('colors', {})
        font_data = data.get('font', {})
        spacing_data = data.get('spacing', {})
        
        # 处理日期
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.now()
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description', ''),
            type=ThemeType(data.get('type', 'light')),
            category=ThemeCategory(data.get('category', 'custom')),
            colors=ThemeColors.from_dict(colors_data),
            font=ThemeFont.from_dict(font_data),
            spacing=ThemeSpacing.from_dict(spacing_data),
            author=data.get('author', ''),
            version=data.get('version', '1.0.0'),
            created_at=created_at,
            updated_at=updated_at,
            preview_image=data.get('preview_image'),
            custom_css=data.get('custom_css', ''),
            metadata=data.get('metadata', {})
        )
    
    def get_css_variables(self) -> str:
        """获取CSS变量定义"""
        css_vars = []
        
        # 颜色变量
        for key, value in self.colors.to_dict().items():
            css_vars.append(f"--color-{key.replace('_', '-')}: {value};")
        
        # 字体变量
        css_vars.append(f"--font-family: {self.font.family};")
        css_vars.append(f"--font-size: {self.font.size}px;")
        css_vars.append(f"--font-weight: {self.font.weight};")
        css_vars.append(f"--font-style: {self.font.style};")
        
        # 间距变量
        for key, value in self.spacing.to_dict().items():
            css_vars.append(f"--spacing-{key}: {value}px;")
        
        return "\n".join([":root {"] + [f"  {var}" for var in css_vars] + ["}"])


@dataclass
class ThemeSettings:
    """主题设置数据模型"""
    current_theme_id: str = "default"
    auto_switch_enabled: bool = False
    light_theme_id: str = "default_light"
    dark_theme_id: str = "default_dark"
    switch_time_light: str = "06:00"  # 切换到浅色主题的时间
    switch_time_dark: str = "18:00"   # 切换到深色主题的时间
    follow_system: bool = True
    custom_themes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'current_theme_id': self.current_theme_id,
            'auto_switch_enabled': self.auto_switch_enabled,
            'light_theme_id': self.light_theme_id,
            'dark_theme_id': self.dark_theme_id,
            'switch_time_light': self.switch_time_light,
            'switch_time_dark': self.switch_time_dark,
            'follow_system': self.follow_system,
            'custom_themes': self.custom_themes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeSettings':
        """从字典创建"""
        return cls(**data)


# 预定义主题
DEFAULT_LIGHT_THEME = Theme(
    id="default_light",
    name="默认浅色",
    description="系统默认浅色主题",
    type=ThemeType.LIGHT,
    category=ThemeCategory.SYSTEM,
    colors=ThemeColors(),
    author="TimeNest Team"
)

DEFAULT_DARK_THEME = Theme(
    id="default_dark",
    name="默认深色",
    description="系统默认深色主题",
    type=ThemeType.DARK,
    category=ThemeCategory.SYSTEM,
    colors=ThemeColors(
        primary="#BB86FC",
        secondary="#03DAC6",
        background="#121212",
        surface="#1E1E1E",
        text_primary="#FFFFFF",
        text_secondary="#B3B3B3",
        accent="#03DAC6",
        border="#333333",
        shadow="#00000040"
    ),
    author="TimeNest Team"
)


# 导出所有模型
__all__ = [
    'ThemeType',
    'ThemeCategory',
    'ThemeColors',
    'ThemeFont',
    'ThemeSpacing',
    'Theme',
    'ThemeSettings',
    'DEFAULT_LIGHT_THEME',
    'DEFAULT_DARK_THEME'
]
