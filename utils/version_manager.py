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
            try:
                self.logger = logging.getLogger(__name__)
            except:
                self.logger = None
            self._config_file = self._find_config_file()
            self._load_app_info()
            self._initialized = True
    
    def _find_config_file(self) -> Optional[Path]:
        """查找配置文件"""
        # 尝试多个可能的位置
        possible_paths = [
            # 项目根目录
            Path(__file__).parent.parent / "app_info.json",
            # 当前工作目录
            Path.cwd() / "app_info.json",
            # 脚本所在目录
            Path(__file__).parent / "app_info.json",
        ]

        for config_path in possible_paths:
            if config_path.exists():
                return config_path

        # 如果都没找到，返回None
        return None
    
    def _load_app_info(self):
        """加载应用信息"""
        self._app_info = self._get_default_app_info()  # 先设置默认值

        if self._config_file and self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded_info = json.load(f)
                    self._app_info = loaded_info
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.info(f"成功加载应用信息: {self._config_file}")
            except Exception as e:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.error(f"加载应用信息失败: {e}")
        else:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning("未找到配置文件，使用默认配置")
    
    def _get_default_app_info(self) -> Dict[str, Any]:
        """获取默认应用信息"""
        return {
            "version": {
                "number": "null",
                "name": "null",
                "build": "null",
                "release_date": "null",
                "full_version": "null"
            },
            "app": {
                "name": "null",
                "display_name": "null",
                "description": "null",
                "slogan": "null"
            },
            "author": {
                "name": "null",
                "display_name": "null",
                "email": "null"
            },
            "links": {
                "website": "null",
                "repository": "null",
                "issues": "null",
                "releases": "null"
            },
            "legal": {
                "license": "null",
                "copyright": "null"
            },
            "technical": {
                "supported_platforms": ["null"]
            },
            "features": {
                "main_features": ["null"]
            },
            "about": {
                "contributors": "null",
                "thanks": ["null"]
            }
        }
    
    def get_version(self) -> str:
        """获取版本号"""
        return self._app_info.get("version", {}).get("number", "null")

    def get_version_name(self) -> str:
        """获取版本名称"""
        return self._app_info.get("version", {}).get("name", "null")

    def get_full_version(self) -> str:
        """获取完整版本信息"""
        full_version = self._app_info.get("version", {}).get("full_version")
        if full_version:
            return full_version

        version = self.get_version()
        version_name = self.get_version_name()
        if version != "null" and version_name != "null":
            return f"{version} {version_name}"
        elif version != "null":
            return version
        else:
            return "null"

    def get_build_number(self) -> str:
        """获取构建号"""
        return self._app_info.get("version", {}).get("build", "null")

    def get_release_date(self) -> str:
        """获取发布日期"""
        return self._app_info.get("version", {}).get("release_date", "null")
    
    def get_app_name(self) -> str:
        """获取应用名称"""
        return self._app_info.get("app", {}).get("name", "null")

    def get_app_display_name(self) -> str:
        """获取应用显示名称"""
        return self._app_info.get("app", {}).get("display_name", "null")

    def get_app_description(self) -> str:
        """获取应用描述"""
        return self._app_info.get("app", {}).get("description", "null")

    def get_app_slogan(self) -> str:
        """获取应用标语"""
        return self._app_info.get("app", {}).get("slogan", "null")

    def get_author_name(self) -> str:
        """获取作者名称"""
        return self._app_info.get("author", {}).get("name", "null")

    def get_author_display_name(self) -> str:
        """获取作者显示名称"""
        return self._app_info.get("author", {}).get("display_name", "null")

    def get_author_email(self) -> str:
        """获取作者邮箱"""
        return self._app_info.get("author", {}).get("email", "null")
    
    def get_website_url(self) -> str:
        """获取网站链接"""
        return self._app_info.get("links", {}).get("website", "null")

    def get_repository_url(self) -> str:
        """获取仓库链接"""
        return self._app_info.get("links", {}).get("repository", "null")

    def get_issues_url(self) -> str:
        """获取问题反馈链接"""
        return self._app_info.get("links", {}).get("issues", "null")

    def get_releases_url(self) -> str:
        """获取发布页面链接"""
        return self._app_info.get("links", {}).get("releases", "null")

    def get_license(self) -> str:
        """获取许可证"""
        return self._app_info.get("legal", {}).get("license", "null")

    def get_copyright(self) -> str:
        """获取版权信息"""
        return self._app_info.get("legal", {}).get("copyright", "null")
    
    def get_supported_platforms(self) -> list:
        """获取支持的平台"""
        return self._app_info.get("technical", {}).get("supported_platforms", ["null"])

    def get_main_features(self) -> list:
        """获取主要功能"""
        return self._app_info.get("features", {}).get("main_features", ["null"])

    def get_contributors(self) -> str:
        """获取贡献者信息"""
        return self._app_info.get("about", {}).get("contributors", "null")

    def get_thanks_list(self) -> list:
        """获取致谢列表"""
        return self._app_info.get("about", {}).get("thanks", ["null"])
    
    def get_all_info(self) -> Dict[str, Any]:
        """获取所有应用信息"""
        return self._app_info.copy() if self._app_info else {}
    
    def reload_config(self):
        """重新加载配置"""
        self._load_app_info()
        if hasattr(self, 'logger') and self.logger:
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
