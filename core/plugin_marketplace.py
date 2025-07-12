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
TimeNest 插件商城管理器
负责插件的下载、安装、更新等功能
"""

import os
import json
import logging
import requests
import zipfile
import tempfile
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer


class PluginMarketplaceStatus(Enum):
    """插件商城状态"""
    OFFLINE = "offline"
    ONLINE = "online"
    ERROR = "error"
    CONNECTING = "connecting"


@dataclass
class MarketplacePlugin:
    """商城插件信息"""
    id: str
    name: str
    version: str
    description: str
    author: str
    category: str
    download_url: str
    homepage: str = ""
    repository: str = ""
    license: str = ""
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    size: int = 0
    checksum: str = ""
    dependencies: List[str] = field(default_factory=list)
    min_app_version: str = "1.0.0"
    max_app_version: str = ""
    screenshots: List[str] = field(default_factory=list)
    changelog: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketplacePlugin':
        """从字典创建插件信息"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            version=data.get('version', ''),
            description=data.get('description', ''),
            author=data.get('author', ''),
            category=data.get('category', ''),
            download_url=data.get('download_url', ''),
            homepage=data.get('homepage', ''),
            repository=data.get('repository', ''),
            license=data.get('license', ''),
            tags=data.get('tags', []),
            downloads=data.get('downloads', 0),
            rating=data.get('rating', 0.0),
            size=data.get('size', 0),
            checksum=data.get('checksum', ''),
            dependencies=data.get('dependencies', []),
            min_app_version=data.get('min_app_version', '1.0.0'),
            max_app_version=data.get('max_app_version', ''),
            screenshots=data.get('screenshots', []),
            changelog=data.get('changelog', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )


