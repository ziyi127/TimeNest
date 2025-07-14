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
TimeNest 关于对话框
显示应用程序信息、版本、作者等
"""

import logging
import os
import sys
import platform
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget, QWidget,
    QScrollArea, QFrame, QGroupBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtGui import QPixmap, QFont, QPalette, QDesktopServices, QIcon

# 导入版本管理器
try:
    from utils.version_manager import version_manager
except ImportError:
    # 如果导入失败，创建一个简单的备用版本（返回None）
    class SimpleVersionManager:
        def get_app_name(self): return None
        def get_full_version(self): return None
        def get_app_description(self): return None
        def get_author_display_name(self): return None
        def get_author_email(self): return None
        def get_website_url(self): return None
        def get_repository_url(self): return None
        def get_issues_url(self): return None
        def get_license(self): return None
        def get_copyright(self): return None
        def get_contributors(self): return None
        def get_main_features(self): return None
        def get_thanks_list(self): return None

    version_manager = SimpleVersionManager()


class AboutDialog(QDialog):
    """
    关于对话框
    
    显示应用程序的详细信息，包括：
    - 应用程序基本信息
    - 版本信息
    - 作者和贡献者
    - 许可证信息
    - 系统信息
    - 致谢信息
    """
    
    # 应用程序信息从版本管理器获取
    @property
    def APP_NAME(self):
        return version_manager.get_app_name()

    @property
    def APP_VERSION(self):
        return version_manager.get_full_version()

    @property
    def APP_DESCRIPTION(self):
        return version_manager.get_app_description()

    @property
    def APP_AUTHOR(self):
        return version_manager.get_author_display_name()

    @property
    def APP_EMAIL(self):
        return version_manager.get_author_email()

    @property
    def APP_WEBSITE(self):
        return version_manager.get_website_url()

    @property
    def APP_REPOSITORY(self):
        return version_manager.get_repository_url()

    @property
    def APP_LICENSE(self):
        return version_manager.get_license()
    
    def __init__(self, parent=None):
        """
        初始化关于对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.AboutDialog')
        
        # 初始化UI
        self.init_ui()
        
        # 连接信号
        self.connect_signals()
        
        self.logger.info("关于对话框初始化完成")
    
    def init_ui(self):
        """
        初始化用户界面
        """
        app_name = self.APP_NAME or "null"
        self.setWindowTitle(f"关于 {app_name}")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 关于标签页
        self.about_tab = self.create_about_tab()
        self.tab_widget.addTab(self.about_tab, "关于")
        
        # 版本信息标签页
        self.version_tab = self.create_version_tab()
        self.tab_widget.addTab(self.version_tab, "版本信息")
        
        # 作者标签页
        self.authors_tab = self.create_authors_tab()
        self.tab_widget.addTab(self.authors_tab, "作者")
        
        # 许可证标签页
        self.license_tab = self.create_license_tab()
        self.tab_widget.addTab(self.license_tab, "许可证")
        
        # 系统信息标签页
        self.system_tab = self.create_system_tab()
        self.tab_widget.addTab(self.system_tab, "系统信息")
        
        # 致谢标签页
        self.credits_tab = self.create_credits_tab()
        self.tab_widget.addTab(self.credits_tab, "致谢")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.website_btn = QPushButton("访问官网")
        self.github_btn = QPushButton("GitHub")
        self.feedback_btn = QPushButton("反馈问题")
        
        button_layout.addWidget(self.website_btn)
        button_layout.addWidget(self.github_btn)
        button_layout.addWidget(self.feedback_btn)
        button_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_about_tab(self) -> QWidget:
        """
        创建关于标签页
        
        Returns:
            关于标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 应用程序图标和名称
        header_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 优先使用app_icon.png作为关于页面的logo
        icon_loaded = False
        icon_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_32x32.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_24x24.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon_16x16.png'),
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'tray_icon.png')
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                    icon_loaded = True
                    break

        if not icon_loaded:
            # 如果没有找到图标文件，显示默认样式
            icon_label.setStyleSheet("QLabel { border: 1px solid gray; background-color: #f0f0f0; }")
            icon_label.setText("ICON")
        header_layout.addWidget(icon_label)
        
        # 应用程序信息
        info_layout = QVBoxLayout()
        
        # 应用程序名称
        app_name = self.APP_NAME or "null"
        name_label = QLabel(app_name)
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)

        # 版本
        app_version = self.APP_VERSION or "null"
        version_label = QLabel(f"版本 {app_version}")
        version_font = QFont()
        version_font.setPointSize(12)
        version_label.setFont(version_font)
        info_layout.addWidget(version_label)
        
        # 描述
        app_description = self.APP_DESCRIPTION or "null"
        desc_label = QLabel(app_description)
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 详细信息
        details_layout = QGridLayout()
        
        details_layout.addWidget(QLabel("作者:"), 0, 0)
        details_layout.addWidget(QLabel(self.APP_AUTHOR), 0, 1)
        
        details_layout.addWidget(QLabel("邮箱:"), 1, 0)
        email_label = QLabel(f'<a href="mailto:{self.APP_EMAIL}">{self.APP_EMAIL}</a>')
        email_label.setOpenExternalLinks(True)
        details_layout.addWidget(email_label, 1, 1)
        
        details_layout.addWidget(QLabel("官网:"), 2, 0)
        website_label = QLabel(f'<a href="{self.APP_WEBSITE}">{self.APP_WEBSITE}</a>')
        website_label.setOpenExternalLinks(True)
        details_layout.addWidget(website_label, 2, 1)

        details_layout.addWidget(QLabel("项目地址:"), 3, 0)
        repository_label = QLabel(f'<a href="{self.APP_REPOSITORY}">{self.APP_REPOSITORY}</a>')
        repository_label.setOpenExternalLinks(True)
        details_layout.addWidget(repository_label, 3, 1)

        details_layout.addWidget(QLabel("许可证:"), 4, 0)
        details_layout.addWidget(QLabel(self.APP_LICENSE), 4, 1)
        
        layout.addLayout(details_layout)
        
        # 功能特性
        features_group = QGroupBox("主要功能")
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "📅 智能课程表管理",
            "⏰ 课程提醒和通知",
            "📊 多样化组件显示",
            "🎨 自定义界面主题",
            "📱 系统托盘集成",
            "💾 数据导入导出",
            "🔧 丰富的配置选项",
            "🌐 多语言支持"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_group)
        
        layout.addStretch()
        
        return tab
    
    def create_version_tab(self) -> QWidget:
        """
        创建版本信息标签页
        
        Returns:
            版本信息标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 版本信息
        version_group = QGroupBox("版本信息")
        version_layout = QGridLayout(version_group)
        
        version_layout.addWidget(QLabel("应用程序版本:"), 0, 0)
        app_version = self.APP_VERSION or "null"
        version_layout.addWidget(QLabel(app_version), 0, 1)
        
        version_layout.addWidget(QLabel("构建日期:"), 1, 0)
        build_date = version_manager.get_release_date() or "null"
        version_layout.addWidget(QLabel(build_date), 1, 1)

        version_layout.addWidget(QLabel("构建号:"), 2, 0)
        build_number = version_manager.get_build_number() or "null"
        version_layout.addWidget(QLabel(build_number), 2, 1)
        
        layout.addWidget(version_group)
        
        # 依赖信息
        deps_group = QGroupBox("依赖库版本")
        deps_layout = QVBoxLayout(deps_group)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # 获取依赖信息
        dependencies = self.get_dependencies_info()
        
        row = 0
        for name, version in dependencies.items():
            scroll_layout.addWidget(QLabel(name), row, 0)
            scroll_layout.addWidget(QLabel(version), row, 1)
            row += 1
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        deps_layout.addWidget(scroll_area)
        
        layout.addWidget(deps_group)
        
        # 更新历史
        history_group = QGroupBox("更新历史")
        history_layout = QVBoxLayout(history_group)
        
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        history_text.setPlainText(self.get_update_history())
        history_layout.addWidget(history_text)
        
        layout.addWidget(history_group)
        
        return tab
    
    def create_authors_tab(self) -> QWidget:
        """
        创建作者标签页
        
        Returns:
            作者标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 主要作者
        main_authors_group = QGroupBox("主要作者")
        main_authors_layout = QVBoxLayout(main_authors_group)
        
        main_authors = []

        # 从版本管理器获取作者信息
        author_name = version_manager.get_author_display_name()
        author_email = version_manager.get_author_email()
        if author_name:
            main_authors.append({
                "name": author_name,
                "role": "项目负责人 & 核心开发者",
                "email": author_email or "null",
                "github": version_manager.get_repository_url() or "null"
            })
        else:
            # 如果没有作者信息，显示null
            main_authors.append({
                "name": "null",
                "role": "null",
                "email": "null",
                "github": "null"
            })
        
        for author in main_authors:
            author_widget = self.create_author_widget(author)
            main_authors_layout.addWidget(author_widget)
        
        layout.addWidget(main_authors_group)
        
        # 贡献者
        contributors_group = QGroupBox("贡献者")
        contributors_layout = QVBoxLayout(contributors_group)
        
        contributors_text = QTextEdit()
        contributors_text.setReadOnly(True)
        contributors_text.setMaximumHeight(150)
        contributors_text.setPlainText(
            "暂无其他贡献者\n\n"
            "欢迎更多开发者加入 TimeNest 项目！\n"
            "如果您想为项目做出贡献，请访问我们的 GitHub 仓库。"
        )
        contributors_layout.addWidget(contributors_text)
        
        layout.addWidget(contributors_group)
        
        # 联系方式
        contact_group = QGroupBox("联系我们")
        contact_layout = QGridLayout(contact_group)
        
        contact_layout.addWidget(QLabel("项目邮箱:"), 0, 0)
        contact_email = QLabel(f'<a href="mailto:{self.APP_EMAIL}">{self.APP_EMAIL}</a>')
        contact_email.setOpenExternalLinks(True)
        contact_layout.addWidget(contact_email, 0, 1)
        
        contact_layout.addWidget(QLabel("GitHub:"), 1, 0)
        github_link = QLabel(f'<a href="{self.APP_REPOSITORY}">{self.APP_REPOSITORY}</a>')
        github_link.setOpenExternalLinks(True)
        contact_layout.addWidget(github_link, 1, 1)

        contact_layout.addWidget(QLabel("问题反馈:"), 2, 0)
        issues_url = version_manager.get_issues_url()
        issues_link = QLabel(f'<a href="{issues_url}">GitHub Issues</a>')
        issues_link.setOpenExternalLinks(True)
        contact_layout.addWidget(issues_link, 2, 1)
        
        layout.addWidget(contact_group)
        
        layout.addStretch()
        
        return tab
    
    def create_author_widget(self, author_info: dict) -> QWidget:
        """
        创建作者信息widget
        
        Args:
            author_info: 作者信息字典
            
        Returns:
            作者信息widget
        """
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        layout = QVBoxLayout(widget)
        
        # 姓名和角色
        name_label = QLabel(author_info.get('name'))
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        role_label = QLabel(author_info.get('role'))
        layout.addWidget(role_label)
        
        # 联系方式
        contact_layout = QHBoxLayout()
        
        
        if 'email' in author_info:
            email_label = QLabel(f'<a href="mailto:{author_info.get("email")}">📧 邮箱</a>')
            email_label.setOpenExternalLinks(True)
            contact_layout.addWidget(email_label)
        
        
        if 'github' in author_info:
            github_label = QLabel(f'<a href="{author_info.get("github")}">🐙 GitHub</a>')
        
            github_label = QLabel(f'<a href="{author_info.get("github")}">🐙 GitHub</a>')
            github_label.setOpenExternalLinks(True)
            contact_layout.addWidget(github_label)
        
        contact_layout.addStretch()
        layout.addLayout(contact_layout)
        
        return widget
    
    def create_license_tab(self) -> QWidget:
        """
        创建许可证标签页
        
        Returns:
            许可证标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 许可证信息
        license_group = QGroupBox(f"{self.APP_LICENSE} 许可证")
        license_layout = QVBoxLayout(license_group)
        
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText(self.get_license_text())
        license_layout.addWidget(license_text)
        
        layout.addWidget(license_group)
        
        # 第三方许可证
        third_party_group = QGroupBox("第三方库许可证")
        third_party_layout = QVBoxLayout(third_party_group)
        
        third_party_text = QTextEdit()
        third_party_text.setReadOnly(True)
        third_party_text.setPlainText(self.get_third_party_licenses())
        third_party_layout.addWidget(third_party_text)
        
        layout.addWidget(third_party_group)
        
        return tab
    
    def create_system_tab(self) -> QWidget:
        """
        创建系统信息标签页
        
        Returns:
            系统信息标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 系统信息
        system_group = QGroupBox("系统信息")
        system_layout = QGridLayout(system_group)
        
        system_info = self.get_system_info()
        
        row = 0
        for key, value in system_info.items():
            system_layout.addWidget(QLabel(f"{key}:"), row, 0)
            system_layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        
        layout.addWidget(system_group)
        
        # Python 信息
        python_group = QGroupBox("Python 环境")
        python_layout = QGridLayout(python_group)
        
        python_info = self.get_python_info()
        
        row = 0
        for key, value in python_info.items():
            python_layout.addWidget(QLabel(f"{key}:"), row, 0)
            python_layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        
        layout.addWidget(python_group)
        
        # Qt 信息
        qt_group = QGroupBox("Qt 环境")
        qt_layout = QGridLayout(qt_group)
        
        qt_info = self.get_qt_info()
        
        row = 0
        for key, value in qt_info.items():
            qt_layout.addWidget(QLabel(f"{key}:"), row, 0)
            qt_layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        
        layout.addWidget(qt_group)
        
        layout.addStretch()
        
        return tab
    
    def create_credits_tab(self) -> QWidget:
        """
        创建致谢标签页
        
        Returns:
            致谢标签页widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 致谢文本
        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setPlainText(self.get_credits_text())
        layout.addWidget(credits_text)
        
        return tab
    
    def connect_signals(self):
        """
        连接信号和槽
        """
        self.close_btn.clicked.connect(self.accept)
        self.website_btn.clicked.connect(self.open_website)
        self.github_btn.clicked.connect(self.open_github)
        self.feedback_btn.clicked.connect(self.open_feedback)
    
    def get_dependencies_info(self) -> dict:
        """
        获取依赖库信息
        
        Returns:
            依赖库信息字典
        """
        dependencies = {}
        
        try:
            import PyQt6
            dependencies['PyQt6'] = PyQt6.QtCore.PYQT_VERSION_STR
        except ImportError:
            dependencies['PyQt6'] = '未安装'
        
        try:
            import pandas
            dependencies['pandas'] = pandas.__version__
        except ImportError:
            dependencies['pandas'] = '未安装'
        
        try:
            import numpy
            dependencies['numpy'] = numpy.__version__
        except ImportError:
            dependencies['numpy'] = '未安装'
        
        try:
            import yaml
            dependencies['PyYAML'] = yaml.__version__
        except ImportError:
            dependencies['PyYAML'] = '未安装'
        
        try:
            import requests
            dependencies['requests'] = requests.__version__
        except ImportError:
            dependencies['requests'] = '未安装'
        
        try:
            import openpyxl
            dependencies['openpyxl'] = openpyxl.__version__
        except ImportError:
            dependencies['openpyxl'] = '未安装'
        
        return dependencies
    
    def get_system_info(self) -> dict:
        """
        获取系统信息
        
        Returns:
            系统信息字典
        """
        return {
            '操作系统': platform.system(),
            '系统版本': platform.release(),
            '系统架构': platform.machine(),
            '处理器': platform.processor() or '未知',
            '主机名': platform.node(),
            '平台': platform.platform()
        }
    
    def get_python_info(self) -> dict:
        """
        获取Python信息
        
        Returns:
            Python信息字典
        """
        return {
            'Python版本': sys.version.split()[0],
            '完整版本': sys.version.replace('\n', ' '),
            '可执行文件': sys.executable,
            '编译器': platform.python_compiler(),
            '构建信息': f"{platform.python_build()[0]} ({platform.python_build()[1]})"
        }
    
    def get_qt_info(self) -> dict:
        """
        获取Qt信息
        
        Returns:
            Qt信息字典
        """
        try:
            from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
            return {
                'Qt版本': QT_VERSION_STR,
                'PyQt版本': PYQT_VERSION_STR,
                '应用程序名称': QApplication.applicationName() or '未设置',
                '应用程序版本': QApplication.applicationVersion() or '未设置'
            }
        except ImportError:
            return {'Qt': '未安装'}
    
    def get_update_history(self) -> str:
        """
        获取更新历史
        
        Returns:
            更新历史文本
        """
        # 从版本管理器获取版本信息
        current_version = version_manager.get_full_version() or "null"
        release_date = version_manager.get_release_date() or "null"

        return f"""版本 {current_version} ({release_date})
• 当前版本信息从配置文件读取
• 移除硬编码版本信息
• 支持动态版本管理
• 版本信息统一管理

历史版本:
• 版本信息现在统一从 app_info.json 配置文件管理
• 不再使用硬编码的版本号
• 支持灵活的版本信息配置
• 便于版本发布和维护"""
    
    def get_license_text(self) -> str:
        """
        获取许可证文本
        
        Returns:
            许可证文本
        """
        return """MIT License

Copyright (c) 2024 TimeNest Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
    
    def get_third_party_licenses(self) -> str:
        """
        获取第三方库许可证信息
        
        Returns:
            第三方库许可证文本
        """
        return """本软件使用了以下第三方库：

