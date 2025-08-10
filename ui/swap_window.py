import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QFrame, QListWidget, 
                              QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class SwapWindow(QMainWindow):
    """换课窗口 - 用于换课功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # 确保配置窗口不透明
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.init_ui()
        self.setup_window_properties()
        
    def setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("TimeNest 换课")
        self.setMinimumSize(400, 300)
        self.resize(500, 400)
        
        # 设置窗口标志 - 确保配置窗口正常显示
        self.setWindowFlags(
            Qt.WindowType.Window |           # 标准窗口
            Qt.WindowType.WindowCloseButtonHint |  # 关闭按钮
            Qt.WindowType.WindowMinimizeButtonHint  # 最小化按钮
        )
        
        # 居中显示
        if self.parent():
            parent_center = self.parent().geometry().center()
            self.move(parent_center.x() - self.width() // 2, 
                     parent_center.y() - self.height() // 2)
        
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
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333;
        """)
        main_layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel("选择要交换的课程")
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
        """)
        main_layout.addWidget(desc_label)
        
        # 课程列表
        self.course_list = QListWidget()
        self.course_list.setStyleSheet("""
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
        """)
        
        # 添加示例课程
        courses = [
            "数学 (张老师) - 08:00-08:45",
            "语文 (李老师) - 08:55-09:40",
            "英语 (王老师) - 10:00-10:45",
            "物理 (赵老师) - 10:55-11:40",
            "化学 (孙老师) - 14:00-14:45"
        ]
        
        for course in courses:
            item = QListWidgetItem(course)
            self.course_list.addItem(item)
        
        main_layout.addWidget(self.course_list)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        swap_btn = QPushButton("换课")
        swap_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        swap_btn.clicked.connect(self.on_swap_clicked)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f8f8;
                color: #333;
                border: 1px solid #ddd;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(swap_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def on_swap_clicked(self):
        """换课按钮点击事件"""
        selected_items = self.course_list.selectedItems()
        if selected_items:
            course = selected_items[0].text()
            QMessageBox.information(self, "换课成功", f"已选择课程: {course}\n换课功能将在后续版本中完善。")
            self.close()
        else:
            QMessageBox.warning(self, "请选择课程", "请先选择要换课的课程。")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("换课窗口已关闭")
        super().closeEvent(event)


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建换课窗口
    swap_window = SwapWindow()
    swap_window.show()
    
    sys.exit(app.exec())
