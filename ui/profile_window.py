import sys
import logging
from typing import Optional
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTreeWidget, QTreeWidgetItem, QStackedWidget,
                              QLabel, QPushButton, QFrame, QSplitter,
                              QListWidget, QTextEdit,
                              QComboBox, QCheckBox, QGroupBox,
                              QTableWidget, QTableWidgetItem, QApplication)
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QCloseEvent

logger = logging.getLogger(__name__)


class ProfileWindow(QMainWindow):
    """档案编辑窗口 - 仿ClassIsland档案编辑窗口"""
    
    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)  # 确保配置窗口不透明
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.init_ui()
        self.setup_window_properties()
        
    def setup_window_properties(self) -> None:
        """设置窗口属性"""
        self.setWindowTitle("TimeNest 档案编辑")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # 设置窗口标志 - 确保配置窗口正常显示
        self.setWindowFlags(
            Qt.WindowType.Window |           # 标准窗口
            Qt.WindowType.WindowCloseButtonHint |  # 关闭按钮
            Qt.WindowType.WindowMinimizeButtonHint  # 最小化按钮
        )
        
        # 居中显示
        parent = self.parent()
        if parent and isinstance(parent, QWidget):
            parent_geometry: QRect = parent.geometry()
            parent_center: QPoint = parent_geometry.center()
            # 显式转换为int以解决类型检查问题
            x: int = int(parent_center.x()) - self.width() // 2
            y: int = int(parent_center.y()) - self.height() // 2
            self.move(x, y)
        
    def init_ui(self) -> None:
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧导航面板
        self.create_navigation_panel(splitter)
        
        # 右侧内容区域
        self.create_content_area(splitter)
        
        # 设置分割器比例
        splitter.setSizes([250, 750])
        
    def create_navigation_panel(self, parent: QSplitter) -> None:
        """创建导航面板"""
        # 导航框架
        nav_frame = QFrame()
        nav_frame.setObjectName("NavigationFrame")
        nav_frame.setFixedWidth(250)
        parent.addWidget(nav_frame)
        
        # 导航布局
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # 标题
        title_label = QLabel("档案编辑")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2d2d2d;
                color: white;
            }
        """)
        nav_layout.addWidget(title_label)
        
        # 档案管理组
        profile_group = QGroupBox("档案管理")
        profile_layout = QVBoxLayout(profile_group)
        
        # 档案列表
        self.profile_list = QListWidget()
        self.profile_list.addItem("默认档案")
        self.profile_list.addItem("学生档案1")
        self.profile_list.addItem("学生档案2")
        self.profile_list.setCurrentRow(0)
        profile_layout.addWidget(self.profile_list)
        
        # 档案操作按钮
        button_layout = QHBoxLayout()
        new_btn = QPushButton("新建")
        delete_btn = QPushButton("删除")
        duplicate_btn = QPushButton("复制")
        
        button_layout.addWidget(new_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(duplicate_btn)
        
        profile_layout.addLayout(button_layout)
        nav_layout.addWidget(profile_group)
        
        # 导航树
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setIndentation(15)
        self.nav_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #f0f0f0;
                border: none;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        
        # 添加导航项
        self.add_navigation_items()
        
        # 连接导航树信号
        self.nav_tree.currentItemChanged.connect(self.on_navigation_changed)
        
        nav_layout.addWidget(self.nav_tree)
        
    def add_navigation_items(self) -> None:
        """添加导航项"""
        # 课程表管理
        schedule_item = QTreeWidgetItem(["课程表管理"])
        schedule_item.setData(0, Qt.ItemDataRole.UserRole, "schedule")
        
        # 时间表
        time_layout_item = QTreeWidgetItem(["时间表"])
        time_layout_item.setData(0, Qt.ItemDataRole.UserRole, "time_layout")
        
        # 课表
        class_plan_item = QTreeWidgetItem(["课表"])
        class_plan_item.setData(0, Qt.ItemDataRole.UserRole, "class_plan")
        
        # 科目管理
        subject_item = QTreeWidgetItem(["科目管理"])
        subject_item.setData(0, Qt.ItemDataRole.UserRole, "subject")
        
        # 临时课表
        temp_plan_item = QTreeWidgetItem(["临时课表"])
        temp_plan_item.setData(0, Qt.ItemDataRole.UserRole, "temp_plan")
        
        # 添加子项
        schedule_item.addChild(time_layout_item)
        schedule_item.addChild(class_plan_item)
        schedule_item.addChild(temp_plan_item)
        
        # 添加到树
        self.nav_tree.addTopLevelItems([schedule_item, subject_item])
        
        # 默认选择第一个项
        self.nav_tree.setCurrentItem(schedule_item)
        
    def create_content_area(self, parent: QSplitter) -> None:
        """创建内容区域"""
        # 内容框架
        content_frame = QFrame()
        content_frame.setObjectName("ContentFrame")
        parent.addWidget(content_frame)
        
        # 内容布局
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 标题栏
        self.title_bar = QLabel("课程表管理")
        self.title_bar.setObjectName("ContentTitle")
        self.title_bar.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background-color: white;
                border-bottom: 1px solid #ddd;
            }
        """)
        content_layout.addWidget(self.title_bar)
        
        # 内容堆栈
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # 添加各个编辑页面
        self.add_edit_pages()
        
    def add_edit_pages(self) -> None:
        """添加编辑页面"""
        # 课程表管理页面
        schedule_page = self.create_schedule_management_page()
        self.content_stack.addWidget(schedule_page)
        
        # 时间表页面
        time_layout_page = self.create_time_layout_page()
        self.content_stack.addWidget(time_layout_page)
        
        # 课表页面
        class_plan_page = self.create_class_plan_page()
        self.content_stack.addWidget(class_plan_page)
        
        # 科目管理页面
        subject_page = self.create_subject_management_page()
        self.content_stack.addWidget(subject_page)
        
        # 临时课表页面
        temp_plan_page = self.create_temp_plan_page()
        self.content_stack.addWidget(temp_plan_page)
        
    def create_schedule_management_page(self):
        """创建课程表管理页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("课程表管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        description = QLabel("在这里管理您的课程表配置")
        description.setStyleSheet("font-size: 14px; color: #666; margin: 10px 20px;")
        layout.addWidget(description)
        
        # 课程表概览
        overview_group = QGroupBox("当前课程表概览")
        overview_layout = QVBoxLayout(overview_group)
        
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setPlainText(
            "默认档案\n"
            "时间表: 标准时间表\n"
            "课表: 周一至周五课程表\n"
            "科目数量: 8个\n"
            "课程时段: 8个\n"
        )
        overview_layout.addWidget(overview_text)
        
        layout.addWidget(overview_group)
        layout.addStretch()
        return page
        
    def create_time_layout_page(self):
        """创建时间表页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("时间表管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # 时间表列表
        table_group = QGroupBox("时间表列表")
        table_layout = QVBoxLayout(table_group)
        
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["时间表名称", "时段数量", "操作"])
        table.setItem(0, 0, QTableWidgetItem("标准时间表"))
        table.setItem(0, 1, QTableWidgetItem("8"))
        table.setItem(1, 0, QTableWidgetItem("短时间表"))
        table.setItem(1, 1, QTableWidgetItem("6"))
        table.setItem(2, 0, QTableWidgetItem("长时间表"))
        table.setItem(2, 1, QTableWidgetItem("10"))
        
        table_layout.addWidget(table)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        add_btn = QPushButton("添加时间表")
        edit_btn = QPushButton("编辑选中")
        delete_btn = QPushButton("删除选中")
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        table_layout.addLayout(button_layout)
        layout.addWidget(table_group)
        
        layout.addStretch()
        return page
        
    def create_class_plan_page(self):
        """创建课表页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("课表管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # 课表列表
        plan_group = QGroupBox("课表列表")
        plan_layout = QVBoxLayout(plan_group)
        
        plan_list = QListWidget()
        plan_list.addItem("周一至周五课程表")
        plan_list.addItem("周末课程表")
        plan_list.addItem("考试周课程表")
        plan_layout.addWidget(plan_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        add_btn = QPushButton("添加课表")
        edit_btn = QPushButton("编辑选中")
        delete_btn = QPushButton("删除选中")
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        plan_layout.addLayout(button_layout)
        layout.addWidget(plan_group)
        
        layout.addStretch()
        return page
        
    def create_subject_management_page(self):
        """创建科目管理页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("科目管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # 科目列表
        subject_group = QGroupBox("科目列表")
        subject_layout = QVBoxLayout(subject_group)
        
        subject_table = QTableWidget(5, 4)
        subject_table.setHorizontalHeaderLabels(["科目名称", "教师", "教室", "颜色"])
        subject_table.setItem(0, 0, QTableWidgetItem("数学"))
        subject_table.setItem(0, 1, QTableWidgetItem("张老师"))
        subject_table.setItem(0, 2, QTableWidgetItem("101教室"))
        subject_table.setItem(1, 0, QTableWidgetItem("语文"))
        subject_table.setItem(1, 1, QTableWidgetItem("李老师"))
        subject_table.setItem(1, 2, QTableWidgetItem("102教室"))
        subject_table.setItem(2, 0, QTableWidgetItem("英语"))
        subject_table.setItem(2, 1, QTableWidgetItem("王老师"))
        subject_table.setItem(2, 2, QTableWidgetItem("103教室"))
        subject_table.setItem(3, 0, QTableWidgetItem("物理"))
        subject_table.setItem(3, 1, QTableWidgetItem("赵老师"))
        subject_table.setItem(3, 2, QTableWidgetItem("201实验室"))
        subject_table.setItem(4, 0, QTableWidgetItem("化学"))
        subject_table.setItem(4, 1, QTableWidgetItem("孙老师"))
        subject_table.setItem(4, 2, QTableWidgetItem("202实验室"))
        
        subject_layout.addWidget(subject_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        add_btn = QPushButton("添加科目")
        edit_btn = QPushButton("编辑选中")
        delete_btn = QPushButton("删除选中")
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        subject_layout.addLayout(button_layout)
        layout.addWidget(subject_group)
        
        layout.addStretch()
        return page
        
    def create_temp_plan_page(self):
        """创建临时课表页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("临时课表")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        description = QLabel("配置临时课表和换课设置")
        description.setStyleSheet("font-size: 14px; color: #666; margin: 10px 20px;")
        layout.addWidget(description)
        
        # 临时课表设置
        temp_group = QGroupBox("临时课表设置")
        temp_layout = QVBoxLayout(temp_group)
        
        enable_checkbox = QCheckBox("启用临时课表")
        temp_layout.addWidget(enable_checkbox)
        
        duration_label = QLabel("临时课表持续时间:")
        temp_layout.addWidget(duration_label)
        
        duration_combo = QComboBox()
        duration_combo.addItems(["1天", "3天", "7天", "30天"])
        temp_layout.addWidget(duration_combo)
        
        layout.addWidget(temp_group)
        layout.addStretch()
        return page
        
    def on_navigation_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem) -> None:
        """导航项改变时的处理"""
        if current:
            page_key = current.data(0, Qt.ItemDataRole.UserRole)
            if not page_key:  # 如果是父节点，获取第一个子节点
                if current.childCount() > 0:
                    child_item = current.child(0)
                    if child_item:
                        page_key = child_item.data(0, Qt.ItemDataRole.UserRole)
            
            if page_key:
                self.switch_to_page(page_key)
            
    def switch_to_page(self, page_key: str) -> None:
        """切换到指定页面"""
        page_map = {
            "schedule": 0,
            "time_layout": 1,
            "class_plan": 2,
            "subject": 3,
            "temp_plan": 4
        }
        
        page_index = page_map.get(page_key, 0)
        self.content_stack.setCurrentIndex(page_index)
        
        # 更新标题
        titles = {
            "schedule": "课程表管理",
            "time_layout": "时间表管理",
            "class_plan": "课表管理",
            "subject": "科目管理",
            "temp_plan": "临时课表"
        }
        
        self.title_bar.setText(titles.get(page_key, "档案编辑"))
        
    def closeEvent(self, event: QCloseEvent) -> None:
        """窗口关闭事件"""
        logger.info("档案编辑窗口已关闭")
        super().closeEvent(event)


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建档案编辑窗口
    profile_window = ProfileWindow()
    profile_window.show()
    
    sys.exit(app.exec())
