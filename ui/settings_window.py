import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QTreeWidget, QTreeWidgetItem, QStackedWidget, 
                              QLabel, QPushButton, QFrame, QSplitter, QGroupBox,
                              QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class SettingsWindow(QMainWindow):
    """设置窗口 - 仿ClassIsland设置窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # 确保配置窗口不透明
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        
        # 从主题管理器获取主题颜色并缓存
        from core.components.theme_manager import theme_manager
        self.theme_manager = theme_manager
        self.theme = theme_manager.current_theme
        self.colors = theme_manager.get_theme_colors(self.theme)
        
        self.init_ui()
        self.setup_window_properties()
        
    def setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("TimeNest 设置")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # 设置窗口标志 - 确保配置窗口正常显示
        self.setWindowFlags(
            Qt.WindowType.Window |           # 标准窗口
            Qt.WindowType.WindowCloseButtonHint |  # 关闭按钮
            Qt.WindowType.WindowMinimizeButtonHint  # 最小化按钮
        )
        
        # 居中显示
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            center_x = screen_geometry.width() // 2
            center_y = screen_geometry.height() // 2
            self.move(center_x - self.width() // 2, center_y - self.height() // 2)
        elif self.parent():
            parent_center = self.parent().geometry().center()
            self.move(parent_center.x() - self.width() // 2, 
                     parent_center.y() - self.height() // 2)
        
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧导航面板
        self.create_navigation_panel(splitter)
        
        # 右侧内容区域
        self.create_content_area(splitter)
        
        # 设置分割器比例
        splitter.setSizes([200, 700])
        
    def create_navigation_panel(self, parent):
        """创建导航面板"""
        # 使用缓存的主题颜色
        colors = self.colors
        
        # 导航框架
        nav_frame = QFrame()
        nav_frame.setObjectName("NavigationFrame")
        nav_frame.setFixedWidth(200)
        parent.addWidget(nav_frame)
        
        # 导航布局
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # 标题
        title_label = QLabel("设置")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: {colors['background'].name()};
                color: {colors['text_primary'].name()};
            }}
        """)
        nav_layout.addWidget(title_label)
        
        # 导航树
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setIndentation(0)
        self.nav_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {colors['background'].name()};
                border: none;
                color: {colors['text_primary'].name()};
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {colors['border'].name()};
            }}
            QTreeWidget::item:selected {{
                background-color: {colors['accent'].name()};
                color: white;
            }}
        """)
        
        # 添加导航项
        self.add_navigation_items()
        
        # 连接导航树信号
        self.nav_tree.currentItemChanged.connect(self.on_navigation_changed)
        
        nav_layout.addWidget(self.nav_tree)
        
    def add_navigation_items(self):
        """添加导航项"""
        # 基本设置
        basic_item = QTreeWidgetItem(["基本"])
        basic_item.setData(0, Qt.UserRole, "basic")
        
        # 窗口设置
        window_item = QTreeWidgetItem(["窗口"])
        window_item.setData(0, Qt.UserRole, "window")
        
        # 课程表设置
        schedule_item = QTreeWidgetItem(["课程表"])
        schedule_item.setData(0, Qt.UserRole, "schedule")
        
        # 通知设置
        notification_item = QTreeWidgetItem(["通知"])
        notification_item.setData(0, Qt.UserRole, "notification")
        
        # 外观设置
        appearance_item = QTreeWidgetItem(["外观"])
        appearance_item.setData(0, Qt.UserRole, "appearance")
        
        # 隐私设置
        privacy_item = QTreeWidgetItem(["隐私"])
        privacy_item.setData(0, Qt.UserRole, "privacy")
        
        # 关于
        about_item = QTreeWidgetItem(["关于"])
        about_item.setData(0, Qt.UserRole, "about")
        
        # 添加到树
        self.nav_tree.addTopLevelItems([
            basic_item, window_item, schedule_item, 
            notification_item, appearance_item, 
            privacy_item, about_item
        ])
        
        # 默认选择第一个项
        self.nav_tree.setCurrentItem(basic_item)
        
    def create_content_area(self, parent):
        """创建内容区域"""
        # 使用缓存的主题颜色
        colors = self.colors

        # 内容框架
        content_frame = QFrame()
        content_frame.setObjectName("ContentFrame")
        parent.addWidget(content_frame)

        # 内容布局
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 标题栏
        self.title_bar = QLabel("基本设置")
        self.title_bar.setObjectName("ContentTitle")
        self.title_bar.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background-color: {colors['background'].name()};
                color: {colors['text_primary'].name()};
                border-bottom: 1px solid {colors['border'].name()};
            }}
        """)
        content_layout.addWidget(self.title_bar)
        
        # 内容堆栈
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # 添加各个设置页面
        self.add_setting_pages()
        
    def add_setting_pages(self):
        """添加设置页面"""
        # 基本设置页面
        basic_page = self.create_basic_settings_page()
        self.content_stack.addWidget(basic_page)
        
        # 窗口设置页面
        window_page = self.create_window_settings_page()
        self.content_stack.addWidget(window_page)
        
        # 课程表设置页面
        schedule_page = self.create_schedule_settings_page()
        self.content_stack.addWidget(schedule_page)
        
        # 通知设置页面
        notification_page = self.create_notification_settings_page()
        self.content_stack.addWidget(notification_page)
        
        # 外观设置页面
        appearance_page = self.create_appearance_settings_page()
        self.content_stack.addWidget(appearance_page)
        
        # 隐私设置页面
        privacy_page = self.create_privacy_settings_page()
        self.content_stack.addWidget(privacy_page)
        
        # 关于页面
        about_page = self.create_about_page()
        self.content_stack.addWidget(about_page)
        
    def create_basic_settings_page(self):
        """创建基本设置页面"""
        # 使用缓存的主题颜色
        colors = self.colors

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("基本设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        description = QLabel("在这里配置TimeNest的基本设置")
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 10px 20px;")
        layout.addWidget(description)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QVBoxLayout(basic_group)
        
        self.auto_update_checkbox = QCheckBox("自动检查更新")
        self.auto_update_checkbox.setChecked(True)
        basic_layout.addWidget(self.auto_update_checkbox)
        
        self.notifications_checkbox = QCheckBox("启用桌面通知")
        self.notifications_checkbox.setChecked(True)
        basic_layout.addWidget(self.notifications_checkbox)
        
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "繁体中文", "English"])
        language_layout.addWidget(self.language_combo)
        basic_layout.addLayout(language_layout)
        
        layout.addWidget(basic_group)
        
        layout.addStretch()
        return page
        
    def create_window_settings_page(self):
        """创建窗口设置页面"""
        # 使用缓存的主题颜色
        colors = self.colors

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("窗口设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        description = QLabel("配置主窗口的显示和行为")
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 10px 20px;")
        layout.addWidget(description)
        
        # 窗口设置组
        window_group = QGroupBox("窗口设置")
        window_layout = QVBoxLayout(window_group)
        
        update_interval_layout = QHBoxLayout()
        update_interval_layout.addWidget(QLabel("更新间隔 (分钟):"))
        self.update_interval_spinbox = QSpinBox()
        self.update_interval_spinbox.setRange(1, 60)
        self.update_interval_spinbox.setValue(5)
        update_interval_layout.addWidget(self.update_interval_spinbox)
        window_layout.addLayout(update_interval_layout)
        
        window_layout.addWidget(QLabel("窗口透明度:"))
        self.window_opacity_spinbox = QSpinBox()
        self.window_opacity_spinbox.setRange(50, 100)
        self.window_opacity_spinbox.setValue(95)
        window_layout.addWidget(self.window_opacity_spinbox)
        
        layout.addWidget(window_group)
        
        # 浮动窗口设置组
        floating_window_group = QGroupBox("浮动窗口设置")
        floating_window_layout = QVBoxLayout(floating_window_group)
        
        # 鼠标悬停透明度设置
        self.hover_effect_checkbox = QCheckBox("启用鼠标悬停透明效果")
        self.hover_effect_checkbox.setChecked(True)
        floating_window_layout.addWidget(self.hover_effect_checkbox)
        
        hover_opacity_layout = QHBoxLayout()
        hover_opacity_layout.addWidget(QLabel("鼠标悬停透明度 (0.0-1.0):"))
        self.hover_opacity_spinbox = QDoubleSpinBox()
        self.hover_opacity_spinbox.setRange(0.0, 1.0)
        self.hover_opacity_spinbox.setSingleStep(0.1)
        self.hover_opacity_spinbox.setValue(0.3)
        hover_opacity_layout.addWidget(self.hover_opacity_spinbox)
        floating_window_layout.addLayout(hover_opacity_layout)
        
        # 触控点击透明度设置
        self.touch_effect_checkbox = QCheckBox("启用触控点击透明效果")
        self.touch_effect_checkbox.setChecked(True)
        floating_window_layout.addWidget(self.touch_effect_checkbox)
        
        touch_opacity_layout = QHBoxLayout()
        touch_opacity_layout.addWidget(QLabel("触控点击透明度 (0.0-1.0):"))
        self.touch_opacity_spinbox = QDoubleSpinBox()
        self.touch_opacity_spinbox.setRange(0.0, 1.0)
        self.touch_opacity_spinbox.setSingleStep(0.1)
        self.touch_opacity_spinbox.setValue(0.2)
        touch_opacity_layout.addWidget(self.touch_opacity_spinbox)
        floating_window_layout.addLayout(touch_opacity_layout)
        
        layout.addWidget(floating_window_group)
        
        layout.addStretch()
        return page
        
    def create_schedule_settings_page(self):
        """创建课程表设置页面"""
        # 使用缓存的主题颜色
        colors = self.colors

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("课程表设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        description = QLabel("配置课程表的显示和行为")
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 10px 20px;")
        layout.addWidget(description)
        
        layout.addStretch()
        return page
        
    def create_notification_settings_page(self):
        """创建通知设置页面"""
        # 使用缓存的主题颜色
        colors = self.colors

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("通知设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        description = QLabel("配置通知的显示和行为")
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 10px 20px;")
        layout.addWidget(description)
        
        layout.addStretch()
        return page
        
    def create_appearance_settings_page(self):
        """创建外观设置页面"""
        # 使用缓存的主题颜色
        colors = self.colors

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("外观设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        description = QLabel("配置应用程序的外观和主题")
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 10px 20px;")
        layout.addWidget(description)
        
        # 主题设置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_layout.addWidget(QLabel("选择主题:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色主题", "浅色主题", "自动"])
        theme_layout.addWidget(self.theme_combo)
        
        self.auto_switch_checkbox = QCheckBox("自动根据系统主题切换")
        theme_layout.addWidget(self.auto_switch_checkbox)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        return page
        
    def create_privacy_settings_page(self):
        """创建隐私设置页面"""
        # 从主题管理器获取主题颜色
        from core.components.theme_manager import theme_manager
        theme = theme_manager.current_theme
        colors = theme_manager.get_theme_colors(theme)

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("隐私设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        description = QLabel("配置隐私相关的设置")
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 10px 20px;")
        layout.addWidget(description)
        
        layout.addStretch()
        return page
        
    def create_about_page(self):
        """创建关于页面"""
        # 从主题管理器获取主题颜色
        from core.components.theme_manager import theme_manager
        theme = theme_manager.current_theme
        colors = theme_manager.get_theme_colors(theme)

        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("关于 TimeNest")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(title)
        
        version_label = QLabel("版本: 1.0.2")
        version_label.setStyleSheet(f"font-size: 16px; margin: 10px 20px; color: {colors['text_primary'].name()};")
        layout.addWidget(version_label)
        
        description = QLabel(
            "TimeNest 是一个智能课程表桌面应用程序，\n"
            "完整重构自ClassIsland的Python实现。"
        )
        description.setStyleSheet(f"font-size: 14px; color: {colors['text_secondary'].name()}; margin: 20px;")
        layout.addWidget(description)
        
        layout.addStretch()
        return page
        
    def on_navigation_changed(self, current, previous):
        """导航项改变时的处理"""
        if current:
            page_key = current.data(0, Qt.UserRole)
            self.switch_to_page(page_key)
            
    def switch_to_page(self, page_key):
        """切换到指定页面"""
        page_map = {
            "basic": 0,
            "window": 1,
            "schedule": 2,
            "notification": 3,
            "appearance": 4,
            "privacy": 5,
            "about": 6
        }
        
        page_index = page_map.get(page_key, 0)
        self.content_stack.setCurrentIndex(page_index)
        
        # 更新标题
        titles = {
            "basic": "基本设置",
            "window": "窗口设置",
            "schedule": "课程表设置",
            "notification": "通知设置",
            "appearance": "外观设置",
            "privacy": "隐私设置",
            "about": "关于 TimeNest"
        }
        
        self.title_bar.setText(titles.get(page_key, "设置"))
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("设置窗口已关闭")
        super().closeEvent(event)


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建设置窗口
    settings_window = SettingsWindow()
    settings_window.show()
    
    sys.exit(app.exec())