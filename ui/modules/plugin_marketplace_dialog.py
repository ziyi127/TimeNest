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
        QMessageBox.information(self, "功能开发中", "卸载插件功能正在开发中...")

    def configure_plugin(self, plugin_id: str):
        """配置插件"""
        QMessageBox.information(self, "功能开发中", "配置插件功能正在开发中...")

    def enable_all_plugins(self):
        """启用所有插件"""
        QMessageBox.information(self, "功能开发中", "启用所有插件功能正在开发中...")

    def disable_all_plugins(self):
        """禁用所有插件"""
        QMessageBox.information(self, "功能开发中", "禁用所有插件功能正在开发中...")

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
        QMessageBox.information(self, "功能开发中", "创建新插件功能正在开发中...")

    def package_plugin(self):
        """打包插件"""
        QMessageBox.information(self, "功能开发中", "打包插件功能正在开发中...")

    def test_plugin(self):
        """测试插件"""
        QMessageBox.information(self, "功能开发中", "测试插件功能正在开发中...")

    def generate_template(self):
        """生成模板代码"""
        QMessageBox.information(self, "功能开发中", "生成模板代码功能正在开发中...")

    def show_api_docs(self):
        """显示API文档"""
        QMessageBox.information(self, "功能开发中", "API文档功能正在开发中...")

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