PyQt6
许可证：GPL v3 / Commercial
网站：https://www.riverbankcomputing.com/software/pyqt/

pandas
许可证：BSD 3-Clause
网站：https://pandas.pydata.org/

numpy
许可证：BSD 3-Clause
网站：https://numpy.org/

PyYAML
许可证：MIT
网站：https://pyyaml.org/

requests
许可证：Apache 2.0
网站：https://requests.readthedocs.io/

openpyxl
许可证：MIT
网站：https://openpyxl.readthedocs.io/

Pillow
许可证：PIL Software License
网站：https://pillow.readthedocs.io/

pygame
许可证：LGPL
网站：https://www.pygame.org/

感谢这些优秀的开源项目！"""
    
    def get_credits_text(self) -> str:
        """
        获取致谢文本
        
        Returns:
            致谢文本
        """
        return """感谢所有为 TimeNest 项目做出贡献的人们！

🎯 项目愿景
TimeNest 致力于为学生和教育工作者提供最好的课程表管理和时间提醒工具。我们希望通过智能化的设计和人性化的交互，让每个人都能更好地管理自己的学习时间。

👥 开发团队
感谢我们的核心开发团队，他们投入了大量的时间和精力来打造这个产品：
• 项目架构设计
• 核心功能开发
• 用户界面设计
• 测试和质量保证
• 文档编写

