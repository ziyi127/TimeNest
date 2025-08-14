import logging
from typing import Optional
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QCheckBox, QGroupBox, QWidget)
from PySide6.QtCore import Qt
from core.components.theme_manager import theme_manager, ThemeType


class ThemeSettingsWindow(QDialog):
    """主题设置窗口 - 用于配置应用程序主题"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("主题设置")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 主题选择组
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        # 主题选择下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色主题", "浅色主题", "自动"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(QLabel("选择主题:"))
        theme_layout.addWidget(self.theme_combo)
        
        # 自动切换复选框
        self.auto_switch_checkbox = QCheckBox("自动根据系统主题切换")
        self.auto_switch_checkbox.stateChanged.connect(self.on_auto_switch_changed)
        theme_layout.addWidget(self.auto_switch_checkbox)
        
        main_layout.addWidget(theme_group)
        
        # 预览组
        preview_group = QGroupBox("主题预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("主题预览效果")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: rgba(20, 20, 20, 220);
                border-radius: 8px;
                padding: 20px;
                color: white;
                font-size: 14px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(preview_group)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # 应用样式
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
                color: white;
            }
            QGroupBox {
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #CCCCCC;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QCheckBox {
                color: #CCCCCC;
            }
        """)
        
    def load_current_settings(self):
        """加载当前设置"""
        try:
            current_theme = theme_manager.current_theme
            if current_theme == ThemeType.DARK:
                self.theme_combo.setCurrentIndex(0)
            elif current_theme == ThemeType.LIGHT:
                self.theme_combo.setCurrentIndex(1)
            else:
                self.theme_combo.setCurrentIndex(2)
                
            # 设置自动切换复选框
            self.auto_switch_checkbox.setChecked(current_theme == ThemeType.AUTO)
            
            # 更新预览
            self.update_preview()
            
        except Exception as e:
            self.logger.error(f"加载设置时出错: {e}")
            
    def on_theme_changed(self, theme_text: str) -> None:
        """主题改变事件"""
        try:
            if theme_text == "深色主题":
                theme_manager.current_theme = ThemeType.DARK
            elif theme_text == "浅色主题":
                theme_manager.current_theme = ThemeType.LIGHT
            else:
                theme_manager.current_theme = ThemeType.AUTO
                
            self.update_preview()
            
        except Exception as e:
            self.logger.error(f"主题改变时出错: {e}")
            
    def on_auto_switch_changed(self, state: int) -> None:
        """自动切换状态改变事件"""
        try:
            if state == 2:  # Qt.Checked = 2
                theme_manager.current_theme = ThemeType.AUTO
            else:
                # 如果禁用自动切换，使用深色主题
                theme_manager.current_theme = ThemeType.DARK
                
            self.update_preview()
            
        except Exception as e:
            self.logger.error(f"自动切换改变时出错: {e}")
            
    def update_preview(self):
        """更新预览效果"""
        try:
            current_theme = theme_manager.current_theme
            if current_theme == ThemeType.DARK:
                self.preview_label.setText("深色主题预览\n当前主题: 深色模式")
                self.preview_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(20, 20, 20, 220);
                        border-radius: 8px;
                        padding: 20px;
                        color: white;
                        font-size: 14px;
                    }
                """)
            elif current_theme == ThemeType.LIGHT:
                self.preview_label.setText("浅色主题预览\n当前主题: 浅色模式")
                self.preview_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(245, 245, 245, 255);
                        border-radius: 8px;
                        padding: 20px;
                        color: black;
                        font-size: 14px;
                    }
                """)
            else:
                self.preview_label.setText("自动主题预览\n当前主题: 自动模式")
                self.preview_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(20, 20, 20, 220);
                        border-radius: 8px;
                        padding: 20px;
                        color: white;
                        font-size: 14px;
                    }
                """)
                
        except Exception as e:
            self.logger.error(f"更新预览时出错: {e}")
            
    def accept(self):
        """确定按钮点击"""
        try:
            # 保存设置到用户偏好
            # 这里可以添加保存逻辑
            super().accept()
        except Exception as e:
            self.logger.error(f"接受设置时出错: {e}")
            super().reject()
            
    def reject(self):
        """取消按钮点击"""
        try:
            # 恢复原始设置
            self.load_current_settings()
            super().reject()
        except Exception as e:
            self.logger.error(f"拒绝设置时出错: {e}")
            super().reject()


# 测试代码
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建主题设置窗口
    theme_window = ThemeSettingsWindow()
    theme_window.show()
    
    sys.exit(app.exec())
