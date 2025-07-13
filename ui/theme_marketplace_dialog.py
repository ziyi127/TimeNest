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
TimeNest 主题市场对话框
提供主题浏览、下载、安装和管理功能
"""

import logging
from typing import Dict, List, Optional, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QListWidget,
    QListWidgetItem, QTabWidget, QWidget, QTextEdit,
    QProgressBar, QMessageBox, QScrollArea, QFrame,
    QGroupBox, QFormLayout, QSpinBox, QCheckBox
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
import requests
from pathlib import Path


if TYPE_CHECKING:
    from core.app_manager import AppManager:

    from core.app_manager import AppManager
    from core.theme_marketplace import ThemeMarketplace, ThemeInfo


class ThemeItemWidget(QFrame):
    """主题项目组件"""
    
    download_requested = pyqtSignal(str)  # 主题ID
    install_requested = pyqtSignal(str)   # 主题ID
    uninstall_requested = pyqtSignal(str) # 主题ID
    preview_requested = pyqtSignal(str)   # 主题ID
    
    def __init__(self, theme_info: 'ThemeInfo', is_installed: bool = False):
        super().__init__()
        self.theme_info = theme_info
        self.is_installed = is_installed
        self.logger = logging.getLogger(f'{__name__}.ThemeItemWidget')
        
        self.setup_ui()
        self.load_preview_image()
    
    def setup_ui(self):
        """设置界面"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #4472C4;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 预览图片
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(200, 120)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setText("加载中...")
        layout.addWidget(self.preview_label)
        
        # 主题信息
        info_layout = QVBoxLayout()
        
        # 主题名称
        name_label = QLabel(self.theme_info.name)
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        # 作者和版本
        author_label = QLabel(f"作者: {self.theme_info.author} | 版本: {self.theme_info.version}")
        author_label.setStyleSheet("color: #666;")
        info_layout.addWidget(author_label)
        
        # 描述
        desc_label = QLabel(self.theme_info.description)
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(40)
        info_layout.addWidget(desc_label)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        downloads_label = QLabel(f"下载: {self.theme_info.downloads}")
        stars_label = QLabel(f"⭐ {self.theme_info.stars}")
        stats_layout.addWidget(downloads_label)
        stats_layout.addWidget(stars_label)
        stats_layout.addStretch()
        info_layout.addLayout(stats_layout)
        
        layout.addLayout(info_layout)
        
        # 标签
        if self.theme_info.tags:
            tags_layout = QHBoxLayout()
            for tag in self.theme_info.tags[:3]:  # 最多显示3个标签:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    background-color: #e3f2fd;
                    color: #1976d2;
                    padding: 2px 6px;
                    border-radius: 10px;
                    font-size: 10px;
                """)
                tags_layout.addWidget(tag_label)
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览")
        self.preview_button.clicked.connect(lambda: self.preview_requested.emit(self.theme_info.id))
        button_layout.addWidget(self.preview_button)
        
        
        if self.is_installed:
            self.action_button = QPushButton("卸载")
        
            self.action_button = QPushButton("卸载")
            self.action_button.setStyleSheet("background-color: #f44336; color: white;")
            self.action_button.clicked.connect(lambda: self.uninstall_requested.emit(self.theme_info.id))
        else:
            self.action_button = QPushButton("下载")
            self.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
            self.action_button.clicked.connect(lambda: self.download_requested.emit(self.theme_info.id))
        
        button_layout.addWidget(self.action_button)
        layout.addLayout(button_layout)
        
        self.setFixedSize(220, 320)
    
    def load_preview_image(self):
        """加载预览图片"""
        try:
            # 这里应该异步加载图片，简化处理
            self.preview_label.setText(f"预览图\n{self.theme_info.name}")
        except Exception as e:
            self.logger.error(f"加载预览图失败: {e}")
            self.preview_label.setText("预览不可用")
    
    def set_installed_status(self, installed: bool):
        """设置安装状态"""
        self.is_installed = installed
        if installed and hasattr(installed, "self.action_button"):
    self.action_button.setText("卸载")
            self.action_button.setText("卸载")
            self.action_button.setStyleSheet("background-color: #f44336; color: white;")
            self.action_button.clicked.disconnect()
            self.action_button.clicked.connect(lambda: self.uninstall_requested.emit(self.theme_info.id))
        else:
            self.action_button.setText("下载")
            self.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
            self.action_button.clicked.disconnect()
            self.action_button.clicked.connect(lambda: self.download_requested.emit(self.theme_info.id))


class ThemeMarketplaceDialog(QDialog):
    """主题市场对话框"""
    
    theme_applied = pyqtSignal(str)  # 主题已应用
    
    def __init__(self, app_manager: 'AppManager', parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.theme_marketplace = None
        self.logger = logging.getLogger(f'{__name__}.ThemeMarketplaceDialog')
        
        self.theme_widgets: Dict[str, ThemeItemWidget] = {}
        
        self.setup_ui()
        self.setup_marketplace()
        self.load_themes()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("主题市场")
        self.setFixedSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 顶部搜索栏
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索主题...")
        self.search_edit.textChanged.connect(self.search_themes)
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "深色", "浅色", "彩色", "简约", "现代"])
        self.category_combo.currentTextChanged.connect(self.filter_themes)
        search_layout.addWidget(QLabel("分类:"))
        search_layout.addWidget(self.category_combo)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["下载量", "评分", "最新", "名称"])
        self.sort_combo.currentTextChanged.connect(self.sort_themes)
        search_layout.addWidget(QLabel("排序:"))
        search_layout.addWidget(self.sort_combo)
        
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_themes)
        search_layout.addWidget(refresh_button)
        
        layout.addLayout(search_layout)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 在线主题选项卡
        self.online_tab = self.create_online_themes_tab()
        self.tab_widget.addTab(self.online_tab, "在线主题")
        
        # 已安装主题选项卡
        self.installed_tab = self.create_installed_themes_tab()
        self.tab_widget.addTab(self.installed_tab, "已安装")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)
        
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def create_online_themes_tab(self) -> QWidget:
        """创建在线主题选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 主题网格容器
        self.online_themes_widget = QWidget()
        self.online_themes_layout = QGridLayout(self.online_themes_widget)
        self.online_themes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.online_themes_widget)
        layout.addWidget(scroll_area)
        
        return tab
    
    def create_installed_themes_tab(self) -> QWidget:
        """创建已安装主题选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 已安装主题容器
        self.installed_themes_widget = QWidget()
        self.installed_themes_layout = QGridLayout(self.installed_themes_widget)
        self.installed_themes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.installed_themes_widget)
        layout.addWidget(scroll_area)
        
        return tab
    
    def setup_marketplace(self):
        """设置主题市场"""
        try:
            from core.theme_marketplace import ThemeMarketplace
            
            self.theme_marketplace = ThemeMarketplace(
                self.app_manager.config_manager,
                self.app_manager.theme_manager
            )
            
            # 连接信号
            self.theme_marketplace.themes_loaded.connect(self.on_themes_loaded)
            self.theme_marketplace.theme_installed.connect(self.on_theme_installed)
            self.theme_marketplace.theme_uninstalled.connect(self.on_theme_uninstalled)
            self.theme_marketplace.error_occurred.connect(self.on_error_occurred)
            
        except Exception as e:
            self.logger.error(f"设置主题市场失败: {e}")
            QMessageBox.critical(self, "错误", f"初始化主题市场失败: {e}")
    
    def load_themes(self):
        """加载主题"""
        if self.theme_marketplace:
            self.theme_marketplace.fetch_themes()
    
    def on_themes_loaded(self, themes: List.get('ThemeInfo')):
        """主题加载完成"""
        try:
            # 清空现有主题
            self.clear_theme_widgets()
            
            # 添加在线主题
            row, col = 0, 0
            max_cols = 4
            
            for theme in themes:
                is_installed = self.theme_marketplace.is_theme_installed(theme.id)
                theme_widget = ThemeItemWidget(theme, is_installed)
                
                # 连接信号
                theme_widget.download_requested.connect(self.download_theme)
                theme_widget.install_requested.connect(self.install_theme)
                theme_widget.uninstall_requested.connect(self.uninstall_theme)
                theme_widget.preview_requested.connect(self.preview_theme)
                
                self.online_themes_layout.addWidget(theme_widget, row, col)
                self.theme_widgets[theme.id] = theme_widget
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # 加载已安装主题
            self.load_installed_themes()
            
        except Exception as e:
            self.logger.error(f"加载主题失败: {e}")
    
    def load_installed_themes(self):
        """加载已安装主题"""
        try:
            if not self.theme_marketplace:
                return:
                return
            
            # 清空已安装主题布局
            self.clear_installed_theme_widgets()
            
            installed_themes = self.theme_marketplace.get_installed_themes()
            
            row, col = 0, 0
            max_cols = 4
            
            for theme in installed_themes:
                theme_widget = ThemeItemWidget(theme, True)
                
                # 连接信号
                theme_widget.uninstall_requested.connect(self.uninstall_theme)
                theme_widget.preview_requested.connect(self.preview_theme)
                
                self.installed_themes_layout.addWidget(theme_widget, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
        except Exception as e:
            self.logger.error(f"加载已安装主题失败: {e}")
    
    def clear_theme_widgets(self):
        """清空主题组件"""
        for widget in self.theme_widgets.values():
            widget.deleteLater()
        self.theme_widgets.clear()
        
        # 清空布局
        while self.online_themes_layout.count():
            child = self.online_themes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def clear_installed_theme_widgets(self):
        """清空已安装主题组件"""
        while self.installed_themes_layout.count():
            child = self.installed_themes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def search_themes(self, query: str):
        """搜索主题"""
        # 简化实现：隐藏/显示主题组件
        for theme_widget in self.theme_widgets.values():
            theme_info = theme_widget.theme_info
            visible = (query.lower() in theme_info.name.lower() or
                      query.lower() in theme_info.description.lower() or
                      any(query.lower() in tag.lower() for tag in theme_info.tags))
            theme_widget.setVisible(visible)
    
    def filter_themes(self, category: str):
        """按分类过滤主题"""
        if category == "全部":
            for widget in self.theme_widgets.values():
                widget.setVisible(True)
        else:
            for theme_widget in self.theme_widgets.values():
                visible = category.lower() in [tag.lower() for tag in theme_widget.theme_info.tags]
                theme_widget.setVisible(visible)
    
    def sort_themes(self, sort_by: str):
        """排序主题"""
        # 这里可以实现重新排序逻辑
        pass
    
    def refresh_themes(self):
        """刷新主题"""
        if self.theme_marketplace:
            self.theme_marketplace.refresh_themes_cache()
    
    def download_theme(self, theme_id: str):
        """下载主题"""
        try:
            if not self.theme_marketplace:
                return:
                return
            
            # 查找主题信息
            theme_info = None
            for widget in self.theme_widgets.values():
                if widget.theme_info.id == theme_id:
                    theme_info = widget.theme_info
                    break
            
            
            if theme_info and hasattr(theme_info, "self.progress_bar"):
    self.progress_bar.setVisible(True)
            
                self.progress_bar.setVisible(True)
                self.theme_marketplace.download_theme(theme_info)
            
        except Exception as e:
            self.logger.error(f"下载主题失败: {e}")
            QMessageBox.critical(self, "错误", f"下载失败: {e}")
    
    def install_theme(self, theme_id: str):
        """安装主题"""
        # 下载完成后会自动安装
        pass
    
    def uninstall_theme(self, theme_id: str):
        """卸载主题"""
        try:
            if not self.theme_marketplace:
                return:
                return
            
            reply = QMessageBox.question(
                self, "确认卸载", "确定要卸载这个主题吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            
            if reply == QMessageBox.StandardButton.Yes:
                self.theme_marketplace.uninstall_theme(theme_id)
            
                self.theme_marketplace.uninstall_theme(theme_id)
            
        except Exception as e:
            self.logger.error(f"卸载主题失败: {e}")
            QMessageBox.critical(self, "错误", f"卸载失败: {e}")
    
    def preview_theme(self, theme_id: str):
        """预览主题"""
        try:
            # 这里可以实现主题预览功能
            QMessageBox.information(self, "预览", f"主题 {theme_id} 的预览功能正在开发中")
            
        except Exception as e:
            self.logger.error(f"预览主题失败: {e}")
    
    def on_theme_installed(self, theme_id: str):
        """主题安装完成"""
        self.progress_bar.setVisible(False)
        
        # 更新主题组件状态
        if theme_id in self.theme_widgets:
            self.theme_widgets[theme_id].set_installed_status(True)
        
        # 刷新已安装主题
        self.load_installed_themes()
        
        QMessageBox.information(self, "成功", "主题安装成功！")
    
    def on_theme_uninstalled(self, theme_id: str):
        """主题卸载完成"""
        # 更新主题组件状态
        if theme_id in self.theme_widgets:
            self.theme_widgets[theme_id].set_installed_status(False)
        
        # 刷新已安装主题
        self.load_installed_themes()
        
        QMessageBox.information(self, "成功", "主题卸载成功！")
    
    def on_error_occurred(self, error_msg: str):
        """错误处理"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", error_msg)
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            if self.theme_marketplace:
                self.theme_marketplace.cleanup()
        except Exception as e:
            self.logger.error(f"清理主题市场失败: {e}")
        
        super().closeEvent(event)
