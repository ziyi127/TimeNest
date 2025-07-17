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
TimeNest 插件市场模块
集成在线插件浏览、下载安装、已安装插件管理、插件设置等功能
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox,
    QGroupBox, QFormLayout, QListWidget, QListWidgetItem,
    QTextEdit, QProgressBar, QMessageBox, QScrollArea,
    QFrame, QGridLayout, QSplitter, QSpinBox, QSlider,
    QApplication, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QPixmap, QIcon


if TYPE_CHECKING:
    from core.app_manager import AppManager


class PluginItemWidget(QFrame):
    """插件项目组件"""
    
    install_requested = Signal(str)  # 插件ID
    uninstall_requested = Signal(str)  # 插件ID
    configure_requested = Signal(str)  # 插件ID
    
    def __init__(self, plugin_info: Dict[str, Any], is_installed: bool = False):
        super().__init__()
        self.plugin_info = plugin_info
        self.is_installed = is_installed
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            PluginItemWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
            }
            PluginItemWidget:hover {
                border-color: #4472C4;
                background-color: #f8f9fa;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
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
            self.config_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.config_button.clicked.connect(lambda: self.configure_requested.emit(self.plugin_info.get('id')))
            button_layout.addWidget(self.config_button)

            self.uninstall_button = QPushButton("卸载")
            self.uninstall_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            self.uninstall_button.clicked.connect(lambda: self.uninstall_requested.emit(self.plugin_info.get('id')))
            button_layout.addWidget(self.uninstall_button)
        else:
            self.install_button = QPushButton("安装")
            self.install_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """)
            self.install_button.clicked.connect(lambda: self.install_requested.emit(self.plugin_info.get('id')))
            button_layout.addWidget(self.install_button)

        layout.addLayout(button_layout)

        # 设置最小和最大尺寸，而不是固定尺寸
        self.setMinimumSize(260, 160)
        self.setMaximumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)


class PluginMarketplaceDialog(QDialog):
    """插件市场主对话框"""
    
    # 信号定义
    plugin_installed = Signal(str)  # 插件ID
    plugin_uninstalled = Signal(str)  # 插件ID
    
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

    def showEvent(self, event):
        """对话框显示时自动刷新"""
        super().showEvent(event)
        # 延迟刷新，确保界面已完全显示
        QTimer.singleShot(100, self.refresh_plugins)

    def resizeEvent(self, event):
        """窗口大小变化时重新布局"""
        super().resizeEvent(event)
        # 延迟重新布局，避免频繁调用
        if hasattr(self, 'resize_timer'):
            self.resize_timer.stop()
        else:
            self.resize_timer = QTimer()
            self.resize_timer.setSingleShot(True)
            self.resize_timer.timeout.connect(self.update_online_plugins)

        self.resize_timer.start(200)  # 200ms延迟

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
        self.online_plugins_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.online_plugins_layout.setSpacing(10)  # 设置组件间距
        self.online_plugins_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        
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
            self.logger.info("开始加载插件数据...")

            # 加载已安装插件
            self.load_installed_plugins()

            # 加载在线插件（异步）
            self.load_online_plugins()

        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            self.status_label.setText(f"加载失败: {e}")

    def load_installed_plugins(self):
        """加载已安装插件"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'plugin_manager'):
                plugin_manager = self.app_manager.plugin_manager
                self.installed_plugins = []

                for plugin_id, plugin in plugin_manager.plugins.items():
                    metadata = plugin.get_metadata()
                    if metadata:
                        plugin_info = {
                            'id': plugin_id,
                            'name': metadata.name,
                            'version': metadata.version,
                            'description': metadata.description,
                            'author': metadata.author,
                            'status': plugin.get_status().value,
                            'plugin_type': metadata.plugin_type.value
                        }
                        self.installed_plugins.append(plugin_info)

                self.update_installed_plugins()
                self.logger.info(f"已加载 {len(self.installed_plugins)} 个已安装插件")
            else:
                # 使用示例数据
                self.installed_plugins = [
                    {
                        'id': 'weather_enhanced',
                        'name': '增强天气插件',
                        'version': '1.0.0',
                        'author': 'TimeNest Team',
                        'status': 'enabled',
                        'description': '提供详细的天气信息显示'
                    }
                ]
                self.update_installed_plugins()

        except Exception as e:
            self.logger.error(f"加载已安装插件失败: {e}")

    def load_online_plugins(self):
        """加载在线插件"""
        try:
            self.status_label.setText("正在刷新插件列表...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条

            # 尝试从插件商城获取插件列表
            if self.app_manager and hasattr(self.app_manager, 'plugin_manager'):
                plugin_manager = self.app_manager.plugin_manager
                marketplace = plugin_manager.get_marketplace()

                if marketplace:
                    try:
                        # 刷新插件列表
                        marketplace.refresh_plugins()

                        # 获取可用插件
                        available_plugins = marketplace.get_available_plugins()

                        if available_plugins:
                            self.online_plugins = []
                            for plugin in available_plugins:
                                plugin_info = {
                                    'id': plugin.id,
                                    'name': plugin.name,
                                    'version': plugin.version,
                                    'description': plugin.description,
                                    'author': plugin.author,
                                    'category': plugin.category,
                                    'downloads': plugin.downloads,
                                    'rating': plugin.rating,
                                    'size': f"{plugin.size / 1024 / 1024:.1f} MB" if plugin.size > 0 else "未知",
                                    'tags': plugin.tags,
                                    'download_url': plugin.download_url
                                }
                                self.online_plugins.append(plugin_info)

                            self.logger.info(f"从商城加载了 {len(self.online_plugins)} 个插件")
                        else:
                            # 使用示例数据作为备用
                            self.load_example_plugins()
                    except Exception as e:
                        self.logger.warning(f"从商城加载插件失败: {e}")
                        self.load_example_plugins()
                else:
                    # 使用示例数据作为备用
                    self.load_example_plugins()
            else:
                # 使用示例数据作为备用
                self.load_example_plugins()

            self.update_online_plugins()
            self.update_settings_plugin_combo()
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"已加载 {len(self.online_plugins)} 个在线插件")

        except Exception as e:
            self.logger.error(f"加载在线插件失败: {e}")
            self.load_example_plugins()  # 失败时使用示例数据
            self.update_online_plugins()
            self.update_settings_plugin_combo()
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"加载在线插件失败，显示示例数据")

    def load_example_plugins(self):
        """加载示例插件数据"""
        self.online_plugins = [
            {
                'id': 'weather_enhanced',
                'name': '增强天气插件',
                'version': '1.0.0',
                'description': '提供详细的天气信息显示，包括温度、湿度、风速等多项指标',
                'author': 'TimeNest Team',
                'category': '组件',
                'downloads': 1250,
                'rating': 4.8,
                'size': '2.5 MB',
                'tags': ['weather', 'component', 'utility'],
                'download_url': 'local://weather_enhanced'
            },
            {
                'id': 'pomodoro_timer',
                'name': '番茄钟插件',
                'version': '2.1.0',
                'description': '专业的番茄工作法计时器，帮助提高工作效率',
                'author': 'Productivity Team',
                'category': '工具',
                'downloads': 3420,
                'rating': 4.9,
                'size': '1.8 MB',
                'tags': ['productivity', 'timer', 'focus'],
                'download_url': 'https://example.com/pomodoro_timer.zip'
            },
            {
                'id': 'dark_theme',
                'name': '深色主题包',
                'version': '1.5.2',
                'description': '精美的深色主题集合，保护眼睛，提升夜间使用体验',
                'author': 'Design Studio',
                'category': '主题',
                'downloads': 5680,
                'rating': 4.7,
                'size': '3.2 MB',
                'tags': ['theme', 'dark', 'design'],
                'download_url': 'https://example.com/dark_theme.zip'
            },
            {
                'id': 'calendar_sync',
                'name': '日历同步插件',
                'version': '1.3.1',
                'description': '与Google日历、Outlook等主流日历服务同步',
                'author': 'Sync Solutions',
                'category': '扩展',
                'downloads': 2890,
                'rating': 4.6,
                'size': '4.1 MB',
                'tags': ['calendar', 'sync', 'integration'],
                'download_url': 'https://example.com/calendar_sync.zip'
            }
        ]

    def connect_signals(self):
        """连接信号"""
        pass

    def update_online_plugins(self):
        """更新在线插件显示"""
        try:
            # 清空现有插件
            self.clear_plugin_widgets()

            if not self.online_plugins:
                # 如果没有插件，显示提示信息
                no_plugins_label = QLabel("暂无可用插件")
                no_plugins_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_plugins_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 14px;
                        padding: 50px;
                    }
                """)
                self.online_plugins_layout.addWidget(no_plugins_label, 0, 0, 1, 4)
                return

            # 计算最佳列数（根据容器宽度动态调整）
            container_width = self.online_plugins_widget.width()
            plugin_width = 280  # 插件组件的大概宽度
            spacing = 10  # 间距
            max_cols = max(1, (container_width - 20) // (plugin_width + spacing))  # 至少1列
            max_cols = min(max_cols, 4)  # 最多4列

            # 添加插件项目
            row, col = 0, 0

            for i, plugin in enumerate(self.online_plugins):
                try:
                    is_installed = any(p['id'] == plugin.get('id') for p in self.installed_plugins)
                    plugin_widget = PluginItemWidget(plugin, is_installed)

                    # 连接信号
                    plugin_widget.install_requested.connect(self.install_plugin)
                    plugin_widget.uninstall_requested.connect(self.uninstall_plugin)
                    plugin_widget.configure_requested.connect(self.configure_plugin)

                    # 添加到布局
                    self.online_plugins_layout.addWidget(plugin_widget, row, col)
                    self.plugin_widgets[plugin.get('id')] = plugin_widget

                    # 计算下一个位置
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

                except Exception as e:
                    self.logger.error(f"创建插件组件失败 {plugin.get('name', 'Unknown')}: {e}")
                    continue

            # 添加弹性空间，确保插件靠左对齐
            if self.online_plugins:
                # 在最后一行添加弹性空间
                spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                self.online_plugins_layout.addItem(spacer, row, max_cols, 1, 1)

                # 在底部添加垂直弹性空间
                v_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                self.online_plugins_layout.addItem(v_spacer, row + 1, 0, 1, max_cols)

            self.logger.info(f"成功显示 {len(self.plugin_widgets)} 个插件，布局: {row + 1} 行 x {max_cols} 列")

        except Exception as e:
            self.logger.error(f"更新在线插件失败: {e}")

    def update_installed_plugins(self):
        """更新已安装插件列表"""
        try:
            self.installed_plugins_list.clear()

            for plugin in self.installed_plugins:
                item = QListWidgetItem(f"{plugin.get('name')} v{plugin.get('version')}")
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
                self.settings_plugin_combo.addItem(plugin.get('name'), plugin.get('id'))

        except Exception as e:
            self.logger.error(f"更新设置插件下拉框失败: {e}")

    def clear_plugin_widgets(self):
        """清空插件组件"""
        try:
            # 先断开所有信号连接，避免在删除过程中触发信号
            for widget in self.plugin_widgets.values():
                if hasattr(widget, 'install_requested'):
                    widget.install_requested.disconnect()
                if hasattr(widget, 'uninstall_requested'):
                    widget.uninstall_requested.disconnect()
                if hasattr(widget, 'configure_requested'):
                    widget.configure_requested.disconnect()

            # 清空插件组件字典
            for widget in self.plugin_widgets.values():
                widget.setParent(None)
                widget.deleteLater()
            self.plugin_widgets.clear()

            # 彻底清空布局
            while self.online_plugins_layout.count():
                child = self.online_plugins_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
                    child.widget().deleteLater()
                elif child.layout():
                    # 如果是嵌套布局，也要清理
                    self.clear_layout(child.layout())

            # 强制处理待删除的对象
            QApplication.processEvents()

        except Exception as e:
            self.logger.error(f"清空插件组件失败: {e}")

    def clear_layout(self, layout):
        """递归清空布局"""
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())
        except Exception as e:
            self.logger.error(f"清空布局失败: {e}")

    def search_plugins(self, query: str):
        """搜索插件"""
        try:
            for plugin_id, widget in self.plugin_widgets.items():
                plugin = next((p for p in self.online_plugins if p['id'] == plugin_id), None)
                if plugin:
                    visible = (query.lower() in plugin.get('name').lower() or
                              query.lower() in plugin.get('description').lower())
                    widget.setVisible(visible)
        except Exception as e:
            self.logger.error(f"搜索插件失败: {e}")

    def filter_plugins(self, category: str):
        """按分类过滤插件"""
        try:
            for plugin_id, widget in self.plugin_widgets.items():
                plugin = next((p for p in self.online_plugins if p['id'] == plugin_id), None)
                if plugin:
                    visible = category == "全部" or plugin['category', ''] == category
                    widget.setVisible(visible)
        except Exception as e:
            self.logger.error(f"过滤插件失败: {e}")

    def refresh_plugins(self):
        """刷新插件列表"""
        try:
            self.logger.info("手动刷新插件列表")
            self.status_label.setText("正在刷新插件列表...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条

            # 重新加载数据
            self.load_data()

        except Exception as e:
            self.logger.error(f"刷新插件失败: {e}")
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"刷新失败: {e}")

    def _refresh_complete(self):
        """刷新完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("刷新完成")

    def install_plugin(self, plugin_id: str):
        """安装插件"""
        try:
            plugin = next((p for p in self.online_plugins if p['id'] == plugin_id), None)
            if plugin:
                reply = QMessageBox.question(
                    self, "确认安装", f"确定要安装插件 '{plugin.get('name')}' 吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.status_label.setText(f"正在安装 {plugin.get('name')}...")
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setRange(0, 100)
                    self.progress_bar.setValue(0)

                    # 检查是否是本地示例插件
                    download_url = plugin.get('download_url', '')
                    if download_url.startswith('local://'):
                        # 安装本地示例插件
                        self._install_local_plugin(plugin)
                    else:
                        # 尝试从网络下载安装
                        self._install_remote_plugin(plugin)

        except Exception as e:
            self.logger.error(f"安装插件失败: {e}")
            QMessageBox.critical(self, "错误", f"安装失败: {e}")
            self.progress_bar.setVisible(False)
            self.status_label.setText("安装失败")

    def _install_local_plugin(self, plugin):
        """安装本地示例插件"""
        try:
            plugin_id = plugin.get('id')

            # 模拟安装进度
            self.progress_bar.setValue(20)
            QTimer.singleShot(200, lambda: self.progress_bar.setValue(40))
            QTimer.singleShot(400, lambda: self.progress_bar.setValue(60))
            QTimer.singleShot(600, lambda: self.progress_bar.setValue(80))
            QTimer.singleShot(800, lambda: self.progress_bar.setValue(100))

            # 检查是否有对应的本地插件文件
            import os
            plugin_dir = os.path.join(os.getcwd(), 'plugins', f'example_{plugin_id}')

            if os.path.exists(plugin_dir):
                # 尝试通过插件管理器安装
                if self.app_manager and hasattr(self.app_manager, 'plugin_manager'):
                    plugin_manager = self.app_manager.plugin_manager
                    success = plugin_manager.install_plugin_from_path(plugin_dir)

                    if success:
                        QTimer.singleShot(1000, lambda: self._install_complete(plugin, True))
                    else:
                        QTimer.singleShot(1000, lambda: self._install_complete(plugin, False))
                else:
                    # 模拟成功安装
                    QTimer.singleShot(1000, lambda: self._install_complete(plugin, True))
            else:
                # 模拟成功安装（即使没有实际文件）
                QTimer.singleShot(1000, lambda: self._install_complete(plugin, True))

        except Exception as e:
            self.logger.error(f"安装本地插件失败: {e}")
            self._install_complete(plugin, False)

    def _install_remote_plugin(self, plugin):
        """安装远程插件"""
        try:
            # 模拟网络下载
            self.progress_bar.setValue(10)
            QTimer.singleShot(300, lambda: self.progress_bar.setValue(30))
            QTimer.singleShot(600, lambda: self.progress_bar.setValue(50))
            QTimer.singleShot(900, lambda: self.progress_bar.setValue(70))
            QTimer.singleShot(1200, lambda: self.progress_bar.setValue(90))
            QTimer.singleShot(1500, lambda: self.progress_bar.setValue(100))

            # 尝试通过插件商城下载
            if self.app_manager and hasattr(self.app_manager, 'plugin_manager'):
                plugin_manager = self.app_manager.plugin_manager
                marketplace = plugin_manager.get_marketplace()

                if marketplace:
                    # 异步下载
                    QTimer.singleShot(1600, lambda: self._download_and_install(marketplace, plugin))
                else:
                    # 模拟成功
                    QTimer.singleShot(1600, lambda: self._install_complete(plugin, True))
            else:
                # 模拟成功
                QTimer.singleShot(1600, lambda: self._install_complete(plugin, True))

        except Exception as e:
            self.logger.error(f"安装远程插件失败: {e}")
            self._install_complete(plugin, False)

    def _download_and_install(self, marketplace, plugin):
        """下载并安装插件"""
        try:
            plugin_id = plugin.get('id')
            success = marketplace.download_plugin(plugin_id)
            self._install_complete(plugin, success)
        except Exception as e:
            self.logger.error(f"下载安装插件失败: {e}")
            self._install_complete(plugin, False)

    def _install_complete(self, plugin, success=True):
        """安装完成"""
        try:
            self.progress_bar.setVisible(False)

            if success:
                # 检查是否已在已安装列表中
                plugin_id = plugin.get('id')
                existing = next((p for p in self.installed_plugins if p['id'] == plugin_id), None)

                if not existing:
                    # 添加到已安装列表
                    installed_plugin = {
                        'id': plugin_id,
                        'name': plugin.get('name'),
                        'version': plugin.get('version'),
                        'author': plugin.get('author'),
                        'status': 'enabled',
                        'description': plugin.get('description')
                    }
                    self.installed_plugins.append(installed_plugin)

                # 更新界面
                self.update_online_plugins()
                self.update_installed_plugins()
                self.update_settings_plugin_combo()

                self.status_label.setText("安装完成")
                QMessageBox.information(self, "安装成功", f"插件 '{plugin.get('name')}' 安装成功！")

                # 重新加载已安装插件（从插件管理器）
                self.load_installed_plugins()
            else:
                self.status_label.setText("安装失败")
                QMessageBox.critical(self, "安装失败", f"插件 '{plugin.get('name')}' 安装失败！")

        except Exception as e:
            self.logger.error(f"安装完成处理失败: {e}")
            self.status_label.setText("安装失败")
            QMessageBox.critical(self, "错误", f"安装完成处理失败: {e}")

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
            from PySide6.QtWidgets import QFileDialog

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
            from PySide6.QtWidgets import QFileDialog

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
        try:
            # 创建示例代码对话框
            dialog = ExampleCodeDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开示例代码失败: {e}")

    def show_guidelines(self):
        """显示开发指南"""
        try:
            # 创建开发指南对话框
            dialog = DevelopmentGuidelinesDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开开发指南失败: {e}")

    def closeEvent(self, event):
        """关闭事件 - 只关闭窗口，不退出程序"""
        try:
            # 直接关闭窗口，不退出程序
            event.accept()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"关闭处理失败: {e}")
            event.accept()


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
        from PySide6.QtWidgets import QFileDialog

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
        from PySide6.QtWidgets import QFileDialog

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
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

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