🌟 社区贡献
感谢开源社区的支持和贡献：
• 功能建议和反馈
• 错误报告和修复
• 文档改进
• 翻译工作
• 推广和宣传

🎨 设计灵感
感谢以下项目和设计理念给我们的启发：
• Material Design
• Fluent Design System
• 各种优秀的开源项目

📚 技术支持
感谢以下技术和平台的支持：
• Python 编程语言
• Qt 框架
• GitHub 代码托管
• 各种开源库和工具

💝 特别感谢
• 所有的测试用户和反馈者
• 提供建议和想法的朋友们
• 支持开源软件发展的组织和个人
• 每一个使用 TimeNest 的用户

🚀 未来展望
我们将继续改进和完善 TimeNest，为用户提供更好的体验。如果您有任何建议或想法，欢迎与我们联系！

再次感谢大家的支持！

—— TimeNest 开发团队"""
    
    def open_website(self):
        """
        打开官网
        """
        QDesktopServices.openUrl(QUrl(self.APP_WEBSITE))
    
    def open_github(self):
        """
        打开GitHub页面
        """
        QDesktopServices.openUrl(QUrl(self.APP_WEBSITE))
    
    def open_feedback(self):
        """
        打开反馈页面
        """
        feedback_url = "https://github.com/timenest/timenest/issues"
        QDesktopServices.openUrl(QUrl(feedback_url))