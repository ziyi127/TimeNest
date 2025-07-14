#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 版本管理器
统一管理应用版本信息和元数据
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class VersionManager:
    """版本管理器 - 统一管理应用信息"""
    
    _instance = None
    _app_info = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.logger = logging.getLogger(__name__)
            self._config_file = self._find_config_file()
            self._load_app_info()
            self._initialized = True
    
    def _find_config_file(self) -> Path:
        """查找配置文件"""
        # 从当前文件位置向上查找根目录
        current_dir = Path(__file__).parent
        
        # 向上查找，直到找到app_info.json或到达根目录
        for _ in range(5):  # 最多向上查找5级
            config_path = current_dir / "app_info.json"
            if config_path.exists():
                return config_path
            
            parent = current_dir.parent
            if parent == current_dir:  # 已到达根目录
                break
            current_dir = parent
        
        # 如果没找到，尝试项目根目录
        project_root = Path(__file__).parent.parent
        config_path = project_root / "app_info.json"
        
        if not config_path.exists():
            self.logger.warning(f"未找到配置文件 app_info.json，将使用默认配置")
            return None
        
        return config_path
    
    def _load_app_info(self):
        """加载应用信息"""
        if self._config_file and self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._app_info = json.load(f)
                self.logger.info(f"成功加载应用信息: {self._config_file}")
            except Exception as e:
                self.logger.error(f"加载应用信息失败: {e}")
                self._app_info = self._get_default_app_info()
        else:
            self.logger.warning("使用默认应用信息")
            self._app_info = self._get_default_app_info()
    
    def _get_default_app_info(self) -> Dict[str, Any]:
        """获取默认应用信息 - 返回空结构"""
        return {
            "version": {},
            "app": {},
            "author": {},
            "links": {},
            "legal": {},
            "technical": {},
            "features": {},
            "about": {}
        }
    
    def get_version(self) -> Optional[str]:
        """获取版本号"""
        return self._app_info.get("version", {}).get("number")

    def get_version_name(self) -> Optional[str]:
        """获取版本名称"""
        return self._app_info.get("version", {}).get("name")

    def get_full_version(self) -> Optional[str]:
        """获取完整版本信息"""
        version = self.get_version()
        version_name = self.get_version_name()
        if version and version_name:
            return f"{version} {version_name}"
        elif version:
            return version
        else:
            return None

    def get_build_number(self) -> Optional[str]:
        """获取构建号"""
        return self._app_info.get("version", {}).get("build")

    def get_release_date(self) -> Optional[str]:
        """获取发布日期"""
        return self._app_info.get("version", {}).get("release_date")
    
    def get_app_name(self) -> Optional[str]:
        """获取应用名称"""
        return self._app_info.get("app", {}).get("name")

    def get_app_display_name(self) -> Optional[str]:
        """获取应用显示名称"""
        return self._app_info.get("app", {}).get("display_name")

    def get_app_description(self) -> Optional[str]:
        """获取应用描述"""
        return self._app_info.get("app", {}).get("description")

    def get_app_slogan(self) -> Optional[str]:
        """获取应用标语"""
        return self._app_info.get("app", {}).get("slogan")

    def get_author_name(self) -> Optional[str]:
        """获取作者名称"""
        return self._app_info.get("author", {}).get("name")

    def get_author_display_name(self) -> Optional[str]:
        """获取作者显示名称"""
        return self._app_info.get("author", {}).get("display_name")

    def get_author_email(self) -> Optional[str]:
        """获取作者邮箱"""
        return self._app_info.get("author", {}).get("email")
    
    def get_website_url(self) -> Optional[str]:
        """获取网站链接"""
        return self._app_info.get("links", {}).get("website")

    def get_repository_url(self) -> Optional[str]:
        """获取仓库链接"""
        return self._app_info.get("links", {}).get("repository")

    def get_issues_url(self) -> Optional[str]:
        """获取问题反馈链接"""
        return self._app_info.get("links", {}).get("issues")

    def get_releases_url(self) -> Optional[str]:
        """获取发布页面链接"""
        return self._app_info.get("links", {}).get("releases")

    def get_license(self) -> Optional[str]:
        """获取许可证"""
        return self._app_info.get("legal", {}).get("license")

    def get_copyright(self) -> Optional[str]:
        """获取版权信息"""
        return self._app_info.get("legal", {}).get("copyright")
    
    def get_supported_platforms(self) -> Optional[list]:
        """获取支持的平台"""
        return self._app_info.get("technical", {}).get("supported_platforms")

    def get_main_features(self) -> Optional[list]:
        """获取主要功能"""
        return self._app_info.get("features", {}).get("main_features")

    def get_contributors(self) -> Optional[str]:
        """获取贡献者信息"""
        return self._app_info.get("about", {}).get("contributors")

    def get_thanks_list(self) -> Optional[list]:
        """获取致谢列表"""
        return self._app_info.get("about", {}).get("thanks")
    
    def get_all_info(self) -> Dict[str, Any]:
        """获取所有应用信息"""
        return self._app_info.copy() if self._app_info else {}
    
    def reload_config(self):
        """重新加载配置"""
        self._load_app_info()
        self.logger.info("应用信息已重新加载")


# 创建全局实例
version_manager = VersionManager()


# 便捷函数
def get_version() -> str:
    """获取版本号"""
    return version_manager.get_version()


def get_full_version() -> str:
    """获取完整版本信息"""
    return version_manager.get_full_version()


def get_app_name() -> str:
    """获取应用名称"""
    return version_manager.get_app_name()


def get_app_info() -> Dict[str, Any]:
    """获取所有应用信息"""
    return version_manager.get_all_info()