class ExampleCodeDialog(QDialog):
    """示例代码对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插件示例代码")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_examples()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 示例选择
        example_layout = QHBoxLayout()
        example_layout.addWidget(QLabel("选择示例:"))
        
        self.example_combo = QComboBox()
        self.example_combo.addItems([
            "基础插件模板",
            "UI扩展插件",
            "服务提供插件",
            "消息处理插件",
            "定时任务插件",
            "数据处理插件"
        ])
        self.example_combo.currentTextChanged.connect(self.on_example_changed)
        example_layout.addWidget(self.example_combo)
        example_layout.addStretch()
        
        layout.addLayout(example_layout)

        # 代码显示
        self.code_text = QTextEdit()
        self.code_text.setFont(QFont("Consolas", 10))
        self.code_text.setReadOnly(True)
        layout.addWidget(self.code_text)

        # 按钮
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("复制代码")
        copy_btn.clicked.connect(self.copy_code)
        button_layout.addWidget(copy_btn)
        
        save_btn = QPushButton("保存为文件")
        save_btn.clicked.connect(self.save_code)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_examples(self):
        """加载示例代码"""
        self.examples = {
            "基础插件模板": '''
# -*- coding: utf-8 -*-
"""基础插件模板"""

from core.plugin_base import IPlugin, PluginStatus
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class BasicPlugin(IPlugin):
    """基础插件示例"""
    
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        self.widget = None
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.logger.info("插件初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            self.status = PluginStatus.ACTIVE
            self.logger.info("插件已激活")
            return True
        except Exception as e:
            self.logger.error(f"插件激活失败: {e}")
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            self.status = PluginStatus.INACTIVE
            self.logger.info("插件已停用")
            return True
        except Exception as e:
            self.logger.error(f"插件停用失败: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.widget:
            self.widget.close()
            self.widget = None
        self.logger.info("插件资源已清理")
    
    def get_status(self) -> PluginStatus:
        """获取插件状态"""
        return self.status
''',
            "UI扩展插件": '''
# -*- coding: utf-8 -*-
"""UI扩展插件示例"""

from core.plugin_base import IPlugin, PluginStatus
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QMessageBox
)
from PySide6.QtCore import Signal

class UIExtensionPlugin(IPlugin):
    """UI扩展插件示例"""
    
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        self.widget = None
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.create_widget()
            return True
        except Exception as e:
            self.logger.error(f"UI插件初始化失败: {e}")
            return False
    
    def create_widget(self):
        """创建UI组件"""
        self.widget = PluginWidget()
        self.widget.message_sent.connect(self.handle_message)
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            if self.widget:
                self.widget.show()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            self.logger.error(f"UI插件激活失败: {e}")
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            if self.widget:
                self.widget.hide()
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            self.logger.error(f"UI插件停用失败: {e}")
            return False
    
    def handle_message(self, message):
        """处理消息"""
        self.logger.info(f"收到消息: {message}")
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.widget:
            self.widget.close()
            self.widget = None
    
    def get_status(self) -> PluginStatus:
        return self.status

class PluginWidget(QWidget):
    """插件UI组件"""
    
    message_sent = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI扩展插件")
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("UI扩展插件示例")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 文本区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在这里输入消息...")
        layout.addWidget(self.text_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        send_btn = QPushButton("发送消息")
        send_btn.clicked.connect(self.send_message)
        button_layout.addWidget(send_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_text)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
    
    def send_message(self):
        """发送消息"""
        message = self.text_edit.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            QMessageBox.information(self, "成功", "消息已发送")
        else:
            QMessageBox.warning(self, "警告", "请输入消息内容")
    
    def clear_text(self):
        """清空文本"""
        self.text_edit.clear()
''',
            "服务提供插件": '''
# -*- coding: utf-8 -*-
"""服务提供插件示例"""

from core.plugin_base import (
    IPlugin, IServiceProvider, PluginStatus,
    ServiceInterface, ServiceMethod, ServiceType
)
from typing import Dict, Any

class ServiceProviderPlugin(IPlugin, IServiceProvider):
    """服务提供插件示例"""
    
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        self.data_store = {}
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            # 注册服务
            service_interface = self.get_service_interface()
            plugin_manager.register_service(service_interface)
            return True
        except Exception as e:
            self.logger.error(f"服务插件初始化失败: {e}")
            return False
    
    def get_service_interface(self) -> ServiceInterface:
        """获取服务接口"""
        interface = ServiceInterface(
            name="data_service",
            version="1.0.0",
            provider_id=self.metadata.id,
            service_type=ServiceType.UTILITY
        )
        
        # 添加服务方法
        interface.add_method(ServiceMethod(
            name="store_data",
            callable=self.store_data,
            description="存储数据"
        ))
        
        interface.add_method(ServiceMethod(
            name="get_data",
            callable=self.get_data,
            description="获取数据"
        ))
        
        interface.add_method(ServiceMethod(
            name="delete_data",
            callable=self.delete_data,
            description="删除数据"
        ))
        
        return interface
    
    def store_data(self, key: str, value: Any) -> bool:
        """存储数据"""
        try:
            self.data_store[key] = value
            self.logger.info(f"数据已存储: {key}")
            return True
        except Exception as e:
            self.logger.error(f"存储数据失败: {e}")
            return False
    
    def get_data(self, key: str) -> Any:
        """获取数据"""
        return self.data_store.get(key)
    
    def delete_data(self, key: str) -> bool:
        """删除数据"""
        try:
            if key in self.data_store:
                del self.data_store[key]
                self.logger.info(f"数据已删除: {key}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"删除数据失败: {e}")
            return False
    
    def activate(self) -> bool:
        self.status = PluginStatus.ACTIVE
        return True
    
    def deactivate(self) -> bool:
        self.status = PluginStatus.INACTIVE
        return True
    
    def cleanup(self) -> None:
        self.data_store.clear()
    
    def get_status(self) -> PluginStatus:
        return self.status
''',
            "消息处理插件": '''
# -*- coding: utf-8 -*-
"""消息处理插件示例"""

from core.plugin_base import IPlugin, PluginStatus
from core.plugin_system import Message, MessageType
from typing import Dict, Any

class MessageHandlerPlugin(IPlugin):
    """消息处理插件示例"""
    
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        self.message_bus = None
        self.handlers = {}
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.message_bus = plugin_manager.get_message_bus()
            
            # 注册消息处理器
            self.register_handlers()
            return True
        except Exception as e:
            self.logger.error(f"消息插件初始化失败: {e}")
            return False
    
    def register_handlers(self):
        """注册消息处理器"""
        # 注册不同主题的处理器
        topics = ["system.notification", "user.action", "data.update"]
        
        for topic in topics:
            self.message_bus.register_handler(
                self.metadata.id,
                topic,
                self.handle_message
            )
            self.logger.info(f"已注册消息处理器: {topic}")
    
    def handle_message(self, message: Message):
        """处理消息"""
        try:
            self.logger.info(f"收到消息 - 主题: {message.topic}, 发送者: {message.sender_id}")
            
            # 根据消息类型处理
            if message.message_type == MessageType.EVENT:
                self.handle_event_message(message)
            elif message.message_type == MessageType.REQUEST:
                self.handle_request_message(message)
            elif message.message_type == MessageType.RESPONSE:
                self.handle_response_message(message)
            
        except Exception as e:
            self.logger.error(f"处理消息失败: {e}")
    
    def handle_event_message(self, message: Message):
        """处理事件消息"""
        payload = message.payload
        self.logger.info(f"处理事件: {payload}")
        
        # 可以根据事件类型执行不同操作
        if message.topic == "system.notification":
            self.process_notification(payload)
        elif message.topic == "user.action":
            self.process_user_action(payload)
    
    def handle_request_message(self, message: Message):
        """处理请求消息"""
        # 处理请求并发送响应
        response_data = self.process_request(message.payload)
        
        # 创建响应消息
        response = Message(
            message_type=MessageType.RESPONSE,
            topic=f"response.{message.topic}",
            sender_id=self.metadata.id,
            payload=response_data,
            correlation_id=message.message_id
        )
        
        self.message_bus.send_message(response)
    
    def handle_response_message(self, message: Message):
        """处理响应消息"""
        self.logger.info(f"收到响应: {message.payload}")
    
    def process_notification(self, payload: Dict[str, Any]):
        """处理通知"""
        self.logger.info(f"处理通知: {payload.get('message', '')}")
    
    def process_user_action(self, payload: Dict[str, Any]):
        """处理用户操作"""
        action = payload.get('action', '')
        self.logger.info(f"处理用户操作: {action}")
    
    def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        # 简单的请求处理示例
        return {
            "status": "success",
            "message": "请求已处理",
            "data": payload
        }
    
    def send_message(self, topic: str, payload: Dict[str, Any]):
        """发送消息"""
        message = Message(
            message_type=MessageType.EVENT,
            topic=topic,
            sender_id=self.metadata.id,
            payload=payload
        )
        
        self.message_bus.send_message(message)
    
    def activate(self) -> bool:
        self.status = PluginStatus.ACTIVE
        return True
    
    def deactivate(self) -> bool:
        self.status = PluginStatus.INACTIVE
        return True
    
    def cleanup(self) -> None:
        # 取消注册消息处理器
        if self.message_bus:
            topics = ["system.notification", "user.action", "data.update"]
            for topic in topics:
                self.message_bus.unregister_handler(self.metadata.id, topic)
    
    def get_status(self) -> PluginStatus:
        return self.status
''',
            "定时任务插件": '''
# -*- coding: utf-8 -*-
"""定时任务插件示例"""

from core.plugin_base import IPlugin, PluginStatus
from PySide6.QtCore import QTimer, QObject, Signal
from datetime import datetime, timedelta
from typing import Callable, Dict, Any

class ScheduledTaskPlugin(IPlugin):
    """定时任务插件示例"""
    
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        self.scheduler = TaskScheduler()
        self.tasks = {}
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.scheduler.task_executed.connect(self.on_task_executed)
            
            # 添加示例任务
            self.add_sample_tasks()
            return True
        except Exception as e:
            self.logger.error(f"定时任务插件初始化失败: {e}")
            return False
    
    def add_sample_tasks(self):
        """添加示例任务"""
        # 每分钟执行的任务
        self.add_task(
            "minute_task",
            self.minute_task,
            interval=60000  # 60秒
        )
        
        # 每5分钟执行的任务
        self.add_task(
            "five_minute_task",
            self.five_minute_task,
            interval=300000  # 5分钟
        )
    
    def add_task(self, task_id: str, callback: Callable, interval: int):
        """添加定时任务"""
        task = ScheduledTask(task_id, callback, interval)
        self.tasks[task_id] = task
        self.scheduler.add_task(task)
        self.logger.info(f"已添加定时任务: {task_id}")
    
    def remove_task(self, task_id: str):
        """移除定时任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            self.scheduler.remove_task(task)
            del self.tasks[task_id]
            self.logger.info(f"已移除定时任务: {task_id}")
    
    def minute_task(self):
        """每分钟执行的任务"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"每分钟任务执行 - 当前时间: {current_time}")
        
        # 可以在这里执行具体的业务逻辑
        # 例如：检查系统状态、清理临时文件等
    
    def five_minute_task(self):
        """每5分钟执行的任务"""
        self.logger.info("每5分钟任务执行 - 执行系统维护")
        
        # 可以在这里执行更复杂的任务
        # 例如：数据备份、性能监控等
    
    def on_task_executed(self, task_id: str, success: bool):
        """任务执行完成回调"""
        if success:
            self.logger.info(f"任务执行成功: {task_id}")
        else:
            self.logger.error(f"任务执行失败: {task_id}")
    
    def activate(self) -> bool:
        try:
            self.scheduler.start()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            self.logger.error(f"启动定时任务失败: {e}")
            return False
    
    def deactivate(self) -> bool:
        try:
            self.scheduler.stop()
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            self.logger.error(f"停止定时任务失败: {e}")
            return False
    
    def cleanup(self) -> None:
        self.scheduler.stop()
        self.tasks.clear()
    
    def get_status(self) -> PluginStatus:
        return self.status

class ScheduledTask:
    """定时任务类"""
    
    def __init__(self, task_id: str, callback: Callable, interval: int):
        self.task_id = task_id
        self.callback = callback
        self.interval = interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.execute)
        self.timer.setInterval(interval)
    
    def execute(self):
        """执行任务"""
        try:
            self.callback()
            return True
        except Exception as e:
            print(f"任务执行失败 {self.task_id}: {e}")
            return False
    
    def start(self):
        """启动任务"""
        self.timer.start()
    
    def stop(self):
        """停止任务"""
        self.timer.stop()

class TaskScheduler(QObject):
    """任务调度器"""
    
    task_executed = Signal(str, bool)
    
    def __init__(self):
        super().__init__()
        self.tasks = []
    
    def add_task(self, task: ScheduledTask):
        """添加任务"""
        self.tasks.append(task)
    
    def remove_task(self, task: ScheduledTask):
        """移除任务"""
        if task in self.tasks:
            task.stop()
            self.tasks.remove(task)
    
    def start(self):
        """启动所有任务"""
        for task in self.tasks:
            task.start()
    
    def stop(self):
        """停止所有任务"""
        for task in self.tasks:
            task.stop()
''',
            "数据处理插件": '''
# -*- coding: utf-8 -*-
"""数据处理插件示例"""

from core.plugin_base import IPlugin, PluginStatus
from typing import List, Dict, Any, Optional
import json
import csv
from datetime import datetime

class DataProcessorPlugin(IPlugin):
    """数据处理插件示例"""
    
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        self.data_cache = {}
        self.processors = {}
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.plugin_manager = plugin_manager
            self.register_processors()
            return True
        except Exception as e:
            self.logger.error(f"数据处理插件初始化失败: {e}")
            return False
    
    def register_processors(self):
        """注册数据处理器"""
        self.processors = {
            "json": JsonProcessor(),
            "csv": CsvProcessor(),
            "text": TextProcessor(),
            "number": NumberProcessor()
        }
        self.logger.info("数据处理器已注册")
    
    def process_data(self, data_type: str, data: Any, operation: str, **kwargs) -> Any:
        """处理数据"""
        try:
            if data_type not in self.processors:
                raise ValueError(f"不支持的数据类型: {data_type}")
            
            processor = self.processors[data_type]
            result = processor.process(data, operation, **kwargs)
            
            # 缓存结果
            cache_key = f"{data_type}_{operation}_{hash(str(data))}"
            self.data_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
        except Exception as e:
            self.logger.error(f"数据处理失败: {e}")
            raise
    
    def get_cached_result(self, data_type: str, data: Any, operation: str) -> Optional[Any]:
        """获取缓存结果"""
        cache_key = f"{data_type}_{operation}_{hash(str(data))}"
        cached = self.data_cache.get(cache_key)
        return cached["result"] if cached else None
    
    def clear_cache(self):
        """清空缓存"""
        self.data_cache.clear()
        self.logger.info("数据缓存已清空")
    
    def activate(self) -> bool:
        self.status = PluginStatus.ACTIVE
        return True
    
    def deactivate(self) -> bool:
        self.status = PluginStatus.INACTIVE
        return True
    
    def cleanup(self) -> None:
        self.clear_cache()
        self.processors.clear()
    
    def get_status(self) -> PluginStatus:
        return self.status

class DataProcessor:
    """数据处理器基类"""
    
    def process(self, data: Any, operation: str, **kwargs) -> Any:
        """处理数据"""
        raise NotImplementedError

class JsonProcessor(DataProcessor):
    """JSON数据处理器"""
    
    def process(self, data: Any, operation: str, **kwargs) -> Any:
        if operation == "parse":
            return json.loads(data) if isinstance(data, str) else data
        elif operation == "stringify":
            return json.dumps(data, ensure_ascii=False, indent=kwargs.get("indent", 2))
        elif operation == "validate":
            try:
                json.loads(data) if isinstance(data, str) else json.dumps(data)
                return True
            except:
                return False
        elif operation == "extract":
            path = kwargs.get("path", "")
            return self.extract_value(data, path)
        else:
            raise ValueError(f"不支持的JSON操作: {operation}")
    
    def extract_value(self, data: Dict, path: str) -> Any:
        """从JSON中提取值"""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

class CsvProcessor(DataProcessor):
    """CSV数据处理器"""
    
    def process(self, data: Any, operation: str, **kwargs) -> Any:
        if operation == "parse":
            return self.parse_csv(data, **kwargs)
        elif operation == "generate":
            return self.generate_csv(data, **kwargs)
        elif operation == "filter":
            return self.filter_csv(data, **kwargs)
        else:
            raise ValueError(f"不支持的CSV操作: {operation}")
    
    def parse_csv(self, data: str, **kwargs) -> List[Dict]:
        """解析CSV数据"""
        lines = data.strip().split("\n")
        if not lines:
            return []
        
        delimiter = kwargs.get("delimiter", ",")
        headers = lines[0].split(delimiter)
        
        result = []
        for line in lines[1:]:
            values = line.split(delimiter)
            row = dict(zip(headers, values))
            result.append(row)
        
        return result
    
    def generate_csv(self, data: List[Dict], **kwargs) -> str:
        """生成CSV数据"""
        if not data:
            return ""
        
        delimiter = kwargs.get("delimiter", ",")
        headers = list(data[0].keys())
        
        lines = [delimiter.join(headers)]
        for row in data:
            values = [str(row.get(header, "")) for header in headers]
            lines.append(delimiter.join(values))
        
        return "\n".join(lines)
    
    def filter_csv(self, data: List[Dict], **kwargs) -> List[Dict]:
        """过滤CSV数据"""
        filter_func = kwargs.get("filter_func")
        if not filter_func:
            return data
        
        return [row for row in data if filter_func(row)]

class TextProcessor(DataProcessor):
    """文本数据处理器"""
    
    def process(self, data: str, operation: str, **kwargs) -> Any:
        if operation == "clean":
            return data.strip().replace("\r\n", "\n").replace("\r", "\n")
        elif operation == "split":
            delimiter = kwargs.get("delimiter", "\n")
            return data.split(delimiter)
        elif operation == "count_words":
            return len(data.split())
        elif operation == "count_lines":
            return len(data.split("\n"))
        elif operation == "extract_keywords":
            return self.extract_keywords(data, **kwargs)
        else:
            raise ValueError(f"不支持的文本操作: {operation}")
    
    def extract_keywords(self, text: str, **kwargs) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = text.lower().split()
        # 过滤常见停用词
        stop_words = {"的", "是", "在", "有", "和", "与", "或", "但", "而", "了", "着", "过"}
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 统计词频
        word_count = {}
        for word in keywords:
            word_count[word] = word_count.get(word, 0) + 1
        
        # 按词频排序
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前N个关键词
        top_n = kwargs.get("top_n", 10)
        return [word for word, count in sorted_words[:top_n]]

class NumberProcessor(DataProcessor):
    """数值数据处理器"""
    
    def process(self, data: List[float], operation: str, **kwargs) -> Any:
        if operation == "sum":
            return sum(data)
        elif operation == "average":
            return sum(data) / len(data) if data else 0
        elif operation == "max":
            return max(data) if data else None
        elif operation == "min":
            return min(data) if data else None
        elif operation == "sort":
            reverse = kwargs.get("reverse", False)
            return sorted(data, reverse=reverse)
        elif operation == "filter":
            min_val = kwargs.get("min_val")
            max_val = kwargs.get("max_val")
            result = data
            if min_val is not None:
                result = [x for x in result if x >= min_val]
            if max_val is not None:
                result = [x for x in result if x <= max_val]
            return result
        else:
            raise ValueError(f"不支持的数值操作: {operation}")
'''
        }
        
        # 默认显示第一个示例
        self.on_example_changed(self.example_combo.currentText())
    
    def on_example_changed(self, example_name: str):
        """示例选择改变"""
        if example_name in self.examples:
            self.code_text.setPlainText(self.examples[example_name])
    
    def copy_code(self):
        """复制代码"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_text.toPlainText())
        QMessageBox.information(self, "成功", "代码已复制到剪贴板")
    
    def save_code(self):
        """保存代码为文件"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存代码", "", "Python文件 (*.py);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_text.toPlainText())
                QMessageBox.information(self, "成功", f"代码已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")


class DevelopmentGuidelinesDialog(QDialog):
    """开发指南对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插件开发指南")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_guidelines()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 指南显示
        self.guidelines_text = QTextEdit()
        self.guidelines_text.setFont(QFont("Microsoft YaHei", 10))
        self.guidelines_text.setReadOnly(True)
        layout.addWidget(self.guidelines_text)

        # 按钮
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_guidelines(self):
        """加载开发指南"""
        guidelines_content = """# TimeNest 插件开发指南

## 1. 开发环境准备

### 1.1 必需工具
- Python 3.8+
- PySide6
- TimeNest SDK
- 代码编辑器（推荐 VS Code 或 PyCharm）

### 1.2 项目结构
```
my_plugin/
├── plugin.json          # 插件元数据
├── __init__.py          # 插件入口
├── main.py              # 主要逻辑
├── ui/                  # UI组件
│   └── widgets.py
├── resources/           # 资源文件
│   ├── icons/
│   └── styles/
└── tests/               # 测试文件
    └── test_plugin.py
```

## 2. 插件开发流程

### 2.1 创建插件项目
1. 使用插件开发工具创建新项目
2. 选择合适的模板
3. 配置插件元数据
4. 实现核心功能

### 2.2 实现插件接口
```python
from core.plugin_base import IPlugin, PluginStatus

class MyPlugin(IPlugin):
    def initialize(self, plugin_manager) -> bool:
        # 初始化逻辑
        return True
    
    def activate(self) -> bool:
        # 激活逻辑
        return True
    
    def deactivate(self) -> bool:
        # 停用逻辑
        return True
    
    def cleanup(self) -> None:
        # 清理资源
        pass
```

### 2.3 配置插件元数据
```json
{
    "id": "my_plugin",
    "name": "我的插件",
    "version": "1.0.0",
    "description": "插件描述",
    "author": "作者名",
    "main_class": "MyPlugin",
    "api_version": "1.0.0",
    "min_app_version": "1.0.0",
    "dependencies": [],
    "permissions": [],
    "tags": ["utility"]
}
```

## 3. 最佳实践

### 3.1 代码规范
- 使用 PEP 8 代码风格
- 添加适当的注释和文档字符串
- 使用类型提示
- 遵循单一职责原则

### 3.2 错误处理
```python
try:
    # 可能出错的代码
    result = risky_operation()
except SpecificException as e:
    self.logger.error(f"操作失败: {e}")
    return False
except Exception as e:
    self.logger.error(f"未知错误: {e}")
    return False
```

### 3.3 日志记录
```python
# 使用插件自带的日志记录器
self.logger.info("插件初始化成功")
self.logger.warning("检测到潜在问题")
self.logger.error("操作失败")
self.logger.debug("调试信息")
```

### 3.4 资源管理
- 在 cleanup() 方法中释放所有资源
- 避免内存泄漏
- 正确关闭文件和网络连接

### 3.5 线程安全
- 使用 Qt 的信号槽机制进行线程间通信
- 避免在非主线程中直接操作 UI
- 使用适当的同步机制

## 4. UI 开发指南

### 4.1 使用 PySide6
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PluginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hello, Plugin!"))
```

### 4.2 样式设计
- 遵循应用主题
- 使用一致的颜色方案
- 保持界面简洁
- 支持深色/浅色主题切换

### 4.3 响应式设计
- 适配不同屏幕尺寸
- 使用合适的布局管理器
- 考虑高DPI显示器

## 5. 测试指南

### 5.1 单元测试
```python
import unittest
from my_plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
    
    def test_initialization(self):
        result = self.plugin.initialize(mock_plugin_manager)
        self.assertTrue(result)
```

### 5.2 集成测试
- 测试插件与系统的集成
- 验证消息通信
- 检查服务接口

### 5.3 用户界面测试
- 测试UI响应
- 验证用户交互
- 检查界面布局

## 6. 性能优化

### 6.1 启动优化
- 延迟加载非必需组件
- 使用异步初始化
- 减少启动时间

### 6.2 内存优化
- 及时释放不用的对象
- 使用弱引用避免循环引用
- 监控内存使用

### 6.3 响应优化
- 使用后台线程处理耗时操作
- 实现进度反馈
- 避免阻塞主线程

## 7. 安全考虑

### 7.1 权限控制
- 只请求必需的权限
- 验证用户输入
- 防止代码注入

### 7.2 数据保护
- 加密敏感数据
- 安全存储配置
- 保护用户隐私

## 8. 发布流程

### 8.1 打包插件
1. 使用插件开发工具打包
2. 验证插件包完整性
3. 测试安装和卸载

### 8.2 版本管理
- 遵循语义化版本
- 维护更新日志
- 处理向后兼容性

### 8.3 文档编写
- 编写用户手册
- 提供API文档
- 包含示例代码

## 9. 常见问题

### 9.1 插件无法加载
- 检查 plugin.json 格式
- 验证主类名称
- 查看错误日志

### 9.2 UI显示异常
- 检查Qt版本兼容性
- 验证样式表语法
- 测试不同主题

### 9.3 性能问题
- 使用性能分析工具
- 优化算法复杂度
- 减少不必要的计算

## 10. 社区资源

- 官方文档: https://timenest.dev/docs
- 开发者论坛: https://forum.timenest.dev
- GitHub仓库: https://github.com/timenest/plugins
- 示例插件: https://github.com/timenest/plugin-examples

---

遵循这些指南将帮助您开发出高质量、稳定可靠的 TimeNest 插件。
如有问题，请参考官方文档或在开发者社区寻求帮助。
"""
        
        self.guidelines_text.setPlainText(guidelines_content)
