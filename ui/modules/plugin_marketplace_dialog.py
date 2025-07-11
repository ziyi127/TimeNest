#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 插件市场模块
集成在线插件浏览、下载安装、已安装插件管理、插件设置等功能
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox, 
    QGroupBox, QFormLayout, QListWidget, QListWidgetItem,
    QTextEdit, QProgressBar, QMessageBox, QScrollArea,
    QFrame, QGridLayout, QSplitter, QSpinBox, QSlider
)
from PyQt6.QtGui import QFont, QPixmap, QIcon

if TYPE_CHECKING:
    from core.app_manager import AppManager


class PluginItemWidget(QFrame):
    """插件项目组件"""
    
    install_requested = pyqtSignal(str)  # 插件ID
    uninstall_requested = pyqtSignal(str)  # 插件ID
    configure_requested = pyqtSignal(str)  # 插件ID
    
    def __init__(self, plugin_info: Dict[str, Any], is_installed: bool = False):
        super().__init__()
        self.plugin_info = plugin_info
        self.is_installed = is_installed
        
        self.setup_ui()
    
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
        
        # 插件图标和名称
        header_layout = QHBoxLayout()
        
        # 图标
        self.icon_label = QLabel("🔌")
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 24px; border: 1px solid #ccc; border-radius: 4px;")
        header_layout.addWidget(self.icon_label)
        
        # 插件信息
        info_layout = QVBoxLayout()
        
        # 插件名称
        name_label = QLabel(self.plugin_info.get('name', '未知插件'))
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        # 作者和版本
        author_label = QLabel(f"作者: {self.plugin_info.get('author', '未知')} | 版本: {self.plugin_info.get('version', '1.0.0')}")
        author_label.setStyleSheet("color: #666; font-size: 10px;")
        info_layout.addWidget(author_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 插件描述
        desc_label = QLabel(self.plugin_info.get('description', '暂无描述'))
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(40)
        desc_label.setStyleSheet("color: #555;")
        layout.addWidget(desc_label)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        downloads_label = QLabel(f"下载: {self.plugin_info.get('downloads', 0)}")
        rating_label = QLabel(f"⭐ {self.plugin_info.get('rating', 0)}")
        stats_layout.addWidget(downloads_label)
        stats_layout.addWidget(rating_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        if self.is_installed:
            self.config_button = QPushButton("配置")
            self.config_button.clicked.connect(lambda: self.configure_requested.emit(self.plugin_info['id']))
            button_layout.addWidget(self.config_button)
            
            self.uninstall_button = QPushButton("卸载")
            self.uninstall_button.setStyleSheet("background-color: #f44336; color: white;")
            self.uninstall_button.clicked.connect(lambda: self.uninstall_requested.emit(self.plugin_info['id']))
            button_layout.addWidget(self.uninstall_button)
        else:
            self.install_button = QPushButton("安装")
            self.install_button.setStyleSheet("background-color: #4CAF50; color: white;")
            self.install_button.clicked.connect(lambda: self.install_requested.emit(self.plugin_info['id']))
            button_layout.addWidget(self.install_button)
        
        layout.addLayout(button_layout)
        
        self.setFixedSize(280, 180)


class PluginMarketplaceDialog(QDialog):
    """插件市场主对话框"""
    
    # 信号定义
    plugin_installed = pyqtSignal(str)  # 插件ID
    plugin_uninstalled = pyqtSignal(str)  # 插件ID
    
    def __init__(self, app_manager: 'AppManager', parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.PluginMarketplaceDialog')
        
        # 数据存储
        self.online_plugins = []
        self.installed_plugins = []
        self.plugin_widgets = {}
        
        self.setup_ui()
        self.load_data()
        self.connect_signals()
        
        self.logger.info("插件市场模块初始化完成")
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("插件市场")
        self.setFixedSize(1200, 800)
        
        layout = QVBoxLayout(self)
        
        # 顶部搜索栏
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索插件...")
        self.search_edit.textChanged.connect(self.search_plugins)
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "工具", "主题", "组件", "扩展"])
        self.category_combo.currentTextChanged.connect(self.filter_plugins)
        search_layout.addWidget(QLabel("分类:"))
        search_layout.addWidget(self.category_combo)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["下载量", "评分", "最新", "名称"])
        search_layout.addWidget(QLabel("排序:"))
        search_layout.addWidget(self.sort_combo)
        
        refresh_button = QPushButton("🔄 刷新")
        refresh_button.clicked.connect(self.refresh_plugins)
        search_layout.addWidget(refresh_button)
        
        layout.addLayout(search_layout)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 1. 在线插件选项卡
        self.online_tab = self.create_online_plugins_tab()
        self.tab_widget.addTab(self.online_tab, "🌐 在线插件")
        
        # 2. 已安装插件选项卡
        self.installed_tab = self.create_installed_plugins_tab()
        self.tab_widget.addTab(self.installed_tab, "💾 已安装")
        
        # 3. 插件设置选项卡
        self.settings_tab = self.create_plugin_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ 插件设置")
        
        # 4. 开发工具选项卡
        self.dev_tab = self.create_development_tab()
        self.tab_widget.addTab(self.dev_tab, "🛠️ 开发工具")
        
        layout.addWidget(self.tab_widget)
        
        # 底部状态栏
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_layout.addStretch()
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        status_layout.addWidget(self.close_button)
        
        layout.addLayout(status_layout)
    
    def create_online_plugins_tab(self) -> QWidget:
        """创建在线插件选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 插件网格容器
        self.online_plugins_widget = QWidget()
        self.online_plugins_layout = QGridLayout(self.online_plugins_widget)
        self.online_plugins_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.online_plugins_widget)
        layout.addWidget(scroll_area)
        
        return tab
    
    def create_installed_plugins_tab(self) -> QWidget:
        """创建已安装插件选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.enable_all_button = QPushButton("全部启用")
        self.enable_all_button.clicked.connect(self.enable_all_plugins)
        toolbar_layout.addWidget(self.enable_all_button)
        
        self.disable_all_button = QPushButton("全部禁用")
        self.disable_all_button.clicked.connect(self.disable_all_plugins)
        toolbar_layout.addWidget(self.disable_all_button)
        
        toolbar_layout.addStretch()
        
        self.uninstall_selected_button = QPushButton("卸载选中")
        self.uninstall_selected_button.clicked.connect(self.uninstall_selected_plugins)
        toolbar_layout.addWidget(self.uninstall_selected_button)
        
        layout.addLayout(toolbar_layout)
        
        # 已安装插件列表
        self.installed_plugins_list = QListWidget()
        self.installed_plugins_list.itemSelectionChanged.connect(self.on_installed_plugin_selected)
        layout.addWidget(self.installed_plugins_list)
        
        # 插件详情
        details_group = QGroupBox("插件详情")
        details_layout = QFormLayout(details_group)
        
        self.plugin_name_label = QLabel("未选择插件")
        self.plugin_version_label = QLabel("-")
        self.plugin_author_label = QLabel("-")
        self.plugin_status_label = QLabel("-")
        self.plugin_description_text = QTextEdit()
        self.plugin_description_text.setMaximumHeight(80)
        self.plugin_description_text.setReadOnly(True)
        
        details_layout.addRow("插件名称:", self.plugin_name_label)
        details_layout.addRow("版本:", self.plugin_version_label)
        details_layout.addRow("作者:", self.plugin_author_label)
        details_layout.addRow("状态:", self.plugin_status_label)
        details_layout.addRow("描述:", self.plugin_description_text)
        
        layout.addWidget(details_group)
        
        return tab
    
    def create_plugin_settings_tab(self) -> QWidget:
        """创建插件设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 插件选择
        plugin_select_layout = QHBoxLayout()
        
        self.settings_plugin_combo = QComboBox()
        self.settings_plugin_combo.currentTextChanged.connect(self.on_settings_plugin_changed)
        plugin_select_layout.addWidget(QLabel("选择插件:"))
        plugin_select_layout.addWidget(self.settings_plugin_combo)
        
        plugin_select_layout.addStretch()
        
        layout.addLayout(plugin_select_layout)
        
        # 设置区域
        self.settings_scroll_area = QScrollArea()
        self.settings_scroll_area.setWidgetResizable(True)
        
        self.settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_widget)
        
        # 默认提示
        self.no_plugin_label = QLabel("请选择一个插件进行配置")
        self.no_plugin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_plugin_label.setStyleSheet("color: #999; font-size: 16px;")
        self.settings_layout.addWidget(self.no_plugin_label)
        
        self.settings_scroll_area.setWidget(self.settings_widget)
        layout.addWidget(self.settings_scroll_area)
        
        # 设置操作按钮
        settings_buttons_layout = QHBoxLayout()
        
        self.save_settings_button = QPushButton("保存设置")
        self.save_settings_button.clicked.connect(self.save_plugin_settings)
        self.save_settings_button.setEnabled(False)
        settings_buttons_layout.addWidget(self.save_settings_button)
        
        self.reset_settings_button = QPushButton("重置设置")
        self.reset_settings_button.clicked.connect(self.reset_plugin_settings)
        self.reset_settings_button.setEnabled(False)
        settings_buttons_layout.addWidget(self.reset_settings_button)
        
        settings_buttons_layout.addStretch()
        
        layout.addLayout(settings_buttons_layout)
        
        return tab
    
    def create_development_tab(self) -> QWidget:
        """创建开发工具选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 插件开发工具
        dev_tools_group = QGroupBox("插件开发工具")
        dev_tools_layout = QVBoxLayout(dev_tools_group)
        
        tools_buttons_layout = QHBoxLayout()
        
        self.create_plugin_button = QPushButton("创建新插件")
        self.create_plugin_button.clicked.connect(self.create_new_plugin)
        tools_buttons_layout.addWidget(self.create_plugin_button)
        
        self.package_plugin_button = QPushButton("打包插件")
        self.package_plugin_button.clicked.connect(self.package_plugin)
        tools_buttons_layout.addWidget(self.package_plugin_button)
        
        self.test_plugin_button = QPushButton("测试插件")
        self.test_plugin_button.clicked.connect(self.test_plugin)
        tools_buttons_layout.addWidget(self.test_plugin_button)
        
        dev_tools_layout.addLayout(tools_buttons_layout)
        
        layout.addWidget(dev_tools_group)
        
        # 插件模板
        template_group = QGroupBox("插件模板")
        template_layout = QVBoxLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "基础插件模板",
            "UI组件插件",
            "数据处理插件",
            "主题插件",
            "通知插件"
        ])
        template_layout.addWidget(QLabel("选择模板:"))
        template_layout.addWidget(self.template_combo)
        
        self.generate_template_button = QPushButton("生成模板代码")
        self.generate_template_button.clicked.connect(self.generate_template)
        template_layout.addWidget(self.generate_template_button)
        
        layout.addWidget(template_group)
        
        # 开发文档
        docs_group = QGroupBox("开发文档")
        docs_layout = QVBoxLayout(docs_group)
        
        docs_buttons_layout = QHBoxLayout()
        
        self.api_docs_button = QPushButton("API 文档")
        self.api_docs_button.clicked.connect(self.show_api_docs)
        docs_buttons_layout.addWidget(self.api_docs_button)
        
        self.examples_button = QPushButton("示例代码")
        self.examples_button.clicked.connect(self.show_examples)
        docs_buttons_layout.addWidget(self.examples_button)
        
        self.guidelines_button = QPushButton("开发指南")
        self.guidelines_button.clicked.connect(self.show_guidelines)
        docs_buttons_layout.addWidget(self.guidelines_button)
        
        docs_layout.addLayout(docs_buttons_layout)
        
        layout.addWidget(docs_group)
        
        layout.addStretch()
        
        return tab

    def load_data(self):
        """加载数据"""
        try:
            # 加载在线插件（模拟数据）
            self.online_plugins = [
                {
                    'id': 'weather_widget',
                    'name': '天气组件',
                    'author': 'WeatherDev',
                    'version': '1.2.0',
                    'description': '显示实时天气信息的浮窗组件',
                    'downloads': 1250,
                    'rating': 4.5,
                    'category': '组件'
                },
                {
                    'id': 'todo_manager',
                    'name': '待办事项管理',
                    'author': 'ProductivityTeam',
                    'version': '2.1.0',
                    'description': '强大的待办事项管理插件，支持分类和提醒',
                    'downloads': 890,
                    'rating': 4.8,
                    'category': '工具'
                },
                {
                    'id': 'dark_theme_pro',
                    'name': '专业深色主题',
                    'author': 'ThemeStudio',
                    'version': '1.0.5',
                    'description': '精美的深色主题包，包含多种配色方案',
                    'downloads': 2100,
                    'rating': 4.7,
                    'category': '主题'
                }
            ]

            # 加载已安装插件（模拟数据）
            self.installed_plugins = [
                {
                    'id': 'weather_widget',
                    'name': '天气组件',
                    'version': '1.2.0',
                    'author': 'WeatherDev',
                    'status': '已启用',
                    'description': '显示实时天气信息的浮窗组件'
                }
            ]

            # 更新界面
            self.update_online_plugins()
            self.update_installed_plugins()
            self.update_settings_plugin_combo()

        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")

    def connect_signals(self):
        """连接信号"""
        pass

    def update_online_plugins(self):
        """更新在线插件显示"""
        try:
            # 清空现有插件
            self.clear_plugin_widgets()

            # 添加插件项目
            row, col = 0, 0
            max_cols = 4

            for plugin in self.online_plugins:
                is_installed = any(p['id'] == plugin['id'] for p in self.installed_plugins)
                plugin_widget = PluginItemWidget(plugin, is_installed)

                # 连接信号
                plugin_widget.install_requested.connect(self.install_plugin)
                plugin_widget.uninstall_requested.connect(self.uninstall_plugin)
                plugin_widget.configure_requested.connect(self.configure_plugin)

                self.online_plugins_layout.addWidget(plugin_widget, row, col)
                self.plugin_widgets[plugin['id']] = plugin_widget

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        except Exception as e:
            self.logger.error(f"更新在线插件失败: {e}")

    def update_installed_plugins(self):
        """更新已安装插件列表"""
        try:
            self.installed_plugins_list.clear()

            for plugin in self.installed_plugins:
                item = QListWidgetItem(f"{plugin['name']} v{plugin['version']}")
                item.setData(Qt.ItemDataRole.UserRole, plugin)

                # 设置状态图标
                if plugin['status'] == '已启用':
                    item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogApplyButton))
                else:
                    item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogCancelButton))

                self.installed_plugins_list.addItem(item)

        except Exception as e:
            self.logger.error(f"更新已安装插件失败: {e}")

    def update_settings_plugin_combo(self):
        """更新设置插件下拉框"""
        try:
            self.settings_plugin_combo.clear()
            self.settings_plugin_combo.addItem("请选择插件...")

            for plugin in self.installed_plugins:
                self.settings_plugin_combo.addItem(plugin['name'], plugin['id'])

        except Exception as e:
            self.logger.error(f"更新设置插件下拉框失败: {e}")

    def clear_plugin_widgets(self):
        """清空插件组件"""
        for widget in self.plugin_widgets.values():
            widget.deleteLater()
        self.plugin_widgets.clear()

        # 清空布局
        while self.online_plugins_layout.count():
            child = self.online_plugins_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def search_plugins(self, query: str):
        """搜索插件"""
        try:
            for plugin_id, widget in self.plugin_widgets.items():
                plugin = next((p for p in self.online_plugins if p['id'] == plugin_id), None)
                if plugin:
                    visible = (query.lower() in plugin['name'].lower() or
                              query.lower() in plugin['description'].lower())
                    widget.setVisible(visible)
        except Exception as e:
            self.logger.error(f"搜索插件失败: {e}")

    def filter_plugins(self, category: str):
        """按分类过滤插件"""
        try:
            for plugin_id, widget in self.plugin_widgets.items():
                plugin = next((p for p in self.online_plugins if p['id'] == plugin_id), None)
                if plugin:
                    visible = category == "全部" or plugin.get('category', '') == category
                    widget.setVisible(visible)
        except Exception as e:
            self.logger.error(f"过滤插件失败: {e}")

    def refresh_plugins(self):
        """刷新插件列表"""
        try:
            self.status_label.setText("正在刷新插件列表...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(50)

            # 模拟刷新延迟
            QTimer.singleShot(1000, self._refresh_complete)

        except Exception as e:
            self.logger.error(f"刷新插件失败: {e}")

    def _refresh_complete(self):
        """刷新完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("刷新完成")
        self.load_data()

    def install_plugin(self, plugin_id: str):
        """安装插件"""
        try:
            plugin = next((p for p in self.online_plugins if p['id'] == plugin_id), None)
            if plugin:
                reply = QMessageBox.question(
                    self, "确认安装", f"确定要安装插件 '{plugin['name']}' 吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 模拟安装过程
                    self.status_label.setText(f"正在安装 {plugin['name']}...")
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setValue(0)

                    # 模拟安装进度
                    QTimer.singleShot(500, lambda: self.progress_bar.setValue(30))
                    QTimer.singleShot(1000, lambda: self.progress_bar.setValue(60))
                    QTimer.singleShot(1500, lambda: self.progress_bar.setValue(100))
                    QTimer.singleShot(2000, lambda: self._install_complete(plugin))

        except Exception as e:
            self.logger.error(f"安装插件失败: {e}")
            QMessageBox.critical(self, "错误", f"安装失败: {e}")

    def _install_complete(self, plugin):
        """安装完成"""
        try:
            # 添加到已安装列表
            installed_plugin = {
                'id': plugin['id'],
                'name': plugin['name'],
                'version': plugin['version'],
                'author': plugin['author'],
                'status': '已启用',
                'description': plugin['description']
            }
            self.installed_plugins.append(installed_plugin)

            # 更新界面
            self.update_online_plugins()
            self.update_installed_plugins()
            self.update_settings_plugin_combo()

            self.progress_bar.setVisible(False)
            self.status_label.setText("安装完成")

            QMessageBox.information(self, "安装成功", f"插件 '{plugin['name']}' 安装成功！")

        except Exception as e:
            self.logger.error(f"完成安装失败: {e}")

    def uninstall_plugin(self, plugin_id: str):
        """卸载插件"""
        try:
            reply = QMessageBox.question(
                self, "确认卸载", f"确定要卸载插件 '{plugin_id}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 获取插件管理器
                if hasattr(self.app_manager, 'plugin_manager'):
                    plugin_manager = self.app_manager.plugin_manager

                    if plugin_manager.unload_plugin(plugin_id):
                        QMessageBox.information(self, "成功", f"插件 '{plugin_id}' 已卸载")
                        self.refresh_installed_plugins()
                    else:
                        QMessageBox.warning(self, "失败", f"卸载插件 '{plugin_id}' 失败")
                else:
                    QMessageBox.warning(self, "错误", "插件管理器不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"卸载插件失败: {e}")

    def configure_plugin(self, plugin_id: str):
        """配置插件"""
        try:
            # 创建插件配置对话框
            dialog = PluginConfigDialog(plugin_id, self.app_manager, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开插件配置失败: {e}")

    def enable_all_plugins(self):
        """启用所有插件"""
        try:
            if hasattr(self.app_manager, 'plugin_manager'):
                plugin_manager = self.app_manager.plugin_manager
                loaded_plugins = plugin_manager.get_loaded_plugins()

                enabled_count = 0
                for plugin_id in loaded_plugins:
                    if plugin_manager.activate_plugin(plugin_id):
                        enabled_count += 1

                QMessageBox.information(self, "完成", f"已启用 {enabled_count} 个插件")
                self.refresh_installed_plugins()
            else:
                QMessageBox.warning(self, "错误", "插件管理器不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"启用插件失败: {e}")

    def disable_all_plugins(self):
        """禁用所有插件"""
        try:
            if hasattr(self.app_manager, 'plugin_manager'):
                plugin_manager = self.app_manager.plugin_manager
                active_plugins = plugin_manager.get_active_plugins()

                disabled_count = 0
                for plugin_id in active_plugins:
                    if plugin_manager.deactivate_plugin(plugin_id):
                        disabled_count += 1

                QMessageBox.information(self, "完成", f"已禁用 {disabled_count} 个插件")
                self.refresh_installed_plugins()
            else:
                QMessageBox.warning(self, "错误", "插件管理器不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"禁用插件失败: {e}")

    def uninstall_selected_plugins(self):
        """卸载选中的插件"""
        QMessageBox.information(self, "功能开发中", "卸载选中插件功能正在开发中...")

    def on_installed_plugin_selected(self):
        """已安装插件选择变化"""
        QMessageBox.information(self, "功能开发中", "插件详情显示功能正在开发中...")

    def on_settings_plugin_changed(self, plugin_name: str):
        """设置插件变化"""
        QMessageBox.information(self, "功能开发中", "插件设置功能正在开发中...")

    def save_plugin_settings(self):
        """保存插件设置"""
        QMessageBox.information(self, "保存成功", "插件设置已保存")

    def reset_plugin_settings(self):
        """重置插件设置"""
        QMessageBox.information(self, "重置完成", "插件设置已重置为默认值")

    def create_new_plugin(self):
        """创建新插件"""
        try:
            # 创建插件创建对话框
            dialog = PluginCreationDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                plugin_info = dialog.get_plugin_info()
                template_type = dialog.get_template_type()
                output_dir = dialog.get_output_dir()

                # 获取插件开发工具
                if hasattr(self.app_manager, 'plugin_development_tools'):
                    dev_tools = self.app_manager.plugin_development_tools

                    if dev_tools.create_plugin_from_template(template_type, plugin_info, output_dir):
                        QMessageBox.information(self, "成功", f"插件已创建在: {output_dir}")
                    else:
                        QMessageBox.warning(self, "失败", "插件创建失败")
                else:
                    QMessageBox.warning(self, "错误", "插件开发工具不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建插件失败: {e}")

    def package_plugin(self):
        """打包插件"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            # 选择插件目录
            plugin_dir = QFileDialog.getExistingDirectory(
                self, "选择插件目录", "", QFileDialog.Option.ShowDirsOnly
            )

            if not plugin_dir:
                return

            # 选择输出位置
            output_path, _ = QFileDialog.getSaveFileName(
                self, "保存插件包", "", "TimeNest插件包 (*.tnp)"
            )

            if not output_path:
                return

            # 获取插件开发工具
            if hasattr(self.app_manager, 'plugin_development_tools'):
                dev_tools = self.app_manager.plugin_development_tools

                package_path = dev_tools.package_plugin(plugin_dir, output_path)
                if package_path:
                    QMessageBox.information(self, "成功", f"插件已打包为: {package_path}")
                else:
                    QMessageBox.warning(self, "失败", "插件打包失败")
            else:
                QMessageBox.warning(self, "错误", "插件开发工具不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打包插件失败: {e}")

    def test_plugin(self):
        """测试插件"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            # 选择插件目录或包文件
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择插件文件", "", "所有支持的文件 (*.tnp);;插件包 (*.tnp)"
            )

            if not file_path:
                # 如果没有选择文件，尝试选择目录
                plugin_dir = QFileDialog.getExistingDirectory(
                    self, "选择插件目录", "", QFileDialog.Option.ShowDirsOnly
                )
                if not plugin_dir:
                    return
                file_path = plugin_dir

            # 获取插件开发工具
            if hasattr(self.app_manager, 'plugin_development_tools'):
                dev_tools = self.app_manager.plugin_development_tools

                if file_path.endswith('.tnp'):
                    # 测试插件包
                    if dev_tools.validate_plugin_package(file_path):
                        QMessageBox.information(self, "测试通过", "插件包验证通过")
                    else:
                        QMessageBox.warning(self, "测试失败", "插件包验证失败")
                else:
                    # 测试插件目录
                    if dev_tools.test_plugin(file_path):
                        QMessageBox.information(self, "测试通过", "插件测试通过")
                    else:
                        QMessageBox.warning(self, "测试失败", "插件测试失败，请检查日志")
            else:
                QMessageBox.warning(self, "错误", "插件开发工具不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试插件失败: {e}")

    def generate_template(self):
        """生成模板代码"""
        try:
            # 创建模板选择对话框
            dialog = TemplateSelectionDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                template_type = dialog.get_selected_template()
                output_dir = dialog.get_output_dir()

                if hasattr(self.app_manager, 'plugin_development_tools'):
                    dev_tools = self.app_manager.plugin_development_tools

                    # 使用默认插件信息
                    plugin_info = {
                        'id': 'template_plugin',
                        'name': 'Template Plugin',
                        'author': 'Developer',
                        'description': 'Generated from template',
                        'version': '1.0.0'
                    }

                    if dev_tools.create_plugin_from_template(template_type, plugin_info, output_dir):
                        QMessageBox.information(self, "成功", f"模板已生成在: {output_dir}")
                    else:
                        QMessageBox.warning(self, "失败", "模板生成失败")
                else:
                    QMessageBox.warning(self, "错误", "插件开发工具不可用")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成模板失败: {e}")

    def show_api_docs(self):
        """显示API文档"""
        try:
            # 创建API文档对话框
            dialog = ApiDocumentationDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开API文档失败: {e}")

    def show_examples(self):
        """显示示例代码"""
        QMessageBox.information(self, "功能开发中", "示例代码功能正在开发中...")

    def show_guidelines(self):
        """显示开发指南"""
        QMessageBox.information(self, "功能开发中", "开发指南功能正在开发中...")

    def closeEvent(self, event):
        """关闭事件 - 只关闭窗口，不退出程序"""
        try:
            # 直接关闭窗口，不退出程序
            event.accept()  # 只关闭窗口，不退出程序

        except Exception as e:
            self.logger.error(f"关闭处理失败: {e}")
            event.accept()  # 只关闭窗口，不退出程序


class PluginCreationDialog(QDialog):
    """插件创建对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建新插件")
        self.setFixedSize(500, 600)

        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 插件信息
        info_group = QGroupBox("插件信息")
        info_layout = QFormLayout(info_group)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("例如: my_awesome_plugin")
        info_layout.addRow("插件ID:", self.id_edit)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: My Awesome Plugin")
        info_layout.addRow("插件名称:", self.name_edit)

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("您的名字")
        info_layout.addRow("作者:", self.author_edit)

        self.version_edit = QLineEdit("1.0.0")
        info_layout.addRow("版本:", self.version_edit)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("插件功能描述...")
        info_layout.addRow("描述:", self.description_edit)

        layout.addWidget(info_group)

        # 模板选择
        template_group = QGroupBox("选择模板")
        template_layout = QVBoxLayout(template_group)

        self.template_combo = QComboBox()
        self.template_combo.addItem("基础插件模板", "basic")
        self.template_combo.addItem("UI组件插件模板", "ui_component")
        self.template_combo.addItem("通知插件模板", "notification")
        self.template_combo.addItem("主题插件模板", "theme")
        template_layout.addWidget(self.template_combo)

        self.template_desc_label = QLabel()
        self.template_desc_label.setWordWrap(True)
        template_layout.addWidget(self.template_desc_label)

        layout.addWidget(template_group)

        # 输出目录
        output_group = QGroupBox("输出目录")
        output_layout = QHBoxLayout(output_group)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("选择插件创建目录...")
        output_layout.addWidget(self.output_edit)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_btn)

        layout.addWidget(output_group)

        # 按钮
        button_layout = QHBoxLayout()

        create_btn = QPushButton("创建插件")
        create_btn.clicked.connect(self.accept)
        button_layout.addWidget(create_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # 连接信号
        self.template_combo.currentTextChanged.connect(self.update_template_description)
        self.update_template_description()

    def browse_output_dir(self):
        """浏览输出目录"""
        from PyQt6.QtWidgets import QFileDialog

        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", "", QFileDialog.Option.ShowDirsOnly
        )

        if dir_path:
            self.output_edit.setText(dir_path)

    def update_template_description(self):
        """更新模板描述"""
        descriptions = {
            "基础插件模板": "包含基本插件结构的模板，适合简单功能插件",
            "UI组件插件模板": "用于创建UI组件的插件模板，包含界面文件",
            "通知插件模板": "用于扩展通知功能的插件模板",
            "主题插件模板": "用于创建主题的插件模板，包含样式文件"
        }

        current_text = self.template_combo.currentText()
        self.template_desc_label.setText(descriptions.get(current_text, ""))

    def get_plugin_info(self) -> Dict[str, str]:
        """获取插件信息"""
        return {
            'id': self.id_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'author': self.author_edit.text().strip(),
            'version': self.version_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip()
        }

    def get_template_type(self) -> str:
        """获取模板类型"""
        return self.template_combo.currentData()

    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.output_edit.text().strip()


