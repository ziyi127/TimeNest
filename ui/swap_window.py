import logging
import sys
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class SwapWindow(QMainWindow):
    """换课窗口 - 用于换课功能"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, False
        )  # 确保配置窗口不透明
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

        # 初始化成员变量
        self.swaps: List[str] = []
        self.course_list: QListWidget = QListWidget()
        self.swap_list: QListWidget = QListWidget()
        self.add_button: QPushButton = QPushButton()
        self.remove_button: QPushButton = QPushButton()
        self.apply_button: QPushButton = QPushButton()

        self.init_ui()
        self.setup_window_properties()

    def setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("TimeNest 换课")
        self.setMinimumSize(400, 300)
        self.resize(500, 400)

        # 设置窗口标志 - 确保配置窗口正常显示
        self.setWindowFlags(
            Qt.WindowType.Window  # 标准窗口
            | Qt.WindowType.WindowCloseButtonHint  # 关闭按钮
            | Qt.WindowType.WindowMinimizeButtonHint  # 最小化按钮
        )

        # 居中显示
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            center_x = screen_geometry.width() // 2
            center_y = screen_geometry.height() // 2
            self.move(center_x - self.width() // 2, center_y - self.height() // 2)
        elif self.parent():
            parent_widget = self.parent()
            # 确保父窗口部件是QWidget类型
            if isinstance(parent_widget, QWidget):
                parent_center = parent_widget.geometry().center()
                self.move(
                    parent_center.x() - self.width() // 2,
                    parent_center.y() - self.height() // 2,
                )

    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题
        title_label = QLabel("换课")
        title_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            color: #333;
        """
        )
        main_layout.addWidget(title_label)

        # 描述
        desc_label = QLabel("选择要交换的课程")
        desc_label.setStyleSheet(
            """
            font-size: 14px;
            color: #666;
        """
        )
        main_layout.addWidget(desc_label)

        # 课程列表
        self.course_list = QListWidget()
        self.course_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """
        )

        # 添加示例课程
        courses = [
            "数学 (张老师) - 08:00-08:45",
            "语文 (李老师) - 08:55-09:40",
            "英语 (王老师) - 10:00-10:45",
            "物理 (赵老师) - 10:55-11:40",
            "化学 (孙老师) - 14:00-14:45",
        ]

        for course in courses:
            item = QListWidgetItem(course)
            # 类型检查：确保 course_list 不为 None
            if self.course_list:
                self.course_list.addItem(item)

        main_layout.addWidget(self.course_list)

        # 换课列表
        self.swap_list = QListWidget()
        self.swap_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                min-height: 100px;
            }
        """
        )
        main_layout.addWidget(QLabel("已选择的课程:"))
        main_layout.addWidget(self.swap_list)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("添加 >>")
        self.remove_button = QPushButton("<< 移除")
        self.apply_button = QPushButton("应用换课")

        # 连接信号
        self.add_button.clicked.connect(self.add_swap)
        self.remove_button.clicked.connect(self.remove_swap)
        self.apply_button.clicked.connect(self.apply_swaps)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)

        main_layout.addLayout(button_layout)

    def on_swap_clicked(self):
        """换课按钮点击事件"""
        selected_items = self.course_list.selectedItems()
        if selected_items:
            course = selected_items[0].text()
            QMessageBox.information(
                self, "换课成功", f"已选择课程: {course}\n换课功能将在后续版本中完善。"
            )
            self.close()
        else:
            QMessageBox.warning(self, "请选择课程", "请先选择要换课的课程。")

    def add_swap(self) -> None:
        """添加换课记录"""
        selected_items = self.course_list.selectedItems()
        if selected_items:
            course = selected_items[0].text()
            self.swaps.append(course)
            self.update_swap_list()
        else:
            QMessageBox.warning(self, "请选择课程", "请先选择要换课的课程。")

    def remove_swap(self) -> None:
        """移除换课记录"""
        selected_items = self.swap_list.selectedItems()
        if selected_items:
            course = selected_items[0].text()
            self.swaps.remove(course)
            self.update_swap_list()
        else:
            QMessageBox.warning(self, "请选择换课记录", "请先选择要移除的换课记录。")

    def update_swap_list(self) -> None:
        """更新换课列表"""
        self.swap_list.clear()
        for course in self.swaps:
            item = QListWidgetItem(course)
            self.swap_list.addItem(item)

    def apply_swaps(self) -> None:
        """应用换课记录"""
        if self.swaps:
            QMessageBox.information(
                self,
                "换课成功",
                f"已选择课程: {', '.join(self.swaps)}\n换课功能将在后续版本中完善。",
            )
            self.close()
        else:
            QMessageBox.warning(self, "请选择课程", "请先选择要换课的课程。")

    def closeEvent(self, event: QCloseEvent) -> None:
        """窗口关闭事件"""
        event.accept()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建换课窗口
    swap_window = SwapWindow()
    swap_window.show()

    sys.exit(app.exec())
