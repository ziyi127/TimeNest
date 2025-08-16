#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
悬浮窗组件
"""

import sys
import os
import random
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout,
                               QHBoxLayout, QPushButton, QMenu,
                               QMessageBox, QDialog, QFormLayout,
                               QLineEdit, QComboBox, QDateEdit, QTimeEdit,
                               QListWidget, QListWidgetItem, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFrame, QCheckBox)
from PySide6.QtCore import QDate, QEvent, Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QAction, QMouseEvent, QGuiApplication

# 导入对话框
from frontend.gui.dialogs.course_edit_dialog import CourseEditDialog
from frontend.gui.dialogs.schedule_edit_dialog import ScheduleEditDialog


# 悬浮窗类
class FloatingWindow(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        self.initUI()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """鼠标双击事件，显示管理窗口"""
        self.app.tray_icon.show_management_window()
        event.accept()

    def initUI(self):
        # 设置窗口样式
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 窗口大小和位置 - 调整为屏幕中上部
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = 300
        window_height = 120
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3  # 屏幕中上部

        # 如果是首次启动（使用默认设置），则设置为屏幕中上部
        if (self.app.settings["window_position"]["x"] == 100 and 
            self.app.settings["window_position"]["y"] == 100):
            self.setGeometry(x, y, window_width, window_height)
            # 更新设置
            self.app.settings["window_position"] = {
                "x": x,
                "y": y
            }
            self.app.save_data()
        else:
            # 否则使用用户之前保存的位置
            self.setGeometry(
                self.app.settings["window_position"]["x"],
                self.app.settings["window_position"]["y"],
                window_width,
                window_height
            )

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # 创建背景框架
        self.background_frame = QFrame(self)
        self.background_frame.setStyleSheet("QFrame {background-color: rgba(255, 255, 255, 0.8); border-radius: 10px;}")
        self.background_frame.setMinimumSize(280, 100)
        background_layout = QVBoxLayout(self.background_frame)
        background_layout.setContentsMargins(15, 15, 15, 15)
        background_layout.setSpacing(5)

        # 时间标签
        self.time_label = QLabel("", self)
        self.time_label.setFont(QFont("SimHei", 16, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        background_layout.addWidget(self.time_label)

        # 课程状态标签
        # 先创建标签对象
        self.status_label = QLabel("今日无课程", self)
        self.status_label.setFont(QFont("SimHei", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        background_layout.addWidget(self.status_label)

        # 天气标签
        self.weather_label = QLabel("小雨 25℃", self)
        self.weather_label.setFont(QFont("SimHei", 12))
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        background_layout.addWidget(self.weather_label)

        main_layout.addWidget(self.background_frame)

        # 设置透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(1000)
        self.opacity_animation.setStartValue(0.8)
        self.opacity_animation.setEndValue(0.0)

        # 自动隐藏计时器 - 增加时间到10秒，避免误操作
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)
        # 延长自动隐藏时间到10秒
        self.auto_hide_timeout = 10000  # 10秒

        # 数据更新计时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(self.app.settings["update_interval"])

        # 更新时间和状态
        self.update_time()
        self.update_status()

        # 启动时间更新计时器
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

    def update_time(self):
        """更新时间显示"""
        now = datetime.now()
        time_str = now.strftime("%H:%M %a %d/%m/%y")
        # 替换星期为中文
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        weekday_zh = weekdays[now.weekday()]
        time_str = time_str.replace(now.strftime("%a"), weekday_zh)
        self.time_label.setText(time_str)

    def update_status(self):
        """更新课程状态显示"""
        schedule = self.app.get_today_schedule()
        if schedule["type"] == "none":
            self.status_label.setText("今日无课程")
            self.status_label.setStyleSheet("color: #666666;")
        elif schedule["type"] == "regular":
            course = schedule["course"]
            self.status_label.setText(f"{course['name']} ({course['teacher']}) {course['location']}")
            self.status_label.setStyleSheet("color: #000000;")
        elif schedule["type"] == "temp":
            course = schedule["course"]
            self.status_label.setText(f"【临时】{course['name']} ({course['teacher']}) {course['location']}")
            self.status_label.setStyleSheet("color: #FF5722;")

    def update_data(self):
        """更新数据"""
        self.app.load_data()
        self.update_status()
        # 随机更新天气（实际应用中应从API获取）
        weathers = ["晴", "多云", "小雨", "大雨", "雷暴"]
        temp = random.randint(20, 35)
        self.weather_label.setText(f"{random.choice(weathers)} {temp}℃")

    def start_fade_out(self):
        """开始淡出动画并隐藏窗口"""
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()

    def stop_fade_out(self):
        """停止淡出动画并恢复透明度"""
        self.opacity_animation.stop()
        self.setWindowOpacity(0.8)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件，开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.stop_fade_out()
            # 用户交互后，重置自动隐藏计时器
            self.hide_timer.stop()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_menu()
            # 用户交互后，重置自动隐藏计时器
            self.hide_timer.stop()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件，处理拖动"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件，结束拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            # 保存窗口位置
            self.app.settings["window_position"] = {
                "x": self.x(),
                "y": self.y()
            }
            self.app.save_data()
            event.accept()

    def enterEvent(self, event: QEvent):
        """鼠标进入事件，停止自动隐藏"""
        self.stop_fade_out()
        self.hide_timer.stop()
        event.accept()

    def leaveEvent(self, event: QEvent):
        """鼠标离开事件，启动自动隐藏计时器"""
        self.hide_timer.start(self.auto_hide_timeout)
        event.accept()

    def show_menu(self):
        """显示右键菜单"""
        menu = QMenu(self)
        manage_action = QAction("课表管理", self)
        manage_action.triggered.connect(self.app.tray_icon.show_management_window)
        temp_change_action = QAction("临时调课", self)
        temp_change_action.triggered.connect(self.app.tray_icon.show_temp_change_window)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.app.quit)
        menu.addAction(manage_action)
        menu.addAction(temp_change_action)
        menu.addAction(exit_action)
        menu.exec_(QCursor.pos())