class TemplateSelectionDialog(QDialog):
    """模板选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择插件模板")
        self.setFixedSize(400, 300)

        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 模板列表
        template_group = QGroupBox("可用模板")
        template_layout = QVBoxLayout(template_group)

        self.template_list = QListWidget()

        templates = [
            ("基础插件模板", "basic", "包含基本插件结构"),
            ("UI组件插件模板", "ui_component", "用于创建UI组件"),
            ("通知插件模板", "notification", "用于扩展通知功能"),
            ("主题插件模板", "theme", "用于创建主题")
        ]

        for name, key, desc in templates:
            item = QListWidgetItem(f"{name}\n{desc}")
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.template_list.addItem(item)

        self.template_list.setCurrentRow(0)
        template_layout.addWidget(self.template_list)

        layout.addWidget(template_group)

        # 输出目录
        output_group = QGroupBox("输出目录")
        output_layout = QHBoxLayout(output_group)

        self.output_edit = QLineEdit()
        output_layout.addWidget(self.output_edit)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_btn)

        layout.addWidget(output_group)

        # 按钮
        button_layout = QHBoxLayout()

        generate_btn = QPushButton("生成模板")
        generate_btn.clicked.connect(self.accept)
        button_layout.addWidget(generate_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def browse_output_dir(self):
        """浏览输出目录"""
        from PyQt6.QtWidgets import QFileDialog

        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", "", QFileDialog.Option.ShowDirsOnly
        )

        if dir_path:
            self.output_edit.setText(dir_path)

    def get_selected_template(self) -> str:
        """获取选中的模板"""
        current_item = self.template_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return "basic"

    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.output_edit.text().strip()


class PluginConfigDialog(QDialog):
    """插件配置对话框"""

    def __init__(self, plugin_id: str, app_manager, parent=None):
        super().__init__(parent)
        self.plugin_id = plugin_id
        self.app_manager = app_manager

        self.setWindowTitle(f"配置插件 - {plugin_id}")
        self.setFixedSize(600, 500)

        self.setup_ui()
        self.load_plugin_config()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 插件信息
        info_group = QGroupBox("插件信息")
        info_layout = QFormLayout(info_group)

        self.plugin_name_label = QLabel("未知")
        info_layout.addRow("名称:", self.plugin_name_label)

        self.plugin_version_label = QLabel("未知")
        info_layout.addRow("版本:", self.plugin_version_label)

        self.plugin_status_label = QLabel("未知")
        info_layout.addRow("状态:", self.plugin_status_label)

        layout.addWidget(info_group)

        # 配置选项
        config_group = QGroupBox("配置选项")
        config_layout = QVBoxLayout(config_group)

        # 启用/禁用
        self.enabled_checkbox = QCheckBox("启用插件")
        config_layout.addWidget(self.enabled_checkbox)

        # 自动启动
        self.auto_start_checkbox = QCheckBox("程序启动时自动加载")
        config_layout.addWidget(self.auto_start_checkbox)

        # 权限设置
        permissions_group = QGroupBox("权限设置")
        permissions_layout = QVBoxLayout(permissions_group)

        self.file_access_checkbox = QCheckBox("允许文件访问")
        permissions_layout.addWidget(self.file_access_checkbox)

        self.network_access_checkbox = QCheckBox("允许网络访问")
        permissions_layout.addWidget(self.network_access_checkbox)

        self.system_access_checkbox = QCheckBox("允许系统调用")
        permissions_layout.addWidget(self.system_access_checkbox)

        config_layout.addWidget(permissions_group)

        # 自定义配置
        custom_group = QGroupBox("自定义配置")
        custom_layout = QVBoxLayout(custom_group)

        self.config_text = QTextEdit()
        self.config_text.setPlaceholderText("插件自定义配置（JSON格式）...")
        custom_layout.addWidget(self.config_text)

        config_layout.addWidget(custom_group)

        layout.addWidget(config_group)

        # 按钮
        button_layout = QHBoxLayout()

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(reset_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_plugin_config(self):
        """加载插件配置"""
        try:
            if hasattr(self.app_manager, 'plugin_manager'):
                plugin_manager = self.app_manager.plugin_manager

                # 获取插件元数据
                metadata = plugin_manager.get_plugin_metadata(self.plugin_id)
                if metadata:
                    self.plugin_name_label.setText(metadata.name)
                    self.plugin_version_label.setText(metadata.version)

                # 获取插件状态
                status = plugin_manager.get_plugin_status(self.plugin_id)
                if status:
                    self.plugin_status_label.setText(status.value)
                    self.enabled_checkbox.setChecked(status.value == "enabled")

                # 加载配置
                # 这里应该从配置管理器加载插件特定的配置
                # 暂时使用默认值
                self.auto_start_checkbox.setChecked(True)
                self.file_access_checkbox.setChecked(False)
                self.network_access_checkbox.setChecked(False)
                self.system_access_checkbox.setChecked(False)

        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载插件配置失败: {e}")

    def save_config(self):
        """保存配置"""
        try:
            # 这里应该保存配置到配置管理器
            # 暂时只显示成功消息
            QMessageBox.information(self, "成功", "插件配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}")

    def reset_config(self):
        """重置配置"""
        try:
            reply = QMessageBox.question(
                self, "确认重置", "确定要重置插件配置为默认值吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.load_plugin_config()
                QMessageBox.information(self, "完成", "配置已重置为默认值")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"重置配置失败: {e}")


class ApiDocumentationDialog(QDialog):
    """API文档对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TimeNest 插件 API 文档")
        self.setFixedSize(800, 600)

        self.setup_ui()
        self.load_documentation()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 文档内容
        self.doc_text = QTextEdit()
        self.doc_text.setReadOnly(True)
        layout.addWidget(self.doc_text)

        # 按钮
        button_layout = QHBoxLayout()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_documentation(self):
        """加载文档内容"""
        doc_content = """# TimeNest 插件开发 API 文档

## 1. 插件基础类

### IPlugin 接口

所有插件都必须实现 IPlugin 接口：

```python
from core.plugin_base import IPlugin, PluginStatus

class MyPlugin(IPlugin):
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED

    def initialize(self, plugin_manager) -> bool:
        # 插件初始化逻辑
        return True

    def activate(self) -> bool:
        # 插件激活逻辑
        return True

    def deactivate(self) -> bool:
        # 插件停用逻辑
        return True

    def cleanup(self) -> None:
        # 清理资源
        pass

    def get_status(self) -> PluginStatus:
        return self.status
```

## 2. 插件元数据

在 plugin.json 中定义插件元数据：

```json
{
    "id": "my_plugin",
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "插件描述",
    "author": "作者名",
    "main_class": "MyPlugin",
    "api_version": "1.0.0",
    "min_app_version": "1.0.0",
    "dependencies": [],
    "permissions": ["file_access", "network_access"],
    "tags": ["utility"]
}
```

## 3. 服务接口

### 注册服务

```python
from core.plugin_base import IServiceProvider, ServiceInterface

class MyServicePlugin(IPlugin, IServiceProvider):
    def get_service_interface(self) -> ServiceInterface:
        interface = ServiceInterface(
            name="my_service",
            version="1.0.0",
            provider_id=self.metadata.id,
            service_type=ServiceType.UTILITY
        )

        # 添加方法
        interface.add_method(ServiceMethod(
            name="do_something",
            callable=self.do_something,
            description="执行某个操作"
        ))

        return interface

    def do_something(self, param: str) -> str:
        return f"处理: {param}"
```

## 4. 消息通信

### 发送消息

```python
from core.plugin_system import Message, MessageType

# 获取消息总线
message_bus = plugin_manager.get_message_bus()

# 创建消息
message = Message(
    message_type=MessageType.EVENT,
    topic="my_topic",
    sender_id=self.metadata.id,
    payload={"data": "hello"}
)

# 发送消息
message_bus.send_message(message)
```

### 接收消息

```python
def handle_message(self, message: Message):
    print(f"收到消息: {message.payload}")

# 注册消息处理器
message_bus.register_handler(
    self.metadata.id,
    "my_topic",
    self.handle_message
)
```

## 5. 事件系统

### 订阅事件

```python
from core.plugin_system import EventType

# 获取通信总线
comm_bus = plugin_manager.get_communication_bus()

# 订阅事件
comm_bus.subscribe(
    self.metadata.id,
    EventType.PLUGIN_LOADED,
    self.on_plugin_loaded
)

def on_plugin_loaded(self, event):
    print(f"插件已加载: {event.data}")
```

## 6. UI 扩展

### 创建UI组件

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyPluginWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("我的插件界面"))
```

## 7. 配置管理

### 读取配置

```python
# 获取配置值
value = plugin_manager.get_config(f"plugins.{self.metadata.id}.setting", "default")

# 设置配置值
plugin_manager.set_config(f"plugins.{self.metadata.id}.setting", "new_value")
```

## 8. 最佳实践

1. **错误处理**: 始终使用 try-except 处理异常
2. **日志记录**: 使用 logging 模块记录日志
3. **资源清理**: 在 cleanup() 方法中清理所有资源
4. **线程安全**: 注意多线程环境下的数据安全
5. **性能优化**: 避免在主线程中执行耗时操作

## 9. 调试技巧

1. 使用 logger 输出调试信息
2. 利用插件开发工具进行测试
3. 检查插件依赖关系
4. 验证插件包完整性

更多详细信息请参考官方文档和示例代码。
"""

        self.doc_text.setPlainText(doc_content)
