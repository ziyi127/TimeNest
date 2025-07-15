#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 主题市场
支持在线下载和管理主题
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread, QTimer
from PySide6.QtWidgets import QMessageBox

@dataclass
class ThemeInfo:
    """主题信息"""
    id: str
    name: str
    author: str
    version: str
    description: str
    preview_url: str
    download_url: str
    tags: List[str]
    downloads: int = 0
    stars: int = 0
    created_at: str = ""
    updated_at: str = ""
    file_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeInfo':
        return cls(**data)


class ThemeDownloader(QThread):
    """主题下载器"""
    
    download_progress = Signal(int)  # 下载进度
    download_finished = Signal(str, bool)  # 主题ID, 是否成功
    download_error = Signal(str, str)  # 主题ID, 错误信息
    
    def __init__(self, theme_info: ThemeInfo, download_path: Path):
        super().__init__()
        self.theme_info = theme_info
        self.download_path = download_path
        self.logger = logging.getLogger(f'{__name__}.ThemeDownloader')
    
    def run(self):
        """执行下载"""
        try:
            self.logger.info(f"开始下载主题: {self.theme_info.name}")
            
            response = requests.get(self.theme_info.download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # 确保下载目录存在
            self.download_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                        
                            progress = int((downloaded / total_size) * 100)
                            self.download_progress.emit(progress)
            
            self.logger.info(f"主题下载完成: {self.theme_info.name}")
            self.download_finished.emit(self.theme_info.id, True)
            
        except Exception as e:
            self.logger.error(f"下载主题失败: {e}")
            self.download_error.emit(self.theme_info.id, str(e))


class ThemeMarketplace(QObject):
    """主题市场管理器"""
    
    themes_loaded = Signal(list)  # 主题列表加载完成
    theme_installed = Signal(str)  # 主题安装完成
    theme_uninstalled = Signal(str)  # 主题卸载完成
    error_occurred = Signal(str)  # 错误发生
    
    def __init__(self, config_manager, theme_manager):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.ThemeMarketplace')
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        
        # 主题市场配置
        self.marketplace_url = "https://api.timenest.themes.com/v1"  # 示例URL
        self.themes_cache: List[ThemeInfo] = []
        self.installed_themes: Dict[str, ThemeInfo] = {}
        
        # 下载管理
        self.active_downloads: Dict[str, ThemeDownloader] = {}
        
        # 缓存刷新定时器
        self.cache_timer = QTimer()
        self.cache_timer.timeout.connect(self.refresh_themes_cache)
        self.cache_timer.start(300000)  # 5分钟刷新一次
        
        self._load_installed_themes()
    
    def _load_installed_themes(self):
        """加载已安装的主题"""
        try:
            installed_data = self.config_manager.get_config('installed_themes', {}, 'component')
            for theme_id, theme_data in installed_data.items():
                self.installed_themes[theme_id] = ThemeInfo.from_dict(theme_data)
            
            self.logger.info(f"加载了 {len(self.installed_themes)} 个已安装主题")
            
        except Exception as e:
            self.logger.error(f"加载已安装主题失败: {e}")
    
    def _save_installed_themes(self):
        """保存已安装主题信息"""
        try:
            installed_data = {
                theme_id: theme_info.to_dict()
                for theme_id, theme_info in self.installed_themes.items()
            }
            self.config_manager.set_config('installed_themes', installed_data, 'component')
            self.config_manager.save_all_configs()
            
        except Exception as e:
            self.logger.error(f"保存已安装主题失败: {e}")
    
    def fetch_themes(self, category: str = "all", sort_by: str = "downloads") -> None:
        """获取主题列表"""
        try:
            self.logger.info("正在获取主题市场数据...")
            
            # 构建请求URL
            params = {
                'category': category,
                'sort': sort_by,
                'limit': 50
            }
            
            # 这里使用模拟数据，实际应该从API获取
            mock_themes = self._get_mock_themes()
            self.themes_cache = mock_themes
            self.themes_loaded.emit(mock_themes)
            
            self.logger.info(f"获取到 {len(mock_themes)} 个主题")
            
        except Exception as e:
            self.logger.error(f"获取主题列表失败: {e}")
            self.error_occurred.emit(f"获取主题失败: {e}")
    
    def _get_mock_themes(self) -> List[ThemeInfo]:
        """获取模拟主题数据"""
        return [
            ThemeInfo(
                id="dark_modern",
                name="现代深色",
                author="TimeNest Team",
                version="1.0.0",
                description="现代风格的深色主题，适合夜间使用",
                preview_url="https://example.com/preview1.png",
                download_url="https://example.com/dark_modern.zip",
                tags=["深色", "现代", "简约"],
                downloads=1250,
                stars=89,
                created_at="2024-01-15",
                updated_at="2024-03-20",
                file_size=2048576
            ),
            ThemeInfo(
                id="light_elegant",
                name="优雅浅色",
                author="Design Studio",
                version="1.2.0",
                description="优雅的浅色主题，清新简洁",
                preview_url="https://example.com/preview2.png",
                download_url="https://example.com/light_elegant.zip",
                tags=["浅色", "优雅", "清新"],
                downloads=980,
                stars=76,
                created_at="2024-02-01",
                updated_at="2024-03-15",
                file_size=1843200
            ),
            ThemeInfo(
                id="colorful_vibrant",
                name="活力彩色",
                author="ColorMaster",
                version="2.0.0",
                description="充满活力的彩色主题，适合年轻用户",
                preview_url="https://example.com/preview3.png",
                download_url="https://example.com/colorful_vibrant.zip",
                tags=["彩色", "活力", "年轻"],
                downloads=756,
                stars=92,
                created_at="2024-01-20",
                updated_at="2024-03-25",
                file_size=3145728
            )
        ]
    
    def refresh_themes_cache(self):
        """刷新主题缓存"""
        self.fetch_themes()
    
    def download_theme(self, theme_info: ThemeInfo) -> bool:
        """下载主题"""
        try:
            if theme_info.id in self.active_downloads:
                self.logger.warning(f"主题 {theme_info.name} 正在下载中")
                return False
            
            # 设置下载路径
            themes_dir = Path("themes")
            download_path = themes_dir / f"{theme_info.id}.zip"
            
            # 创建下载器
            downloader = ThemeDownloader(theme_info, download_path)
            downloader.download_finished.connect(self._on_download_finished)
            downloader.download_error.connect(self._on_download_error)
            
            self.active_downloads[theme_info.id] = downloader
            downloader.start()
            
            self.logger.info(f"开始下载主题: {theme_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"启动主题下载失败: {e}")
            self.error_occurred.emit(f"下载失败: {e}")
            return False
    
    def _on_download_finished(self, theme_id: str, success: bool):
        """下载完成处理"""
        if theme_id in self.active_downloads:
            downloader = self.active_downloads.pop(theme_id)
            downloader.deleteLater()
        
        
        if success and hasattr(self, "logger"):
            self.logger.info(f"主题 {theme_id} 下载成功")
            self._install_theme(theme_id)
        else:
            self.logger.error(f"主题 {theme_id} 下载失败")
    
    def _on_download_error(self, theme_id: str, error_msg: str):
        """下载错误处理"""
        if theme_id in self.active_downloads:
            downloader = self.active_downloads.pop(theme_id)
            downloader.deleteLater()
        
        self.logger.error(f"主题 {theme_id} 下载错误: {error_msg}")
        self.error_occurred.emit(f"下载失败: {error_msg}")
    
    def _install_theme(self, theme_id: str):
        """安装主题"""
        try:
            # 查找主题信息
            theme_info = None
            for theme in self.themes_cache:
                if theme.id == theme_id:
                    theme_info = theme
                    break
            
            
            if not theme_info:
                raise ValueError(f"未找到主题信息: {theme_id}")
            
            # 解压和安装主题文件（这里简化处理）
            themes_dir = Path("themes")
            theme_path = themes_dir / f"{theme_id}.zip"
            
            
            if theme_path.exists():
                # 标记为已安装:
            
                # 标记为已安装
                self.installed_themes[theme_id] = theme_info
                self._save_installed_themes()
                
                # 通知主题管理器
                if hasattr(self.theme_manager, 'install_theme'):
                    self.theme_manager.install_theme(theme_path)
                
                self.theme_installed.emit(theme_id)
                self.logger.info(f"主题 {theme_info.name} 安装成功")
            else:
                raise FileNotFoundError(f"主题文件不存在: {theme_path}")
                
        except Exception as e:
            self.logger.error(f"安装主题失败: {e}")
            self.error_occurred.emit(f"安装失败: {e}")
    
    def uninstall_theme(self, theme_id: str) -> bool:
        """卸载主题"""
        try:
            if theme_id not in self.installed_themes:
                self.logger.warning(f"主题 {theme_id} 未安装")
                return False
            
            theme_info = self.installed_themes[theme_id]
            
            # 删除主题文件
            themes_dir = Path("themes")
            theme_path = themes_dir / f"{theme_id}.zip"
            if theme_path.exists():
                theme_path.unlink()
            
            # 从已安装列表中移除
            del self.installed_themes[theme_id]
            self._save_installed_themes()
            
            # 通知主题管理器
            if hasattr(self.theme_manager, 'uninstall_theme'):
                self.theme_manager.uninstall_theme(theme_id)
            
            self.theme_uninstalled.emit(theme_id)
            self.logger.info(f"主题 {theme_info.name} 卸载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"卸载主题失败: {e}")
            self.error_occurred.emit(f"卸载失败: {e}")
            return False
    
    def is_theme_installed(self, theme_id: str) -> bool:
        """检查主题是否已安装"""
        return theme_id in self.installed_themes
    
    def get_installed_themes(self) -> List[ThemeInfo]:
        """获取已安装主题列表"""
        return list(self.installed_themes.values())
    
    def search_themes(self, query: str) -> List[ThemeInfo]:
        """搜索主题"""
        query = query.lower()
        results = []
        
        for theme in self.themes_cache:
            if (query in theme.name.lower() or
                query in theme.description.lower() or
                query in theme.author.lower() or
                any(query in tag.lower() for tag in theme.tags)):
                results.append(theme)
        
        return results
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止所有下载
            for downloader in self.active_downloads.values():
                downloader.terminate()
                downloader.wait()
                downloader.deleteLater()
            
            self.active_downloads.clear()
            
            # 停止定时器
            if self.cache_timer.isActive():
                self.cache_timer.stop()
            
            self.logger.info("主题市场清理完成")
            
        except Exception as e:
            self.logger.error(f"清理主题市场失败: {e}")