class PluginDownloader(QThread):
    """插件下载器"""
    
    # 信号定义
    progress_updated = pyqtSignal(int)  # 下载进度
    download_completed = pyqtSignal(str)  # 下载完成，返回文件路径
    download_failed = pyqtSignal(str)  # 下载失败，返回错误信息
    
    def __init__(self, plugin: MarketplacePlugin, download_dir: Path):
        super().__init__()
        self.plugin = plugin
        self.download_dir = download_dir
        self.logger = logging.getLogger(f'{__name__}.PluginDownloader')
        self._cancelled = False
    
    def run(self):
        """执行下载"""
        try:
            self.logger.info(f"开始下载插件: {self.plugin.name}")
            
            # 创建下载目录
            self.download_dir.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            response = requests.get(self.plugin.download_url, stream=True)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载文件
            filename = f"{self.plugin.id}-{self.plugin.version}.zip"
            file_path = self.download_dir / filename
            
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._cancelled:
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 更新进度
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            # 验证文件完整性
            if self.plugin.checksum:
                if not self._verify_checksum(file_path, self.plugin.checksum):
                    self.download_failed.emit("文件校验失败")
                    return
            
            self.download_completed.emit(str(file_path))
            self.logger.info(f"插件下载完成: {self.plugin.name}")
            
        except Exception as e:
            error_msg = f"下载插件失败: {e}"
            self.logger.error(error_msg)
            self.download_failed.emit(error_msg)
    
    def cancel(self):
        """取消下载"""
        self._cancelled = True
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """验证文件校验和"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum == expected_checksum
            
        except Exception as e:
            self.logger.error(f"验证校验和失败: {e}")
            return False


class PluginMarketplace(QObject):
    """插件商城管理器"""
    
    # 信号定义
    status_changed = pyqtSignal(str)  # 状态变化
    plugins_updated = pyqtSignal()  # 插件列表更新
    plugin_downloaded = pyqtSignal(str)  # 插件下载完成
    plugin_installed = pyqtSignal(str)  # 插件安装完成
    plugin_install_failed = pyqtSignal(str, str)  # 插件安装失败
    download_progress = pyqtSignal(str, int)  # 下载进度
    
    def __init__(self, plugin_manager, config_manager=None):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginMarketplace')
        self.plugin_manager = plugin_manager
        self.config_manager = config_manager
        
        # 商城配置
        self.marketplace_url = "https://github.com/ziyi127/TimeNest-Store"
        self.api_base_url = "https://api.github.com/repos/ziyi127/TimeNest-Store"
        self.raw_base_url = "https://raw.githubusercontent.com/ziyi127/TimeNest-Store/main"
        
        # 状态管理
        self.status = PluginMarketplaceStatus.OFFLINE
        self.available_plugins: List[MarketplacePlugin] = []
        self.featured_plugins: List[MarketplacePlugin] = []
        
        # 下载管理
        self.active_downloads: Dict[str, PluginDownloader] = {}
        self.download_dir = Path("downloads/plugins")
        
        # 缓存管理
        self.cache_file = Path("cache/marketplace_cache.json")
        self.cache_expiry = 3600  # 1小时
        
        # 初始化
        self._load_config()
        self._load_cache()
    
    def _load_config(self):
        """加载商城配置"""
        try:
            if self.config_manager:
                # 从配置管理器加载商城配置
                marketplace_config = self.config_manager.get_config(
                    'marketplace', {}
                )
                
                # 更新商城URL
                if 'marketplace_url' in marketplace_config:
                    self.marketplace_url = marketplace_config.get('marketplace_url')
                    self.api_base_url = f"https://api.github.com/repos/{marketplace_config.get('marketplace_url').split('/')[-2:]}"
                    self.raw_base_url = f"https://raw.githubusercontent.com/{marketplace_config.get('marketplace_url').split('/')[-2:]}/main"
                
                # 更新缓存过期时间
                if 'cache_expiry' in marketplace_config:
                    self.cache_expiry = marketplace_config.get('cache_expiry')
            
            self.logger.info(f"插件商城配置加载完成: {self.marketplace_url}")
            
        except Exception as e:
            self.logger.error(f"加载商城配置失败: {e}")
    
    def _load_cache(self):
        """加载缓存"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # 检查缓存是否过期
                import time
                cache_time = cache_data.get('timestamp', 0)
                if time.time() - cache_time < self.cache_expiry:
                    # 加载缓存的插件列表
                    plugins_data = cache_data.get('plugins', [])
                    self.available_plugins = [
                        MarketplacePlugin.from_dict(plugin_data)
                        for plugin_data in plugins_data
                    ]
                    
                    self.logger.info(f"从缓存加载了 {len(self.available_plugins)} 个插件")
                    self.plugins_updated.emit()
                    return
            
            # 缓存不存在或已过期，刷新插件列表
            self.refresh_plugins()
            
        except Exception as e:
            self.logger.error(f"加载缓存失败: {e}")
            self.refresh_plugins()
    
    def _save_cache(self):
        """保存缓存"""
        try:
            import time
            cache_data = {
                'timestamp': time.time(),
                'plugins': [
                    {
                        'id': plugin.id,
                        'name': plugin.name,
                        'version': plugin.version,
                        'description': plugin.description,
                        'author': plugin.author,
                        'category': plugin.category,
                        'download_url': plugin.download_url,
                        'homepage': plugin.homepage,
                        'repository': plugin.repository,
                        'license': plugin.license,
                        'tags': plugin.tags,
                        'downloads': plugin.downloads,
                        'rating': plugin.rating,
                        'size': plugin.size,
                        'checksum': plugin.checksum,
                        'dependencies': plugin.dependencies,
                        'min_app_version': plugin.min_app_version,
                        'max_app_version': plugin.max_app_version,
                        'screenshots': plugin.screenshots,
                        'changelog': plugin.changelog,
                        'created_at': plugin.created_at,
                        'updated_at': plugin.updated_at
                    }
                    for plugin in self.available_plugins
                ]
            }
            
            # 确保缓存目录存在
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("缓存保存成功")
            
        except Exception as e:
            self.logger.error(f"保存缓存失败: {e}")
    
    def refresh_plugins(self):
        """刷新插件列表"""
        try:
            self.status = PluginMarketplaceStatus.CONNECTING
            self.status_changed.emit(self.status.value)
            
            # 获取插件列表
            plugins_url = f"{self.raw_base_url}/plugins.json"
            response = requests.get(plugins_url, timeout=10)
            response.raise_for_status()
            
            plugins_data = response.json()
            self.available_plugins = [
                MarketplacePlugin.from_dict(plugin_data)
                for plugin_data in plugins_data.get('plugins', [])
            ]
            
            # 获取推荐插件
            featured_ids = plugins_data.get('featured', [])
            self.featured_plugins = [
                plugin for plugin in self.available_plugins
                if plugin.id in featured_ids
            ]
            
            self.status = PluginMarketplaceStatus.ONLINE
            self.status_changed.emit(self.status.value)
            
            # 保存缓存
            self._save_cache()
            
            # 发出更新信号
            self.plugins_updated.emit()
            
            self.logger.info(f"插件列表刷新完成，共 {len(self.available_plugins)} 个插件")

        except Exception as e:
            error_msg = f"刷新插件列表失败: {e}"
            self.logger.error(error_msg)
            self.status = PluginMarketplaceStatus.ERROR
            self.status_changed.emit(self.status.value)

    def get_available_plugins(self) -> List[MarketplacePlugin]:
        """获取可用插件列表"""
        return self.available_plugins

    def get_featured_plugins(self) -> List[MarketplacePlugin]:
        """获取推荐插件列表"""
        return self.featured_plugins

    def search_plugins(self, query: str, category: str = None) -> List[MarketplacePlugin]:
        """搜索插件"""
        try:
            results = []
            query_lower = query.lower()

            for plugin in self.available_plugins:
                # 检查分类过滤
                if category and plugin.category != category:
                    continue

                # 检查搜索关键词
                if (query_lower in plugin.name.lower() or
                    query_lower in plugin.description.lower() or
                    query_lower in plugin.author.lower() or
                    any(query_lower in tag.lower() for tag in plugin.tags)):
                    results.append(plugin)

            return results

        except Exception as e:
            self.logger.error(f"搜索插件失败: {e}")
            return []

    def get_plugin_by_id(self, plugin_id: str) -> Optional[MarketplacePlugin]:
        """根据ID获取插件"""
        for plugin in self.available_plugins:
            if plugin.id == plugin_id:
                return plugin
        return None

    def download_plugin(self, plugin_id: str) -> bool:
        """下载插件"""
        try:
            plugin = self.get_plugin_by_id(plugin_id)
            if not plugin:
                self.logger.error(f"插件不存在: {plugin_id}")
                return False

            # 检查是否已在下载
            if plugin_id in self.active_downloads:
                self.logger.warning(f"插件正在下载中: {plugin_id}")
                return False

            # 创建下载器
            downloader = PluginDownloader(plugin, self.download_dir)

            # 连接信号
            downloader.progress_updated.connect(
                lambda progress: self.download_progress.emit(plugin_id, progress)
            )
            downloader.download_completed.connect(
                lambda file_path: self._on_download_completed(plugin_id, file_path)
            )
            downloader.download_failed.connect(
                lambda error: self._on_download_failed(plugin_id, error)
            )

            # 开始下载
            self.active_downloads[plugin_id] = downloader
            downloader.start()

            self.logger.info(f"开始下载插件: {plugin.name}")
            return True

        except Exception as e:
            error_msg = f"下载插件失败: {e}"
            self.logger.error(error_msg)
            self.plugin_install_failed.emit(plugin_id, error_msg)
            return False

    def _on_download_completed(self, plugin_id: str, file_path: str):
        """下载完成处理"""
        try:
            # 移除下载器
            if plugin_id in self.active_downloads:
                del self.active_downloads[plugin_id]

            # 发出下载完成信号
            self.plugin_downloaded.emit(plugin_id)

            # 自动安装插件
            self.install_plugin(plugin_id, file_path)

        except Exception as e:
            self.logger.error(f"处理下载完成失败: {e}")

    def _on_download_failed(self, plugin_id: str, error: str):
        """下载失败处理"""
        try:
            # 移除下载器
            if plugin_id in self.active_downloads:
                del self.active_downloads[plugin_id]

            # 发出安装失败信号
            self.plugin_install_failed.emit(plugin_id, error)

        except Exception as e:
            self.logger.error(f"处理下载失败失败: {e}")

    def install_plugin(self, plugin_id: str, file_path: str) -> bool:
        """安装插件"""
        try:
            plugin = self.get_plugin_by_id(plugin_id)
            if not plugin:
                self.logger.error(f"插件不存在: {plugin_id}")
                return False

            # 解压插件文件
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 安装插件
                if self.plugin_manager:
                    success = self.plugin_manager.install_plugin_from_path(temp_dir)
                    if success:
                        self.plugin_installed.emit(plugin_id)
                        self.logger.info(f"插件安装成功: {plugin.name}")
                        return True
                    else:
                        self.plugin_install_failed.emit(plugin_id, "插件安装失败")
                        return False
                else:
                    self.logger.error("插件管理器不可用")
                    return False

        except Exception as e:
            error_msg = f"安装插件失败: {e}"
            self.logger.error(error_msg)
            self.plugin_install_failed.emit(plugin_id, error_msg)
            return False

    def cancel_download(self, plugin_id: str):
        """取消下载"""
        if plugin_id in self.active_downloads:
            self.active_downloads[plugin_id].cancel()
            del self.active_downloads[plugin_id]
            self.logger.info(f"取消下载插件: {plugin_id}")

    def get_download_progress(self, plugin_id: str) -> int:
        """获取下载进度"""
        if plugin_id in self.active_downloads:
            # 这里可以实现获取具体进度的逻辑
            return 0
        return -1

    def is_downloading(self, plugin_id: str) -> bool:
        """检查是否正在下载"""
        return plugin_id in self.active_downloads

    def get_status(self) -> PluginMarketplaceStatus:
        """获取商城状态"""
        return self.status

    def cleanup(self):
        """清理资源"""
        # 取消所有下载
        for plugin_id in list(self.active_downloads.keys()):
            self.cancel_download(plugin_id)
        
        self.logger.info("插件商城清理完成")
