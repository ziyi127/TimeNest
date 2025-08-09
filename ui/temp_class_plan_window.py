import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QFrame, QTableWidget, 
                              QTableWidgetItem, QComboBox, QDateEdit, 
                              QMessageBox, QGroupBox)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class TempClassPlanWindow(QMainWindow):
    """临时课表窗口 - 用于加载临时课表功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # 确保配置窗口不透明
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.init_ui()
        self.setup_window_properties()
        
    def setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("TimeNest 临时课表")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
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
        title_label = QLabel("临时课表")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333;
        """)
        main_layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel("创建或加载临时课程表")
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
        """)
        main_layout.addWidget(desc_label)
        
        # 临时课表设置组
        settings_group = QGroupBox("临时课表设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("生效日期:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        settings_layout.addLayout(date_layout)
        
        # 持续时间
        duration_layout = QHBoxLayout()
        duration_label = QLabel("持续时间:")
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["1天", "3天", "7天", "30天"])
        self.duration_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_combo)
        duration_layout.addStretch()
        settings_layout.addLayout(duration_layout)
        
        main_layout.addWidget(settings_group)
        
        # 课程表组
        table_group = QGroupBox("课程安排")
        table_layout = QVBoxLayout(table_group)
        
        # 课程表
        self.class_table = QTableWidget(8, 4)
        self.class_table.setHorizontalHeaderLabels(["时间", "课程", "教师", "教室"])
        self.class_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        # 设置示例数据
        time_slots = [
            "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
            "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40"
        ]
        
        for i, time_slot in enumerate(time_slots):
            self.class_table.setItem(i, 0, QTableWidgetItem(time_slot))
        
        table_layout.addWidget(self.class_table)
        main_layout.addWidget(table_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("保存临时课表")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.on_save_clicked)
        
        load_btn = QPushButton("从文件加载")
        load_btn.setStyleSheet("""
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
        load_btn.clicked.connect(self.on_load_clicked)
        
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
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(load_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def on_save_clicked(self):
        """保存按钮点击事件"""
        date = self.date_edit.date().toString("yyyy-MM-dd")
        duration = self.duration_combo.currentText()
        QMessageBox.information(self, "保存成功", 
                               f"临时课表已保存!\n生效日期: {date}\n持续时间: {duration}\n\n临时课表功能将在后续版本中完善。")
        self.close()
        
    def on_load_clicked(self):
        """加载按钮点击事件"""
        QMessageBox.information(self, "加载课表", "请选择课表文件。\n\n此功能将在后续版本中实现。")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("临时课表窗口已关闭")
        super().closeEvent(event)


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建临时课表窗口
    temp_window = TempClassPlanWindow()
    temp_window.show()
    
    sys.exit(app.exec())
